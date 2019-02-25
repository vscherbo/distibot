#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from __future__ import print_function
import logging
import argparse
import sys
import socket
import signal
import threading

# from bottle import Bottle
# from bottle import route, run, debug, template, static_file, request, get
# from bottle import post, ServerAdapter, Bottle
# from bottle import debug, template, static_file, Bottle
from bottle import template, static_file, Bottle
import plotly
# from plotly.graph_objs import Box
import plotly.graph_objs as pgo
# import Scatter, Layout, Margin

from distibot import Distibot
import webapp.distibot_httpd as distibot_httpd


# import numpy as np

webapp_path = 'webapp'

parser = argparse.ArgumentParser(description='Distillation robot .')
parser.add_argument('--play', type=str, required=True, help='config file')
parser.add_argument('--conf', type=str, default='distibot.conf',
                    help='config file')
parser.add_argument('--log', type=str, default="DEBUG", help='log level')
args = parser.parse_args()

log_format = '[%(filename)-18s:%(lineno)4s - %(funcName)18s()] %(levelname)-7s\
        | %(asctime)-15s | %(message)s'
# log_format = '%(asctime)-15s | %(levelname)-7s | %(message)s'
logging.basicConfig(filename='distibot.log', format=log_format,
                    level=logging.DEBUG)


def signal_handler(signal, frame):
    global dib
    global server
    global app
    logging.info('Catched signal {}'.format(signal))
    ### in main, finally section
    # dib.stop_process()
    # logging.info('after stop_process')
    # dib.release()
    # logging.info('after dib.release')
    server.stop()
    logging.info('after server.stop')
    app.close()
    logging.info('after app.close')


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGHUP, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGUSR1, signal_handler)

dib = Distibot(args.conf)
dib.load_script(args.play)
logging.debug('loaded script {0}.'.format(args.play))

try:
    t_dib = threading.Thread(target=dib.temperature_loop)
    t_dib.start()
    # thread.start_new_thread(dib.temperature_loop, ())
except Exception:
    logging.exception("Error: unable to start thread", exc_info=True)

# ################################
app = Bottle()
app.dib = dib


@app.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    # logging.debug("CSS")
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


@app.route('/ask_flow')
def ask_flow():
    if app.dib.loop_flag:
        return "{0} об.  {1} Hz".format(app.dib.flow_sensor.clicks,
                                        app.dib.flow_sensor.hertz)


@app.route('/ask_t')
def ask_temperature():
    if app.dib.loop_flag:
        # return "{0}".format(app.dib.tsensors.ts_data['boiler'])
        return "Куб:{0}, Хол:{1}".format(app.dib.tsensors.ts_data['boiler'],
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
        margin = pgo.Margin(b=100, l=35, pad=0, r=5, t=10)
        layout = pgo.Layout(autosize=True,
                            width=900, height=600,
                            margin=margin
                            )
        scatter = [pgo.Scatter(x=app.dib.coord_time,
                               y=app.dib.coord_temp,
                               name='Куб'),
                   pgo.Scatter(x=app.dib.coord_time,
                               y=app.dib.coord_temp_condenser,
                               name='Хол')]
        div_plot = plotly.offline.plot({"data": scatter, "layout": layout},
                                       show_link=False, output_type='div')
        return div_plot


loc_host = socket.gethostbyname(socket.gethostname())
server = distibot_httpd.DistibotHTTPD(host=loc_host, port=8080)


# add this at the very end:
# debug(True)


try:
    app.run(server=server)
except Exception:
    logging.exception('exception in app.run', exc_info=True)
finally:
    logging.info("app.run finally")
    dib.stop_process()
    logging.info('finally after stop_process')
    dib.release()
    logging.info('finally after dib.release')

logging.info("Exiting!")
sys.exit(0)
