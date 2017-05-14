#!/usr/bin/env python
# -*- coding: utf-8 -

import socket
# from bottle import route, run, debug, template, static_file, request, get, post
from bottle import run, debug, static_file, template, Bottle

app = application = Bottle()


# Static Routes
@app.get('/<filename:re:.*\.js>')
def javascripts(filename):
        return static_file(filename, root='static/js')


@app.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='static/css')


@app.get('/<filename:re:.*\.png>')
def images(filename):
    return static_file(filename, root='static/images')


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


class StripPathMiddleware(object):
    '''
    Get that slash out of the request
    '''
    def __init__(self, a):
        self.a = a

    def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.a(e, h)


# add this at the very end:
debug(True)

if __name__ == '__main__':
    loc_host = socket.gethostbyname(socket.gethostname())
    run(app=StripPathMiddleware(app),
        # server='python_server',
        host=loc_host,
        port=8080)
    # reloader=True
