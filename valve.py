#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPIO
import time

class Valve:
    v1_on = False
    v2_on = False
    def __init__(self, ways, gpio_1_2, gpio_2_3 = None):
        self.way = 2
        self.ways = ways
        self.gpio_1_2 = gpio_1_2
        if RPIO.OUT == RPIO.gpio_function(self.gpio_1_2):
            RPIO.output(self.gpio_1_2, True)
        RPIO.setup(self.gpio_1_2, RPIO.OUT, initial=RPIO.HIGH)
        self.gpio_2_3 = gpio_2_3
        if self.gpio_2_3 is not None:
            RPIO.setup(self.gpio_2_3, RPIO.OUT, initial=RPIO.HIGH)
    def __del__(self):
        pass
    def v1_turn_on(self):
        if self.v1_on:
            pass
        else:
            RPIO.output(self.gpio_1_2, 0)
            self.v1_on = True

    def v1_turn_off(self):
        if self.v1_on:
            RPIO.output(self.gpio_1_2, 1)
            self.v1_on = False

    def v2_turn_on(self):
        if self.ways == 2:
            return
        if self.v2_on:
            pass
        else:
            RPIO.output(self.gpio_2_3, 0)
            self.v2_on = True

    def v2_turn_off(self):
        if self.ways == 2:
            return
        if self.v2_on:
            RPIO.output(self.gpio_2_3, 1)
            self.v2_on = False

    def way_1(self):
        if not self.way == 1:
            self.v1_turn_on()
            self.v2_turn_off()
            self.way = 1 
    def way_2(self):
        if not self.way == 2:
            self.v1_turn_off()
            self.v2_turn_off()
            self.way = 2 
    def way_3(self):
        if not self.way == 3:
            self.v1_turn_off()
            self.v2_turn_on()
            self.way = 3 
