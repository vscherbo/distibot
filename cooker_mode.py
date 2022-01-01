#!/usr/bin/env python
""" track modes of cooker """

from time import sleep
import argparse
import os
import sys
#from configparser import ConfigParser
import time
import logging
import threading
import RPi.GPIO as gpio
import cooker

def main():
    """ Just main """
    gpio.setmode(gpio.BCM)
    gpio.setwarnings(False)

    hallpin = 18

    gpio.setup( hallpin, gpio.IN)
    #gpio.setup(ledpin, gpio.OUT)
    #gpio.output(ledpin, False)

    found = 0
    not_found = 0
    while not_found < 5:
        if gpio.input(hallpin):
            found += 1
            not_found = 0
        else:
            not_found += 1
            found = 0
        time.sleep(1)

        print('{}^{}^{}'.format(time.strftime('%s'), found, not_found))

if __name__ == '__main__':

    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))

    parser = argparse.ArgumentParser(description='Distibot "cooker" module')
    parser.add_argument('--conf', type=str, default="distibot.conf", help='conf file')
    parser.add_argument('--play', type=str, default="cooker_modes.play", help='play file')
    parser.add_argument('--log_to_file', type=bool, default=False, help='log destination')
    parser.add_argument('--log_level', type=str, default="DEBUG", help='log level')
    args = parser.parse_args()

    numeric_level = getattr(logging, args.log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % numeric_level)

    LOG_FORMAT = '%(asctime)-15s | %(levelname)-7s | %(message)s'

    if args.log_to_file:
        LOG_DIR = ''
        log_file = LOG_DIR + prg_name + ".log"
        logging.basicConfig(filename=log_file, format=LOG_FORMAT, level=numeric_level)
    else:
        logging.basicConfig(stream=sys.stdout, format=LOG_FORMAT, level=numeric_level)

    logging.info('Started')
    ckt = cooker.CookerTester(args.conf)

    ckt.cooker.switch_on()
    sleep(2)

    ckt.load_script(args.play)
    try:
        t_ckt = threading.Thread(target=ckt.play_script())
        t_ckt.start()
    except:
        logging.exception("Error: unable to start thread", exc_info=True)
    else:
        main()

    ckt.cooker.release()

    logging.info('Finished')
