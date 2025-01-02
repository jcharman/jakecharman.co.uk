#!/usr/bin/python3

from os import path
import json
from flask import Flask, render_template, Response, send_from_directory
from markdown import markdown
import frontmatter
from glob import glob
from datetime import datetime


application = Flask(__name__)
app = application
md_directory = path.join(path.realpath(path.dirname(__file__)), path.normpath('projects/'))

@app.context_processor
def processor():
    def get_excerpt(post):
        html = markdown(post.content)
        post_soup = BeautifulSoup(html, 'html.parser')
        all_text = ' '.join([x.get_text() for x in post_soup.findAll('p')])
        return ' '.join(all_text.split()[:200])
    return dict(get_excerpt=get_excerpt)

@app.template_filter('human_date')
def human_date(iso_date: str) -> str:
    try:
        return datetime.fromisoformat(str(iso_date)).strftime('%A %d %B %Y')
    except ValueError:
        return iso_date

@app.template_filter('to_html')
def to_html(content):
    return markdown(content)

def get_all_posts(directory: str) -> list:
    abs_paths = [path.join(directory, x) for x in glob(f'{directory}/*.md')]
    return [frontmatter.load(x) for x in abs_paths]

def get_by_meta_key(directory: str, key: str, value: str):
    return [x for x in get_all_posts(directory) if x.get(key) == value]

@app.route('/')
def index():
    articles_to_return = sorted(
        get_all_posts(
            md_directory), 
            key=lambda d: d.metadata.get('date'),
            reverse=True
        )

    return render_template('projects.html', articles=articles_to_return)

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

@app.route('/<category>/')
def category(category):
    with open(path.join(md_directory, 'categories.json')) as categories_file:
        categories = json.load(categories_file)

    the_category = next((x for x in categories if x.get('id') == category), None)

    if the_category is None:
        return Response(status=404)

    articles_to_return = sorted(
        get_by_meta_key(
            md_directory, 'category', category), 
            key=lambda d: d.metadata.get('date'),
            reverse=True
        )

    return render_template('projects.html', articles=articles_to_return,
                           title=the_category['title'], 
                           description=the_category['long_description'],
                           pageName=f'{the_category["title"]} -')

@app.route('/<category>/<article>')
def article(category, article):
    articles = [x for x in get_by_meta_key(md_directory, 'id', article) if x.metadata.get('category') == category]

    if len(articles) == 0:
        return Response(status=404)
    if len(articles) > 1:
        return Response(status=500)

    the_article = articles[0]
    return render_template('article.html', post=markdown(the_article.content), metadata=the_article.metadata,
                                   pageName=f'{the_article.metadata["title"]} - {the_article.metadata["author"]} -')

@app.route('/image/<image>')
def image(image):
    return send_from_directory(path.join(md_directory, 'images'), image)
