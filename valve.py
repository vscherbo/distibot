#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import gpio_class

class Valve(gpio_class.gpio):

    def __init__(self, gpio_1_2):
        super(Valve, self).__init__()
        self.valve_default_way = True
        self.gpio_1_2 = gpio_1_2
        self.gpio_list.append(gpio_1_2)
        GPIO.setup(self.gpio_1_2, GPIO.OUT, initial=GPIO.LOW)

    def release(self):
        self.default_way()
        super(Valve, self).release()

    def default_way(self):
        self.logger.info("valve.default_way")
        if self.valve_default_way:
            pass
        else:
            GPIO.output(self.gpio_1_2, 0)
            self.valve_default_way = True

    def power_on_way(self):
        self.logger.info("valve.power_on_way")
        if self.valve_default_way:
            GPIO.output(self.gpio_1_2, 1)
            self.valve_default_way = False


class DoubleValve(gpio_class.gpio):

    def __init__(self, gpio_v1, gpio_v2):
        super(DoubleValve, self).__init__()
        self.v1_on = False
        self.v2_on = False
        self.way = 3
        # TODO check initial values
        self.gpio_v1 = gpio_v1
        self.gpio_v2 = gpio_v2
        self.gpio_list.append(gpio_v1)
        self.gpio_list.append(gpio_v2)
        GPIO.setup(self.gpio_v1, GPIO.OUT, initial=GPIO.LOW)
        if self.gpio_v2 is not None:
            GPIO.setup(self.gpio_v2, GPIO.OUT, initial=GPIO.LOW)

    def release(self):
        self.v1_turn_off()
        self.v2_turn_off()
        super(DoubleValve, self).release()
        self.logger.info("DblValve switched off")

    def v1_turn_on(self):
        if not self.v1_on:
            GPIO.output(self.gpio_v1, 1)
            self.v1_on = True

    def v1_turn_off(self):
        if self.v1_on:
            GPIO.output(self.gpio_v1, 0)
            self.v1_on = False

    def v2_turn_on(self):
        if not self.v2_on:
            GPIO.output(self.gpio_v2, 1)
            self.v2_on = True

    def v2_turn_off(self):
        if self.v2_on:
            GPIO.output(self.gpio_v2, 0)
            self.v2_on = False

    def way_1(self):
        if not self.way == 1:
            self.v1_turn_on()
            self.v2_turn_off()
            self.way = 1

    def way_2(self):
        if not self.way == 2:
            self.v1_turn_off()
            self.v2_turn_on()
            self.way = 2

    def way_3(self):
        if not self.way == 3:
            self.v1_turn_off()
            self.v2_turn_off()
            self.way = 3

if __name__ == "__main__":
    import time
    import sys
    v_port1=23
    v_port2=24

    v1 = DoubleValve(gpio_v1=v_port1, gpio_v2=v_port2)

    sleep_time = 2

    print("way_1")
    v1.way_1()
    time.sleep(sleep_time)

    print("way_2")
    v1.way_2()
    time.sleep(sleep_time)

    # default way, both valves are off
    print("way_3")
    v1.way_3()
    time.sleep(sleep_time)

    print("way_1 again")
    v1.way_1()
    time.sleep(sleep_time)

    print("release")
    v1.release()
    sys.exit()
