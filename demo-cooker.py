#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cooker
from time import sleep
import RPIO

ck = cooker.Cooker(gpio_on_off= 17, gpio_up = 22, gpio_down = 27)
#ck = cooker.Cooker(17,22,27)
ck.switch_on()
sleep(2)
ck.power_up()
sleep(2)
ck.power_up()
sleep(2)
print ck.current_power()
sleep(5)
#
#
ck.power_down()
sleep(2)
ck.power_down()
sleep(2)
ck.power_down()
sleep(2)
print ck.current_power()
sleep(5)

ck.switch_off()

RPIO.cleanup()
