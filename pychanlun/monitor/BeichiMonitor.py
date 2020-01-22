import logging
import traceback
from pychanlun.Calc import Calc
from pychanlun.KlineDataTool import KlineDataTool
import numpy as np
import pandas as pd
from numpy import array
import talib as ta
import rqdatac as rq
from datetime import datetime
from rqdatac import *
import time
import threading
from pychanlun.Mail import Mail
import pydash
from pychanlun.funcat.api import *
from pychanlun.config import config
import os
import json
from pychanlun.db import DBPyChanlun
from pychanlun.config import config

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
periodList1 = ['3m', '5m', '15m', '30m', '60m']
periodList2 = ['3m', '5m', '15m', '30m', '60m', '4h']
dominantSymbolInfoList = {}
# 账户资金
account = 19
maxAccountUseRate = 0.1
stopRate = 0.01
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
    return


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
    # 主力合约列表
    dominantSymbolList = []

    for i in range(len(symbolList)):
        df = rq.futures.get_dominant(symbolList[i], start_date=None, end_date=None, rule=0)
        dominantSymbol = df[-1]
        dominantSymbolList.append(dominantSymbol)
        dominantSymbolInfo = rq.instruments(dominantSymbol)
        dominantSymbolInfoList[dominantSymbol] = dominantSymbolInfo.__dict__
    return dominantSymbolList, dominantSymbolInfoList


# 监控期货
# timeScope 监控距离现在多少分钟的
def monitorFuturesAndDigitCoin(type):
    logger = logging.getLogger()
    timeScope = 3
    lastTimeMap = {}
    lastTimeHuilaMap = {}
    lastTimeTupoMap = {}
    lastTimeVreverseMap = {}
    lastTimeDuanBreakMap = {}

    symbolList = []
    if type == "1":
        # auth('13088887055', 'chanlun123456')
        # count = get_query_count()
        # print(count)
        init('license',
             'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
             ('rqdatad-pro.ricequant.com', 16011))
        # 主力合约，主力合约详细信息
        symbolList, dominantSymbolInfoList = getDominantSymbol()
        print("主力合约信息：", dominantSymbolInfoList)
        periodList = periodList1
    else:
        symbolList = symbolListDigitCoin
        periodList = periodList1

    for i in range(len(symbolList)):
        symbol = symbolList[i]
        lastTimeMap[symbol] = {}
        lastTimeHuilaMap[symbol] = {}
        lastTimeTupoMap[symbol] = {}
        lastTimeVreverseMap[symbol] = {}
        lastTimeDuanBreakMap[symbol] = {}

        for j in range(len(periodList)):
            period = periodList[j]
            lastTimeMap[symbol][period] = 0
            lastTimeHuilaMap[symbol][period] = 0
            lastTimeTupoMap[symbol][period] = 0
            lastTimeVreverseMap[symbol][period] = 0
            lastTimeDuanBreakMap[symbol][period] = 0
    print(lastTimeMap)
    print(lastTimeHuilaMap)
    print(lastTimeTupoMap)
    print(lastTimeVreverseMap)
    print(lastTimeDuanBreakMap)
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
                    lastDuanBreakTime = lastTimeDuanBreakMap[symbol][period]

                    diffTime = currentTime - lastTime
                    print("current:", symbol, period, datetime.now())
                    result = calc.calcData(period, symbol)
                    closePrice = result['close'][-1]
                    # 暂停macd背驰的监控，全部基于新战法
                    # monitorBeichi(result, lastTime, currentTime, timeScope, lastTimeMap, symbol, period, closePrice)
                    monitorHuila(result, lastHuilaTime, currentTime, timeScope, lastTimeHuilaMap, symbol, period,
                                 closePrice)
                    monitorTupo(result, lastTupoTime, currentTime, timeScope, lastTimeTupoMap, symbol, period,
                                closePrice)
                    monitorVreverse(result, lastVreverseTime, currentTime, timeScope, lastTimeVreverseMap, symbol,
                                    period,
                                    closePrice)
                    monitorDuanBreak(result, lastDuanBreakTime, currentTime, timeScope, lastTimeDuanBreakMap,
                                     symbol, period, closePrice)
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
            msg = symbol, period, lastBuyDate, lastBuyValue, closePrice, time.strftime(
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
            msg = symbol, period, lastSellDate, lastSellValue, closePrice, time.strftime(
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
            msg = symbol, period, lastBuyDate, lastBuyValue, closePrice, time.strftime(
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
            msg = symbol, period, lastSellDate, lastSellValue, closePrice, time.strftime(
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
        stop_lose_price = result['buy_zs_huila']['stop_lose_price'][-1]
        notLower = result['notLower']

        dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastBuyDate, notLower)
        if lastHuilaTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeHuilaMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)
            msg = symbol, period, 'huila B ', maxOrderCount, lastBuyDate, lastBuyData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            if maxOrderCount >= 1:
                sendEmail(msg)
            # saveStrategy4Log(symbol,period,msg,True,'拉回中枢确认底背',lastBuyData,lastBuyDate,'BuyLong')
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                          remark="huila B")

    if len(result['sell_zs_huila']['date']) > 0:
        notHigher = result['notHigher']
        lastSellDate = result['sell_zs_huila']['date'][-1]
        lastSellData = result['sell_zs_huila']['data'][-1]
        stop_lose_price = result['sell_zs_huila']['stop_lose_price'][-1]

        dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastSellDate, notHigher)
        if lastHuilaTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeHuilaMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)
            msg = symbol, period, 'huila S ', maxOrderCount, lastSellDate, lastSellData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            # saveStrategy4Log(symbol, period, msg, True, '拉回中枢确认顶背', lastSellData, lastSellDate, 'BuyLong')
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                          remark="huila S")
            if maxOrderCount >= 1:
                sendEmail(msg)

    # 监控高级别回拉

    if len(result['buy_zs_huila_higher']['date']) > 0:
        lastBuyDate = result['buy_zs_huila_higher']['date'][-1]
        lastBuyData = result['buy_zs_huila_higher']['data'][-1]
        stop_lose_price = result['buy_zs_huila_higher']['stop_lose_price'][-1]

        notLower = result['notLower']

        dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastBuyDate, notLower)
        if lastHuilaTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeHuilaMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)
            msg = symbol, period, 'higher huila B ', maxOrderCount, lastBuyDate, lastBuyData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            if maxOrderCount >= 1:
                sendEmail(msg)
            # saveStrategy4Log(symbol, period, msg, True, '拉回中枢确认大级别底背', lastBuyData, lastBuyDate,
            #                  'BuyLong')
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                          remark="higher huila B")

    if len(result['sell_zs_huila_higher']['date']) > 0:
        notHigher = result['notHigher']
        lastSellDate = result['sell_zs_huila_higher']['date'][-1]
        lastSellData = result['sell_zs_huila_higher']['data'][-1]
        stop_lose_price = result['sell_zs_huila_higher']['stop_lose_price'][-1]

        dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastSellDate, notHigher)
        if lastHuilaTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeHuilaMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)

            msg = symbol, period, 'higher huila S ', maxOrderCount, lastSellDate, lastSellData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            # saveStrategy4Log(symbol, period, msg, True, '拉回中枢确认大级别顶背', lastSellData, lastSellDate,
            #                  'BuyLong')
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                          remark="higher huila S")
            if maxOrderCount >= 1:
                sendEmail(msg)


'''
监控突破
'''


def monitorTupo(result, lastTupoTime, currentTime, timeScope, lastTimeTupoMap, symbol, period, closePrice):
    # 监控突破
    if len(result['buy_zs_tupo']['date']) > 0:
        lastBuyDate = result['buy_zs_tupo']['date'][-1]
        lastBuyData = result['buy_zs_tupo']['data'][-1]
        stop_lose_price = result['buy_zs_tupo']['stop_lose_price'][-1]
        notLower = result['notLower']

        dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastBuyDate, notLower)
        if lastTupoTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeTupoMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)
            msg = symbol, period, 'tupo B ', maxOrderCount, lastBuyDate, lastBuyData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            if maxOrderCount >= 1:
                sendEmail(msg)
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                          remark="tupo B")

    if len(result['sell_zs_tupo']['date']) > 0:
        notHigher = result['notHigher']
        lastSellDate = result['sell_zs_tupo']['date'][-1]
        lastSellData = result['sell_zs_tupo']['data'][-1]
        stop_lose_price = result['sell_zs_tupo']['stop_lose_price'][-1]
        dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastSellDate, notHigher)
        if lastTupoTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeTupoMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)
            msg = symbol, period, 'tupo S ', maxOrderCount, lastSellDate, lastSellData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                          remark="tupo S")
            if maxOrderCount >= 1:
                sendEmail(msg)

    # 监控高级别突破

    if len(result['buy_zs_tupo_higher']['date']) > 0:
        lastBuyDate = result['buy_zs_tupo_higher']['date'][-1]
        lastBuyData = result['buy_zs_tupo_higher']['data'][-1]
        stop_lose_price = result['buy_zs_tupo_higher']['stop_lose_price'][-1]
        notLower = result['notLower']

        dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastBuyDate, notLower)
        if lastTupoTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeTupoMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)

            msg = symbol, period, 'higher tupo B ', maxOrderCount, lastBuyDate, lastBuyData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            if maxOrderCount >= 1:
                sendEmail(msg)
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                          remark="higher tupo B")

    if len(result['sell_zs_tupo_higher']['date']) > 0:
        notHigher = result['notHigher']
        lastSellDate = result['sell_zs_tupo_higher']['date'][-1]
        lastSellData = result['sell_zs_tupo_higher']['data'][-1]
        stop_lose_price = result['sell_zs_tupo_higher']['stop_lose_price'][-1]

        dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastSellDate, notHigher)
        if lastTupoTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeTupoMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)
            msg = symbol, period, 'higher tupo S ', maxOrderCount,lastSellDate, lastSellData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                          remark="higher tupo S")
            if maxOrderCount >= 1:
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
        stop_lose_price = result['buy_v_reverse']['stop_lose_price'][-1]

        notLower = result['notLower']

        dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastBuyDate, notLower)
        if lastVreverseTime != dateStamp and currentTime - dateStamp <= 60 * timeScope * 10:
            lastTimeVreverseMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)
            msg = symbol, period, 'Vreverse B ', maxOrderCount, lastBuyDate, lastBuyData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            sendEmail(msg)
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                          remark="Vreverse B")

    if len(result['sell_v_reverse']['date']) > 0:
        notHigher = result['notHigher']
        lastSellDate = result['sell_v_reverse']['date'][-1]
        lastSellData = result['sell_v_reverse']['data'][-1]
        stop_lose_price = result['sell_v_reverse']['stop_lose_price'][-1]

        dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastSellDate, notHigher)
        if lastVreverseTime != dateStamp and currentTime - dateStamp <= 60 * timeScope * 10:
            lastTimeVreverseMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)

            msg = symbol, period, 'Vreverse S ',maxOrderCount, lastSellDate, lastSellData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                          remark="Vreverse S")
            sendEmail(msg)

    # 监控高级别V反

    if len(result['buy_v_reverse_higher']['date']) > 0:
        lastBuyDate = result['buy_v_reverse_higher']['date'][-1]
        lastBuyData = result['buy_v_reverse_higher']['data'][-1]
        stop_lose_price = result['buy_v_reverse_higher']['stop_lose_price'][-1]
        notLower = result['notLower']

        dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastBuyDate, notLower)
        if lastVreverseTime != dateStamp and currentTime - dateStamp <= 60 * timeScope * 2:
            lastTimeVreverseMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)

            msg = symbol, period, 'higher Vreverse B ', maxOrderCount,lastBuyDate, lastBuyData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            sendEmail(msg)
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                          remark="higher Vreverse B")

    if len(result['sell_v_reverse_higher']['date']) > 0:
        notHigher = result['notHigher']
        lastSellDate = result['sell_v_reverse_higher']['date'][-1]
        lastSellData = result['sell_v_reverse_higher']['data'][-1]
        stop_lose_price = result['sell_v_reverse_higher']['stop_lose_price'][-1]

        dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastSellDate, notHigher)
        if lastVreverseTime != dateStamp and currentTime - dateStamp <= 60 * timeScope * 2:
            lastTimeVreverseMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)

            msg = symbol, period, 'higher Vreverse S ',maxOrderCount, lastSellDate, lastSellData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                          remark="higher Vreverse S")
            sendEmail(msg)


'''
监控 线段破坏
'''


def monitorDuanBreak(result, lastDuanBreakTime, currentTime, timeScope, lastTimeDuanBreakMap, symbol, period,
                     closePrice):
    # 监控线段破坏
    if len(result['buy_duan_break']['date']) > 0:
        lastBuyDate = result['buy_duan_break']['date'][-1]
        lastBuyData = result['buy_duan_break']['data'][-1]
        stop_lose_price = result['buy_duan_break']['stop_lose_price'][-1]
        notLower = result['notLower']

        dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastBuyDate, notLower)
        if lastDuanBreakTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeDuanBreakMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)
            msg = symbol, period, 'break B ', maxOrderCount, lastBuyDate, lastBuyData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            if maxOrderCount >= 1:
                sendEmail(msg)
            # saveStrategy4Log(symbol,period,msg,True,'拉回中枢确认底背',lastBuyData,lastBuyDate,'BuyLong')
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                          remark="break B")

    if len(result['sell_duan_break']['date']) > 0:
        notHigher = result['notHigher']
        lastSellDate = result['sell_duan_break']['date'][-1]
        lastSellData = result['sell_duan_break']['data'][-1]
        stop_lose_price = result['sell_duan_break']['stop_lose_price'][-1]

        dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastSellDate, notHigher)
        if lastDuanBreakTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeDuanBreakMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)
            msg = symbol, period, 'break S ', maxOrderCount, lastSellDate, lastSellData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            # saveStrategy4Log(symbol, period, msg, True, '拉回中枢确认顶背', lastSellData, lastSellDate, 'BuyLong')
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                          remark="break S")
            if maxOrderCount >= 1:
                sendEmail(msg)

    # 监控高级别线段破坏

    if len(result['buy_duan_break_higher']['date']) > 0:
        lastBuyDate = result['buy_duan_break_higher']['date'][-1]
        lastBuyData = result['buy_duan_break_higher']['data'][-1]
        stop_lose_price = result['buy_duan_break_higher']['stop_lose_price'][-1]

        notLower = result['notLower']

        dateStamp = int(time.mktime(time.strptime(lastBuyDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastBuyDate, notLower)
        if lastDuanBreakTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeDuanBreakMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)
            msg = symbol, period, 'higher break B ', maxOrderCount, lastBuyDate, lastBuyData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            if maxOrderCount >= 1:
                sendEmail(msg)
            # saveStrategy4Log(symbol, period, msg, True, '拉回中枢确认大级别底背', lastBuyData, lastBuyDate,
            #                  'BuyLong')
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notLower,
                          remark="higher break B")

    if len(result['sell_duan_break_higher']['date']) > 0:
        notHigher = result['notHigher']
        lastSellDate = result['sell_duan_break_higher']['date'][-1]
        lastSellData = result['sell_duan_break_higher']['data'][-1]
        stop_lose_price = result['sell_duan_break_higher']['stop_lose_price'][-1]

        dateStamp = int(time.mktime(time.strptime(lastSellDate, "%Y-%m-%d %H:%M")))
        # print("current judge:", symbol, period, lastSellDate, notHigher)
        if lastDuanBreakTime != dateStamp and currentTime - dateStamp <= 60 * timeScope:
            lastTimeDuanBreakMap[symbol][period] = dateStamp
            maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price)

            msg = symbol, period, 'higher break S ', maxOrderCount, lastSellDate, lastSellData, closePrice, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            # saveStrategy4Log(symbol, period, msg, True, '拉回中枢确认大级别顶背', lastSellData, lastSellDate,
            #                  'BuyLong')
            saveBeichiLog(symbol=symbol, period=period, price=closePrice, signal=notHigher,
                          remark="higher break S")
            if maxOrderCount >= 1:
                sendEmail(msg)


def sendEmail(msg):
    print(msg)
    mailResult = mail.send(str(msg))
    if not mailResult:
        print("发送失败")
    else:
        print("发送成功")


# 计算出开仓手数（止损系数，资金使用率双控）
def calMaxOrderCount(dominantSymbol, openPrice, stopPrice):
    margin_rate = dominantSymbolInfoList[dominantSymbol]['margin_rate']
    contract_multiplier = dominantSymbolInfoList[dominantSymbol]['contract_multiplier']

    # 计算最大能使用的资金
    maxAccountUse = account * 10000 * maxAccountUseRate
    # 计算最大止损金额
    maxStopMoney = account * 10000 * stopRate
    # 计算1手需要的保证金
    perOrderMargin = int(openPrice * contract_multiplier * margin_rate)

    # 1手止损的金额
    perOrderStopMoney = abs(openPrice - stopPrice) * contract_multiplier
    # 1手止损的百分比
    perOrderStopRate = round((perOrderStopMoney / perOrderMargin), 2)

    # 根据止损算出的开仓手数(四舍五入)
    maxOrderCount1 = round(maxStopMoney / perOrderStopMoney)

    # 根据最大资金使用率算出的开仓手数(四舍五入)
    maxOrderCount2 = round(maxAccountUse / perOrderMargin)
    maxOrderCount = maxOrderCount2 if maxOrderCount1 > maxOrderCount2 else maxOrderCount1
    return maxOrderCount


threading.Thread(target=monitorFuturesAndDigitCoin, args="1").start()
# threading.Thread(target=monitorFuturesAndDigitCoin, args="2").start()
