# -*- coding: utf-8 -*-

from pychanlun.Calc import Calc
from pychanlun.KlineDataTool import KlineDataTool
from datetime import datetime, timedelta, timezone
import time
import bitmex
import requests
import json
import time
import pandas as pd
import numpy as np


# un_time = time.mktime(df.index[-1].timetuple())
# un_time1 = time.mktime(df.index[-2].timetuple())
# un_time2 = time.mktime(df.index[-3].timetuple())
# un_time3 = time.mktime(df.index[-4].timetuple())
# print(result[-4])
# print(result[-3])
# for i in range(len(df.index)):
# print(un_time)
# print(un_time1)
# print(result[-1])

# 用于调试
class Main:
    def test(self):
        print("haha")
        # calc = Calc()
        # calc.calcData('3min')
        # auth('13088887055', 'chanlun123456')
        # klineDataTool = KlineDataTool()
        # result = klineDataTool.getFutureData('RB1910.XSGE', '210m', 200)
        # result = klineDataTool.getKlineData('3min',200)

        # df = get_price('RB1910.XSGE', frequency='1m', end_date=datetime.now(), count=500,
        #                fields=['open', 'high', 'low', 'close', 'volume'])

        # resultDf = df.resample('210T',closed='left', label='left')\
        #     .agg(ohlc_dict).dropna(how='any')
        # print(resultDf)
        # client = bitmex.bitmex()
        # result = client.Quote.Quote_get(symbol="XBTUSD", reverse=True, count=1).result()
        # print(result)

        # 参考http://aijiebots.com/wenzhang/80
        # 接口1只提供了1m,5m,1h,1d 四种周期
        url = 'https://www.bitmex.com/api/v1/trade/bucketed'
        # 接口2 同样也只提供了4种周期 但是有长度限制 最大750条 这样到值合成出来的15分钟和30分钟只有50条和25条
        # url2 = "https://www.bitmex.com/api/udf/history"
        payload = {
            'binSize': '1m',  # 时间周期，可选参数包括1m,5m,1h,1d
            'partial': 'true',  # 是否返回未完成的K线
            'symbol': 'XBTUSD',  # 合约类型，如永续合约:XBTUSD
            'count': 200,  # 返回K线的条数
            'reverse': 'true',  # 是否显示最近的数据，即按时间降序排列
            'endTime': datetime.now()  # 结束时间，格式：2018-07-23T00:00:00.000Z
            #        'startTime':startTime #开始时间，格式：2018-06-23T00:00:00.000Z
        }
        #  3m,15m,30m,210m 用pandas合成
        # dtime = datetime.now()
        # toTime = int(time.mktime(dtime.timetuple()))
        # print("----", toTime)
        #  1分钟 from:24*60 分钟
        #  3分钟 from: 3* 24*60       resolution 1
        #  5分钟 from: 5* 24*60       resolution 5
        #  15分钟 from : 15* 24*60    resolution 5
        #  30分钟 from : 30* 24*60    resolution 5
        #  60分钟 from : 7天前    resolution 60
        #  210分钟 from : 半年前    resolution 60
        #  1day from : 半年前    resolution D
        # payload2 = {
        #     'resolution': '1',
        #     'symbol': 'XBTUSD',  # 合约类型，如永续合约:XBTUSD
        #     'from': 1560845257,
        #     'to': toTime
        # }
        #
        startTime = datetime.now()
        r = requests.get(url, params=payload)
        endTime = datetime.now() - startTime
        klines = json.loads(r.text)
        print("bitmex接口花费时间:", endTime, datetime.now(), r,klines)
        klines.reverse()
        # print(klines)

        # timeStr = klines[0]['timestamp'].split('.')[0]
        # timeStr = timeStr.replace("T", " ")
        # timeArray = time.strptime(timeStr, "%Y-%m-%d %H:%M:%S")
        # timeStamp = int(time.mktime(timeArray))
        # 调整时间区
        # print(timeStamp + 8 * 3600)

        timeList = []

        for kline in klines:
            timeStr = kline['timestamp'].split('.')[0]
            timeStr = timeStr.replace("T", " ")
            timeArray = time.strptime(timeStr, "%Y-%m-%d %H:%M:%S")
            timeStamp = int(time.mktime(timeArray)) + 8 * 3600
            #  pandas 需要字符串格式的时间
            dateArray = datetime.utcfromtimestamp(timeStamp)
            otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
            timeList.append(otherStyleTime)

        df = pd.DataFrame(klines, index=timeList, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # print(df, timeList)

        # 合成k线
        ohlc_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }
        df.index = pd.DatetimeIndex(df.index)

        resultDf = df.resample('3T', how=ohlc_dict, closed='left', label='left')
        # print(df, resultDf)

    def testNewkline(self):
        url = "https://www.bitmex.com/api/udf/history"
        period = '7d'
        dtime = datetime.now()
        toDate = int(time.mktime(dtime.timetuple()))
        target = 0
        fromDate = 0
        # 最大是10080 ,但是数量大了前端会卡顿
        if period == "1m":
            period = '1'
            fromDate = toDate - 24 * 60 * 60
        elif period == "3m":
            period = '1'
            target = 3
            fromDate = toDate - 24 * 60 * 60 * 3
        elif period == "5m":
            period = '5'

            fromDate = toDate - 1000 * 5 * 60
        elif period == "15m":
            period = '1'
            target = 15
            fromDate = toDate - 10080 * 60

        elif period == "30m":
            period = '1'
            target = 30
            fromDate = toDate - 10080 * 60
        elif period == "60m":
            period = '60'
            fromDate = toDate - 1000 * 60 * 60
        elif period == "210m":
            period = '1'
            target = 210
            fromDate = toDate - 10080 * 60
        elif period == '1d':
            period = 'D'
            fromDate = toDate - 1440 * 24 * 60 * 60
        elif period == '7d':
            period = 'D'
            target = 7
            fromDate = toDate - 1440 * 24 * 60 * 60

        payload = {
            'resolution': period,
            'symbol': 'XBTUSD',  # 合约类型，如永续合约:XBTUSD
            'from': fromDate,
            'to': toDate
        }
        header = {"accept": "*/*", "accept-encoding": "gzip, deflate, br",
                  "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                  "origin": "https://static.bitmex.com",
                  "referer": "https://static.bitmex.com/",
                  }
        startTime = datetime.now()
        r = requests.get(url, params=payload, headers=header, )
        endTime = datetime.now() - startTime
        # print("bitmex接口花费时间:", endTime, datetime.now(), r)
        klines = json.loads(r.text)
        print(len(klines['o']))
        newKlineList = []
        originKlineList = []

        for i in range(len(klines['o'])):
            newKline = {}
            originKline = {}
            originKline['open'] = newKline['open'] = klines['o'][i]
            originKline['high'] = newKline['high'] = klines['h'][i]
            originKline['low'] = newKline['low'] = klines['l'][i]
            originKline['close'] = newKline['close'] = klines['c'][i]
            originKline['volume'] = newKline['volume'] = klines['v'][i]
            originKline['time'] = klines['t'][i]

            dateArray = datetime.utcfromtimestamp(klines['t'][i] + 8 * 3600)
            otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
            newKline['time'] = otherStyleTime
            newKlineList.append(newKline)
            originKlineList.append(originKline)

        print("结果:", newKlineList)
        print("结果:", originKlineList)
        if target == 0:
            return originKlineList
        else:
            # k线聚合处理
            df = pd.DataFrame(newKlineList, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df['time'] = pd.to_datetime(df['time'])
            timeList = np.array(df['time']).tolist()
            df.set_index("time", inplace=True)
            # print(timeList, df)

            if target == 7:
                targetStr = str(target) + 'D'
            else:
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
            print(resultDf)
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


main = Main()
main.testNewkline()
