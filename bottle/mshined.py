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


@route('/todo')
def todo_list():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT id, task FROM todo WHERE status LIKE '1'")
    result = c.fetchall()
    c.close()
    output = template('show_table', rows=result, timestamp=datetime.now())
    return output
    # return str(result)

@route('/timer')
def timer_show():
    output = template('timer_show')
    return output

@route('/ask_timer')
def ask_timer():
    return str(datetime.now())

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
    if curr_temperature >= 0.5:
        snd_play = '<audio autoplay src="Zoop.wav">Your browser does not support the audio element. </audio>'
    	return str(curr_temperature) + snd_play
    else:       
	    return str(curr_temperature)

#add this at the very end:
debug(True)

w1_emu = False
try:
    sensor = w1thermsensor.W1ThermSensor()
#except Exception as ex:
except w1thermsensor.core.KernelModuleLoadError as ex:
    w1_emu = True
    Trange=[x * 0.1 for x in range(0, 102)]
    it = iter(Trange)
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    exit(0)

loc_host = socket.gethostbyname(socket.gethostname())
run(host=loc_host, reloader=True)


