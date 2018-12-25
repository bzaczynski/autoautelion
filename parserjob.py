#!/usr/bin/env python

"""
Scheduled job to parse Autelion and update Redis accordingly.
"""

import os
import logging

import redis

import autelion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Job entry point."""

    logger.info('Started parser job')

    redis_url = os.environ.get('REDIS_URL')

    if redis_url is None:
        logger.error('Unable to read REDIS_URL environment variable')
    else:
        connection = redis.from_url(redis_url)
        connection.set('autelion', autelion.parse())


if __name__ == '__main__':
    try:
        main()
    except redis.DataError as ex:
        logger.error('Unable to write to Redis due to: %s', ex)
    except Exception as ex:
        logger.error('There was an error: %s', ex)
    finally:
        logger.info('Finished parser job')
