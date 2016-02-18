#!/usr/bin/env python
# -*- coding: utf-8 -

import socket, sys, os
import sqlite3
from datetime import datetime
from bottle import route, run, debug, template, static_file, request, get
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

# it works
@route('/tsensor')
def t_show():
    output = template('temperature_show')
    return output

@route('/ask_t')
def ask_temperature():
    global w1_emu
    if w1_emu:
        curr_temperature = it.next()
    else:
        curr_temperature = sensor.get_temperature()
    if curr_temperature >= Talarm:
        #snd_play = '<audio autoplay src="Zoop.wav"></audio>'
        snd_play="""
        <script>
        var audio = document.getElementById('alarm_sound');
        audio.src = 'Zoop.wav'
        </script>
        """
        #snd_play = 'Zoop.wav'
    else:       
        snd_play = ''
    return str(curr_temperature) + snd_play

#add this at the very end:
debug(True)

w1_emu = False
try:
    sensor = w1thermsensor.W1ThermSensor()
    Talarm = 25
#except Exception as ex:
except w1thermsensor.core.KernelModuleLoadError as ex:
    w1_emu = True
    Talarm = 90.5
    Trange=[x * 0.1 for x in range(0, 199)]
    it = iter(Trange)
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    exit(0)

loc_host = socket.gethostbyname(socket.gethostname())
run(host=loc_host, reloader=True)

