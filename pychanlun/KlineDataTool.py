# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import time
from functools import lru_cache

import rqdatac as rq
from pychanlun.db import DBPyChanlun
from bson.codec_options import CodecOptions
import pytz
import pymongo

tz = pytz.timezone('Asia/Shanghai')

okexUrl = "https://www.okex.me/v2/perpetual/pc/public/instruments/BTC-USDT-SWAP/candles"


@lru_cache(maxsize=128)
def getDigitCoinData(symbol, period, endDate, stamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    t = time.time()
    timeStamp = int(round(t * 1000))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
        "Accept": "application/json",
        "App-Type": "web",
        "Referer": "https://www.okex.me/derivatives/swap/full/usdt-btc"}

    payload = {
        'granularity': period,
        'size': 1000,
        't': timeStamp
    }
    r = requests.get(okexUrl, params=payload, headers=headers, timeout=(15, 15))
    data_list = json.loads(r.text)['data']
    df = pd.DataFrame(list(data_list), columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = df['time'].apply(lambda value: datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ'))
    df.fillna(0, inplace=True)
    return df


@lru_cache(maxsize=128)
def getFutureData(symbol, period, endDate, stamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    # 聚宽数据源
    startTime = datetime.now()
    # print("可调用条数:", get_query_count())
    # df = get_bars(symbol, size, unit=period, fields=['date', 'open', 'high', 'low', 'close', 'volume'],
    #               include_now=True, end_dt=datetime.now())
    # df = get_price(symbol, frequency=period, end_date=datetime.now(), count=size,
    #                fields=['open', 'high', 'low', 'close', 'volume'])

    if endDate is None:
        end = datetime.now() + timedelta(1)
    else:
        end = datetime.strptime(endDate, "%Y-%m-%d")
        # symbol = re.sub('\d+', "88", symbol)
    timeDeltaMap = {
        '1m': -5,
        '3m': -5 * 3,
        '5m': -5 * 5,
        '15m': -5 * 15,
        '30m': -5 * 30,
        '60m': -5 * 60,
        '180m': -5 * 180,
        '1d': -1000,
        '3d': -3000
    }
    start_date = end + timedelta(timeDeltaMap[period])
    df = rq.get_price(symbol, frequency=period,
                      fields=['open', 'high', 'low', 'close', 'volume'], start_date=start_date, end_date=end)
    # df = get_price('RB1910.XSGE', frequency='180m', end_date=datetime.now(), count=200,
    #                fields=['open', 'high', 'low', 'close', 'volume'])
    # todo 米匡180m 数据有问题,比通达信和文化财经多一个时间,需要手动去除,但是手动去除也不准,需要等米匡修复
    # todo 米匡回复: 180m 是按照交易时间切分的, 一天固定3根k线,而文华财经和通达信是一天固定2根,后面自己处理吧
    # 还是不能这样处理,会导致很多高低点丢失,影响到30F的结构
    # if period == '180m':
    #     cols = [x for i, x in enumerate(df.index) if '15:00:00' in str(df.index[i])]
    #     df = df.drop(cols)
    # if period == '180m':
    #     ohlc_dict = {
    #         'open': 'first',
    #         'high': 'max',
    #         'low': 'min',
    #         'close': 'last',
    #         'volume': 'sum'
    #     }
    #     # df.index = pd.DatetimeIndex(df.index)
    #
    #     # 聚合k线
    #     df = df.resample('4H', closed='left', label='left') \
    #         .agg(ohlc_dict).dropna(how='any')

    df['time'] = df.index.to_series().apply(lambda value: value.replace(tzinfo=tz).timestamp())
    df.fillna(0, inplace=True)
    return df


@lru_cache(maxsize=128)
def getStockData(symbol, period, endDate, stamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    startTime = datetime.now()
    if endDate is None or endDate == "":
        end = datetime.now() + timedelta(1)
    else:
        end = datetime.strptime(endDate, "%Y-%m-%d")
    end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    timeDeltaMap = {
        '1m': -5,
        '3m': -5 * 3,
        '5m': -5 * 5,
        '15m': -5 * 15,
        '30m': -5 * 30,
        '60m': -5 * 60,
        '180m': -5 * 180,
        '1d': -1000,
        '3d': -3000
    }
    start_date = end + timedelta(timeDeltaMap[period])
    code = "%s_%s" % (symbol, period)
    data_list = DBPyChanlun[code].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
        "_id": {"$gte": start_date, "$lte": end}
    }).sort("_id", pymongo.ASCENDING)
    data_list = list(data_list)
    kline_data = pd.DataFrame(data_list)
    kline_data['time'] = kline_data['_id'].apply(lambda value: value.timestamp())
    kline_data.fillna(0, inplace=True)
    return kline_data


@lru_cache(maxsize=128)
def getGlobalFutureData(symbol, period, endDate, stamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    if endDate is None or endDate == "":
        end = datetime.now() + timedelta(1)
    else:
        end = datetime.strptime(endDate, "%Y-%m-%d")
    end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    timeDeltaMap = {
        '1m': -3,
        '3m': -3 * 3,
        '5m': -3 * 5,
        '15m': -3 * 15,
        '30m': -3 * 30,
        '60m': -3 * 60,
        '180m': -3 * 180,
        '1d': -1000,
        '3d': -3000
    }
    start_date = end + timedelta(timeDeltaMap[period])
    code = "%s_%s" % (symbol, period)
    data_list = DBPyChanlun[code] \
        .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
        .find({"_id": {"$gte": start_date, "$lte": end}}).sort("_id", pymongo.ASCENDING)
    data_list = list(data_list)
    kline_data = pd.DataFrame(data_list)
    kline_data['time'] = kline_data['_id'].apply(lambda value: value.timestamp())
    kline_data.fillna(0, inplace=True)
    return kline_data
