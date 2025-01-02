#!/usr/bin/python3

from flask import Flask, render_template

application = Flask(__name__)
app = application

import projects
import common

# Load the homepage.

