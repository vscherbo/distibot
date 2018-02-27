#!/usr/bin/python -t
# -*- coding: utf-8 -*-

import threading
import logging
import signal
import time

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        pass

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


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
        self.flow = Cooker_stub()
        self.flow_period = 5
        self.flow_timer = threading.Timer(self.flow_period, self.emergency_off)
        self.flow_timer.start()

    def emergency_off(self):
        logging.debug('emergency_off')

    def flow_detected(self, gpio_id=-1):
        pass
        self.flow_timer.cancel()
        # self.flow_timer = threading.Timer(self.flow_period, self.release)
        # self.timers.append(self.flow_timer)


if __name__ == "__main__":
    import os
    import sys
    import thread

    def signal_handler(signal, frame):
        global flag_do
        global o
        if o.flow_timer:
            o.flow_timer.cancel()
        flag_do = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    log_dir = ''
    log_format = '[%(filename)-20s:%(lineno)4s - %(funcName)20s()] %(levelname)-7s | %(asctime)-15s | %(message)s'

    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    # logging.basicConfig(filename=prg_name+'.log', format=log_format, level=logging.DEBUG)
    logging.basicConfig(stream=sys.stdout, format=log_format, level=logging.DEBUG)

    logging.info('Started')
    o = SomeClass()

    """
    getch = _Getch()
    try:
        thread.start_new_thread(getch(), ())
    except Exception, exc:
        print("Error: unable to start thread, exception=%s" % str(exc))
    """

    flag_do = True
    while flag_do:
        time.sleep(1)
        is_alive = o.flow_timer.is_alive()
        flag_do = is_alive
        logging.debug('loop, is_alive={0}'.format(is_alive))
        # o.flow_detected()

    logging.info('Finished')
