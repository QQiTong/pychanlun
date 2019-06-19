import requests
import json
from jqdatasdk import *
from datetime import datetime
import numpy as np
import pandas as pd
import time

# url = "http://api.zb.cn/data/v1/kline?market=btc_usdt"
# 火币合约接口 全局代理后200ms内 , 不代理1s左右
from back.ComposeKline import ComposeKline

hbdmUrl = "https://api.hbdm.com/market/history/kline"
'''
period 1min, 5min, 15min, 30min, 60min,4hour,1day, 1mon
symbol BTC_CW 当周合约 BTC_NW 次周合约 BTC_CQ 季度合约
'''
bitmexUrl = "https://www.bitmex.com/api/v1/trade/bucketed"


# sinaUrl = "http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLineXm?symbol=CODE"

class KlineDataTool:
    # 废弃
    # def getKlineData(self, period, size):
    #     # 3min 和 1week 的火币dm没有提供,需要合成
    #
    #     target = 0
    #     if period == '3min':
    #         period = '1min'
    #         target = 3
    #     para = {"period": period, "size": size, "symbol": "BTC_CQ"}
    #     header = {}
    #     startTime = datetime.now()
    #
    #     r = requests.get(hbdmUrl, params=para, headers=header, )
    #     endTime = datetime.now() - startTime
    #     print("耗时:", endTime)
    #     # verify=True适用于服务端的ssl证书验证，verify=False为关闭ssl验证
    #     # print('get请求获取的响应结果json类型', r.text)
    #     # print("get请求获取响应头", r.headers['Content-Type'])
    #     if r.status_code == 200:
    #
    #         json_r = r.json()
    #         # print("接口请求结果:", json_r)
    #         splitItem = json_r['ch'].split('.')
    #         if splitItem[1] != "BTC_CQ" or splitItem[3] != period:
    #             # 求的参数和返回的参数不一致
    #             return
    #         if target == 3:
    #             # 3min需要合成
    #             composeKline = ComposeKline()
    #             kline3min = composeKline.compose(json_r['data'], 3)
    #             # print("合成的3分钟数据:", kline3min)
    #             return kline3min
    #         return json_r['data']
    #     else:
    #         print("接口请求出错!")

    def getKlineData(self, period, size):
        # 3m,15m,30m,240m 用pandas合成

        target = 0
        if period == '3min' or period == '3m':
            period = '1m'
            target = 3
            size = 750
        #     因为最大只能请求750条数据导致 k线导致合成出来的数据太少
        #  todo 15,30,240,分钟数据量太小
        elif period == '15min' or period == '15m':
            period = '1m'
            target = 15
            size = 750
        elif period == '30min' or period == '30m':
            period = '1m'
            target = 30
            size = 750
        elif period == '240min' or period == '240m':
            period = '1m'
            target = 240
            size = 750
        elif period == '7d':
            period = '1d'
            target = 7
            size = 750
        para = {
            "binSize": period,  # 时间周期，可选参数包括1m,5m,1h,1d
            'partial': 'true',  # 是否返回未完成的K线
            "symbol": "XBTUSD",  # 合约类型，如永续合约:XBTUSD
            "count": size,  # 返回K线的条数
            'reverse': 'true',  # 是否显示最近的数据，即按时间降序排列
            'endTime': datetime.now()  # 结束时间，格式：2018-07-23T00:00:00.000Z
            # 'startTime':startTime #开始时间，格式：2018-06-23T00:00:00.000Z
        }
        header = {}
        startTime = datetime.now()
        r = requests.get(bitmexUrl, params=para, headers=header, )
        endTime = datetime.now() - startTime
        print("bitmex耗时:", endTime)
        # verify=True适用于服务端的ssl证书验证，verify=False为关闭ssl验证
        # print('get请求获取的响应结果json类型', r.text)
        # print("get请求获取响应头", r.headers['Content-Type'])
        if r.status_code == 200:
            klines = r.json()
            print("bitmex耗时返回的结果:", klines)

            return self.procesKlineData(klines, target)
        else:
            print("接口请求出错!")

    #  合成k线 type 合成几分钟的
    def procesKlineData(self, klines, target):
        klines.reverse()
        timeList = []
        newKlineList = []
        for kline in klines:
            timeStr = kline['timestamp'].split('.')[0]
            timeStr = timeStr.replace("T", " ")
            timeArray = time.strptime(timeStr, "%Y-%m-%d %H:%M:%S")
            timeStamp = int(time.mktime(timeArray)) + 8 * 3600
            #  pandas 需要字符串格式的时间
            dateArray = datetime.utcfromtimestamp(timeStamp)
            otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
            timeList.append(otherStyleTime)
            newItem = {
                "open": kline['open'],
                "high": kline['high'],
                "low": kline['low'],
                "close": kline['close'],
                "time": timeStamp,
                "volume": kline['volume']
            }
            newKlineList.append(newItem)
        df = pd.DataFrame(klines, index=timeList, columns=['open', 'high', 'low', 'close', 'volume'])
        print(df, timeList)

        if target == 0:
            return newKlineList
        else:
            # 合成k线
            ohlc_dict = {
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }
            if target == 7:
                targetStr = str(target) + 'D'
            else:
                targetStr = str(target) + 'T'
            df.index = pd.DatetimeIndex(df.index)
            resultDf = df.resample(targetStr, how=ohlc_dict, closed='left', label='left')
            # 转换成list
            resultKline = self.getKLineResult(resultDf)
            print(resultDf, resultKline)
            return resultKline

    def getKLineResult(self, resultDf):
        nparray = np.array(resultDf)
        npKlineList = nparray.tolist()
        klineList = []

        for i in range(len(npKlineList)):
            # timeStamp = int(time.mktime(npKlineList[i][0].timetuple()))
            timeStamp = int(time.mktime(resultDf.index[i].timetuple()))
            item = {}
            item['time'] = timeStamp
            item['open'] = 0 if pd.isna(npKlineList[i][0]) else npKlineList[i][0]
            item['high'] = 0 if pd.isna(npKlineList[i][1]) else npKlineList[i][1]
            item['low'] = 0 if pd.isna(npKlineList[i][2]) else npKlineList[i][2]
            item['close'] = 0 if pd.isna(npKlineList[i][3]) else npKlineList[i][3]
            item['volume'] = 0 if pd.isna(npKlineList[i][4]) else npKlineList[i][4]
            klineList.append(item)
        return klineList

    def getFutureData(self, symbol, period, size):
        # 聚宽数据源
        startTime = datetime.now()
        print("可调用条数:", get_query_count())
        # df = get_bars(symbol, size, unit=period, fields=['date', 'open', 'high', 'low', 'close', 'volume'],
        #               include_now=True, end_dt=datetime.now())
        df = get_price(symbol, frequency=period, end_date=datetime.now(), count=size,
                       fields=['open', 'high', 'low', 'close', 'volume'])
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
