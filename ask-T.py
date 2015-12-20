#!/usr/bin/python -t
from __future__ import print_function
from w1thermsensor import W1ThermSensor
from time import sleep
import signal 
import sys
import time

def signal_handler(signal, frame):
    global loop_flag
    loop_flag = False
    # log.close()
    # sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print("Create sensor")
sensor = W1ThermSensor()
print("Sensor is created")

log = open('sensor-'+time.strftime("%Y-%m-%d-%H-%M") +'.csv','w')
loop_flag = True
while loop_flag:
    temperature_in_celsius = sensor.get_temperature()
    print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius), file=log)
    print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius))
    sleep(2)

log.close()
sys.exit(0)

# sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0000066c6502")
# ll /sys/bus/w1/devices/
