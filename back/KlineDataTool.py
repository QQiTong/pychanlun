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
        startTime = datetime.now()

        r = requests.get(hbdmUrl, params=para, headers=header, )
        endTime = datetime.now() - startTime
        print("耗时:", endTime)
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
        startTime = datetime.now()
        print("可调用条数:", get_query_count())
        # df = get_bars(symbol, size, unit=period, fields=['date', 'open', 'high', 'low', 'close', 'volume'],
        #               include_now=True, end_dt=datetime.now())
        df = get_price(symbol, frequency=period, end_date=datetime.now(), count=size,
        fields = ['open', 'high', 'low', 'close', 'volume'])
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
            item['id'] = timeStamp
            item['open'] = 0 if pd.isna(npKlineList[i][0]) else npKlineList[i][0]
            item['high'] = 0 if pd.isna(npKlineList[i][1]) else npKlineList[i][1]
            item['low'] = 0 if pd.isna(npKlineList[i][2]) else npKlineList[i][2]
            item['close'] = 0 if pd.isna(npKlineList[i][3]) else npKlineList[i][3]
            item['amount'] = 0 if pd.isna(npKlineList[i][4]) else npKlineList[i][4]
            klineList.append(item)
            # print("item->", item)
        # print("期货k线结果:", klineList)
        # endTime = datetime.now() - startTime
        # print("函数时间", endTime)

        return klineList
