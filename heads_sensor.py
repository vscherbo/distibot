#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPIO


class Heads_sensor:

    def __init__(self, gpio_heads_start, gpio_heads_stop, timeout):
        self.timeout = timeout
        self.gpio_heads_start = gpio_heads_start
        RPIO.setup(self.gpio_heads_start, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
        self.gpio_heads_stop = gpio_heads_stop
        RPIO.setup(self.gpio_heads_stop, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
        self.heads = -1  # -1 - before heads, 0 - heads, 1 - after heads

    def release(self):
        #self.ignore_start()
        #self.ignore_stop()
        #RPIO.cleanup()
        pass

    def null_callback(self, gpio_id, val):
        pass

    def ignore_start(self):
        RPIO.add_interrupt_callback(self.gpio_heads_start
                ,self.null_callback
                ,edge='rising')

    def watch_start(self, start_callback):
        self.ignore_stop()
        RPIO.setup(self.gpio_heads_start, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
        RPIO.add_interrupt_callback(self.gpio_heads_start,
                                    start_callback,
                                    edge='rising',
                                    debounce_timeout_ms=self.timeout,
                                    pull_up_down=RPIO.PUD_DOWN)
        RPIO.wait_for_interrupts(threaded=True)

    def ignore_stop(self):
        RPIO.add_interrupt_callback(self.gpio_heads_stop
                ,self.null_callback
                ,edge='rising')

    def watch_stop(self, stop_callback):
        self.ignore_start()
        RPIO.setup(self.gpio_heads_stop, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
        RPIO.add_interrupt_callback(self.gpio_heads_stop,
                                    stop_callback,
                                    edge='rising',
                                    debounce_timeout_ms=self.timeout,
                                    pull_up_down=RPIO.PUD_DOWN)
        RPIO.wait_for_interrupts(threaded=True)
