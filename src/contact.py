#!/usr/bin/python3

from index import app
from os import environ
from flask import request, redirect, render_template



@app.route('/contact/', methods=('GET', 'POST'))
def contact():
    if request.method == 'POST':
        discord_hook = environ['DISCORD_WEBHOOK']
        print(discord_hook)
        print(request.form)
        return redirect('/contact/')
    else:
        return render_template('contact.html')
