from flask import Blueprint, render_template
import json

class Links(Blueprint):
    def __init__(self, file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_url_rule('/', view_func=self.links)
        self.file = file

    def links(self):
        with open(self.file, encoding='utf8') as file:
            links = json.load(file)
        return render_template('links.html', links=links, page_title='Useful Links - ')
