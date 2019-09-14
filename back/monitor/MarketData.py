import logging

import multiprocessing
from threading import current_thread
import pandas as pd
from datetime import datetime, timedelta

import asyncio

import rx
from rx.scheduler import ThreadPoolScheduler
from rx.scheduler.eventloop import AsyncIOScheduler

from rx import operators as ops

from ..model.Symbol import Symbol
from ..model.Bar import Bar
from ..funcat.data.HuobiDataBackend import HuobiDataBackend
from ..funcat.data.RicequantDataBackend import RicequantDataBackend

optimal_thread_count = multiprocessing.cpu_count() * 5
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

loop = asyncio.get_event_loop()
aio_scheduler = AsyncIOScheduler(loop=loop)

ohlc_dict = { 'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum' }


def getData1(symbol):
    logger = logging.getLogger()
    logger.info(symbol.code)
    df1m = None
    if symbol.backend == 'HUOBI':
        dataBackend = HuobiDataBackend()
        # 1m数据
        df1m = dataBackend.get_price(symbol.code, 0, 500, '1min')
    if symbol.backend == 'RICEQUANT':
        dataBackend = RicequantDataBackend()
        start = datetime.now() + timedelta(-3)
        end = datetime.now() + timedelta(1)
        df1m = dataBackend.get_price(symbol.code, start, end, '1m')
    saveData(symbol.code, df1m, "1m")
    # 3m数据
    df3m = df1m.resample('3T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol.code, df3m, "3m")
    # 5m数据
    df5m = df1m.resample('5T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol.code, df5m, "5m")
    # 15m数据
    df15m = df1m.resample('15T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol.code, df15m, "15m")
    # 30m数据
    df30m = df1m.resample('30T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol.code, df30m, "30m")
    # 1h数据
    df1h = df1m.resample('60T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol.code, df1h, "1h")
    # 4h数据
    df4h = df1m.resample('4H', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    saveData(symbol.code, df4h, "4h")


def getData2(symbol):
    if symbol.backend == 'HUOBI':
        dataBackend = HuobiDataBackend()
        # 1d数据
        df1d = dataBackend.get_price(symbol.code, 0, 500, '1day')
        saveData(symbol.code, df1d, "1d")
        df1w = df1d.resample('W', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
        saveData(symbol.code, df1w, "1w")
    if symbol.backend == 'RICEQUANT':
        dataBackend = RicequantDataBackend()
        start = datetime.now() + timedelta(-3)
        end = datetime.now() + timedelta(1)
        df1d = dataBackend.get_price(symbol.code, start, end, '1d')
        saveData(symbol.code, df1d, "1d")
        df1w = df1d.resample('W', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
        saveData(symbol.code, df1w, "1w")


def saveData(code, df, period):
    logger = logging.getLogger()
    logger.info("保存行情数据 %s %s" % (code, period))
    for time, row in df.iterrows():
        bar = Bar(time = time, open = row['open'], close = row['close'], high = row['high'], low = row['low'], volume = row['volume'])
        bar.switch_collection('%s_%s' % (code.lower(), period))
        bar.save()



# 取1m数据，聚合3m、5m、15m、30m和1h的数据
def getMarketData1():
    logger = logging.getLogger()
    logger.info("取市场行情 3m、5m、15m、30m、1h和4h")
    source = rx.from_(Symbol.objects()).pipe(
        ops.catch(lambda e: logger.info("Error Occurred: {0}".format(e)))
    ).subscribe(
        on_next = lambda symbol: getData1(symbol),
        on_error = lambda e: logger.info("Error Occurred: {0}".format(e)),
        on_completed = lambda: logger.info("Done!"),
    )


# 取1h, 4h, 1d, 1w的数据
def getMarketData2():
    logger = logging.getLogger()
    logger.info("取市场行情 1d和1w")
    source = rx.from_(Symbol.objects()).pipe(
        ops.catch(lambda e: logger.info("Error Occurred: {0}".format(e)))
    ).subscribe(
        on_next = lambda symbol: getData2(symbol),
        on_error = lambda e: logger.info("Error Occurred: {0}".format(e)),
        on_completed = lambda: logger.info("Done!"),
    )