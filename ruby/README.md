## Synopsis

Ruby code examples for connecting to 6fusion API and interact with the different components of your account

## Code structure

As part of this repo, we provide the following examples:
 - Meter Health verification


## Installation

Each tool require a different installation process.
#### Ruby Script
##### Requirements:

- Ruby version: 2.1

##### Installation instructions:
  1. Download the repo
  2.  Rename the file config/credentials.yml.example to config/credentials.yml
    * Modify the file to add your credentials, and set the name of the report
  3. Install ruby and bundler:
    - Debian:
      * Install curl : $ sudo apt-get install curl
      * Install rvm : $ \curl -L https://get.rvm.io | bash -s stable --ruby
      * Install ruby 2.1: $ rvm install ruby-2.1-head && rvm use ruby-2.1-head
      * Reload the configuration: $ source ~/.rvm/scripts/rvm
      * Test rvm is installed properly: $type rvm | head -n 1
        - Result should be: rvm is a function
    - CentOS / Fedora :
      * Install curl : $ yum install curl
      * Install rvm : $ gpg2 --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 && curl -sSL https://get.rvm.io | bash -s stable
      * Load rvm into environment variable: $ source /etc/profile.d/rvm.sh
      * Install all the dependencies for installing ruby: $ rvm requirements
      * Install ruby 2.1: $ rvm install ruby-2.1-head && rvm use ruby-2.1-head
  4. Install the dependencies run:
    * bundle install

  5. Run the script
    * ruby meter_health.rb