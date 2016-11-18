#!/usr/bin/env python
# -*- coding: utf-8 -

import tsensor
import time

t1=tsensor.tsensor()

cnt=0
while cnt < 3:
    print t1.get_temperature()
    cnt += 1
    time.sleep(1)
    
