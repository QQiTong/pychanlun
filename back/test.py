import requests
import json
import time
import pydash
from datetime import datetime
from back.funcat.api import *

import sys
from rqdatac import *
from mongoengine import connect
import os

from back.monitor.BeichiLog import BeichiLog
from back.config import config
import rqdatac as rq

periodList = ['3min', '5min', '15min', '30min', '60min', '4hour', '1day']



def getDominantSymbol():
    symbolList = ['RB', 'HC', 'RU', 'NI', 'FU', 'ZN', 'SP', 'BU',
                  'MA', 'TA', 'SR', 'OI', 'AP', 'CF',
                  'M', 'I', 'EG', 'J', 'JM', 'PP', 'L'
                  ]
    dominantSymbolList = []
    for i in range(len(symbolList)):
        df = rq.futures.get_dominant(symbolList[i], start_date=None, end_date=None, rule=0)
        dominantSymbol = df[-1]
        dominantSymbolList.append(dominantSymbol)
    return dominantSymbolList


def app():
    init('license',
         'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
         ('rqdatad-pro.ricequant.com', 16011))
    cfg = config[os.environ.get('PYCHANLUN_CONFIG_ENV', 'default')]
    mongodbSettings = cfg.MONGODB_SETTINGS
    connect('pychanlun', host=mongodbSettings['host'], port=mongodbSettings['port'],
            username=mongodbSettings['username'], password=mongodbSettings['password'], authentication_source='admin')
    # mLog = BeichiLog(symbol="BTC_CQ", period="30min", price=18000, signal=True,remark='XB')
    mLog = BeichiLog(symbol="RB2001", period="30min", price=18000, signal=True,remark='XT')
    mLog = BeichiLog(symbol="RU2001", period="60min", price=18000, signal=True,remark='XB')
    mLog.save()
    # 获取主力合约
    # symbolList = getDominantSymbol()
    # symbolListMap = {}
    # for i in range(len(symbolList)):
    #     symbol = symbolList[i]
    #     symbolListMap[symbol] = {}
    #
    #     for j in range(len(periodList)):
    #         period = periodList[j]
    #         symbolListMap[symbol][period] = ""
    #
    # # print(symbolListMap)
    # # symbolListMap = {}
    # for beichiItem in BeichiLog.objects:
    #     symbolListMap[beichiItem.symbol][beichiItem.period] = beichiItem.signal, " ", str(beichiItem.price)
    #     # print(beichiItem.symbol)
    # print(json.dumps(symbolListMap))


if __name__ == '__main__':
    app()
# hbdmUrl = "https://api.hbdm.com/market/history/kline"
#
# payload1 = {
#     'symbol': 'BTC_CQ',  # 合约类型， 火币季度合约
#     'period': '1min',
#     'size': 2000
# }
#
# r = requests.get(hbdmUrl, params=payload1)
# print(json.loads(r.text)['ch'])

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
