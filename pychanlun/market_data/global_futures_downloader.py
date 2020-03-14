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
from pychanlun.config import config


tz = pytz.timezone('Asia/Shanghai')

"""
python pychanlun\market_data\global_futures.py
"""

symbol_list = config['globalFutureSymbol']
min_list = ['5', '15', '30', '60']

is_run = True

def fetch_global_futures_mink():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0"}
    while is_run:
        # 取分钟数据
        for minute in min_list:
            for symbol in symbol_list:
                var = "_%s_%s_%s" % (symbol, minute, datetime.datetime.now().timestamp())
                url = "https://gu.sina.cn/ft/api/jsonp.php/var %s=/GlobalService.getMink?symbol=%s&type=%s" % (var, symbol, minute)
                response = requests.get(url, headers = headers)
                response_text = response.text
                m = re.search(r'\((.*)\)', response.text)
                content = m.group(1)
                df = pd.DataFrame(json.loads(content))
                df['d'] = df['d'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
                df.set_index("d", inplace=True)
                save_data_m(symbol, '%sm' % minute, df)
                # 合成240F数据
                if minute == '30':
                    ohlc_dict = { 'o': 'first', 'h': 'max', 'l': 'min', 'c': 'last', 'v': 'sum' }
                    df240m = df.resample('240T', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
                    save_data_m(symbol, '240m', df240m)
                time.sleep(15)
                if not is_run:
                    break
            if not is_run:
                    break
        # 取日线数据
        if is_run:
            for symbol in symbol_list:
                d = datetime.datetime.now().strftime('%Y_%m_%d')
                var = "_%s_%s" % (symbol, d)
                url = "https://stock2.finance.sina.com.cn/futures/api/jsonp.php/var %s=/GlobalFuturesService.getGlobalFuturesDailyKLine?symbol=%s&_=%s&source=web" % (var, symbol, d)
                response = requests.get(url, headers = headers)
                response_text = response.text
                m = re.search(r'\((.*)\)', response_text)
                content = m.group(1)
                df = pd.DataFrame(json.loads(content))
                df['date'] = df['date'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
                df.set_index('date', inplace=True)
                save_data_d(symbol, '1d', df)
                # 合成3d数据
                ohlc_dict = { 'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum' }
                df3d = df.resample('3D', closed='right', label='right').agg(ohlc_dict).dropna(how='any')
                save_data_d(symbol, '3d', df3d)
                time.sleep(15)
                if not is_run:
                    break
        time.sleep(5)
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
                "open": float(row['o']),
                "close": float(row['c']),
                "high": float(row['h']),
                "low": float(row['l']),
                "volume": float(row['v'])
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
