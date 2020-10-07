# -*- coding: utf-8 -*-

import json
import time
from datetime import datetime, timedelta
from functools import lru_cache

import pandas as pd
import pymongo
import pytz
import requests
import rqdatac as rq
from QUANTAXIS.QAData.data_resample import QA_data_stockmin_resample, QA_data_day_resample
from bson.codec_options import CodecOptions

from pychanlun.db import DBPyChanlun
from pychanlun.db import DBQuantAxis

tz = pytz.timezone('Asia/Shanghai')

okexUrl = "https://www.okex.me/v2/perpetual/pc/public/instruments/BTC-USDT-SWAP/candles"


@lru_cache(maxsize=128)
def getDigitCoinData(symbol, period, endDate, stamp=datetime.now().strftime("%Y-%m-%d %H:%M")):
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
def getFutureData(symbol, period, endDate, stamp=datetime.now().strftime("%Y-%m-%d %H:%M")):
    # 聚宽数据源
    if endDate is None:
        end = datetime.now().replace(hour=23, minute=59, second=59)
    else:
        end = datetime.strptime(endDate, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    timeDeltaMap = {
        '1m': -10,
        '3m': -41,
        '5m': -35,
        '15m': -105,
        '30m': -210,
        '60m': -420,
        '180m': -1000,
        '1d': -1000,
        '3d': -1000
    }
    start_date = end + timedelta(timeDeltaMap[period])
    df = rq.get_price(symbol, frequency=period, fields=['open', 'high', 'low', 'close', 'volume'], start_date=start_date, end_date=end)
    df['time'] = df.index.to_series().apply(lambda value: value.replace(tzinfo=tz).timestamp())
    df.fillna(0, inplace=True)
    return df


@lru_cache(maxsize=128)
def getStockData(symbol, period, endDate, stamp=datetime.now().strftime("%Y-%m-%d %H:%M")):
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
        '240m': -5 * 180,
        '1d': -1000,
        '3d': -3000
    }
    start_date = end + timedelta(timeDeltaMap[period])
    code = symbol[2:]
    if period == "1m":
        data_list = DBQuantAxis["stock_min"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
                "code": code,
                "type": "1min",
                "time_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
            }) \
            .sort("_id", pymongo.ASCENDING)
        data_list = list(data_list)
        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['time'] = kline_data['time_stamp']
    elif period == "3m":
        data_list = DBQuantAxis["stock_min"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
                "code": code,
                "type": "1min",
                "time_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
            }) \
            .sort("_id", pymongo.ASCENDING)
        data_list = list(data_list)
        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['datetime'] = kline_data['datetime'].apply(lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
        kline_data = QA_data_stockmin_resample(kline_data, 3)
        kline_data['time'] = kline_data.index.to_series().apply(lambda value: value[0].timestamp())

    elif period == "5m":
        data_list = DBQuantAxis["stock_min"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
                "code": code,
                "type": "5min",
                "time_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
            }) \
            .sort("_id", pymongo.ASCENDING)
        data_list = list(data_list)
        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['time'] = kline_data['time_stamp']
    elif period == "15m":
        data_list = DBQuantAxis["stock_min"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
                "code": code,
                "type": "15min",
                "time_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
            }) \
            .sort("_id", pymongo.ASCENDING)
        data_list = list(data_list)
        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['time'] = kline_data['time_stamp']
    elif period == "30m":
        data_list = DBQuantAxis["stock_min"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
                "code": code,
                "type": "30min",
                "time_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
            }) \
            .sort("_id", pymongo.ASCENDING)
        data_list = list(data_list)
        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['time'] = kline_data['time_stamp']
    elif period == "60m":
        data_list = DBQuantAxis["stock_min"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
                "code": code,
                "type": "60min",
                "time_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
            }) \
            .sort("_id", pymongo.ASCENDING)
        data_list = list(data_list)
        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['time'] = kline_data['time_stamp']
    elif period == "180m" or period == "240m" or period == "1d":
        data_list = DBQuantAxis["stock_day"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
                "code": code,
                "date_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
            }) \
            .sort("_id", pymongo.ASCENDING)
        data_list = list(data_list)
        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['time'] = kline_data['date_stamp']
    elif period == "3d":
        data_list = DBQuantAxis["stock_day"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
                "code": code,
                "date_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
            }) \
            .sort("_id", pymongo.ASCENDING)
        data_list = list(data_list)
        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['date'] = kline_data['date'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d"))
        kline_data = QA_data_day_resample(kline_data, "w")
        kline_data['time'] = kline_data.index.to_series().apply(lambda value: value[0].timestamp())

    kline_data.fillna(0, inplace=True)
    return kline_data


@lru_cache(maxsize=128)
def getGlobalFutureData(symbol, period, endDate, stamp=datetime.now().strftime("%Y-%m-%d %H:%M")):
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
    if len(data_list) == 0:
        return None
    kline_data = pd.DataFrame(data_list)
    kline_data['time'] = kline_data['_id'].apply(lambda value: value.timestamp())
    kline_data.fillna(0, inplace=True)
    return kline_data
