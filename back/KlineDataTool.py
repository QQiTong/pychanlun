import requests
import json
from jqdatasdk import *
from datetime import datetime,timedelta
import numpy as np
import pandas as pd
import time
import pydash

import rqdatac as rq
from rqdatac import *


# url = "http://api.zb.cn/data/v1/kline?market=btc_usdt"
# 火币合约接口 全局代理后200ms内 , 不代理1s左右
from back.ComposeKline import ComposeKline

hbdmUrl = "https://api.hbdm.com/market/history/kline"
'''
period 1min, 5min, 15min, 30min, 60min,4hour,1day, 1mon
symbol BTC_CW 当周合约 BTC_NW 次周合约 BTC_CQ 季度合约
'''
bitmexUrl = "https://www.bitmex.com/api/v1/trade/bucketed"


class KlineDataTool:
    #  bitmex 并发请求做了限制
    # def getBtcData(self, period, isBigLevel):
    #     url = "https://www.bitmex.com/api/udf/history"
    #     dtime = datetime.now()
    #     toDate = int(time.mktime(dtime.timetuple()))
    #     target = 0
    #     fromDate = 0
    #     # 最大是10080 ,但是数量大了前端会卡顿
    #     if period == "1m":
    #         period = '1'
    #         fromDate = toDate - 24 * 60 * 60
    #     elif period == "3m":
    #         period = '1'
    #         target = 3
    #         fromDate = toDate - 24 * 60 * 60 * 4
    #     elif period == "5m":
    #         period = '5'
    #         fromDate = toDate - 1000 * 5 * 60
    #     elif period == "15m":
    #         period = '1'
    #         target = 15
    #         fromDate = toDate - 2000 * 5 * 60
    #
    #     elif period == "30m":
    #         period = '1'
    #         target = 30
    #         fromDate = toDate - 2000 * 5 * 60
    #     elif period == "60m":
    #         period = '60'
    #         fromDate = toDate - 10 * 1000 * 5 * 60
    #     elif period == "240m":
    #         period = '1'
    #         target = 240
    #         fromDate = toDate - 1000 * 5 * 60
    #     elif period == '1d':
    #         period = 'D'
    #         fromDate = toDate - 1000 * 60 * 60 * 24
    #     elif period == '7d':
    #         period = 'D'
    #         target = 7
    #         fromDate = toDate - 1000 * 5 * 60 * 24
    #
    #     payload = {
    #         'resolution': period,
    #         'symbol': 'XBTUSD',  # 合约类型，如永续合约:XBTUSD
    #         'from': fromDate,
    #         'to': toDate
    #     }
    #     header = {"accept": "*/*", "accept-encoding": "gzip, deflate, br",
    #               "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    #               "origin": "https://static.bitmex.com",
    #               "referer": "https://static.bitmex.com/",
    #               }
    #     startTime = datetime.now()
    #     r = requests.get(url, params=payload, headers=header, )
    #     endTime = datetime.now() - startTime
    #     klines = json.loads(r.text)
    #     print("bitmex接口花费时间:", endTime, datetime.now(), r,klines)
    #     print(len(klines['o']))
    #     newKlineList = []
    #     originKlineList = []
    #
    #     for i in range(len(klines['o'])):
    #         newKline = {}
    #         originKline = {}
    #         originKline['open'] = newKline['open'] = klines['o'][i]
    #         originKline['high'] = newKline['high'] = klines['h'][i]
    #         originKline['low'] = newKline['low'] = klines['l'][i]
    #         originKline['close'] = newKline['close'] = klines['c'][i]
    #         originKline['volume'] = newKline['volume'] = klines['v'][i]
    #         originKline['time'] = klines['t'][i]
    #
    #         dateArray = datetime.utcfromtimestamp(klines['t'][i] + 8 * 3600)
    #         otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
    #         newKline['time'] = otherStyleTime
    #         newKlineList.append(newKline)
    #         originKlineList.append(originKline)
    #
    #     # print("结果:", newKlineList)
    #     # print("结果:", originKlineList)
    #     if target == 0:
    #         return originKlineList
    #     else:
    #         # k线聚合处理
    #         df = pd.DataFrame(newKlineList, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    #         df['time'] = pd.to_datetime(df['time'])
    #         timeList = np.array(df['time']).tolist()
    #         df.set_index("time", inplace=True)
    #         # print(timeList, df)
    #
    #         if target == 7:
    #             targetStr = str(target) + 'D'
    #         else:
    #             targetStr = str(target) + 'T'
    #         ohlc_dict = {
    #             'open': 'first',
    #             'high': 'max',
    #             'low': 'min',
    #             'close': 'last',
    #             'volume': 'sum'
    #         }
    #         # df.index = pd.DatetimeIndex(df.index)
    #
    #         # 聚合k线
    #         resultDf = df.resample(targetStr, closed='left', label='left') \
    #             .agg(ohlc_dict).dropna(how='any')
    #         # print(resultDf)
    #         # 把索引转成列
    #         resultDf.reset_index('time', inplace=True)
    #         # 将列字符串的时间转成时间戳
    #         nparray = np.array(resultDf)
    #         npKlineList = nparray.tolist()
    #         processedKlineList = []
    #
    #         for i in range(len(npKlineList)):
    #             timeStamp = int(time.mktime(npKlineList[i][0].timetuple()))
    #             item = {}
    #             item['time'] = timeStamp
    #             item['open'] = 0 if pd.isna(npKlineList[i][1]) else npKlineList[i][1]
    #             item['high'] = 0 if pd.isna(npKlineList[i][2]) else npKlineList[i][2]
    #             item['low'] = 0 if pd.isna(npKlineList[i][3]) else npKlineList[i][3]
    #             item['close'] = 0 if pd.isna(npKlineList[i][4]) else npKlineList[i][4]
    #             item['volume'] = 0 if pd.isna(npKlineList[i][5]) else npKlineList[i][5]
    #             processedKlineList.append(item)
    #         # print("处理结果:", processedKlineList)
    #         return processedKlineList


    def getDigitCoinData(self,symbol, period):
        url = hbdmUrl
        target = 0
        #  火币没有提供3min的k线, 只能用1min进行合成
        if period == '3min':
            period = '1min'
            target = 3
        payload = {
            'symbol': symbol,  # 合约类型， 火币季度合约
            'period': period,
            'size':2000
        }

        startTime = datetime.now()
        r = requests.get(url, params=payload )

        endTime = datetime.now() - startTime
        klines = json.loads(r.text)['data']
        # print("火币接口花费时间:", endTime, datetime.now(), r)
        # print(klines)
        newKlineList = []
        originKlineList = []

        for i in range(len(klines)):
            newKline = {}
            originKline = {}
            originKline['open'] = newKline['open'] = klines[i]['open']
            originKline['high'] = newKline['high'] = klines[i]['high']
            originKline['low'] = newKline['low'] = klines[i]['low']
            originKline['close'] = newKline['close'] = klines[i]['close']
            originKline['volume'] = newKline['volume'] = klines[i]['amount']
            originKline['time'] = klines[i]['id']

            dateArray = datetime.utcfromtimestamp(klines[i]['id'] + 8 * 3600)
            otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
            newKline['time'] = otherStyleTime
            newKlineList.append(newKline)
            originKlineList.append(originKline)

        # print("结果:", newKlineList)
        # print("结果:", originKlineList)
        if target == 0:
            return originKlineList
        else:
            # k线聚合处理
            df = pd.DataFrame(newKlineList, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df['time'] = pd.to_datetime(df['time'])
            timeList = np.array(df['time']).tolist()
            df.set_index("time", inplace=True)
            # print(timeList, df)

            targetStr = str(target) + 'T'
            ohlc_dict = {
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }
            # df.index = pd.DatetimeIndex(df.index)

            # 聚合k线
            resultDf = df.resample(targetStr, closed='left', label='left') \
                .agg(ohlc_dict).dropna(how='any')
            # print(resultDf)
            # 把索引转成列
            resultDf.reset_index('time', inplace=True)
            # 将列字符串的时间转成时间戳
            nparray = np.array(resultDf)
            npKlineList = nparray.tolist()
            processedKlineList = []

            for i in range(len(npKlineList)):
                timeStamp = int(time.mktime(npKlineList[i][0].timetuple()))
                item = {}
                item['time'] = timeStamp
                item['open'] = 0 if pd.isna(npKlineList[i][1]) else npKlineList[i][1]
                item['high'] = 0 if pd.isna(npKlineList[i][2]) else npKlineList[i][2]
                item['low'] = 0 if pd.isna(npKlineList[i][3]) else npKlineList[i][3]
                item['close'] = 0 if pd.isna(npKlineList[i][4]) else npKlineList[i][4]
                item['volume'] = 0 if pd.isna(npKlineList[i][5]) else npKlineList[i][5]
                processedKlineList.append(item)
            # print("处理结果:", processedKlineList)
            return processedKlineList

    def getFutureData(self, symbol, period, size):
        # 聚宽数据源
        startTime = datetime.now()
        # print("可调用条数:", get_query_count())
        # df = get_bars(symbol, size, unit=period, fields=['date', 'open', 'high', 'low', 'close', 'volume'],
        #               include_now=True, end_dt=datetime.now())
        # df = get_price(symbol, frequency=period, end_date=datetime.now(), count=size,
        #                fields=['open', 'high', 'low', 'close', 'volume'])
        end = datetime.now() + timedelta(1)
        timeDeltaMap = {
            '1m': -7,
            '3m': -31,
            '5m': -31,
            '15m': -31*3,
            '30m':-31*4,
            '60m': -31*8,
            '240m':-31*8,
            '1d': -31*10,
            '5d':-31*30
        }
        start_date = datetime.now() + timedelta(timeDeltaMap[period])

        df = rq.get_price(symbol, frequency=period,
                            fields=['open', 'high', 'low', 'close', 'volume'],start_date=start_date, end_date=end)

        # df = get_price('RB1910.XSGE', frequency='240m', end_date=datetime.now(), count=200,
        #                fields=['open', 'high', 'low', 'close', 'volume'])
        nparray = np.array(df)
        npKlineList = nparray.tolist()
        # npIndexList = pd.to_numeric(df.index) // 1000000000
        klineList = []

        for i in range(len(npKlineList)):
            # timeStamp = int(time.mktime(npKlineList[i][0].timetuple()))
            timeStamp = int(time.mktime(df.index[i].timetuple()))
            item = {}
            item['time'] = timeStamp
            item['open'] = 0 if pd.isna(npKlineList[i][0]) else npKlineList[i][0]
            item['high'] = 0 if pd.isna(npKlineList[i][1]) else npKlineList[i][1]
            item['low'] = 0 if pd.isna(npKlineList[i][2]) else npKlineList[i][2]
            item['close'] = 0 if pd.isna(npKlineList[i][3]) else npKlineList[i][3]
            item['volume'] = 0 if pd.isna(npKlineList[i][4]) else npKlineList[i][4]
            klineList.append(item)
            # print("item->", item)
        # print("期货k线结果:", klineList)
        # endTime = datetime.now() - startTime
        # print("函数时间", endTime)

        return klineList
