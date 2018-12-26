#!/usr/bin/env python

"""
Web application receiving HTTP traffic at http://autoautelion.herokuapp.com/.

Usage:
$ export AUTELION_USERNAME=<your-username>
$ export AUTELION_PASSWORD=<your-password>
$ export REDIS_URL=redis://localhost
$ FLASK_APP=webapp.py flask run
...or:
$ gunicorn webapp:app --log-file -
"""

import os
import json
import logging
import functools

import flask

import cache
import parser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = flask.Flask(__name__)


def basic_auth(function):
    """Require HTTP Basic Auth."""
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        auth = flask.request.authorization
        if auth is not None:
            if auth.username == os.environ.get('AUTELION_USERNAME'):
                if auth.password == os.environ.get('AUTELION_PASSWORD'):
                    return function(*args, **kwargs)
        return flask.make_response('HTTP 401: Unauthorized', 401, {
            'WWW-Authenticate': 'Basic realm="Login required"'
        })
    return wrapper


@app.route('/')
@basic_auth
def index():
    """Return HTML view of the data from cache."""

    autelion = from_cache_or_get()

    if autelion is None:
        return flask.Response('No data available.', mimetype='text/html')
    else:
        model = {
            'updated_at': autelion.updated_at,
            **autelion.status
        }
        return flask.render_template('index.html.j2', model=model)


@app.route('/api')
@basic_auth
def api_index():
    """Return JSON straight from cache."""

    autelion = from_cache_or_get()

    if autelion is None:
        return flask.Response('No data available.', mimetype='text/html')
    else:

        if autelion.updated_at is None:
            updated_at = None
        else:
            updated_at = autelion.updated_at.isoformat()

        payload = json.dumps({
            'updated_at': updated_at,
            **autelion.status
        }, indent=True)

        return flask.Response(payload, mimetype='application/json')


def from_cache_or_get():
    """Return named tuple from cache or force cache update."""

    autelion = cache.get_autelion()

    if autelion is None:
        status = parser.parse_autelion()
        if status is None:
            return None
        else:
            cache.set_autelion(status)
            return cache.get_autelion()
    else:
        return autelion
