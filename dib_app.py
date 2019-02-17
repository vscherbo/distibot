#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import argparse
import os
import sys

class DibApp(object):
    def __init__(self, description):

        self.parser = argparse.ArgumentParser(description=description)
        self.parser.add_argument('--conf', type=str, default="distibot.conf", help='conf file')
        self.parser.add_argument('--log_file', type=str, default='stdout', help='log file')
        self.parser.add_argument('--log_level', type=str, default="DEBUG", help='log level')
        self.args = self.parser.parse_args()

        numeric_level = getattr(logging, self.args.log_level, None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % numeric_level)

        logging.getLogger(__name__).addHandler(logging.NullHandler())
        # log_format = '[%(filename)-20s:%(lineno)4s - %(funcName)20s()] %(levelname)-7s | %(asctime)-15s | %(message)s'
        log_format = '%(asctime)-15s | %(levelname)-7s | %(message)s'

        if 'stdout' == self.args.log_file:
            logging.basicConfig(stream=sys.stdout, format=log_format, level=numeric_level)
        else:
            log_dir = ''
            if '' == self.args.log_file:
                (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
                log_file = log_dir + prg_name + ".log"
            else:
                log_file = log_dir + self.args.log_file
            logging.basicConfig(filename=log_file, format=log_format, level=numeric_level)

if __name__ == '__main__':




    logging.info('Started')



    logging.info('Finished')
