#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPIO
import time

class Valve:
    def __init__(self, gpio_1_2):
        self.valve_default_way =  True
        self.gpio_1_2 = gpio_1_2
        RPIO.setup(self.gpio_1_2, RPIO.OUT, initial=RPIO.LOW)
    def release(self):
        self.default_way()
        #RPIO.cleanup()
    def default_way(self):
        print("valve.default_way")
        if self.valve_default_way:
            pass
        else:
            RPIO.output(self.gpio_1_2, 0)
            self.valve_default_way =  True

    def power_on_way(self):
        print("valve.power_on_way")
        if self.valve_default_way:
            RPIO.output(self.gpio_1_2, 1)
            self.valve_default_way =  False

class DoubleValve:
    v1_on = False
    v2_on = False
    def __init__(self, ways, gpio_1_2, gpio_2_3 = None):
        self.way = 2
        self.ways = ways
        self.gpio_1_2 = gpio_1_2
        self.gpio_2_3 = gpio_2_3
        RPIO.setup(self.gpio_1_2, RPIO.OUT, initial=RPIO.HIGH)
        if self.gpio_2_3 is not None:
            RPIO.setup(self.gpio_2_3, RPIO.OUT, initial=RPIO.HIGH)
    def release(self):
        RPIO.cleanup()
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
    def way_2(self, gpio_id, value):
        try: 
            int(value)
        except ValueError:
            value = -1
        if not self.way == 2:
            self.v1_turn_off()
            self.v2_turn_off()
            self.way = 2 
    def way_3(self):
        if not self.way == 3:
            self.v1_turn_off()
            self.v2_turn_on()
            self.way = 3 
