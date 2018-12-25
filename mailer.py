#!/usr/bin/env python

"""
Scheduled job to send emails with Autelion reports.
"""

import os
import logging

import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Job entry point."""

    logger.info('Started mailer job')

    redis_url = os.environ.get('REDIS_URL')

    if redis_url is None:
        logger.error('Unable to read REDIS_URL environment variable')
    else:
        connection = redis.from_url(redis_url)
        model = connection.get('autelion')


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        logger.error('There was an error: %s', ex)
    finally:
        logger.info('Finished mailer job')
