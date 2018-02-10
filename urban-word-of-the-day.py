#!/usr/bin/env python

import json
import urllib2

from flask import Flask
from flask.ext.cache import Cache

from bs4 import BeautifulSoup

APP = Flask(__name__)
CACHE = Cache(APP, config={'CACHE_TYPE': 'simple'})
CACHE_TIMEOUT = 1800 # 30 minutes
URL = 'http://www.urbandictionary.com'

def get_wod(day=0):
    if day > 6:
        raise LookupError('Words of the day older than one week from today are not available.')

    content = urllib2.urlopen(URL).read()
    soup = BeautifulSoup(content)
    words = []

    for div in soup.findAll('a', attrs={'class': 'word'}):
        words.append(div.text.strip())

    meanings = __get_elements_of_class('meaning', soup)
    elements = __get_elements_of_class('example', soup)

    return zip(words, meanings, elements)[day]


def __get_elements_of_class(class_name, soup):
    elements = []

    for div in soup.findAll('div', attrs={'class': class_name}):
        elements.append('\n'.join(div.findAll(text=True)).strip())

    return elements


def jsonize_wod(wod):
    return json.dumps({ 'word': wod[0], 'meaning': wod[1], 'example': wod[2] })


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

