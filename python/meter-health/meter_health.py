# -*- coding: utf-8 -*-
import requests
import csv
import logging
import config.credentials
from api_authentication import ApiAuthentication
import time

logging.basicConfig(filename='example.log', level=logging.DEBUG)


class MeterHealth:
    # URL information for the API. ONLY change this method if you know what you are doing
    BASE_URL = "http://52.73.16.241:8080"
    ORGANIZATIONS = "/api/v2.json"
    METERS = "/api/v2/organizations/%d/meters.json"
    TRIES = 20
    SLEEP_SECONDS = 5

    def __init__(self):
        self.token = self.retrieve_token()
        self.payload = {'access_token': self.token}

    def retrieve_token(self):
        token_generator = ApiAuthentication()
        return token_generator.retrieve_token()

    def create_report(self):
        """ It is the main method that calls
        all that need to be done
        """
        if self.token:
            organizations = self.retrieve_organizations()
            if organizations:
                self.build_report(organizations)
            else:
                print("There aren't organizations \n")

    def build_report(self, organizations):
        # Creates/opens the file which will store the info
        total_org = len(organizations)
        print("We found %d organizations \n" % total_org)
        with open(config.credentials.file_name, 'w+') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Organization Name', 'Meter ID', 'Meter Name',
                             'Meter Type', 'Meter Status', 'Last Reading'])
            self.add_information_to_report({'organizations': organizations,
                                            'total_org': total_org,
                                            'writer': writer})
            print("Process successfully finished, analyzed a total of %d organizations" % total_org)

    def add_information_to_report(self, params):
        # Iterates over the organizations to retrieve meters
        organization_index = 1
        for organization in params['organizations']:
            print("Retrieving meters for organization %d of %d ...\n" % (organization_index, params['total_org']))
            organization_index += 1
            meter_info = self.retrieve_meter_info_for(organization['remote_id'], 0)
            self.write_meters_to_report({'meter_info': meter_info,
                                      'organization': organization,
                                      'writer': params['writer']})

    def write_meters_to_report(self, params):
        """ Iterates over a meters for an organization
        to write the info to csv
        """
        for meter in params['meter_info']:
            params['writer'].writerow([params['organization']['name'],
                           meter['remote_id'],
                           meter['name'],
                           meter['kind'],
                           meter['status'],
                           meter['last_processed_on']])

    def retrieve_organizations(self):
        # Validates response from server when retrieving organizations
        json_response = self.request_organizations()
        if self.retrieve_organizations_conditions(json_response):
            return json_response['embedded']['organizations']
        else:
            return []

    def retrieve_organizations_conditions(self, json_response):
        return (json_response and 'embedded' in json_response and 'organizations' in json_response['embedded']
                and json_response['embedded']['organizations'])

    def request_organizations(self):
        # Requests organizations if they aren't returns []
        self.payload['expand'] = 'organizations'
        response = requests.get(self.generate_request_url(self.ORGANIZATIONS), params=self.payload)
        del self.payload['expand']
        return response.json()

    def retrieve_meter_info_for(self, org_id, try_number):
        # Requests meters for an organization, if they aren't meters it returns []
        if try_number < self.TRIES:
            try:
                response = requests.get(self.generate_request_url(self.METERS % org_id), params=self.payload)
                json_response = response.json()
                if 'success' in json_response:
                    print("Reached the total requests allowed in a minute...\n Waiting to retry\n")
                    time.sleep(self.SLEEP_SECONDS)
                    print("Retrying for org %d \n" % org_id)
                    self.retrieve_meter_info_for(org_id,try_number+1)
                    return []
                else:
                    return json_response['embedded']['meters'] if self.retrieve_meters_conditions(json_response) else []
            except:
                print("Could not do request")
                return []

    def retrieve_meters_conditions(self, json_response):
        return (json_response and 'embedded' in json_response and 'meters' in json_response['embedded'])


    def generate_request_url(self, path):
        return self.BASE_URL + path

test = MeterHealth()
test.create_report()
