"""
Caching layer for Autelion status utilizing Redis.

Usage:
$ export REDIS_URL=redis://localhost
>>> import cache
>>> autelion = cache.get_autelion()
>>> if autelion is not None:
...     print(autelion.status, autelion.updated_at)
...
>>> cache.set_autelion({'key1': 'value1', (...)})
"""

import os
import json
import collections
import logging
from datetime import datetime

import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


Autelion = collections.namedtuple('Autelion', 'status updated_at')


class RedisCache:
    """Convenience class for connecting to Redis."""

    def __init__(self):

        redis_url = os.environ.get('REDIS_URL')

        if redis_url is None:
            raise redis.ConnectionError('Undefined REDIS_URL variable')

        self._connection = redis.from_url(redis_url)

    def __getattr__(self, name):
        """Delegate commands to the connection object."""
        return getattr(self._connection, name)


def get_autelion() -> Autelion:
    """Return named tuple with status and last update or None."""
    try:
        redis_cache = RedisCache()

        status, updated_at = redis_cache.mget([
            'autelion_status',
            'autelion_updated_at'
        ])

        if status is None:
            logger.info('Cache miss')
            return None

        try:
            updated_at = datetime.fromisoformat(updated_at.decode('utf-8'))
        except (ValueError, AttributeError):
            logger.error('Unable to parse last update: "%s"', updated_at)
            updated_at = None

        return Autelion(json.loads(status), updated_at)

    except redis.RedisError as ex:
        logger.error('Could not read from Redis: %s', ex)
    except json.JSONDecodeError as ex:
        logger.error('Unable to decode JSON: %s', ex)



def set_autelion(status: dict) -> None:
    """Serialize status to JSON, add timestamp and store both in cache."""
    try:
        autelion = Autelion(status=status, updated_at=datetime.utcnow())

        logger.info('Updating cache')

        RedisCache().mset({
            'autelion_status': json.dumps(autelion.status),
            'autelion_updated_at': autelion.updated_at.isoformat(),
        })

    except TypeError as ex:
        logger.error('Unable to format status as JSON')
    except redis.RedisError as ex:
        logger.error('Could not write to Redis: %s', ex)
