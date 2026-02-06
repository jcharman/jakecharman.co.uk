#!/usr/bin/python3

import traceback
from os import environ, path
import threading
import logging
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit
from re import match
import json
from io import BytesIO
from requests import post
from flask import Flask, render_template, Response, url_for, request, send_from_directory, make_response
from PIL import Image, UnidentifiedImageError
from .content import ContentArea
from .contact import ContactForm
from .storage import LocalStorage
from .links import Links

app = Flask(__name__)

md_path = path.join(path.realpath(path.dirname(__file__)), path.normpath('../projects/'))

projects = ContentArea(
    directory=LocalStorage(md_path),
    name='projects',
    import_name=__name__)

app.register_blueprint(projects, url_prefix='/projects')
app.register_blueprint(ContactForm('contact', __name__), url_prefix='/contact')
app.register_blueprint(Links(path.join(md_path, 'links.json'), 'links', __name__), url_prefix='/links')

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

@app.context_processor
def inject_branding() -> dict:
    ''' Modify branding depending on the URL being used '''
    req_domain = urlsplit(request.base_url).netloc.lower()
    match req_domain:
        case 'jakecharman.co.uk':
            brand = 'Jake Charman'
        case _:
            brand = req_domain
    
    return {'branding': brand}

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

@app.route('/image/<image_name>')
def image( image_name: str) -> Response:
    ''' Resize and return an image. '''
    md_directory = LocalStorage(md_path)
    
    w = int(request.args.get('w', 0))
    h = int(request.args.get('h', 0))

    if w == 0 and h == 0:
        return send_from_directory(md_directory.uri, path.join('images', image_name))
    try:
        the_image = Image.open(path.join(md_directory.uri, 'images', image_name))
    except FileNotFoundError:
        return Response(status=404)
    except UnidentifiedImageError:
        return send_from_directory(md_directory.uri, path.join('images', image_name))

    max_width, max_height = the_image.size

    if (w >= max_width and h >= max_height):
        return send_from_directory(md_directory.uri, path.join('images', image_name))

    if path.exists(path.join('images', f'{w}-{h}-{image_name}')):
        return send_from_directory(md_directory.uri, path.join('images', f'{w}-{h}-{image_name}'))

    req_size = [max_width, max_height]
    if w > 0:
        req_size[0] = w
    if h > 0:
        req_size[1] = h

    resized_img = BytesIO()
    the_image.thumbnail(tuple(req_size))
    the_image.save(resized_img, format=the_image.format)
    the_image.save(path.join(md_directory.uri, 'images', f'{w}-{h}-{image_name}'), the_image.format)

    response = make_response(resized_img.getvalue())
    response.headers.set('Content-Type', f'image/{the_image.format}')
    return response
