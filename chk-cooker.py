#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cooker
from time import sleep
import collections

"""
conf = open('test-chk-cooker.conf', 'r')
Tsteps = collections.OrderedDict(sorted(eval(conf.read()).items(), key=lambda t: t[0]))
conf.close()
set_Tsteps()
"""


ck = cooker.Cooker(gpio_on_off=17, gpio_up=22, gpio_down=27, gpio_fry=15)
ck.switch_on()
sleep(2)
"""
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
"""

ck.set_power_1800()
print ck.current_power()
sleep(3)

ck.set_power_1200()
print ck.current_power()
sleep(3)

print('set Fry mode')
ck.set_fry()
sleep(2)
print ck.current_power()

ck.release()

