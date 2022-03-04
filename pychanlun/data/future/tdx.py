# -*- coding:utf-8 -*-

import urllib
import json
import pandas as pd
from datetime import date
from QUANTAXIS.QAUtil import QA_util_get_trade_gap
from pychanlun.database.cache import RedisCache
from pychanlun.config import settings
from pydash import get
from pychanlun.db import DBQuantAxis
from pychanlun.gateway.tdxhq import ex_get_instrument_bars

global extension_market_list
extension_market_list = None


def get_tdxhq_endpoint():
    return get(settings, 'tdxhq.endpoint', 'http://127.0.0.1:5001')


def to_df(v):
    if isinstance(v, list):
        return pd.DataFrame(data=v)
    elif isinstance(v, dict):
        return pd.DataFrame(data=[v, ])
    else:
        return None


@RedisCache.memoize(expiration=864000)
def fq_future_fetch_instrument(code):
    return DBQuantAxis['future_list'].find_one({'code': code})


@RedisCache.memoize(expiration=86400)
def fq_future_fetch_extension_market_list():
    endpoint = get_tdxhq_endpoint()
    req = urllib.request.Request(urllib.parse.urljoin(endpoint, '/ex/get_markets'), method='GET')
    resp = urllib.request.urlopen(req, timeout=30)
    markets = json.loads(resp.read().decode('utf-8'))
    return to_df(markets)


@RedisCache.memoize(expiration=86400)
def fq_future_fetch_extension_instrument_count():
    endpoint = get_tdxhq_endpoint()
    req = urllib.request.Request(urllib.parse.urljoin(endpoint, '/ex/get_instrument_count'), method='GET')
    resp = urllib.request.urlopen(req, timeout=30)
    num = int(resp.read().decode('utf-8'))
    return num


@RedisCache.memoize(expiration=86400)
def fq_future_fetch_extension_instrument_info(start: int, count: int=500):
    endpoint = get_tdxhq_endpoint()
    query = urllib.parse.urlencode({'start':start, 'count': count})
    req = urllib.request.Request(urllib.parse.urljoin(endpoint, f'/ex/get_instrument_info?{query}'), method='GET')
    resp = urllib.request.urlopen(req, timeout=30)
    info = json.loads(resp.read().decode('utf-8'))
    return to_df(info)


@RedisCache.memoize(expiration=86400)
def fq_future_fetch_extension_instrument_list():
    num = fq_future_fetch_extension_instrument_count()
    return pd.concat(
        [fq_future_fetch_extension_instrument_info((int(num / 500) - i) * 500, 500) for i in range(int(num / 500) + 1)])


def fq_future_fetch_instrument_bars(code, count=700, frequence='1min'):
    # endpoint = get_tdxhq_endpoint()
    instrument = fq_future_fetch_instrument(code)
    if str(frequence) in ['5', '5m', '5min', 'five']:
        frequence = 0
    elif str(frequence) in ['1', '1m', '1min', 'one']:
        frequence = 8
    elif str(frequence) in ['15', '15m', '15min', 'fifteen']:
        frequence = 1
    elif str(frequence) in ['30', '30m', '30min', 'half']:
        frequence = 2
    elif str(frequence) in ['60', '60m', '60min', '1h']:
        frequence = 3
    bars = []
    pages = int(count / 700) + (1 if count % 700 > 0 else 0)
    for i in range(1, pages + 1):
        query = urllib.parse.urlencode({
            'category': frequence,
            'market': instrument['market'],
            'code': code,
            'start': (pages-i)*700,
            'count': 700
        })
        # req = urllib.request.Request(urllib.parse.urljoin(endpoint, f'/ex/get_instrument_bars?{query}'), method='GET')
        # resp = urllib.request.urlopen(req, timeout=30)
        # text = resp.read().decode('utf-8')
        # df = to_df(json.loads(text))
        data = ex_get_instrument_bars(frequence, instrument['market'], code, (pages-i)*700, 700)
        print(data)
        df = to_df(data)
        if df is not None:
            bars.append(df)
    if len(bars) > 0:
        return pd.concat(bars)
    else:
        return None


if __name__ == "__main__":
    print(fq_future_fetch_instrument_bars('RBL9', 800))
