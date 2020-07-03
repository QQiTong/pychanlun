# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime, timedelta
import numpy as np
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

    df = pd.DataFrame(list(data_list))

    klineList = []
    for idx, row in df.iterrows():
        item = {}
        date = datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%S.%fZ")
        date = date + timedelta(hours=8)
        item['time'] = int(time.mktime(date.timetuple()))
        item['open'] = 0 if pd.isna(row[1]) else row[1]
        item['high'] = 0 if pd.isna(row[2]) else row[2]
        item['low'] = 0 if pd.isna(row[3]) else row[3]
        item['close'] = 0 if pd.isna(row[4]) else row[4]
        item['volume'] = 0 if pd.isna(row[5]) else row[5]
        klineList.append(item)
    return klineList


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
        '1m': -7 * 3,
        '3m': -31 * 3,
        '5m': -31 * 3,
        '15m': -31 * 3,
        '30m': -31 * 8,
        '60m': -31 * 8,
        '180m': -31 * 8,
        '1d': -31 * 10,
        '3d': -31 * 30
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

    nparray = np.array(df)
    npKlineList = nparray.tolist()
    # npIndexList = pd.to_numeric(df.index) // 1000000000
    klineList = []

    for i in range(len(npKlineList)):
        # timeStamp = int(time.mktime(npKlineList[i][0].timetuple()))
        timeStamp = int(time.mktime(df.index[i].timetuple()))
        item = {}
        item['time'] = timeStamp
        item['open'] = 0 if pd.isna(npKlineList[i][0]) else npKlineList[i][0]
        item['high'] = 0 if pd.isna(npKlineList[i][1]) else npKlineList[i][1]
        item['low'] = 0 if pd.isna(npKlineList[i][2]) else npKlineList[i][2]
        item['close'] = 0 if pd.isna(npKlineList[i][3]) else npKlineList[i][3]
        item['volume'] = 0 if pd.isna(npKlineList[i][4]) else npKlineList[i][4]
        klineList.append(item)
        # print("item->", item)
    # print("期货k线结果:", klineList)
    # endTime = datetime.now() - startTime
    # print("函数时间", endTime)
    # if period=='3d':
    # print(len(klineList))
    return klineList


@lru_cache(maxsize=128)
def getStockData(symbol, period, endDate, stamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    startTime = datetime.now()
    if endDate is None or endDate == "":
        end = datetime.now() + timedelta(1)
    else:
        end = datetime.strptime(endDate, "%Y-%m-%d")
    end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    timeDeltaMap = {
        '1m': -7 * 3,
        '3m': -31 * 3,
        '5m': -31 * 3,
        '15m': -31 * 3,
        '30m': -31 * 8,
        '60m': -31 * 8,
        '180m': -31 * 8,
        '1d': -31 * 10,
        '3d': -31 * 30
    }
    start_date = end + timedelta(timeDeltaMap[period])
    code = "%s_%s" % (symbol, period)
    data_list = DBPyChanlun[code].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
        "_id": {"$gte": start_date, "$lte": end}
    }).sort("_id", pymongo.ASCENDING)
    df = pd.DataFrame(list(data_list))

    klineList = []
    for idx, row in df.iterrows():
        item = {}
        item['time'] = int(time.mktime(row["_id"].timetuple()))
        item['open'] = 0 if pd.isna(row["open"]) else row["open"]
        item['high'] = 0 if pd.isna(row["high"]) else row["high"]
        item['low'] = 0 if pd.isna(row["low"]) else row["low"]
        item['close'] = 0 if pd.isna(row["close"]) else row["close"]
        item['volume'] = 0 if pd.isna(row["volume"]) else row["volume"]
        klineList.append(item)
    return klineList


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
    df = pd.DataFrame(list(data_list))

    klineList = []
    for idx, row in df.iterrows():
        item = {'time': int(time.mktime(row["_id"].timetuple())), 'open': 0 if pd.isna(row["open"]) else row["open"],
                'high': 0 if pd.isna(row["high"]) else row["high"], 'low': 0 if pd.isna(row["low"]) else row["low"],
                'close': 0 if pd.isna(row["close"]) else row["close"],
                'volume': 0 if pd.isna(row["volume"]) else row["volume"]}
        klineList.append(item)
    return klineList
