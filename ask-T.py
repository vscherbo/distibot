#!/usr/bin/python -t
from __future__ import print_function
from w1thermsensor import W1ThermSensor
from time import sleep
from pushbullet import Pushbullet
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

pb = Pushbullet('XmJ61j9LVdjbPyKcSOUYv1k053raCeJP')
# one_plus_one = pb.get_device('OnePlus One')
c = [x for x in pb.channels if x.name == u"Billy's moonshine"][0]


# Title, Message_body
# to device
# push = one_plus_one.push_note("Процесс", "Тело.")
# push = pb.push_note("Hello world!", "We're using the api.", device=one_plus_one)
# to channel
# c.push_note("Hello "+ c.name, "Hello My Channel")

log = open('sensor-'+time.strftime("%Y-%m-%d-%H-%M") +'.csv','w', 0) # 0 - unbuffered write
loop_flag = True
while loop_flag:
    temperature_in_celsius = sensor.get_temperature()
    print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius), file=log)
    # print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius))
    if temperature_in_celsius > 25.0:
        c.push_note("Превысили 25", str(temperature_in_celsius))
    sleep(10)

log.close()
sys.exit(0)

# sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0000066c6502")
# ll /sys/bus/w1/devices/
