#!/usr/bin/python -t
# -*- coding: utf-8 -*-

import threading
import logging
import signal
import time


def hello():
    print " world"


class Cooker_stub(object):

    def __init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def switch_on(self):
        logging.debug('switch_on')

    def switch_off(self):
        logging.debug('switch_off')


class SomeClass(object):

    def __init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.cooker = Cooker_stub()
        self.cooker_period = 10
        self.cooker_timeout = 2
        # self.cooker_timer = threading.Timer(self.cooker_period, self.cooker_off)
        self.cooker_timer = threading.Timer(self.cooker_period, hello)
        logging.debug(self.cooker_timer.interval)

    def cooker_off(self):
        self.cooker.switch_off()
        self.cooker_pause_timer = threading.Timer(self.cooker_timeout, self.cooker_on)

    def cooker_on(self):
        self.cooker.switch_on()
        self.cooker_timer = threading.Timer(self.cooker_period, self.cooker_off)

if __name__ == "__main__":
    import os

    def signal_handler(signal, frame):
        global flag_do
        flag_do = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    log_dir = ''
    log_format = '[%(filename)-20s:%(lineno)4s - %(funcName)20s()] %(levelname)-7s | %(asctime)-15s | %(message)s'

    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    logging.basicConfig(filename=prg_name+'.log', format=log_format, level=logging.DEBUG)

    logging.info('Started')
    o = SomeClass()
    flag_do = True
    while flag_do:
        time.sleep(1)
        is_alive = o.cooker_timer.is_alive()
        logging.debug('loop, cooker_timer.is_alive={0}'.format(is_alive))

    logging.info('Finished')
