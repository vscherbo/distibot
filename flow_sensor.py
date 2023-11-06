#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Distibot flow sensor

Handle <TODO sensor mark>
"""

import time
import logging
from gpio_dev import GPIO_DEV, GPIO

SECONDS_IN_A_MINUTE = 60
MS_IN_A_SECOND = 1000.0

class FlowSensor(GPIO_DEV):
    """ Class handle flow sensor <sensor mark> """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, gpio_fs):
        """
        Args:
            gpio_fs (int): gpio number for flow sensor

        Attributes:
            clicks (int): number of registered clicks
            hertz (numeric): frequence of rotation


        """
        #super(FlowSensor, self).__init__()
        super().__init__()
        self.clicks = 0
        self.last_click = int(time.time() * MS_IN_A_SECOND)
        self.click_delta = 0
        self.hertz = 0.0
        self.flow = 0.0  # in Liters per second
        self.this_pour = 0.0  # in Liters
        self.inst_pour = 0.0  # current flow
        self.gpio_fs = gpio_fs
        # self.gpio_list.append(gpio_fs)
        #logging.info('init flow-sensor GPIO_flow=%d', self.gpio_fs)

    def release(self):
        GPIO.remove_event_detect(self.gpio_fs)
        #super(FlowSensor, self).release()
        super().release()
        logging.info("flow_sensor released")

    def watch_flow(self, flow_callback):
        """ Start watch an events on gpio_fs
        Args:
            flow_callback (function): callback for event

        """
        self.setup(self.gpio_fs, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.gpio_fs, GPIO.FALLING)
        GPIO.add_event_callback(self.gpio_fs, callback=flow_callback)

    def handle_click(self):
        """ click handler calculates characterisitcs """
        current_time = int(time.time() * MS_IN_A_SECOND)
        self.clicks += 1
        # get the time delta
        self.click_delta = max((current_time - self.last_click), 1)
        # calculate the instantaneous speed
        self.hertz = round(MS_IN_A_SECOND / self.click_delta)
        self.flow = self.hertz * 1000 / 516  # 516Hz -> 1 Liter
        self.inst_pour = self.flow * (self.click_delta / MS_IN_A_SECOND)
        self.this_pour += self.inst_pour
        # Update the last click
        self.last_click = current_time

    def get_rpm(self):
        """ Returns current RPM value """
        return self.hertz

if __name__ == "__main__":
    import sys
    import threading

    LOG_FORMAT = '%(asctime)-15s | %(levelname)-7s | %(message)s'
    logging.basicConfig(stream=sys.stdout, format=LOG_FORMAT,
                        level=logging.DEBUG)

    class FSTester():
        """ flow sensor tester class """

        def __init__(self, gpio_fs, flow_period):
            self.flow_sensor = FlowSensor(gpio_fs=gpio_fs)
            self.flow_period = flow_period
            self.timers = []
            self.do_flag = False
            self.flow_timer = threading.Timer(self.flow_period, self.no_flow)
            self.timers.append(self.flow_timer)

        def release(self):
            """ relase resources """
            logging.debug('FSTester.release')
            for timer in self.timers:
                timer.cancel()
            self.flow_sensor.release()
            self.do_flag = False

        def no_flow(self):
            """ called if timer is out """
            logging.warning('no flow detected after flow_period=%d, exiting',
                            self.flow_period)
            self.release()

        def flow_detected(self, gpio_id):
            """ callback function for a flow sensor's event
            Args:
                gpio_id (int): it will be passed by RPi.GPIO

            """

            # pylint: disable=unused-argument

            self.flow_timer.cancel()
            self.timers.remove(self.flow_timer)

            self.flow_timer = threading.Timer(self.flow_period, self.no_flow)
            self.timers.append(self.flow_timer)
            self.flow_timer.start()

            self.flow_sensor.handle_click()
            logging.debug("flow_count=%d FREQ=%d", self.flow_sensor.clicks, self.flow_sensor.hertz)

    GPIO_FS = 5
    FST = FSTester(GPIO_FS, 5)
    FST.flow_sensor.watch_flow(FST.flow_detected)
    FST.flow_timer.start()
    FST.do_flag = True
    while FST.do_flag:
        try:
            time.sleep(2)
            logging.debug('timer.is_alive=%s', FST.flow_timer.is_alive())
        except KeyboardInterrupt:
            logging.info('\ncaught keyboard interrupt!, bye')
            FST.release()
            sys.exit()
