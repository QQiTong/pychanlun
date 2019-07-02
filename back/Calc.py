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

from back.KlineDataTool import KlineDataTool
from back.ZhongShuProcess import ZhongShuProcess
from back.BiProcess import BiProcess
from back.DuanProcess import DuanProcess
from back.KlineProcess import KlineProcess
from back.Tools import Tools
import back.divergence as divergence

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
        # bitmex 小级别大级别映射
        self.levelMap = {
            '1min': '5min',
            '3min': '15min',
            '15min': '60min',
            '60min': '1day',
            '1day': '1week',
            '5min': '30min',
            '30min': '4hour',
            '4hour': '1week',
            '1week': '1week'
        }
        #  bitmex 参数转换
        self.bitmexPeriodMap = {
            '1min': '1m',
            '3min': '3m',
            '15min': '15m',
            '60min': '60m',
            '1day': '1d',
            '5min': '5m',
            '30min': '30m',
            '4hour': '240m',
            '1week': '7d'
        }

        # 聚宽期货接口参数 本级别和大级别映射
        self.futureLevelMap = {
            '1m': '5m',
            '3m': '15m',
            '15m': '60m',
            '60m': '1d',
            '1d': '7d',
            '5m': '30m',
            '30m': '240m',
            '240m': '5d',
            '5d': '5d'
        }
        #     period参数转换
        self.periodMap = {
            '1min': '1m',
            '3min': '3m',
            '15min': '15m',
            '60min': '60m',
            '1day': '1d',
            '5min': '5m',
            '30min': '30m',
            '4hour': '240m',
            '1week': '5d'
        }

    def calcData(self, period, symbol, save=False):
        klineList = []

        # def processKline():
        #     count = len(highList)
        #     for i in range(count):
        #         add(highList[i], lowList[i], timeList[i])


        # 获取接口数据
        klineDataTool = KlineDataTool()
        if symbol == 'XBTUSD':
            klineData = klineDataTool.getBtcData(self.bitmexPeriodMap[period], False)
            klineDataBigLevel = klineDataTool.getBtcData(self.bitmexPeriodMap[self.levelMap[period]], True)
        else:
            # 期货
            currentPeriod = self.periodMap[period]
            klineData = klineDataTool.getFutureData(symbol, currentPeriod, 1000)
            bigLevelPeriod = self.futureLevelMap[currentPeriod]
            klineDataBigLevel = klineDataTool.getFutureData(symbol, bigLevelPeriod, 40)
        # print("从接口到的数据", klineData)
        # 存数据快照，调试时候用
        if save:
            base_dir = os.path.dirname(__file__)
            with codecs.open(os.path.join(base_dir, 'klineData.json'), 'w', encoding='utf-8') as f:
                json_str = json.dumps(klineData, ensure_ascii=False, indent=4)
                f.write(json_str)
            with codecs.open(os.path.join(base_dir, 'klineDataBigLevel.json'), 'w', encoding='utf-8') as f:
                json_str = json.dumps(klineDataBigLevel, ensure_ascii=False, indent=4)
                f.write(json_str)

        # 读入本都数据
        # flask 读入本地文件需要这样写
        # base_dir = os.path.dirname(__file__)
        # print(base_dir)
        # with codecs.open(os.path.join(base_dir, 'klineData.json'), encoding='utf-8') as f:
        #     klineData = json.load(f)
        # with codecs.open(os.path.join(base_dir, 'klineDataBigLevel.json'), encoding='utf-8') as f:
        #     klineDataBigLevel = json.load(f)

        jsonObj = klineData
        jsonObjBigLevel = klineDataBigLevel

        openPriceList = []
        highList = []
        lowList = []
        closePriceList = []
        timeList = []
        volumeList = []

        # 获取大级别macd
        closeListBigLevel = []
        timeListBigLevel = []

        for i in range(len(jsonObjBigLevel)):
            item = jsonObjBigLevel[i]
            closeListBigLevel.append(round(float(item['close']), 2))
            localTime = time.localtime(item['time'])
            strTime = time.strftime("%Y-%m-%d %H:%M", localTime)
            timeListBigLevel.append(strTime)

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

        # K线所在笔的方向
        directionList = [0 for i in range(len(timeList))]

        # print(highList)
        # print(lowList)
        # print(timeList)

        # k线处理
        klineProcess = KlineProcess()
        count = len(highList)
        for i in range(count):
            klineProcess.add(highList[i], lowList[i], timeList[i])

        # print('处理后的k线:', klineProcess.klineList, "原始k线:", len(klineProcess.klineRawList));
        # 处理后的k线
        # for i in range(len(klineProcess.klineList)):
        #     prn_obj(klineProcess.klineList[i])
        # 笔处理
        biProcess = BiProcess()
        biProcess.handle(klineProcess.klineList)
        # 笔结果
        biResult = [0 for i in range(len(timeList))]
        for i in range(len(biProcess.biList)):
            item = biProcess.biList[i]
            biResult[item.klineList[-1].middle] = item.direction
            for j in range(item.start + 1, item.end + 1):
                directionList[j] = item.direction

        # print("笔结果:", len(biProcess.biList), biResult)

        # 段处理
        duanProcess = DuanProcess()
        duanResult = duanProcess.handle(biResult, highList, lowList)

        # print("段结果:", len(biResult), len(duanResult))

        # 中枢处理
        zhongShu = ZhongShuProcess()
        zhongShuHigh = zhongShu.initHigh(biResult, highList, lowList)
        zhongShuLow = zhongShu.initLow(biResult, highList, lowList)
        zhongShuStartEnd = zhongShu.initStartEnd(biResult, highList, lowList)

        # print('笔中枢高:', len(zhongShuHigh), zhongShuHigh)
        # print('笔中枢低:', len(zhongShuLow), zhongShuLow)
        # print('笔中枢开始结束:', len(zhongShuStartEnd), zhongShuStartEnd)

        zsdata, zsflag = getZhongShuData(zhongShuHigh, zhongShuLow, zhongShuStartEnd, timeList)
        # print("中枢数据:", zsdata, zsflag)

        # 拼接json数据
        resJson = {}
        # 时间
        resJson['date'] = timeList
        resJson['open'] = openPriceList
        resJson['high'] = highList
        resJson['low'] = lowList
        resJson['close'] = closePriceList

        resJson['bidata'] = getBiData(biProcess, timeList)
        resJson['duandata'] = getDuanData(biProcess, duanProcess, timeList)
        resJson['diff'] = getMacd(closePriceList)[0].tolist()
        resJson['dea'] = getMacd(closePriceList)[1].tolist()
        resJson['macd'] = getMacd(closePriceList)[2].tolist()
        resJson['volume'] = volumeList
        resJson['zsdata'] = zsdata
        resJson['zsflag'] = zsflag

        # 获取大级别macd
        resJson['diffBigLevel'] = getMacd(closeListBigLevel)[0].tolist()
        resJson['deaBigLevel'] = getMacd(closeListBigLevel)[1].tolist()
        resJson['macdBigLevel'] = getMacd(closeListBigLevel)[2].tolist()
        resJson['dateBigLevel'] = timeListBigLevel

        diffList = resJson['diff']
        deaList = resJson['dea']
        macdList = resJson['macd']

        # 开发测试中的背驰计算
        time_array = np.array(timeList)
        macd_array = np.array(macdList)
        diff_array = np.array(diffList)
        dea_array = np.array(deaList)
        beichiData = divergence.calc(time_array, macd_array, diff_array, dea_array, biProcess.biList, duanResult)
        resJson['buyMACDBCData'] = beichiData['buyMACDBCData']
        resJson['sellMACDBCData'] = beichiData['sellMACDBCData']

        resJsonStr = json.dumps(resJson)
        # print(resJsonStr)
        return resJson


def getBiData(biProcess, timeList):
    resBiData = {}

    biData = []
    biDate = []
    for i in range(0, len(biProcess.biList) + 1, 1):
        # bi = biProcess.biList[i]

        #  第一笔和最后一笔特殊处理
        if i == 0:
            bi = biProcess.biList[i]
            if bi.direction == 1:
                biData.append(bi.low)
            else:
                biData.append(bi.high)
            biDate.append(timeList[0])
        else:
            bi = biProcess.biList[i - 1]
            if bi.direction == 1:
                biData.append(bi.high)
            else:
                biData.append(bi.low)
            biDate.append(timeList[bi.klineList[-1].middle])
        # print(bi.start, bi.end, bi.klineList[-1].middle, bi.low, bi.high, bi.direction)
    resBiData['data'] = biData
    resBiData['date'] = biDate
    return resBiData


def getDuanData(biProcess, duanProcess, timeList):
    resDuanData = {}

    duanData = []
    duanDate = []
    for i in range(len(timeList)):
        if duanProcess.result[i] == 0:
            continue
        if duanProcess.result[i] == 1:
            for j in range(0, len(biProcess.biList), 1):
                bi = biProcess.biList[j]
                if i == bi.klineList[-1].middle:
                    duanData.append(bi.high)
                    break
        elif duanProcess.result[i] == -1:
            for j in range(0, len(biProcess.biList), 1):
                bi = biProcess.biList[j]
                if i == bi.klineList[-1].middle:
                    duanData.append(bi.low)
                    break
        duanDate.append(timeList[i])
    resDuanData['data'] = duanData
    resDuanData['date'] = duanDate
    return resDuanData


def getZhongShuData(zhongShuHigh, zhongShuLow, zhongShuStartEnd, timeList):
    zsdata = []
    zsStart = []
    zsEnd = []
    zsflag = []
    for i in range(len(zhongShuStartEnd)):
        item = zhongShuStartEnd[i]
        if item == 0:
            continue
        if item == 1:
            # print("中枢起点:", i, zhongShuHigh[i], zhongShuLow[i], zhongShuStartEnd[i])
            zsStart = [timeList[i], zhongShuLow[i]]
        elif item == 2:
            # print("中枢终点:", i, zhongShuHigh[i], zhongShuLow[i], zhongShuStartEnd[i])
            zsEnd = [timeList[i], zhongShuHigh[i]]
        if len(zsStart) and len(zsEnd):
            zsItem = [copy.copy(zsStart), copy.copy(zsEnd)]
            # print("中枢拼接:", zsItem)
            zsdata.append(copy.copy(zsItem))
            if zsStart[1] > zsEnd[1]:
                zsflag.append(-1)
            else:
                zsflag.append(1)
            zsStart.clear()
            zsEnd.clear()
            zsItem.clear()

    return zsdata, zsflag


def getMacd(closePriceList):
    close = array(closePriceList)
    macd = ta.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    result = np.nan_to_num(macd)
    return result
