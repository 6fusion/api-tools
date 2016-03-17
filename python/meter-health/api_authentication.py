from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
import config.credentials
import config.server_paths as server

class ApiAuthentication:

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
        url = server.base_url + server.token_path
        return {'client': client, 'oauth': oauth, 'url': url}

    def build_authentication_token(self, environment):
        token = environment['oauth'].fetch_token(token_url=environment['url'],
                                                 username=config.credentials.username,
                                                 password=config.credentials.password,
                                                 client_id=config.credentials.client_id,
                                                 client_secret=config.credentials.client_secret,
                                                 scope=config.credentials.scope)
        return token['access_token'] if (token and 'access_token' in token and token['access_token']) else []
        