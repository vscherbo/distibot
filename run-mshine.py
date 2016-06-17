#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
import collections
from mshinectl import Moonshine_controller
import signal
import sys
import time


def signal_handler(signal, frame):
    global loop_flag
    global mshinectl
    print("signal_handler release")
    mshinectl.release()
    loop_flag = False
    # log.close()
    # sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGHUP, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

alarm_limit = 3

log = open('sensor-'
           + time.strftime("%Y-%m-%d-%H-%M")
           + '.csv', 'w', 0)  # 0 - unbuffered write
mshinectl = Moonshine_controller(log=log)

#Talarms = [77.0, 79.0, 85.0, 88.0, 94.5, 98.5, 999.9] # 1st production

# Raw moonshine
Tsteps = collections.OrderedDict()
Tsteps[0.0] = mshinectl.start_process
#Tsteps[77.0] = mshinectl.cooker.switch_off
Tsteps[79.0] = mshinectl.cooker.set_power_600
Tsteps[85.0] = mshinectl.start_watch_heads
Tsteps[98.5] = mshinectl.finish


"""
Tsteps = {0.0 : mshinectl.start_process
          77.0: mshinectl.cooker.switch_off,
          79.0: mshinectl.cooker.set_power_600,
          85.0: mshinectl.start_watch_heads,
          94.5, mshinectl.stop_body,
          98.5, mshinectl.finish,
          999.9: do_nothing] # 1st production
"""

Tkeys = Tsteps.keys()
Talarm = Tkeys.pop(0)
Tcmd = Tsteps.pop(Talarm)
Tcmd_prev = 'before start'
Tcmd_last = 'before start'

alarm_cnt = 0
loop_flag = True
while loop_flag:
    temperature_in_celsius = mshinectl.sensor.get_temperature()
    # print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius))
    if temperature_in_celsius > Talarm:
        Tcmd_last = Tcmd.__name__
        mshinectl.pb_channel.push_note("Превысили " + str(Talarm),
                                       str(temperature_in_celsius)
                                       + ", Tcmd=" + str(Tcmd.__name__))

        Tcmd()
        alarm_cnt += 1
        if alarm_cnt >= alarm_limit:
            alarm_cnt = 0
            try:
                Talarm = Tkeys.pop(0)
            except IndexError:
                Talarm = 999.0
            Tcmd = Tsteps.pop(Talarm, mshinectl.do_nothing)
    # debug
    # print("alarm_cnt="+str(alarm_cnt) + " Talarm=" + str(Talarm))
    csv_prefix = time.strftime("%H:%M:%S") + "," + str(temperature_in_celsius)
    if Tcmd_last == Tcmd_prev:
        print(csv_prefix, file=log)
    else:
        print(csv_prefix + "," + Tcmd_last, file=log)
        Tcmd_prev = Tcmd_last
    time.sleep(5)

print("Exiting!")
log.close()
sys.exit(0)

# sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0000066c6502")
# ll /sys/bus/w1/devices/
