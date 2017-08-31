#!/usr/bin/env python
# -*- coding: utf-8 -

import tsensor
import time

t1 = tsensor.Tsensor()

cnt = 0
T = 0
# while cnt < 3:
while T < 99.9:
    T = t1.get_temperature()
    print T
    cnt += 1
    # time.sleep(1)
