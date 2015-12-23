import sqlite3
from datetime import datetime
from bottle import route, run, debug, template, static_file, request, get

# Static Routes
@get('/<filename:re:.*\.js>')
def javascripts(filename):
        return static_file(filename, root='static/js')

@get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='static/css')


@route('/todo')
def todo_list():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT id, task FROM todo WHERE status LIKE '1'")
    result = c.fetchall()
    c.close()
    output = template('make_table', rows=result, timestamp=datetime.now())
    return output
    # return str(result)

@route('/timer')
def timer_show():
    output = template('timer_show')
    return output

@route('/ask_timer')
def ask_timer():
    return str(datetime.now())

#add this at the very end:
debug(True)
run(reloader=True)


