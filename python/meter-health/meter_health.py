# -*- coding: utf-8 -*-
import requests
import csv
import logging
import config.credentials
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

logging.basicConfig(filename='example.log', level=logging.DEBUG)


class MeterHealth:
    # URL information for the API. ONLY change this method if you know what you are doing
    BASE_URL = "http://54.90.173.204:8080"
    ORGANIZATIONS = "/api/v2.json"
    METERS = "/api/v2/organizations/%d/meters.json"
    TOKEN_URL = "/oauth/token"

    def __init__(self):
        self.token = self.retrieve_token()
        self.payload = {'access_token': self.token}

    def create_report(self):
        """ It is the main method that calls
        all that need to be done
        """
        if self.token:
            organizations = self.retrieve_organizations()
            if organizations:
                self.build_csv(organizations)
            else:
                print("There aren't organizations \n")

    def build_csv(self, organizations):
        # Creates/opens the file which will store the info
        total_org = len(organizations)
        print("We found %d organizations \n" % total_org)
        with open(config.credentials.file_name, 'w+') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Organization Name', 'Meter ID', 'Meter Name',
                             'Meter Type', 'Meter Status', 'Last Reading'])
            self.add_information_to_csv({'organizations': organizations,
                                         'writer': writer,
                                         'total_org': total_org})
            print("Process successfully finished, analyzed a total of %d organizations" % total_org)

    def add_information_to_csv(self, params):
        # Iterates over the organizations to retrieve meters
        organization_index = 1
        for organization in params['organizations']:
            print("Retrieving meters for organization %d of %d ...\n" % (organization_index, params['total_org']))
            organization_index += 1
            meter_info = self.retrieve_meter_info_for(organization['remote_id'])
            self.write_meters_to_csv({"meter_info": meter_info,
                                      "organization": organization,
                                      "writer": params["writer"]})

    def write_meters_to_csv(self, params):
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

    def retrieve_meter_info_for(self, org_id):
        # Requests meters for an organization, if they aren't meters it returns []
        response = requests.get(self.generate_request_url(self.METERS % org_id), params=self.payload)
        json_response = response.json()
        return json_response['embedded']['meters'] if self.retrieve_meters_conditions(json_response) else []

    def retrieve_meters_conditions(self, json_response):
        return (json_response and 'embedded' in json_response and 'meters' in json_response['embedded']
                and json_response['embedded']['meters'])

    def retrieve_token(self):
        """ Gets the authorization token if something is wrong during the request
        it returns [] and prints a message that the process failed
        """
        environment = self.set_token_variables()
        try:
            return self.build_authentication_token(environment)
        except:
            print("\n Check your credentials,we weren't able to retrieve an authorization token! \n")
            return []

    def set_token_variables(self):
        client = LegacyApplicationClient(client_id=config.credentials.client_id)
        oauth = OAuth2Session(client=client)
        url = self.BASE_URL + self.TOKEN_URL
        return {'client': client, 'oauth': oauth, 'url': url}

    def build_authentication_token(self, environment):
        token = environment['oauth'].fetch_token(token_url=environment['url'],
                                                 username=config.credentials.username,
                                                 password=config.credentials.password,
                                                 client_id=config.credentials.client_id,
                                                 client_secret=config.credentials.client_secret,
                                                 scope=config.credentials.scope)
        return token['access_token'] if (token and 'access_token' in token and token['access_token']) else []

    def generate_request_url(self, path):
        return self.BASE_URL + path

test = MeterHealth()
test.create_report()
