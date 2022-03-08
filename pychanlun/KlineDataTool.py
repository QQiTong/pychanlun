# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta, time
from functools import lru_cache

import pandas as pd
import pymongo
import pytz
from QUANTAXIS.QAData.data_resample import QA_data_stockmin_resample, QA_data_day_resample, QA_data_futuremin_resample, \
    QA_data_futureday_resample
from bson.codec_options import CodecOptions

from pychanlun.db import DBPyChanlun
from pychanlun.db import DBQuantAxis
from pychanlun.data.future.db import fq_data_future_fetch_min, fq_data_future_fetch_day
from pychanlun.data.stock import fq_data_stock_fetch_min, fq_data_stock_fetch_day, fq_data_stock_resample_90min, fq_data_stock_resample_120min
from pychanlun.config import cfg

tz = pytz.timezone('Asia/Shanghai')

okexUrl = "https://www.okex.me/v2/perpetual/pc/public/instruments/BTC-USDT-SWAP/candles"
zbUrl = "http://api.zb.center/data/v1/kline?market=btc_usdt&type=1day"
# time_delta_maps[0] 用于复盘， time_delta_maps[1]用于监控
time_delta_maps = [
    {
        '1m': -25,
        '3m': -25 * 3,
        '5m': -25 * 5,
        '15m': -25 * 15,
        '30m': -25 * 30,
        '60m': -25 * 60,
        '180m': -5 * 180,
        '1d': -1000,
        '3d': -1000
    },
    {
        '1m': -7,
        '3m': -5 * 3,
        '5m': -5 * 5,
        '15m': -5 * 15,
        '30m': -5 * 30,
        '60m': -5 * 60,
        '180m': -3 * 180,
        '240m': -3 * 180,
        '1d': -1000,
        '3d': -3000
    }
]


@lru_cache(maxsize=128)
def getDigitCoinData(symbol, period, endDate, cache_stamp=int(datetime.now().timestamp()), monitor=1):
    if endDate is None or endDate == "":
        end = datetime.now() + timedelta(1)
    else:
        end = datetime.strptime(endDate, "%Y-%m-%d")
    end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    if monitor == 0:
        current_time_delta = time_delta_maps[0]
    else:
        current_time_delta = time_delta_maps[1]
    start_date = end + timedelta(current_time_delta[period])
    code = "OKEX.BTC-USDT"
    if period == "1m":
        data_list = DBQuantAxis["cryptocurrency_min"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
            "symbol": code,
            "type": "1min",
            "time_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
        }) \
            .sort("_id", pymongo.ASCENDING)
        data_list = list(data_list)
        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['time'] = kline_data['time_stamp']
        process_ohlc_str(kline_data)
        kline_data['datetime'] = kline_data['datetime'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
        kline_data.set_index('datetime', drop=False, inplace=True)
    elif period == "3m":
        data_list = DBQuantAxis["cryptocurrency_min"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
            "symbol": code,
            "type": "1min",
            "time_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
        }) \
            .sort("_id", pymongo.ASCENDING)
        data_list = list(data_list)
        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['datetime'] = kline_data['datetime'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
        kline_data = QA_data_stockmin_resample(kline_data, 3)
        kline_data['time'] = kline_data.index.to_series().apply(lambda value: value[0].timestamp())
        process_ohlc_str(kline_data)
        kline_data.set_index('datetime', drop=False, inplace=True)
    elif period == "5m":
        data_list = DBQuantAxis["cryptocurrency_min"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
            "symbol": code,
            "type": "5min",
            "time_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
        }) \
            .sort("_id", pymongo.ASCENDING)
        data_list = list(data_list)
        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['datetime'] = kline_data['datetime'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
        kline_data['time'] = kline_data['time_stamp']
        process_ohlc_str(kline_data)
        kline_data.set_index('datetime', drop=False, inplace=True)
    elif period == "15m":
        data_list = DBQuantAxis["cryptocurrency_min"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
            "symbol": code,
            "type": "15min",
            "time_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
        }) \
            .sort("_id", pymongo.ASCENDING)
        data_list = list(data_list)
        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['datetime'] = kline_data['datetime'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
        kline_data['time'] = kline_data['time_stamp']
        process_ohlc_str(kline_data)
        kline_data.set_index('datetime', drop=False, inplace=True)
    elif period == "30m":
        data_list = DBQuantAxis["cryptocurrency_min"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
            "symbol": code,
            "type": "30min",
            "time_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
        }) \
            .sort("_id", pymongo.ASCENDING)
        data_list = list(data_list)
        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['datetime'] = kline_data['datetime'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
        kline_data['time'] = kline_data['time_stamp']
        process_ohlc_str(kline_data)
        kline_data.set_index('datetime', drop=False, inplace=True)
    elif period == "60m":
        data_list = DBQuantAxis["cryptocurrency_min"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
            "symbol": code,
            "type": "60min",
            "time_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
        }) \
            .sort("_id", pymongo.ASCENDING)

        data_list = list(data_list)

        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['datetime'] = kline_data['datetime'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
        kline_data['time'] = kline_data['time_stamp']
        process_ohlc_str(kline_data)
        kline_data.set_index('datetime', drop=False, inplace=True)
    # elif period == "180m":
    #     data_list = DBQuantAxis["cryptocurrency_min"] \
    #         .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
    #         .find({
    #         "type":"60min",
    #         "symbol": code,
    #         "date_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
    #     }) \
    #         .sort("_id", pymongo.ASCENDING)
    #     data_list = list(data_list)
    #     if len(data_list) == 0:
    #         return None
    #     kline_data = pd.DataFrame(data_list)
    #     kline_data['datetime'] = kline_data['datetime'].apply(
    #         lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
    #     kline_data['volume'] = kline_data['trade'] * 100
    #     # todo 转180m 报错 AttributeError: 'RangeIndex' object has no attribute 'indexer_between_time'
    #     kline_data = QA_data_futuremin_resample(kline_data, '180min')
    #     kline_data['time'] = kline_data.index.to_series().apply(lambda value: value[0].timestamp())
    #     kline_data.set_index('datetime', drop=False, inplace=True)

    elif period == "180m" or period == "240m" or period == "1d":
        data_list = DBQuantAxis["cryptocurrency_day"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
            "symbol": code,
            "date_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
        }) \
            .sort("_id", pymongo.ASCENDING)
        data_list = list(data_list)
        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['datetime'] = kline_data['date'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d"))
        kline_data['time'] = kline_data['date_stamp']
        process_ohlc_str(kline_data)
        kline_data.set_index('datetime', drop=False, inplace=True)
    elif period == "3d":
        data_list = DBQuantAxis["cryptocurrency_day"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
            "symbol": code,
            "date_stamp": {"$gte": start_date.timestamp(), "$lte": end.timestamp()}
        }) \
            .sort("_id", pymongo.ASCENDING)
        data_list = list(data_list)
        if len(data_list) == 0:
            return None
        kline_data = pd.DataFrame(data_list)
        kline_data['date'] = kline_data['date'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d"))
        # kline_data['volume'] = kline_data['trade'] * 100

        kline_data['code'] = kline_data['symbol']
        kline_data = QA_data_day_resample(kline_data, "w")
        kline_data['datetime'] = kline_data.index
        kline_data['time'] = kline_data.index.to_series().apply(lambda value: value[0].timestamp())
        kline_data.set_index('datetime', drop=False, inplace=True)
    kline_data.fillna(0, inplace=True)
    return kline_data


'''
由于BTC从数据库中取出的ohlc都是字符串类型，将其转为float
'''


def process_ohlc_str(kline_data):
    kline_data['open'] = kline_data['open'].apply(lambda value: float(value))
    kline_data['high'] = kline_data['high'].apply(lambda value: float(value))
    kline_data['low'] = kline_data['low'].apply(lambda value: float(value))
    kline_data['close'] = kline_data['close'].apply(lambda value: float(value))

@lru_cache(maxsize=128)
def getFutureData(symbol, period, endDate, cache_stamp=int(datetime.now().timestamp())):
    return
    # if endDate is None:
    #     end = (datetime.now() + timedelta(days=1)).replace(hour=23, minute=59, second=59)
    # else:
    #     end = datetime.strptime(endDate, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    # timeDeltaMap = {
    #     '1m': -10,
    #     '3m': -41,
    #     '5m': -41,
    #     '15m': -105,
    #     '30m': -210,
    #     '60m': -420,
    #     '180m': -1000,
    #     '1d': -1000,
    #     '3d': -1000
    # }
    # start_date = end + timedelta(timeDeltaMap[period])
    # df = rq.get_price(symbol, frequency=period, fields=['open', 'high', 'low', 'close', 'volume'],
    #                   start_date=start_date, end_date=end, expect_df=False)
    # df['time'] = df.index.to_series().apply(lambda value: value.replace(tzinfo=tz).timestamp())
    # if symbol != 'AU99':
    #     df['low'] = df['low'].apply(lambda value: int(value))
    #     df['high'] = df['high'].apply(lambda value: int(value))
    #     df['open'] = df['open'].apply(lambda value: int(value))
    #     df['close'] = df['close'].apply(lambda value: int(value))
    # df.fillna(0, inplace=True)
    # return df


'''
monitor 1 监控， 0 复盘
监控获取少量数据，复盘取大量数据
# 从quantaxis数据库获取数据
'''


@lru_cache(maxsize=128)
def get_future_data_v2(symbol, period, endDate, cache_stamp=int(datetime.now().timestamp()), monitor=1):
    if endDate is None or endDate == "":
        end = datetime.now() + timedelta(1)
    else:
        end = datetime.strptime(endDate, "%Y-%m-%d")
    end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    if monitor == 0:
        current_time_delta = time_delta_maps[0]
    else:
        current_time_delta = time_delta_maps[1]
    start_date = end + timedelta(current_time_delta[period])
    code = symbol
    if period == "1m":
        kline_data = fq_data_future_fetch_min(code, "1min", start_date, end)
    elif period == "3m":
        kline_data = fq_data_future_fetch_min(code, "1min", start_date, end)
        kline_data = QA_data_futuremin_resample(kline_data, '3min')
        kline_data['time'] = kline_data.index.to_series().apply(lambda value: value[0].timestamp()- 8 * 3600)
        kline_data["time_stamp"] = kline_data['time']
        kline_data.reset_index(inplace=True)
        kline_data.set_index("datetime", inplace=True, drop=False)
    elif period == "5m":
        kline_data = fq_data_future_fetch_min(code, "5min", start_date, end)
    elif period == "15m":
        kline_data = fq_data_future_fetch_min(code, "15min", start_date, end)
    elif period == "30m":
        kline_data = fq_data_future_fetch_min(code, "30min", start_date, end)
    elif period == "60m":
        kline_data = fq_data_future_fetch_min(code, "60min", start_date, end)
    elif period == "180m":
        kline_data = fq_data_future_fetch_min(code, "60min", start_date, end)
        kline_data = QA_data_futuremin_resample(kline_data, '180min')
        kline_data['time'] = kline_data.index.to_series().apply(lambda value: value[0].timestamp()- 8 * 3600)
        kline_data["time_stamp"] = kline_data['time']
        kline_data.reset_index(inplace=True)
        kline_data.set_index("datetime", inplace=True, drop=False)
    elif period == "240m" or period == "1d":
        kline_data = fq_data_future_fetch_day(code, start_date, end)
    elif period == "3d":
        kline_data = fq_data_future_fetch_day(code, start_date, end)
        kline_data = QA_data_futureday_resample(kline_data, "w")
        kline_data.reset_index(inplace=True)
        kline_data['datetime'] = kline_data['date'].apply(lambda x: datetime.combine(x, time()))
        kline_data['date_stamp'] = kline_data['datetime'].apply(lambda x: x.timestamp())
        kline_data['time_stamp'] = kline_data['date_stamp']
        kline_data["time"] = kline_data['time_stamp']
        kline_data.reset_index(inplace=True)
        kline_data.set_index('datetime', drop=False, inplace=True)
    kline_data.fillna(0, inplace=True)
    kline_data = kline_data.round({"open": 2, "high": 2, "low": 2, "close": 2, "volume": 2, "amount": 2})
    kline_data['datetime'] = kline_data.index
    return kline_data


@lru_cache(maxsize=128)
def get_stock_data(symbol, period, endDate, cache_stamp=int(datetime.now().timestamp()), useCustomData=False):
    if endDate is None or endDate == "":
        end = datetime.now() + timedelta(1)
    else:
        end = datetime.strptime(endDate, "%Y-%m-%d")
    end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=cfg.TZ)
    start = end + timedelta(cfg.TIME_DELTA[period])
    code = symbol[2:]

    kline_data = None
    if period == "1m":
        kline_data = fq_data_stock_fetch_min(code, "1min", start, end, useCustomData=useCustomData)
    elif period == "3m":
        kline_data = fq_data_stock_fetch_min(code, "1min", start, end, useCustomData=useCustomData)
        kline_data = QA_data_stockmin_resample(kline_data, 3)
    elif period == "5m":
        kline_data = fq_data_stock_fetch_min(code, "5min", start, end, useCustomData=useCustomData)
    elif period == "15m":
        kline_data = fq_data_stock_fetch_min(code, "15min", start, end, useCustomData=useCustomData)
    elif period == "30m":
        kline_data = fq_data_stock_fetch_min(code, "30min", start, end, useCustomData=useCustomData)
    elif period == "60m":
        kline_data = fq_data_stock_fetch_min(code, "60min", start, end, useCustomData=useCustomData)
    elif period == "90m":
        if useCustomData:
            kline_data = fq_data_stock_fetch_min(code, "90min", start, end, useCustomData=useCustomData)
        else:
            kline_data = fq_data_stock_fetch_min(code, "30min", start, end, useCustomData=useCustomData)
            kline_data = fq_data_stock_resample_90min(kline_data)
    elif period == "120m":
        if useCustomData:
            kline_data = fq_data_stock_fetch_min(code, "120min", start, end, useCustomData=useCustomData)
        else:
            kline_data = fq_data_stock_fetch_min(code, "60min", start, end, useCustomData=useCustomData)
            kline_data = fq_data_stock_resample_120min(kline_data)
    elif period == "1d":
        kline_data = fq_data_stock_fetch_day(code, start, end, useCustomData=useCustomData)
    elif period == "1w":
        kline_data = fq_data_stock_fetch_day(code, start, end, useCustomData=useCustomData)
        kline_data = QA_data_day_resample(kline_data, "w")
        kline_data['time_stamp'] = kline_data.index.to_series().apply(lambda value: value[0].timestamp())
    if kline_data is not None:
        kline_data.fillna(0, inplace=True)
    kline_data['datetime'] = kline_data.index
    return kline_data

@lru_cache(maxsize=128)
def getStockData(symbol, period, endDate, cache_stamp=int(datetime.now().timestamp()), monitor=1):
    if endDate is None or endDate == "":
        end = datetime.now() + timedelta(1)
    else:
        end = datetime.strptime(endDate, "%Y-%m-%d")
    end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    if monitor == 0:
        current_time_delta = time_delta_maps[0]
    else:
        current_time_delta = time_delta_maps[1]
    start_date = end + timedelta(current_time_delta[period])
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
        kline_data['datetime'] = kline_data['datetime'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
        kline_data.set_index('datetime', drop=False, inplace=True)
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
        kline_data['datetime'] = kline_data['datetime'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
        kline_data = QA_data_stockmin_resample(kline_data, 3)
        kline_data['time'] = kline_data.index.to_series().apply(lambda value: value[0].timestamp())
        kline_data.set_index('datetime', drop=False, inplace=True)
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
        kline_data['datetime'] = kline_data['datetime'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
        kline_data['time'] = kline_data['time_stamp']
        kline_data.set_index('datetime', drop=False, inplace=True)
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
        kline_data['datetime'] = kline_data['datetime'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
        kline_data['time'] = kline_data['time_stamp']
        kline_data.set_index('datetime', drop=False, inplace=True)
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
        kline_data['datetime'] = kline_data['datetime'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
        kline_data['time'] = kline_data['time_stamp']
        kline_data.set_index('datetime', drop=False, inplace=True)
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
        kline_data['datetime'] = kline_data['datetime'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
        kline_data['time'] = kline_data['time_stamp']
        kline_data.set_index('datetime', drop=False, inplace=True)
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
        kline_data['datetime'] = kline_data['date'].apply(
            lambda value: datetime.strptime(value, "%Y-%m-%d"))
        kline_data['time'] = kline_data['date_stamp']
        kline_data.set_index('datetime', drop=False, inplace=True)
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
        kline_data['datetime'] = kline_data.index
        kline_data['time'] = kline_data.index.to_series().apply(lambda value: value[0].timestamp())
        kline_data.set_index('datetime', drop=False, inplace=True)

    kline_data.fillna(0, inplace=True)
    return kline_data


@lru_cache(maxsize=128)
def getGlobalFutureData(symbol, period, endDate, cache_stamp=int(datetime.now().timestamp()), monitor=1):
    # 通达信还未完成，暂时先用新浪内盘数据源
    if "L9" in symbol:
        symbol = symbol[:-2] + "0"
    # print("symbol", symbol)
    if endDate is None or endDate == "":
        end = datetime.now() + timedelta(1)
    else:
        end = datetime.strptime(endDate, "%Y-%m-%d")
    end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    if monitor == 0:
        current_time_delta = time_delta_maps[0]
    else:
        current_time_delta = time_delta_maps[1]
    start_date = end + timedelta(current_time_delta[period])
    code = "%s_%s" % (symbol, period)
    data_list = DBPyChanlun[code] \
        .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
        .find({"_id": {"$gte": start_date, "$lte": end}}).sort("_id", pymongo.ASCENDING)
    data_list = list(data_list)
    if len(data_list) == 0:
        return None
    kline_data = pd.DataFrame(data_list)
    kline_data['time'] = kline_data['_id'].apply(lambda value: value.timestamp())
    kline_data['time_stamp'] = kline_data['time']
    kline_data['datetime'] = kline_data['_id']
    kline_data.fillna(0, inplace=True)
    return kline_data


def current_minute(symbol):
    return rq.current_minute(symbol)
