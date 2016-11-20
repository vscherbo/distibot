#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
from mshinectl import Moonshine_controller
import sys
import socket
import signal
import thread
# import time
import mshine_httpd
# from bottle import Bottle
# from bottle import route, run, debug, template, static_file, request, get, post, ServerAdapter, Bottle
from bottle import debug, template, static_file, Bottle

webapp_path = 'webapp'


def signal_handler(signal, frame):
    global mshinectl
    global do_flag
    global server
    print("signal_handler release")
    mshinectl.stop_process()
    mshinectl.release()
    server.stop()
    # do_flag = False

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

# ################################
loc_host = socket.gethostbyname(socket.gethostname())
app = Bottle()


@app.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    print("CSS")
    return static_file(filename, root=webapp_path + '/static/css')


@app.get('/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root=webapp_path + '/static/js')

"""
@app.get('/<filename:re:.*\.wav>')
def stylesheets(filename):
    return static_file(filename, root=webapp_path + '/static/sound')

@app.get('/<filename:re:.*\.png>')
def stylesheets(filename):
    return static_file(filename, root=webapp_path + '/static/images')
"""


# it works
@app.route('/tsensor')
def t_show():
    output = template('webapp/temperature_show')
    return output


@app.route('/ask_t')
def ask_temperature():
    global mshinectl
    curr_temperature = mshinectl.temperature_in_celsius
    return str(curr_temperature)

# add this at the very end:
debug(True)

server = mshine_httpd.MshineHTTPD(host=loc_host, port=8080)
server.set_msc(mshinectl=mshinectl)

try:
    app.run(server=server)
except Exception, ex:
    print(ex)

"""
do_flag = True
while do_flag:
    time.sleep(1)
    pass
"""

print("Exiting!")
sys.exit(0)
