# -*- coding: utf-8 -*-

import logging
import traceback
import datetime
import time
import threading
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

tz = pytz.timezone('Asia/Shanghai')

"""
python pychanlun\market_data\global_futures.py
"""

ohlc_dict = { '开盘价': 'first', '最高价': 'max', '最低价': 'min', '收盘价': 'last', '成交量': 'sum' }

stocks = ['AAPL','MSFT','GOOG','FB','AMZN','NFLX','NVDA','AMD']

is_run = True
pwd = hashlib.md5(b'chanlun123456').hexdigest()

def fetch_global_futures_mink():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0"}
    while is_run:
        # 取分钟数据
        url = "http://ldhqsj.com/us_pluralK.action?username=chanlun&password="+pwd+"&id="+ ",".join(stocks) +"&jys=NA&period=1&num=-200"
        print(url)
        resp = requests.get(url)
        content = resp.text
        f = StringIO(content)
        lines = f.readlines()
        date_str = None
        if lines[0].strip() == '日期':
            date_str = lines[1].strip()
            lines = lines[2:]
        df = pd.read_csv(StringIO("".join(lines)))
        if date_str is not None:
            df['时间'] = df['时间'].apply(lambda x: date_str + ' ' + x)
        df['时间'] = df['时间'].apply(lambda x: datetime.datetime.strptime(x, '%Y%m%d %H:%M'))
        df.set_index('时间', inplace=True)
        for code in stocks:
            df1m = df[df['品种代码'] == code]
            save_data_m(code, '1m', df1m)
            # 3m
            df3m = df1m.resample('3T', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
            save_data_m(code, '3m', df3m)
            # 5m
            df5m = df1m.resample('5T', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
            save_data_m(code, '5m', df5m)
            # 15m
            df15m = df1m.resample('15T', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
            save_data_m(code, '15m', df15m)
            # 30m
            df30m = df1m.resample('30T', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
            save_data_m(code, '30m', df30m)
            # 60mm
            df60m = df1m.resample('60T', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
            save_data_m(code, '60m', df60m)
            # 240m
            df240m = df1m.resample('240T', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
            save_data_m(code, '240m', df240m)
        if not is_run:
            break
        time.sleep(200)
    logging.info("外盘分钟数据抓取程序已停止。")


def save_data_m(code, period, df):
    if not df.empty:
        logging.info("保存 %s %s %s" % (code, period, df.index.values[-1]))
    batch = []
    for idx, row in df.iterrows():
        batch.append(UpdateOne({
            "_id": idx.replace(tzinfo=tz)
        }, {
            "$set": {
                "open": float(row['开盘价']),
                "close": float(row['收盘价']),
                "high": float(row['最高价']),
                "low": float(row['最低价']),
                "volume": float(row['成交量'])
            }
        }, upsert=True))
        if len(batch) >= 100:
            DBPyChanlun["%s_%s" % (code, period)].bulk_write(batch)
            batch = []
    if len(batch) > 0:
        DBPyChanlun["%s_%s" % (code, period)].bulk_write(batch)
        batch = []


def save_data_d(code, period, df):
    if not df.empty:
        logging.info("保存 %s %s %s" % (code, period, df.index.values[-1]))
    batch = []
    for idx, row in df.iterrows():
        batch.append(UpdateOne({
            "_id": idx.replace(tzinfo=tz)
        }, {
            "$set": {
                "open": float(row['open']),
                "close": float(row['close']),
                "high": float(row['high']),
                "low": float(row['low']),
                "volume": float(row['volume'])
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
    thread_list.append(threading.Thread(target=fetch_global_futures_mink))
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
