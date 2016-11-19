#!/usr/bin/env python
# -*- coding: utf-8 -

import socket, sys, os
import sqlite3
from datetime import datetime
from bottle import route, run, debug, template, static_file, request, get, post, ServerAdapter, Bottle
#from w1thermsensor import W1ThermSensor
import w1thermsensor


class MshineHTTPD(ServerAdapter):
    server = None

    def __init__(self, mshinectl):
        self.msc = mshinectl

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
        # self.server.server_close() <--- alternative but causes bad fd exception
        self.server.shutdown()

# ################################
# loc_host = socket.gethostbyname(socket.gethostname())
# app = Bottle()

# Static Routes
@app.get('/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='static/js')

@app.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='static/css')

@app.get('/<filename:re:.*\.wav>')
def stylesheets(filename):
    return static_file(filename, root='static/sound')

@app.get('/<filename:re:.*\.png>')
def stylesheets(filename):
    return static_file(filename, root='static/images')

@app.route('/push_accepted', methods=['GET', 'POST'])
def push_accepted():
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
    output = template('temperature_show')
    return output

@app.route('/ask_t')
def ask_temperature():
    curr_temperature = msc.temperature_in_celsius
    return str(curr_temperature)

#add this at the very end:
debug(True)

"""
server = MshineHTTPD(host=loc_host, port=8080)
try:
    app.run(server=server)
except Exception,ex:
    print ex
"""
