#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cooker
from time import sleep

ck = cooker.Cooker(22,27,17)
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

