"""
Web scraper and parser of Autelion at https://helion.pl/autelion/.

Usage:
$ export AUTELION_USERNAME=<your-username>
$ export AUTELION_PASSWORD=<your-password>
>>> import parser
>>> status = parser.parse_autelion()
>>> if status is not None:
...     print(status)
"""

import os
import logging

import requests
import bs4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutelionException(Exception):
    """Raised when communication with Autelion fails."""


class Autelion:
    """Convenience class for connecting to Autelion."""

    def __init__(self):
        self.session = requests.Session()

    def __enter__(self):

        username = os.environ.get('AUTELION_USERNAME')
        password = os.environ.get('AUTELION_PASSWORD')

        if username is None:
            raise AutelionException('Undefined AUTELION_USERNAME variable')

        if password is None:
            raise AutelionException('Undefined AUTELION_PASSWORD variable')

        payload = {
            'id': username,
            'haslo': password
        }

        logger.info('Getting cookies')
        self.session.get(url())  # obtain cookies

        logger.info('Logging user in')
        response = self.session.post(url('index.cgi'), data=payload)

        if response.url.endswith('blad_log') or \
           response.url.endswith('index.cgi'):
            raise AutelionException('Login failed')

        return self

    def __exit__(self, *args, **kwargs):
        logger.info('Logging user out')
        self.session.get(url('logout.cgi'))

    def get_status(self):
        """Return a dict with Autelion status."""

        books = {}
        payments = {}

        # id, title, published_at
        logger.info('Getting book list')
        response = self.session.get(url('ksiazka.cgi'))
        html = bs4.BeautifulSoup(response.text, features='lxml')
        for row in html.select('tr.ukryta'):
            columns = row.select('td')
            books[columns[0].text] = {
                'title': columns[2].select('a')[0].text,
                'published_at': columns[3].text
            }

        # isbn
        for id_ in books:
            logger.info('Gettig ISBN for book with id=%s', id_)
            response = self.session.get(url(f'ksiazka.cgi?ksiazka={id_}'))
            if response.ok:
                html = bs4.BeautifulSoup(response.text, features='lxml')
                books[id_]['isbn'] = html.select('.book-info')[0].text[6:]

        # copies_sold, revenue, current_royalty
        logger.info('Getting revenue info')
        response = self.session.get(url('main.cgi'))
        if response.ok:
            html = bs4.BeautifulSoup(response.text, features='lxml')
            for row in html.select('#autelion tr.ukryta'):
                id_ = row.select('td:nth-of-type(1) a')[0].text
                if id_ in books:
                    books[id_]['copies_sold'] = int(row.select('td')[3].text)
                    books[id_]['revenue'] = number(row.select('td')[4].text)
                    books[id_]['royalty'] = {
                        'total': number(row.select('td')[5].text),
                        'paid': number(row.select('td')[6].text),
                        'current': number(row.select('td')[7].text)
                    }
                else:
                    logger.warn('Book with ID=%s not found', id_)

        # past payments
        logger.info('Getting payments info')
        response = self.session.get(url('historia.cgi'))
        if response.ok:
            html = bs4.BeautifulSoup(response.text, features='lxml')
            for row in html.select('.tableSort2 tbody tr'):
                when = row.select('td a')[0].text
                payments[when] = number(row.select('td')[1].text)

        return {
            'books': books,
            'payments': payments
        }


def url(path=''):
    """Return URL with relative path appended."""
    return f'https://helion.pl/autelion/{path.lstrip("/")}'


def number(text):
    """Return floating point number."""
    return float(text.replace('.', '').replace(',', '.'))


def parse_autelion():
    """Return dict with Autelion status or None."""
    try:
        with Autelion() as autelion:
            if autelion is not None:
                return autelion.get_status()
    except AutelionException as ex:
        logger.error('Unable to get status from Autelion: %s', ex)
