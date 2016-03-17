require 'yaml'
module HelperMethods
  def retrieve_credentials
    file = File.read('./config/credentials.yml')
    YAML.load(file)
  end

  def retrieve_site_base_url
    'http://52.73.16.241:8080'
  end

  def retrieve_site_oauth_path
    '/oauth/token'
  end

  def retrieve_organizations_path
    '/api/v2.json'
  end

  def retrieve_meters_path
    "/api/v2/organizations/%d/meters.json"
  end
end