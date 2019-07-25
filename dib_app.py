#!/usr/bin/env python

""" Import this module to create a command line Distibot application
"""

import logging
import argparse
import os
import sys
from configparser import ConfigParser

class DibApp():
    """ distibot CLI app
    """
    def __init__(self, description=None):
        self.parser = argparse.ArgumentParser(description=description)
        self.parser.add_argument('--conf', type=str, default="distibot.conf", help='conf file')
        self.parser.add_argument('--log_file', type=str, help='log file')
        self.parser.add_argument('--log_level', type=str, default="DEBUG", help='log level')
        self.args = self.parser.parse_args()

        self.set_logging()

        self.config = None
        self.load_config()

    def set_logging(self, log_format='short'):
        """ Set logging
        """
        numeric_level = getattr(logging, self.args.log_level, None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % numeric_level)

        logging.getLogger(__name__).addHandler(logging.NullHandler())
        if log_format == 'short':
            log_format = '%(asctime)-15s | %(levelname)-7s | %(message)s'
        elif log_format == 'full':
            log_format = '[%(filename)-20s:%(lineno)4s - %(funcName)20s()] \
%(levelname)-7s | %(asctime)-15s | %(message)s'

        if self.args.log_file and self.args.log_file == 'stdout':
            logging.basicConfig(stream=sys.stdout, format=log_format, level=numeric_level)
        else:
            if self.args.log_file:
                log_file = self.args.log_file
            else:
                log_dir = ''
                prg_name = os.path.splitext(os.path.basename(__file__))[0]
                log_file = log_dir + prg_name + ".log"
            logging.basicConfig(filename=log_file, format=log_format, level=numeric_level)

    def load_config(self):
        """ Read a config file
        """
        self.config = ConfigParser()
        self.config.read(self.args.conf)

    def run(self):
        """ Empty run method
        """
        logging.info('%s is running', self)

def main():
    """ Just main
    """
    #logging.info('Started')
    dib_app = DibApp('An empty Dib CLI application')
    dib_app.run()
    #logging.info('Finished')

if __name__ == '__main__':
    main()
