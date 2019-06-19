from back.Calc import Calc
from back.KlineDataTool import KlineDataTool
from jqdatasdk import *
from datetime import datetime, timedelta, timezone
import time
import bitmex
import requests
import json
import time
import pandas as pd


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
    # calc = Calc()
    # calc.calcData('3min')
    # auth('13088887055', 'chanlun123456')
    # klineDataTool = KlineDataTool()
    # result = klineDataTool.getFutureData('RB1910.XSGE', '240m', 200)
    # result = klineDataTool.getKlineData('3min',200)

    # df = get_price('RB1910.XSGE', frequency='1m', end_date=datetime.now(), count=500,
    #                fields=['open', 'high', 'low', 'close', 'volume'])

    # resultDf = df.resample('240T',closed='left', label='left')\
    #     .agg(ohlc_dict).dropna(how='any')
    # print(resultDf)
    # client = bitmex.bitmex()
    # result = client.Quote.Quote_get(symbol="XBTUSD", reverse=True, count=1).result()
    # print(result)

    # 参考http://aijiebots.com/wenzhang/80
    # 接口1只提供了1m,5m,1h,1d 四种周期
    url = 'https://www.bitmex.com/api/v1/trade/bucketed'
    # 接口2 同样也只提供了4种周期
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
    #  3m,15m,30m,240m 用pandas合成
    # dtime = datetime.now()
    # toTime = int(time.mktime(dtime.timetuple()))
    # print("----", toTime)
    #  1分钟 from:24*60 分钟
    #  3分钟 from: 3* 24*60       resolution 1
    #  5分钟 from: 5* 24*60       resolution 5
    #  15分钟 from : 15* 24*60    resolution 5
    #  30分钟 from : 30* 24*60    resolution 5
    #  60分钟 from : 7天前    resolution 60
    #  240分钟 from : 半年前    resolution 60
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
    print("bitmex接口花费时间:", endTime, datetime.now(), r)
    klines = json.loads(r.text)
    klines.reverse()
    print(klines)

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
    print(df, timeList)

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
    print(df, resultDf)
    # toTime = int(time.mktime(timeStr.timetuple()))
    # utc_dt = timeStr.replace(tzinfo=timezone.utc)
    # print(utc_dt)
    # cn_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    # print(cn_dt)
    # jan_dt = utc_dt.astimezone(timezone(timedelta(hours=9)))
    # print(jan_dt)
    # cn_2_jan_dt = cn_dt.astimezone(timezone(timedelta(hours=9)))
    # print(cn_2_jan_dt)
    # for kline in klines:
    #     print(kline)
