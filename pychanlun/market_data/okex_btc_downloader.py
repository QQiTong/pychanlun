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
from pychanlun.config import config, cfg

tz = pytz.timezone('Asia/Shanghai')

"""
python pychanlun\market_data\global_futures.py
"""


min_list = ['1m','3m','5m','15m','30m','60m','240m','1d','1w']

okexPeriodMap = {
            '1m':'60',
            '3m': '180',
            '5m': '300',
            '15m': '900',
            '60m': '3600',
            '30m': '1800',
            '240m': '14400',
            '1d': '86400',
            '1w': '604800'
        }

is_run = True
symbol = 'BTC'
def fetch_global_futures_mink():
    while is_run:
        # 取分钟数据
        for minute in min_list:
            url = "http://www.okex.com/api/swap/v3/instruments/BTC-USDT-SWAP/candles?granularity=%s"   % (okexPeriodMap[minute])
            response = requests.get(url,proxies=cfg.PROXIES)
            response_text = response.text
            df = pd.DataFrame(json.loads(response_text))
            # [['2020-03-22T02:31:00.000Z','12','32','54','34'],['2020-03-22T02:31:00.000Z','12','32','54','34']]

            df = df.iloc[::-1]
            save_data_m(symbol, '%s' % minute, df)
            time.sleep(1)
            if not is_run:
                break
            if not is_run:
                break
        time.sleep(200)
    logging.info("OKEX数据抓取程序已停止。")

def save_data_m(code, period, df):
    if not df.empty:
        logging.info("保存 %s %s %s" % (code, period, df.index.values[-1]))
    batch = []
    for idx, row in df.iterrows():
        date = datetime.datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%S.%fZ")
        batch.append(UpdateOne({
            "_id": date
        }, {
            "$set": {
                "open": float(row[1]),
                "high": float(row[2]),
                "low": float(row[3]),
                "close": float(row[4]),
                "volume": float(row[5])
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
