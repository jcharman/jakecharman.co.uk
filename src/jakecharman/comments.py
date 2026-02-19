#!/usr/bin/python3

import sqlite3
from flask import Blueprint, Response, request
from uuid import uuid4
from requests import post
from os import environ


class PostComments():
    def __init__(self, post_id: str, db_path: str):
        self.__db_path = db_path
        self.__post_id = post_id
        self._webhook = environ['DISCORD_WEBHOOK']
        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS comments (name TEXT, comment TEXT, date INT, post_id TEXT, approved BOOL, key TEXT)")
            self.comments = cursor.execute(
                "SELECT name, comment, date FROM comments WHERE approved = 1 AND post_id = ? ORDER BY date DESC",
                (post_id,)
                ).fetchall()

    def send_to_discord(self, name: str, comment: str, comment_id: int, key: str):
        ''' Send the message '''
        message_to_send = f'New comment from {name}\n\n{comment}'
        if len(message_to_send) > 2000:
            chars_to_lose = len(message_to_send) - 1900
            message_to_send = message_to_send[-chars_to_lose:]
        message_to_send += f'\n\n[Approve](https://jakecharman.co.uk/comments/approve/{comment_id}?key={key})'
        post(self._webhook, data={'content': message_to_send}, timeout=30)

    def make_comment(self, name: str, comment: str):
        with sqlite3.connect(self.__db_path) as db:
            key = str(uuid4())
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO comments (name, comment, date, post_id, approved, key) VALUES (?, ?, datetime('now'), ?, 0, ?)",
                (name, comment, self.__post_id, key)
                )
            db.commit()
            self.send_to_discord(name, comment, cursor.lastrowid, key)
            return cursor.lastrowid

class Approval(Blueprint):
    def __init__(self, db_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__db_path = db_path
        self.add_url_rule('/approve/<comment_id>', view_func=self.approve)

    def approve(self, comment_id: str):
        with sqlite3.connect(self.__db_path) as db:
            cursor = db.cursor()
            key = cursor.execute("SELECT key FROM comments WHERE rowid = ?", (comment_id,)).fetchone()[0]
        if request.args.get('key') == key:
            with sqlite3.connect(self.__db_path) as db:
                cursor = db.cursor()
                cursor.execute("UPDATE comments SET approved = 1 WHERE rowid = ?", (comment_id,))
                db.commit()
            return Response(status=200)
        return Response(status=403)
