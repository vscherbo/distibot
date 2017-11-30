#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Class for GPIO output devices
"""


"""
import importlib.util
try:
    importlib.util.find_spec('RPi.GPIO')
    import RPi.GPIO as GPIO
"""

import imp
try:
    imp.find_module('RPi.GPIO')
    import RPi.GPIO as GPIO
except ImportError:
    """
    import FakeRPi.GPIO as GPIO
    OR
    import FakeRPi.RPiO as RPiO
    """
    import FakeRPi.GPIO as GPIO

import logging

class GPIO_DEV(object):

    def __init__(self):
        self.gpio_list = []
        logging.getLogger(__name__).addHandler(logging.NullHandler())

        GPIO.setmode(GPIO.BCM)
        logging.info('gpio_class initialized')

    def release(self):
        if self.gpio_list is not None:
            GPIO.cleanup(self.gpio_list)
            s = "cleaned gpio_list=[" + ', '.join(['{}']*len(self.gpio_list)) + "]"
            logging.info(s.format(*self.gpio_list))
            logging.info('gpio_class released')


if __name__ == "__main__":
    import os
    log_dir = ''
    log_format = '[%(filename)-20s:%(lineno)4s - %(funcName)20s()] %(levelname)-7s | %(asctime)-15s | %(message)s'

    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    logging.basicConfig(filename=prg_name+'.log', format=log_format, level=logging.INFO)

    logging.info('Started')
    g1 = GPIO_DEV()
    g1.release()
    logging.info('Finished')

