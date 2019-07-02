from back.Calc import Calc
from back.KlineDataTool import KlineDataTool
from jqdatasdk import *
import numpy as np
import pandas as pd
from numpy import array
import talib as ta
import time

from back.Mail import Mail

'''
背驰监控
'''

klineDataTool = KlineDataTool()
symbolList1 = ['RB1910.XSGE', 'HC1910.XSGE', 'RU1909.XSGE', 'NI1907.XSGE', 'FU1909.XSGE', 'ZN1908.XSGE',
               'SP1909.XSGE', 'MA1909.XZCE', 'SR1909.XZCE', 'AP1910.XZCE', 'CF1909.XZCE', 'J1909.XDCE', 'JM1909.XDCE',
               'PP1909.XDCE']

# 23:30结束的  甲醇 白糖 玻璃
symbolList2 = ['MA1909.XZCE', 'SR1909.XZCE', 'FG1909.XZCE']
# 1:00 结束的锌 镍
symbolList3 = ['NI1907.XSGE', 'ZN1907.XSGE']

periodList = ['1min', '3min', '5min', '15min', '30min', '60min']

symbolList = symbolList1
mail = Mail()


# 监控期货
# timeScope 监控距离现在多少分钟的
def monitorFutures(timeScope):
    auth('13088887055', 'chanlun123456')

    lastTimeMap = {}
    for i in range(len(symbolList)):
        symbol = symbolList[i]
        lastTimeMap[symbol] = {}
        for j in range(len(periodList)):
            period = periodList[j]
            lastTimeMap[symbol][period] = 0

    print(lastTimeMap)

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
                print("diffTime:", diffTime, symbol, period)

                period = '5min'
                symbol = 'RB1910.XSGE'
                result = calc.calcData(period, symbol)
                if len(result['buyMACDBCData']['date']) > 0:
                    lastBuyDate = result['buyMACDBCData']['date'][-1]
                    lastBuyValue = result['buyMACDBCData']['value'][-1]

                    dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))

                    if lastTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                        msg = "当前:", symbol, period, lastBuyDate, lastBuyValue
                        print(msg)
                        mailResult = mail.send(str(msg))
                        if not mailResult:
                            print("发送失败")
                if len(result['sellMACDBCData']['date']) > 0:
                    lastSellDate = result['sellMACDBCData']['date'][-1]
                    lastSellValue = result['sellMACDBCData']['value'][-1]
                    dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))

                    if lastTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                        msg = "当前:", symbol, period, lastSellDate, lastSellValue
                        print(msg)
                        mailResult = mail.send(str(msg))
                        if not mailResult:
                            print("发送失败")
                time.sleep(5)


# 监控BTC
# timeScope 监控距离现在多少分钟的
def monitorBTC(timeScope):
    symbol = 'XBTUSD'
    lastTimeMap = {}
    lastTimeMap[symbol] = {}
    for j in range(len(periodList)):
        period = periodList[j]
        lastTimeMap[symbol][period] = 0
    print(lastTimeMap)

    while True:
        for j in range(len(periodList)):
            period = periodList[j]
            calc = Calc()
            result = calc.calcData(period, symbol)
            # 当前时间戳 秒为单位
            currentTime = int(time.time())

            lastTime = lastTimeMap[symbol][period]
            diffTime = currentTime - lastTime

            if len(result['buyMACDBCData']['date']) > 0:
                lastBuyDate = result['buyMACDBCData']['date'][-1]
                dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
                lastBuyValue = result['buyMACDBCData']['value'][-1]

                if lastTime != dateStamp and currentTime - dateStamp <= 60*timeScope:
                    lastTimeMap[symbol][period] = dateStamp
                    msg = "当前:", symbol, period, lastBuyDate, lastBuyValue
                    print(msg)
                    mailResult = mail.send(str(msg))
                    if not mailResult:
                        print("发送失败")

            if len(result['sellMACDBCData']['date']) > 0:
                lastSellDate = result['sellMACDBCData']['date'][-1]
                lastSellValue = result['sellMACDBCData']['value'][-1]
                dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))

                if lastTime != dateStamp and currentTime - dateStamp <= 60*timeScope:
                    lastTimeMap[symbol][period] = dateStamp
                    msg = "当前:", symbol, period, lastSellDate, lastSellValue
                    print(msg)
                    mailResult = mail.send(str(msg))
                    if not mailResult:
                        print("发送失败")
            time.sleep(5)
        time.sleep(10)


monitorBTC(240)
# monitorFutures(60)
