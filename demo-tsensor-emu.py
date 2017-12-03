#!/usr/bin/env python
# -*- coding: utf-8 -

import tsensor
import time

t1 = tsensor.Tsensor()

t_range = (20, 21, 22, -200, 23, 24, 25, 111, 26, 27)

t_prev = t_range[0]
print 't_prev={}'.format(t_prev)

for t in t_range:
    if abs((t-t_prev)/t_prev) > 0.3:
        t_curr = t_prev
    else:
        t_prev = t
        t_curr = t
    print t_curr


cnt = 4
while cnt < 3:
    print t1.get_temperature()
    cnt += 1
    time.sleep(1)
