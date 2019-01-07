#!/usr/bin/env python
# -*- coding: utf-8 -

# from bottle import route, run, get, post, request
# from bottle import template, static_file, debug
# from bottle Bottle
from bottle import ServerAdapter


class DistibotHTTPD(ServerAdapter):
    server = None

    def set_msc(self, distibot):
        self.dib = distibot

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw):
                    pass
            self.options['handler_class'] = QuietHandler
        self.server = make_server(self.host, self.port, handler,
                                  **self.options)
        self.server.serve_forever()

    def stop(self):
        # self.server.server_close() <- alternative but causes fd exception
        self.server.server_close()
        # self.server.shutdown()

# Static Routes

"""
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

"""

'''
@route('/push_accepted', methods=['GET', 'POST'])
def push_accepted():
    hide_btn = """
        <script>
        var button_ack = document.getElementById('button_ack');
        button_ack.style.display = 'none'
        </script>
    """
    return hide_btn
'''

"""
# it works
@route('/tsensor')
def t_show():
    output = template('temperature_show')
    return output

@route('/ask_t')
def ask_temperature():
    curr_temperature = dib.temperature_in_celsius
    return str(curr_temperature)

"""
#add this at the very end:
#debug(True)


# ################################
# loc_host = socket.gethostbyname(socket.gethostname())
# app = Bottle()
"""
server = MshineHTTPD(host=loc_host, port=8080)
try:
    app.run(server=server)
except Exception,ex:
    print ex
"""
