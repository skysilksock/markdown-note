from flask import *
from flask_cors import CORS
from functools import wraps


import os
import configparser
import sqlite3
# import pysqlite3 as sqlite3

'''
+-------------+-------------+
|     列名    |     类型    |
+-------------+-------------+
|      id     |     INT     |
|   username  |   VARCHAR   |
|     date    |   VARCHAR   |
|    title    |   VARCHAR   |
|     text    |     TEXT    |
-----------------------------
'''

app = Flask(__name__)
CORS(app)


def sqlite(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        g.conn = sqlite3.connect("db/markdownNote.db")
        ans = func(*args, **kwargs)
        g.conn.close()
        return ans
    return wrapper


@app.route('/')
def Home():
    return "Hello World"


@app.route('/api/insert-note', methods=['POST'])
@sqlite
def insert_note():
    try:
        username = request.get_json()["username"] if "username" in request.get_json() else "admin"
        up_time = request.get_json()["time"]
        title = request.get_json()["noteName"]
        markdownText = request.get_json()["markdownText"].replace("'","''")
        sql_insert = f"insert into notes values(NULL,'{username}','{up_time}','{title}','{markdownText}')"
        print(sql_insert)
        g.conn.execute(sql_insert)
        g.conn.commit()
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(e)
        return jsonify({'status': 'no', 'info': str(e)})

@app.route('/api/get-note-list', methods=['POST'])
@sqlite
def get_note_list():
    try:
        username = request.get_json()["username"] if "username" in request.get_json() else "admin"
        date = request.get_json()["time"]
        sql_search = f"select id,title from notes where username='{username}' and date='{date}';"
        ans = g.conn.execute(sql_search).fetchall()
        return jsonify({'status': 'ok', 'data': ans})
    except Exception as e:
        print(e)
        return jsonify({'status': 'no', 'info': str(e)})

@app.route('/api/get-note', methods=['POST'])
@sqlite
def get_note():
    try:
        # username = request.get_json()["username"] if "username" in request.get_json() else "admin"
        # date = request.get_json()["time"]
        note_id = request.get_json()["id"]
        sql_search = f"select text from notes where id='{note_id}';"
        ans = g.conn.execute(sql_search).fetchone()[0]
        return jsonify({'status': 'ok', 'data': ans})
    except Exception as e:
        print(e)
        return jsonify({'status': 'no', 'info': str(e)})


@app.route('/api/delete-note', methods=['POST'])
@sqlite
def delete_note():
    note_id = request.get_json()["id"]
    sql_delete = f"delete from notes where id={note_id}"
    g.conn.execute(sql_delete)
    g.conn.commit()
    return jsonify({'status': 'ok'})


@app.route('/api/update-note', methods=['POST'])
@sqlite
def update_note():
    try:
        markdownText = request.get_json()["markdownText"].replace("'","''")
        Id = request.get_json()["id"]
        sql_update = f"update notes set text='{markdownText}' where id={Id}"
        g.conn.execute(sql_update)
        g.conn.commit()
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(e)
        return jsonify({'status': 'no', 'info': str(e)})

def configParse(path: str) -> tuple:
    config = configparser.ConfigParser()
    config.read(path)
    host = config['Server']['Host']
    port = config['Server']['Port']
    return host, port

if __name__ == '__main__':
    # print(os.getcwd())
    host, port = configParse("config.ini")
    app.run(host=host, debug=True, port=port)