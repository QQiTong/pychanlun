import logging
from datetime import datetime
import time
import pandas as pd
import talib as ta
import numpy as np
from ..funcat.data.BitmexDataBackend import BitmexDataBackend
from ..funcat.utils import get_int_date
from ..KlineProcess import KlineProcess
from ..BiProcess import BiProcess
from ..DuanProcess import DuanProcess
from .. import entanglement as entanglement
from .. import divergence as divergence
from ..Mail import Mail
from .. import Duan

mail = Mail()

def doMonitor1():
    """
    策略3 XBTUSD 3m 15m 监控
    """
    logger = logging.getLogger()
    logger.info("策略3 XBTUSD 3m 15m 监控 %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    dtime = datetime.now()
    endTime = int(time.mktime(dtime.timetuple()))
    startTime = endTime - 24 * 60 * 60 * 5
    dataBackend = BitmexDataBackend()
    prices = dataBackend.get_price('XBTUSD', startTime, endTime, '1')

    df1m = pd.DataFrame.from_records(prices)
    df1m['time'] = pd.to_datetime(df1m.time.values, unit='s', utc=True).tz_convert('Asia/Shanghai')
    df1m.set_index("time", inplace=True)
    ohlc_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }
    # 聚合3m数据
    df3m = df1m.resample('3T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    df3m.reset_index('time', inplace=True)
    # 聚合15m数据
    df15m = df1m.resample('15T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    df15m.reset_index('time', inplace=True)

    #3m笔和段
    high3m = df3m.high.values
    low3m = df3m.low.values
    close3m = df3m.close.values
    time3m = df3m.time.values
    count3m = len(time3m)
    klineProcess3m = KlineProcess()
    for i in range(count3m):
        klineProcess3m.add(high3m[i], low3m[i], time3m[i])

    biProcess3m = BiProcess()
    biProcess3m.handle(klineProcess3m.klineList)
    biResult3m = biProcess3m.biResult(count3m)

    duanProcess3m = DuanProcess()
    duanResult3m = duanProcess3m.handle(biResult3m, high3m, low3m)

    diff3m, dea3m, macd3m = ta.MACD(np.array([float(x) for x in close3m]), fastperiod=12, slowperiod=26, signalperiod=9)
    diff3m = np.nan_to_num(diff3m)
    dea3m = np.nan_to_num(dea3m)
    macd3m = np.nan_to_num(macd3m)

    #15m笔和段
    high15m = df15m.high.values
    low15m = df15m.low.values
    close15m = df15m.close.values
    time15m = df15m.time.values
    count15m = len(time15m)
    klineProcess15m = KlineProcess()
    for i in range(count15m):
        klineProcess15m.add(high15m[i], low15m[i], time15m[i])

    biProcess15m = BiProcess()
    biProcess15m.handle(klineProcess15m.klineList)
    biResult15m = biProcess15m.biResult(count15m)

    duanProcess15m = DuanProcess()
    duanResult15m = duanProcess15m.handle(biResult15m, high15m, low15m)
    diff15m, dea15m, macd15m = ta.MACD(np.array([float(x) for x in close15m]), fastperiod=12, slowperiod=26, signalperiod=9)
    diff15m = np.nan_to_num(diff15m)
    dea15m = np.nan_to_num(dea15m)
    macd15m = np.nan_to_num(macd15m)

    # 计算中枢
    entanglementList3m = entanglement.calcEntanglements(time3m, duanResult3m, biResult3m, high3m, low3m)
    entanglementList15m = entanglement.calcEntanglements(time15m, duanResult15m, biResult15m, high15m, low15m)

    # 计算背驰3m
    diver = divergence.calc(time3m, macd3m, diff3m, dea3m, biProcess3m.biList, duanResult3m)
    if diver['buyMACDBCData']['date'] is not None and len(diver['buyMACDBCData']['date']) > 0:
        last = diver['buyMACDBCData']['date'][-1]
        lastTs = (last - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        nowTs = dtime.timestamp()
        if nowTs-lastTs < 600:
            # 顶背驰了
            # 看大级别有没有破位
            if Duan.notHigher(duanResult3m, high3m):
                macdPos = ""
                if macd15m[-1] >= 0:
                    macdPos = "大级别MACD零轴上"
                else:
                    macdPos = "大级别MACD零轴下"
                msg = '顶背驰', 'XBTUSD', '3m', macdPos
                logger.info(msg)
                mailResult = mail.send(str(msg))
                if not mailResult:
                    logger.info("发送失败")
    if diver['sellMACDBCData']['date'] is not None and len(diver['sellMACDBCData']['date']):
        last = diver['sellMACDBCData']['date'][-1]
        lastTs = (last - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        nowTs = dtime.timestamp()
        if nowTs-lastTs < 600:
            # 底背驰
            # 看大级别有没有破位
            if Duan.notLower(duanResult3m, low3m):
                macdPos = ""
                if macd15m[-1] >= 0:
                    macdPos = "大级别MACD零轴上"
                else:
                    macdPos = "大级别MACD零轴下"
                msg = '底背驰', 'XBTUSD', '3m', macdPos
                logger.info(msg)
                mailResult = mail.send(str(msg))
                if not mailResult:
                    logger.info("发送失败")


def doMonitor2():
    """
    策略3 XBTUSD 15m 60m 监控
    """
    logger = logging.getLogger()
    logger.info("策略3 XBTUSD 15m 60m 监控 %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    dtime = datetime.now()
    endTime = int(time.mktime(dtime.timetuple()))
    startTime = endTime - 24 * 60 * 60 * 5
    dataBackend = BitmexDataBackend()
    prices = dataBackend.get_price('XBTUSD', startTime, endTime, '5')

    df5m = pd.DataFrame.from_records(prices)
    df5m['time'] = pd.to_datetime(df5m.time.values, unit='s', utc=True).tz_convert('Asia/Shanghai')
    df5m.set_index("time", inplace=True)
    ohlc_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }
    # 聚合15m数据
    df15m = df5m.resample('15T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    df15m.reset_index('time', inplace=True)
    # 聚合60m数据
    df60m = df5m.resample('60T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    df60m.reset_index('time', inplace=True)

    #15m笔和段
    high15m = df15m.high.values
    low15m = df15m.low.values
    close15m = df15m.close.values
    time15m = df15m.time.values
    count15m = len(time15m)
    klineProcess15m = KlineProcess()
    for i in range(count15m):
        klineProcess15m.add(high15m[i], low15m[i], time15m[i])

    biProcess15m = BiProcess()
    biProcess15m.handle(klineProcess15m.klineList)
    biResult15m = biProcess15m.biResult(count15m)

    duanProcess15m = DuanProcess()
    duanResult15m = duanProcess15m.handle(biResult15m, high15m, low15m)

    diff15m, dea15m, macd15m = ta.MACD(np.array([float(x) for x in close15m]), fastperiod=12, slowperiod=26, signalperiod=9)
    diff15m = np.nan_to_num(diff15m)
    dea15m = np.nan_to_num(dea15m)
    macd15m = np.nan_to_num(macd15m)

    #60m笔和段
    high60m = df60m.high.values
    low60m = df60m.low.values
    close60m = df60m.close.values
    time60m = df60m.time.values
    count60m = len(time60m)
    klineProcess60m = KlineProcess()
    for i in range(count60m):
        klineProcess60m.add(high60m[i], low60m[i], time60m[i])

    biProcess60m = BiProcess()
    biProcess60m.handle(klineProcess60m.klineList)
    biResult60m = biProcess60m.biResult(count60m)

    duanProcess60m = DuanProcess()
    duanResult60m = duanProcess15m.handle(biResult60m, high60m, low60m)

    diff60m, dea60m, macd60m = ta.MACD(np.array([float(x) for x in close60m]), fastperiod=12, slowperiod=26, signalperiod=9)
    diff60m = np.nan_to_num(diff60m)
    dea60m = np.nan_to_num(dea60m)
    macd60m = np.nan_to_num(macd60m)

    # 计算中枢
    entanglementList16m = entanglement.calcEntanglements(time15m, duanResult15m, biResult15m, high15m, low15m)
    entanglementList60m = entanglement.calcEntanglements(time60m, duanResult60m, biResult60m, high60m, low60m)

    # 计算背驰3m
    diver = divergence.calc(time15m, macd15m, diff15m, dea15m, biProcess15m.biList, duanResult15m)
    if diver['buyMACDBCData']['date'] is not None and len(diver['buyMACDBCData']['date']) > 0:
        last = diver['buyMACDBCData']['date'][-1]
        lastTs = (last - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        nowTs = dtime.timestamp()
        if nowTs-lastTs < 600:
            # 顶背驰了
            # 看大级别有没有破位
            if Duan.notHigher(duanResult15m, high15m):
                macdPos = ""
                if macd60m[-1] >= 0:
                    macdPos = "大级别MACD零轴上"
                else:
                    macdPos = "大级别MACD零轴下"
                msg = '顶背驰', 'XBTUSD', '15m', macdPos
                logger.info(msg)
                mailResult = mail.send(str(msg))
                if not mailResult:
                    logger.info("发送失败")
    if diver['sellMACDBCData']['date'] is not None and len(diver['sellMACDBCData']['date']):
        last = diver['sellMACDBCData']['date'][-1]
        lastTs = (last - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        nowTs = dtime.timestamp()
        if nowTs-lastTs < 600:
            # 底背驰
            # 看大级别有没有破位
            if Duan.notLower(duanResult15m, low15m):
                macdPos = ""
                if macd60m[-1] >= 0:
                    macdPos = "大级别MACD零轴上"
                else:
                    macdPos = "大级别MACD零轴下"
                msg = '底背驰', 'XBTUSD', '3m', macdPos
                logger.info(msg)
                mailResult = mail.send(str(msg))
                if not mailResult:
                    logger.info("发送失败")
