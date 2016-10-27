#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import valve
import RPIO
import sys

RPIO.setmode(RPIO.BCM)
#res = RPIO.gpio_function(10)
#print "res=",str(res)
#sys.exit()

v1 = valve.Valve(gpio_1_2 = 23)
print('default')
v1.default_way()
time.sleep(3)

print('power_on')
v1.power_on_way()
time.sleep(3)

v1.release()

RPIO.cleanup()
sys.exit()



#v1.way_1()
#v1.way_2()
#v1.way_1()

"""
v1.v1_turn_off()
time.sleep(3)
v1.v1_turn_on()
time.sleep(3)
#v1.v1_turn_off()
"""

