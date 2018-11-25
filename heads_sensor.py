#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gpio_dev import GPIO_DEV, GPIO
import logging


class Heads_sensor(GPIO_DEV):

    def __init__(self, hs_type, gpio_heads_start, gpio_heads_finish, timeout=1000):
        super(Heads_sensor, self).__init__()

        if 'OPT' == hs_type:
            self.edge = GPIO.RISING
            self.PUD = GPIO.PUD_DOWN
            # self.edge = GPIO.FALLING
            # self.PUD = GPIO.PUD_UP
        elif 'RES' == hs_type:
            self.edge = GPIO.RISING
            self.PUD = GPIO.PUD_DOWN
        else:
            raise NameError('a wrong value=[{0}] for hs_type'.format(hs_type))

        self.timeout = timeout
        self.flag_ignore_start = True
        self.flag_ignore_finish = True
        #
        self.gpio_heads_start = gpio_heads_start
        self.gpio_list.append(gpio_heads_start)
        #
        self.gpio_heads_finish = gpio_heads_finish
        self.gpio_list.append(gpio_heads_finish)
        #
        hs_args = {'hs_type': hs_type,
                   'gpio_start': gpio_heads_start,
                   'gpio_finish': gpio_heads_finish}
        logging.info('init {hs_type} heads-sensor GPIO_start={gpio_start}, GPIO_finish={gpio_finish}'.format(**hs_args))

    def release(self):
        self.ignore_start()
        self.ignore_finish()
        super(Heads_sensor, self).release()
        logging.info("heads_sensor release")

    def ignore_start(self):
        if self.flag_ignore_start:
            logging.info('ignore_start: pass')
            pass
        else:
            self.flag_ignore_start = True
            # GPIO.remove_event_detect(self.gpio_heads_start)
            # logging.info('ignore_start: remove_event_detect on {0}'.format(self.gpio_heads_start))
            logging.info('ignore_start: FIRST')

    def ignore_finish(self):
        if self.flag_ignore_finish:
            logging.info('ignore_finish: pass')
            pass
        else:
            self.flag_ignore_finish = True
            # GPIO.remove_event_detect(self.gpio_heads_finish)
            # logging.info('ignore_finish: remove_event_detect on {0}'.format(self.gpio_heads_finish))
            logging.info('ignore_finish: FIRST')

    # TODO merge watch_start & watch_finish in a single method
    def watch_start(self, start_callback):
        self.flag_ignore_start = False
        GPIO.setup(self.gpio_heads_start, GPIO.IN, pull_up_down=self.PUD)
        GPIO.add_event_detect(self.gpio_heads_start, self.edge, bouncetime=self.timeout)
        GPIO.add_event_callback(self.gpio_heads_start, start_callback)

    def watch_finish(self, finish_callback):
        GPIO.setup(self.gpio_heads_finish, GPIO.IN, pull_up_down=self.PUD)
        self.ignore_start()
        self.flag_ignore_finish = False
        GPIO.add_event_detect(self.gpio_heads_finish, self.edge, bouncetime=self.timeout)
        GPIO.add_event_callback(self.gpio_heads_finish, finish_callback)

if __name__ == "__main__":
    import time
    import argparse
    import signal
    import os
    import sys
#    import ConfigParser
#    import io

    def segv_handler(signal, frame):
        logging.info('Catched signal {}'.format(signal))
        logging.info('frame.f_locals={}'.format(frame.f_locals))
        logging.info('frame: filename={}, function={}, line_no={}'.format(frame.f_code.co_filename, frame.f_code.co_name, frame.f_lineno))

    def signal_handler(signal, frame):
        global loop_flag
        logging.info('Catched signal {}'.format(signal))
        hs.release()
        loop_flag = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGUSR1, signal_handler)
    signal.signal(signal.SIGSEGV, segv_handler)

    log_dir = ''
    log_format = '[%(filename)-20s:%(lineno)4s - %(funcName)20s()] %(levelname)-7s | %(asctime)-15s | %(message)s'

    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    conf_file_name = "hs.conf"

    parser = argparse.ArgumentParser(description='Distibot "heads_sensor" module')
    parser.add_argument('--conf', type=str, default=conf_file_name, help='conf file')
    parser.add_argument('--log_to_file', type=bool, default=False, help='log destination')
    parser.add_argument('--log_level', type=str, default="DEBUG", help='log level')
    args = parser.parse_args()

    numeric_level = getattr(logging, args.log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % numeric_level)

    log_format = '[%(filename)-22s:%(lineno)4s - %(funcName)20s()] %(levelname)-7s | %(asctime)-15s | %(message)s'
    # log_format = '%(asctime)-15s | %(levelname)-7s | %(message)s'

    if args.log_to_file:
        log_dir = ''
        log_file = log_dir + prg_name + ".log"
        logging.basicConfig(filename=log_file, format=log_format, level=numeric_level)
    else:
        logging.basicConfig(stream=sys.stdout, format=log_format, level=numeric_level)

    hs = Heads_sensor(hs_type='OPT', gpio_heads_start=25, gpio_heads_finish=14, timeout=200)

    def heads_started(gpio_id):
        logging.debug('inside heads_started, gpio_id={}'.format(gpio_id))
        hs.watch_finish(heads_finished)

    def heads_finished(gpio_id):
        logging.debug('inside heads_finished, gpio_id={}'.format(gpio_id))
        hs.ignore_finish()

    hs.watch_start(heads_started)
    logging.info('Started')

    loop_flag = True
    step_counter = 0
    while loop_flag:
        step_counter += 1
        logging.info("step={step:>4}".format(step=step_counter))
        time.sleep(2)

    if loop_flag:  # not unset inside signal_handler
        hs.release()
