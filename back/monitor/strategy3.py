from datetime import datetime
import time
import pandas as pd
from ..funcat.data.BitmexDataBackend import BitmexDataBackend
from ..funcat.utils import get_int_date

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
    # 聚合15m数据
    df15m = df1m.resample('15T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
