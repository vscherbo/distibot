#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
from mshinectl import Moonshine_controller
import sys
import socket
import signal
import thread
from bottle import route, run, debug, template, static_file, get
# request, post


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


# Static Routes
@get('/<filename:re:.*\.js>')
def javascripts(filename):
        return static_file(filename, root='static/js')


@get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='static/css')

"""
@get('/<filename:re:.*\.png>')
def stylesheets(filename):
    return static_file(filename, root='static/images')
"""


# it works
@route('/tsensor')
def t_show():
    output = template('temperature_show')
    return output


@route('/ask_t')
def ask_temperature():
    curr_temperature = mshinectl.sensor.get_temperature()
    return str(curr_temperature)

# add this at the very end:
debug(True)

loc_host = socket.gethostbyname(socket.gethostname())
run(host=loc_host, reloader=True)

print("Exiting!")
sys.exit(0)
