#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
import collections
from mshinectl import Moonshine_controller
import signal
import sys
import time
import thread


def signal_handler(signal, frame):
    global do_flag
    global mshinectl
    print("signal_handler release")
    mshinectl.release()
    do_flag = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGHUP, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

mshinectl = Moonshine_controller()

# Talarms = [77.0, 79.0, 85.0, 88.0, 94.5, 98.5, 999.9] # 1st production

Tsteps = collections.OrderedDict()
# select body #########################
"""
Tsteps[0.0] = mshinectl.start_process
Tsteps[73.0] = mshinectl.cooker.switch_off
Tsteps[76.0] = mshinectl.cooker.set_power_600
Tsteps[85.0] = mshinectl.start_watch_heads
Tsteps[94.5] = mshinectl.stop_body_power_on
Tsteps[98.5] = mshinectl.finish
"""
"""
# Raw moonshine ########################
Tsteps[0.0] = mshinectl.start_process
Tsteps[75.0] = mshinectl.cooker.switch_off
Tsteps[79.0] = mshinectl.cooker.set_power_600
Tsteps[85.0] = mshinectl.start_watch_heads
Tsteps[98.5] = mshinectl.finish
"""

# 2nd pass: cut tails ##################
Tsteps[0.0] = mshinectl.start_process
Tsteps[73.0] = mshinectl.cooker.switch_off
Tsteps[76.0] = mshinectl.wait4body
Tsteps[94.5] = mshinectl.stop_body
Tsteps[98.5] = mshinectl.finish

"""
Tsteps = {0.0 : mshinectl.start_process
          75.0: mshinectl.cooker.switch_off,
          79.0: mshinectl.cooker.set_power_600,
          85.0: mshinectl.start_watch_heads,
          94.5, mshinectl.stop_body,
          98.5, mshinectl.finish,
          999.9: do_nothing] # 1st production
"""

mshinectl.set_Tsteps(Tsteps)

try:
    thread.start_new_thread(mshinectl.temperature_loop)
except Exception, exc:
    print("Error: unable to start thread, exception=%s" % str(exc))


do_flag = True
while do_flag:
    time.sleep(5)
    pass

print("Exiting!")
sys.exit(0)

# sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0000066c6502")
# ll /sys/bus/w1/devices/
