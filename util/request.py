# -*- coding: utf-8 -*-

import requests
import sys

reload(sys)
sys.setdefaultencoding('utf8')

base_url = 'http://192.168.31.122:8083/'


def post(url, data=None, **kwargs):
    response = requests.post(base_url + url, data)
    print response.json()
    if 'callback' in kwargs:
        kwargs['callback'](response.json())


def get(url, data=None, **kwargs):
    response = requests.get(base_url + url, data)
    print response.json()
    if not response.json()['success']:
        kwargs['callback'](response.json()['msg'])
    if 'callback' in kwargs:
        kwargs['callback'](response.json()['data'])
