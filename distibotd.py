#!/usr/bin/env python
# -*- coding: utf-8 -

import socket
# from bottle import route, run, debug, template, static_file, request, get, post
from bottle import run, debug, static_file, template, Bottle

from distibot import Distibot
import sys
# import signal
import thread
import argparse

parser = argparse.ArgumentParser(description='Distillation robot .')
parser.add_argument('--conf', type=str, help='config file')
parser.add_argument('--emu', action="store_true",  help='emu mode')
parser.add_argument('--log', type=str, default="DEBUG", help='log level')
args = parser.parse_args()

webapp_path = 'webapp'


distibot = Distibot(args.emu)
distibot.load_config(args.conf)

app = application = Bottle()
app.dib = distibot


# ################################
import plotly
# from plotly.graph_objs import Box
from plotly.graph_objs import Scatter, Layout, Margin

"""
# Static Routes
@app.get('/<filename:re:.*\.js>')
def javascripts(filename):
        return static_file(filename, root='static/js')


@app.route('/')
def show_index():
    '''
    The front "index" page
    '''
    return 'Hello'


@app.route('/page/<page_name>')
def show_page(page_name):
    '''
    Return a page that has been rendered using a template
    '''
    return template('page', page_name=page_name)
"""


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
        return str(app.dib.temperature_in_celsius)


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
        div_plot = plotly.offline.plot({"data": [Scatter(x=app.dib.coord_time, y=app.dib.coord_temp)],
                                       "layout": layout},
                                       show_link=False, output_type='div')
        return div_plot


# add this at the very end:
debug(True)


try:
    thread.start_new_thread(distibot.temperature_loop, ())
except Exception, exc:
    print("Error: unable to start thread, exception=%s" % str(exc))


# add this at the very end:
debug(True)


if __name__ == '__main__':

    def signal_handler(signal, frame):
        global distibot
        global server
        global app
        print("signal_handler release")
        distibot.stop_process()
        distibot.release()
        app.close()

    # signal.signal(signal.SIGINT, signal_handler)
    # signal.signal(signal.SIGHUP, signal_handler)
    # signal.signal(signal.SIGTERM, signal_handler)

    loc_host = socket.gethostbyname(socket.gethostname())
    try:
        run(app=app,
            # server='python_server',
            host=loc_host,
            port=8080)
        # reloader=True
    except Exception, ex:
        print(ex)
    finally:
        distibot.stop_process()
        distibot.release()

    print("Exiting!")
    sys.exit(0)
