import logging
import traceback
import multiprocessing
import rx
import asyncio
import pytz
import pydash
import pymongo
import pandas as pd
from threading import current_thread
from datetime import datetime, timedelta
from rx.scheduler import ThreadPoolScheduler
from rx.scheduler.eventloop import AsyncIOScheduler
from rx import operators as ops
from bson.codec_options import CodecOptions

from ..db import DBPyChanlun
from ..funcat.data.HuobiDataBackend import HuobiDataBackend
from ..funcat.data.RicequantDataBackend import RicequantDataBackend

optimal_thread_count = multiprocessing.cpu_count() * 5
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

loop = asyncio.get_event_loop()
aio_scheduler = AsyncIOScheduler(loop=loop)

tz = pytz.timezone('Asia/Shanghai')

ohlc_dict = { 'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum' }


def is_data_feeding(code, period):
    # 通过判断5分钟内有数据更新
    data = DBPyChanlun['%s_%s' % (code.lower(), period)].find({
        'date_created': { '$gte': datetime.now(pytz.timezone("Asia/Shanghai"))-timedelta(minutes=5) }
    })
    return len(list(data)) > 0

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

def get_market_data_ricequant_incr(symbol, period, period_alias = None, is_debug = False):
    if period_alias is None:
        period_alias = period
    logger = logging.getLogger()
    code = symbol['code']
    dataBackend = RicequantDataBackend()
    last = DBPyChanlun['%s_%s' % (code.lower(), period_alias)].with_options(
        codec_options=CodecOptions(tz_aware=True, tzinfo=tz)
    ).find().sort('_id', pymongo.DESCENDING).limit(1)
    last = list(last)
    if len(last) == 0:
        last = None
    else:
        last = last[0]
    # 默认先下载30天的数据
    now_datetime = datetime.now(tz)
    start_datetime = datetime.now(tz) + timedelta(days=-30)
    # 今天的开始时间
    start_of_day = datetime(now_datetime.year, now_datetime.month, now_datetime.day, tzinfo=tz)
    # 今天的结束日期
    end_of_day = datetime(now_datetime.year, now_datetime.month, now_datetime.day, 23, 59, 59, tzinfo=tz)
    last_datetime = None
    if last is not None:
        last_datetime = last['_id']
        start_datetime = last['_id']
    # 如果开始日期不是今天，那么一天一天地下载历史数据
    if start_datetime < start_of_day:
        start_datetime = datetime(start_datetime.year, start_datetime.month, start_datetime.day, tzinfo=tz)
    while start_datetime < start_of_day:
        end_datetime = datetime(start_datetime.year, start_datetime.month, start_datetime.day, 23, 59, 59, tzinfo=tz)
        trading_dates = dataBackend.get_trading_dates(start_date=start_datetime.strftime('%Y%m%d'), end_date=start_datetime.strftime('%Y%m%d'))
        # 不是交易日跳过
        if trading_dates is None or len(trading_dates) == 0:
            start_datetime = start_datetime + timedelta(days=1)
            continue
        # get_trading_hours 返回的时间是不对的
        magic = int(now_datetime.timestamp() / 1800)
        trading_date = start_datetime.strftime('%Y-%m-%d')
        trading_hours1 = dataBackend.get_trading_hours(code=code, trading_date=trading_date, magic=magic)
        trading_date = dataBackend.get_next_trading_date(trading_date).strftime('%Y-%m-%d')
        trading_hours2 = dataBackend.get_trading_hours(code=code, trading_date=trading_date, magic=magic)
        trading_hours = []
        for trading_hour in trading_hours1:
            trading_hour[0] = trading_hour[0].replace(tzinfo=tz)
            trading_hour[1] = trading_hour[1].replace(tzinfo=tz)
            if trading_hour[1] >end_of_day:
                break
            trading_hours.append(trading_hour)
        for trading_hour in trading_hours2:
            trading_hour[0] = trading_hour[0].replace(tzinfo=tz)
            trading_hour[1] = trading_hour[1].replace(tzinfo=tz)
            if trading_hour[1] >end_of_day:
                break
            trading_hours.append(trading_hour)
        if trading_hours is None or len(trading_hours) == 0:
            start_datetime = start_datetime + timedelta(days=1)
            continue
        if last_datetime is not None:
            if period_alias == '1d' and last is not None:
                if last.get('date_created') is not None and last['date_created'] > trading_hours[-1][1]:
                    start_datetime = start_datetime + timedelta(days=1)
                    continue
            else:
                if last_datetime >= trading_hours[-1][1]:
                    start_datetime = start_datetime + timedelta(days=1)
                    continue
        df = dataBackend.get_price(symbol['code'], start_datetime, end_datetime + timedelta(1), period)

        if df is None:
            start_datetime = start_datetime + timedelta(days=1)
            continue
        logger.info("保存行情数据 %s %s %s %s" % (code, period_alias, start_datetime, end_datetime))
        saveData(symbol['code'], df, period_alias)
        start_datetime = start_datetime + timedelta(days=1)

    end_datetime = datetime(start_datetime.year, start_datetime.month, start_datetime.day, 23, 59, 59, tzinfo=tz)
    trading_dates = dataBackend.get_trading_dates(start_date=start_datetime.strftime('%Y%m%d'), end_date=start_datetime.strftime('%Y%m%d'))
    if trading_dates is None or len(trading_dates) == 0:
        return
    # get_trading_hours 返回的时间是不对的
    magic = int(now_datetime.timestamp() / 1800)
    trading_date = start_datetime.strftime('%Y-%m-%d')
    trading_hours1 = dataBackend.get_trading_hours(code=code, trading_date=trading_date, magic=magic)
    trading_date = dataBackend.get_next_trading_date(trading_date).strftime('%Y-%m-%d')
    trading_hours2 = dataBackend.get_trading_hours(code=code, trading_date=trading_date, magic=magic)
    trading_hours = []
    for trading_hour in trading_hours1:
        trading_hour[0] = trading_hour[0].replace(tzinfo=tz)
        trading_hour[1] = trading_hour[1].replace(tzinfo=tz)
        if trading_hour[1] >end_of_day:
            break
        trading_hours.append(trading_hour)
    for trading_hour in trading_hours2:
        trading_hour[0] = trading_hour[0].replace(tzinfo=tz)
        trading_hour[1] = trading_hour[1].replace(tzinfo=tz)
        if trading_hour[1] >end_of_day:
            break
        trading_hours.append(trading_hour)
    if trading_hours is None or len(trading_hours) == 0:
        return
    if last_datetime is not None:
        if period_alias == '1d' and last is not None:
            if last.get('date_created') is not None and last['date_created'] > trading_hours[-1][1].replace(tzinfo=tz):
                return
        else:
            hours_index = pydash.find_last_index(trading_hours, lambda x: x[1].replace(tzinfo=tz) < now_datetime)
            if hours_index >= 0:
                if last_datetime >= trading_hours[hours_index][1].replace(tzinfo=tz):
                    return
    df = dataBackend.get_price(symbol['code'], start_datetime, end_datetime + timedelta(1), period)
    if df is None:
        return
    logger.info("保存行情数据 %s %s %s %s" % (code, period_alias, start_datetime, end_datetime))
    saveData(symbol['code'], df, period_alias)

def getMarketDataRICEQUANT(symbol, is_debug = False):
    get_market_data_ricequant_incr(symbol, '1m', period_alias=None, is_debug=is_debug)
    get_market_data_ricequant_incr(symbol, '3m', period_alias=None, is_debug=is_debug)
    get_market_data_ricequant_incr(symbol, '5m', period_alias=None, is_debug=is_debug)
    get_market_data_ricequant_incr(symbol, '15m', period_alias=None, is_debug=is_debug)
    get_market_data_ricequant_incr(symbol, '30m', period_alias=None, is_debug=is_debug)
    get_market_data_ricequant_incr(symbol, '60m', '1h', is_debug)
    get_market_data_ricequant_incr(symbol, '240m', '4h', is_debug)
    get_market_data_ricequant_incr(symbol, '1d', period_alias=None, is_debug=is_debug)

def getMarketData(symbol, is_debug = False):

    logger = logging.getLogger()
    df1m = None
    try:
        if symbol['backend'] == 'HUOBI':
            getMarketDataHUOBI(symbol)
        if symbol['backend'] == 'RICEQUANT':
            getMarketDataRICEQUANT(symbol, is_debug)
    except BaseException as e:
        logger.info("Error Occurred: {0}".format(traceback.format_exc()))

def saveData(code, df, period):
    logger = logging.getLogger()
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
    DBPyChanlun['symbol'].update_one({ "code": code }, { "$set": { "market_data_updated": datetime.now(tz) } })
