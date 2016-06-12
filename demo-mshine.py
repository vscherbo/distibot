#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
import mshinectl 
import sys
import time

def signal_handler(signal, frame):
    global loop_flag
    loop_flag = False
    # log.close()
    # sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

alarm_limit = 1

def do_nothing():
    pass

mshinectl = Moonshine_controller()

#Talarms = [77.0, 79.0, 85.0, 88.0, 94.5, 98.5, 999.9] # 1st production

# Raw moonshine
Tsteps = {0.0 : mshinectl.start_process
          77.0: mshinectl.cooker.switch_off, 
          79.0: mshinectl.cooker.set_power_600, 
          85.0: mshinectl.start_watch_heads
          }
"""          
//          94.5, mshinectl.stop_body,
          98.5, mshinectl.finish,
          999.9: do_nothing}
"""          
"""
Tsteps = {0.0 : mshinectl.start_process
          77.0: mshinectl.cooker.switch_off, 
          79.0: mshinectl.cooker.set_power_600, 
          85.0: mshinectl.start_watch_heads, 
          94.5, mshinectl.stop_body,
          98.5, mshinectl.finish,
          999.9: do_nothing] # 1st production
"""

step_max = 2

log = open('sensor-'+time.strftime("%Y-%m-%d-%H-%M") +'.csv','w', 0) # 0 - unbuffered write
(Talarm, Tcmd) = Tsteps.pop(0)
loop_flag = True
step_counter = 0
while loop_flag:
    temperature_in_celsius = mshinectl.sensor.get_temperature()
    print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius), file=log)
    # print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius))
    step_counter += 1
    if step_counter >= step_max:
        step_counter = 0
        c.push_note("Превысили "+str(Talarm), str(temperature_in_celsius))
        print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius) +", Превысили "+str(Talarm), file=log)
        Tcmd
        (Talarm, Tcmd) = Tsteps.popitem(0, )
    # debug 
    # print("alarm_cnt="+str(alarm_cnt) + " Talarm=" + str(Talarm))
    time.sleep(5)

log.close()
sys.exit(0)
