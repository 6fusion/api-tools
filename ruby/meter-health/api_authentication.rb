require 'rubygems'
require 'bundler/setup'
require 'rest_client'
require 'oauth2'
require 'nokogiri'
require 'yaml'

class ApiAuthentication

	SITE_BASE_URL = 'http://52.73.16.241:8080'
  SITE_OAUTH_PATH = '/oauth/token'

	def initialize
		@credentials = retrieve_credentials()
	end

	def generate_token
		client = OAuth2::Client.new(@credentials['app_id'], @credentials['app_secret'],
      site: SITE_BASE_URL, token_url: SITE_OAUTH_PATH, scope: @credentials['scope'])
    token = client.password.get_token(@credentials['user_email'],
      @credentials['user_password'],scope: @credentials['scope'])
    token && token.token ? token.token : nil
	end

	private

	def retrieve_credentials
    file = File.read('./config/credentials.yml')
    YAML.load(file)
  end
end