#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
import RPIO_wrap.RPIO as RPIO
logger = logging.getLogger(__name__)
# hs_handler = logging.FileHandler('run-moonshine.log')
hs_handler = logging.StreamHandler()
formatter = logging.Formatter(log_format)
hs_handler.setFormatter(formatter)
logger.addHandler(hs_handler)


class Heads_sensor:

    def __init__(self, gpio_heads_start, gpio_heads_stop, timeout):
        self.timeout = timeout
        self.gpio_heads_start = gpio_heads_start
        # RPIO.setup(self.gpio_heads_start, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
        self.gpio_heads_stop = gpio_heads_stop
        # RPIO.setup(self.gpio_heads_stop, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
        self.heads = -1  # -1 - before heads, 0 - heads, 1 - after heads
        hs_gpios = {'gpio_start': gpio_heads_start, 'gpio_stop': gpio_heads_stop}
        logger.debug('init heads-sensor GPIO_start={gpio_start}, GPIO_stop={gpio_stop}'.format(**hs_gpios))

    def release(self):
        self.ignore_start()
        self.ignore_stop()
        RPIO.stop_waiting_for_interrupts()
        print "heads_sensor stop_waiting_for_interrupts"
        RPIO.cleanup()

    def null_callback(self, gpio_id, val):
        pass

    def ignore_start(self):
        try:
            RPIO.del_interrupt_callback(self.gpio_heads_start)
        except KeyError:
            pass
        """
        RPIO.add_interrupt_callback(self.gpio_heads_start,
                                    self.null_callback,
                                    edge='rising')
        """

    def ignore_stop(self):
        try:
            RPIO.del_interrupt_callback(self.gpio_heads_stop)
        except KeyError:
            pass
        """
        RPIO.add_interrupt_callback(self.gpio_heads_stop,
                                    self.null_callback,
                                    edge='rising')
        """

    def watch_start(self, start_callback):
        # self.ignore_stop()
        RPIO.setup(self.gpio_heads_start, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
        RPIO.add_interrupt_callback(self.gpio_heads_start,
                                    start_callback,
                                    edge='rising',
                                    debounce_timeout_ms=self.timeout,
                                    pull_up_down=RPIO.PUD_DOWN)
        RPIO.wait_for_interrupts(threaded=True)

    def watch_stop(self, stop_callback):
        self.ignore_start()
        RPIO.setup(self.gpio_heads_stop, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
        RPIO.add_interrupt_callback(self.gpio_heads_stop,
                                    stop_callback,
                                    edge='rising',
                                    debounce_timeout_ms=self.timeout,
                                    pull_up_down=RPIO.PUD_DOWN)
        RPIO.wait_for_interrupts(threaded=True)
