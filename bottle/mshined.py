#!/usr/bin/env python
# -*- coding: utf-8 -

import sqlite3
from datetime import datetime
from bottle import route, run, debug, template, static_file, request, get
from w1thermsensor import W1ThermSensor

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
    curr_temperature = sensor.get_temperature()
    if curr_temperature >= 23.0:
        snd_play = """<audio autoplay>
         <source src="Zoop.wav" type="audio/wav">
         Your browser does not support the audio element.
         </audio>"""
    	return str(curr_temperature) + snd_play
    else:       
	    return str(curr_temperature)

#add this at the very end:
debug(True)
sensor = W1ThermSensor()
run(host='192.168.2.106', reloader=True)


