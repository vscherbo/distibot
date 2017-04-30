#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)
# import RPIO_wrap.RPIO as RPIO
import RPIO
import time
logger = logging.getLogger(__name__)
# hs_handler = logging.FileHandler('moonshine.log')
# hs_handler = logging.StreamHandler()
# formatter = logging.Formatter(log_format)
# hs_handler.setFormatter(formatter)
# logger.addHandler(hs_handler)


class Flow_sensor:
    PINTS_IN_A_LITER = 2.11338
    SECONDS_IN_A_MINUTE = 60
    MS_IN_A_SECOND = 1000.0
    displayFormat = 'metric'
    beverage = 'beer'
    enabled = True
    clicks = 0
    lastClick = 0
    clickDelta = 0
    hertz = 0.0
    flow = 0 # in Liters per second
    thisPour = 0.0 # in Liters
    totalPour = 0.0 # in Liters
    count = 0

    def __init__(self, gpio_flow_pin):
        self.clicks = 0
        self.lastClick = int(time.time() * self.MS_IN_A_SECOND)
        self.clickDelta = 0
        self.hertz = 0.0
        self.flow = 0.0
        self.thisPour = 0.0
        self.totalPour = 0.0
        self.enabled = True
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

    def update(self, currentTime):
        self.clicks += 1
        # get the time delta
        self.clickDelta = max((currentTime - self.lastClick), 1)
        # calculate the instantaneous speed
        if (self.enabled == True and self.clickDelta < 1000):
          self.hertz = self.MS_IN_A_SECOND / self.clickDelta
          self.flow = self.hertz / (self.SECONDS_IN_A_MINUTE * 8.1)  # In Liters per second
          instPour = self.flow * (self.clickDelta / self.MS_IN_A_SECOND)  
          self.thisPour += instPour
          self.totalPour += instPour
        # Update the last click
        self.lastClick = currentTime

    def countPulse(self, gpio_id, value):
       self.count = self.count+1
       currentTime = int(time.time() * self.MS_IN_A_SECOND)
       self.update(currentTime)
       print "Count={0} Pour={1}".format(self.count, self.thisPour)

if __name__ == "__main__":
    import time
    import sys
    fs = Flow_sensor(7)
    fs.watch_flow(fs.countPulse)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print '\ncaught keyboard interrupt!, bye'
            fs.release()
            RPIO.cleanup()
            sys.exit()

