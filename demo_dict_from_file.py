#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
    demo parse play script for 2 tempersture sensors
"""   


from __future__ import print_function
import collections
import ConfigParser
import io
import logging

import inspect


class Distibot(object):
    """
    A stub distibot class
    """

    def __init__(self, conf_filename='distibot.conf'):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.parse_conf(conf_filename)
        self.outdir = 'output'  # TODO config

        self.loop_flag = True

    def call_log(self):
        stack = inspect.stack()
        the_class = stack[1][0].f_locals["self"].__class__
        the_method = stack[1][0].f_code.co_name
        logging.info("called %s.%s", the_class, the_method)

    def parse_conf(self, conf_filename):
        # Load and parse the conf file
        with open(conf_filename) as f:
            dib_config = f.read()
            self.config = ConfigParser.RawConfigParser(allow_no_value=True)
            self.config.readfp(io.BytesIO(dib_config))

    def load_script(self, play_filename):
        with open(play_filename, 'r') as script:
            self.Tsteps = collections.OrderedDict(sorted(eval(
                                                  script.read()).items(),
                                                  key=lambda t: t[0])
                                                  )
        logging.debug('Tsteps=%s', self.Tsteps)
        self.set_Tsteps()

    def set_Tsteps(self):
        self.Tkeys = self.Tsteps.keys()
        logging.debug('Tkeys=%s', self.Tkeys)

        self.Tstage = self.Tkeys.pop(0)
        logging.debug('Tstage[0]=%s', self.Tstage)
        self.Tstep_current = self.Tsteps.pop(self.Tstage)
        logging.debug('Tstep_current=%s', self.Tstep_current)
        logging.debug('type(Tstep_current)=%s', type(self.Tstep_current))
        #self.Tsensor, self.Tcmd = self.Tsteps[self.Tstage]
        #logging.debug('Tsensor=%s, Tcmd=%s', self.Tsensor, self.Tcmd)

    def start_process(self):
        self.call_log()

    def start_watch_heads(self):
        self.call_log()

    def stop_body(self):
        self.call_log()

    def finish(self):
        self.call_log()


if __name__ == "__main__":
    import argparse
    import os
    import sys
    import signal

    def dib_stop():
        global dib
        dib.stop_process()
        logging.info('after stop_process')
        dib.release()
        logging.info('after dib.release')

    def signal_handler(signal, frame):
        logging.info('Catched signal {}'.format(signal))
        dib_stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGUSR1, signal_handler)

    def segv_handler(signal, frame):
        logging.info('Catched signal {}'.format(signal))
        logging.info('frame.f_locals={}'.format(frame.f_locals))
        logging.info('frame: filename={}, function={}, line_no={}'.format(
                      frame.f_code.co_filename,
                      frame.f_code.co_name, frame.f_lineno))
        dib_stop()

    signal.signal(signal.SIGSEGV, segv_handler)

    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    # conf_file = prg_name +".conf"

    parser = argparse.ArgumentParser(description='Distibot module')
    parser.add_argument('--conf', type=str, default="distibot.conf",
                        help='conf file')
    parser.add_argument('--play', type=str, default="dib-debug-condenser.play",
                        help='play file')
    parser.add_argument('--log_to_file', type=bool, default=False,
                        help='log destination')
    parser.add_argument('--log_level', type=str, default="DEBUG",
                        help='log level')
    args = parser.parse_args()

    numeric_level = getattr(logging, args.log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {0}'.format(numeric_level))

    log_format = '[%(filename)-22s:%(lineno)4s - %(funcName)20s()] \
            %(levelname)-7s | %(asctime)-15s | %(message)s'
    # log_format = '%(asctime)-15s | %(levelname)-7s | %(message)s'

    if args.log_to_file:
        log_dir = ''
        log_file = log_dir + prg_name + ".log"
        logging.basicConfig(filename=log_file, format=log_format,
                            level=numeric_level)
    else:
        logging.basicConfig(stream=sys.stdout, format=log_format,
                            level=numeric_level)

    # end of prolog
    logging.info('Started')

    dib = Distibot(conf_filename=args.conf)
    dib.load_script(args.play)

    logging.info('Exit')
