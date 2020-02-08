# -*- coding: utf-8 -*-

import os
import logging
from pytdx.reader import TdxLCMinBarReader, TdxFileNotFoundException
import re
from pychanlun.db import DBPyChanlun
import pytz
from datetime import datetime, timedelta
from multiprocessing import Pool
from pymongo import UpdateOne

"""
rx: https://rxpy.readthedocs.io/en/latest/get_started.html
"""

tz = pytz.timezone('Asia/Shanghai')

def run(**kwargs):
    logger = logging.getLogger()
    TDX_HOME = os.environ.get("TDX_HOME")
    if TDX_HOME is None:
        logger.error("没有指定通达信安装目录环境遍历（TDX_HOME）")
        return

    days = kwargs.get("days", 30)
    codes = []

    for subdir in ["sh", "sz"]:
        path = os.path.join(TDX_HOME, "vipdoc\\%s\\fzline" % subdir)
        files = os.listdir(path)
        for filename in files:
            code = None
            if subdir == "sh":
                match = re.match("(sh)6(\\d{5})", filename, re.I)
                if match is not None:
                    code = match.group()
            elif subdir == "sz":
                match = re.match("(sz)(00|30)(\\d{4})", filename, re.I)
                if match is not None:
                    code = match.group()
            filepath = os.path.join(path, filename)
            if code is not None:
                codes.append({"code": code, "filepath": filepath, "days": days})
    pool = Pool(50)
    pool.map(parse_and_save, codes)
    pool.close()
    pool.join()


def parse_and_save(info):
    logger = logging.getLogger()
    logger.info("code=%s filepath=%s", info["code"], info["filepath"])
    start_time = datetime.now() - timedelta(days=info["days"])
    reader = TdxLCMinBarReader()
    df = reader.get_df(info["filepath"])
    df = df[df.index >= start_time]
    save_data(info["code"], "5m", df)

    ohlc = { 'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum', 'amount': 'sum' }
    # 合成15分钟数据
    df15m = df.resample('15T', closed='right', label='right').agg(ohlc).dropna(how='any')
    save_data(info["code"], "15m", df15m)
    df30m = df.resample('30T', closed='right', label='right').agg(ohlc).dropna(how='any')
    save_data(info["code"], "30m", df30m)
    return True


def save_data(code, period, df):
    batch = []
    for time, row in df.iterrows():
        batch.append(UpdateOne({
            "_id": time.replace(tzinfo=tz)
        }, {
            "$set": {
                "open": round(row["open"].item(), 2),
                "close": round(row["close"].item(), 2),
                "high": round(row["high"].item(), 2),
                "low": round(row["low"].item(), 2),
                "volume": round(row["volume"].item(), 2),
                "amount": round(row["amount"].item(), 2)
            }
        }, upsert = True))
        if len(batch) >= 1000:
            DBPyChanlun["%s_%s" % (code, period)].bulk_write(batch)
            batch = []
    if len(batch) > 0:
        DBPyChanlun["%s_%s" % (code, period)].bulk_write(batch)
        batch = []
