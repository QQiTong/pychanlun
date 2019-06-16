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


# sinaUrl = "http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLineXm?symbol=CODE"

class KlineDataTool:

    def getKlineData(self, period, size):
        # 3min 和 1week 的火币dm没有提供,需要合成

        target = 0
        if period == '3min':
            period = '1min'
            target = 3
        para = {"period": period, "size": size, "symbol": "BTC_CQ"}
        header = {}
        r = requests.get(hbdmUrl, params=para, headers=header, )
        # verify=True适用于服务端的ssl证书验证，verify=False为关闭ssl验证
        # print('get请求获取的响应结果json类型', r.text)
        # print("get请求获取响应头", r.headers['Content-Type'])
        if r.status_code == 200:

            json_r = r.json()
            # print("接口请求结果:", json_r)
            splitItem = json_r['ch'].split('.')
            if splitItem[1] != "BTC_CQ" or splitItem[3] != period:
                # 求的参数和返回的参数不一致
                return
            if target == 3:
                # 3min需要合成
                composeKline = ComposeKline()
                kline3min = composeKline.compose(json_r['data'], 3)
                # print("合成的3分钟数据:", kline3min)
                return kline3min
            return json_r['data']
        else:
            print("接口请求出错!")

    def getFutureData(self, symbol, period, size):
        # 聚宽数据源
        print("可调用条数:", get_query_count())
        target = 0
        if period == '4hour':
           period = '1m'
           target = 4  # 合成240分钟
        if period == '3m':
           period = '1m'
           target = 3  # 合成3分钟

        df = get_bars(symbol, size, unit=period, fields=['date', 'open', 'high', 'low', 'close', 'volume'],
                      include_now=True, end_dt=datetime.now())
        print(df)
        nparray = np.array(df)
        npKlineList = nparray.tolist()
        klineList = []

        for i in range(len(npKlineList)):
            timeStamp = int(time.mktime(npKlineList[i][0].timetuple()))
            item = {}
            item['id'] = timeStamp
            item['open'] = npKlineList[i][1]
            item['high'] = npKlineList[i][2]
            item['low'] = npKlineList[i][3]
            item['show'] = npKlineList[i][4]
            item['amount'] = npKlineList[i][5]
            klineList.append(item)
            print("item->", item)
        print("期货k线结果:", klineList)
        composeKline = ComposeKline()
        if target == 3 :
            kline3min = composeKline.compose(klineList, 3)
            return kline3min
        if target == 4 :
            kline240min = composeKline.compose(klineList, 240)
            return kline240min
        return klineList
