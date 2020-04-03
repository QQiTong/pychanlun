# -*- coding: utf-8 -*-

import requests
import json
import time
import pydash
from datetime import datetime, timedelta

from bson import CodecOptions

from pychanlun.Calc import Calc
from pychanlun.KlineDataTool import KlineDataTool
from pychanlun.Mail import Mail
from pychanlun.funcat.api import *
from pychanlun.monitor import BeichiMonitor
import sys
from rqdatac import *
import os
import pymongo

from pychanlun.config import config
import rqdatac as rq
import requests
from pychanlun.db import DBPyChanlun
from tqsdk import TqApi
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from tqsdk import tafunc
import re
import pytz
import string

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
        if item is not 'BTC' and item is not 'ETH_CQ':
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
    df1d = rq.get_price('SR2009', frequency='1m', fields=['open', 'high', 'low', 'close', 'volume'],
                        )
    print(df1d)
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
          % (signal, remark, symbol + '_' + period, signal, direction, '开:' + str(close_price) + ' 止:' + str(stop_lose_price) + ' 触:' + str(price), amount,
             '开:' + fire_time_str + ' 触:' + date_created_str)
    requests.post(url)


#
def testOkex1():
    startTime = int(round(time.time() * 1000))

    PROXIES = {
        "http": "socks5://127.0.0.1:10808",
        "https": "socks5://127.0.0.1:10808"
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
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
    data_list = DBPyChanlun['future_auto_position'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
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


def app():
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
    testGroupBy()


if __name__ == '__main__':
    app()
