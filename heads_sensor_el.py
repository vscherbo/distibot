#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gpio_dev import GPIO_DEV, GPIO
import logging


class Heads_sensor(GPIO_DEV):

    def __init__(self, gpio_heads_start, gpio_heads_stop, timeout=1000):
        super(Heads_sensor, self).__init__()
        self.timeout = timeout
        self.flag_ignore_start = True
        self.flag_ignore_stop = True
        #
        self.gpio_heads_start = gpio_heads_start
        self.gpio_list.append(gpio_heads_start)
        #
        self.gpio_heads_stop = gpio_heads_stop
        self.gpio_list.append(gpio_heads_stop)
        #
        hs_gpios = {'gpio_start': gpio_heads_start,
                    'gpio_stop': gpio_heads_stop}
        logging.info('init heads-sensor GPIO_start={gpio_start}, GPIO_stop={gpio_stop}'.format(**hs_gpios))

    def release(self):
        self.ignore_start()
        self.ignore_stop()
        super(Heads_sensor, self).release()
        logging.info("heads_sensor release")

    def ignore_start(self):
        if self.flag_ignore_start:
            pass
        else:
            self.flag_ignore_start = True
            logging.info('ignore_start: remove_event_detect on {0}'.format(self.gpio_heads_start))
            GPIO.remove_event_detect(self.gpio_heads_start)

    def ignore_stop(self):
        if self.flag_ignore_stop:
            pass
        else:
            self.flag_ignore_stop = True
            logging.info('ignore_stop: remove_eventy_detect on {0}'.format(self.gpio_heads_stop))
            GPIO.remove_event_detect(self.gpio_heads_stop)

    # TODO merge watch_start & watch_stop in a single method
    def watch_start(self, start_callback):
        self.flag_ignore_start = False
        GPIO.setup(self.gpio_heads_start, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.gpio_heads_start, GPIO.RISING, bouncetime=self.timeout)
        GPIO.add_event_callback(self.gpio_heads_start, start_callback)

    def watch_stop(self, stop_callback):
        self.ignore_start()
        self.flag_ignore_stop = False
        GPIO.setup(self.gpio_heads_stop, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.gpio_heads_stop, GPIO.RISING, bouncetime=self.timeout)
        GPIO.add_event_callback(self.gpio_heads_stop, stop_callback)

if __name__ == "__main__":
    import time
    import signal
    import os
    log_dir = ''
    log_format = '[%(filename)-20s:%(lineno)4s - %(funcName)20s()] %(levelname)-7s | %(asctime)-15s | %(message)s'

    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    logging.basicConfig(filename=prg_name+'.log', format=log_format, level=logging.INFO)

    def signal_handler(signal, frame):
        global loop_flag
        loop_flag = False

    signal.signal(signal.SIGINT, signal_handler)

    def heads_started(gpio_id):
        global hs
        logging.info("{} Стартовали головы, gpio_id={}".format(time.strftime("%Y-%m-%d-%H-%M-%S"), gpio_id))
        hs.watch_stop(heads_finished)

    def heads_finished(gpio_id):
        global hs
        logging.info("{} Закончились головы, gpio_id={}".format(time.strftime("%Y-%m-%d-%H-%M-%S"), gpio_id))
        hs.ignore_stop()

    hs = Heads_sensor(gpio_heads_start=25, gpio_heads_stop=14,
                      timeout=2000)
    hs.watch_start(heads_started),

    loop_flag = True
    step_counter = 0
    while loop_flag:
        step_counter += 1
        logging.info("step={}".format(step_counter))
        time.sleep(2)

    hs.release()
