#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)
# import RPIO_wrap.RPIO as RPIO
import RPIO
logger = logging.getLogger(__name__)
# hs_handler = logging.FileHandler('moonshine.log')
# hs_handler = logging.StreamHandler()
# formatter = logging.Formatter(log_format)
# hs_handler.setFormatter(formatter)
# logger.addHandler(hs_handler)


class Heads_sensor:

    def __init__(self, gpio_heads_start, gpio_heads_stop, timeout):
        self.timeout = timeout
        self.flag_ignore_start = True
        self.flag_ignore_stop = True
        self.gpio_heads_start = gpio_heads_start
        # RPIO.setup(self.gpio_heads_start,
        #            RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
        self.gpio_heads_stop = gpio_heads_stop
        # RPIO.setup(self.gpio_heads_stop, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
        hs_gpios = {'gpio_start': gpio_heads_start,
                    'gpio_stop': gpio_heads_stop}
        logger.info('init heads-sensor GPIO_start={gpio_start}, GPIO_stop={gpio_stop}'.format(**hs_gpios))

    def release(self):
        self.ignore_start()
        self.ignore_stop()
        print "heads_sensor ignore start and stop"
        # RPIO.stop_waiting_for_interrupts()
        # print "heads_sensor stop_waiting_for_interrupts"
        # RPIO.cleanup()

    def null_callback(self, gpio_id, value):
        try:
            int(value)
        except ValueError:
            print("null_callback BAD value="+str(value))
            value = -1
        pass

    def ignore_start(self):
        if self.flag_ignore_start:
            pass
        else:
            self.flag_ignore_start = True
            """
            try:
                logger.info('ignore_start: try del callback')
                RPIO.del_interrupt_callback(self.gpio_heads_start)
            except KeyError:
                pass
            """
            logger.info('ignore_start: add null_callback')
            RPIO.add_interrupt_callback(self.gpio_heads_start,
                                        self.null_callback,
                                        edge='rising',
                                        debounce_timeout_ms=self.timeout,
                                        pull_up_down=RPIO.PUD_DOWN)

    def ignore_stop(self):
        if self.flag_ignore_stop:
            pass
        else:
            self.flag_ignore_stop = True
            """
            try:
                logger.info('ignore_stop: try del callback')
                RPIO.del_interrupt_callback(self.gpio_heads_stop)
            except KeyError:
                pass
            """
            logger.info('ignore_stop: setup {0} as OUTPUT'.format(self.gpio_heads_start))
            RPIO.setup(self.gpio_heads_start, RPIO.OUT)
            """
            logger.info('ignore_stop: add null_callback')
            RPIO.add_interrupt_callback(self.gpio_heads_stop,
                                        self.null_callback,
                                        edge='rising',
                                        debounce_timeout_ms=self.timeout,
                                        pull_up_down=RPIO.PUD_DOWN)
            """

    def watch_start(self, start_callback):
        # self.ignore_stop()
        self.flag_ignore_start = False
        RPIO.setup(self.gpio_heads_start, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
        RPIO.wait_for_interrupts(threaded=True)
        RPIO.add_interrupt_callback(self.gpio_heads_start,
                                    start_callback,
                                    edge='rising',
                                    debounce_timeout_ms=self.timeout,
                                    pull_up_down=RPIO.PUD_DOWN)

    def watch_stop(self, stop_callback):
        self.ignore_start()
        self.flag_ignore_stop = False
        RPIO.setup(self.gpio_heads_stop, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
        RPIO.wait_for_interrupts(threaded=True)
        RPIO.add_interrupt_callback(self.gpio_heads_stop,
                                    stop_callback,
                                    edge='rising',
                                    debounce_timeout_ms=self.timeout,
                                    pull_up_down=RPIO.PUD_DOWN)
