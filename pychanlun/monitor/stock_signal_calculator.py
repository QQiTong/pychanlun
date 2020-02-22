# -*- coding: utf-8 -*-

from pychanlun.db import DBPyChanlun
import re
import os
import logging
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
from pychanlun.basic.pattern import DualEntangleForBuyLong, PerfectForBuyLong, BuyCategory
import talib as ta
import numpy as np
import pydash
import pandas as pd


tz = pytz.timezone('Asia/Shanghai')


def run(**kwargs):
    # 清理掉1年以上的数据
    cutoff_time = datetime.now(tz) - timedelta(days=360)
    DBPyChanlun["stock_signal"].with_options(codec_options=CodecOptions(
        tz_aware=True, tzinfo=tz)).delete_many({
            "fire_time": {"$lte": cutoff_time}
        })
    code = kwargs.get('code')
    period = kwargs.get('period')
    codes = []
    if code is None:
        collist = DBPyChanlun.list_collection_names()
        for code in collist:
            match = re.match("((sh|sz)(\\d{6}))_(5m|15m|30m)", code, re.I)
            if match is not None:
                code = match.group(1)
                period = match.group(4)
                codes.append({"code": code, "period": period})
    else:
        if period is None:
            for period in ['5m', '15m', '30m']:
                codes.append({ 'code': code, 'period': period })
        else:
            codes.append({ 'code': code, 'period': period })

    # 计算执缠策略
    pool = Pool()
    pool.map(calculate, codes)
    pool.close()
    pool.join()

    # 计算连板
    pool = Pool()
    pool.map(raising_limit, codes)
    pool.close()
    pool.join()

    # 最近的100条记录输出到通达信软件
    export_to_tdx()


def calculate(info):
    logger = logging.getLogger()
    code = info["code"]
    period = info["period"]
    # 清理掉1年以上的数据
    cutoff_time = datetime.now(tz) - timedelta(days=360)
    DBPyChanlun['%s_%s' % (code, period)].with_options(codec_options=CodecOptions(
        tz_aware=True, tzinfo=tz)).delete_many({
            "_id": {"$lte": cutoff_time}
        })

    # 日线均线计算，只计算34日均线上的股票
    bars = DBPyChanlun['%s_%s' % (code, '240m')].with_options(codec_options=CodecOptions(
        tz_aware=True, tzinfo=tz)).find().sort('_id', pymongo.DESCENDING).limit(500)
    bars = list(bars)
    bars.reverse()
    if len(bars) > 0:
        df = pd.DataFrame(bars)
        close = [float(x) for x in df.close]
        ma34 = ta.MA(np.array(close), timeperiod=34)
        if close[-1] < ma34[-1]:
            return

    bars = DBPyChanlun['%s_%s' % (code, period)].with_options(codec_options=CodecOptions(
        tz_aware=True, tzinfo=tz)).find().sort('_id', pymongo.DESCENDING).limit(5000)
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

    # 笔信号
    bi_series = [0 for i in range(count)]
    CalcBi(count, bi_series, high_series,
           low_series, open_series, close_series)
    duan_series = [0 for i in range(count)]
    CalcDuan(count, duan_series, bi_series, high_series, low_series)

    higher_duan_series = [0 for i in range(count)]
    CalcDuan(count, higher_duan_series, duan_series, high_series, low_series)

    entanglement_list = entanglement.CalcEntanglements(
        time_series, duan_series, bi_series, high_series, low_series)
    zs_huila = entanglement.la_hui(entanglement_list, time_series, high_series,
                                   low_series, open_series, close_series, bi_series, duan_series)
    zs_tupo = entanglement.tu_po(entanglement_list, time_series, high_series,
                                 low_series, open_series, close_series, bi_series, duan_series)
    v_reverse = entanglement.v_reverse(entanglement_list, time_series, high_series,
                                       low_series, open_series, close_series, bi_series, duan_series)
    duan_pohuai = entanglement.po_huai(time_series, high_series, low_series, open_series, close_series, bi_series, duan_series)


    higher_entaglement_list = entanglement.CalcEntanglements(
        time_series, higher_duan_series, duan_series, high_series, low_series)

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
        if PerfectForBuyLong(duan_series, high_series, low_series, duan_end):
            tags.append("完备")
        category = BuyCategory(higher_duan_series, duan_series, high_series, low_series, idx)
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

        if PerfectForBuyLong(duan_series, high_series, low_series, duan_end):
            tags.append("完备")
        category = BuyCategory(higher_duan_series, duan_series, high_series, low_series, idx)
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

        if PerfectForBuyLong(duan_series, high_series, low_series, duan_end):
            tags.append("完备")
        category = BuyCategory(higher_duan_series, duan_series, high_series, low_series, idx)
        save_signal(code, period, '多-笔中枢三卖V', fire_time,
                    price, stop_lose_price, 'BUY_LONG', tags, category)


    count = len(duan_pohuai['buy_duan_break']['date'])
    for i in range(count):
        idx = duan_pohuai['buy_duan_break']['idx'][i]
        fire_time = duan_pohuai['buy_duan_break']['date'][i]
        price = duan_pohuai['buy_duan_break']['data'][i]
        stop_lose_price = duan_pohuai['buy_duan_break']['stop_lose_price'][i]
        category = BuyCategory(higher_duan_series, duan_series, high_series, low_series, idx)
        save_signal(code, period, '多-线段破坏', fire_time,
                    price, stop_lose_price, 'BUY_LONG', [], category)


def save_signal(code, period, remark, fire_time, price, stop_lose_price, position, tags=[], category=""):
    logger = logging.getLogger()
    # 股票只是BUY_LONG才记录
    if position == "BUY_LONG":
        if (stop_lose_price - price) / price > -0.05:
            logger.info("%s %s %s %s %s %s %s" %
                        (code, period, remark, tags, category, fire_time, price))
            DBPyChanlun['stock_signal'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find_one_and_update({
                "code": code, "period": period, "fire_time": fire_time, "position": position
            }, {
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
    logger = logging.getLogger()
    TDX_HOME = os.environ.get("TDX_HOME")
    if TDX_HOME is None:
        logger.error("没有指定通达信安装目录环境遍历（TDX_HOME）")
        return
    seq = []
    # 连扳票
    raising_limit_stocks = DBPyChanlun['stock'].with_options(codec_options=CodecOptions(
        tz_aware=True, tzinfo=tz)).find({"raising_limit_count": {"$gte": 1}}).sort('raising_limit_count', pymongo.DESCENDING)
    c = 0
    raising_limit_count = 0
    for signal in list(raising_limit_stocks):
        if signal["raising_limit_count"] != raising_limit_count:
            raising_limit_count = signal["raising_limit_count"]
            c = c + 1
        if c <= 3:
            code = signal["_id"]
            if code.startswith("sh"):
                code = code.replace("sh", "1")
            elif code.startswith("sz"):
                code = code.replace("sz", "0")
            else:
                continue
            seq.append(code + "\n")
        else:
            break

    # 缠论票
    signals = DBPyChanlun['stock_signal'].with_options(codec_options=CodecOptions(
        tz_aware=True, tzinfo=tz)).find({}).sort('fire_time', pymongo.DESCENDING).limit(20)

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


def raising_limit(info):
    """
    计算股票连扳的数量，忽略最后2个涨停是一字板的股票。
    """
    code = info["code"]
    bars = DBPyChanlun['%s_240m' % code].with_options(codec_options=CodecOptions(
        tz_aware=True, tzinfo=tz)).find().sort('_id', pymongo.DESCENDING).limit(30)
    bars = list(bars)
    count = 0
    for idx in range(len(bars)-1):
        if bars[idx]["close"] >= round(bars[idx+1]["close"]*1.1, 2):
            count = count + 1
        else:
            break
    if count > 1:
        bars = pydash.chain(bars).take(2).filter(lambda bar: bar["high"] != bar["low"]).value()
        if  len(bars) == 0:
            # 最后2个涨停板是一字板
            count = 0
    DBPyChanlun["stock"].with_options(codec_options=CodecOptions(
        tz_aware=True, tzinfo=tz)).find_one_and_update({
            "_id": code
        }, {
            "$set": {
                "raising_limit_count": count
            }
        }, upsert=True)
