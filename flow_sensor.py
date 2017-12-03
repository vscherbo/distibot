#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gpio_dev import GPIO_DEV, GPIO
import time
import logging


class Flow_sensor(GPIO_DEV):
    SECONDS_IN_A_MINUTE = 60
    MS_IN_A_SECOND = 1000.0
    enabled = True
    clicks = 0
    lastClick = 0
    clickDelta = 0
    hertz = 0.0
    flow = 0  # in Liters per second
    instPour = 0.0  # current flow
    thisPour = 0.0  # in Liters

    def __init__(self, gpio_flow_pin):
        super(Flow_sensor, self).__init__()
        self.clicks = 0
        self.lastClick = int(time.time() * self.MS_IN_A_SECOND)
        self.clickDelta = 0
        self.hertz = 0.0
        self.flow = 0.0
        self.thisPour = 0.0
        self.totalPour = 0.0
        self.enabled = True
        self.gpio_flow_pin = gpio_flow_pin
        self.gpio_list.append(gpio_flow_pin)
        logging.info('init flow-sensor GPIO_flow={0}'.format(self.gpio_flow_pin))

    def release(self):
        GPIO.remove_event_detect(self.gpio_flow_pin)
        super(Flow_sensor, self).release()
        logging.debug("flow_sensor released")

    def watch_flow(self, flow_callback):
        GPIO.setup(self.gpio_flow_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.gpio_flow_pin, GPIO.FALLING)
        GPIO.add_event_callback(self.gpio_flow_pin, callback=flow_callback)

    def handle_click(self):
        currentTime = int(time.time() * self.MS_IN_A_SECOND)
        self.clicks += 1
        # get the time delta
        self.clickDelta = max((currentTime - self.lastClick), 1)
        # calculate the instantaneous speed
        if self.enabled is True:
            self.hertz = self.MS_IN_A_SECOND / self.clickDelta
            self.flow = self.hertz / 700
            self.instPour = self.flow * (self.clickDelta / self.MS_IN_A_SECOND)
            self.thisPour += self.instPour
        # Update the last click
        self.lastClick = currentTime


def countPulse(gpio_id):
    global fs
    fs.handle_click()
    print "Count={0} V={1} Pour={2}".format(fs.clicks, fs.flow*3600, fs.thisPour)

if __name__ == "__main__":
    import sys
    channel = 9
    fs = Flow_sensor(channel)
    fs.watch_flow(countPulse)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print '\ncaught keyboard interrupt!, bye'
            fs.release()
            sys.exit()
