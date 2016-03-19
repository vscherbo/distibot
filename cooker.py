#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPIO
import time

class Cooker:
    power_max = 2000
    power_min = 120
    def __init__(self, gpio_on_off, gpio_up, gpio_down):
        self.gpio_on_off = gpio_on_off
        RPIO.setup(self.gpio_on_off, RPIO.OUT, initial=RPIO.HIGH)
        self.gpio_up = gpio_up
        RPIO.setup(self.gpio_up, RPIO.OUT, initial=RPIO.HIGH)
        self.gpio_down = gpio_down
        RPIO.setup(self.gpio_down, RPIO.OUT, initial=RPIO.HIGH)
        self.power = 1400
        self.state_on = False
    def switch_on(self):
        if not self.state_on:
            RPIO.output(gpio_on_off, 0)
            time.sleep(1)
            RPIO.output(gpio_on_off, 1)
            self.state_on = True 
    def switch_off(self):
        if self.state_on:
            RPIO.output(gpio_on_off, 0)
            time.sleep(1)
            RPIO.output(gpio_on_off, 1)
            self.state_on = False
    def power_up(self):
        if self.power < power_max:
            RPIO.output(gpio_up, 0)
            time.sleep(1)
            RPIO.output(gpio_up, 1)
            self.power += 200

