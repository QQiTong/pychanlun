import requests
import json
import time
import pydash
from datetime import datetime, timedelta

from back.KlineDataTool import KlineDataTool
from back.funcat.api import *

import sys
from rqdatac import *
from mongoengine import connect
import os

from back.monitor.BeichiLog import BeichiLog
from back.config import config
import rqdatac as rq
import requests

periodList = ['3min', '5min', '15min', '30min', '60min', '4hour', '1day']


def getDominantSymbol():
    with open(os.path.join(os.path.pathname(__file__), "../futureSymbol.json"), 'r') as load_f:
        symbolList = json.load(load_f)
        print(symbolList)

    dominantSymbolList = []
    for i in range(len(symbolList)):
        df = rq.futures.get_dominant(symbolList[i], start_date=None, end_date=None, rule=0)
        dominantSymbol = df[-1]
        dominantSymbolList.append(dominantSymbol)
    return dominantSymbolList


def testDb():
    # with open("../futureSymbol.json", 'r') as load_f:
    #     load_dict = json.load(load_f)
    #     print(load_dict)
    # init('license',
    #      'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
    #      ('rqdatad-pro.ricequant.com', 16011))
    # cfg = config[os.environ.get('PYCHANLUN_CONFIG_ENV', 'default')]
    # mongodbSettings = cfg.MONGODB_SETTINGS
    # connect('pychanlun', host=mongodbSettings['host'], port=mongodbSettings['port'],
    #         username=mongodbSettings['username'], password=mongodbSettings['password'], authentication_source='admin')
    # mLog = BeichiLog(symbol="BTC_CQ", period="30min", price=18000, signal=True,remark='XB')
    # mLog = BeichiLog(symbol="RU2001", period="4hour", price=16001, signal=True,remark='XT')
    # mLog = BeichiLog(symbol="RU2001", period="4hour", price=16000, signal=True,remark='XT')
    # mLog.save()
    return False

def testChange():
    # dominantSymbolList = getDominantSymbol()
    # symbolChangeMap = {}
    end = datetime.now() + timedelta(1)
    start = datetime.now() + timedelta(-1)
    # for i in range(len(dominantSymbolList)):
    #     item = dominantSymbolList[i]
    #     df1d = rq.get_price(item, frequency='1d', fields=['open', 'high', 'low', 'close', 'volume'],
    #                       start_date=start, end_date=end)
    #     df1m = rq.get_price(item, frequency='1m', fields=['open', 'high', 'low', 'close', 'volume'],
    #                       start_date=start, end_date=end)
    #     preday = df1d.iloc[len(df1d)-1, 3]
    #     today = df1m.iloc[len(df1m)-1, 3]
    #     change = (today - preday) / preday
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

def app():
    testHuobi()

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
