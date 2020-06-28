# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import time
import pydash

import rqdatac as rq
from rqdatac import *
from pychanlun.config import cfg
from pychanlun.db import DBPyChanlun
from bson.codec_options import CodecOptions
import pytz
import pymongo

tz = pytz.timezone('Asia/Shanghai')


# url = "http://api.zb.cn/data/v1/kline?market=btc_usdt"
# 火币合约接口 全局代理后200ms内 , 不代理1s左右
from pychanlun.ComposeKline import ComposeKline
import re

hbdmUrl = "http://api.hbdm.com/market/history/kline"
# okexUrl = "https://www.okex.com/api/swap/v3/instruments/BTC-USDT-SWAP/candles"
okexUrl = "https://www.okex.me/v2/perpetual/pc/public/instruments/BTC-USDT-SWAP/candles"
# 火币永续合约免翻墙
hbSwapUrl = "http://api.btcgateway.pro/swap-ex/market/history/kline?contract_code=BTC-USD"
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
    #     elif period == "180m":
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
    #     r = requests.get(url, params=payload, headers=header, timeout=(15, 15))
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

    # 火币永续合约 btc 币本位
    # def getDigitCoinData(self, symbol, period,endDate):
    #     if symbol == 'BTC':
    #         symbol = 'BTC-USD'
    #     url = hbSwapUrl
    #     target = 0
    #     #  火币没有提供3m的k线, 只能用1m进行合成
    #     if period == '3m':
    #         period = '1min'
    #         target = 3
    #     payload = {
    #         'symbol': symbol,  # 合约类型， 火币季度合约
    #         'period': period,
    #         'size': 2000
    #     }
    #
    #     startTime = datetime.now()
    #     r = requests.get(url, params=payload, verify=False, timeout=(15, 15))
    #     endTime = datetime.now() - startTime
    #     klines = json.loads(r.text)['data']
    #     # print("火币接口花费时间:", endTime, datetime.now(), r)
    #     # print(klines)
    #     newKlineList = []
    #     originKlineList = []
    #
    #     for i in range(len(klines)):
    #         newKline = {}
    #         originKline = {}
    #         originKline['open'] = newKline['open'] = klines[i]['open']
    #         originKline['high'] = newKline['high'] = klines[i]['high']
    #         originKline['low'] = newKline['low'] = klines[i]['low']
    #         originKline['close'] = newKline['close'] = klines[i]['close']
    #         originKline['volume'] = newKline['volume'] = klines[i]['amount']
    #         originKline['time'] = klines[i]['id']
    #
    #         dateArray = datetime.utcfromtimestamp(klines[i]['id'] + 8 * 3600)
    #         otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
    #         newKline['time'] = otherStyleTime
    #         newKlineList.append(newKline)
    #         originKlineList.append(originKline)
    #
    #     # print("结果:", newKlineList)
    #     # print("结果:", originKlineList)
    #     if target == 0:
    #         # if period=='1week':
    #         #     print(len(originKlineList))
    #         return originKlineList
    #     else:
    #         # k线聚合处理
    #         df = pd.DataFrame(newKlineList, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    #         df['time'] = pd.to_datetime(df['time'])
    #         timeList = np.array(df['time']).tolist()
    #         df.set_index("time", inplace=True)
    #         # print(timeList, df)
    #
    #         targetStr = str(target) + 'T'
    #         ohlc_dict = {
    #             'open': 'first',
    #             'high': 'max',
    #             'low': 'min',
    #             'close': 'last',
    #             'volume': 'sum'
    #         }
    #         # df.index = pd.DatetimeIndex(df.index)
    #         # 聚合k线
    #         resultDf = df.resample(targetStr, closed='left', label='left').agg(ohlc_dict).dropna(how='any')
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

    # OKEX 永续合约 usdt金本位 从数据库中获取
    # def getDigitCoinData(self,symbol,period,endDate):
    #     startTime = datetime.now()
    #     if endDate is None or endDate == "":
    #         end = datetime.now() + timedelta(1)
    #     else:
    #         end = datetime.strptime(endDate, "%Y-%m-%d")
    #     end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
    #     timeDeltaMap = {
    #         '1m': -7*3,
    #         '3m': -31*3,
    #         '5m': -31*3,
    #         '15m': -31 * 3,
    #         '30m': -31 * 8,
    #         '60m': -31 * 8,
    #         '180m': -31 * 8,
    #         '1d': -31 * 10,
    #         '3d': -31 * 30,
    #         '1w': -31* 30
    #     }
    #     start_date =  end + timedelta(timeDeltaMap[period])
    #     code = "%s_%s" % (symbol, period)
    #     data_list = DBPyChanlun[code].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
    #         "_id": { "$gte": start_date, "$lte": end }
    #     }).sort("_id", pymongo.ASCENDING)
    #     df = pd.DataFrame(list(data_list))
    #
    #     klineList = []
    #     for idx, row in df.iterrows():
    #         item = {}
    #         item['time'] = int(time.mktime(row["_id"].timetuple()))
    #         item['open'] = 0 if pd.isna(row["open"]) else row["open"]
    #         item['high'] = 0 if pd.isna(row["high"]) else row["high"]
    #         item['low'] = 0 if pd.isna(row["low"]) else row["low"]
    #         item['close'] = 0 if pd.isna(row["close"]) else row["close"]
    #         item['volume'] = 0 if pd.isna(row["volume"]) else row["volume"]
    #         klineList.append(item)
    #     return klineList

    # OKEX 永续合约 usdt金本位 抓包找到的另外一个接口 直接从网络获取但是只能获取1000条
    def getDigitCoinData(self,symbol,period,endDate):
        t = time.time()
        timeStamp = int(round(t * 1000))
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            "Accept": "application/json",
            "App-Type": "web",
            "Referer": "https://www.okex.me/derivatives/swap/full/usdt-btc"}

        payload = {
            'granularity': period,
            'size': 1000,
            't': timeStamp
        }
        r = requests.get(okexUrl, params=payload, headers=headers, timeout=(15, 15))
        data_list = json.loads(r.text)['data']

        df = pd.DataFrame(list(data_list))

        klineList = []
        for idx, row in df.iterrows():
            item = {}
            date = datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%S.%fZ")
            date = date + timedelta(hours=8)
            item['time'] = int(time.mktime(date.timetuple()))
            item['open'] = 0 if pd.isna(row[1]) else row[1]
            item['high'] = 0 if pd.isna(row[2]) else row[2]
            item['low'] = 0 if pd.isna(row[3]) else row[3]
            item['close'] = 0 if pd.isna(row[4]) else row[4]
            item['volume'] = 0 if pd.isna(row[5]) else row[5]
            klineList.append(item)
        return klineList

    # endDate 查看主力合约历史k线
    def getFutureData(self, symbol, period, endDate):
        # 聚宽数据源
        startTime = datetime.now()
        # print("可调用条数:", get_query_count())
        # df = get_bars(symbol, size, unit=period, fields=['date', 'open', 'high', 'low', 'close', 'volume'],
        #               include_now=True, end_dt=datetime.now())
        # df = get_price(symbol, frequency=period, end_date=datetime.now(), count=size,
        #                fields=['open', 'high', 'low', 'close', 'volume'])

        if endDate is None:
            end = datetime.now() + timedelta(1)
        else :
            end = datetime.strptime(endDate,"%Y-%m-%d")
            # symbol = re.sub('\d+', "88", symbol)
        timeDeltaMap = {
            '1m': -7*3,
            '3m': -31*3,
            '5m': -31*3,
            '15m': -31 * 3,
            '30m': -31 * 8,
            '60m': -31 * 8,
            '180m': -31 * 8,
            '1d': -31 * 10,
            '3d': -31 * 30
        }
        start_date =  end + timedelta(timeDeltaMap[period])
        df = rq.get_price(symbol, frequency=period,
                          fields=['open', 'high', 'low', 'close', 'volume'], start_date=start_date, end_date=end)

        # df = get_price('RB1910.XSGE', frequency='180m', end_date=datetime.now(), count=200,
        #                fields=['open', 'high', 'low', 'close', 'volume'])
        # todo 米匡180m 数据有问题,比通达信和文化财经多一个时间,需要手动去除,但是手动去除也不准,需要等米匡修复
        # todo 米匡回复: 180m 是按照交易时间切分的, 一天固定3根k线,而文华财经和通达信是一天固定2根,后面自己处理吧
        # 还是不能这样处理,会导致很多高低点丢失,影响到30F的结构
        # if period == '180m':
        #     cols = [x for i, x in enumerate(df.index) if '15:00:00' in str(df.index[i])]
        #     df = df.drop(cols)
        # if period == '180m':
        #     ohlc_dict = {
        #         'open': 'first',
        #         'high': 'max',
        #         'low': 'min',
        #         'close': 'last',
        #         'volume': 'sum'
        #     }
        #     # df.index = pd.DatetimeIndex(df.index)
        #
        #     # 聚合k线
        #     df = df.resample('4H', closed='left', label='left') \
        #         .agg(ohlc_dict).dropna(how='any')

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
        # if period=='3d':
        # print(len(klineList))
        return klineList


    def getStockData(self, symbol, period, endDate):
        startTime = datetime.now()
        if endDate is None or endDate == "":
            end = datetime.now() + timedelta(1)
        else:
            end = datetime.strptime(endDate, "%Y-%m-%d")
        end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
        timeDeltaMap = {
            '1m': -7*3,
            '3m': -31*3,
            '5m': -31*3,
            '15m': -31 * 3,
            '30m': -31 * 8,
            '60m': -31 * 8,
            '180m': -31 * 8,
            '1d': -31 * 10,
            '3d': -31 * 30
        }
        start_date =  end + timedelta(timeDeltaMap[period])
        code = "%s_%s" % (symbol, period)
        data_list = DBPyChanlun[code].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
            "_id": { "$gte": start_date, "$lte": end }
        }).sort("_id", pymongo.ASCENDING)
        df = pd.DataFrame(list(data_list))

        klineList = []
        for idx, row in df.iterrows():
            item = {}
            item['time'] = int(time.mktime(row["_id"].timetuple()))
            item['open'] = 0 if pd.isna(row["open"]) else row["open"]
            item['high'] = 0 if pd.isna(row["high"]) else row["high"]
            item['low'] = 0 if pd.isna(row["low"]) else row["low"]
            item['close'] = 0 if pd.isna(row["close"]) else row["close"]
            item['volume'] = 0 if pd.isna(row["volume"]) else row["volume"]
            klineList.append(item)
        return klineList
    # 获取外盘期货数据
    def getGlobalFutureData(self, symbol, period, endDate):
        startTime = datetime.now()
        if endDate is None or endDate == "":
            end = datetime.now() + timedelta(1)
        else:
            end = datetime.strptime(endDate, "%Y-%m-%d")
        end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
        timeDeltaMap = {
            '1m': -7*3,
            '3m': -7*1,
            '5m': -7*1,
            '15m': -31 * 3,
            '30m': -31 * 8,
            '60m': -31 * 8,
            '180m': -31 * 8,
            '1d': -31 * 10,
            '3d': -31 * 30
        }
        start_date =  end + timedelta(timeDeltaMap[period])
        code = "%s_%s" % (symbol, period)
        data_list = DBPyChanlun[code].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
            "_id": { "$gte": start_date, "$lte": end }
        }).sort("_id", pymongo.ASCENDING)
        df = pd.DataFrame(list(data_list))

        klineList = []
        for idx, row in df.iterrows():
            item = {}
            item['time'] = int(time.mktime(row["_id"].timetuple()))
            item['open'] = 0 if pd.isna(row["open"]) else row["open"]
            item['high'] = 0 if pd.isna(row["high"]) else row["high"]
            item['low'] = 0 if pd.isna(row["low"]) else row["low"]
            item['close'] = 0 if pd.isna(row["close"]) else row["close"]
            item['volume'] = 0 if pd.isna(row["volume"]) else row["volume"]
            klineList.append(item)
        return klineList