"""
策略4：回拉中枢或者突破中枢开仓
"""

import logging
from datetime import datetime, timedelta
import time
import pytz
import pandas as pd
import talib as ta
import numpy as np
import rx
import pymongo
from rx.scheduler import ThreadPoolScheduler
from rx.scheduler.eventloop import AsyncIOScheduler
from rx import operators as ops

import pydash
import json
import traceback

from ..funcat.data.HuobiDataBackend import HuobiDataBackend
from ..funcat.utils import get_int_date
from ..funcat.api import *

from ..KlineProcess import KlineProcess
from ..BiProcess import BiProcess
from ..DuanProcess import DuanProcess
from .. import entanglement as entanglement
from .. import divergence as divergence
from ..Mail import Mail
from .. import Duan
from ..db import DBPyChanlun
from .MarketData import is_data_feeding

tz = pytz.timezone('Asia/Shanghai')
mail = Mail()

def doExecute(symbol, period):
    if not is_data_feeding(symbol['code'], period):
        return
    logger = logging.getLogger()
    logger.info("策略4 %s %s" % (symbol['code'], period))
    raw_data = {}
    bars = DBPyChanlun['%s_%s' % (symbol['code'].lower(), period)].find().sort('_id', pymongo.DESCENDING).limit(1000)
    bars = list(bars)
    if len(bars) < 13:
        return
    time_series = []
    high_series = []
    low_series = []
    open_series = []
    close_series = []
    count = len(bars)
    for i in range(count - 1, -1, -1):
        time_series.append(bars[i]['_id'])
        high_series.append(bars[i]['high'])
        low_series.append(bars[i]['low'])
        open_series.append(bars[i]['open'])
        close_series.append(bars[i]['close'])
    kline_process = KlineProcess()
    for i in range(count):
        kline_process.add(high_series[i], low_series[i], time_series[i])
    bi_process = BiProcess()
    bi_process.handle(kline_process.klineList)
    direction_series = [0 for i in range(count)]
    # 笔信号
    bi_series = [0 for i in range(count)]
    for i in range(len(bi_process.biList)):
        item = bi_process.biList[i]
        bi_series[item.klineList[-1].middle] = item.direction
        for j in range(item.start + 1, item.end + 1):
            direction_series[j] = item.direction
    duan_process = DuanProcess()
    duan_series = duan_process.handle(bi_series, high_series, low_series)
    higher_duan_process = DuanProcess()
    higher_duan_series = higher_duan_process.handle(duan_series, high_series, low_series)
    # 笔中枢的会拉和突破
    entanglement_list = entanglement.calcEntanglements(time_series, duan_series, bi_series, high_series, low_series)
    zs_huila = entanglement.la_hui(entanglement_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series)
    zs_tupo = entanglement.tu_po(entanglement_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series)

    count = len(zs_huila['buy_zs_huila']['date'])
    for i in range(count):
        saveLog(symbol, period, raw_data, True, '拉回中枢确认底背', zs_huila['buy_zs_huila']['date'][i], zs_huila['buy_zs_huila']['data'][i], 'BuyLong')
    count = len(zs_huila['sell_zs_huila']['date'])
    for i in range(count):
        saveLog(symbol, period, raw_data, True, '拉回中枢确认顶背', zs_huila['sell_zs_huila']['date'][i], zs_huila['sell_zs_huila']['data'][i], 'SellShort')

    count = len(zs_tupo['buy_zs_tupo']['date'])
    for i in range(count):
        saveLog(symbol, period, raw_data, True, '突破中枢开多', zs_tupo['buy_zs_tupo']['date'][i], zs_tupo['buy_zs_tupo']['data'][i], 'BuyLong')
    count = len(zs_tupo['sell_zs_tupo']['date'])
    for i in range(count):
        saveLog(symbol, period, raw_data, True, '突破中枢开空', zs_tupo['sell_zs_tupo']['date'][i], zs_tupo['sell_zs_tupo']['data'][i], 'SellShort')

    # 段中枢的回拉和突破
    higher_entaglement_list = entanglement.calcEntanglements(time_series, higher_duan_series, duan_series, high_series, low_series)
    higher_zs_huila = entanglement.la_hui(higher_entaglement_list, time_series, high_series, low_series, open_series, close_series, duan_series, higher_duan_series)
    higher_zs_tupo = entanglement.tu_po(higher_entaglement_list, time_series, high_series, low_series, open_series, close_series, duan_series, higher_duan_series)

    count = len(higher_zs_huila['buy_zs_huila']['date'])
    for i in range(count):
        saveLog(symbol, period, raw_data, True, '拉回中枢确认底背', higher_zs_huila['buy_zs_huila']['date'][i], higher_zs_huila['buy_zs_huila']['data'][i], 'BuyLong')
    count = len(higher_zs_huila['sell_zs_huila']['date'])
    for i in range(count):
        saveLog(symbol, period, raw_data, True, '拉回中枢确认顶背', higher_zs_huila['sell_zs_huila']['date'][i], higher_zs_huila['sell_zs_huila']['data'][i], 'SellShort')

    count = len(higher_zs_tupo['buy_zs_tupo']['date'])
    for i in range(count):
        saveLog(symbol, period, raw_data, True, '突破中枢开多', higher_zs_tupo['buy_zs_tupo']['date'][i], higher_zs_tupo['buy_zs_tupo']['data'][i], 'BuyLong')
    count = len(higher_zs_tupo['sell_zs_tupo']['date'])
    for i in range(count):
        saveLog(symbol, period, raw_data, True, '突破中枢开空', higher_zs_tupo['sell_zs_tupo']['date'][i], higher_zs_tupo['sell_zs_tupo']['data'][i], 'SellShort')

def saveLog(symbol, period, raw_data, signal, remark, fire_time, price, position):
    last_fire = DBPyChanlun['strategy4_log'].find_one({
        'symbol': symbol['code'],
        'peroid': period,
        'fire_time': fire_time,
        'position': position
    })

    if last_fire is not None:
        DBPyChanlun['strategy4_log'].find_one_and_update({
            'symbol': symbol['code'], 'period': period, 'fire_time': fire_time, 'position': position
        }, {
            '$set': {
                'remark': remark,
                'price': price,
                'date_created': datetime.utcnow()
            },
            '$inc': {
                'update_count': 1
            }
        }, upsert=True)
    else:
        date_created = datetime.utcnow()
        DBPyChanlun['strategy4_log'].insert_one({
            'symbol': symbol['code'],
            'period': period,
            'raw_data': raw_data,
            'signal': True,
            'remark': remark,
            'date_created': date_created,#记录插入的时间
            'fire_time': fire_time, #背驰发生的时间
            'price': price,
            'position': position,
            'update_count': 1, # 这条背驰记录的更新次数
        })
        if (date_created - fire_time).total_seconds() < 600:
            # 在10分钟内的触发邮件通知
            mailResult = mail.send("%s %s %s %s" % (symbol['code'], fire_time, price, position))
            print(mailResult)


def doCaculate(symbol):
    logger = logging.getLogger()
    periods = ['3m', '5m', '15m', '30m', '1h', '4h','1d']
    for period in periods:
        try:
            doExecute(symbol, period)
        except BaseException as e:
            logger.info("Error Occurred: {0}".format(traceback.format_exc()))

