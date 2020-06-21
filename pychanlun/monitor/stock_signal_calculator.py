# -*- coding: utf-8 -*-

from pychanlun.db import DBPyChanlun
import re
import os
import logging
import decimal
from datetime import datetime, timedelta, date
from multiprocessing import Pool
from bson.codec_options import CodecOptions
import pytz
import pymongo
from pychanlun.basic.bi import CalcBi, CalcBiList
from pychanlun.basic.duan import CalcDuan
from pychanlun import Duan
from pychanlun import entanglement as entanglement
from pychanlun import divergence as divergence
from pychanlun.basic.comm import FindPrevEq, FindNextEq, FindPrevEntanglement
from pychanlun.basic.pattern import DualEntangleForBuyLong, perfect_buy_long, buy_category
import talib as ta
import numpy as np
import pydash
import pandas as pd

tz = pytz.timezone('Asia/Shanghai')


def run(**kwargs):
    # 清理掉1年以上的数据
    cutoff_time = datetime.now(tz) - timedelta(days=360)
    DBPyChanlun["stock_signal"] \
        .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
        .delete_many({"fire_time": {"$lte": cutoff_time}})
    code = kwargs.get('code')
    period = kwargs.get('period')
    codes = []
    if code is None:
        collection_list = DBPyChanlun.list_collection_names()
        for code in collection_list:
            match = re.match("((sh|sz)(\\d{6}))_(30m|60m|180m)", code, re.I)
            if match is not None:
                code = match.group(1)
                period = match.group(4)
                codes.append({"code": code, "period": period})
    else:
        if period is None:
            for period in ['30m', '60m', '180m']:
                codes.append({'code': code, 'period': period})
        else:
            codes.append({'code': code, 'period': period})

    # 计算执缠策略
    pool = Pool()
    pool.map(calculate, codes)
    pool.close()
    pool.join()

    export_to_tdx()


def calculate(info):
    code = info["code"]
    period = info["period"]

    # 日线均线计算，只计算34日均线上的股票
    bars = DBPyChanlun['%s_%s' % (code, '180m')] \
        .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
        .find().sort('_id', pymongo.DESCENDING).limit(500)
    bars = list(bars)
    bars.reverse()
    if len(bars) > 0:
        df = pd.DataFrame(bars)
        close = [float(x) for x in df.close]
        ma34 = ta.MA(np.array(close), timeperiod=34)
        if close[-1] < ma34[-1]:
            return
        bars = pydash.chain(bars).take_right(10).value()
        c = 0
        for x in range(1, len(bars)):
            cur_close = decimal.Decimal('%.2f' % bars[x]['close'])
            pre_close = decimal.Decimal('%.2f' % bars[x-1]['close'])
            if cur_close >= (pre_close * decimal.Decimal('1.1')):
                c = c + 1
        if c == 0:
            return
    else:
        return

    bars = DBPyChanlun['%s_%s' % (code, period)] \
        .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz))\
        .find().sort('_id', pymongo.DESCENDING)\
        .limit(1000)
    bars = list(bars)
    bars.reverse()
    if len(bars) == 0:
        DBPyChanlun['%s_%s' % (code, period)].drop()
        return
    elif len(bars) < 13:
        return
    count = len(bars)
    df = pd.DataFrame(bars)
    time_series = df['_id']
    high_series = df['high']
    low_series = df['low']
    open_series = df['open']
    close_series = df['close']

    # 清理一些历史数据节省空间
    if period == '180m':
        cutoff_time = datetime.now(tz=tz) - timedelta(days=10000)
    elif period == '60m':
        cutoff_time = datetime.now(tz=tz) - timedelta(hours=10000)
    elif period == '30m':
        cutoff_time = datetime.now(tz=tz) - timedelta(hours=5000)
    elif period == '15m':
        cutoff_time = datetime.now(tz=tz) - timedelta(hours=2500)
    elif period == '5m':
        cutoff_time = datetime.now(tz=tz) - timedelta(minutes=50000)
    elif period == '3m':
        cutoff_time = datetime.now(tz=tz) - timedelta(minutes=30000)
    elif period == '1m':
        cutoff_time = datetime.now(tz=tz) - timedelta(minutes=10000)
    else:
        cutoff_time = datetime.now(tz=tz) - timedelta(days=10000)

    DBPyChanlun['%s_%s' % (code, period)] \
        .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
        .delete_many({"_id": {"$lt": cutoff_time}})

    # 笔信号
    bi_series = [0 for i in range(count)]
    CalcBi(count, bi_series, high_series, low_series, open_series, close_series)
    duan_series = [0 for i in range(count)]
    CalcDuan(count, duan_series, bi_series, high_series, low_series)

    higher_duan_series = [0 for i in range(count)]
    CalcDuan(count, higher_duan_series, duan_series, high_series, low_series)

    entanglement_list = entanglement.CalcEntanglements(time_series, duan_series, bi_series, high_series, low_series)
    zs_huila = entanglement \
        .la_hui(entanglement_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series)
    zs_tupo = entanglement \
        .tu_po(entanglement_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series)
    v_reverse = entanglement \
        .v_reverse(entanglement_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series)
    duan_pohuai = entanglement \
        .po_huai(time_series, high_series, low_series, open_series, close_series, bi_series, duan_series)

    higher_entaglement_list = entanglement \
        .CalcEntanglements(time_series, higher_duan_series, duan_series, high_series, low_series)

    # 笔中枢信号的记录
    count = len(zs_huila['buy_zs_huila']['date'])
    for i in range(count):
        idx = zs_huila['buy_zs_huila']['idx'][i]
        fire_time = zs_huila['buy_zs_huila']['date'][i]
        price = zs_huila['buy_zs_huila']['data'][i]
        stop_lose_price = zs_huila['buy_zs_huila']['stop_lose_price'][i]
        tags = []
        # 当前级别的中枢
        ent = FindPrevEntanglement(entanglement_list, fire_time)
        # 中枢开始的段
        duan_start = FindPrevEq(duan_series, 1, ent.start)
        duan_end = FindNextEq(duan_series, -1, duan_start, len(duan_series))

        if DualEntangleForBuyLong(duan_series, entanglement_list, higher_entaglement_list, fire_time, price):
            tags.append("双盘")
        if perfect_buy_long(duan_series, high_series, low_series, duan_end):
            tags.append("完备")
        category = buy_category(higher_duan_series, duan_series, high_series, low_series, idx)
        save_signal(code, period, '多-拉回笔中枢确认底背',
                    fire_time, price, stop_lose_price, 'BUY_LONG', tags, category)

    count = len(zs_tupo['buy_zs_tupo']['date'])
    for i in range(count):
        idx = zs_tupo['buy_zs_tupo']['idx'][i]
        fire_time = zs_tupo['buy_zs_tupo']['date'][i]
        price = zs_tupo['buy_zs_tupo']['data'][i]
        stop_lose_price = zs_tupo['buy_zs_tupo']['stop_lose_price'][i]
        tags = []
        # 当前级别的中枢
        ent = FindPrevEntanglement(entanglement_list, fire_time)
        # 中枢开始的段
        duan_start = FindPrevEq(duan_series, 1, ent.start)
        duan_end = FindNextEq(duan_series, -1, duan_start, len(duan_series))

        if perfect_buy_long(duan_series, high_series, low_series, duan_end):
            tags.append("完备")
        category = buy_category(higher_duan_series, duan_series, high_series, low_series, idx)
        save_signal(code, period, '多-升破笔中枢',
                    fire_time, price, stop_lose_price, 'BUY_LONG', tags, category)

    count = len(v_reverse['buy_v_reverse']['date'])
    for i in range(count):
        idx = v_reverse['buy_v_reverse']['idx'][i]
        fire_time = v_reverse['buy_v_reverse']['date'][i]
        price = v_reverse['buy_v_reverse']['data'][i]
        stop_lose_price = v_reverse['buy_v_reverse']['stop_lose_price'][i]
        tags = []
        # 当前级别的中枢
        ent = FindPrevEntanglement(entanglement_list, fire_time)
        # 中枢开始的段
        duan_start = FindPrevEq(duan_series, 1, ent.start)
        duan_end = FindNextEq(duan_series, -1, duan_start, len(duan_series))

        if perfect_buy_long(duan_series, high_series, low_series, duan_end):
            tags.append("完备")
        category = buy_category(higher_duan_series, duan_series, high_series, low_series, idx)
        save_signal(code, period, '多-笔中枢三卖V', fire_time,
                    price, stop_lose_price, 'BUY_LONG', tags, category)

    count = len(duan_pohuai['buy_duan_break']['date'])
    for i in range(count):
        idx = duan_pohuai['buy_duan_break']['idx'][i]
        fire_time = duan_pohuai['buy_duan_break']['date'][i]
        price = duan_pohuai['buy_duan_break']['data'][i]
        stop_lose_price = duan_pohuai['buy_duan_break']['stop_lose_price'][i]
        category = buy_category(higher_duan_series, duan_series, high_series, low_series, idx)
        save_signal(code, period, '多-线段破坏', fire_time,
                    price, stop_lose_price, 'BUY_LONG', [], category)


def save_signal(code, period, remark, fire_time, price, stop_lose_price, position, tags=[], category=""):
    # 股票只是BUY_LONG才记录
    if position == "BUY_LONG":
        logging.info("%s %s %s %s %s %s %s" % (code, period, remark, tags, category, fire_time, price))
        DBPyChanlun['stock_signal']\
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz))\
            .find_one_and_update({"code": code, "period": period, "fire_time": fire_time, "position": position}, {
                '$set': {
                    'code': code,
                    'period': period,
                    'remark': remark,
                    'fire_time': fire_time,
                    'price': price,
                    'stop_lose_price': stop_lose_price,
                    'position': position,
                    'tags': tags,
                    'category': category
                }
            }, upsert=True)


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
        .find({'period': {'$in': ['30m', '60m', '180m']}, 'fire_time': {'$gte': t}}) \
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
