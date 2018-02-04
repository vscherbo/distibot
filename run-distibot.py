#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
from distibot import Distibot
import sys
import socket
# import signal
import thread
import webapp.distibot_httpd as distibot_httpd
# from bottle import Bottle
# from bottle import route, run, debug, template, static_file, request, get
# from bottle import post, ServerAdapter, Bottle
from bottle import debug, template, static_file, Bottle
import argparse

# import numpy as np

webapp_path = 'webapp'

parser = argparse.ArgumentParser(description='Distillation robot .')
parser.add_argument('--conf', type=str, help='config file')
parser.add_argument('--emu', action="store_true",  help='emu mode')
parser.add_argument('--log', type=str, default="DEBUG", help='log level')
args = parser.parse_args()


def signal_handler(signal, frame):
    global dib
    global server
    global app
    print("signal_handler release")
    dib.stop_process()
    dib.release()
    app.close()
    server.stop()

# signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGHUP, signal_handler)
# signal.signal(signal.SIGTERM, signal_handler)

dib = Distibot(emu_mode=args.emu)
dib.load_script(args.conf)


try:
    thread.start_new_thread(dib.temperature_loop, ())
except Exception, exc:
    print("Error: unable to start thread, exception=%s" % str(exc))

# ################################
import plotly
# from plotly.graph_objs import Box
from plotly.graph_objs import Scatter, Layout, Margin

app = Bottle()
app.dib = dib


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


@app.get('/<filename:re:.*\.html>')
def html_pages(filename):
    return static_file(filename, root=webapp_path + '/static/html')

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
    if app.dib.loop_flag:
        output = template('webapp/temperature_show')
        return output


@app.route('/ask_t')
def ask_temperature():
    if app.dib.loop_flag:
        return "{0} {1}".format(app.dib.tsensors.ts_data['boiler'],
                                app.dib.tsensors.ts_data['condenser'])


@app.route('/ask_stage')
def ask_stage():
    if app.dib.loop_flag:
        enable_icon = """
            <script type="text/javascript">
            var div_icons = document.getElementsByClassName('stage');
            for (var i=0; i < div_icons.length; i++) {
                var stage = div_icons[i];
                if ('""" + app.dib.stage + """_stage' == stage.id) {
                    stage.disabled = false;
                } else {
                    stage.disabled = true;
                }
            }
            </script>
        """
        return enable_icon


@app.route('/plot')
def plot():
    if app.dib.loop_flag:
        # prepare plot params
        margin = Margin(l=35, r=5, b=100, t=10, pad=0)
        layout = Layout(autosize=True, margin=margin, width=900, height=600)
        scatter = [Scatter(x=app.dib.coord_time, y=app.dib.coord_temp),
                   Scatter(x=app.dib.coord_time, y=app.dib.coord_temp_condenser)]
        div_plot = plotly.offline.plot({"data": scatter, "layout": layout},
                                       show_link=False, output_type='div')
        return div_plot


loc_host = socket.gethostbyname(socket.gethostname())
server = distibot_httpd.DistibotHTTPD(host=loc_host, port=8080)


# add this at the very end:
debug(True)

try:
    app.run(server=server)
except Exception, ex:
    print(ex)
finally:
    dib.stop_process()
    dib.release()

print("Exiting!")
sys.exit(0)
