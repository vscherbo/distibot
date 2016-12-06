#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
from mshinectl import Moonshine_controller
import sys
import socket
# import signal
import thread
# import time
import webapp.mshine_httpd as mshine_httpd
# from bottle import Bottle
# from bottle import route, run, debug, template, static_file, request, get, post, ServerAdapter, Bottle
from bottle import debug, template, static_file, Bottle
import argparse

webapp_path = 'webapp'

parser = argparse.ArgumentParser(description='Moonshine controller .')
parser.add_argument('--conf', type=str, help='config file')
parser.add_argument('--emu', action="store_true",  help='emu mode')
parser.add_argument('--log', type=str, default="DEBUG", help='log level')
args = parser.parse_args()


def signal_handler(signal, frame):
    global mshinectl
    # global do_flag
    global server
    global app
    print("signal_handler release")
    mshinectl.stop_process()
    mshinectl.release()
    app.close()
    server.stop()
    # do_flag = False

# signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGHUP, signal_handler)
# signal.signal(signal.SIGTERM, signal_handler)

mshinectl = Moonshine_controller(args.emu)
mshinectl.load_config(args.conf)
# mshinectl.load_config('msc-body-from-raw.conf')
# mshinectl.load_config('msc-now.conf')

try:
    thread.start_new_thread(mshinectl.temperature_loop, ())
except Exception, exc:
    print("Error: unable to start thread, exception=%s" % str(exc))

# ################################
app = Bottle()


@app.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    print("CSS")
    return static_file(filename, root=webapp_path + '/static/css')


@app.get('/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root=webapp_path + '/static/js')


@app.get('/<filename:re:.*\.png>')
def images(filename):
    return static_file(filename, root=webapp_path + '/static/images')

"""
@app.get('/<filename:re:.*\.wav>')
def stylesheets(filename):
    return static_file(filename, root=webapp_path + '/static/sound')
"""


@app.route('/push_accepted', methods=['GET', 'POST'])
def push_accepted():
    global ack_button_display
    # do something
    # new = request.POST.get('value', '').strip()
    # print new
    ack_button_display = False

    hide_btn = """
        <script>
        var button_ack = document.getElementById('button_ack');
        button_ack.style.display = 'none'
        </script>
    """
    return hide_btn


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


@app.route('/ask_stage')
def ask_stage():
    global mshinectl
    enable_icon = """
        <script type="text/javascript">
        var div_icons = document.getElementsByClassName('stage');
        for (var i=0; i < div_icons.length; i++) {
            var stage = div_icons[i];
            if ('""" + mshinectl.stage + """_stage' == stage.id) {
                 stage.disabled = false;
            } else {
                 stage.disabled = true;
            }
        }
        </script>
    """
    return enable_icon

loc_host = socket.gethostbyname(socket.gethostname())
server = mshine_httpd.MshineHTTPD(host=loc_host, port=8080)

# add this at the very end:
debug(True)

try:
    app.run(server=server)
except Exception, ex:
    print(ex)
finally:
    mshinectl.stop_process()
    mshinectl.release()

print("Exiting!")
mshinectl.release()
sys.exit(0)
