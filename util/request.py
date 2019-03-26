# -*- coding: utf-8 -*-

import requests
import sys

reload(sys)
sys.setdefaultencoding('utf8')

base_url = 'http://localhost:8080/'


def post(url, data=None, **kwargs):
    response = requests.post(base_url + url, data)
    if 'callback' in kwargs:
        kwargs['callback'](response)


def get(url, data=None, **kwargs):
    response = requests.get(base_url + url, data)
    if not response.json()['success']:
        print response.json()
        kwargs['callback'](response.json()['msg'])
    if 'callback' in kwargs:
        kwargs['callback'](response.json()['data'])
