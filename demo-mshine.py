#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
import collections
from mshinectl import Moonshine_controller
import sys
import signal
import time

def signal_handler(signal, frame):
    global loop_flag
    global mshinectl
    loop_flag = False
    print("release")
    mshinectl.release()
    # log.close()
    # sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

alarm_limit = 1

log = open('sensor-'+time.strftime("%Y-%m-%d-%H-%M") +'.csv','w', 0) # 0 - unbuffered write
mshinectl = Moonshine_controller(log = log)

#Talarms = [77.0, 79.0, 85.0, 88.0, 94.5, 98.5, 999.9] # 1st production

# Raw moonshine
Tsteps = collections.OrderedDict()
Tsteps[0.0] = mshinectl.start_process
Tsteps[77.0] = mshinectl.cooker.switch_off
Tsteps[79.0] = mshinectl.cooker.set_power_600
Tsteps[85.0] = mshinectl.start_watch_heads


"""          
//          94.5, mshinectl.stop_body,
          98.5, mshinectl.finish,
          999.9: mshinectl.do_nothing}
"""          
"""
Tsteps = {0.0 : mshinectl.start_process
          77.0: mshinectl.cooker.switch_off, 
          79.0: mshinectl.cooker.set_power_600, 
          85.0: mshinectl.start_watch_heads, 
          94.5, mshinectl.stop_body,
          98.5, mshinectl.finish,
          999.9: mshinectl.do_nothing] # 1st production
"""

step_max = 2

Tkeys = Tsteps.keys()
Talarm = Tkeys.pop(0)
Tcmd = Tsteps.pop(Talarm)

send_overflow = True

loop_flag = True
step_counter = 0
while loop_flag:
    temperature_in_celsius = mshinectl.sensor.get_temperature()
    print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius), file=log)
    # print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius))
    step_counter += 1
    if step_counter >= step_max:
        step_counter = 0
        if send_overflow:
            mshinectl.pb_channel.push_note("Превысили "+str(Talarm), str(temperature_in_celsius)+", Tcmd="+str(Tcmd.__name__))
            print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius) +", Превысили "+str(Talarm)+", Tcmd="+str(Tcmd.__name__), file=log)
        if Talarm > 100 and send_overflow: 
            send_overflow = False

        Tcmd()
        try:
            Talarm = Tkeys.pop(0)
        except IndexError:
            Talarm = 999.0
        Tcmd = Tsteps.pop(Talarm, mshinectl.do_nothing)

    # debug 
    # print("alarm_cnt="+str(alarm_cnt) + " Talarm=" + str(Talarm))
    time.sleep(5)

print("Exiting!")


log.close()
sys.exit(0)
