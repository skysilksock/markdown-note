from flask import *
from flask_cors import CORS
from functools import wraps


import os
import configparser
# import sqlite3
import pysqlite3 as sqlite3

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

@app.route('/api/get-tags')
@sqlite
def get_tags():
    try:
        username = request.args.get('username')
        sql_search = f"select id,tag_name from tags where username='{username}';"
        ans = g.conn.execute(sql_search).fetchall()
        return jsonify({'status': 'ok', 'data': [{'id': a, 'name': b} for a, b in ans]})
    except Exception as e:
        print(e)
        return jsonify({'status': 'no', 'info': str(e)})

@app.route('/api/create-tag')
@sqlite
def create_tag():
    try:
        username = request.args.get('username')
        tag_name = request.args.get('tag_name')
        sql_insert = f"insert into tags values(NULL,'{tag_name}','{username}');"
        g.conn.execute(sql_insert)
        g.conn.commit()
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(e)
        return jsonify({'status': 'no', 'info': str(e)})


@app.route('/api/change-note-tag', methods=['POST'])
@sqlite
def change_note_tag():
    try:
        note_id = request.get_json()["note_id"]
        tag_id = request.get_json()["tag_id"]
        sql_update = f"update notes set tag_id='{tag_id}' where id={note_id};"
        g.conn.execute(sql_update)
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
        # sql_search = f"""select notes.text,tags.tag_name
        #                 from notes join tags on notes.tag_id=tags.id
        #                 where notes.id={note_id};"""
        sql_search = f"select text,tag_id from notes where id={note_id}"
        ans = g.conn.execute(sql_search).fetchone()
        return jsonify({'status': 'ok', 'data': ans})
    except Exception as e:
        return jsonify({'status': 'no', 'info': str(e)})

@app.route('/api/get-notes-by-tag')
@sqlite
def get_notes_by_tag():
    try:
        username = request.args.get('username')
        tag_id = request.args.get('tag_id')
        sql_search = f"select id,title from notes where username='{username}' and tag_id={tag_id};"
        ans = g.conn.execute(sql_search).fetchall()
        return jsonify({'status': 'ok', 'data': ans})
    except Exception as e:
        return jsonify({'status': 'no', 'info': str(e)})

@app.route('/api/get-all-notes')
@sqlite
def get_all_notes():
    try:
        username = request.args.get('username')
        sql_search = f"select id,title from notes where username='{username}';"
        ans = g.conn.execute(sql_search).fetchall()
        return jsonify({'status': 'ok', 'data': ans})
    except Exception as e:
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

@app.route('/api/get-database')
def get_database():
    assert os.path.exists("./db/markdownNote.db")
    return send_file("./db/markdownNote.db")

def configParse(path: str) -> tuple:
    assert os.path.exists(path)
    config = configparser.ConfigParser()
    config.read(path)
    host = config['Server']['Host']
    port = config['Server']['Port']
    return host, port

if __name__ == '__main__':
    # print(os.getcwd())
    host, port = configParse("config.ini")
    app.run(host=host, debug=True, port=port)