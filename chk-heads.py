#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)
import RPIO
import signal
import time
import heads_sensor


def signal_handler(signal, frame):
    global loop_flag
    loop_flag = False

signal.signal(signal.SIGINT, signal_handler)


def heads_started(gpio_id, value):
    global hs
    try:
        int(value)
    except ValueError:
        print("heads_started BAD value="+str(value))
        value = -1

    print(time.strftime("%Y-%m-%d-%H-%M-%S ") + "Стартовали головы", "gpio_id=" + str(gpio_id) +
          ", value=" + str(value))
    hs.ignore_start()
    hs.watch_stop(heads_finished),


def heads_finished(gpio_id, value):
    global hs
    try:
        int(value)
    except ValueError:
        print("heads_started BAD value="+str(value))
        value = -1

    print(time.strftime("%Y-%m-%d-%H-%M-%S ") + "Закончились головы", "gpio_id=" + str(gpio_id) +
          ", value=" + str(value))
    hs.ignore_stop()


hs = heads_sensor.Heads_sensor(gpio_heads_start=25, gpio_heads_stop=14,
                               timeout=2000)
hs.watch_start(heads_started),

loop_flag = True
step_counter = 0
while loop_flag:
    step_counter += 1
    print(step_counter)
    time.sleep(2)

hs.release()

#try:
#    RPIO.cleanup()
#except BaseException as e:
#    print('Exception while RPIO.cleanup ' + str(e))

print("Exiting")
