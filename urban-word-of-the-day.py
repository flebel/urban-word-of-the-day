#!/usr/bin/env python

import json
import requests

from flask import Flask
from flask.ext.cache import Cache

from bs4 import BeautifulSoup

APP = Flask(__name__)
CACHE = Cache(APP, config={'CACHE_TYPE': 'simple'})
CACHE_TIMEOUT = 1800 # 30 minutes
URL = 'https://www.urbandictionary.com'

def get_wod(day=0):
    if day > 6:
        raise LookupError('Words of the day older than one week from today are not available.')

    content = requests.get(URL).text
    soup = BeautifulSoup(content)
    words = []
    meanings = []

    for div in soup.findAll('a', attrs={'class': 'word'}):
        words.append(div.text.strip())

    for div in soup.findAll('div', attrs={'class': 'meaning'}):
        meanings.append('\n'.join(div.findAll(text=True)).strip())

    return zip(words, meanings)[day]


def jsonize_wod(wod):
    return json.dumps({ 'word': wod[0], 'meaning': wod[1] })


@APP.route('/')
@APP.route('/today')
@CACHE.cached(timeout=CACHE_TIMEOUT)
def today():
    return jsonize_wod(get_wod(0))


@APP.route('/yesterday')
@CACHE.cached(timeout=CACHE_TIMEOUT)
def yesterday():
    return jsonize_wod(get_wod(1))


if __name__ == '__main__':
    APP.run(debug=True)

