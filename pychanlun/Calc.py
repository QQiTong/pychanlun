# -*- coding: utf-8 -*-

import json
import os
import time
import numpy as np
import pandas as pd
import codecs

from numpy import array
import talib as ta
from flask import make_response
import copy
import pydash
from datetime import datetime

from pychanlun.basic.bi import CalcBi
from pychanlun.basic.duan import CalcDuan
from pychanlun import Duan
from pychanlun.KlineDataTool import KlineDataTool
from pychanlun.Tools import Tools
import pychanlun.divergence as divergence
import pychanlun.entanglement as entanglement
from pychanlun.basic.pattern import DualEntangleForBuyLong, DualEntangleForSellShort

# 币安的数据结构
# [
#     [
#         1499040000000,      # Open time
#         "0.01634790",       # Open
#         "0.80000000",       # High
#         "0.01575800",       # Low
#         "0.01577100",       # Close
#         "148976.11427815",  # Volume
#         1499644799999,      # Close time
#         "2434.19055334",    # Quote asset volume
#         308,                # Number of trades
#         "1756.87402397",    # Taker buy base asset volume
#         "28.46694368",      # Taker buy quote asset volume
#         "17928899.62484339" # Ignore.
#     ]
# ]
'''
火币数据结构
{
    amount: 133.9523230990729,
    close: 8858.25,
    count: 168,
    high: 8860.01,
    id: 1560609600,
    low: 8842.35,
    open: 8859.96,
    vol: 11862
}
'''


class Calc:
    def __init__(self):
        # 火币dm接口参数 本级别和大级别映射
        # 火币深度不够,无法容纳大资金
        self.levelMap = {
            '1m': '5m',
            '3m': '15m',
            '15m': '60m',
            '60m': '1d',
            '1d': '1w',
            '5m': '30m',
            '30m': '240m',
            '240m': '1w',
            # '1w': '1w'
        }

        self.huobiPeriodMap = {
            '1m': '1min',
            # 火币没有提供3min的数据 需要合成
            '3m': '3m',
            '5m': '5min',
            '15m': '15min',
            '60m': '60min',

            '30m': '30min',
            '240m': '4hour',
            '1d': '1day',
            '1w': '1week'
        }

        # bitmex 小级别大级别映射
        # self.levelMap = {
        #     '1min': '5min',
        #     '3min': '15min',
        #     '15min': '60min',
        #     '60min': '1day',
        #     '1day': '1week',
        #     '5min': '30min',
        #     '30min': '4hour',
        #     '4hour': '1week',
        #     '1week': '1week'
        # }
        #  bitmex 参数转换
        # self.bitmexPeriodMap = {
        #     '1min': '1m',
        #     '3min': '3m',
        #     '15min': '15m',
        #     '60min': '60m',
        #     '1day': '1d',
        #     '5min': '5m',
        #     '30min': '30m',
        #     '4hour': '240m',
        #     '1week': '7d'
        # }

        # 聚宽期货接口参数 本级别和大级别映射
        self.futureLevelMap = {
            '1m': '5m',
            '3m': '15m',
            '15m': '60m',
            '60m': '1d',
            '1d': '3d',
            '5m': '30m',
            '30m': '240m',
            '240m': '3d',
            '3d': '3d',  # 周线数量只有33根画不出macd 只好取3d了
        }
        #     period参数转换
        self.periodMap = {
            '1m': '1m',
            '3m': '3m',
            '15m': '15m',
            '60m': '60m',
            '1d': '1d',
            '5m': '5m',
            '30m': '30m',
            '240m': '240m',
            '1w': '1w'
        }

    def calcData(self, period, symbol, save=False,endDate=None):
        start = time.clock()  # 开始计时
        # 统计程序执行时间

        klineList = []

        # def processKline():
        #     count = len(highList)
        #     for i in range(count):
        #         add(highList[i], lowList[i], timeList[i])

        # 获取接口数据
        klineDataTool = KlineDataTool()
        if '_CQ' in symbol:
            klineData = klineDataTool.getDigitCoinData(symbol, self.huobiPeriodMap[period])
            # klineDataBigLevel = klineDataTool.getDigitCoinData(symbol, self.huobiPeriodMap[self.levelMap[period]])
            # klineDataBigLevel = pydash.filter_(klineDataBigLevel,
            #                                    lambda klineItem: klineItem['time'] >= klineData[0]['time'])
        else:
            # 期货
            currentPeriod = self.periodMap[period]
            klineData = klineDataTool.getFutureData(symbol, currentPeriod, endDate)
            # bigLevelPeriod = self.futureLevelMap[currentPeriod]
            # klineDataBigLevel = klineDataTool.getFutureData(symbol, bigLevelPeriod, 1000)
            # klineDataBigLevel = pydash.filter_(klineDataBigLevel,
            #                                    lambda klineItem: klineItem['time'] >= klineData[0]['time'])
        # print("从接口到的数据", klineData)
        # 存数据快照，调试时候用
        if save:
            base_dir = os.path.dirname(__file__)
            with codecs.open(os.path.join(base_dir, 'klineData.json'), 'w', encoding='utf-8') as f:
                json_str = json.dumps(klineData, ensure_ascii=False, indent=4)
                f.write(json_str)
            # with codecs.open(os.path.join(base_dir, 'klineDataBigLevel.json'), 'w', encoding='utf-8') as f:
            #     json_str = json.dumps(klineDataBigLevel, ensure_ascii=False, indent=4)
            #     f.write(json_str)

        # 读入本都数据
        # flask 读入本地文件需要这样写
        # base_dir = os.path.dirname(__file__)
        # print(base_dir)
        # with codecs.open(os.path.join(base_dir, 'klineData.json'), encoding='utf-8') as f:
        #     klineData = json.load(f)
        # with codecs.open(os.path.join(base_dir, 'klineDataBigLevel.json'), encoding='utf-8') as f:
        #     klineDataBigLevel = json.load(f)

        jsonObj = klineData
        # jsonObjBigLevel = klineDataBigLevel

        openPriceList = []
        highList = []
        lowList = []
        closePriceList = []
        timeList = []
        volumeList = []

        # 获取大级别macd
        closeListBigLevel = []
        timeListBigLevel = []

        # for i in range(len(jsonObjBigLevel)):
        #     item = jsonObjBigLevel[i]
        #     closeListBigLevel.append(round(float(item['close']), 2))
        #     localTime = time.localtime(item['time'])
        #     strTime = time.strftime("%Y-%m-%d %H:%M", localTime)
        #     timeListBigLevel.append(strTime)

        for i in range(len(jsonObj)):
            item = jsonObj[i]
            localTime = time.localtime(item['time'])
            strTime = time.strftime("%Y-%m-%d %H:%M", localTime)
            highList.append(round(float(item['high']), 2))
            lowList.append(round(float(item['low']), 2))

            openPriceList.append(round(float(item['open']), 2))
            closePriceList.append(round(float(item['close']), 2))
            timeList.append(strTime)
            volumeList.append(round(float(item['volume']), 2))

        count = len(timeList)
        # 笔结果
        biList = [0 for i in range(count)]
        CalcBi(count, biList, highList, lowList, openPriceList, closePriceList)

        # 段处理
        duanList = [0 for i in range(count)]
        CalcDuan(count, duanList, biList, highList, lowList)

        # 高一级别段处理
        higherDuanList = [0 for i in range(count)]
        CalcDuan(count, higherDuanList, duanList, highList, lowList)

        # 高高一级别段处理
        higherHigherDuanList = [0 for i in range(count)]
        CalcDuan(count, higherHigherDuanList, higherDuanList, highList, lowList)

        # print("段结果:", len(biResult), len(duanResult))
        entanglementList = entanglement.CalcEntanglements(timeList, duanList, biList, highList, lowList)
        huila = entanglement.la_hui(entanglementList, timeList, highList, lowList, openPriceList, closePriceList, biList, duanList)
        tupo = entanglement.tu_po(entanglementList, timeList, highList, lowList, openPriceList, closePriceList, biList, duanList)
        v_reverse = entanglement.v_reverse(entanglementList, timeList, highList, lowList, openPriceList, closePriceList, biList, duanList)
        duan_pohuai = entanglement.po_huai(timeList, highList, lowList, openPriceList, closePriceList, biList, duanList)
        # 段中枢
        entanglementHigherList = entanglement.CalcEntanglements(timeList, higherDuanList, duanList, highList, lowList)
        huila_higher = entanglement.la_hui(entanglementHigherList, timeList, highList, lowList, openPriceList, closePriceList, duanList, higherDuanList)
        tupo_higher = entanglement.tu_po(entanglementHigherList, timeList, highList, lowList, openPriceList, closePriceList, duanList, higherDuanList)
        v_reverse_higher = entanglement.v_reverse(entanglementHigherList, timeList, highList, lowList, openPriceList, closePriceList, duanList, higherDuanList)
        duan_pohuai_higher = entanglement.po_huai(timeList, highList, lowList, openPriceList, closePriceList, duanList, higherDuanList)

        # 计算是不是双盘结构
        for idx in range(len(huila["sell_zs_huila"]["date"])):
            fire_time = huila["sell_zs_huila"]["date"][idx]
            fire_price = huila["sell_zs_huila"]["data"][idx]
            if DualEntangleForSellShort(duanList, entanglementList, entanglementHigherList, fire_time, fire_price):
                huila["sell_zs_huila"]["tag"][idx] = "双盘"
        for idx in range(len(huila["buy_zs_huila"]["date"])):
            fire_time = huila["buy_zs_huila"]["date"][idx]
            fire_price = huila["buy_zs_huila"]["data"][idx]
            if DualEntangleForBuyLong(duanList, entanglementList, entanglementHigherList, fire_time, fire_price):
                huila["buy_zs_huila"]["tag"][idx] = "双盘"
        for idx in range(len(tupo["sell_zs_tupo"]["date"])):
            fire_time = tupo["sell_zs_tupo"]["date"][idx]
            fire_price = tupo["sell_zs_tupo"]["data"][idx]
            if DualEntangleForSellShort(duanList, entanglementList, entanglementHigherList, fire_time, fire_price):
                tupo["sell_zs_tupo"]["tag"][idx] = "双盘"
        for idx in range(len(tupo["buy_zs_tupo"]["date"])):
            fire_time = tupo["buy_zs_tupo"]["date"][idx]
            fire_price = tupo["buy_zs_tupo"]["data"][idx]
            if DualEntangleForBuyLong(duanList, entanglementList, entanglementHigherList, fire_time, fire_price):
                tupo["buy_zs_tupo"]["tag"][idx] = "双盘"
        for idx in range(len(v_reverse["sell_v_reverse"]["date"])):
            fire_time = v_reverse["sell_v_reverse"]["date"][idx]
            fire_price = v_reverse["sell_v_reverse"]["data"][idx]
            if DualEntangleForSellShort(duanList, entanglementList, entanglementHigherList, fire_time, fire_price):
                v_reverse["sell_v_reverse"]["tag"][idx] = "双盘"
        for idx in range(len(v_reverse["buy_v_reverse"]["date"])):
            fire_time = v_reverse["buy_v_reverse"]["date"][idx]
            fire_price = v_reverse["buy_v_reverse"]["data"][idx]
            if DualEntangleForBuyLong(duanList, entanglementList, entanglementHigherList, fire_time, fire_price):
                v_reverse["buy_v_reverse"]["tag"][idx] = "双盘"
        for idx in range(len(duan_pohuai["sell_duan_break"]["date"])):
            fire_time = duan_pohuai["sell_duan_break"]["date"][idx]
            fire_price = duan_pohuai["sell_duan_break"]["data"][idx]
            if DualEntangleForSellShort(duanList, entanglementList, entanglementHigherList, fire_time, fire_price):
                duan_pohuai["sell_duan_break"]["tag"][idx] = "双盘"
        for idx in range(len(duan_pohuai["buy_duan_break"]["date"])):
            fire_time = duan_pohuai["buy_duan_break"]["date"][idx]
            fire_price = duan_pohuai["buy_duan_break"]["data"][idx]
            if DualEntangleForBuyLong(duanList, entanglementList, entanglementHigherList, fire_time, fire_price):
                duan_pohuai["buy_duan_break"]["tag"][idx] = "双盘"

        # 高级别段中枢
        entanglementHigherHigherList = entanglement.CalcEntanglements(timeList, higherHigherDuanList, higherDuanList, highList, lowList)

        zsdata, zsflag = getZhongShuData(entanglementList)
        duan_zsdata, duan_zsflag = getZhongShuData(entanglementHigherList)
        higher_duan_zsdata, higher_duan_zsflag = getZhongShuData(entanglementHigherHigherList)
        # print("中枢数据:", zsdata, zsflag)

        # 拼接json数据
        resJson = {}
        # 时间
        resJson['date'] = timeList
        resJson['open'] = openPriceList
        resJson['high'] = highList
        resJson['low'] = lowList
        resJson['close'] = closePriceList

        resJson['bidata'] = getLineData(timeList, biList, highList, lowList)
        resJson['duandata'] = getLineData(timeList, duanList, highList, lowList)

        resJson['higherDuanData'] = getLineData(timeList, higherDuanList, highList, lowList)
        resJson['higherHigherDuanData'] = getLineData(timeList, higherHigherDuanList, highList, lowList)

        # resJson['diff'] = getMacd(closePriceList)[0].tolist()
        # resJson['dea'] = getMacd(closePriceList)[1].tolist()
        # resJson['macd'] = getMacd(closePriceList)[2].tolist()
        # resJson['macdAreaData'] = calcArea(resJson['diff'], resJson['macd'], timeList)
        # resJson['boll_up'] = getBoll(closePriceList)[0].tolist()
        # resJson['boll_middle'] = getBoll(closePriceList)[1].tolist()
        # resJson['boll_bottom'] = getBoll(closePriceList)[2].tolist()
        # resJson['ama'] = getAma(closePriceList).tolist()
        resJson['volume'] = volumeList
        resJson['zsdata'] = zsdata
        resJson['zsflag'] = zsflag
        resJson['duan_zsdata'] = duan_zsdata
        resJson['duan_zsflag'] = duan_zsflag
        resJson['higher_duan_zsdata'] = higher_duan_zsdata
        resJson['higher_duan_zsflag'] = higher_duan_zsflag

        # 获取大级别macd
        # resJson['diffBigLevel'] = getMacd(closeListBigLevel)[0].tolist()
        # resJson['deaBigLevel'] = getMacd(closeListBigLevel)[1].tolist()
        # resJson['macdBigLevel'] = getMacd(closeListBigLevel)[2].tolist()
        # resJson['dateBigLevel'] = timeListBigLevel

        # diffList = resJson['diff']
        # deaList = resJson['dea']
        # macdList = resJson['macd']

        # 背驰计算
        time_array = np.array(timeList)
        # macd_array = np.array(macdList)
        # diff_array = np.array(diffList)
        # dea_array = np.array(deaList)
        # high_array = np.array(highList)
        # low_array = np.array(lowList)
        # open_array = np.array(openPriceList)
        # close_array = np.array(closePriceList)
        # beichiData = divergence.calcAndNote(time_array, high_array, low_array, open_array, close_array, macd_array, diff_array, dea_array, biProcess.biList, biResult, duanResult)
        # beichiData2 = divergence.calcAndNote(time_array, high_array, low_array, open_array, close_array, macd_array, diff_array, dea_array, biProcess.biList, biResult, higherDuanResult, True)
        # buyMACDBCData = beichiData['buyMACDBCData']
        # sellMACDBCData = beichiData['sellMACDBCData']
        # buyMACDBCData2 = beichiData2['buyMACDBCData']
        # sellMACDBCData2 = beichiData2['sellMACDBCData']

        # buyHigherMACDBCData = {}
        # buyHigherMACDBCData['date'] = []
        # buyHigherMACDBCData['data'] = []
        # buyHigherMACDBCData['value'] = []
        #
        # sellHigherMACDBCData = {}
        # sellHigherMACDBCData['date'] = []
        # sellHigherMACDBCData['data'] = []
        # sellHigherMACDBCData['value'] = []

        # strategy3计算
        resJson['notLower'] = calcNotLower(duanList, lowList)
        resJson['notHigher'] = calcNotHigher(duanList, highList)
        # for x in range(len(buyMACDBCData2['date'])):
        #     if pydash.find_index(buyMACDBCData['date'], lambda t: t == buyMACDBCData2['date'][x]) == -1:
        #         buyHigherMACDBCData['date'].append(buyMACDBCData2['date'][x])
        #         buyHigherMACDBCData['data'].append(buyMACDBCData2['data'][x])
        #         buyHigherMACDBCData['value'].append(buyMACDBCData2['value'][x])
        # for x in range(len(sellMACDBCData2['date'])):
        #     if pydash.find_index(sellMACDBCData['date'], lambda t: t == sellMACDBCData2['date'][x]) == -1:
        #         sellHigherMACDBCData['date'].append(sellMACDBCData2['date'][x])
        #         sellHigherMACDBCData['data'].append(sellMACDBCData2['data'][x])
        #         sellHigherMACDBCData['value'].append(sellMACDBCData2['value'][x])
        # resJson['buyMACDBCData'] = buyMACDBCData
        # resJson['sellMACDBCData'] = sellMACDBCData
        #
        # resJson['buyHigherMACDBCData'] = buyMACDBCData2
        # resJson['sellHigherMACDBCData'] = sellMACDBCData2

        resJson['buy_zs_huila'] = huila['buy_zs_huila']
        resJson['sell_zs_huila'] =huila['sell_zs_huila']
        resJson['buy_zs_huila_higher'] = huila_higher['buy_zs_huila']
        resJson['sell_zs_huila_higher'] =huila_higher['sell_zs_huila']

        resJson['buy_zs_tupo'] = tupo['buy_zs_tupo']
        resJson['sell_zs_tupo'] = tupo['sell_zs_tupo']
        resJson['buy_zs_tupo_higher'] = tupo_higher['buy_zs_tupo']
        resJson['sell_zs_tupo_higher'] = tupo_higher['sell_zs_tupo']

        resJson['buy_v_reverse'] = v_reverse['buy_v_reverse']
        resJson['sell_v_reverse'] = v_reverse['sell_v_reverse']
        resJson['buy_v_reverse_higher'] = v_reverse_higher['buy_v_reverse']
        resJson['sell_v_reverse_higher'] = v_reverse_higher['sell_v_reverse']

        resJson['buy_duan_break'] = duan_pohuai['buy_duan_break']
        resJson['sell_duan_break'] = duan_pohuai['sell_duan_break']
        resJson['buy_duan_break_higher'] = duan_pohuai_higher['buy_duan_break']
        resJson['sell_duan_break_higher'] = duan_pohuai_higher['sell_duan_break']

        resJsonStr = json.dumps(resJson)
        # print(resJsonStr)

        elapsed = (time.clock() - start)  # 结束计时
        print("程序执行的时间:" + str(elapsed) + "s")  # 印出时间
        return resJson


def getLineData(timeList, signalList, highList, lowList):
    res = {
        'data': [],
        'date': []
    }
    for i in range(0, len(timeList), 1):
        if signalList[i] == 1:
            res['data'].append(highList[i])
            res['date'].append(timeList[i])
        elif signalList[i] == -1:
            res['data'].append(lowList[i])
            res['date'].append(timeList[i])
    return res

def getZhongShuData(entanglementList):
    zsdata = []
    zsflag = []
    for i in range(len(entanglementList)):
        e = entanglementList[i]
        if e.direction == -1:
            zsflag.append(-1)
            zsdata.append([[e.startTime, e.top], [e.endTime, e.bottom]])
        else:
            zsflag.append(1)
            zsdata.append([[e.startTime, e.bottom], [e.endTime, e.top]])
    return zsdata, zsflag


# def getZhongShuData(zhongShuHigh, zhongShuLow, zhongShuStartEnd, timeList):
#     zsdata = []
#     zsStart = []
#     zsEnd = []
#     zsflag = []
#     for i in range(len(zhongShuStartEnd)):
#         item = zhongShuStartEnd[i]
#         if item == 0:
#             continue
#         if item == 1:
#             # print("中枢起点:", i, zhongShuHigh[i], zhongShuLow[i], zhongShuStartEnd[i])
#             zsStart = [timeList[i], zhongShuLow[i]]
#         elif item == 2:
#             # print("中枢终点:", i, zhongShuHigh[i], zhongShuLow[i], zhongShuStartEnd[i])
#             zsEnd = [timeList[i], zhongShuHigh[i]]
#         if len(zsStart) and len(zsEnd):
#             zsItem = [copy.copy(zsStart), copy.copy(zsEnd)]
#             # print("中枢拼接:", zsItem)
#             zsdata.append(copy.copy(zsItem))
#             if zsStart[1] > zsEnd[1]:
#                 zsflag.append(-1)
#             else:
#                 zsflag.append(1)
#             zsStart.clear()
#             zsEnd.clear()
#             zsItem.clear()

#     return zsdata, zsflag


def getMacd(closePriceList):
    close = array(closePriceList)
    macd = ta.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    result = np.nan_to_num(macd)
    return result


def getBoll(closePriceList):
    close = array(closePriceList)
    boll = ta.BBANDS(close, 20, 2)
    result = np.nan_to_num(boll)
    return result


def getAma(closePriceList):
    close = array(closePriceList)
    ama = ta.KAMA(close)
    result = np.nan_to_num(ama)
    return result


def calcNotLower(duanList, lowList):
    if Duan.notLower(duanList, lowList):
        macdPos = ""
        # if macd15m[-1] >= 0:
        #     macdPos = "大级别MACD零轴上"
        # else:
        #     macdPos = "大级别MACD零轴下"
        # msg = 'XB-3', symbol, period
        return True
    else:
        return False


def calcNotHigher(duanList, highList):
    if Duan.notHigher(duanList, highList):
        macdPos = ""
        # if macd15m[-1] >= 0:
        #     macdPos = "大级别MACD零轴上"
        # else:
        #     macdPos = "大级别MACD零轴下"
        # msg = 'XB-3', symbol, period
        return True
    else:
        return False


#     计算macd面积
def calcArea(diff, macd, timeList):
    # 1 : 0轴上方 -1 零轴下方
    currentFlag = 1
    upSum = 0
    downSum = 0

    macdAreaList = {
        # 保存面积的值
        'date': [],
        # 保存dif
        'data': [],
        # 保存时间
        'value': []
    }

    for i in range(len(macd)):
        # 如果少于33根 的值
        if i < 33:
            continue
        # 0轴上方
        if macd[i] > 0:
            if currentFlag == -1:
                macdAreaList['value'].append(downSum)
                macdAreaList['data'].append(round(diff[i],2))
                macdAreaList['date'].append(timeList[i])
                downSum = 0
                currentFlag = 1
            upSum = round(upSum + macd[i]*100)
        else:
            if currentFlag == 1:
                macdAreaList['value'].append(upSum)
                macdAreaList['data'].append(round(diff[i],2))
                macdAreaList['date'].append(timeList[i])
                upSum = 0
                currentFlag = -1
            downSum = round(downSum + macd[i]*100)
    return macdAreaList
