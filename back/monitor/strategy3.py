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

tz = pytz.timezone('Asia/Shanghai')
mail = Mail()


def doExecute(symbol, period1, period2, inspect_time = None, is_debug = False):
    logger = logging.getLogger()
    logger.info("策略3 %s %s %s" % (symbol['code'], period1, period2))
    if is_debug:
        print(period1, period2, 'inspect_time', inspect_time)
    rawData = {}
    bars1 = []
    bars2 = []
    if inspect_time is None:
        bars1 = DBPyChanlun['%s_%s' % (symbol['code'].lower(), period1)].find().sort('_id', pymongo.DESCENDING).limit(1000)
        bars1 = list(bars1)
        bars2 = DBPyChanlun['%s_%s' % (symbol['code'].lower(), period2)].find().sort('_id', pymongo.DESCENDING).limit(1000)
        bars2 = list(bars2)
        # 对齐时间
        t = min(bars1[0]['_id'], bars2[0]['_id'])
        bars1 = pydash.filter_(bars1, lambda x: x['_id'] <= t)
        bars2 = pydash.filter_(bars2, lambda x: x['_id'] <= t)
    else:
        bars1 = DBPyChanlun['%s_%s' % (symbol['code'].lower(), period1)].find({
            '_id': { '$lte': inspect_time }
        }).sort('_id', pymongo.DESCENDING).limit(1000)
        bars1 = list(bars1)
        bars2 = DBPyChanlun['%s_%s' % (symbol['code'].lower(), period2)].find({
            '_id': { '$lte': inspect_time }
        }).sort('_id', pymongo.DESCENDING).limit(1000)
        bars2 = list(bars2)
    if is_debug:
        print('bars1', len(bars1), 'bars2', len(bars2))
    if len(bars1) < 13 or len(bars2) < 13:
        if is_debug: print('周期数不够')
        return
    period1Time = []
    period1High = []
    period1Low = []
    period1Open = []
    period1Close = []
    len1 = len(bars1)
    for i in range(len1 - 1, -1, -1):
        period1Time.append(int(time.mktime(bars1[i]['_id'].timetuple())))
        period1High.append(bars1[i]['high'])
        period1Low.append(bars1[i]['low'])
        period1Open.append(bars1[i]['open'])
        period1Close.append(bars1[i]['close'])
    period2Time = []
    period2High = []
    period2Low = []
    period2Open = []
    period2Close = []
    len2 = len(bars2)
    for i in range(len2 - 1, -1, -1):
        period2Time.append(int(time.mktime(bars2[i]['_id'].timetuple())))
        period2High.append(bars2[i]['high'])
        period2Low.append(bars2[i]['low'])
        period2Open.append(bars2[i]['open'])
        period2Close.append(bars2[i]['close'])
    # 计算MACD
    period1Diff, period1Dea, period1Macd = ta.MACD(np.array([float(x) for x in period1Close]), fastperiod=12, slowperiod=26, signalperiod=9)
    period1Diff = np.nan_to_num(period1Diff)
    period1Dea = np.nan_to_num(period1Dea)
    period1Macd = np.nan_to_num(period1Macd)
    period2Diff, period2Dea, period2Macd = ta.MACD(np.array([float(x) for x in period2Close]), fastperiod=12, slowperiod=26, signalperiod=9)
    period2Diff = np.nan_to_num(period1Diff)
    period2Dea = np.nan_to_num(period2Dea)
    period2Macd = np.nan_to_num(period2Macd)

    # 本周期K线处理
    period1KlineProcess = KlineProcess()
    for i in range(len1):
        period1KlineProcess.add(period1High[i], period1Low[i], period1Time[i])
    # 本周期笔处理
    period1BiProcess = BiProcess()
    period1BiProcess.handle(period1KlineProcess.klineList)
    period1BiResult = period1BiProcess.biResult(len1)
    # 本周期段处理
    period1DuanProcess = DuanProcess()
    period1DuanResult = period1DuanProcess.handle(period1BiResult, period1High, period1Low)

    # 高周期K线处理
    period2KlineProcess = KlineProcess()
    for i in range(len2):
        period2KlineProcess.add(period2High[i], period2Low[i], period2Time[i])
    # 高周期笔处理
    period2BiProcess = BiProcess()
    period2BiProcess.handle(period2KlineProcess.klineList)
    period2BiResult = period2BiProcess.biResult(len2)
    # 高周期段处理
    period2DuanProcess = DuanProcess()
    period2DuanResult = period2DuanProcess.handle(period2BiResult, period2High, period2Low)

    divergence_down, divergence_up = divergence.calc(
        period1Time,
        period1High,
        period1Low,
        period1Open,
        period1Close,
        period1Macd,
        period1Diff,
        period1Dea,
        period1BiProcess.biList,
        period1BiResult,
        period1DuanResult
    )
    if is_debug:
        print('divergence_down', divergence_down)
        print('divergence_up', divergence_up)

    # 高周期是否顶背驰
    higher_divergence_down, higher_divergence_up = divergence.calc(
        period2Time,
        period2High,
        period2Low,
        period2Open,
        period2Close,
        period2Macd,
        period2Diff,
        period2Dea,
        period2BiProcess.biList,
        period2BiResult,
        period2DuanResult
    )

    for i in range(len(divergence_down)):
        if divergence_down[i] == 1:
            if pydash.find_index(higher_divergence_up[i-5:i+5], lambda x: x == 1) > -1:
                if is_debug: print('本级别底背，但是高级别顶背')
                continue
            # 要不破前低
            i1 = pydash.find_last_index(period1DuanResult, lambda x: x == -1)
            i2 = pydash.find_last_index(period1DuanResult[:i1], lambda x: x == -1)
            if period1Low[i] < period1Low[i2]:
                if is_debug: print('创新低了')
                continue
            # 信号成立
            xb = datetime.utcfromtimestamp(period1Time[i])
            xb_price = period1Low[i]
            # 高周期MACD在0轴上吗
            msg = {
                'code': symbol['code'],
                'signal': 'XB',
                'name': '线底背驰',
                'period': period1,
                'fire_time': xb.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S'),
                'price': xb_price
            }
            if period2Macd[-1] < 0:
                msg['category'] = '%s MACD零轴下' % period2
            else:
                msg['category'] = '%s MACD零轴上' % period2
            # 底背驰信号
            msg = json.dumps(msg, ensure_ascii=False, indent=4)
            saveLog(symbol = symbol, period = period1, raw_data = rawData, signal = True, remark = msg, fire_time=xb, price=xb_price, position='BuyLong', is_debug=is_debug)
    for i in range(len(divergence_up)):
        if divergence_up[i] == 1:
            if pydash.find_index(higher_divergence_down[i-5:i+5], lambda x: x == 1) > -1:
                if is_debug: print('本级顶背，但是高级别底背')
                continue
            # 信号成立
            # 要不创新高
            i1 = pydash.find_last_index(period1DuanResult, lambda x: x == 1)
            i2 = pydash.find_last_index(period1DuanResult[:i1], lambda x: x == 1)
            if period1High[i] > period1High[i2]:
                if is_debug: print('创新高了')
                continue
            xb = datetime.utcfromtimestamp(period1Time[i])
            xb_price = period1High[i]
            # 高级别MACD在0轴下吗
            msg = {
                'code': symbol['code'],
                'signal': 'XT',
                'name': '线顶背驰',
                'period': period1,
                'fire_time': xb.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S'),
                'price': xb_price
            }
            if period2Macd[-1] > 0:
                msg['category'] = '%s MACD零轴上' % period2
            else:
                msg['category'] = '%s MACD零轴下' % period2
            # 顶背驰信号
            msg = json.dumps(msg, ensure_ascii=False, indent=4)
            saveLog(symbol = symbol, period = period1, raw_data = rawData, signal = True, remark = msg, fire_time=xb, price=xb_price, position='SellShort', is_debug=is_debug)


def saveLog(symbol, period, raw_data, signal, remark, fire_time, price, position, is_debug):
    logger = logging.getLogger()
    last_fire = DBPyChanlun['strategy3_log'].find_one({
        'symbol': symbol['code'],
        'peroid': period,
        'fire_time': fire_time,
        'position': position
    })
    if is_debug:
        logger.debug(last_fire)
    if last_fire is not None:
        DBPyChanlun['strategy3_log'].find_one_and_update({
            'symbol': symbol['code'], 'period': period, 'fire_time': fire_time, 'position': position
        }, {
            '$set': {
                'remark': remark,
                'price': price,
                'date_created': datetime.utcnow()
            },
            '$inc': {'update_count': 1}
        }, upsert=True)
    else:
        date_created = datetime.utcnow()
        DBPyChanlun['strategy3_log'].insert_one({
            'symbol': symbol['code'],
            'period': period,
            'raw_data': raw_data,
            'signal': True,
            'remark': remark,
            'date_created': date_created,#记录插入的时间
            'fire_time': fire_time, #背驰发生的时间,
            'price': price,
            'position': position,
            'update_count': 1, # 这条背驰记录的更新次数
        })
        if (date_created - fire_time).total_seconds() < 600:
            # 在10分钟内的触发邮件通知
            mailResult = mail.send(remark)
            print(mailResult)


def doCaculate(symbol, inspect_time = None, is_debug = False):
    logger = logging.getLogger()
    pairs = [
        { 'current': '3m', 'higher': '15m' },
        { 'current': '5m', 'higher': '30m' },
        { 'current': '15m', 'higher': '1h' },
        { 'current': '30m', 'higher': '4h' },
        { 'current': '1h', 'higher': '1d' }
    ]
    for i in range(len(pairs)):
        try:
            doExecute(symbol, pairs[i]['current'], pairs[i]['higher'], inspect_time, is_debug)
        except BaseException as e:
            logger.info("Error Occurred: {0}".format(traceback.format_exc()))

