import logging
import traceback
import multiprocessing
import rx
import asyncio
import pytz
import pandas as pd
from threading import current_thread
from datetime import datetime, timedelta
from rx.scheduler import ThreadPoolScheduler
from rx.scheduler.eventloop import AsyncIOScheduler
from rx import operators as ops

from ..db import DBPyChanlun
from ..funcat.data.HuobiDataBackend import HuobiDataBackend
from ..funcat.data.RicequantDataBackend import RicequantDataBackend

optimal_thread_count = multiprocessing.cpu_count() * 5
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

loop = asyncio.get_event_loop()
aio_scheduler = AsyncIOScheduler(loop=loop)

ohlc_dict = { 'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum' }

def getMarketDataHUOBI(symbol):
    dataBackend = HuobiDataBackend()
    # 1m数据
    df1m = dataBackend.get_price(symbol['code'], 0, 500, '1min')
    if df1m is None:
        return
    saveData(symbol['code'], df1m, "1m")
    # 3m数据
    df3m = df1m.resample('3T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol['code'], df3m, "3m")
    # 5m数据
    df5m = df1m.resample('5T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol['code'], df5m, "5m")
    # 15m数据
    df15m = df1m.resample('15T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol['code'], df15m, "15m")
    # 30m数据
    df30m = df1m.resample('30T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol['code'], df30m, "30m")
    # 1h数据
    df1h = df1m.resample('60T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol['code'], df1h, "1h")
    # 4h数据
    df4h = df1m.resample('4H', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol['code'], df4h, "4h")
    # 1d数据
    df1d = dataBackend.get_price(symbol['code'], 0, 500, '1day')
    saveData(symbol['code'], df1d, "1d")
    # 1w数
    df1w = df1d.resample('W', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol['code'], df1w, "1w")


def getMarketDataRICEQUANT(symbol):
    dataBackend = RicequantDataBackend()
    start = datetime.now() + timedelta(-3)
    end = datetime.now() + timedelta(1)
    df1m = dataBackend.get_price(symbol['code'], start, end, '1m')
    if df1m is None:
        return
    saveData(symbol['code'], df1m, "1m")
    # 3m数据
    df3m = df1m.resample('3T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol['code'], df3m, "3m")
    # 5m数据
    df5m = df1m.resample('5T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol['code'], df5m, "5m")
    # 15m数据
    df15m = df1m.resample('15T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol['code'], df15m, "15m")
    # 30m数据
    df30m = df1m.resample('30T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol['code'], df30m, "30m")
    # 1h数据
    df1h = df1m.resample('60T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol['code'], df1h, "1h")

    start = datetime.now() + timedelta(-3)
    end = datetime.now() + timedelta(1)

    # 4h数据
    df4h = dataBackend.get_price(symbol['code'], start, end, '240m')
    saveData(symbol['code'], df4h, "4h")
    # 1d数据
    df1d = dataBackend.get_price(symbol['code'], start, end, '1d')
    saveData(symbol['code'], df1d, "1d")
    # 1w数据
    df1w = df1d.resample('W', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol['code'], df1w, "1w")

def getMarketData(symbol):
    logger = logging.getLogger()
    logger.info("下载市场行情数据 %s" % symbol['code'])
    df1m = None
    try:
        if symbol['backend'] == 'HUOBI':
            getMarketDataHUOBI(symbol)
        if symbol['backend'] == 'RICEQUANT':
            getMarketDataRICEQUANT(symbol)
    except BaseException as e:
        logger.info("Error Occurred: {0}".format(traceback.format_exc()))

def saveData(code, df, period):
    logger = logging.getLogger()
    logger.info("保存行情数据 %s %s" % (code, period))
    for time, row in df.iterrows():
        try:
            DBPyChanlun['%s_%s' % (code.lower(), period)].find_one_and_update({
                '_id': time
            }, {
                '$set': {
                    'open': round(row['open'].item(), 2),
                    'close': round(row['close'].item(), 2),
                    'high': round(row['high'].item(), 2),
                    'low': round(row['low'].item(), 2),
                    'volume': round(row['volume'].item(), 2),
                    'date_created': datetime.now(pytz.timezone("Asia/Shanghai"))
                }
            }, upsert = True)
        except BaseException as e:
            logger.info("Error Occurred: {0}".format(traceback.format_exc()))
