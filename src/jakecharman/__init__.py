#!/usr/bin/python3

import traceback
from os import environ
import threading
import logging
import xml.etree.ElementTree as ET
from os import path
from re import match
import json
from requests import post
from flask import Flask, render_template, Response, url_for, request
from .content import ContentArea
from .contact import ContactForm
from .storage import LocalStorage

app = Flask(__name__)

md_path = path.join(path.realpath(path.dirname(__file__)), path.normpath('../projects/'))

projects = ContentArea(
    directory=LocalStorage(md_path),
    name='projects',
    import_name=__name__)

app.register_blueprint(projects, url_prefix='/projects')
app.register_blueprint(ContactForm('contact', __name__), url_prefix='/contact')

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

    if not code.isdigit():
        code=400
    elif int(code) not in error_definitions:
        return Response(status=code)

    return render_template('error.html',
                           error=f'{code}: {error_definitions.get(int(code))}',
                           description=error_desc.get(int(code)))

def get_routes() -> list:
    ''' Get a list of all routes that make up the app '''
    routes = []
    for rule in app.url_map.iter_rules():
        if 0 >= len(rule.arguments):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            routes.append(url)
    return routes

def get_build_date():
    ''' Get the build date of the Docker container we're running in '''
    try:
        with open('/var/www/jc/.buildinfo.json', encoding='utf8') as build:
            build_json = json.load(build)
            return build_json['date']
    except Exception: # pylint: disable=broad-exception-caught
        return '1970-01-01'

@app.route('/sitemap.xml')
def sitemap():
    ''' Return an XML site map '''
    date = get_build_date()
    root = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    base_url = match(r'^https?:\/\/.+:?\d*(?=\/)', request.base_url).group()
    base_url = base_url.replace('http://', 'https://')
    for route in get_routes():
        url = ET.SubElement(root, 'url')
        ET.SubElement(url, 'loc').text = base_url + route
        ET.SubElement(url, 'lastmod').text = date
    for article in projects.get_all_posts():
        if 'link' in article.metadata:
            continue
        url = ET.SubElement(root, 'url')
        ET.SubElement(url, 'loc').text = f'{base_url}/projects/{article.metadata['id']}'
        ET.SubElement(url, 'lastmod').text = article.metadata['date'].strftime('%Y-%m-%d')

    return Response(ET.tostring(root, encoding='utf-8'), 200, {'content-type': 'application/xml'})
