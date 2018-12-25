"""
Autelion parser.
"""

import os
import json
import datetime

import requests
import bs4


def parse():
    """Return JSON-formatted string with Autelion report."""

    books = {}
    payments = {}

    session = requests.Session()
    session.get(url())  # obtain cookies

    # log in
    response = session.post(url('index.cgi'), data={
        'id': os.environ.get('AUTELION_USERNAME'),
        'haslo': os.environ.get('AUTELION_PASSWORD')
    })

    if response.url.endswith('blad_log') or response.url.endswith('index.cgi'):
        raise Exception('Unable to log in to Autelion')

     # id, title, published_at
    response = session.get(url('ksiazka.cgi'))
    html = bs4.BeautifulSoup(response.text, features='lxml')
    for row in html.select('tr.ukryta'):
        columns = row.select('td')
        books[columns[0].text] = {
            'title': columns[2].select('a')[0].text,
            'published_at': columns[3].text
        }

    # isbn
    for id_ in books:
        response = session.get(url(f'ksiazka.cgi?ksiazka={id_}'))
        if response.ok:
            html = bs4.BeautifulSoup(response.text, features='lxml')
            books[id_]['isbn'] = html.select('.book-info')[0].text[6:]

    # copies_sold, revenue, current_royalty
    response = session.get(url('main.cgi'))
    if response.ok:
        html = bs4.BeautifulSoup(response.text, features='lxml')
        for row in html.select('#autelion tr.ukryta'):
            id_ = row.select('td:nth-of-type(1) a')[0].text
            books[id_]['copies_sold'] = int(row.select('td')[3].text)
            books[id_]['revenue'] = number(row.select('td')[4].text)
            books[id_]['royalty'] = {
                'total': number(row.select('td')[5].text),
                'paid': number(row.select('td')[6].text),
                'current': number(row.select('td')[7].text)
            }

    # past payments
    response = session.get(url('historia.cgi'))
    if response.ok:
        html = bs4.BeautifulSoup(response.text, features='lxml')
        for row in html.select('.tableSort2 tbody tr'):
            when = row.select('td a')[0].text
            payments[when] = number(row.select('td')[1].text)

    return json.dumps({
        'last_updated_at': datetime.datetime.utcnow().isoformat(),
        'books': books,
        'payments': payments
    })


def url(path=''):
    """Return URL with relative path appended."""
    return f'https://helion.pl/autelion/{path.lstrip("/")}'


def number(text):
    """Return floating point number."""
    return float(text.replace('.', '').replace(',', '.'))
