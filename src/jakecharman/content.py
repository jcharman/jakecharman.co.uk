#!/usr/bin/python3

from os import path
import json
from datetime import datetime
import frontmatter
from markdown import markdown
from bs4 import BeautifulSoup
from flask import render_template, Response, Blueprint
from .storage import LocalStorage

class ContentArea(Blueprint):
    def __init__(self, directory: LocalStorage, *args, **kwargs):
        self.md_directory = directory

        super().__init__(*args, **kwargs)

        self.add_app_template_filter(self.category_title, 'category_title')
        self.add_app_template_filter(self.human_date, 'human_date')
        self.add_app_template_filter(self.to_html, 'to_html')

        self.context_processor(self.processor)

        self.add_url_rule('/', view_func=self.projects)
        self.add_url_rule('/category/<category_id>/', view_func=self.category)
        self.add_url_rule('/<article_id>', view_func=self.article)
        #self.add_url_rule('/image/<image_name>', view_func=self.image)

    def processor(self) -> dict:
        ''' Jninja processors '''
        def get_excerpt(post: frontmatter.Post) -> str:
            html = markdown(post.content)
            post_soup = BeautifulSoup(html, 'html.parser')
            all_text = ' '.join([x.get_text() for x in post_soup.findAll('p')])
            return ' '.join(all_text.split()[:200])
        return dict(get_excerpt=get_excerpt)

    def category_title(self, category_id: str) -> str:
        ''' Jninja filter to get a category title by its ID '''
        with self.md_directory.open('categories.json') as categories_file:
            categories = json.load(categories_file)

        return categories.get(category_id).get('title', '')

    def human_date(self, iso_date: str) -> str:
        ''' Jninja filter to convert an ISO date to human readable. '''
        try:
            return datetime.fromisoformat(str(iso_date)).strftime('%A %d %B %Y')
        except ValueError:
            return iso_date

    def to_html(self, content: str) -> str:
        ''' Jninja filter to wrap markdown '''
        return markdown(content)

    def get_all_posts(self) -> list:
        ''' Get all posts in the posts directory '''
        abs_paths = [x.path for x in self.md_directory.ls() if x.path.endswith('.md')]
        posts = []
        for p in abs_paths:
            with self.md_directory.open(p) as f:
                posts.append(frontmatter.load(f))
        return posts
    
    def get_live_posts(self) -> list:
        ''' Get all posts in the posts directory excluding ones with a date in the future '''
        return [x for x in self.get_all_posts() if x.metadata.get('date') <= datetime.now().date()]

    def get_by_meta_key(self, key: str, value: str) -> list:
        ''' Get posts by a metadata key value pair '''
        return [x for x in self.get_live_posts() if x.get(key) == value or isinstance(x.get(key, []), list) and value in x.get(key, [])]

    def projects(self) -> str:
        ''' Load the projects page '''
        articles_to_return = sorted(
            self.get_live_posts(),
                key=lambda d: d.metadata.get('date'),
                reverse=True
            )

        if len(articles_to_return) < 1:
            return render_template('error.html',
                                error='There\'s nothing here... yet.',
                                description='I\'m still working on this page. Check back soon for some content.')
        try:
            with self.md_directory.open('categories.json') as categories_file:
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

    def category(self, category_id: str) -> str:
        ''' Load the page for a given category '''
        try:
            with self.md_directory.open('categories.json') as categories_file:
                categories = json.load(categories_file)
            the_category = categories.get(category_id)
        except FileNotFoundError:
            return render_template('error.html',
                                error='There\'s nothing here... yet.',
                                description='I\'m still working on this page. Check back soon for some content.')

        if the_category is None:
            return Response(status=404)

        articles_to_return = sorted(
            self.get_by_meta_key(
                'categories', category_id),
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

    def article(self, article_id: str) -> str:
        ''' Load a single article '''
        articles = self.get_by_meta_key('id', article_id)

        if len(articles) == 0:
            return Response(status=404)
        if len(articles) > 1:
            return Response(status=500)

        the_article = articles[0]
        return render_template('article.html', post=markdown(the_article.content),
                            metadata=the_article.metadata,
                            page_title=f'{the_article.metadata["title"]} - ')