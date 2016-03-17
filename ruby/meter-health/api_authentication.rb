require 'rubygems'
require 'bundler/setup'
require 'rest_client'
require 'oauth2'
require 'nokogiri'
require 'yaml'
require_relative 'helper_methods.rb'

class ApiAuthentication

  include HelperMethods

	def initialize
		@credentials = retrieve_credentials()
	end

  def generate_token
    client = OAuth2::Client.new(@credentials['app_id'], @credentials['app_secret'],
    	site: retrieve_site_base_url, token_url: retrieve_site_oauth_path,
    	scope: @credentials['scope'])
    token = client.password.get_token(@credentials['user_email'],
    	@credentials['user_password'],scope: @credentials['scope'])
    token && token.token ? token.token : nil
  end
end