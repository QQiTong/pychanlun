# -*- coding: utf-8 -*-

from pychanlun.db import DBPyChanlun
import re
import os
import logging
from datetime import datetime, timedelta
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
from pychanlun.basic.pattern import PerfectForBuyLong, BuyPosition
import talib as ta
import numpy as np

tz = pytz.timezone('Asia/Shanghai')


def run(**kwargs):
    # 清理掉1年以上的数据
    cutoff_time = datetime.now(tz) - timedelta(days=360)
    DBPyChanlun["stock_signal"].with_options(codec_options=CodecOptions(
        tz_aware=True, tzinfo=tz)).delete_many({
            "fire_time": {"$lte": cutoff_time}
        })
    codes = []
    collist = DBPyChanlun.list_collection_names()
    for code in collist:
        match = re.match("((sh|sz)(\\d{6}))_(5m|15m|30m)", code, re.I)
        if match is not None:
            code = match.group(1)
            period = match.group(4)
            codes.append({"code": code, "period": period})
    pool = Pool()
    pool.map(calculate, codes)
    pool.close()
    pool.join()


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
    bars = DBPyChanlun['%s_%s' % (code, period)].with_options(codec_options=CodecOptions(
        tz_aware=True, tzinfo=tz)).find().sort('_id', pymongo.DESCENDING).limit(5000)
    bars = list(bars)
    if len(bars) < 13:
        return
    raw_data = {}
    time_series = []
    high_series = []
    low_series = []
    open_series = []
    close_series = []
    count = len(bars)
    for i in range(count - 1, -1, -1):
        time_series.append(bars[i]['_id'])
        high_series.append(bars[i]['high'])
        low_series.append(bars[i]['low'])
        open_series.append(bars[i]['open'])
        close_series.append(bars[i]['close'])
    # 笔信号
    bi_series = [0 for i in range(count)]
    CalcBi(count, bi_series, high_series,
           low_series, open_series, close_series)
    duan_series = [0 for i in range(count)]
    CalcDuan(count, duan_series, bi_series, high_series, low_series)

    higher_duan_series = [0 for i in range(count)]
    CalcDuan(count, higher_duan_series, duan_series, high_series, low_series)

    # 笔中枢的回拉和突破
    entanglement_list = entanglement.CalcEntanglements(
        time_series, duan_series, bi_series, high_series, low_series)
    zs_huila = entanglement.la_hui(entanglement_list, time_series, high_series,
                                   low_series, open_series, close_series, bi_series, duan_series)
    zs_tupo = entanglement.tu_po(entanglement_list, time_series, high_series,
                                 low_series, open_series, close_series, bi_series, duan_series)
    v_reverse = entanglement.v_reverse(entanglement_list, time_series, high_series,
                                       low_series, open_series, close_series, bi_series, duan_series)

    # 段中枢的回拉和突破
    higher_entaglement_list = entanglement.CalcEntanglements(
        time_series, higher_duan_series, duan_series, high_series, low_series)
    higher_zs_huila = entanglement.la_hui(higher_entaglement_list, time_series, high_series,
                                          low_series, open_series, close_series, duan_series, higher_duan_series)
    higher_zs_tupo = entanglement.tu_po(higher_entaglement_list, time_series, high_series,
                                        low_series, open_series, close_series, duan_series, higher_duan_series)
    higher_v_reverse = entanglement.v_reverse(higher_entaglement_list, time_series, high_series,
                                              low_series, open_series, close_series, duan_series, higher_duan_series)

    # 笔中枢信号的记录
    count = len(zs_huila['buy_zs_huila']['date'])
    for i in range(count):
        fire_time = zs_huila['buy_zs_huila']['date'][i]
        price = zs_huila['buy_zs_huila']['data'][i]
        tags = []
        # 当前级别的中枢
        ent = FindPrevEntanglement(entanglement_list, fire_time)
        # 中枢开始的段
        duan_start = FindPrevEq(duan_series, 1, ent.start)
        duan_end = FindNextEq(duan_series, -1, duan_start, len(duan_series))
        # 段的开始如果在更大级别的中枢，就是双盘
        higher_ent = FindPrevEntanglement(higher_entaglement_list, fire_time)
        if ent and higher_ent and duan_start > 0:
            if duan_start <= higher_ent.end and duan_start >= higher_ent.start:
                if price < (higher_ent.zg + higher_ent.zd)/2:
                    tags.append("双盘")
        if PerfectForBuyLong(duan_series, high_series, low_series, duan_end):
            tags.append("完备")
        save_signal(code, period, '拉回笔中枢确认底背', fire_time, price, 'BUY_LONG', tags)

    count = len(zs_huila['sell_zs_huila']['date'])
    for i in range(count):
        save_signal(code, period, '拉回笔中枢确认顶背', zs_huila['sell_zs_huila']
                    ['date'][i], zs_huila['sell_zs_huila']['data'][i], 'SELL_SHORT')

    count = len(zs_tupo['buy_zs_tupo']['date'])
    for i in range(count):
        fire_time = zs_tupo['buy_zs_tupo']['date'][i]
        price = zs_tupo['buy_zs_tupo']['data'][i]
        tags = []
        # 当前级别的中枢
        ent = FindPrevEntanglement(entanglement_list, fire_time)
        # 中枢开始的段
        duan_start = FindPrevEq(duan_series, 1, ent.start)
        duan_end = FindNextEq(duan_series, -1, duan_start, len(duan_series))
        # 段的开始如果在更大级别的中枢，就是双盘
        higher_ent = FindPrevEntanglement(higher_entaglement_list, fire_time)
        if ent and higher_ent and duan_start > 0:
            if duan_start <= higher_ent.end and duan_start >= higher_ent.start:
                if price < (higher_ent.zg + higher_ent.zd)/2:
                    tags.append("双盘")
        if PerfectForBuyLong(duan_series, high_series, low_series, duan_end):
            tags.append("完备")
        save_signal(code, period, '升破笔中枢预多', fire_time, price, 'BUY_LONG', tags)

    count = len(zs_tupo['sell_zs_tupo']['date'])
    for i in range(count):
        save_signal(code, period, '跌破笔中枢预空', zs_tupo['sell_zs_tupo']
                    ['date'][i], zs_tupo['sell_zs_tupo']['data'][i], 'SELL_SHORT')

    count = len(v_reverse['buy_v_reverse']['date'])
    for i in range(count):
        fire_time = v_reverse['buy_v_reverse']['date'][i]
        price = v_reverse['buy_v_reverse']['data'][i]
        tags = []
        # 当前级别的中枢
        ent = FindPrevEntanglement(entanglement_list, fire_time)
        # 中枢开始的段
        duan_start = FindPrevEq(duan_series, 1, ent.start)
        duan_end = FindNextEq(duan_series, -1, duan_start, len(duan_series))
        # 段的开始如果在更大级别的中枢，就是双盘
        higher_ent = FindPrevEntanglement(higher_entaglement_list, fire_time)
        if ent and higher_ent and duan_start > 0:
            if duan_start <= higher_ent.end and duan_start >= higher_ent.start:
                if price < (higher_ent.zg + higher_ent.zd)/2:
                    tags.append("双盘")
        if PerfectForBuyLong(duan_series, high_series, low_series, duan_end):
            tags.append("完备")
        save_signal(code, period, '笔中枢三卖V', fire_time, price, 'BUY_LONG', tags)

    count = len(v_reverse['sell_v_reverse']['date'])
    for i in range(count):
        save_signal(code, period, '笔中枢三买V', v_reverse['sell_v_reverse']
                    ['date'][i], v_reverse['sell_v_reverse']['data'][i], 'SELL_SHORT')

    # 段中枢信号的记录
    count = len(higher_zs_huila['buy_zs_huila']['date'])
    for i in range(count):
        save_signal(code, period, '拉回段中枢确认底背', higher_zs_huila['buy_zs_huila']
                    ['date'][i], higher_zs_huila['buy_zs_huila']['data'][i], 'BUY_LONG')
    count = len(higher_zs_huila['sell_zs_huila']['date'])
    for i in range(count):
        save_signal(code, period, '拉回段中枢确认顶背', higher_zs_huila['sell_zs_huila']
                    ['date'][i], higher_zs_huila['sell_zs_huila']['data'][i], 'SELL_SHORT')

    count = len(higher_zs_tupo['buy_zs_tupo']['date'])
    for i in range(count):
        save_signal(code, period, '升破段中枢预多', higher_zs_tupo['buy_zs_tupo']
                    ['date'][i], higher_zs_tupo['buy_zs_tupo']['data'][i], 'BUY_LONG')
    count = len(higher_zs_tupo['sell_zs_tupo']['date'])
    for i in range(count):
        save_signal(code, period, '跌破段中枢预空',
                    higher_zs_tupo['sell_zs_tupo']['date'][i], higher_zs_tupo['sell_zs_tupo']['data'][i], 'SELL_SHORT')

    count = len(higher_v_reverse['buy_v_reverse']['date'])
    for i in range(count):
        save_signal(code, period, '段中枢三卖V', higher_v_reverse['buy_v_reverse']
                    ['date'][i], higher_v_reverse['buy_v_reverse']['data'][i], 'BUY_LONG')
    count = len(higher_v_reverse['sell_v_reverse']['date'])
    for i in range(count):
        save_signal(code, period, '段中枢三买V', higher_v_reverse['sell_v_reverse']
                    ['date'][i], higher_v_reverse['sell_v_reverse']['data'][i], 'SELL_SHORT')

    # 缠论一买，二买，三买计算
    count = len(time_series)
    diff, dea, macd = ta.MACD(np.array([float(x) for x in close_series]), fastperiod=12, slowperiod=26, signalperiod=9)
    for idx in range(count):
        d1 = FindPrevEq(duan_series, -1, idx)
        g1 = FindPrevEq(duan_series, 1, idx)
        # 是下跌线段
        if d1 > g1 > 0:
            # 找下跌线段开始到目前最低的笔高
            llvh = high_series[g1]
            llvhIdx = g1
            for x in range(g1+1, idx):
                if bi_series[x] == 1 and high_series[x] < llvh:
                    llvh = high_series[x]
                    llvhIdx = x
            # 前面一笔上是不是第一次突破llvh
            bi_c = 0
            bi_s = max(d1, FindNextEq(bi_series, -1, llvhIdx, idx))
            while True:
                bi_e = FindNextEq(bi_series, 1, bi_s, idx)
                if bi_e == -1:
                    # 没有向上笔了
                    break
                # 找到一个向上笔
                if low_series[bi_s] <= llvh and high_series[bi_e] > llvh:
                    bi_c = bi_c + 1
                bi_s = FindNextEq(bi_series, -1, bi_e, idx)
                if bi_s == -1:
                    break
            if bi_c == 1:
                # 只有一次突破，现在是不是向下笔
                bi_d1 = FindPrevEq(bi_series, -1, idx)
                bi_g1 = FindPrevEq(bi_series, 1, idx)
                if bi_d1 > bi_g1 > 0:
                    if macd[idx-1] <= 0 and macd[idx] > 0:
                        is_signal = True
                        for y in range(bi_d1+1, idx):
                            if macd[y-1] <= 0 and macd[y] > 0:
                                # 前面出现过
                                is_signal = False
                                break
                        # 成立
                        if is_signal:
                            p = BuyPosition(entanglement_list, duan_series, bi_series, high_series, low_series, idx)
                            remark = "转折"
                            if p == 1:
                                remark = "一买"
                            elif p == 2:
                                remark = "二买"
                            elif p == 3:
                                remark = "三买"
                            save_signal(code, period, remark, time_series[idx], close_series[idx], 'BUY_LONG')


def save_signal(code, period, remark, fire_time, price, position, tags = []):
    logger = logging.getLogger()
    # 股票只是BUY_LONG才记录
    if position == "BUY_LONG":
        logger.info("%s %s %s %s %s %s" % (code, period, remark, tags, fire_time, price))
        DBPyChanlun['stock_signal'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find_one_and_update({
            "code": code, "period": period, "fire_time": fire_time, "position": position
        }, {
            '$set': {
                'code': code,
                'period': period,
                'remark': remark,
                'fire_time': fire_time,
                'price': price,
                'position': position,
                'tags': tags
            }
        }, upsert=True)
