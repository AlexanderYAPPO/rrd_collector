'''
Created on Nov 14, 2014

@author: alexander
'''

import re
import datetime


def parse_date_to_epoch(date):
        date_list = date[0].split('/')
        time_list = date[1].split(':')
        result_time = datetime.datetime(
            int('20' + date_list[0]),
            int(date_list[1]),
            int(date_list[2]),
            int(time_list[0]),
            int(time_list[1]),
            int(time_list[2])
            ).strftime('%s')
        return result_time


class LogParser:

    def read_next(self):
        self.latency = 0
        self.last_line = self.file.readline()
        if not self.last_line:
            self.have_lines = False
            self.file.close()
        else:
            reg_pattern = '^([0-9]+/[0-9]+/[0-9]+)\s([0-9]+:[0-9]+:[0-9]+)\s'
            parsed_line = re.search(reg_pattern, self.last_line)
            if not parsed_line:
                self.success = False
                return
            self.time_stamp = parse_date_to_epoch(
                [parsed_line.group(1), parsed_line.group(2)]
                )
            reg_pattern = (
                '^([0-9]+/[0-9]+/[0-9]+)\s([0-9]+:[0-9]+:[0-9]+)' +
                '\sTRACE\sConnectionManager:\sOperation\stransfer\s[0-9]+\s' +
                '[a-zA-Z\?]*,\s([0-9]+)ms:\sHTTP/1.1\s200\sOK$')
            parsed_line = re.search(reg_pattern, self.last_line)
            if parsed_line is None:
                fail_reg_pattern = (
                    '^([0-9]+/[0-9]+/[0-9]+)\s([0-9]+:[0-9]+:[0-9]+)' +
                    '\sTRACE\sConnectionManager:\sOperation\stransfer\s' +
                    '[0-9]+\s[a-zA-Z\?]*,\s([0-9]+)ms:\sHTTP/1.1\s.+$')
                if re.search(fail_reg_pattern, self.last_line):
                    self.faults += 1
                self.success = False
            else:
                self.success = True
                self.latency = int(parsed_line.group(3))
            self.query_number += 1


    def __init__(self, file_name):
        self.faults = 0
        self.have_lines = True
        self.time_stamp = None
        self.success = True
        self.latency = 0
        self.query_number = 1
        self.file = open(file_name, 'r')
        # self.file.readline()
        # self.file.readline()
        # self.file.readline()
        self.read_next()
        if not self.last_line:
            self.have_lines = False
