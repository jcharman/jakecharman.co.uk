#!/usr/bin/python3

from os import path
import json
from datetime import datetime
from io import BytesIO
from glob import glob
from PIL import Image, UnidentifiedImageError
import frontmatter
from markdown import markdown
from bs4 import BeautifulSoup
from flask import render_template, Response, send_from_directory, request, make_response
from index import app

md_directory = path.join(path.realpath(path.dirname(__file__)), path.normpath('projects/'))

@app.context_processor
def processor() -> dict:
    ''' Jninja processors '''
    def get_excerpt(post: frontmatter.Post) -> str:
        html = markdown(post.content)
        post_soup = BeautifulSoup(html, 'html.parser')
        all_text = ' '.join([x.get_text() for x in post_soup.findAll('p')])
        return ' '.join(all_text.split()[:200])
    return dict(get_excerpt=get_excerpt)

@app.template_filter('category_title')
def category_title(category_id: str) -> str:
    ''' Jninja filter to get a category title by its ID '''
    with open(path.join(md_directory, 'categories.json'), encoding='utf8') as categories_file:
        categories = json.load(categories_file)

    return categories.get(category_id).get('title', '')

@app.template_filter('human_date')
def human_date(iso_date: str) -> str:
    ''' Jninja filter to convert an ISO date to human readable. '''
    try:
        return datetime.fromisoformat(str(iso_date)).strftime('%A %d %B %Y')
    except ValueError:
        return iso_date

@app.template_filter('to_html')
def to_html(content: str) -> str:
    ''' Jninja filter to wrap markdown '''
    return markdown(content)

def get_all_posts(directory: str = md_directory) -> list:
    ''' Get all posts in the posts directory '''
    abs_paths = [path.join(directory, x) for x in glob(f'{directory}/*.md')]
    return [frontmatter.load(x) for x in abs_paths]

def get_by_meta_key(directory: str, key: str, value: str) -> list:
    ''' Get posts by a metadata key value pair '''
    return [x for x in get_all_posts(directory) if x.get(key) == value or type(x.get(key, [])) is list and value in x.get(key, [])]

@app.route('/projects/')
def projects() -> str:
    ''' Load the projects page '''
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
        with open(path.join(md_directory, 'categories.json'), encoding='utf8') as categories_file:
            categories = json.load(categories_file)
    except FileNotFoundError:
        return render_template('error.html',
                               error='There\'s nothing here... yet.',
                               description='I\'m still working on this page. Check back soon for some content.')

    return render_template('projects.html',
                           articles=articles_to_return,
                           all_categories=categories,
                           title='Projects',
                           page_title='Projects - ',
                           description='A selection of projects I\'ve been involved in')

@app.route('/projects/category/<category_id>/')
def category(category_id: str) -> str:
    ''' Load the page for a given category '''
    try:
        with open(path.join(md_directory, 'categories.json'), encoding='utf8') as categories_file:
            categories = json.load(categories_file)
        the_category = categories.get(category_id)
    except FileNotFoundError:
        return render_template('error.html',
                               error='There\'s nothing here... yet.',
                               description='I\'m still working on this page. Check back soon for some content.')

    if the_category is None:
        return Response(status=404)

    articles_to_return = sorted(
        get_by_meta_key(
            md_directory, 'categories', category_id),
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
                           current_category=category_id)

@app.route('/projects/<article_id>')
def article(article_id: str) -> str:
    ''' Load a single article '''
    articles = get_by_meta_key(md_directory, 'id', article_id)

    if len(articles) == 0:
        return Response(status=404)
    if len(articles) > 1:
        return Response(status=500)

    the_article = articles[0]
    return render_template('article.html', post=markdown(the_article.content), 
                           metadata=the_article.metadata,
                           page_title=f'{the_article.metadata["title"]} - ')

@app.route('/projects/image/<image_name>')
def image(image_name: str) -> Response:
    ''' Resize and return an image. '''
    w = int(request.args.get('w', 0))
    h = int(request.args.get('h', 0))

    if w == 0 and h == 0:
        return send_from_directory(md_directory, path.join('images', image_name))
    try:
        the_image = Image.open(path.join(md_directory, 'images', image_name))
    except FileNotFoundError:
        return Response(status=404)
    except UnidentifiedImageError:
        return send_from_directory(md_directory, path.join('images', image_name))

    max_width, max_height = the_image.size

    if (w >= max_width and h >= max_height):
        return send_from_directory(md_directory, path.join('images', image_name))
    
    if path.exists(path.join('images', f'{w}-{h}-{image_name}')):
        return send_from_directory(md_directory, path.join('images', f'{w}-{h}-{image_name}'))

    req_size = [max_width, max_height]
    if w > 0:
        req_size[0] = w
    if h > 0:
        req_size[1] = h

    resized_img = BytesIO()
    the_image.thumbnail(tuple(req_size))
    the_image.save(resized_img, format=the_image.format)
    the_image.save(path.join(md_directory, 'images', f'{w}-{h}-{image_name}'), the_image.format)

    response = make_response(resized_img.getvalue())
    response.headers.set('Content-Type', f'image/{the_image.format}')
    return response
