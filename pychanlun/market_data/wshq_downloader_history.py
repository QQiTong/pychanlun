# -*- coding: utf-8 -*-

import logging
import traceback
import time
import threading

from pychanlun.DingMsg import DingMsg
from pychanlun.db import DBPyChanlun
import requests
import re
import json
import pandas as pd
from pymongo import UpdateOne
import pytz
import signal
import hashlib
from io import StringIO
from pychanlun.config import config
from datetime import datetime, timedelta

tz = pytz.timezone('Asia/Shanghai')

"""
python pychanlun\market_data\global_futures.py
"""
'''
微盛投资
http://www.wstock.net/
实时API接口是按次数、市场收费的，这些品种分属我方
WG市场(新加坡富时A50指数）
CE市场 (道琼斯指数 标准普尔指数 纳斯达克指数 )、
CM市场(纽约金 纽约银)、
NE市场(美原油)、
CO市场(美大豆、美豆油)，
LE市场（伦敦镍）总共6个市场，
每日1万次     1980元/月 频率1000ms
每日10万次    3080元/月 频率500ms
不限次数      3880元/月 频率300ms
每日100万次   4680元/月 不限频率     
每日500万次   6480元/月 不限频率     
每日1000万次   7980元/月 不限频率     

6个市场 1980元/月 1万次调用   23,760‬‬ /年   年付 8.5折  20,196‬/年
5个市场 1780元/月 1万次调用   21,360‬ /年   年付 8.5折  18,156‬‬/年
4个市场 1580元/月 1万次调用   18,960‬ /年   年付 8.5折  16,116‬‬/年
2个市场 1180元/月 1万次调用   14,160 /年   年付 8.5折  12,036‬‬/年

新浪虽然免费，但是没有3分钟和股指期货的数据

请求参数：
num：        指定返回记录数目
symbol：     品种名称
desc：       1为倒序（递减），默认值为0表示递增
q_type:     指定排序方式，0代表以Date排序，1代表以Volume排序，2代表以Amount排序，3代表以Symbol排序(默认值为3)
return_t:   返回指定K线类型，0为日线，1为月线，2为周线，3为分钟线，4为季线，5为年线 (默认值0)
qt_type:    指定分钟线类型，例如qt_type=1 则返回1分钟数据，qt_type=3则返回3分钟数据，以此类推(默认值为1)。需在return_t=3的情况下使用

返回参数：
symbol 	股票代码
Name    股票名字
Date    交易时间
Open    开盘价
High    最高价
Low     最低价
Close   收盘价
Volume  当日总成交量

小道琼连续: CEYMA0
小标普连续: CEESA0
小纳指连续: CENQA0

富时A50:   WGCNA0

原油连续：  NECLA0

美黄金主力: CMGCA0
美白银主力: CMSIA0


美豆油连续：COZLA0
美豆粕连续：COZMA0
美大豆连续：COZSA0

美棉花连续：IECTA0

伦镍     : LENID3M
'''
dingMsg = DingMsg()

# 转化成简称入库
global_future_alias = config['global_future_alias']
global_future_symbol = config['global_future_symbol']
ohlc_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
# 8个品种 LENID3M 暂时没接
futures = ['CEYMA0', 'CEESA0', 'CENQA0', 'WGCNA0', 'NECLA0', 'CMGCA0', 'CMSIA0','COZSA0','COZLA0','COZMA0']

is_run = True

'''
此文件用于初始化历史数据
'''
def fetch_futures_mink():
    count = 0
    while is_run:
        try:
            for code in futures:
                # 1 ,3 ,5 ,15 ,30 ,60 ,180,240
                qt_type = 180
                # 0：日线 ,3： 分钟线
                return_t = 3
                # 取分钟数据
                url = "http://db2015.wstock.cn/wsDB_API/kline.php?num=5000&symbol=%s&desc=1&q_type=0&return_t=%s&qt_type=%s&r_type=2&u=u2368&p=abc1818" % (code,return_t,qt_type)

                count = count +1
                print(url, "调用次数:",count)
                resp = requests.get(url, timeout=10)
                df1m = pd.DataFrame(json.loads(resp.text))
                df1m = df1m.sort_values(by="Date", ascending=True)
                df1m['Date'] = df1m['Date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
                # 刷日线的时候解开这个注释
                # df1m['Date'] = df1m['Date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
                df1m.set_index('Date', inplace=True)
                code = global_future_alias[code]

                save_data_m(code, '180m', df1m)
                # 3m
                # df3m = df1m.resample('3T', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
                # df3m = df3m[1:]
                # save_data_m(code, '3m', df3m)
                # # 5m
                # df5m = df1m.resample('5T', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
                # df5m = df5m[1:]
                # save_data_m(code, '5m', df5m)
                # # 15m
                # df15m = df1m.resample('15T', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
                # df15m = df15m[1:]
                # save_data_m(code, '15m', df15m)
                # # 30m
                # df30m = df1m.resample('30T', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
                # df30m = df30m[1:]
                # save_data_m(code, '30m', df30m)
                # # 60mm
                # df60m = df1m.resample('60T', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
                # df60m = df60m[1:]
                # save_data_m(code, '60m', df60m)
                # # 180m
                # df180m = df1m.resample('240T', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
                # df180m = df180m[1:]
                # save_data_m(code, '180m', df180m)
                # # 1D
                # df1d = df1m.resample('1D', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
                # df1d = df1d[1:]
                # save_data_m(code, '1d', df1d)
                # # # 3D
                # df3d = df1d.resample('3D', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
                # df3d = df3d[1:]
                # save_data_m(code, '3d', df3d)
                time.sleep(1)
                if not is_run:
                    break

            time.sleep(10)
        except Exception as e:
            print("外盘期货采集出错", Exception, e)
            # dingMsg.send("remind外盘期货采集出错")



def save_data_m(code, period, df):
    if not df.empty:
        logging.info("保存 %s %s %s" % (code, period, df.index.values[-1]))
    batch = []
    for idx, row in df.iterrows():
        batch.append(UpdateOne({
            "_id": idx.replace(tzinfo=tz)
        }, {
            "$set": {
                "open": float(row['Open']),
                "close": float(row['Close']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "volume": float(row['Volume'])
            }
        }, upsert=True))
        if len(batch) >= 100:
            DBPyChanlun["%s_%s" % (code, period)].bulk_write(batch)
            batch = []
    if len(batch) > 0:
        DBPyChanlun["%s_%s" % (code, period)].bulk_write(batch)
        batch = []


def signal_hanlder(signalnum, frame):
    logging.info("正在停止程序。")
    global is_run
    is_run = False


def run(**kwargs):
    signal.signal(signal.SIGINT, signal_hanlder)
    thread_list = []
    thread_list.append(threading.Thread(target=fetch_futures_mink))
    for thread in thread_list:
        thread.start()

    while True:
        for thread in thread_list:
            if thread.isAlive():
                break
        else:
            break


if __name__ == '__main__':
    run()
