from datetime import datetime
import time
import pandas as pd
from ..funcat.data.BitmexDataBackend import BitmexDataBackend
from ..funcat.utils import get_int_date
from ..KlineProcess import KlineProcess
from ..BiProcess import BiProcess
from ..DuanProcess import DuanProcess

def doMonitor1():
    print("监控 STRATEGY 3 %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    dtime = datetime.now()
    endTime = int(time.mktime(dtime.timetuple()))
    startTime = endTime - 24 * 60 * 60 * 5
    dataBackend = BitmexDataBackend()
    prices = dataBackend.get_price('XBTUSD', startTime, endTime, '1')

    df1m = pd.DataFrame.from_records(prices)
    df1m['time'] = pd.to_datetime(df1m.time.values, unit='s', utc=True).tz_convert('Asia/Shanghai')
    df1m.set_index("time", inplace=True)
    ohlc_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }
    # 聚合3m数据
    df3m = df1m.resample('3T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    df3m.reset_index('time', inplace=True)
    # 聚合15m数据
    df15m = df1m.resample('15T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
    df15m.reset_index('time', inplace=True)

    #3m笔和段
    high3m = df3m.high.values
    low3m = df3m.low.values
    time3m = df3m.time.values
    count3m = len(time3m)
    klineProcess3m = KlineProcess()
    for i in range(count3m):
        klineProcess3m.add(high3m[i], low3m[i], time3m[i])

    biProcess3m = BiProcess()
    biProcess3m.handle(klineProcess3m.klineList)
    biResult3m = biProcess3m.biResult(count3m)

    #15m笔和段
    high15m = df15m.high.values
    low15m = df15m.low.values
    time15m = df15m.time.values
    count15m = len(time15m)
    klineProcess15m = KlineProcess()
    for i in range(count15m):
        klineProcess15m.add(high15m[i], low15m[i], time15m[i])

    biProcess15m = BiProcess()
    biProcess15m.handle(klineProcess15m.klineList)
    biResult15m = biProcess15m.biResult(count15m)