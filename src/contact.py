#!/usr/bin/python3

from index import app
from os import environ
from flask import request, render_template
from requests import post, get
from uuid import uuid4
from textwrap import dedent

def validate_turnstile(response: str, ip: str) -> bool:
    turnstile_secret = environ['TURNSTILE_SECRET']
    cf_response = post(
        url='https://challenges.cloudflare.com/turnstile/v0/siteverify',
        data={
            'secret': turnstile_secret,
            'response': response,
            'remoteip': ip,
            'idempotency_key': uuid4()
        },
        timeout=30
    ).json()

    return cf_response.get('success', False)

def send_to_discord(form: dict) -> bool:
    try:
        discord_hook = environ['DISCORD_WEBHOOK']
    except KeyError as e:
        app.logger.error(e.with_traceback())
        return False
    discord_msg = dedent(
        f'''
            __**New Contact Form Response**__

            **From:** {form.get('name')} <{form.get('email')}>

        ''')
    if form.get("message") == '':
        discord_msg += '*No Message*'
    else:
        discord_msg += f'>>> {form.get("message")}'
    discord_response = post(
        url=discord_hook,
        data={
        'username': form.get('name'),
        'content': discord_msg
        },
        timeout=30
    )
    if discord_response.status_code == 204:
        return True
    app.logger.error(discord_response.status_code, discord_response.text)
    return False

@app.route('/contact/', methods=('GET', 'POST'))
def contact():
    if request.method == 'POST':
        if not validate_turnstile(request.form['cf-turnstile-response'], request.remote_addr):
            return render_template('contact.html', error=True, user_message='You appear to be a robot.')
        send_result = send_to_discord(request.form)
        if send_result:
            return render_template('contact.html', user_message='Your message has been sent!')
        return render_template('contact.html', error=True, user_message='An error occurred.')
    else:
        return render_template('contact.html', page_title='Contact - ')
