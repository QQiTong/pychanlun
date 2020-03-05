# -*- coding: utf-8 -*-

import os
import logging
from pytdx.reader import TdxDailyBarReader, TdxLCMinBarReader, TdxFileNotFoundException
import re
from pychanlun.db import DBPyChanlun
import pytz
from datetime import datetime, timedelta, time
from multiprocessing import Pool
from pymongo import UpdateOne
import pandas as pd
import traceback

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

    days = kwargs.get("days", 7)

    codes = []
    for subdir in ["sh", "sz"]:
        path = os.path.join(TDX_HOME, "vipdoc\\%s\\minline" % subdir)
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
    for idx in range(len(codes)):
        info = codes[idx]
        logger.info("%s/%s code=%s filepath=%s", idx+1, len(codes), info["code"], info["filepath"])
        parse_and_save_1m(info)
    # pool = Pool()
    # pool.map(parse_and_save_1m, codes)
    # pool.close()
    # pool.join()

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
    for idx in range(len(codes)):
        info = codes[idx]
        logger.info("%s/%s code=%s filepath=%s", idx+1, len(codes), info["code"], info["filepath"])
        parse_and_save_5m(info)
    # pool = Pool()
    # pool.map(parse_and_save_5m, codes)
    # pool.close()
    # pool.join()

    codes = []
    for subdir in ["sh", "sz"]:
        path = os.path.join(TDX_HOME, "vipdoc\\%s\\lday" % subdir)
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
    for idx in range(len(codes)):
        info = codes[idx]
        logger.info("%s/%s code=%s filepath=%s", idx+1, len(codes), info["code"], info["filepath"])
        parse_and_save_day(info)
    # pool = Pool()
    # pool.map(parse_and_save_day, codes)
    # pool.close()
    # pool.join()


def calc_60m(df):
    bars = []
    rows = []
    for index, row in df.iterrows():
        rows.append(row)
        if index.time() == time(hour=10,minute=30,second=0,microsecond=0):
            g = pd.DataFrame(rows)
            bar = {"date": index, "open": rows[0]["open"], "close": rows[-1]["close"], "high": g.high.max(), "low": g.low.min(), "volume": g.volume.sum(), "amount":g.amount.sum()}
            bars.append(bar)
            rows = []
        elif index.time() == time(hour=11,minute=30,second=0,microsecond=0):
            g = pd.DataFrame(rows)
            bar = {"date": index, "open": rows[0]["open"], "close": rows[-1]["close"], "high": g.high.max(), "low": g.low.min(), "volume": g.volume.sum(), "amount":g.amount.sum()}
            bars.append(bar)
            rows = []
        elif index.time() == time(hour=14,minute=0,second=0,microsecond=0):
            g = pd.DataFrame(rows)
            bar = {"date": index, "open": rows[0]["open"], "close": rows[-1]["close"], "high": g.high.max(), "low": g.low.min(), "volume": g.volume.sum(), "amount":g.amount.sum()}
            bars.append(bar)
            rows = []
        elif index.time() == time(hour=15,minute=0,second=0,microsecond=0):
            g = pd.DataFrame(rows)
            bar = {"date": index, "open": rows[0]["open"], "close": rows[-1]["close"], "high": g.high.max(), "low": g.low.min(), "volume": g.volume.sum(), "amount":g.amount.sum()}
            bars.append(bar)
            rows = []
    if len(bars) > 0:
        df60m = pd.DataFrame(bars)
        df60m.set_index("date", inplace=True)
        return df60m
    else:
        return None

def parse_and_save_1m(info):
    start_time = datetime.now() - timedelta(days=info["days"])
    reader = TdxLCMinBarReader()
    df = reader.get_df(info["filepath"])
    df = df[df.index >= start_time]
    # save_data(info["code"], "1m", df)

    ohlc = {'open': 'first', 'high': 'max', 'low': 'min',
            'close': 'last', 'volume': 'sum', 'amount': 'sum'}
    # 合成3分钟数据
    df3m = df.resample('3T', closed='right', label='right').agg(
        ohlc).dropna(how='any')
    save_data(info["code"], "3m", df3m)
    return True

def parse_and_save_5m(info):
    start_time = datetime.now() - timedelta(days=info["days"])
    reader = TdxLCMinBarReader()
    df = reader.get_df(info["filepath"])
    df = df[df.index >= start_time]
    save_data(info["code"], "5m", df)

    ohlc = {'open': 'first', 'high': 'max', 'low': 'min',
            'close': 'last', 'volume': 'sum', 'amount': 'sum'}
    # 合成15分钟数据
    df15m = df.resample('15T', closed='right', label='right').agg(
        ohlc).dropna(how='any')
    save_data(info["code"], "15m", df15m)
    df30m = df.resample('30T', closed='right', label='right').agg(
        ohlc).dropna(how='any')
    save_data(info["code"], "30m", df30m)
    df60m = calc_60m(df30m)
    if df60m is not None:
        save_data(info["code"], "60m", df60m)
    return True


def parse_and_save_day(info):
    logger = logging.getLogger()
    try:
        start_time = datetime.now() - timedelta(days=info["days"])
        reader = TdxDailyBarReader()
        df = reader.get_df(info["filepath"])
        df = df[df.index >= start_time]
        save_data(info["code"], "240m", df)
    except BaseException as e:
        logger.info("Error Occurred: {0}".format(traceback.format_exc()))
    return True


def save_data(code, period, df):
    batch = []
    for time, row in df.iterrows():
        batch.append(UpdateOne({
            "_id": time.replace(tzinfo=tz)
        }, {
            "$set": {
                "open": round(row["open"], 2),
                "close": round(row["close"], 2),
                "high": round(row["high"], 2),
                "low": round(row["low"], 2),
                "volume": round(row["volume"], 2),
                "amount": round(row["amount"], 2)
            }
        }, upsert=True))
        if len(batch) >= 1000:
            DBPyChanlun["%s_%s" % (code, period)].bulk_write(batch)
            batch = []
    if len(batch) > 0:
        DBPyChanlun["%s_%s" % (code, period)].bulk_write(batch)
        batch = []
