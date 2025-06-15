#!/usr/bin/python3

import xml.etree.ElementTree as ET
import json
from flask import url_for, request, Response
from re import match
from index import app
from projects import get_all_posts

def get_routes() -> list:
    routes = []
    for rule in app.url_map.iter_rules():
        if 0 >= len(rule.arguments):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            routes.append(url)
    return routes

def get_build_date():
    try:
        with open('/var/www/jc/.buildinfo.json', encoding='utf8') as build:
            build_json = json.load(build)
            return build_json['date']
    except:
        return '1970-01-01'

@app.route('/sitemap.xml')
def sitemap():
    date = get_build_date()
    root = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    base_url = match(r'^https?:\/\/.+:?\d*(?=\/)', request.base_url).group()
    base_url = base_url.replace('http://', 'https://')
    for route in get_routes():
        url = ET.SubElement(root, 'url')
        ET.SubElement(url, 'loc').text = base_url + route
        ET.SubElement(url, 'lastmod').text = date
    for article in get_all_posts():
        if 'link' in article.metadata:
            continue
        url = ET.SubElement(root, 'url')
        ET.SubElement(url, 'loc').text = f'{base_url}/projects/{article.metadata['id']}'
        ET.SubElement(url, 'lastmod').text = article.metadata['date'].strftime('%Y-%m-%d')
        
    return Response(ET.tostring(root, encoding='utf-8'), 200, {'content-type': 'application/xml'})