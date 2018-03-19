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

    def __init__(self, gpio_fs):
        super(Flow_sensor, self).__init__()
        self.clicks = 0
        self.lastClick = int(time.time() * self.MS_IN_A_SECOND)
        self.clickDelta = 0
        self.hertz = 0.0
        self.flow = 0.0
        self.thisPour = 0.0
        self.totalPour = 0.0
        self.enabled = True
        self.gpio_fs = gpio_fs
        self.gpio_list.append(gpio_fs)
        logging.info('init flow-sensor GPIO_flow={0}'.format(self.gpio_fs))

    def release(self):
        GPIO.remove_event_detect(self.gpio_fs)
        super(Flow_sensor, self).release()
        logging.debug("flow_sensor released")

    def watch_flow(self, flow_callback):
        GPIO.setup(self.gpio_fs, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.gpio_fs, GPIO.FALLING)
        GPIO.add_event_callback(self.gpio_fs, callback=flow_callback)

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

class FS_tester():

    def __init__(self, gpio_fs, flow_period):
        self.flow_sensor = Flow_sensor(gpio_fs=gpio_fs)
        self.flow_period = flow_period
        self.timers = []
        self.flow_timer = threading.Timer(self.flow_period, self.release)
        self.timers.append(self.flow_timer)

    def release(self):
        for t in self.timers:
            t.cancel()
        self.flow_sensor.release()

    def flow_detected(self, gpio_id):
        # self.timers.remove(self.flow_timer)
        # self.flow_timer = threading.Timer(self.flow_period, self.release)
        # self.timers.append(self.flow_timer)
        self.flow_sensor.handle_click()
        print "flow_count={0} V={1} Pour={2}".format(self.flow_sensor.clicks, self.flow_sensor.flow*3600, self.flow_sensor.thisPour)
                    


def countPulse(gpio_id):
    global fs
    # fst.flow_sensor.handle_click()
    fs.handle_click()
    print "Count={0} V={1} Pour={2}".format(fs.clicks, fs.flow*3600, fs.thisPour)

if __name__ == "__main__":
    import sys
    import threading
    gpio_fs = 11
    fst = FS_tester(gpio_fs, 3)
    # fs = Flow_sensor(gpio_fs)
    # fs.watch_flow(countPulse)
    fst.flow_sensor.watch_flow(fst.flow_detected)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print '\ncaught keyboard interrupt!, bye'
            fst.release()
            sys.exit()
