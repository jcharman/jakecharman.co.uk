#!/usr/bin/python3

import traceback
from os import environ
import threading
import logging
from requests import post
from flask import Flask, render_template

app = Flask(__name__)

# These imports need to come after our app is defined as they add routes to it.
import projects # pylint: disable=wrong-import-position,unused-import
import contact  # pylint: disable=wrong-import-position,unused-import

class DiscordLogger(logging.Handler):
    ''' Simple logging handler to send a message to Discord '''

    level = logging.ERROR

    def __init__(self, webhook):
        super().__init__()
        self._webhook = webhook

    def send_to_discord(self, msg: logging.LogRecord):
        ''' Send the message '''
        if msg.exc_info is not None:
            message_to_send = f'{msg.msg}\n\n{"".join(traceback.format_exception(*msg.exc_info))}'
        else:
            message_to_send = msg.msg
        if len(message_to_send) > 2000:
            chars_to_lose = len(message_to_send) - 2000
            if msg.exc_info is not None:
                message_to_send = f'{msg.msg}\n\n{"".join(traceback.format_exception(*msg.exc_info))[-chars_to_lose:]}'
            else:
                message_to_send = msg.msg[-chars_to_lose:]
        post(self._webhook, data={'content': message_to_send}, timeout=30)

    def emit(self, record: logging.LogRecord) -> None:
        ''' Take in the record and start a new thread to send it to Discord '''
        app.logger.info('Sending error to Discord')
        dc_thread = threading.Thread(target=self.send_to_discord, args=[record])
        dc_thread.start()

discord_logger = DiscordLogger(environ['DISCORD_ERR_HOOK'])
app.logger.addHandler(discord_logger)

@app.route('/')
def index() -> str:
    ''' Load the homepage '''
    return render_template('index.html')

@app.route('/error/<code>')
def error(code) -> str:
    ''' Render a nicer error page for a given code '''
    error_definitions = {
        400: 'Bad Request',
        403: 'Forbidden',
        404: 'Page Not Found',
        418: 'I\'m a Teapot',
        500: 'Internal Server Error',
        503: 'Service Temporarily Unavailable',
        505: 'HTTP Version Not Supported'
    }
    error_desc = {
        400: 'Sorry, I didn\'t understand your request.',
        403: 'Sorry, you aren\'t allowed to view this page.',
        404: 'Sorry, that page doesn\'t exist.',
        418: 'I can\'t brew coffee as I am, in fact, a teapot.',
        500: 'Something went wrong on my end.',
        503: 'My website is experiencing some issues and will be back shortly.',
        505: 'Your browser tried to use a HTTP version I don\'t support. Check it is up to date.'
    }

    return render_template('error.html',
                           error=f'{code}: {error_definitions.get(int(code))}',
                           description=error_desc.get(int(code)))
