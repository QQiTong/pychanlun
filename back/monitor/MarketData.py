import logging

import multiprocessing
from threading import current_thread
import pandas as pd

import rx
from rx.scheduler import ThreadPoolScheduler
from rx import operators as ops

from ..model.Symbol import Symbol
from ..model.Bar import Bar
from ..funcat.data.HuobiDataBackend import HuobiDataBackend

optimal_thread_count = multiprocessing.cpu_count()
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

ohlc_dict = { 'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum' }

def getData1(symbol):
    backend = symbol.backend
    if backend == 'HUOBI':
        dataBackend = HuobiDataBackend()
        # 1m数据
        prices = dataBackend.get_price(symbol.code, 0, 500, '1min')
        df1m = pd.DataFrame.from_records(prices)
        df1m['time'] = pd.to_datetime(df1m.time.values, unit='s', utc=True).tz_convert('Asia/Shanghai')
        df1m.set_index("time", inplace=True)
        saveData(symbol.code, df1m, "1m")
        # 3m数据
        df3m = df1m.resample('3T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
        saveData(symbol.code, df3m, "3m")
        # 5m数据
        df5m = df1m.resample('5T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
        saveData(symbol.code, df5m, "5m")
        # 15m数据
        df15m = df1m.resample('15T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
        saveData(symbol.code, df15m, "15m")
        # 30m数据
        df30m = df1m.resample('30T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
        saveData(symbol.code, df30m, "30m")
        # 1h数据
        df1h = df1m.resample('60T', closed='left', label='left').agg(ohlc_dict).dropna(how='any')
        saveData(symbol.code, df1h, "1h")


def saveData(code, df, period):
    print('保存行情数据', code, period)
    for time, row in df.iterrows():
        bar = Bar(time = time, open = row['open'], close = row['close'], high = row['high'], low = row['low'], volume = row['volume'])
        bar.switch_collection('%s_%s' % (code.lower(), period))
        bar.save()

# 取1m数据，聚合3m、5m、15m、30m和1h的数据
def getMarketData1():
    logger = logging.getLogger()
    logger.info("取市场行情")
    source = rx.from_(Symbol.objects()).pipe(
        ops.subscribe_on(pool_scheduler),
        ops.do_action(lambda symbol: getData1(symbol))
    ).subscribe(lambda value: print('%s获取数据完成' % value.code))
