#!/usr/bin/env python

"""
Web application receiving HTTP traffic.
"""

import os
import json
import logging
import datetime
import functools

import redis
import flask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = flask.Flask(__name__)
app.config['redis'] = redis.from_url(os.environ.get('REDIS_URL'))


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
    """Return HTML view of the data from Redis."""
    try:
        model = json.loads(read_from_redis())
        model['last_updated_at'] = datetime.datetime.strptime(
            model['last_updated_at'], '%Y-%m-%dT%H:%M:%S.%f')
        return flask.render_template('index.html.j2', model=model)
    except TypeError as ex:
        logger.error('Unable to decode JSON from Redis due to: %s', ex)
        return flask.Response('No data available', mimetype='text/plain')
    except json.JSONDecodeError as ex:
        logger.error('Unable to decode JSON from Redis due to: %s', ex)
        return flask.Response('There was an error', mimetype='text/plain')


@app.route('/api')
@basic_auth
def api_index():
    """Return JSON straight from Redis."""
    return flask.Response(read_from_redis(), mimetype='application/json')


def read_from_redis():
    """Return JSON string from Redis."""
    try:
        return app.config['redis'].get('autelion')
    except redis.ConnectionError as ex:
        logger.error('Unable to read from Redis due to: %s', ex)
        return '{}'
