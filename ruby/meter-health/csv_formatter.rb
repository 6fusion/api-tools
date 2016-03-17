require 'csv'
require_relative 'helper_methods.rb'

class CsvFormatter

  include HelperMethods

  def initialize(headers)
    @headers = headers
    @credentials = retrieve_credentials
    create_file_with_headers
  end

  def write(info)
    CSV.open(@credentials["file_name"], "a+") do |csv|
      csv << info
    end
  end

  private

  def create_file_with_headers
    CSV.open(@credentials["file_name"], "w+") do |csv|
      csv << @headers
    end
  end
end