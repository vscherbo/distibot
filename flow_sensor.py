#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)
# import GPIO_wrap.GPIO as GPIO
import RPi.GPIO as GPIO
import time
logger = logging.getLogger(__name__)
# hs_handler = logging.FileHandler('moonshine.log')
# hs_handler = logging.StreamHandler()
# formatter = logging.Formatter(log_format)
# hs_handler.setFormatter(formatter)
# logger.addHandler(hs_handler)


class Flow_sensor:
    PINTS_IN_A_LITER = 2.11338
    SECONDS_IN_A_MINUTE = 60
    MS_IN_A_SECOND = 1000.0
    displayFormat = 'metric'
    beverage = 'beer'
    enabled = True
    clicks = 0
    lastClick = 0
    clickDelta = 0
    hertz = 0.0
    flow = 0 # in Liters per second
    instPour = 0.0 # current flow
    thisPour = 0.0 # in Liters
    count = 0

    def __init__(self, gpio_flow_pin):
        self.clicks = 0
        self.lastClick = int(time.time() * self.MS_IN_A_SECOND)
        self.clickDelta = 0
        self.hertz = 0.0
        self.flow = 0.0
        self.thisPour = 0.0
        self.totalPour = 0.0
        self.enabled = True
        self.gpio_flow_pin = gpio_flow_pin
        logger.info('init flow-sensor GPIO_flow={0}'.format(self.gpio_flow_pin))

    def release(self):
        GPIO.setup(self.gpio_flow_pin, GPIO.OUT)
        print "flow_sensor released"

    def watch_flow(self, flow_callback):
        GPIO.setup(self.gpio_flow_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.gpio_flow_pin, GPIO.FALLING)
        GPIO.add_event_callback(self.gpio_flow_pin, callback=flow_callback)

    def update(self, currentTime):
        self.clicks += 1
        # get the time delta
        self.clickDelta = max((currentTime - self.lastClick), 1)
        # calculate the instantaneous speed
        if (self.enabled == True and self.clickDelta < 1000):
          self.hertz = self.MS_IN_A_SECOND / self.clickDelta
          self.myFlow = self.hertz /700
          # self.flow = self.hertz / (self.SECONDS_IN_A_MINUTE * 12.0)  # In Liters per second
          # instPour = self.flow * (self.clickDelta / self.MS_IN_A_SECOND)  
          self.instPour = self.myFlow * (self.clickDelta / self.MS_IN_A_SECOND)  
          self.thisPour += self.instPour
        # Update the last click
        self.lastClick = currentTime

    def countPulse(self, gpio_id):
       self.count = self.count+1
       currentTime = int(time.time() * self.MS_IN_A_SECOND)
       self.update(currentTime)
       print "Count={0} Pour={1}".format(self.clicks, self.thisPour)

if __name__ == "__main__":
    import time
    import sys
    GPIO.setmode(GPIO.BCM)
    channel=7
    fs = Flow_sensor(channel)
    fs.watch_flow(fs.countPulse)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print '\ncaught keyboard interrupt!, bye'
            fs.release()
            GPIO.remove_event_detect(channel)
            sys.exit()

