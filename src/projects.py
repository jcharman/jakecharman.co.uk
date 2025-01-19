#!/usr/bin/python3

from os import path
import json
from flask import Flask, render_template, Response, send_from_directory, request, make_response
from markdown import markdown
import frontmatter
from glob import glob
from datetime import datetime
from index import app
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

md_directory = path.join(path.realpath(path.dirname(__file__)), path.normpath('projects/'))

@app.context_processor
def processor():
    def get_excerpt(post):
        html = markdown(post.content)
        post_soup = BeautifulSoup(html, 'html.parser')
        all_text = ' '.join([x.get_text() for x in post_soup.findAll('p')])
        return ' '.join(all_text.split()[:200])
    return dict(get_excerpt=get_excerpt)

@app.template_filter('category_title')
def category_title(category_id: str) -> str:
    with open(path.join(md_directory, 'categories.json')) as categories_file:
        categories = json.load(categories_file)

    return categories.get(category_id).get('title', '')

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
    return [x for x in get_all_posts(directory) if x.get(key) == value or type(x.get(key, [])) is list and value in x.get(key, [])]

@app.route('/projects/')
def projects():
    articles_to_return = sorted(
        get_all_posts(
            md_directory), 
            key=lambda d: d.metadata.get('date'),
            reverse=True
        )

    if len(articles_to_return) < 1:
        return render_template('error.html',
                               error='There\'s nothing here... yet.',
                               description='I\'m still working on this page. Check back soon for some content.')
    try:
        with open(path.join(md_directory, 'categories.json')) as categories_file:
            categories = json.load(categories_file)
    except FileNotFoundError:
        return render_template('error.html',
                               error='There\'s nothing here... yet.',
                               description='I\'m still working on this page. Check back soon for some content.')

    return render_template('projects.html',
                           articles=articles_to_return,
                           all_categories=categories,
                           title='Projects',
                           description='A selection of projects I\'ve been involved in')

@app.route('/projects/category/<category>/')
def category(category):
    try:
        with open(path.join(md_directory, 'categories.json')) as categories_file:
            categories = json.load(categories_file)
        the_category = categories.get(category)
    except FileNotFoundError:
        return render_template('error.html',
                               error='There\'s nothing here... yet.',
                               description='I\'m still working on this page. Check back soon for some content.')

    if the_category is None:
        return Response(status=404)

    articles_to_return = sorted(
        get_by_meta_key(
            md_directory, 'categories', category), 
            key=lambda d: d.metadata.get('date'),
            reverse=True
        )

    if len(articles_to_return) < 1:
        return render_template('error.html',
                               error='There\'s nothing here... yet.',
                               description='I\'m still working on this page. Check back soon for some content.')

    return render_template('projects.html', articles=articles_to_return,
                           title=the_category['title'], 
                           description=the_category['long_description'],
                           page_title=f'{the_category["title"]} - ',
                           all_categories=categories,
                           current_category=category)

@app.route('/projects/<article>')
def article(article):
    articles = get_by_meta_key(md_directory, 'id', article)

    if len(articles) == 0:
        return Response(status=404)
    if len(articles) > 1:
        return Response(status=500)

    the_article = articles[0]
    return render_template('article.html', post=markdown(the_article.content), 
                           metadata=the_article.metadata,
                           page_title=f'{the_article.metadata["title"]} - ')

@app.route('/projects/image/<image>')
def image(image):
    w = int(request.args.get('w', 0))
    h = int(request.args.get('h', 0))

    if w == 0 and h == 0:
        return send_from_directory(md_directory, path.join('images', image))
    try:
        the_image = Image.open(path.join(md_directory, 'images', image))
    except FileNotFoundError:
        return Response(status=404)
    max_width, max_height = the_image.size

    if (w >= max_width and h >= max_height):
        return send_from_directory(md_directory, path.join('images', image))

    req_size = [max_width, max_height]
    if w > 0:
        req_size[0] = w
    if h > 0:
        req_size[1] = h

    resized_img = BytesIO()
    the_image.thumbnail(tuple(req_size))
    the_image.save(resized_img, format='jpeg')
    
    response = make_response(resized_img.getvalue())
    response.headers.set('Content-Type', 'image/jpeg')
    return response

