#!/usr/bin/env python

"""
Parse Autelion, update Redis and send notification via email if necessary.

Usage:
$ export AUTELION_USERNAME=<your-username>
$ export AUTELION_PASSWORD=<your-password>
$ export REDIS_URL=redis://localhost
$ export SENDGRID_API_KEY=<your-api-key>
$ export EMAIL_ADDRESS=<your-email>
$ python updaterjob.py
"""

import os
import logging

import cache
import parser
import mailer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Updater job entry point."""

    logger.info('Updater job started')

    try:
        status = parser.parse_autelion()

        if status is None:
            logger.error('Updater job failed to parse Autelion')
        else:
            old_autelion = cache.get_autelion()
            cache.set_autelion(status)
            new_autelion = cache.get_autelion()

            if new_autelion is None:
                logger.error('Updater job failed to update cache')
            else:
                if old_autelion is None:
                    logger.info('There was no previous status')
                    mailer.send(new_autelion)
                else:
                    if old_autelion.status == new_autelion.status:
                        logger.info('Previous status has not changed')
                    else:
                        logger.info('Previous status has changed')
                        mailer.send(new_autelion)
    finally:
        logger.info('Updater job finished')


if __name__ == '__main__':
    main()
