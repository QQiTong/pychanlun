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

URL15M = "https://gu.sina.cn/ft/api/jsonp.php/var _%s_15_%s=/GlobalService.getMink?symbol=%s&type=15"
URL30M = "https://gu.sina.cn/ft/api/jsonp.php/var _%s_30_%s=/GlobalService.getMink?symbol=%s&type=30"
URL60M = "https://gu.sina.cn/ft/api/jsonp.php/var _%s_60_%s=/GlobalService.getMink?symbol=%s&type=60"
URL1D = "https://stock2.finance.sina.com.cn/futures/api/jsonp.php/var _%s=/GlobalFuturesService.getGlobalFuturesDailyKLine?symbol=%s&_=%s&source=web"
symbol_list = config['globalFutureSymbol']
min_list = ['5', '15', '15', '30', '60']

is_run = True

def fetch_global_futures_mink():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0"}
    while is_run:
        for minute in min_list:
            for symbol in symbol_list:
                var = "_%s_%s_%s" % (symbol, minute, datetime.datetime.now().timestamp())
                response = requests.get("https://gu.sina.cn/ft/api/jsonp.php/var %s=/GlobalService.getMink?symbol=%s&type=%s" % (var, symbol, minute), headers = headers)
                response_text = response.text
                m = re.search(r'\((.*)\)', response.text)
                content = m.group(1)
                df = pd.DataFrame(json.loads(content))
                df['d'] = df['d'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
                save_data(symbol, '%sm' % minute, df)
                time.sleep(5)
                if not is_run:
                    break
            if not is_run:
                    break
        time.sleep(5)
    logging.info("外盘分钟数据抓取程序已停止。")


def save_data(code, period, df):
    if not df.empty:
        logging.info("保存 %s %s %s" % (code, period, df['d'].iloc[-1]))
    batch = []
    for _, row in df.iterrows():
        batch.append(UpdateOne({
            "_id": row['d'].replace(tzinfo=tz)
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
