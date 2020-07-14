# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime, timedelta, date
from multiprocessing import Pool

import pydash
import pymongo
import pytz
from bson.codec_options import CodecOptions

from pychanlun.chanlun_service import get_data
from pychanlun.db import DBPyChanlun
from pychanlun.db import DBQuantAxis
from pychanlun.monitor.a_stock_common import save_a_stock_signal

tz = pytz.timezone('Asia/Shanghai')


def run(**kwargs):
    # 清理掉1年以上的数据
    cutoff_time = datetime.now(tz) - timedelta(days=360)
    DBPyChanlun["stock_signal"] \
        .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
        .delete_many({"fire_time": {"$lte": cutoff_time}})

    periods = ['30m', '60m']
    symbol = kwargs.get('symbol')
    period = kwargs.get('period')
    codes = []
    if symbol is None:
        stock_list = DBQuantAxis["stock_list"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find()
        for stock in stock_list:
            symbol = "%s%s" % (stock["sse"], stock["code"])
            if period is None:
                for period in periods:
                    codes.append({"sse": stock["sse"], "symbol": symbol, "code": stock["code"], "period": period})
            else:
                codes.append({"sse": stock["sse"], "symbol": symbol, "code": stock["code"], "period": period})
    # else:
    #     if period is None:
    #         for period in periods:
    #             codes.append({'symbol': symbol, 'period': period})
    #     else:
    #         codes.append({'symbol': symbol, 'period': period})

    # 计算执缠策略
    pool = Pool()
    pool.map(calculate, codes)
    pool.close()
    pool.join()

    export_to_tdx()


def calculate(info):
    sse = info["sse"]
    symbol = info["symbol"]
    code = info["code"]
    period = info["period"]
    resp = get_data(symbol, period, datetime.now().strftime("%Y-%m-%d"))
    for signal in ["buy_zs_huila", "buy_zs_tupo", "buy_v_reverse", "buy_five_v_reverse", "buy_duan_break"]:
        signals = resp[signal]
        for idx in range(len(signals["date"])):
            fire_time = signals["date"][idx]
            fire_time = datetime.strptime(fire_time, "%Y-%m-%d %H:%M").replace(tzinfo=tz)
            price = signals["data"][idx]
            stop_lose_price = signals["data"][idx]
            tag = signals["tag"][idx]
            tags = [] if tag is None else tag.split(",")
            save_a_stock_signal(
                sse,
                symbol,
                code,
                period,
                '拉回笔中枢看涨',
                fire_time,
                price,
                stop_lose_price,
                'BUY_LONG',
                tags,
                "",
                True
            )


def export_to_tdx():
    TDX_HOME = os.environ.get("TDX_HOME")
    if TDX_HOME is None:
        logging.error("没有指定通达信安装目录环境遍历（TDX_HOME）")
        return
    seq = []
    t = datetime.now(tz) - timedelta(days=5)
    t = t.replace(hour=0, minute=0, second=0, microsecond=0)
    signals = DBPyChanlun['stock_signal'] \
        .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
        .find({'period': {'$in': ['30m', '60m', '240m']}, 'fire_time': {'$gte': t}}) \
        .sort('fire_time', pymongo.DESCENDING)

    for signal in list(signals):
        code = signal["code"]
        if code.startswith("sh"):
            code = code.replace("sh", "1")
        elif code.startswith("sz"):
            code = code.replace("sz", "0")
        else:
            continue
        seq.append(code + "\n")
    seq = pydash.uniq(seq)
    with open(os.path.join(TDX_HOME, "T0002\\blocknew\\CL%s.blk" % date.today().strftime("%d")), "w") as fo:
        fo.writelines(seq)
