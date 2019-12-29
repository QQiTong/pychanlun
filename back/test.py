import requests
import json
import time
import pydash
from datetime import datetime, timedelta

from back.Calc import Calc
from back.KlineDataTool import KlineDataTool
from back.funcat.api import *

import sys
from rqdatac import *
import os
import pymongo

from back.config import config
import rqdatac as rq
import requests
from back.db import DBPyChanlun

periodList = ['3min', '5min', '15min', '30min', '60min', '4hour', '1day']


def getDominantSymbol():
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
    init('license',
         'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
         ('rqdatad-pro.ricequant.com', 16011))
    dominantSymbolList = getDominantSymbol()
    # symbolChangeMap = {}
    # end = datetime.now() + timedelta(1)
    # start = datetime.now() + timedelta(-7)
    # for i in range(len(dominantSymbolList)):
    #     item = dominantSymbolList[i]
    #     print(item)
    #     df1d = rq.get_price(item, frequency='1d', fields=['open', 'high', 'low', 'close', 'volume'],
    #                         start_date=start, end_date=end)
    #     df1m = rq.get_price(item, frequency='1m', fields=['open', 'high', 'low', 'close', 'volume'],
    #                         start_date=start, end_date=end)
    #     if df1d is None or df1m is None:
    #         change = "--"
    #     else:
    #         preday = df1d.iloc[0, 3]
    #         today = df1m.iloc[0, 3]
    #         change = (today - preday) / preday
    #     symbolChangeMap[item] = change
    #     print(change)
    return False


def testProxy():
    proxies = {'http': '127.0.0.1:10809', 'https': '127.0.0.1:10809'}
    # url = 'http://www.baidu.com'
    # requests.post(url, proxies=proxies, verify=False)  # verify是否验证服务器的SSL证书
    return False


def testHuobi():
    proxies = {'http': '127.0.0.1:10809', 'https': '127.0.0.1:10809'}
    hbdmUrl = "http://api.hbdm.com/market/history/kline"
    payload1 = {
        'symbol': 'BTC_CQ',  # 合约类型， 火币季度合约
        'period': '1min',
        'size': 2000
    }
    r = requests.get(hbdmUrl, params=payload1, proxies=proxies, verify=False)
    print(json.loads(r.text)['data'])


def testPydash():
    a = [1, 2, 1, 5]
    b = pydash.find_index(a, lambda x: x == 1)
    print(b)


def testTime():
    stamp = 1568091600
    test = datetime.fromtimestamp(stamp)
    print(test)


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
    elif period == "210m":
        period = '1'
        target = 210
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
    # getBtcData('210m')
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
    result = calc.calcData("3m","RB2001")
    print("结果：",result)
def app():
    # testBitmex()
    testBeichiDb()
    # testHuila()
    # testChange()

if __name__ == '__main__':
    app()

# currentTime = int(time.time())
# print(currentTime)
#
# dateStamp = int(time.mktime(time.strptime("2019-08-25 12:55", "%Y-%m-%d %H:%M")))
# print(dateStamp)
# a = [1,2,3,4,3]
#
# result = pydash.find_index(a,lambda i:i ==3)
# print(result)

# result = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
# print(result)
# a = [0,1,2,3,4,5,6]
# b = [9,8,7,6,5,4,3]
# r = CROSS(a, b)
# print(r.series)
