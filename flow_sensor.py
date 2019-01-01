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


if __name__ == "__main__":
    import sys
    import threading

    log_format = '%(asctime)-15s | %(levelname)-7s | %(message)s'
    numeric_level = logging.DEBUG
    logging.basicConfig(stream=sys.stdout, format=log_format, level=numeric_level)


    class FS_tester():

        def __init__(self, gpio_fs, flow_period):
            self.flow_sensor = Flow_sensor(gpio_fs=gpio_fs)
            self.flow_period = flow_period
            self.timers = []
            self.flow_timer = threading.Timer(self.flow_period, self.no_flow)
            self.timers.append(self.flow_timer)

        def release(self):
            logging.debug('FS_tester.release')
            for t in self.timers:
                t.cancel()
            self.flow_sensor.release()
            self.do_flag = False

        def no_flow(self):
            logging.warning('no flow detected after flow_period={}, exiting'.format(self.flow_period))
            self.release()

        def flow_detected(self, gpio_id):
            self.flow_timer.cancel()
            self.timers.remove(self.flow_timer)

            self.flow_timer = threading.Timer(self.flow_period, self.no_flow)
            self.timers.append(self.flow_timer)
            self.flow_timer.start()

            self.flow_sensor.handle_click()
            logging.debug("flow_count={0} V={1} Pour={2}".format(self.flow_sensor.clicks, self.flow_sensor.flow*3600, self.flow_sensor.thisPour))


    gpio_fs = 11
    fst = FS_tester(gpio_fs, 5)
    fst.flow_sensor.watch_flow(fst.flow_detected)
    fst.flow_timer.start()
    fst.do_flag = True
    while fst.do_flag:
        try:
            time.sleep(2)
            logging.debug('timer.is_alive={}'.format(fst.flow_timer.is_alive()))
        except KeyboardInterrupt:
            print '\ncaught keyboard interrupt!, bye'
            fst.release()
            sys.exit()
