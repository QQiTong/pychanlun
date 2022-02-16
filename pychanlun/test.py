# -*- coding: utf-8 -*-
import math
import requests
import json
import time
import pydash
from datetime import datetime, timedelta

from bson import CodecOptions
from pymongo import UpdateOne

from pychanlun.Calc import Calc

from pychanlun.Mail import Mail
# from pychanlun.funcat.api import *
from pychanlun.monitor import BeichiMonitor
import sys
from rqdatac import *
import os
import pymongo

from pychanlun.config import config
import rqdatac as rq
import requests
from pychanlun.db import DBPyChanlun
# from tqsdk import TqApi
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
# from tqsdk import tafunc
import re
import pytz
import string
import hashlib
from futu import *
# from WindPy import w
import talib as ta
import copy
from pychanlun.db import DBQuantAxis

tz = pytz.timezone('Asia/Shanghai')

periodList = ['3min', '5min', '15min', '30min', '60min', '4hour', '1day']


def getDominantSymbolWithInfo():
    # symbolList = config['symbolList']
    # dominantSymbolInfoList = []
    #
    # dominantSymbolList = []
    # for i in range(len(symbolList)):
    #     df = rq.futures.get_dominant(symbolList[i], start_date=None, end_date=None, rule=0)
    #     dominantSymbol = df[-1]
    #     dominantSymbolList.append(dominantSymbol)
    #     dominantSymbolInfo = rq.instruments(dominantSymbol)
    #     dominantSymbolInfoList.append(dominantSymbolInfo.__dict__)
    #     print("当前主力合约:", dominantSymbolInfoList)
    # return dominantSymbolList
    # 需要监控的合约
    symbolList = config['symbolList']
    # 主力合约列表
    dominantSymbolList = []
    # 主力合约详细信息
    dominantSymbolInfoList = {}
    for i in range(len(symbolList)):
        df = rq.futures.get_dominant(symbolList[i], start_date=None, end_date=None, rule=0)
        dominantSymbol = df[-1]
        dominantSymbolList.append(dominantSymbol)
        dominantSymbolInfo = rq.instruments(dominantSymbol)
        dominantSymbolInfoList[dominantSymbol] = dominantSymbolInfo.__dict__

    print("当前主力合约:", dominantSymbolInfoList)
    print("当前主力合约2:", dominantSymbolList)


def getDominantSymbol():
    symbolList = config['symbolList']
    dominantSymbolList = []
    for i in range(len(symbolList)):
        df = rq.futures.get_dominant(symbolList[i], start_date=None, end_date=None, rule=0)
        dominantSymbol = df[-1]
        dominantSymbolList.append(dominantSymbol)
    return dominantSymbolList


def testDb():
    # init('license',
    #      'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
    #      ('rqdatad-pro.ricequant.com', 16011))

    # test = DBPyChanlun['strategy3_log']\
    #     .find_one_and_update({'symbol':'TA2001', 'period':'30m'},
    #                         {'$set': {'beichi_time': 33},'$inc':{'update_count':1}},
    #                            upsert=False)

    test = DBPyChanlun['strategy3_log'] \
        .find({'symbol': 'TA2001', 'period': '30m'})
    print(list(test))

    return False


def testChange():
    # init('license',
    #      'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
    #      ('rqdatad-pro.ricequant.com', 16011))
    startTime = time.process_time()
    symbolChangeMap = {}
    dominantSymbolList = ['RB2005', 'HC2005', 'RU2005', 'NI2004', 'FU2005', 'ZN2003', 'SP2005', 'BU2006', 'AU2006',
                          'AG2006', 'MA2005', 'TA2005', 'SR2005', 'OI2005', 'AP2005', 'CF2005', 'M2005', 'I2005',
                          'EG2005', 'J2005', 'JM2005', 'PP2005', 'P2005', 'RM2005', 'Y2005']
    weekday = datetime.now().weekday()

    end = datetime.now() + timedelta(1)
    # 周日weekday 6 取前2天 周一 weekday 0 取前3天 需要取
    if weekday == 0:
        start = datetime.now() + timedelta(-3)
    elif weekday == 6:
        start = datetime.now() + timedelta(-2)
    else:
        start = datetime.now() + timedelta(-1)
    for i in range(len(dominantSymbolList)):
        item = dominantSymbolList[i]
        # print(item)
        if item != 'BTC' and item != 'ETH_CQ':
            df1d = rq.get_price(item, frequency='1d', fields=['open', 'high', 'low', 'close', 'volume'],
                                start_date=start, end_date=end)
            df1m = rq.current_minute(item)
            preday = df1d.iloc[0, 3]
            today = df1m.iloc[0, 0]
            print(df1d)
            if df1d is None or df1m is None:
                change = "--"
            else:
                print(today)
                change = round((today - preday) / preday, 4)
            resultItem = {'change': change, 'price': today}
            symbolChangeMap[item] = resultItem
    print(symbolChangeMap)
    elapsed = (time.process_time() - startTime)  # 结束计时
    print("程序执行的时间:" + str(elapsed) + "s")  # 印出时间
    return False


def testProxy():
    proxies = {'http': '127.0.0.1:10809', 'https': '127.0.0.1:10809'}
    # url = 'http://www.baidu.com'
    # requests.post(url, proxies=proxies, verify=False)  # verify是否验证服务器的SSL证书
    return False


def testHuobi():
    startTime = int(round(time.time() * 1000))

    PROXIES = {
        "http": "socks5://127.0.0.1:10808",
        "https": "socks5://127.0.0.1:10808"
    }
    hbdmUrl = "http://api.hbdm.com/market/history/kline"
    payload1 = {
        'symbol': 'BTC_CQ',  # 合约类型， 火币季度合约
        'period': '1min',
        'size': 2000
    }
    r = requests.get(hbdmUrl, params=payload1, proxies=PROXIES)
    endTime = int(round(time.time() * 1000)) - startTime
    print("耗费时间：", endTime)
    print(json.loads(r.text)['data'])


def testPydash():
    a = [1, 2, 1, 5]
    b = pydash.find_index(a, lambda x: x == 1)
    print(b)


def testTime():
    import pytz
    tz = pytz.timezone('Asia/Shanghai')
    str = '2020-03-19T09:10:00.000Z'
    result = datetime.strptime(str, "%Y-%m-%dT%H:%M:%S.%fZ")

    print(result, result)

    stamp = 1568091600
    test = datetime.fromtimestamp(stamp)
    print(test)


def testTime2():
    # str = '2019-12-30 09:00'
    # date = time.strptime(str,"%Y-%m-%d %H:%M")
    # print(time.mktime(date))
    timeStr = datetime.strftime(datetime.now(), '%Y-%m-%d')
    print(timeStr)


def getBtcData(period):
    url = "https://www.bitmex.com/api/udf/history"
    dtime = datetime.now()
    toDate = int(time.mktime(dtime.timetuple()))
    target = 0
    fromDate = 0
    # 最大是10080 ,但是数量大了前端会卡顿
    if period == "1m":
        period = '1'
        fromDate = toDate - 24 * 60 * 60
    elif period == "3m":
        period = '1'
        target = 3
        fromDate = toDate - 24 * 60 * 60 * 4
    elif period == "5m":
        period = '5'
        fromDate = toDate - 1000 * 5 * 60
    elif period == "15m":
        period = '1'
        target = 15
        fromDate = toDate - 2000 * 5 * 60

    elif period == "30m":
        period = '1'
        target = 30
        fromDate = toDate - 2000 * 5 * 60
    elif period == "60m":
        period = '60'
        fromDate = toDate - 10 * 1000 * 5 * 60
    elif period == "240m":
        period = '1'
        target = 240
        fromDate = toDate - 1000 * 5 * 60
    elif period == '1d':
        period = 'D'
        fromDate = toDate - 1000 * 60 * 60 * 24
    elif period == '7d':
        period = 'D'
        target = 7
        fromDate = toDate - 1000 * 5 * 60 * 24

    payload = {
        'resolution': period,
        'symbol': 'XBTUSD',  # 合约类型，如永续合约:XBTUSD
        'from': fromDate,
        'to': toDate
    }
    header = {"accept": "*/*", "accept-encoding": "gzip, deflate, br",
              "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
              "origin": "https://static.bitmex.com",
              "referer": "https://static.bitmex.com/",
              }
    startTime = datetime.now()
    proxies = {'http': '127.0.0.1:10809', 'https': '127.0.0.1:10809'}
    r = requests.get(url, params=payload, headers=header, proxies=proxies)
    endTime = datetime.now() - startTime
    klines = json.loads(r.text)
    print(target, len(klines))


def getBtcData2():
    url = "https://www.bitmex.com/api/v1/trade/bucketed"
    proxies = {'http': '127.0.0.1:10809', 'https': '127.0.0.1:10809'}
    payload = {
        "binSize": "1m",
        "symbol": "XBTUSD",
        "count": 750,
        "startTime": "2019-09-01 21:13"
    }
    r = requests.get(url, params=payload, proxies=proxies)
    print(r)


def testBitmex():
    for i in range(100):
        getBtcData2()
        # getBtcData2()
        # getBtcData2()
        # getBtcData('1m')
        # getBtcData('3m')
        # getBtcData('5m')
        # getBtcData('15m')
        # getBtcData('30m')
    # getBtcData('60m')
    # getBtcData('240m')
    # getBtcData('1d')
    # getBtcData('7d')


def saveBeichiLog(symbol, period, price, signal, remark):
    DBPyChanlun['beichi_log'].insert_one({
        'date_created': datetime.now().strftime("%m-%d %H:%M"),
        'symbol': symbol,
        'period': period,
        'price': round(price, 2),
        'signal': signal,
        'remark': remark
    })


def testBeichiDb():
    saveBeichiLog(symbol="BTC_CQ", period="15m", price=8166, signal=True, remark="break B")
    saveBeichiLog(symbol="BTC_CQ", period="30m", price=8166, signal=True, remark="Vfan B")


def testHuila():
    init('license',
         'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
         ('rqdatad-pro.ricequant.com', 16011))
    calc = Calc()
    result = calc.calcData("3m", "RB2001")
    print("结果：", result)


def testTQ():
    api = TqApi()
    df = api.get_kline_serial("SHFE.rb2005", 60 * 240)
    nparray = np.array(df)
    npKlineList = nparray.tolist()
    # npIndexList = pd.to_numeric(df.index) // 1000000000
    klineList = []

    for i in range(len(npKlineList)):
        # timeStamp = int(time.mktime(npKlineList[i][0].timetuple()))
        # timeStamp = int(time.mktime(df.index[i].timetuple()))
        timeStamp = str(tafunc.time_to_datetime(npKlineList[i][0]))
        item = {}
        item['time'] = timeStamp
        item['open'] = 0 if pd.isna(npKlineList[i][2]) else npKlineList[i][2]
        item['high'] = 0 if pd.isna(npKlineList[i][3]) else npKlineList[i][3]
        item['low'] = 0 if pd.isna(npKlineList[i][4]) else npKlineList[i][4]
        item['close'] = 0 if pd.isna(npKlineList[i][5]) else npKlineList[i][5]
        item['volume'] = 0 if pd.isna(npKlineList[i][6]) else npKlineList[i][6]
        print(item)
        klineList.append(item)
    # print(klineList)
    api.wait_update()


def testRQ():
    # start = time.process_time()
    # df = rq.current_minute('RB2005',fields=['open', 'high', 'low', 'close', 'volume'])
    # print(df)
    # print(df.iloc[0, 0])
    # print(df.iloc[0, 1])
    # print(df.iloc[0, 2])
    # print(df.iloc[0, 3])
    end = datetime.now() + timedelta(1)
    start = datetime.now() + timedelta(-1)
    df = rq.get_price('L2009', frequency='30m', fields=['open', 'high', 'low', 'close', 'volume'],
                      start_date='2020-06-24', end_date='2020-06-30')
    print(df)
    # print(df1d.iloc[0,0])
    # print(df1d.iloc[0,1])
    # print(df1d.iloc[0,2])
    # print(df1d.iloc[0,3])
    # elapsed = (time.process_time() - start)  # 结束计时
    # print("程序执行的时间:" + str(elapsed) + "s")  # 印出时间
    return False


def testMonitor():
    # 15F,60F  [3585,3537]
    #  26  7
    start = time.clock()
    BeichiMonitor.calStopWinCount("BU2006", '3m', 3200)
    elapsed = (time.clock() - start)  # 结束计时
    print("程序执行的时间:" + str(elapsed) + "s")  # 印出时间


def testThread():
    symbolList = getDominantSymbol()
    n = 12
    c = [symbolList[i:i + n] for i in range(0, len(symbolList), n)]
    print("--", c)


def testWaipan():
    timeStamp = time.time()
    url = "https://gu.sina.cn/ft/api/jsonp.php//GlobalService.getMink"
    payload = {
        "symbol": "CL",
        "type": 60
    }
    content = requests.get(url, params=payload).content
    p1 = re.compile(r'[(](.*?)[)]', re.S)  # 最小匹配
    result = re.findall(p1, content.decode('utf-8'))[0]
    klines = json.loads(result)

    originKlineList = []

    for i in range(len(klines)):
        newKline = {}
        originKline = {}
        originKline['open'] = klines[i]['o']
        originKline['high'] = klines[i]['h']
        originKline['low'] = klines[i]['l']
        originKline['close'] = klines[i]['c']
        originKline['time'] = klines[i]['d']

        timeArray = time.strptime(klines[0]['d'], "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
        originKlineList.append(originKline)
    print(timeStamp)
    print(klines[0]['d'])


def testWechat():
    # symbol, period, signal, direction, amount, stop_lose_price, fire_time_str, price, date_created_str,
    # close_price, remark
    symbol = 'RB2005'
    period = '3m'
    signal = 'huila'
    direction = 'B'
    amount = 3
    stop_lose_price = 3376
    fire_time_str = '202003090919'
    price = 3387
    date_created_str = '202003090919'
    close_price = 3387
    remark = '双盘'
    url = "http://www.yutiansut.com/signal?user_id=oL-C4w2KYo5DB486YBwAK2M69uo4&template=xiadan_report&strategy_id=%s" \
          "&realaccount=%s&code=%s&order_direction=%s&order_offset=%s&price=%s&volume=%s&order_time=%s" \
          % (signal, remark, symbol + '_' + period, signal, direction,
             '开:' + str(close_price) + ' 止:' + str(stop_lose_price) + ' 触:' + str(price), amount,
             '开:' + fire_time_str + ' 触:' + date_created_str)
    requests.post(url)


#
def testOkex1():
    startTime = int(round(time.time() * 1000))

    PROXIES = {
        "http": "socks5://127.0.0.1:10808",
        "https": "socks5://127.0.0.1:10808"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
        "Accept": "application/json",
        "App-Type": "web",
        "Referer": "https://www.okex.me/derivatives/swap/full/usdt-btc"}

    t = time.time()
    timeStamp = int(round(t * 1000))
    # 接口1
    okexUrl = "https://www.okex.me/v2/perpetual/pc/public/instruments/BTC-USDT-SWAP/candles"
    payload = {
        'granularity': 300,
        'size': 1000,
        't': timeStamp
    }

    r = requests.get(okexUrl, params=payload, headers=headers)
    endTime = int(round(time.time() * 1000)) - startTime
    print("耗费时间：", endTime)
    klines = json.loads(r.text)['data']
    # print(klines)
    originKlineList = []
    for i in range(len(klines)):
        originKline = {}
        date = datetime.strptime(klines[i][0], "%Y-%m-%dT%H:%M:%S.%fZ")
        originKline['open'] = klines[i][1]
        originKline['high'] = klines[i][2]
        originKline['low'] = klines[i][3]
        originKline['close'] = klines[i][4]
        originKline['volume'] = klines[i][5]
        # dateArray = datetime.utcfromtimestamp(klines[i]['id'] + 8 * 3600)
        otherStyleTime = date.strftime("%Y-%m-%d %H:%M:%S")
        originKline['time'] = otherStyleTime
        originKlineList.append(originKline)
    print("结果:", len(originKlineList))


def testOkex2():
    startTime = int(round(time.time() * 1000))

    # PROXIES = {
    #     "http": "socks5://127.0.0.1:10808",
    #     "https": "socks5://127.0.0.1:10808"
    # }
    t = time.time()
    timeStamp = int(round(t * 1000))

    # 接口2
    # okexUrl = "https://www.okex.com/api/swap/v3/instruments/BTC-USDT-SWAP/candles"
    okexUrl = "https://www.okex.me/api/swap/v3/instruments/BTC-USDT-SWAP/candles"
    payload = {
        'granularity': 300,
        # 'start':'2020-03-22T02:31:00.000Z',
        # 'end':'2020-03-22T18:55:00.000Z',
    }

    r = requests.get(okexUrl, params=payload)
    endTime = int(round(time.time() * 1000)) - startTime
    print("耗费时间：", endTime)
    klines = json.loads(r.text)
    print(klines)
    originKlineList = []
    for i in range(len(klines)):
        originKline = {}
        date = datetime.strptime(klines[i][0], "%Y-%m-%dT%H:%M:%S.%fZ")
        originKline['open'] = klines[i][1]
        originKline['high'] = klines[i][2]
        originKline['low'] = klines[i][3]
        originKline['close'] = klines[i][4]
        originKline['volume'] = klines[i][5]
        # dateArray = datetime.utcfromtimestamp(klines[i]['id'] + 8 * 3600)
        otherStyleTime = date.strftime("%Y-%m-%d %H:%M:%S")
        originKline['time'] = otherStyleTime
        originKlineList.append(originKline)
    print("结果:", len(originKlineList))


def testOkexTiker():
    startTime = int(round(time.time() * 1000))

    PROXIES = {
        "http": "socks5://127.0.0.1:10808",
        "https": "socks5://127.0.0.1:10808"
    }
    okexUrl = "https://www.okex.com/api/swap/v3/instruments/BTC-USD-SWAP/ticker"
    r = requests.get(okexUrl, proxies=PROXIES)
    endTime = int(round(time.time() * 1000)) - startTime
    print("耗费时间：", endTime)
    tiker = json.loads(r.text)
    print(tiker)


def testChaji():
    a = ['RB2005', 'HC2005']
    b = ['RB2005', 'HC2010', 'RU2005']
    ret = []
    for i in a:
        if i not in b:
            ret.append(i)
    print(ret)


def testGlobalChangeList():
    globalFutureSymbol = ["CL", "GC", "SI", "CT", "S", "SM", "BO", "NID", "ZSD"]
    #
    changeList = {'RB2005': {'price': 11, 'change': 0.23}}
    globalChangeList = {}
    for i in range(len(globalFutureSymbol)):
        item = globalFutureSymbol[i]
        # 查日线开盘价
        code = "%s_%s" % (item, '1d')
        data_list = DBPyChanlun[code].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find(
        ).sort("_id", pymongo.DESCENDING)
        dayOpenPrice = data_list[0]['open']
        code = "%s_%s" % (item, '5m')

        # 差5分钟收盘价
        data_list = DBPyChanlun[code].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find(
        ).sort("_id", pymongo.DESCENDING)
        minClosePrice = data_list[0]['open']

        change = round((minClosePrice - dayOpenPrice) / dayOpenPrice, 4)
        changeItem = {
            'change': change,
            'price': minClosePrice
        }
        print(item, '-> ', dayOpenPrice, ' -> ', minClosePrice)
        globalChangeList[item] = changeItem

        conbineChangeList = dict(changeList, **globalChangeList)

    print("外盘涨跌幅列表", conbineChangeList)


def testDingDing():
    import requests
    import json
    url = 'https://oapi.dingtalk.com/robot/send?access_token=39474549996bad7e584523a02236d69b68be8963e2937274e4e0c57fbb629477'
    msg = {
        "symbol": 'test',
        "period": 'test',
        "signal": 'test',
        "direction": 'test',
        "amount": 'test',
        "fire_time": 'test',
        "price": 'test',
        "date_created": 'test',
        "close_price": 'test',
        "remark": 'test',
        "remind": 'Ding'
    }
    program = {
        "msgtype": "text",
        "text": {"content": json.dumps(msg, ensure_ascii=False, indent=4)},
    }
    headers = {'Content-Type': 'application/json'}
    f = requests.post(url, data=json.dumps(program), headers=headers)
    print(f)


def testMail():
    mail = Mail()
    msg = {
        "symbol": 'test',
        "period": 'test',
        "signal": 'test',
        "direction": 'test',
        "amount": 'test',
        "fire_time": 'test',
        "price": 'test',
        "date_created": 'test',
        "close_price": 'test',
        "remark": 'test',
        "remind": 'Ding'
    }
    mailResult = mail.send(json.dumps(msg, ensure_ascii=False, indent=4))
    if not mailResult:
        print("发送失败")


def testGroupBy():
    startDate = '2020-03-29'
    endDate = '2020-04-02'
    end = datetime.strptime(endDate, "%Y-%m-%d")
    end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    start = datetime.strptime(startDate, "%Y-%m-%d")
    start = start.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    data_list = DBPyChanlun['future_auto_position'].with_options(
        codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
        "date_created": {"$gte": start, "$lte": end}
    }).sort("_id", pymongo.ASCENDING)
    df = pd.DataFrame(list(data_list))

    for idx, row in df.iterrows():
        # 根据日期分组
        date_created = df.loc[idx, 'date_created']
        date_created_str = formatTime(date_created)
        df.loc[idx, 'new_date_created'] = date_created_str
        # 根据symbol分组 查询盈利品种排行和亏损品种排行
        symbol = df.loc[idx, 'symbol']
        # RB2010 -> RB
        simple_symbol = symbol.rstrip(string.digits)
        df.loc[idx, 'simple_symbol'] = simple_symbol

    win_end_group_by_date = df['win_end_money'].groupby(df['new_date_created'])
    lose_end_group_by_date = df['lose_end_money'].groupby(df['new_date_created'])
    win_end_group_by_symbol = df['win_end_money'].groupby(df['simple_symbol'])
    lose_end_group_by_symbol = df['lose_end_money'].groupby(df['simple_symbol'])
    # print(win_end_group_by_symbol.sum())
    # print(lose_end_group_by_symbol.sum())

    # print(win_end_group_by_date.sum())
    # print(lose_end_group_by_date.sum())
    # 日期列表
    dateList = []
    # 当日盈利累加
    win_end_list = []
    # 每天亏损累加
    lose_end_list = []
    # 净盈亏
    net_profit_list = []
    # 保存日期
    for name, group in win_end_group_by_date:
        dateList.append(name)
    # 保存品种简称

    for i in range(len(win_end_group_by_date.sum())):
        win_end_list.append(int(win_end_group_by_date.sum()[i]))
        lose_end_list.append(int(lose_end_group_by_date.sum()[i]))
        net_profit_list.append(int(win_end_group_by_date.sum()[i]) + int(lose_end_group_by_date.sum()[i]))

    sorted_win_money_list = win_end_group_by_symbol.mean().sort_values(ascending=False)
    sorted_lose_money_list = lose_end_group_by_symbol.mean().sort_values(ascending=True)

    win_symbol_list = list(sorted_win_money_list.index)
    lose_symbol_list = list(sorted_lose_money_list.index)

    # 取整数
    win_money_list = list(sorted_win_money_list.dropna(axis=0))
    lose_money_list = list(sorted_lose_money_list.dropna(axis=0))
    for i in range(len(win_money_list)):
        win_money_list[i] = int(win_money_list[i])
    for i in range(len(lose_money_list)):
        lose_money_list[i] = int(lose_money_list[i])

    print(win_symbol_list, win_money_list)
    print(lose_symbol_list, lose_money_list)


def formatTime(localTime):
    date_created_stamp = int(time.mktime(localTime.timetuple()))
    timeArray = time.localtime(date_created_stamp)
    return time.strftime("%Y-%m-%d", timeArray)


'''
 外盘期货 代码         入库别名简称           11个品种  这个 24小时采集  20秒采集1次   24*60*3 = 4320 次
 原油：@CL0W           --CL
 黄金：@GC0W           --GC
 白银：@SI0W           --SI
 道琼斯：@YM0Y         --YM
 A50: CN0Y             ---CN
 伦镍：03NID           --NI
 大豆：@ZS0W           ---S
 豆粕：@ZM0Y           --M
 豆油：@ZL0W           --L
 棕榈油：CPO0W         --P
 棉花：CT0W            --T

 美国股票    代码      8只股票  这个每天 晚上 21:00 到 凌晨 4:00 采集就可以了 . 20秒采集1次 一天采集 7*60 * 3 = 1260次
 苹果        AAPL
 微软        MSFT
 谷歌        GOOG
 Facebook    FB
 亚马逊      AMZN
 奈飞        NFLX
 英伟达      NVDA
 AMD        AMD

'''


# ldhqsj.com  备用地址 106.15.58.126  数据有遗漏 且不稳定，废弃
def testMeigu():
    pwd = hashlib.md5(b'chanlun123456').hexdigest()
    # 请求多个品种的美国股票
    stock = "http://ldhqsj.com/us_pluralK.action?username=chanlun&password=" + pwd + "&id=AAPL,MSFT,GOOG,FB,AMZN,NFLX,NVDA,AMD&jys=NA&period=1&num=-200"
    # 请求多个品种的外盘期权
    global_future = "http://ldhqsj.com/foreign_pluralK.action?username=chanlun&password=" + pwd + "&id=@CL0W,@GC0W,@SI0W,@YM0Y,CN0Y,03NID,@ZS0W,@ZM0Y,@ZL0W,CPO0W,CT0W&period=1&num=-200"
    print("调用地址", stock)
    print("调用地址", global_future)
    startTime = int(round(time.time() * 1000))
    stock_resp = requests.get(stock)
    global_future_resp = requests.get(global_future)
    endTime = int(round(time.time() * 1000)) - startTime
    print("消耗时间：", endTime)
    stock_result = stock_resp.text
    global_future_result = global_future_resp.text
    print("美股", stock_result)
    print("期货", global_future_result)


def testFutu():
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    ret, data, page_req_key = quote_ctx.request_history_kline('HK.00700', start='2017-06-20', end='2018-06-22',
                                                              max_count=50)  # 请求开头50个数据
    print(ret, data)
    ret, data, page_req_key = quote_ctx.request_history_kline('HK.00700', start='2017-06-20', end='2018-06-22',
                                                              max_count=50, page_req_key=page_req_key)  # 请求下50个数据
    print(ret, data)
    quote_ctx.close()


ohlc_dict = {'开盘价': 'first', '最高价': 'max', '最低价': 'min', '收盘价': 'last', '成交量': 'sum'}
# 8个品种 4个市场  'LENID3M' 伦镍暂时没接 ，要接又多了一个市场
futures = ['CEYMA0', 'CEESA0', 'CENQA0', 'WGCNA0', 'NECLA0', 'CMGCA0', 'CMSIA0']


def testWStock():
    startTime = int(round(time.time() * 1000))
    url = "http://db2015.wstock.cn/wsDB_API/kline.php?num=5000&symbol=NECLA0&desc=1&q_type=0&return_t=3&qt_type=1&r_type=2&u=u2368&p=abc1818"
    resp = requests.get(url)
    print("==>", resp.text)
    df = pd.DataFrame(json.loads(resp.text))
    df = df.sort_values(by="Date", ascending=True)
    endTime = int(round(time.time() * 1000)) - startTime
    print("消耗时间：", endTime)
    print(len(df))
    df['Date'] = df['Date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    df.set_index('Date', inplace=True)
    print(len(df[1:]))
    # save_data_m("LENID3M",'1m',df)


def save_data_m(code, period, df):
    if not df.empty:
        logging.info("保存 %s %s %s" % (code, period, df.index.values[-1]))
    batch = []
    for idx, row in df.iterrows():
        batch.append(UpdateOne({
            "_id": idx.replace(tzinfo=tz)
        }, {
            "$set": {
                "open": float(row['Open']),
                "close": float(row['Close']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "volume": float(row['Volume'])
            }
        }, upsert=True))
        if len(batch) >= 100:
            DBPyChanlun["%s_%s" % (code, period)].bulk_write(batch)
            batch = []
    if len(batch) > 0:
        DBPyChanlun["%s_%s" % (code, period)].bulk_write(batch)
        batch = []


def testMongoArr():
    symbol = 'GC'
    direction = 'long'
    status = 'holding'
    close_price = 1750
    date_created = datetime.utcnow()
    signal = 'fractal'
    period = '5m'
    stop_win_count = 1
    stop_win_price = 1748
    stop_win_money = 201
    DBPyChanlun['future_auto_position'].find_one_and_update({
        'symbol': symbol, 'direction': direction, 'status': status
    }, {
        '$set': {
            'close_price': close_price,  # 只需要更新最新价格，用于判断是否止损
            'last_update_time': date_created,  # 最后信号更新时间
            'last_update_signal': signal,  # 最后更新的信号
            'last_update_period': period,  # 最后更新的周期

            # 'amount':last_fire['amount'] - stop_win_count # 持仓的数量减去动止的数量
        },
        '$addToSet': {
            'dynamicPositionList': {
                'date_created': date_created,  # 动止时间
                'stop_win_count': stop_win_count,  # 动止的数量
                'stop_win_price': stop_win_price,  # 动止时的价格
                'stop_win_money': stop_win_money,  # 动止时的盈利
                'direction': direction
            }
        },
        '$inc': {
            'update_count': 1
        }
    }, upsert=True)


# wind 外盘不提供分钟线数据
def testWind():
    w.start()
    startTime = int(round(time.time() * 1000))
    # 取IF00.CFE的分钟数据
    codes = "IF00.CFE"
    fields = "open,high,low,close"
    error, wsd_data = w.wsd(codes, "open,high,low,close", "2015-12-10", "2015-12-22", "Fill=Previous", usedf=True)
    print(error, wsd_data)
    endTime = int(round(time.time() * 1000)) - startTime
    print("消耗时间：", endTime)


def calc_ma(close_list, day):
    ma = ta.MA(np.array(close_list), day)
    result = np.nan_to_num(ma).round(decimals=2)
    return result


def get_global_day_ma_list():
    global_future_symbol = config['global_future_symbol']
    combinSymbol = copy.deepcopy(global_future_symbol)
    aboveList = {}
    for i in range(len(combinSymbol)):
        item = combinSymbol[i]
        # 查日线开盘价
        code = "%s_%s" % (item, '1d')
        data_list = list(DBPyChanlun[code].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find(
        ).limit(31).sort("_id", pymongo.DESCENDING))
        if len(data_list) == 0:
            continue
        data_list.reverse()
        day_close_price_list = list(pd.DataFrame(data_list)['close'])
        day_ma_20 = calc_ma(day_close_price_list, 20)
        code = "%s_%s" % (item, '1m')

        # 查1分钟收盘价
        data_list = list(DBPyChanlun[code].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find(
        ).sort("_id", pymongo.DESCENDING))
        if len(data_list) == 0:
            continue
        min_close_price = list(pd.DataFrame(data_list)['close'])[0]
        above_item = {
            'above_ma_20': min_close_price >= day_ma_20[-1]
        }
        print(item, '-> ', above_item)
        aboveList[item] = above_item
    return aboveList


def testMA():
    symbol_ma_20_map = {}
    dominantSymbolList = getDominantSymbol()
    for i in range(len(dominantSymbolList)):
        item = dominantSymbolList[i]
        end = datetime.now() + timedelta(1)
        start = datetime.now() + timedelta(-31)
        df1d = rq.get_price(item, frequency='1d', fields=['open', 'high', 'low', 'close', 'volume'],
                            start_date=start, end_date=end)
        day_close = list(df1d['close'])
        df1m = rq.current_minute(item)
        current_price = df1m.iloc[0, 0]
        day_ma_20 = calc_ma(day_close, 20)[-1]
        result_item = {'above_ma_20': current_price >= day_ma_20}
        symbol_ma_20_map[item] = result_item
    global_day_ma_list = get_global_day_ma_list()
    conbine_day_ma_list = dict(symbol_ma_20_map, **global_day_ma_list)
    print(conbine_day_ma_list)
    return conbine_day_ma_list


def testSplit():
    a = [i for i in range(10)]
    b = [a[i:i + 5] for i in range(0, len(a), 5)]
    print(b)


def testStatistic():
    startDate = '2020-04-28'
    endDate = '2020-08-13'
    end = datetime.strptime(endDate, "%Y-%m-%d")
    end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    start = datetime.strptime(startDate, "%Y-%m-%d")
    start = start.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    df_beichi_win = pd.DataFrame(list(
        DBPyChanlun['future_auto_position'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
            "date_created": {"$gte": start, "$lte": end}, "status": "winEnd", "signal": "beichi"
        }).sort("_id", pymongo.ASCENDING)))

    df_beichi_lose = pd.DataFrame(list(
        DBPyChanlun['future_auto_position'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
            "date_created": {"$gte": start, "$lte": end}, "status": "loseEnd", "signal": "beichi"
        }).sort("_id", pymongo.ASCENDING)))

    df_break_win = pd.DataFrame(list(
        DBPyChanlun['future_auto_position'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
            "date_created": {"$gte": start, "$lte": end}, "status": "winEnd", "signal": "break"
        }).sort("_id", pymongo.ASCENDING)))
    df_break_lose = pd.DataFrame(list(
        DBPyChanlun['future_auto_position'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
            "date_created": {"$gte": start, "$lte": end}, "status": "loseEnd", "signal": "break"
        }).sort("_id", pymongo.ASCENDING)))

    df_huila_win = pd.DataFrame(list(
        DBPyChanlun['future_auto_position'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
            "date_created": {"$gte": start, "$lte": end}, "status": "winEnd", "signal": "huila"
        }).sort("_id", pymongo.ASCENDING)))
    df_huila_lose = pd.DataFrame(list(
        DBPyChanlun['future_auto_position'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
            "date_created": {"$gte": start, "$lte": end}, "status": "loseEnd", "signal": "huila"
        }).sort("_id", pymongo.ASCENDING)))

    df_tupo_win = pd.DataFrame(list(
        DBPyChanlun['future_auto_position'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
            "date_created": {"$gte": start, "$lte": end}, "status": "winEnd", "signal": "tupo"
        }).sort("_id", pymongo.ASCENDING)))
    df_tupo_lose = pd.DataFrame(list(
        DBPyChanlun['future_auto_position'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
            "date_created": {"$gte": start, "$lte": end}, "status": "loseEnd", "signal": "tupo"
        }).sort("_id", pymongo.ASCENDING)))

    # df_v_reverse_win = pd.DataFrame(list(DBPyChanlun['future_auto_position'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
    #     "date_created": {"$gte": start, "$lte": end}, "status": "winEnd", "signal": "v_reverse"
    # }).sort("_id", pymongo.ASCENDING)))
    # df_v_reverse_lose = pd.DataFrame(list(DBPyChanlun['future_auto_position'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
    #     "date_created": {"$gte": start, "$lte": end}, "status": "loseEnd", "signal": "v_reverse"
    # }).sort("_id", pymongo.ASCENDING)))

    df_five_v_reverse_win = pd.DataFrame(list(
        DBPyChanlun['future_auto_position'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
            "date_created": {"$gte": start, "$lte": end}, "status": "winEnd", "signal": "five_v_reverse"
        }).sort("_id", pymongo.ASCENDING)))
    df_five_v_reverse_lose = pd.DataFrame(list(
        DBPyChanlun['future_auto_position'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
            "date_created": {"$gte": start, "$lte": end}, "status": "loseEnd", "signal": "five_v_reverse"
        }).sort("_id", pymongo.ASCENDING)))

    signal_result = {
        "beichi_win_count": len(df_beichi_win),
        "beichi_lose_count": len(df_beichi_lose),
        "huila_win_count": len(df_huila_win),
        "huila_lose_count": len(df_huila_lose),
        "break_win_count": len(df_break_win),
        "break_lose_count": len(df_break_lose),
        "tupo_win_count": len(df_tupo_win),
        "tupo_lose_count": len(df_tupo_lose),
        # "v_reverse_win_count": len(df_v_reverse_win),
        # "v_reverse_lose_count": len(df_v_reverse_lose),
        "five_v_reverse_win_count": len(df_five_v_reverse_win),
        "five_v_reverse_lose_count": len(df_five_v_reverse_lose),

        "beichi_win_lose_count_rate": round(len(df_beichi_win) / len(df_beichi_lose), 2) if len(
            df_beichi_lose) != 0 else 1,
        "beichi_win_lose_money_rate": round(
            df_beichi_win['win_end_money'].sum() / df_beichi_lose['lose_end_money'].sum(), 2) if df_beichi_lose[
                                                                                                     'lose_end_money'].sum() != 0 else 1,

        "huila_win_lose_count_rate": round(len(df_huila_win) / len(df_huila_lose), 2) if len(df_huila_lose) != 0 else 1,
        "huila_win_lose_money_rate": round(df_huila_win['win_end_money'].sum() / df_huila_lose['lose_end_money'].sum(),
                                           2) if df_huila_lose['lose_end_money'].sum() != 0 else 1,

        "break_win_lose_count_rate": round(len(df_break_win) / len(df_break_lose), 2) if len(df_break_lose) != 0 else 1,
        "break_win_lose_money_rate": round(df_break_win['win_end_money'].sum() / df_break_lose['lose_end_money'].sum(),
                                           2) if df_break_lose['lose_end_money'].sum() != 0 else 1,

        "tupo_win_lose_count_rate": round(len(df_tupo_win) / len(df_tupo_lose), 2) if len(df_tupo_lose) != 0 else 1,
        "tupo_win_lose_money_rate": round(df_tupo_win['win_end_money'].sum() / df_tupo_lose['lose_end_money'].sum(),
                                          2) if df_tupo_lose['lose_end_money'].sum() != 0 else 1,

        # "v_reverse_win_lose_count_rate": round(len(df_v_reverse_win) / len(df_v_reverse_lose),2) if len(df_v_reverse_lose) != 0 else 1,
        # "v_reverse_win_lose_money_rate": round(df_v_reverse_win['win_end_money'].sum() / df_v_reverse_lose['lose_end_money'].sum(), 2) if df_v_reverse_lose['lose_end_money'].sum() != 0 else 1,
        #
        "five_v_reverse_win_lose_count_rate": round(len(df_five_v_reverse_win) / len(df_five_v_reverse_lose), 2) if len(
            df_five_v_reverse_lose) != 0 else 1,
        "five_v_reverse_win_lose_money_rate": round(
            df_five_v_reverse_win['win_end_money'].sum() / df_five_v_reverse_lose['lose_end_money'].sum(), 2) if
        df_five_v_reverse_lose[
            'lose_end_money'].sum() != 0 else 1
    }
    print(signal_result)


def testGetFutureSignalList():
    symbolList = config['symbolList']
    # 主力合约列表
    dominantSymbolList = []
    # 主力合约详细信息
    dominantSymbolInfoList = {}
    for i in range(len(symbolList)):
        df = rq.futures.get_dominant(symbolList[i], start_date=None, end_date=None, rule=0)
        dominantSymbol = df[-1]
        dominantSymbolList.append(dominantSymbol)
        dominantSymbolInfo = rq.instruments(dominantSymbol)
        dominantSymbolInfoList[dominantSymbol] = dominantSymbolInfo.__dict__

    print("当前主力合约:", dominantSymbolInfoList)
    print("当前主力合约2:", dominantSymbolList)
    symbolListMap = {}
    periodList = ['1m', '3m', '5m', '15m', '30m']
    for i in range(len(dominantSymbolList)):
        symbol = dominantSymbolList[i]
        symbolListMap[symbol] = {}
        for j in range(len(periodList)):
            period = periodList[j]
            symbolListMap[symbol][period] = {}
            symbolListMap[symbol][period]["direction"] = ""
            symbolListMap[symbol][period]["signal"] = ""

    future_signal_list = DBPyChanlun['future_signal'].find().sort(
        "fire_time", pymongo.DESCENDING)
    print(future_signal_list.count())

    for signalItem in future_signal_list:
        # print("信号item:", signalItem)
        # utc 转本地时间
        date_created = signalItem['date_created'] + timedelta(hours=8)
        date_created_str = date_created.strftime("%m-%d %H:%M")
        fire_time = signalItem['fire_time'] + timedelta(hours=8)
        fire_time_str = fire_time.strftime("%m-%d %H:%M")
        # str(round(signalItem['price'], 2))
        if 'level_direction' in signalItem:
            level_direction = signalItem['level_direction']
        else:
            level_direction = ""
        # msg = "%s %s %s %s" % (str(signalItem['signal']), str(signalItem['direction']), fire_time_str,
        #                           str(signalItem.get('tag', '')))
        msg = "%s %s" % (str(signalItem['signal']), str(signalItem['direction']))
        if signalItem['symbol'] in symbolListMap:
            if signalItem['period'] == '60m':
                continue
            symbolListMap[signalItem['symbol']][signalItem['period']]["direction"] = level_direction
            symbolListMap[signalItem['symbol']][signalItem['period']]["signal"] = msg
    print("期货信号列表", symbolListMap)
    return symbolListMap


def testDynamicProfit():
    statisticList = {}
    startDate = '2020-09-23'
    endDate = '2020-09-24'
    end = datetime.strptime(endDate, "%Y-%m-%d")
    end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    start = datetime.strptime(startDate, "%Y-%m-%d")
    start = start.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    data_list = DBPyChanlun['future_auto_position'].with_options(
        codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
        "date_created": {"$gte": start, "$lte": end}, "status": {'$ne': 'exception'}
    }).sort("_id", pymongo.ASCENDING)
    # print(data_list.count())
    df = pd.DataFrame(list(data_list))
    # 当持仓表中没有 单子止盈过的的时候 win_end_money字段为空
    if len(df) == 0 or 'win_end_money' not in df.columns.values or 'lose_end_money' not in df.columns.values:
        return {
            'date': [],
            'win_end_list': [],
            'lose_end_list': [],
            'net_profit_list': [],
            'win_money_list': [],
            'lose_money_list': [],
            'win_symbol_list': [],
            'lose_symbol_list': []
        }
    for idx, row in df.iterrows():
        # 根据日期分组
        date_created = df.loc[idx, 'date_created']
        date_created_str = formatTime(date_created)
        # 新增 格式化后的 日期列 2020-09-21
        df.loc[idx, 'new_date_created'] = date_created_str
        # 根据symbol分组 查询盈利品种排行和亏损品种排行
        symbol = df.loc[idx, 'symbol']
        # RB2010 -> RB
        simple_symbol = symbol.rstrip(string.digits)
        # 新增格式化后的 品种简称列
        df.loc[idx, 'simple_symbol'] = simple_symbol

    win_end_group_by_date = df['win_end_money'].groupby(df['new_date_created'])
    per_order_margin_group_by_date = df['per_order_margin'].groupby(df['new_date_created'])
    per_order_amount_group_by_date = df['amount'].groupby(df['new_date_created'])
    lose_end_group_by_date = df['lose_end_money'].groupby(df['new_date_created'])
    #
    win_end_group_by_symbol = df['win_end_money'].groupby(df['simple_symbol'])
    lose_end_group_by_symbol = df['lose_end_money'].groupby(df['simple_symbol'])
    # 查询 动止列表不为空的记录
    # win_end_group_by_date_dynamic = df['dynamicPositionList'][(df.status != 'exception') & (df.dynamicPositionList.notnull())].groupby(df['new_date_created'])
    win_end_group_by_date_dynamic = df['dynamicPositionList'][(df.status != 'exception')].groupby(
        df['new_date_created']) if 'dynamicPositionList' in df else []
    # 转化为list
    win_end_group_by_date_dynamic_list = list(win_end_group_by_date_dynamic)
    # 按日期记录每天的动止盈利
    dynamic_win_list = []
    for i in range(len(win_end_group_by_date_dynamic_list)):
        dynamic_win_sum = 0
        item = list(win_end_group_by_date_dynamic_list[i][1])
        for j in range(len(item)):
            if isinstance(item[j], list):
                for k in range(len(item[j])):
                    dynamic_win_sum = dynamic_win_sum + item[j][k]['stop_win_money']
        dynamic_win_list.append(int(dynamic_win_sum))
    # print(dynamic_win_list)
    # print(win_end_group_by_symbol.sum())
    # print(lose_end_group_by_symbol.sum())

    # print(win_end_group_by_date.sum())
    # print(lose_end_group_by_date.sum())
    # print(list(per_order_margin_group_by_date))
    # print(list(per_order_amount_group_by_date))
    per_order_margin_group_by_date_list = list(per_order_margin_group_by_date)
    per_order_amount_group_by_date_list = list(per_order_amount_group_by_date)
    # 总保证金
    total_margin_list = []

    for i in range(len(per_order_margin_group_by_date_list)):
        item_margin = per_order_margin_group_by_date_list[i][1]
        item_amount = per_order_amount_group_by_date_list[i][1]
        total_margin_sum = item_margin * item_amount
        # print("保证金\n",item_margin,"数量\n" ,item_amount,"总保证金\n",total_margin_sum.sum())
        total_margin_list.append(int(total_margin_sum.sum()))
    # print(total_margin_list)

    # 日期列表
    dateList = []
    # 当日盈利累加
    win_end_list = []
    # 每天亏损累加
    lose_end_list = []
    # 净盈亏
    net_profit_list = []

    # 盈利次数 列表
    win_end_count_list = []
    # 亏损次数 列表
    lose_end_count_list = []
    # 胜率 列表
    win_lose_count_rate = []
    # 盈亏比 列表
    win_lose_money_rate = []

    # 盈利单持仓天数
    win_end_holding_day_list = []
    # 亏损单持仓天数
    lose_end_holding_day_list = []

    # 保存日期
    for name, group in win_end_group_by_date:
        dateList.append(name)
    # 保存品种简称
    for i in range(len(win_end_group_by_date.sum())):
        # 止盈的盈利和 动止的盈利 累加
        dynamic_win_money = 0
        if len(dynamic_win_list) > 0:
            dynamic_win_money = dynamic_win_list[i]

        win_end_list.append(int(win_end_group_by_date.sum()[i]) + dynamic_win_money)
        lose_end_list.append(int(lose_end_group_by_date.sum()[i]))
        net_profit_list.append(
            int(win_end_group_by_date.sum()[i]) + dynamic_win_money + int(lose_end_group_by_date.sum()[i]))

        win_lose_money_rate.append(abs(round((int(win_end_group_by_date.sum()[i]) + dynamic_win_money) /
                                             (int(lose_end_group_by_date.sum()[i])), 2)))

        win_end_count_list.append(int(win_end_group_by_date.count()[i]))
        lose_end_count_list.append(int(lose_end_group_by_date.count()[i]))
        win_lose_count_rate.append(round(int(win_end_group_by_date.count()[i]) /
                                         (int(lose_end_group_by_date.count()[i]) + int(
                                             win_end_group_by_date.count()[i])), 2))

    sorted_win_money_list = win_end_group_by_symbol.max().sort_values(ascending=False).dropna(axis=0)
    sorted_lose_money_list = lose_end_group_by_symbol.max().sort_values(ascending=True).dropna(axis=0)

    win_symbol_list = list(sorted_win_money_list.index)
    lose_symbol_list = list(sorted_lose_money_list.index)

    # print(len(win_symbol_list))
    for i in range(len(win_symbol_list)):
        item_list = df[(df['simple_symbol'] == win_symbol_list[i]) & (df['status'] == 'winEnd')]
        count = 0
        for idx, row in item_list.iterrows():
            # 保存前一个 如果下一个 品种相同 就累加持仓天数
            start_date = row['date_created']
            end_date = row['win_end_time']
            delta_days = abs((end_date - start_date).days)
            if count == 0:
                win_end_holding_day_list.append(delta_days)
                print("symbol:", win_symbol_list[i], count, delta_days, i)
            else:
                win_end_holding_day_list[i] = (win_end_holding_day_list[i] + delta_days)
                print("symbol:", win_symbol_list[i], count, delta_days, i)
            count = count + 1
    for i in range(len(lose_symbol_list)):
        # print(win_symbol_list[i])
        item_list = df[(df['simple_symbol'] == lose_symbol_list[i]) & (df['status'] == 'loseEnd')]
        count = 0
        for idx, row in item_list.iterrows():
            start_date = row['date_created']
            end_date = row['lose_end_time']
            delta_days = abs((end_date - start_date).days)
            if count == 0:
                lose_end_holding_day_list.append(delta_days)
                print("symbol:", lose_symbol_list[i], count, delta_days)
            else:
                lose_end_holding_day_list[i] = lose_end_holding_day_list[i] + delta_days
                print("symbol:", lose_symbol_list[i], count, delta_days)
            count = count + 1
    print(win_end_holding_day_list, lose_end_holding_day_list)

    # 取整数
    win_money_list = list(sorted_win_money_list.dropna(axis=0))
    lose_money_list = list(sorted_lose_money_list.dropna(axis=0))
    for i in range(len(win_money_list)):
        win_money_list[i] = int(win_money_list[i])
    for i in range(len(lose_money_list)):
        lose_money_list[i] = int(lose_money_list[i])

    # print(win_symbol_list, win_money_list)
    # print(lose_symbol_list, lose_money_list)
    # print(win_end_list)
    # print(lose_end_list)
    # print(win_end_count_list)
    # print(lose_end_count_list)
    # print(win_lose_count_rate)
    # print(win_lose_money_rate)
    # print(sorted_win_money_list)

    # print(list(win_end_group_by_symbol))

    statisticList = {
        'date': dateList,
        'win_end_list': win_end_list,
        'lose_end_list': lose_end_list,
        'net_profit_list': net_profit_list,
        'win_money_list': win_money_list,
        'lose_money_list': lose_money_list,
        'win_symbol_list': win_symbol_list,
        'lose_symbol_list': lose_symbol_list,
        'total_margin_list': total_margin_list
    }
    print(win_symbol_list)
    print(lose_symbol_list)
    # print(lose_money_list)


def testPower():
    statisticList = {}
    startDate = '2020-10-09'
    endDate = '2020-10-20'
    end = datetime.strptime(endDate, "%Y-%m-%d")
    end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    start = datetime.strptime(startDate, "%Y-%m-%d")
    start = start.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    data_list = DBPyChanlun['future_auto_position'].with_options(
        codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
        "date_created": {"$gte": start, "$lte": end}, "status": {'$ne': 'exception'}
    }).sort("_id", pymongo.ASCENDING)
    # print(data_list.count())
    df = pd.DataFrame(list(data_list))
    # 当持仓表中没有 单子止盈过的的时候 win_end_money字段为空
    if len(df) == 0 or 'win_end_money' not in df.columns.values or 'lose_end_money' not in df.columns.values:
        return {
            'date': [],
            'win_end_list': [],
            'lose_end_list': [],
            'net_profit_list': [],
            'win_money_list': [],
            'lose_money_list': [],
            'win_symbol_list': [],
            'lose_symbol_list': []
        }
    for idx, row in df.iterrows():
        # 根据日期分组
        date_created = df.loc[idx, 'date_created']
        date_created_str = formatTime(date_created)
        # 新增 格式化后的 日期列 2020-09-21
        df.loc[idx, 'new_date_created'] = date_created_str
        # 根据symbol分组 查询盈利品种排行和亏损品种排行
        symbol = df.loc[idx, 'symbol']
        # RB2010 -> RB
        simple_symbol = symbol.rstrip(string.digits)
        # 新增格式化后的 品种简称列
        df.loc[idx, 'simple_symbol'] = simple_symbol

    win_end_group_by_date = df['win_end_money'].groupby(df['new_date_created'])
    per_order_margin_group_by_date = df['per_order_margin'].groupby(df['new_date_created'])
    per_order_amount_group_by_date = df['amount'].groupby(df['new_date_created'])
    lose_end_group_by_date = df['lose_end_money'].groupby(df['new_date_created'])
    #
    win_end_group_by_symbol = df['win_end_money'].groupby(df['simple_symbol'])
    lose_end_group_by_symbol = df['lose_end_money'].groupby(df['simple_symbol'])
    # 查询 动止列表不为空的记录
    # win_end_group_by_date_dynamic = df['dynamicPositionList'][(df.status != 'exception') & (df.dynamicPositionList.notnull())].groupby(df['new_date_created'])
    win_end_group_by_date_dynamic = df['dynamicPositionList'][(df.status != 'exception')].groupby(
        df['new_date_created']) if 'dynamicPositionList' in df else []
    # 转化为list
    win_end_group_by_date_dynamic_list = list(win_end_group_by_date_dynamic)
    # 按日期记录每天的动止盈利
    dynamic_win_list = []
    for i in range(len(win_end_group_by_date_dynamic_list)):
        dynamic_win_sum = 0
        item = list(win_end_group_by_date_dynamic_list[i][1])
        for j in range(len(item)):
            if isinstance(item[j], list):
                for k in range(len(item[j])):
                    dynamic_win_sum = dynamic_win_sum + item[j][k]['stop_win_money']
        dynamic_win_list.append(int(dynamic_win_sum))

    print(dynamic_win_list)

    per_order_margin_group_by_date_list = list(per_order_margin_group_by_date)
    per_order_amount_group_by_date_list = list(per_order_amount_group_by_date)
    # 总保证金
    total_margin_list = []

    for i in range(len(per_order_margin_group_by_date_list)):
        item_margin = per_order_margin_group_by_date_list[i][1]
        item_amount = per_order_amount_group_by_date_list[i][1]
        total_margin_sum = item_margin * item_amount
        # print("保证金\n",item_margin,"数量\n" ,item_amount,"总保证金\n",total_margin_sum.sum())
        total_margin_list.append(int(total_margin_sum.sum()))

    # 日期列表
    dateList = []
    # 当日盈利累加
    win_end_list = []
    # 每天亏损累加
    lose_end_list = []
    # 净盈亏
    net_profit_list = []

    # 盈利次数 列表
    win_end_count_list = []
    # 亏损次数 列表
    lose_end_count_list = []
    # 胜率 列表
    win_lose_count_rate = []
    # 盈亏比 列表
    win_lose_money_rate = []

    # 盈利单持仓天数
    win_end_holding_day_list = []
    # 亏损单持仓天数
    lose_end_holding_day_list = []

    # 保存日期
    for name, group in win_end_group_by_date:
        dateList.append(name)

    power_list = []
    win_end_group_by_power = df['win_end_money'].groupby(df['power'])
    lose_end_group_by_power = df['lose_end_money'].groupby(df['power'])

    for name, group in win_end_group_by_power:
        power_list.append(name)

    win_end_power_list = []
    lose_end_power_list = []
    net_profit_power_list = []

    win_end_count_power_list = []

    lose_end_count_power_list = []

    win_lose_count_power_rate = []

    win_lose_money_power_rate = []

    print(win_end_group_by_power.sum())

    win_end_power_list = list(win_end_group_by_power.sum())
    lose_end_power_list = list(lose_end_group_by_power.sum())
    net_profit_power_list = list(win_end_group_by_power.sum() + lose_end_group_by_power.sum())
    win_end_count_power_list = list(win_end_group_by_power.count())
    lose_end_count_power_list = list(lose_end_group_by_power.count())

    win_lose_count_power_rate = list(
        win_end_group_by_power.count() / (win_end_group_by_power.count() + lose_end_group_by_power.count()))

    win_lose_money_power_rate = list(
        win_end_group_by_power.sum() / (win_end_group_by_power.sum() + lose_end_group_by_power.sum()))
    # print(list(win_end_group_by_power.sum()))

    # for i in range(len(win_end_group_by_power.sum())):

    # win_end_power_list.append(int(win_end_group_by_power.sum()[i]))
    # lose_end_power_list.append(int(lose_end_group_by_power.sum()[i]))
    # net_profit_power_list.append(int(win_end_group_by_power.sum()[i]) + int(lose_end_group_by_power.sum()[i]))
    #
    # win_lose_money_power_rate.append(abs(round((int(win_end_group_by_power.sum()[i])) /
    #                                      (int(lose_end_group_by_power.sum()[i])), 2)))
    #
    # win_end_count_power_list.append(int(win_end_group_by_power.count()[i]))
    # lose_end_count_power_list.append(int(lose_end_group_by_power.count()[i]))
    # win_lose_count_power_rate.append(round(int(win_end_group_by_power.count()[i]) /
    #                                  (int(lose_end_group_by_power.count()[i]) + int(win_end_group_by_power.count()[i])), 2))
    print(power_list)
    print(win_end_power_list)
    print(lose_end_power_list)
    print(net_profit_power_list)

    print(win_end_count_power_list)
    print(lose_end_count_power_list)
    print(win_lose_count_power_rate)
    print(win_lose_money_power_rate)


def testBus():
    from pychanlun.monitor.BusinessService import businessService
    test = businessService.getStatisticList('2020-10-20,2020-10-27')
    print(json.dumps(test))


def test_future_change_list():
    end = datetime.now()- timedelta(1)
    end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    start_date = end + timedelta(-1)
    # print("->",start_date,end)
    symbol_list = config['symbolList']
    change_list = {}
    for i in range(len(symbol_list)):
        item = symbol_list[i] + "L9"
        # 查日线开盘价
        data_list = list(
            DBQuantAxis["future_day"].find({"code": item}).sort("_id", pymongo.DESCENDING).limit(1))
        if len(data_list) == 0:
            continue
        day_open_price = data_list[0]['open']
        # 查1分钟收盘价
        data_list2 = list(DBQuantAxis["future_min"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({
            "code": item,
            "type": "1min",
            "time_stamp": {"$gte": start_date.timestamp()}
        }) \
            .sort("_id", pymongo.DESCENDING).limit(1))

        if len(data_list2) == 0:
            continue
        min_close_price = data_list2[0]['close']

        change = round((min_close_price - day_open_price) / day_open_price, 4)
        change_item = {
            'change': change,
            'price': min_close_price
        }
        # print(item, '-> ', day_open_price, ' -> ', min_close_price)
        change_list[item] = change_item
    # print(change_list)
    return change_list


def app():
    test_future_change_list()
    # testBus()
    # testPower()
    # testDynamicProfit()
    # testGetFutureSignalList()
    # testStatistic()
    # testDingDing()
    # testBitmex()
    # testBeichiDb()
    # testHuila()
    # testChange()
    # testTQ()
    # testRQ()
    # testMonitor()
    # testThread()
    # testHuobi()
    # testWaipan()
    # testWechat()
    # testOkex1()
    # testOkex2()
    # testOkexTiker()
    # testChaji()
    # testGlobalChangeList()
    # testTime2()
    # testMail()
    # testDingDing()
    # testGroupBy()
    # testMeigu()
    # testFutu()
    # testWStock()
    # testMongoArr()
    # testWind()
    # testMA()
    # testSplit()


if __name__ == '__main__':
    app()
