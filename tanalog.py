#!/usr/bin/env python
""" 
An analog temperature sensor LM35 module connected via ADC MCP3201

VREF и VDD -> 3.3V
IN- и VSS -> GND
CLK -> GPIO11 (SPI_CLK)
DOUT -> GPIO9 (SPI_MISO)
CS/SHDN -> GPIO8 (SPI_CE0)
"""

import time
import logging
import re
from gpio_dev import GPIO_DEV, GPIO


class Tanalog():
    """ Single sensor calss
    """
    def __init__(self, gpio_CS, gpio_DOUT, gpio_CLK, Vref=3.3 ):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self.CS = int(gpio_CS)
        self.DOUT = int(gpio_DOUT)
        self.CLK = int(gpio_CLK)
        self.Vref =float( Vref)
        GPIO.setup(self.CS, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)
        GPIO.setup(self.CLK, GPIO.OUT)

    def get_temperature(self):
        """ Get measured temperature
        """
        GPIO.output(self.CS, True)
        GPIO.output(self.CLK, True)
        GPIO.output(self.CS, False)
        binData = 0
        i1 = 14

        while (i1 >= 0):
                GPIO.output(self.CLK, False)
                bitDOUT = GPIO.input(self.DOUT)
                GPIO.output(self.CLK, True)
                bitDOUT = bitDOUT << i1
                binData |= bitDOUT
                i1 -= 1

        GPIO.output(self.CS, True)
        binData &= 0xFFF
        loc_res = round(self.Vref * binData/4096.0/0.01, 2)  # 10mV per C
        #print('Temperature = ' + str(res) + 'C')
        return loc_res


if __name__ == '__main__':
    from time import sleep, strftime
    import argparse
    import os
    import sys
    from configparser import ConfigParser

    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    CONF_FILE_NAME = "distibot.conf"

    parser = argparse.ArgumentParser(description='Distibot "tanalog" module')
    parser.add_argument('--conf', type=str, default=CONF_FILE_NAME, help='conf file')
    parser.add_argument('--log_to_file', type=bool, default=False, help='log destination')
    parser.add_argument('--log_level', type=str, default="DEBUG", help='log level')
    args = parser.parse_args()

    numeric_level = getattr(logging, args.log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % numeric_level)

    # LOG_FORMAT = '[%(filename)-20s:%(lineno)4s - %(funcName)20s()] \
    # %(levelname)-7s | %(asctime)-15s | %(message)s'
    LOG_FORMAT = '%(asctime)-15s | %(levelname)-7s | %(message)s'

    if args.log_to_file:
        LOG_DIR = ''
        log_file = LOG_DIR + prg_name + ".log"
        logging.basicConfig(filename=log_file, format=LOG_FORMAT, level=numeric_level)
    else:
        logging.basicConfig(stream=sys.stdout, format=LOG_FORMAT, level=numeric_level)

    logging.info('Started')

    config = ConfigParser()
    config.read(args.conf)

    tanalog = Tanalog(config["tanalog"]["gpio_CS"],
                      config["tanalog"]["gpio_DOUT"],
                      config["tanalog"]["gpio_CLK"],
                      config["tanalog"]["Vref"],
                     )

    LOOP_FLAG = True
    while LOOP_FLAG:
        loc_t = tanalog.get_temperature()
        logging.info('loc_t=%s C', loc_t)

        try:
            sleep(1)
        except KeyboardInterrupt:
            LOOP_FLAG = False
            logging.info('\nKeyboard interrupt!, bye')

