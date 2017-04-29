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


class Flow_sensor:

    def __init__(self, gpio_flow_pin):
        self.gpio_flow_pin = gpio_flow_pin
        logger.info('init flow-sensor GPIO_flow={0}'.format(self.gpio_flow_pin))

    def release(self):
        RPIO.setup(self.gpio_flow_pin, RPIO.OUT)
        print "flow_sensor released"

    def watch_flow(self, flow_callback):
        RPIO.setup(self.gpio_flow_pin, RPIO.IN, pull_up_down=RPIO.PUD_UP)
        RPIO.wait_for_interrupts(threaded=True)
        RPIO.add_interrupt_callback(self.gpio_flow_pin,
                                    flow_callback,
                                    edge='falling',
#                                    debounce_timeout_ms=self.timeout,
                                    pull_up_down=RPIO.PUD_UP)


def countPulse(gpio_id, value):
   global count
   count = count+1
   print count

if __name__ == "__main__":
    import time
    import sys
    global count
    count = 0
    fs = Flow_sensor(7)
    fs.watch_flow(countPulse)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print '\ncaught keyboard interrupt!, bye'
            fs.release()
            RPIO.cleanup()
            sys.exit()

