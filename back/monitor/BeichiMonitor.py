from back.Calc import Calc
from back.KlineDataTool import KlineDataTool
from jqdatasdk import *
import numpy as np
import pandas as pd
from numpy import array
import talib as ta
import rqdatac as rq
from rqdatac import *
import time
import threading
from back.Mail import Mail

'''
背驰监控
'''

klineDataTool = KlineDataTool()
# symbolList1 = ['RB9999.XSGE', 'HC9999.XSGE', 'RU9999.XSGE', 'NI9999.XSGE', 'FU9999.XSGE', 'ZN9999.XSGE',
#                'SP9999.XSGE', 'MA9999.XZCE', 'SR9999.XZCE', 'AP9999.XZCE', 'CF9999.XZCE', 'J9999.XDCE', 'JM9999.XDCE',
#                'PP9999.XDCE']
# 米筐数据 主力连续合约 这个会比实时数据少一天
# symbolList1 = ['RB88', 'HC88', 'RU88', 'NI88', 'FU88', 'ZN88',
#                'SP88', 'MA88', 'SR88', 'AP88', 'CF88', 'J88', 'JM88',
#                'PP88']
# 米筐数据 主力具体合约 这个是实时数据
symbolList1 = ['RB1910', 'HC2001', 'RU2001', 'NI1910', 'FU2001', 'ZN1910',
               'SP2001', 'MA1909', 'SR2001', 'AP1910', 'CF2001', 'J2001', 'JM1909',
               'PP2001','TA2001','I2001','M2001','Y2001','EG2001']

# 23:30结束的  甲醇 白糖 玻璃 棉花
symbolList2 = ['MA1909', 'SR2001', 'FG2001','CF2001']
# 1:00 结束的锌 镍
symbolList3 = ['NI1910', 'ZN1910']

periodList = ['1min', '3min', '5min', '15min', '30min', '60min']
periodList2 = ['3min', '5min', '15min', '30min', '60min']

symbolList = symbolList1
mail = Mail()


# 监控期货
# timeScope 监控距离现在多少分钟的
def monitorFutures():
    # auth('13088887055', 'chanlun123456')
    # count = get_query_count()
    # print(count)
    init('license',
         'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
         ('rqdatad-pro.ricequant.com', 16011))
    timeScope = 2
    lastTimeMap = {}
    for i in range(len(symbolList)):
        symbol = symbolList[i]
        lastTimeMap[symbol] = {}
        for j in range(len(periodList2)):
            period = periodList2[j]
            lastTimeMap[symbol][period] = 0

    print(lastTimeMap)

    while True:
        for i in range(len(symbolList)):
            for j in range(len(periodList2)):
                symbol = symbolList[i]
                period = periodList2[j]
                calc = Calc()
                # 当前时间戳 秒为单位
                currentTime = int(time.time())

                lastTime = lastTimeMap[symbol][period]
                diffTime = currentTime - lastTime
                print("current:", symbol, period)

                # period = '5min'
                # symbol = 'RB1910'
                result = calc.calcData(period, symbol)
                closePrice = result['close'][-1]
                if len(result['buyMACDBCData']['date']) > 0:
                    lastBuyDate = result['buyMACDBCData']['date'][-1]
                    lastBuyValue = result['buyMACDBCData']['value'][-1]

                    dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))

                    if lastTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                        msg = "current:", symbol, period, lastBuyDate, lastBuyValue,closePrice
                        print(msg)
                        mailResult = mail.send(str(msg))
                        if not mailResult:
                            print("发送失败")
                if len(result['sellMACDBCData']['date']) > 0:
                    lastSellDate = result['sellMACDBCData']['date'][-1]
                    lastSellValue = result['sellMACDBCData']['value'][-1]
                    dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))

                    if lastTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                        msg = "current:", symbol, period, lastSellDate, lastSellValue,closePrice
                        print(msg)
                        mailResult = mail.send(str(msg))
                        if not mailResult:
                            print("发送失败")
                # 监控高级别
                if len(result['buyHigherMACDBCData']['date']) > 0:
                    lastBuyDate = result['buyHigherMACDBCData']['date'][-1]
                    lastBuyValue = result['buyHigherMACDBCData']['value'][-1]

                    dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))

                    if lastTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                        msg = "current:", symbol, period, lastBuyDate, lastBuyValue,closePrice
                        print(msg)
                        mailResult = mail.send(str(msg))
                        if not mailResult:
                            print("发送失败")

                if len(result['sellHigherMACDBCData']['date']) > 0:
                    lastSellDate = result['sellHigherMACDBCData']['date'][-1]
                    lastSellValue = result['sellHigherMACDBCData']['value'][-1]
                    dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))

                    if lastTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                        msg = "current:", symbol, period, lastSellDate, lastSellValue,closePrice
                        print(msg)
                        mailResult = mail.send(str(msg))
                        if not mailResult:
                            print("发送失败")
                time.sleep(5)


# 监控BTC
# timeScope 监控距离现在多少分钟的
def monitorBTC():
    timeScope = 2

    symbol = 'XBTUSD'
    lastTimeMap = {}
    lastTimeMap[symbol] = {}
    for j in range(len(periodList2)):
        period = periodList2[j]
        lastTimeMap[symbol][period] = 0
    print(lastTimeMap)

    while True:
        for j in range(len(periodList2)):
            period = periodList2[j]
            calc = Calc()
            # period = '3min'
            result = calc.calcData(period, symbol)
            # 当前时间戳 秒为单位
            currentTime = int(time.time())

            lastTime = lastTimeMap[symbol][period]
            diffTime = currentTime - lastTime
            closePrice = result['close'][-1]
            print("current:", symbol, period)

            if len(result['buyMACDBCData']['date']) > 0:
                lastBuyDate = result['buyMACDBCData']['date'][-1]
                dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
                lastBuyValue = result['buyMACDBCData']['value'][-1]

                if lastTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                    lastTimeMap[symbol][period] = dateStamp
                    msg = "current:", symbol, period, lastBuyDate, lastBuyValue,closePrice
                    print(msg)
                    mailResult = mail.send(str(msg))
                    if not mailResult:
                        print("发送失败")

            if len(result['sellMACDBCData']['date']) > 0:
                lastSellDate = result['sellMACDBCData']['date'][-1]
                lastSellValue = result['sellMACDBCData']['value'][-1]
                dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))

                if lastTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                    lastTimeMap[symbol][period] = dateStamp
                    msg = "current:", symbol, period, lastSellDate, lastSellValue,closePrice
                    print(msg)
                    mailResult = mail.send(str(msg))
                    if not mailResult:
                        print("发送失败")
            # 监控高级别
            if len(result['buyHigherMACDBCData']['date']) > 0:
                lastBuyDate = result['buyHigherMACDBCData']['date'][-1]
                dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
                lastBuyValue = result['buyHigherMACDBCData']['value'][-1]

                if lastTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                    lastTimeMap[symbol][period] = dateStamp
                    msg = "current:", symbol, period, lastBuyDate, lastBuyValue,closePrice
                    print(msg)
                    mailResult = mail.send(str(msg))
                    if not mailResult:
                        print("发送失败")
            if len(result['sellHigherMACDBCData']['date']) > 0:
                lastSellDate = result['sellHigherMACDBCData']['date'][-1]
                lastSellValue = result['sellHigherMACDBCData']['value'][-1]
                dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))

                if lastTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                    lastTimeMap[symbol][period] = dateStamp
                    msg = "current:", symbol, period, lastSellDate, lastSellValue,closePrice
                    print(msg)
                    mailResult = mail.send(str(msg))
                    if not mailResult:
                        print("发送失败")
            time.sleep(5)
        time.sleep(10)


threading.Thread(target=monitorBTC).start()
threading.Thread(target=monitorFutures).start()
# monitorBTC(2)
# monitorFutures(2)
