import logging
from datetime import datetime
import time
import pandas as pd
import talib as ta
import numpy as np
import rx
from rx.scheduler import ThreadPoolScheduler
from rx.scheduler.eventloop import AsyncIOScheduler
from rx import operators as ops
from mongoengine.context_managers import *

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
from ..model.Symbol import Symbol
from ..model.Bar import Bar
from ..model.Strategy3Log import Strategy3Log


mail = Mail()


def doExecute(symbol, period1, period2):
    logger = logging.getLogger()
    logger.info("策略3 %s %s %s" % (symbol.code, period1, period2))
    rawData = {}
    bars1 = None
    bars2 = None
    with switch_collection(Bar, '%s_%s' % (symbol.code.lower(), period1)) as Bar1:
        bars1 = Bar1.objects.order_by('-_id').limit(1000)
    with switch_collection(Bar, '%s_%s' % (symbol.code.lower(), period2)) as Bar2:
        bars2 = Bar2.objects.order_by('-_id').limit(1000)
    if len(bars1) < 13 or len(bars2) < 13: return
    period1Time = []
    period1High = []
    period1Low = []
    period1Open = []
    period1Close = []
    len1 = len(bars1)
    for i in range(len1 - 1, -1, -1):
        period1Time.append(int(time.mktime(bars1[i].id.timetuple())))
        period1High.append(bars1[i].high)
        period1Low.append(bars1[i].low)
        period1Open.append(bars1[i].open)
        period1Close.append(bars1[i].close)
    period2Time = []
    period2High = []
    period2Low = []
    period2Open = []
    period2Close = []
    len2 = len(bars2)
    for i in range(len2 - 1, -1, -1):
        period2Time.append(int(time.mktime(bars1[i].id.timetuple())))
        period2High.append(bars1[i].high)
        period2Low.append(bars1[i].low)
        period2Open.append(bars1[i].open)
        period2Close.append(bars1[i].close)
    # 计算MACD
    period1Diff, period1Dea, period1Macd = ta.MACD(np.array([float(x) for x in period1Close]), fastperiod=12, slowperiod=26, signalperiod=9)
    period1Diff = np.nan_to_num(period1Diff)
    period1Dea = np.nan_to_num(period1Dea)
    period1Macd = np.nan_to_num(period1Macd)
    period2Diff, period2Dea, period2Macd = ta.MACD(np.array([float(x) for x in period2Close]), fastperiod=12, slowperiod=26, signalperiod=9)
    period2Diff = np.nan_to_num(period1Diff)
    period2Dea = np.nan_to_num(period2Dea)
    period2Macd = np.nan_to_num(period2Macd)

    # 计算金叉
    period1GoldCross = CROSS(period1Diff, period1Dea)
    # 是否发生金叉
    isCross = pydash.find_index(period1GoldCross.series[-5:-1], lambda x: x == True) > -1
    if not isCross:
        return
    else:
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

        notLower = Duan.notLower(period1DuanResult, period1Low)
        if not notLower:
            return
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
            period1DuanResult
        )
        # 本周期是否有底背驰
        isDiver = pydash.find_index(divergence_down[-5:-1], lambda x: x == 1) > -1
        if not isDiver:
            return
        # 高周期是否顶背驰
        divergence_down, divergence_up = divergence.calc(
            period2Time,
            period2High,
            period2Low,
            period2Open,
            period2Close,
            period2Macd,
            period2Diff,
            period2Dea,
            period2BiProcess.biList,
            period2DuanResult
        )
        isDiver = pydash.find_index(divergence_up[-5:-1], lambda x: x == 1) > -1
        if isDiver:
            return
        # 高周期MACD在0轴上吗
        msg = { 'code': symbol.code, 'signal': 'XB', 'name': '线底背驰', 'period': period1 }
        if period2Macd[-1] < 0:
            msg['category'] = '%s MACD零轴下' % period2
        else:
            msg['category'] = '%s MACD零轴上' % period2
        # 底背驰信号
        msg = json.dumps(msg, ensure_ascii=False, indent=4)
        mailResult = mail.send(msg)
        mLog = Strategy3Log(symbol = symbol, period = period1, raw_data = rawData, signal = True, remark = msg)
        mLog.save()

    # 计算死叉
    period1DeadCross = CROSS(period1Dea, period1Diff)
    # 是否发生死叉
    isCross = pydash.find_index(period1DeadCross.series[-5:-1], lambda x: x == True) > -1
    if not isCross:
        return
    else:
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

        notLower = Duan.notLower(period1DuanResult, period1Low)
        if not notLower:
            return
        divergence_down, divergence_up = divergence.calc(period1Time, period1Macd, period1Diff, period1Dea, period1BiProcess.biList, period1DuanResult)
        # 本周期是否有顶背驰
        isDiver = pydash.find_index(divergence_up[-5:-1], lambda x: x == 1) > -1
        if not isDiver:
            return
        # 高周期是否底背驰
        divergence_down, divergence_up = divergence.calc(period2Time, period2Macd, period2Diff, period2Dea, period2BiProcess.biList, period2DuanResult)
        isDiver = pydash.find_index(divergence_down[-5:-1], lambda x: x == 1) > -1
        if isDiver:
            return
        # 高级别MACD在0轴下吗
        msg = { 'code': symbol.code, 'signal': 'XB', 'name': '线底背驰', 'period': period1 }
        if period2Macd[-1] > 0:
            msg['category'] = '%s MACD零轴上' % period2
        else:
            msg['category'] = '%s MACD零轴下' % period2
        # 底背驰信号
        msg = json.dumps(msg, ensure_ascii=False, indent=4)
        mailResult = mail.send(msg)
        saveLog(symbol = symbol, period = period1, raw_data = rawData, signal = True, remark = msg)


def saveLog(symbol, period, raw_data, signal, remark):
    mLog = Strategy3Log(symbol = symbol, period = period, raw_data = raw_data, signal = True, remark = remark)
    mLog.save()


def doCaculate(symbol):
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
            doExecute(symbol, pairs[i]['current'], pairs[i]['higher'])
        except BaseException as e:
            logger.info("Error Occurred: {0}".format(traceback.format_exc()))


def doMonitor():
    """
    策略3 监控
    """
    logger = logging.getLogger()
    logger.info("策略3 监控")

    rx.from_(Symbol.objects()).subscribe(
        on_next = lambda symbol: doCaculate(symbol),
        on_error = lambda e: logger.info("Error Occurred: {0}".format(e)),
        on_completed = lambda: logger.info("Done!"),
    )
