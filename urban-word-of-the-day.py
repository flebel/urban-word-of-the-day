#!/usr/bin/env python

import json
import requests

from collections import namedtuple

from flask import Flask
from flask.ext.cache import Cache

from bs4 import BeautifulSoup

APP = Flask(__name__)
CACHE = Cache(APP, config={'CACHE_TYPE': 'simple'})
CACHE_TIMEOUT = 1800  # 30 minutes
_UrbanWord = namedtuple('UrbanWord', 'word meaning example')


class UrbanWord(_UrbanWord):
    def jsonify(self):
        return json.dumps({
            'word': self.word,
            'meaning': self.meaning,
            'example': self.example
        })


class UrbanWordRetriever(object):
    DEFAULT_URL = 'https://www.urbandictionary.com'

    def __init__(self, day, url=DEFAULT_URL):
        if day > 6:
            raise LookupError('Words of the day older than one week from today'
                              ' are not available.')
        self.day = day
        self.url = url

    @staticmethod
    def __get_elements_of_class(class_name, soup):
        elements = []
        for div in soup.findAll('div', attrs={'class': class_name}):
            elements.append('\n'.join(div.findAll(text=True)).strip())
        return elements

    def retrieve(self):
        content = requests.get(self.url).text
        soup = BeautifulSoup(content)

        words = []
        for div in soup.findAll('a', attrs={'class': 'word'}):
            words.append(div.text.strip())

        meanings = UrbanWordRetriever.__get_elements_of_class('meaning', soup)
        example = UrbanWordRetriever.__get_elements_of_class('example', soup)

        return UrbanWord(words[self.day], meanings[self.day],
                         example[self.day])


@APP.route('/')
@APP.route('/today')
@CACHE.cached(timeout=CACHE_TIMEOUT)
def today():
    word = UrbanWordRetriever(0).retrieve()
    return word.jsonify()


@APP.route('/yesterday')
@CACHE.cached(timeout=CACHE_TIMEOUT)
def yesterday():
    word = UrbanWordRetriever(1).retrieve()
    return word.jsonify()


if __name__ == '__main__':
    APP.run(debug=True)
