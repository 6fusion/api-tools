import requests
import csv
import logging
import sys
import datetime
import re
import calendar
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

# Uncomment the following 2 lines on non HTTPS environments
# import os
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

logging.basicConfig(filename='consumption_report.log', level=logging.DEBUG)

class ConsumptionReport:
    # Change the values here to match your user and your API credentials (or set a valid oauth token)
    CLIENT_SECRET = "e4ec5e4d593980958f9abb8fb1b416384ab59cda47d67f15e823a13e7832b089"
    CLIENT_ID = "bc6e260e38a77de79faa64f649a0281c25a0a58e5785ae31ab3caa6a1d1d9089"
    USERNAME = "veristor.service@gmail.com"
    PASSWORD = "@password1"
    SCOPE = ["admin_organization"]
    # OPTIONAL, please ensure that this token NEVER expires.
    # Leave it empty if you prefer that the app generates its own token each time
    OAUTH_TOKEN = ''

    # URL information for the API. ONLY change this method if you know what you are doing
    BASE_URL = "https://api.6fusion.com"
    TOKEN_URL = "/oauth/token"
    ORGANIZATIONS = "/api/v2.json"
    BILLING_GROUPS = "/api/v2/organizations/%d/billing_groups.json"
    BILLING_GROUP_MACHINES = "/api/v2/organizations/%d/billing_groups/%d/machines.json"
    MACHINE_READINGS = "/api/v2/organizations/%d/infrastructures/%d/machines/%d/readings.json"

    # Export filename has the date as part of the name, for
    EXPORT_FILENAME = 'consumption_report_%s.csv' % datetime.date.today().isoformat()
    # DEFAULT CONSTANTS
    DESCRIPTIVE = True
    MINIMUM_YEAR_VALID = 2000
    MAX_ELEMENTS_LIMIT = 99999
    INT_MAX = sys.maxsize
    NUMERIC_REGEX = '\d+'
    FILE_HEADERS = ["Organization Name", "Billing Group", "Avg CPU Usage (MHz)", "Min CPU Usage (MHz)",
                    "Max CPU Usage (MHz)", "Avg MEM Usage (MB)", "Min MEM Usage (MB)", "Max MEM Usage (MB)"]

    def __init__(self, cmd_args):
        print "Starting the billing summary process"
        self.load_dates_from_args(cmd_args)
        self.token = self.retrieve_token()
        self.payload = {'access_token': self.token}

    # Method used for getting dates information from the arguments for the application
    def load_dates_from_args(self, cmd_args):
        # verify the 2 parameters (year and month)
        if cmd_args and len(cmd_args) == 3:
            numeric_regex = re.compile(self.NUMERIC_REGEX)

            year_arg = int(cmd_args[1]) if numeric_regex.match(cmd_args[1]) else 0
            month_arg = int(cmd_args[2]) if numeric_regex.match(cmd_args[2]) else 0

            # verify each argument
            if year_arg > self.MINIMUM_YEAR_VALID and month_arg > 0:
                since_date = datetime.datetime.strptime("%d%d" % (year_arg, month_arg), '%Y%m')

                self.until_date = since_date.replace(
                    day=calendar.monthrange(since_date.year, since_date.month)[1], minute=59, second=59,
                    hour=23).isoformat()
                self.since_date = since_date.isoformat()
            else:
                print('*********    ERROR    *********')
                print "Please ensure that your arguments match a valid year and a valid month."
                print "Eg. python consumption_report_script.py 2016 04"
                exit(0)
        else:
            print('\n*********    ERROR    *********')
            print "Please ensure that you provide 2 arguments to the script the year and the month which you require the information from"
            print "Eg. python consumption_report_script.py 2016 04"
            exit(0)

    # Main mathod of the aplication, invokes all the required sub-methods
    def create_report(self):
        organizations = self.retrieve_organizations()
        if organizations:
            self.analyze_organizations(organizations)
        else:
            print('\n*********    ERROR    *********')
            print("Provided credentials are from a user without authorized organizations")
            exit(0)

    # After getting all organizations, we need to
    def analyze_organizations(self, organizations):
        total_org = len(organizations)
        organization_index = 1
        if self.DESCRIPTIVE: print("%d organizations found" % total_org)
        with open(self.EXPORT_FILENAME, 'w+') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self.FILE_HEADERS)
            for organization in organizations:
                if self.DESCRIPTIVE: print(
                    "\nRetrieving Billing Groups for organization %s - %d of %d" % (
                        organization['name'], organization_index, total_org))
                organization_index += 1
                self.process_billing_groups(organization, writer)
        print('\nProcess finished successfully. "%s" file created' % self.EXPORT_FILENAME)

    # Execute the calculations required for all billing groups of an organization
    def process_billing_groups(self, organization, writer):
        # Beyond this process, is recommended to have larger limits on all requests
        self.payload['limit'] = self.MAX_ELEMENTS_LIMIT
        billing_groups = self.retrieve_billing_groups_for(organization['remote_id'])
        bg_index = 1
        billing_groups_count = len(billing_groups)
        if billing_groups_count > 0:
            if self.DESCRIPTIVE: print "  - %d billing groups found" % billing_groups_count
            for billing_group in billing_groups:
                if self.DESCRIPTIVE: print(
                "    + Retrieving Machines for Billing Group %s - %d of %d" % (billing_group['name'], bg_index,
                                                                               billing_groups_count))
                machines = self.retrieve_machines_billing_groups_for(organization['remote_id'],
                                                                     billing_group['remote_id'])
                billing_group_summary = self.process_machines_summary(machines, organization['remote_id'])
                writer.writerow([organization['name'], billing_group['name'], billing_group_summary['cpu_average'],
                                 billing_group_summary['cpu_min'], billing_group_summary['cpu_max'],
                                 billing_group_summary['memory_average'], billing_group_summary['memory_min'],
                                 billing_group_summary['memory_max']])
                bg_index += 1
        else:
            if self.DESCRIPTIVE: print "  - No Billing groups found"

    # Generates summary information from all machines (obtaining readings)
    def process_machines_summary(self, machines, org_id):
        machines_count = len(machines)
        # Get all readings for all machines and generate a single list
        all_readings = []
        if machines_count > 0:
            if self.DESCRIPTIVE: print("      - %d machines found" % machines_count)
            # include since and until for all requests of metrics
            self.payload['since'] = self.since_date
            self.payload['until'] = self.until_date

            for machine in machines:
                # get infrastructure from its href
                infrastructure_href = machine['_links']['infrastructure']['href']
                infrastructure_id = int(infrastructure_href.replace('.json', '').split('/')[-1])
                all_readings += self.retrieve_machine_readings_for(org_id, infrastructure_id, machine['remote_id'])

            # Remove the information from the payload after usage
            del self.payload['since']
            del self.payload['until']
        else:
            if self.DESCRIPTIVE: print("      - No Machines found")

        return self.calculate_readings_summary(all_readings)

    # Calculates required metrics based on all readings for all machines on a billing group
    def calculate_readings_summary(self, readings):
        readings_count = len(readings)
        cpu_max = cpu_min = cpu_average = memory_max = memory_min = memory_average = 0.0

        # just perform calculations if we have readings
        if readings_count > 0:
            cpu_min = memory_min = self.INT_MAX
            total_cpu = total_memory = 0.0

            for reading in readings:
                memory_current = reading['memory_megabytes']
                cpu_current = reading['cpu_mhz']

                # Assign the maximum, minimum for each element
                if memory_current < memory_min: memory_min = memory_current
                if memory_current > memory_max: memory_max = memory_current
                if cpu_current < cpu_min: cpu_min = cpu_current
                if cpu_current > cpu_max: cpu_max = cpu_current
                total_cpu += cpu_current
                total_memory += memory_current

            memory_average = total_memory / readings_count
            cpu_average = total_cpu / readings_count

        return {'cpu_max': self.float_format(cpu_max), 'cpu_min': self.float_format(cpu_min),
                'cpu_average': self.float_format(cpu_average), 'memory_max': self.float_format(memory_max),
                'memory_min': self.float_format(memory_min), 'memory_average': self.float_format(memory_average)}

    # Requests organizations if they aren't returns []
    def retrieve_organizations(self):
        self.payload['expand'] = 'organizations'
        response = requests.get(self.generate_request_url(self.ORGANIZATIONS), params=self.payload)
        # Remove it from the payload as we may not need it for other elements
        del self.payload['expand']
        json_response = response.json()
        if (json_response and 'embedded' in json_response and 'organizations' in json_response['embedded']
            and json_response["embedded"]["organizations"]):
            return json_response["embedded"]["organizations"]
        else:
            return []

    # Requests billing_groups for an organization, if they aren't billing_groups it returns []
    def retrieve_billing_groups_for(self, org_id):
        response = requests.get(self.generate_request_url(self.BILLING_GROUPS % org_id), params=self.payload)
        json_response = response.json()
        if (json_response and 'embedded' in json_response and 'billing_groups' in json_response['embedded']
            and json_response["embedded"]["billing_groups"]):
            return json_response["embedded"]["billing_groups"]
        else:
            return []

    # Requests machines for a billing_group, if there aren't machines it returns []
    def retrieve_machines_billing_groups_for(self, org_id, billing_id):
        response = requests.get(self.generate_request_url(self.BILLING_GROUP_MACHINES % (org_id, billing_id)),
                                params=self.payload)
        json_response = response.json()
        if (json_response and 'embedded' in json_response and 'machines' in json_response['embedded']
            and json_response["embedded"]["machines"]):
            return json_response["embedded"]["machines"]
        else:
            return []

    # Requests machine_readings for a machine, if there aren't readings it returns []
    def retrieve_machine_readings_for(self, org_id, infrastructure_id, machine_id):
        response = requests.get(
            self.generate_request_url(self.MACHINE_READINGS % (org_id, infrastructure_id, machine_id)),
            params=self.payload)
        json_response = response.json()
        if (json_response and 'embedded' in json_response and 'readings' in json_response['embedded']
            and json_response["embedded"]["readings"]):
            return json_response["embedded"]["readings"]
        else:
            return []

    # Gets the authorization token if something is wrong during the request
    # it returns [] and prints a message that the process failed
    def retrieve_token(self):
        # if we have a valid token
        if self.OAUTH_TOKEN != '': return self.OAUTH_TOKEN
        client = LegacyApplicationClient(client_id=self.CLIENT_ID)
        oauth = OAuth2Session(client=client)
        url = self.BASE_URL + self.TOKEN_URL
        try:
            token = oauth.fetch_token(token_url=url, username=self.USERNAME, password=self.PASSWORD,
                                      client_id=self.CLIENT_ID, client_secret=self.CLIENT_SECRET,
                                      scope=self.SCOPE)
            if token and 'access_token' in token and token['access_token']:
                return token['access_token']
            else:
                raise Exception

        except Exception, e:
            print('*********    ERROR    *********')
            print('Failed to authenticate with API: ' + str(e))
            print("Check your credentials, couldn't retrieve an authorization token! \n")
            exit(0)

    # Generates URL for different requests
    def generate_request_url(self, path):
        return self.BASE_URL + path

    # Converts a float number to have just 2 decimals
    def float_format(self, number):
        return ("%.2f" % number)


test2 = ConsumptionReport(sys.argv)
test2.create_report()
