#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
from mshinectl import Moonshine_controller
import signal
import sys
import time
import thread


def signal_handler(signal, frame):
    global do_flag
    global mshinectl
    print("signal_handler release")
    mshinectl.release()
    do_flag = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGHUP, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

mshinectl = Moonshine_controller()
mshinectl.load_config('msc-body-from-raw.conf')
# mshinectl.load_config('msc-now.conf')

try:
    thread.start_new_thread(mshinectl.temperature_loop, ())
except Exception, exc:
    print("Error: unable to start thread, exception=%s" % str(exc))


do_flag = True
while do_flag:
    time.sleep(5)
    pass

print("Exiting!")
sys.exit(0)
