## Synopsis

Python code examples for connecting to 6fusion API and interact with the different components of your account

## Code structure

As part of this repo, we provide the following examples:
 - Meter Health verification


## Installation

Each tool require a different installation process.
#### Python Script
##### Requirements:

- Python version: 2.7

##### Installation instructions:
  1. Download the repo
  2.  Rename the file config/credentials.py.example to config/credentials.py
    * Modify the file to add your credentials, and set the name of the report
  3. Install pip:
    - To install pip on Ubuntu, Debian or Linux Mint: $ sudo apt-get install python-pip
    - To install pip on Fedora: $ sudo yum install python-pip
    - To install pip on CentOS, first enable EPEL repository, and then run: $ sudo yum install python-pip
		Source: http://ask.xmodulo.com/install-pip-linux.html
  4. Install the dependencies run:
    * pip install --upgrade pip
    * pip install -r requirements.txt
  5. Run the script
    * python meter_health.py
    * Note: if you are running the script on development environment you need to also set an environment variable:
      ** export OAUTHLIB_INSECURE_TRANSPORT=true



