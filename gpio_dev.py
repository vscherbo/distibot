#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Class for GPIO devices
"""

import inspect

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

GPIO_LEVEL = {False: 'LOW', True: 'HIGH'}

class GPIO_DEV(object):

    def __init__(self):
        self.gpio_list = []
        logging.getLogger(__name__).addHandler(logging.NullHandler())

        GPIO.setmode(GPIO.BCM)
        logging.info('gpio_dev initialized')

    def setup(self, channel, mode, pull_up_down=GPIO.PUD_OFF, initial=None):
        if initial:
            GPIO.setup(channel, mode, pull_up_down=pull_up_down, initial=initial)
        else:
            GPIO.setup(channel, mode, pull_up_down=pull_up_down)
        logging.info('BEFORE append gpio_list=%s, channel=%s',
                     self.gpio_list, channel)
        if isinstance(channel, list):
            self.gpio_list.extend(channel)
        else:
            self.gpio_list.append(channel)
        logging.info('gpio_list=%s', self.gpio_list)

    def output(self, channel, value):
        GPIO.output(channel, value)
        logging.info('OUTPUT channel=%s, value=%s', channel, GPIO_LEVEL[value])

    def input(self, channel):
        val = GPIO.input(channel)
        logging.info('INPUT channel=%s, val=%s', channel, GPIO_LEVEL[val])
        return val

    def call_log(self):
        stack = inspect.stack()
        the_class = stack[1][0].f_locals["self"].__class__
        the_method = stack[1][0].f_code.co_name
        logging.info("called %s.%s", the_class, the_method)

    def release(self):
        if len(self.gpio_list) > 0:
            GPIO.cleanup(self.gpio_list)
            s = "cleaned gpio_list=[" + ', '.join(['{}']*len(self.gpio_list)) + "]"
            logging.info(s.format(*self.gpio_list))
            self.gpio_list = []
            logging.info('gpio_dev released')


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
    g1 = GPIO_DEV()

    g1.setup(23, GPIO.OUT, initial=GPIO.LOW)
    g1.setup(24, GPIO.OUT, initial=GPIO.LOW)

    g1.release()
    logging.info('Finished')
