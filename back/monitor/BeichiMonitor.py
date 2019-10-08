import logging
import traceback
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
import pydash
from back.funcat.api import *
from back.config import config
import os
import json
from back.db import DBPyChanlun
from back.config import config

'''
背驰监控
'''
klineDataTool = KlineDataTool()
# 米筐数据 主力连续合约 这个会比实时数据少一天
# symbolList1 = ['RB88', 'HC88', 'RU88', 'NI88', 'FU88', 'ZN88',
#                'SP88', 'MA88', 'SR88', 'AP88', 'CF88', 'J88', 'JM88',
#                'PP88']
# 米筐数据 主力具体合约 这个是实时数据


symbolListDigitCoin = ['BTC_CQ'
                       # 'ETH_CQ', 'BCH_CQ', 'LTC_CQ', 'BSV_CQ'
                       ]
#
# periodList2 = ['3min', '5min', '15min', '30min', '60min', '4hour']
periodList = ['3m', '5m', '15m', '30m', '60m']
periodList2 = ['3m', '5m', '15m', '30m', '60m']

mail = Mail()


def saveBeichiLog(symbol, period, price, signal, remark):
    DBPyChanlun['beichi_log'].insert_one({
        'date_created': datetime.now().strftime("%m-%d %H:%M"),
        'symbol': symbol,
        'period': period,
        'price': round(price, 2),
        'signal': signal,
        'remark': remark
    })


# def saveStrategy4Log(symbol, period, raw_data, signal, remark, fire_time, price, position):
#     last_fire = DBPyChanlun['strategy4_log'].find_one({
#         'symbol': symbol['code'],
#         'peroid': period,
#         'fire_time': fire_time,
#         'position': position
#     })
#
#     if last_fire is not None:
#         DBPyChanlun['strategy4_log'].find_one_and_update({
#             'symbol': symbol['code'], 'period': period, 'fire_time': fire_time, 'position': position
#         }, {
#             '$set': {
#                 'remark': remark,
#                 'price': price,
#                 'date_created': datetime.utcnow()
#             },
#             '$inc': {
#                 'update_count': 1
#             }
#         }, upsert=True)
#     else:
#         date_created = datetime.utcnow()
#         DBPyChanlun['strategy4_log'].insert_one({
#             'symbol': symbol['code'],
#             'period': period,
#             'raw_data': raw_data,
#             'signal': True,
#             'remark': remark,
#             'date_created': date_created,#记录插入的时间
#             'fire_time': fire_time, #背驰发生的时间
#             'price': price,
#             'position': position,
#             'update_count': 1, # 这条背驰记录的更新次数
#         })
#         if (date_created - fire_time).total_seconds() < 600:
#             # 在10分钟内的触发邮件通知
#             mailResult = mail.send("%s %s %s %s" % (symbol['code'], fire_time, price, position))
#             print(mailResult)

def getDominantSymbol():
    symbolList = config['symbolList']
    dominantSymbolList = []
    for i in range(len(symbolList)):
        df = rq.futures.get_dominant(symbolList[i], start_date=None, end_date=None, rule=0)
        dominantSymbol = df[-1]
        dominantSymbolList.append(dominantSymbol)
    return dominantSymbolList


# 监控期货
# timeScope 监控距离现在多少分钟的
def monitorFuturesAndDigitCoin(type):
    logger = logging.getLogger()
    timeScope = 2
    lastTimeMap = {}
    lastTimeHuilaMap = {}
    lastTimeTupoMap = {}
    lastTimeVreverseMap = {}

    symbolList = []
    if type == "1":
        # auth('13088887055', 'chanlun123456')
        # count = get_query_count()
        # print(count)
        init('license',
             'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
             ('rqdatad-pro.ricequant.com', 16011))

        symbolList = getDominantSymbol()
        periodList = periodList2
    else:
        symbolList = symbolListDigitCoin
        periodList = periodList2

    for i in range(len(symbolList)):
        symbol = symbolList[i]
        lastTimeMap[symbol] = {}
        lastTimeHuilaMap[symbol] = {}
        lastTimeTupoMap[symbol] = {}
        lastTimeVreverseMap[symbol] = {}

        for j in range(len(periodList)):
            period = periodList[j]
            lastTimeMap[symbol][period] = 0
            lastTimeHuilaMap[symbol][period] = 0
            lastTimeTupoMap[symbol][period] = 0
            lastTimeVreverseMap[symbol][period] = 0
    print(lastTimeMap)
    print(lastTimeHuilaMap)
    print(lastTimeTupoMap)
    print(lastTimeVreverseMap)
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
                    lastHuilaTime = lastTimeHuilaMap[symbol][period]
                    lastTupoTime = lastTimeTupoMap[symbol][period]
                    lastVreverseTime = lastTimeVreverseMap[symbol][period]
                    diffTime = currentTime - lastTime
                    print("current:", symbol, period, datetime.now())
                    result = calc.calcData(period, symbol)
                    closePrice = result['close'][-1]
                    monitorBeichi(result, lastTime, currentTime, timeScope, lastTimeMap, symbol, period, closePrice)
                    monitorHuila(result, lastHuilaTime, currentTime, timeScope, lastTimeHuilaMap, symbol, period,
                                 closePrice)
                    monitorTupo(result, lastTupoTime, currentTime, timeScope, lastTimeTupoMap, symbol, period,
                                closePrice)
                    monitorVreverse(result, lastVreverseTime, currentTime, timeScope, lastTimeVreverseMap, symbol, period,
                                closePrice)

            if type == "1":
                time.sleep(0)
            else:
                time.sleep(5)
    except Exception:
        logger.info("Error Occurred: {0}".format(traceback.format_exc()))
        print("Error Occurred: {0}".format(traceback.format_exc()))
        if type == "1":
            print("期货出异常了", Exception)

            threading.Thread(target=monitorFuturesAndDigitCoin, args="1").start()
        else:
            print("火币出异常了", Exception)
            time.sleep(5)
            threading.Thread(target=monitorFuturesAndDigitCoin, args="2").start()


'''
监控背驰
'''
def monitorBeichi(result, lastTime, currentTime, timeScope, lastTimeMap, symbol, period, closePrice):
    # 监控背驰
    if len(result['buyMACDBCData']['date']) > 0:
        lastBuyDate = result['buyMACDBCData']['date'][-1]
        lastBuyValue = result['buyMACDBCData']['value'][-1]
        firstBi = result['buyMACDBCData']['stop_win_price'][-1]

        notLower = result['notLower']
        dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastBuyDate, notLower)
        if lastTime != dateStamp and notLower and currentTime - dateStamp <= 60 * timeScope:
            lastTimeMap[symbol][period] = dateStamp
            msg = "current:", symbol, period, lastBuyDate, lastBuyValue, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            sendEmail(msg)
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                          remark=lastBuyValue)

    if len(result['sellMACDBCData']['date']) > 0:
        notHigher = result['notHigher']
        lastSellDate = result['sellMACDBCData']['date'][-1]
        lastSellValue = result['sellMACDBCData']['value'][-1]

        dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastSellDate, notHigher)
        if lastTime != dateStamp and notHigher and currentTime - dateStamp <= 60 * timeScope:
            lastTimeMap[symbol][period] = dateStamp
            msg = "current:", symbol, period, lastSellDate, lastSellValue, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                          remark=lastSellValue)
            sendEmail(msg)

    # 监控高级别背驰
    if len(result['buyHigherMACDBCData']['date']) > 0:
        lastBuyDate = result['buyHigherMACDBCData']['date'][-1]
        lastBuyValue = result['buyHigherMACDBCData']['value'][-1]

        dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
        notLower = result['notLower']
        # print("current judge:", symbol, period, lastBuyDate, notLower)
        if lastTime != dateStamp and notLower and currentTime - dateStamp <= 60 * timeScope:
            lastTimeMap[symbol][period] = dateStamp
            msg = "current:", symbol, period, lastBuyDate, lastBuyValue, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                          remark=lastBuyValue)
            sendEmail(msg)

    if len(result['sellHigherMACDBCData']['date']) > 0:
        lastSellDate = result['sellHigherMACDBCData']['date'][-1]
        lastSellValue = result['sellHigherMACDBCData']['value'][-1]
        dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
        notHigher = result['notHigher']
        # print("current judge:", symbol, period, lastSellDate, notHigher)
        if lastTime != dateStamp and notHigher and currentTime - dateStamp <= 60 * timeScope:
            lastTimeMap[symbol][period] = dateStamp
            msg = "current:", symbol, period, lastSellDate, lastSellValue, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                          remark=lastSellValue)
            sendEmail(msg)


'''
监控回拉
'''
def monitorHuila(result, lastHuilaTime, currentTime, timeScope, lastTimeHuilaMap, symbol, period, closePrice):
    # 监控回拉
    if len(result['buy_zs_huila']['date']) > 0:
        lastBuyDate = result['buy_zs_huila']['date'][-1]
        lastBuyData = result['buy_zs_huila']['data'][-1]
        notLower = result['notLower']

        dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastBuyDate, notLower)
        if lastHuilaTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeHuilaMap[symbol][period] = dateStamp
            msg = "current:", symbol, period, 'huila B', lastBuyDate, lastBuyData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            sendEmail(msg)
            # saveStrategy4Log(symbol,period,msg,True,'拉回中枢确认底背',lastBuyData,lastBuyDate,'BuyLong')
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                          remark="huila B")

    if len(result['sell_zs_huila']['date']) > 0:
        notHigher = result['notHigher']
        lastSellDate = result['sell_zs_huila']['date'][-1]
        lastSellData = result['sell_zs_huila']['data'][-1]

        dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastSellDate, notHigher)
        if lastHuilaTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeHuilaMap[symbol][period] = dateStamp
            msg = "current:", symbol, period, 'huila T', lastSellDate, lastSellData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            # saveStrategy4Log(symbol, period, msg, True, '拉回中枢确认顶背', lastSellData, lastSellDate, 'BuyLong')
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                          remark="huila T")
            sendEmail(msg)

            # 监控高级别回拉

            if len(result['buy_zs_huila_higher']['date']) > 0:
                lastBuyDate = result['buy_zs_huila_higher']['date'][-1]
                lastBuyData = result['buy_zs_huila_higher']['data'][-1]
                notLower = result['notLower']

                dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
                # print("current judge:", symbol, period, lastBuyDate, notLower)
                if lastHuilaTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                    lastTimeHuilaMap[symbol][period] = dateStamp
                    msg = "current:", symbol, period, 'higher huila B', lastBuyDate, lastBuyData, closePrice, time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                    sendEmail(msg)
                    # saveStrategy4Log(symbol, period, msg, True, '拉回中枢确认大级别底背', lastBuyData, lastBuyDate,
                    #                  'BuyLong')
                    saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                                  remark="higher huila B")

            if len(result['sell_zs_huila_higher']['date']) > 0:
                notHigher = result['notHigher']
                lastSellDate = result['sell_zs_huila_higher']['date'][-1]
                lastSellData = result['sell_zs_huila_higher']['data'][-1]

                dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
                # print("current judge:", symbol, period, lastSellDate, notHigher)
                if lastHuilaTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                    lastTimeHuilaMap[symbol][period] = dateStamp
                    msg = "current:", symbol, period, 'higher huila T', lastSellDate, lastSellData, closePrice, time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    # saveStrategy4Log(symbol, period, msg, True, '拉回中枢确认大级别顶背', lastSellData, lastSellDate,
                    #                  'BuyLong')
                    saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                                  remark="higher huila T")
                    sendEmail(msg)


'''
监控突破
'''
def monitorTupo(result, lastTupoTime, currentTime, timeScope, lastTimeTupoMap, symbol, period, closePrice):
    # 监控突破
    if len(result['buy_zs_tupo']['date']) > 0:
        lastBuyDate = result['buy_zs_tupo']['date'][-1]
        lastBuyData = result['buy_zs_tupo']['data'][-1]
        notLower = result['notLower']

        dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastBuyDate, notLower)
        if lastTupoTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeTupoMap[symbol][period] = dateStamp
            msg = "current:", symbol, period, 'tupo B', lastBuyDate, lastBuyData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            sendEmail(msg)
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                          remark="tupo B")

    if len(result['sell_zs_tupo']['date']) > 0:
        notHigher = result['notHigher']
        lastSellDate = result['sell_zs_tupo']['date'][-1]
        lastSellData = result['sell_zs_tupo']['data'][-1]

        dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastSellDate, notHigher)
        if lastTupoTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeTupoMap[symbol][period] = dateStamp
            msg = "current:", symbol, period, 'tupo T', lastSellDate, lastSellData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                          remark="tupo T")
            sendEmail(msg)

            # 监控高级别突破

            if len(result['buy_zs_tupo_higher']['date']) > 0:
                lastBuyDate = result['buy_zs_tupo_higher']['date'][-1]
                lastBuyData = result['buy_zs_tupo_higher']['data'][-1]
                notLower = result['notLower']

                dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
                # print("current judge:", symbol, period, lastBuyDate, notLower)
                if lastTupoTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                    lastTimeTupoMap[symbol][period] = dateStamp
                    msg = "current:", symbol, period, 'higher tupo B', lastBuyDate, lastBuyData, closePrice, time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                    sendEmail(msg)
                    saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                                  remark="higher tupo B")

            if len(result['sell_zs_tupo_higher']['date']) > 0:
                notHigher = result['notHigher']
                lastSellDate = result['sell_zs_tupo_higher']['date'][-1]
                lastSellData = result['sell_zs_tupo_higher']['data'][-1]

                dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
                # print("current judge:", symbol, period, lastSellDate, notHigher)
                if lastTupoTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                    lastTimeTupoMap[symbol][period] = dateStamp
                    msg = "current:", symbol, period, 'higher tupo T', lastSellDate, lastSellData, closePrice, time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                    saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                                  remark="higher tupo T")
                    sendEmail(msg)

'''
监控3买卖 V反
'''
def monitorVreverse(result, lastVreverseTime, currentTime, timeScope, lastTimeVreverseMap, symbol, period,
                                closePrice):
    # 监控V反
    if len(result['buy_v_reverse']['date']) > 0:
        lastBuyDate = result['buy_v_reverse']['date'][-1]
        lastBuyData = result['buy_v_reverse']['data'][-1]
        notLower = result['notLower']

        dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastBuyDate, notLower)
        if lastVreverseTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeVreverseMap[symbol][period] = dateStamp
            msg = "current:", symbol, period, 'Vreverse B', lastBuyDate, lastBuyData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            sendEmail(msg)
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                          remark="Vreverse B")

    if len(result['sell_v_reverse']['date']) > 0:
        notHigher = result['notHigher']
        lastSellDate = result['sell_v_reverse']['date'][-1]
        lastSellData = result['sell_v_reverse']['data'][-1]

        dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastSellDate, notHigher)
        if lastVreverseTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeVreverseMap[symbol][period] = dateStamp
            msg = "current:", symbol, period, 'Vreverse T', lastSellDate, lastSellData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                          remark="Vreverse T")
            sendEmail(msg)

            # 监控高级别V反

            if len(result['buy_v_reverse_higher']['date']) > 0:
                lastBuyDate = result['buy_v_reverse_higher']['date'][-1]
                lastBuyData = result['buy_v_reverse_higher']['data'][-1]
                notLower = result['notLower']

                dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
                # print("current judge:", symbol, period, lastBuyDate, notLower)
                if lastVreverseTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                    lastTimeVreverseMap[symbol][period] = dateStamp
                    msg = "current:", symbol, period, 'higher Vreverse B', lastBuyDate, lastBuyData, closePrice, time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                    sendEmail(msg)
                    saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                                  remark="higher Vreverse B")

            if len(result['sell_v_reverse_higher']['date']) > 0:
                notHigher = result['notHigher']
                lastSellDate = result['sell_v_reverse_higher']['date'][-1]
                lastSellData = result['sell_v_reverse_higher']['data'][-1]

                dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
                # print("current judge:", symbol, period, lastSellDate, notHigher)
                if lastVreverseTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
                    lastTimeVreverseMap[symbol][period] = dateStamp
                    msg = "current:", symbol, period, 'higher Vreverse T', lastSellDate, lastSellData, closePrice, time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                    saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                                  remark="higher Vreverse T")
                    sendEmail(msg)


def sendEmail(msg):
    print(msg)
    mailResult = mail.send(str(msg))
    if not mailResult:
        print("发送失败")
    else:
        print("发送成功")


threading.Thread(target=monitorFuturesAndDigitCoin, args="1").start()
threading.Thread(target=monitorFuturesAndDigitCoin, args="2").start()
