#!/usr/bin/python3

from flask import Flask, render_template, Response

app = Flask(__name__)

import projects

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/error/<code>')
def error(code):
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
