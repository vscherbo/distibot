#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Distibot hall sensor

Handle <TODO sensor mark>
"""

import time
import logging
from gpio_dev import GPIO_DEV, GPIO

SECONDS_IN_A_MINUTE = 60
MS_IN_A_SECOND = 1000.0

class HallSensor(GPIO_DEV):
    """ Class handle hall sensor <sensor mark> """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, gpio_hs):
        """
        Args:
            gpio_hs (int): gpio number for hall sensor

        Attributes:
            clicks (int): number of registered clicks
            hertz (numeric): frequence of changes magnetic field


        """
        super(HallSensor, self).__init__()
        self.clicks = 0
        self.last_click = int(time.time() * MS_IN_A_SECOND)
        self.click_delta = 0
        self.hertz = 0.0
        self.gpio_hs = gpio_hs
        # self.gpio_list.append(gpio_hs)
        #logging.info('init hall-sensor GPIO_hall=%d', self.gpio_hs)

    def release(self):
        GPIO.remove_event_detect(self.gpio_hs)
        super(HallSensor, self).release()
        logging.info("hall_sensor released")

    def watch_magnet(self, hall_callback):
        """ Start watch an events on gpio_hs
        Args:
            hall_callback (function): callback for event

        """
        self.setup(self.gpio_hs, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.gpio_hs, GPIO.RISING)
        GPIO.add_event_callback(self.gpio_hs, callback=hall_callback)

    def handle_click(self):
        """ click handler calculates characterisitcs """
        current_time = int(time.time() * MS_IN_A_SECOND)
        self.clicks += 1
        # get the time delta
        self.click_delta = max((current_time - self.last_click), 1)
        # calculate a freq
        self.hertz = round(MS_IN_A_SECOND / self.click_delta)
        # Update the last click
        self.last_click = current_time


if __name__ == "__main__":
    import sys
    import threading

    LOG_FORMAT = '%(asctime)-15s | %(levelname)-7s | %(message)s'
    logging.basicConfig(stream=sys.stdout, format=LOG_FORMAT,
                        level=logging.INFO)
                        #level=logging.DEBUG)

    class HSTester():
        """ hall sensor tester class """

        def __init__(self, gpio_hs, hall_period):
            """ hall_period in seconds """
            self.hall_sensor = HallSensor(gpio_hs=gpio_hs)
            self.hall_period = hall_period
            self.timers = []
            self.do_flag = False
            self.hall_timer = threading.Timer(self.hall_period, self.no_hall)
            self.timers.append(self.hall_timer)

        def release(self):
            """ relase resources """
            logging.debug('HSTester.release')
            for timer in self.timers:
                timer.cancel()
            self.hall_sensor.release()
            self.do_flag = False

        def no_hall(self):
            """ called if timer is out """
            logging.warning('no magnet detected after hall_period=%d, exiting',
                            self.hall_period)
            self.release()

        def hall_detected(self, gpio_id):
            """ callback function for a hall sensor's event
            Args:
                gpio_id (int): it will be passed by RPi.GPIO

            """

            # pylint: disable=unused-argument

            self.hall_timer.cancel()
            self.timers.remove(self.hall_timer)

            self.hall_timer = threading.Timer(self.hall_period, self.no_hall)
            self.timers.append(self.hall_timer)
            self.hall_timer.start()

            self.hall_sensor.handle_click()
            #logging.info("hall_count=%d FREQ=%d", self.hall_sensor.clicks, self.hall_sensor.hertz)
            logging.info("hall_count=%d", self.hall_sensor.clicks)

    GPIO_HS = 18
    HST = HSTester(GPIO_HS, 5)
    HST.hall_sensor.watch_magnet(HST.hall_detected)
    HST.hall_timer.start()
    HST.do_flag = True
    while HST.do_flag:
        try:
            time.sleep(2)
            logging.debug('timer.is_alive=%s', HST.hall_timer.is_alive())
        except KeyboardInterrupt:
            logging.info('\ncaught keyboard interrupt!, bye')
            HST.release()
            sys.exit()
