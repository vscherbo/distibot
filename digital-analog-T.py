#!/usr/bin/python -t
from __future__ import print_function
from w1thermsensor import W1ThermSensor
from thermocouples_reference import thermocouples
import RPi.GPIO as GPIO
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

CS = 8
DOUT = 9
CLK = 11

vc = 4.97
Tref=22.5
R2=138 

R1=471
R2=R2 + 1013
coef = 1 + R2*1000.0/R1

print('coef=' + str(coef))

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(CS, GPIO.OUT)
GPIO.setup(DOUT, GPIO.IN)
GPIO.setup(CLK, GPIO.OUT)

typeK = thermocouples['K']

print("Create sensor")
sensor = W1ThermSensor()
print("Sensor is created")

log = open('sensor-'+time.strftime("%Y-%m-%d-%H-%M") +'.csv','w')
loop_flag = True
while loop_flag:
    # digital sensor
    temperature_in_celsius = sensor.get_temperature()
    #print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius), file=log)
    #print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius))

    # thermocouple
    GPIO.output(CS, True)
    GPIO.output(CLK, True)
    GPIO.output(CS, False)
    binData = 0
    i1 = 14

    while (i1 >= 0):
        GPIO.output(CLK, False)
        bitDOUT = GPIO.input(DOUT)
        GPIO.output(CLK, True)
        bitDOUT = bitDOUT << i1
        binData |= bitDOUT
        i1 -= 1

    GPIO.output(CS, True)
    binData &= 0xFFF
    Vadc = vc * binData/4096.0
    Voltage = round(Vadc, 4)
    Vt = Vadc/coef
    T = round(typeK.inverse_CmV(Vt*1000, Tref=Tref), 4)
    T0 = round(typeK.inverse_CmV(Vt*1000), 4)
    pr_str = '{0} T({1})={2}C, T0={3}C, Tdig={4}C' .format(time.strftime("%H:%M:%S"), Tref, T-T0, T0, temperature_in_celsius)
    print(pr_str)
    print(pr_str, file=log)
    
    sleep(2)

log.close()
sys.exit(0)

# sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0000066c6502")
# ll /sys/bus/w1/devices/

