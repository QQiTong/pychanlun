from back.Calc import Calc
from back.KlineDataTool import KlineDataTool
from jqdatasdk import *
import numpy as np
import pandas as pd
from numpy import array
import talib as ta
import rqdatac as rq
from datetime import datetime
from rqdatac import *
import time
import threading
from back.Mail import Mail

'''
背驰监控
'''
klineDataTool = KlineDataTool()
# 米筐数据 主力连续合约 这个会比实时数据少一天
# symbolList1 = ['RB88', 'HC88', 'RU88', 'NI88', 'FU88', 'ZN88',
#                'SP88', 'MA88', 'SR88', 'AP88', 'CF88', 'J88', 'JM88',
#                'PP88']
# 米筐数据 主力具体合约 这个是实时数据
symbolListFuture = ['RB2001', 'HC2001', 'RU2001', 'NI1911', 'FU2001', 'ZN1910', 'SP2001',  'BU1912',
                    # 'CU1910', 'AL1910','AU1912', 'AG1912',
                    'MA2001', 'TA2001',  'SR2001', 'OI2001',  'AP1910', 'CF2001',
                    'M2001', 'I2001', 'EG2001', 'J2001', 'JM2001', 'PP2001',
                    # 'RM2001','FG2001', 'ZC1911','CJ1912','Y2001', 'P2001','L2001', 'C2001','V2001', 'A2001', 'B1910'
                    ]

symbolListDigitCoin = ['BTC_CQ'
                       # 'ETH_CQ', 'BCH_CQ', 'LTC_CQ', 'BSV_CQ'
                       ]
#
periodList1 = ['1min', '3min', '5min', '15min', '30min', '60min']
periodList2 = ['3min', '5min', '15min', '30min', '60min']


mail = Mail()



# 监控期货
# timeScope 监控距离现在多少分钟的
def monitorFuturesAndDigitCoin(type):
    timeScope = 2
    lastTimeMap = {}
    symbolList = []
    if type == "1":
        # auth('13088887055', 'chanlun123456')
        # count = get_query_count()
        # print(count)
        init('license',
             'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
             ('rqdatad-pro.ricequant.com', 16011))

        symbolList = symbolListFuture
        periodList = periodList2
    else:
        symbolList = symbolListDigitCoin
        periodList = periodList1

    for i in range(len(symbolList)):
        symbol = symbolList[i]
        lastTimeMap[symbol] = {}
        for j in range(len(periodList)):
            period = periodList[j]
            lastTimeMap[symbol][period] = 0
    print(lastTimeMap)
    startTime = int(time.time())
    try:
        while True:
            for i in range(len(symbolList)):
                for j in range(len(periodList)):
                    symbol = symbolList[i]
                    period = periodList[j]

                    calc = Calc()
                    # 当前时间戳 秒为单位
                    currentTime = int(time.time())

                    lastTime = lastTimeMap[symbol][period]
                    diffTime = currentTime - lastTime
                    print("current:", symbol, period)


                    result = calc.calcData(period, symbol)
                    closePrice = result['close'][-1]
                    if len(result['buyMACDBCData']['date']) > 0:
                        lastBuyDate = result['buyMACDBCData']['date'][-1]
                        lastBuyValue = result['buyMACDBCData']['value'][-1]
                        notLower = result['notLower']
                        dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
                        # print("current judge:", symbol, period, lastBuyDate, notLower)
                        if lastTime != dateStamp and notLower and currentTime - dateStamp <= 60 * timeScope:
                            lastTimeMap[symbol][period] = dateStamp
                            msg = "current:", symbol, period, lastBuyDate, lastBuyValue, closePrice ,notLower ,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                            print(msg)
                            mailResult = mail.send(str(msg))
                            if not mailResult:
                                print("发送失败")
                            else:
                                print("发送成功")
                    if len(result['sellMACDBCData']['date']) > 0:
                        notHigher = result['notHigher']
                        lastSellDate = result['sellMACDBCData']['date'][-1]
                        lastSellValue = result['sellMACDBCData']['value'][-1]

                        dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
                        # print("current judge:", symbol, period, lastSellDate, notHigher)
                        if lastTime != dateStamp and notHigher and currentTime - dateStamp <= 60 * timeScope:
                            lastTimeMap[symbol][period] = dateStamp
                            msg = "current:", symbol, period, lastSellDate, lastSellValue, closePrice,notHigher ,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                            print(msg)
                            mailResult = mail.send(str(msg))
                            if not mailResult:
                                print("发送失败")
                            else:
                                print("发送成功")

                    # 监控高级别
                    if len(result['buyHigherMACDBCData']['date']) > 0:
                        lastBuyDate = result['buyHigherMACDBCData']['date'][-1]
                        lastBuyValue = result['buyHigherMACDBCData']['value'][-1]

                        dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
                        notLower = result['notLower']
                        # print("current judge:", symbol, period, lastBuyDate, notLower)
                        if lastTime != dateStamp and notLower and currentTime - dateStamp <= 60 * timeScope:
                            lastTimeMap[symbol][period] = dateStamp
                            msg = "current:", symbol, period, lastBuyDate, lastBuyValue, closePrice,notLower ,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                            print(msg)
                            mailResult = mail.send(str(msg))
                            if not mailResult:
                                print("发送失败")
                            else:
                                print("发送成功")

                    if len(result['sellHigherMACDBCData']['date']) > 0:
                        lastSellDate = result['sellHigherMACDBCData']['date'][-1]
                        lastSellValue = result['sellHigherMACDBCData']['value'][-1]
                        dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
                        notHigher = result['notHigher']
                        # print("current judge:", symbol, period, lastSellDate, notHigher)
                        if lastTime != dateStamp and notHigher and currentTime - dateStamp <= 60 * timeScope:
                            lastTimeMap[symbol][period] = dateStamp
                            msg = "current:", symbol, period, lastSellDate, lastSellValue, closePrice,notHigher ,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                            print(msg)
                            mailResult = mail.send(str(msg))
                            if not mailResult:
                                print("发送失败")
                            else:
                                print("发送成功")
                    if type== "1":
                        time.sleep(0)
                    else:
                        time.sleep(5)
    except :
        if type == "1":
            print("期货出异常了")

            threading.Thread(target=monitorFuturesAndDigitCoin, args="1").start()
        else:
            print("火币出异常了")
            threading.Thread(target=monitorFuturesAndDigitCoin, args="2").start()


threading.Thread(target=monitorFuturesAndDigitCoin, args="1").start()
threading.Thread(target=monitorFuturesAndDigitCoin, args="2").start()
