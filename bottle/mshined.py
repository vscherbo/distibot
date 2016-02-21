#!/usr/bin/env python
# -*- coding: utf-8 -

import socket, sys, os
import sqlite3
from datetime import datetime
from bottle import route, run, debug, template, static_file, request, get, post
#from w1thermsensor import W1ThermSensor
import w1thermsensor


# Static Routes
@get('/<filename:re:.*\.js>')
def javascripts(filename):
        return static_file(filename, root='static/js')

@get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='static/css')

@get('/<filename:re:.*\.wav>')
def stylesheets(filename):
    return static_file(filename, root='static/sound')

@get('/<filename:re:.*\.png>')
def stylesheets(filename):
    return static_file(filename, root='static/images')

@route('/push_accepted', methods=['GET', 'POST'])
def push_accepted():
    global ack_button_display, Talarm, w1_emu
    # do something
    # new = request.POST.get('value', '').strip()
    # print new
    ack_button_display = False
    if w1_emu:
        Talarm = Talarms_emu.pop(0)
    else:
        Talarm = Talarms.pop(0)

    hide_btn = """
        <script>
        var button_ack = document.getElementById('button_ack');
        button_ack.style.display = 'none'
        </script>
    """
    return hide_btn

# it works
@route('/tsensor')
def t_show():
    output = template('temperature_show')
    return output

@route('/ask_t')
def ask_temperature():
    global w1_emu, ack_button_display
    if w1_emu:
        #curr_temperature = 22
        curr_temperature = it.next()
    else:
        curr_temperature = sensor.get_temperature()
    if curr_temperature >= Talarm:
        ack_button_display = True
        snd_file = '/Zoop.wav'
    else:       
        snd_play = ''
        snd_file = ''
    # style_display = 'inline' if ack_button_display else 'none'
    if ack_button_display:
        style_display = 'block'
    else:
        style_display = 'none'
    snd_play="<script>var audio = document.getElementById('alarm_sound'); audio.src ='" + snd_file + "'; var button_ack = document.getElementById('button_ack'); button_ack.style.display ='" + style_display + "'; button_ack.textContent = 'Принято';</script>"
    return str(curr_temperature) + snd_play

#add this at the very end:
debug(True)

Talarms_emu = [25.0, 26.0, 26.5, 27, 28, 29, 30, 31, 999.9] # debug
Talarms = [77.0, 79.0, 87.0, 89.0, 95.0, 98.7, 999.9] # production

w1_emu = False
ack_button_display = True # False

try:
    sensor = w1thermsensor.W1ThermSensor()
    Talarm = Talarms.pop(0)
#except Exception as ex:
except w1thermsensor.core.KernelModuleLoadError as ex:
    w1_emu = True
    Talarm = Talarms_emu.pop(0)
    Trange=[x * 0.1 for x in range(242, 99999)]
    it = iter(Trange)
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    exit(0)


loc_host = socket.gethostbyname(socket.gethostname())
run(host=loc_host, reloader=True)

