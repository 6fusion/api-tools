require 'rubygems'
require 'bundler/setup'
require 'rest_client'
require 'json'
require 'csv'
require 'yaml'
require_relative 'api_authentication.rb'

class MeterHealth

  ORGANIZATIONS = "/api/v2.json"
  METERS = "/api/v2/organizations/%d/meters.json"
  SITE_BASE_URL = 'http://52.73.16.241:8080'
  TRIES = 20
  SLEEP_TIME = 5

  def initialize
    @credentials = retrieve_credentials
    @token = retrieve_token
  end

  def create_report
    if @token
      request_information
    else
      puts "Verify yor credentials, we weren't able to retrieve a token"
    end
  end

  private
  
  def retrieve_credentials
    file = File.read('./config/credentials.yml')
    YAML.load(file)
  end

  def retrieve_token
    api_authentication = ApiAuthentication.new()
    api_authentication.generate_token
  end

  def request_information
    organizations = JSON.parse(retrieve_organizations)
    if organizations && organizations["embedded"]["organizations"]
      write_to_csv(organizations["embedded"]["organizations"])
    else
      puts "No organizations were found"
    end
  end

  def retrieve_organizations
    response = RestClient.get("#{SITE_BASE_URL}#{ORGANIZATIONS}",
      { params: { access_token: @token, expand: 'organizations' } })
  end

  def write_to_csv(organizations)
    CSV.open(@credentials["file_name"], "w+") do |csv|
      csv << ['Organization Name', 'Meter ID', 'Meter Name',
              'Meter Type', 'Meter Status', 'Last Reading']
      total_org = organizations.count
      org_index = 1
      organizations.each do |org|
        print "Retrieving meters for organization #{org_index} of #{total_org}\n"
        retrieve_and_write_meters_to_csv(org,csv)
        org_index += 1
      end
    end
  end

  def retrieve_and_write_meters_to_csv(org,csv)
    meters = retrieve_meters_for_org(org)
    meters.each do |meter|
      csv << [ org['name'],
               meter['remote_id'],
               meter['name'],
               meter['kind'],
               meter['status'],
               meter['last_processed_on']
             ]
    end
  end

  def retrieve_meters_for_org(org)
    response = request_meters(org)
    meters = JSON.parse(response)
    if meters && meters["embedded"]["meters"]
      meters["embedded"]["meters"]
    else
      []
    end
  end

  def request_meters(org)
    tries = TRIES
    begin
      response = RestClient.get(("#{SITE_BASE_URL}#{METERS}" % org['remote_id']),
      { params: { access_token: @token } })
      return response
    rescue
      puts "Reached the total requests allowed in a minute...\n Waiting to retry\n"
      tries -= 1
      if tries > 0
        sleep(SLEEP_TIME)
        puts "Retrying for org #{org['name']}\n"
        retry
        return {}
      else
        puts "We were not able to retrieve info for org #{org['name']} too many retries attempted"
        return {}
      end
    end
  end
end

test = MeterHealth.new
test.create_report