#!/usr/bin/python3

import sqlite3
from os import path
from datetime import datetime
import json
from flask import request, Response, redirect
from index import app
from projects import md_directory, get_by_meta_key

database = '/tmp/db' #path.join(md_directory, 'comments.db')
with sqlite3.Connection(database) as db:
    db.execute('CREATE TABLE IF NOT EXISTS comments (date INTEGER, article TEXT, name TEXT, comment TEXT)')
    db.commit()

@app.route('/comments/<article>', methods=['GET', 'POST'])
def post_comments(article: str):
    match request.method:
        case 'POST':
            if len(get_by_meta_key(md_directory, 'id', article)) == 0:
                return Response(status=404)
            with sqlite3.Connection(database) as db:
                db.execute('INSERT INTO comments (date, article, name, comment) VALUES (?, ?, ?, ?)', (datetime.now(), article, request.form.get('name'), request.form.get('comment')))
                db.commit()
            return redirect(f'/projects/{article}')
        case 'GET':
            if len(get_by_meta_key(md_directory, 'id', article)) == 1:
                with sqlite3.Connection(database) as db:
                    res = db.execute('SELECT * FROM comments WHERE `article` = ?', (article,))
                    return json.dumps([{'author': x[2], 'date': x[0], 'comment': x[3]} for x in res.fetchall()])
