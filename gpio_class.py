#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)


class gpio(object):
    gpio_list = []
    logger = None

    def __init__(self):
        self.logger = logging.getLogger("gpio")
        if not len(self.logger.handlers):
            file_handler = logging.FileHandler('gpio.log')
            formatter = logging.Formatter(log_format)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.DEBUG)

        mode = GPIO.getmode()
        if mode != GPIO.BCM or mode is None:
            GPIO.setmode(GPIO.BCM)

    def release(self):
        if self.gpio_list is not None:
            GPIO.cleanup(self.gpio_list)
            s = "cleaned gpio_list=[" + ', '.join(['{}']*len(self.gpio_list)) + "]"
            self.logger.info(s.format(*self.gpio_list))
            self.logger.info('gpio_class released')
