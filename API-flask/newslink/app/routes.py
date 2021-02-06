from app import app
from app.models import *
from flask import jsonify, request

from .modules.top_stories.top_stories import get_top_stories
from .modules.search.search import search_stories

# top stories
# search
# feed
# recommded
# trending topics

@app.route('/')
def index():
    return "Hello World"

@app.route('/top/stories/')
def top():
    stories = get_top_stories()
    return jsonify(stories)

@app.route("/search/<query>")
def search(query):
    stories = search_stories(query)
    return jsonify(stories)

