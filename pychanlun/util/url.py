# -*- coding: utf-8 -*-

import urllib.parse


def fq_util_url_join(url, *paths):
    for path in paths:
        url = url.rstrip('/') + '/' + path.lstrip('/')
    return url


def fq_util_url_encode(params, doseq=False):
    if params and isinstance(params, dict):
        for key, value in params.items():
            if isinstance(value, bool):
                params[key] = 'true' if value else 'false'
        return urllib.parse.urlencode(params, doseq)
    return ''
