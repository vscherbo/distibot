#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Class for GPIO devices
"""


import imp
try:
    imp.find_module('RPi')
    import RPi.GPIO as GPIO
except ImportError:
    """
    import FakeRPi.GPIO as GPIO
    OR
    import FakeRPi.RPiO as RPiO
    """
    import FakeRPi.GPIO as GPIO

import logging


class GPIO_DIB(object):

    def __init__(self):
        self.gpio_list = []
        logging.getLogger(__name__).addHandler(logging.NullHandler())

        GPIO.setmode(GPIO.BCM)
        logging.info('gpio_class initialized')

    def setup(self, channel, mode, initial=None, pull_up_down=GPIO.PUD_OFF):
        GPIO.setup(channel, mode, initial=initial, pull_up_down=pull_up_down)
        logging.info('BEFORE append gpio_list=%s, channel=%s',
                     self.gpio_list, channel)
        if isinstance(channel, list):
            self.gpio_list.extend(channel)
        else:
            self.gpio_list.append(channel)
        logging.info('gpio_list=%s', self.gpio_list)

    def output(self, channel, value):
        GPIO.output(channel, value)
        logging.info('OUTPUT channel=%s, value=%s', channel, value)

    def release(self):
        if self.gpio_list is not None:
            GPIO.cleanup(self.gpio_list)
            s = "cleaned gpio_list=[" + ', '.join(['{}']*len(self.gpio_list)) + "]"
            logging.info(s.format(*self.gpio_list))
            logging.info('gpio_class released')


if __name__ == "__main__":
    import os
    import sys
    log_dir = ''
    log_format = '[%(filename)-20s:%(lineno)4s - %(funcName)20s()] \
            %(levelname)-7s | %(asctime)-15s | %(message)s'

    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    # logging.basicConfig(filename=prg_name+'.log', \
    #        format=log_format, level=logging.INFO)
    logging.basicConfig(stream=sys.stdout, format=log_format,
                        level=logging.DEBUG)

    logging.info('Started')
    g1 = GPIO_DIB()

    g1.setup(23, GPIO.OUT, initial=GPIO.LOW)
    g1.setup(24, GPIO.OUT, initial=GPIO.LOW)

    g1.release()
    logging.info('Finished')
