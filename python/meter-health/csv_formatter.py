# -*- coding: utf-8 -*-
import csv
import config.credentials

class CsvFormatter:
    def __init__(self,headers):
        self.file_name = config.credentials.file_name
        self.headers = headers
        self.create_file_with_headers()

    def create_file_with_headers(self):
        with open(self.file_name, 'w+') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self.headers)

    def write(self,info):
        with open(self.file_name, 'a+') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(info)


