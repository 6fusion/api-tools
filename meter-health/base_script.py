import requests
import csv
import logging
logging.basicConfig(filename='example.log',level=logging.DEBUG)
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

class BaseScript2:
    # Change the values here to match your user and your API credentials
    CLIENT_ID = 'WRITE YOUR API CLIENT ID HERE'
    CLIENT_SECRET = 'WRITE YOUR API CLIENT SECRET HERE'
    USERNAME = 'WRITE YOUR USERNAME HERE'
    PASSWORD = 'WRITE YOUR PASSWORD HERE'
    SCOPE = ['admin_organization']

    # URL information for the API. ONLY change this method if you know what you are doing
    BASE_URL = "https://api.6fusion.com"
    ORGANIZATIONS ="/api/v2.json"
    METERS = "/api/v2/organizations/%d/meters.json"
    TOKEN_URL = "/oauth/token"

    def __init__(self):
        self.token = self.retrieve_token()
        self.payload = {'access_token': self.token}

    # create_report: is the main method that calls
    # all that need to be done:
    # 1. retrieve organizations
    # 2. iterate over the organizations to get meters
    # 3. create the csv file
    def create_report(self):
        if self.token:
            organizations = self.retrieve_organizations()
            if organizations:
                total_org = len(organizations)
                organization_index = 1
                print("We found %d organizations \n" % total_org)
                with open('example_file_test.csv', 'w+') as csv_file:
                    fieldnames = ["Organization Name", "Meter ID", "Meter Name",
                                    "Meter Type", "Meter Status", "Last Reading"]
                    writer = csv.writer(csv_file)
                    writer.writerow(fieldnames)
                    for organization in organizations:
                        print("Retrieving meters for organization %d of %d ...\n" % (organization_index, total_org))
                        organization_index += 1
                        meter_info = self.retrieve_meter_info_for(organization['remote_id'])
                        for meter in meter_info:
                            writer.writerow([organization['name'], meter['remote_id'], meter['name'], meter['kind'],
                                                meter['status'], meter['last_processed_on']])
                    print('Process successfully finished, analyzed a total of %d organizations' % total_org)
            else:
                print("There aren't organizations \n")

    # Requests organizations if they aren't returns []
    def retrieve_organizations(self):
        self.payload['expand'] = 'organizations'
        response = requests.get(self.generate_request_url(self.ORGANIZATIONS), params = self.payload)
        del self.payload['expand']
        json_response = response.json()
        if (json_response and 'embedded' in json_response and 'organizations' in json_response['embedded']
                and json_response["embedded"]["organizations"]):
            return json_response["embedded"]["organizations"]
        else:
            return []

    # Requests meters for an organization, if they aren't meters it returns []
    def retrieve_meter_info_for(self, org_id):
        response = requests.get(self.generate_request_url(self.METERS % org_id), params=self.payload)
        json_response = response.json()
        if (json_response and 'embedded' in json_response and 'meters' in json_response['embedded']
                and json_response["embedded"]["meters"]):
            return json_response["embedded"]["meters"]
        else:
            return []

    # Gets the authorization token if something is wrong during the request
    # it returns [] and prints a message that the process failed
    def retrieve_token(self):
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
                return []
        except:
            print("\nCheck your credentials,we weren't able to retrieve an authorization token! \n")
            return []

    def generate_request_url(self, path):
        return self.BASE_URL + path

test2 = BaseScript2()
test2.create_report()
