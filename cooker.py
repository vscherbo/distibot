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
    def click_button(self,gpio_port_num):
        RPIO.output(gpio_port_num, 0)
        time.sleep(0.1)
        RPIO.output(gpio_port_num, 1)

    def switch_on(self):
        if not self.state_on:
            self.click_button(self.gpio_on_off)
            self.state_on = True 
    def switch_off(self):
        if self.state_on:
            self.click_button(self.gpio_on_off)
            self.state_on = False
    def power_up(self):
        if self.power < power_max:
            self.click_button(self.gpio_up)
            self.power += 200
    def power_down(self):
        if self.power > power_min:
            self.click_button(self.gpio_down)
            self.power -= 200

