#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Distibot hall sensor

Handle <TODO sensor mark>
"""

import time
#import logging
from gpio_dev import GPIO_DEV, GPIO, logging

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
            last_click (time): time of last click
            click_delta (int): ...


        """
        super(HallSensor, self).__init__()
        self.clicks = 0
        self.last_click = time.time()
        self.click_delta = 0
        self.gpio_hs = gpio_hs
        self.setup(self.gpio_hs, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def __repr__(self):
        return 'field={}, last_change={}, delta={}'.format(self.field,\
               time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.last_click)),\
               self.click_delta) 

    @property
    def field(self):
        return self.input(self.gpio_hs)

    def release(self):
        GPIO.remove_event_detect(self.gpio_hs)
        super(HallSensor, self).release()
        logging.info("hall_sensor released")

    def watch_magnet(self, hall_callback):
        """ Start watch an events on gpio_hs
        Args:
            hall_callback (function): callback for event

        """
        GPIO.add_event_detect(self.gpio_hs, GPIO.BOTH)
        #GPIO.add_event_detect(self.gpio_hs, GPIO.BOTH, bouncetime=500)
        GPIO.add_event_callback(self.gpio_hs, callback=hall_callback)

    def handle_click(self):
        """ click handler calculates characterisitcs """
        current_time = time.time()
        self.clicks += 1
        # get the time delta
        self.click_delta = int(current_time - self.last_click)
        # Update the last click
        self.last_click = current_time


if __name__ == "__main__":
    import sys
    import threading

    LOG_FORMAT = '%(asctime)-15s | %(levelname)-7s | %(message)s'
    logging.basicConfig(stream=sys.stdout, format=LOG_FORMAT,
                        level=logging.INFO)

    class HSTester():
        """ hall sensor tester class """

        def __init__(self, gpio_hs, hall_period):
            """ hall_period in seconds """
            self.hall_sensor = HallSensor(gpio_hs=gpio_hs)
            logging.info("hall_sensor: %s", self.hall_sensor)
            self.hall_period = hall_period
            self.timers = []
            self.do_flag = False
            if self.hall_sensor.field:
                self.hall_timer = None
            else:
                self.hall_timer = threading.Timer(self.hall_period, self.no_hall)
                self.timers.append(self.hall_timer)
                self.hall_timer.start()

        def release(self):
            """ relase resources """
            logging.debug('HSTester.release')
            for timer in self.timers:
                timer.cancel()
            #if self.hall_timer:
            #    self.hall_timer.cancel()

            self.hall_sensor.release()
            self.do_flag = False

        def no_hall(self):
            """ called if timer is out """
            logging.warning('no magnet detected after hall_period=%d, exiting',
                            self.hall_period)
            self.release()

        def watch_magnet(self, callback):
            self.hall_sensor.watch_magnet(callback)

        def hall_detected(self, gpio_id):
            """ callback function for a hall sensor's event
            Args:
                gpio_id (int): it will be passed by RPi.GPIO

            """
            field = self.hall_sensor.input(gpio_id)
            logging.debug("field=%s", field)
            if field:
                self.hall_timer.cancel()
                self.timers.remove(self.hall_timer)
            else:
                self.hall_timer = threading.Timer(self.hall_period, self.no_hall)
                self.timers.append(self.hall_timer)
                self.hall_timer.start()
            #logging.debug("hall_count=%d", self.hall_sensor.clicks)
            logging.info("hall_sensor: %s", self.hall_sensor)

            self.hall_sensor.handle_click()

        def timer_status(self):
            """ return a timer status """
            if self.hall_timer:
                res = self.hall_timer.is_alive()
            else:
                res = 'not set'
            return res

    GPIO_HS = 18
    HST = HSTester(GPIO_HS, 5)
    HST.watch_magnet(HST.hall_detected)
    HST.do_flag = True
    while HST.do_flag:
        try:
            time.sleep(2)
            logging.debug('timer.is_alive=%s', HST.timer_status())
        except KeyboardInterrupt:
            logging.info('\ncaught keyboard interrupt!, bye')
            HST.release()
            sys.exit()
