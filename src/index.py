#!/usr/bin/python3

from flask import Flask, render_template, Response

app = Flask(__name__)

import projects

@app.route('/')
def index():
    print('blah')
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
        400: 'Sorry, we didn\'t understand your request.',
        403: 'Sorry, you aren\'t allowed to view this page.',
        404: 'Sorry, that page doesn\'t exist.',
        418: 'I can\'t brew coffee as I am, in fact, a teapot.',
        500: 'Something went wrong on our end.',
        503: 'Our website is experiencing some issues and will be back shortly.',
        505: 'Your browser tried to use a HTTP version we don\'t support. Check it is up to date.'
    }
    errorText = f'''
        <div id='error'>
            <h2>{code}: {error_definitions.get(int(code))}</h2>
            <p>{error_desc.get(int(code))}</p>
            <a href='/'>Click here to return to our homepage</a>
        </div>
    '''
    return render_template('error.html', post=errorText)