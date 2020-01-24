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

tz = pytz.timezone('Asia/Shanghai')


def run(**kwargs):
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
    cutoff_time = datetime.now(tz) - timedelta(days=360)
    DBPyChanlun['%s_%s' % (code, period)].with_options(codec_options=CodecOptions(
        tz_aware=True, tzinfo=tz)).delete_many({
            "_id": { "$lte": cutoff_time }
        })
    bars = DBPyChanlun['%s_%s' % (code, period)].with_options(codec_options=CodecOptions(
        tz_aware=True, tzinfo=tz)).find().sort('_id', pymongo.DESCENDING).limit(3000)
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

    count = len(zs_huila['buy_zs_huila']['date'])
    for i in range(count):
        save_signal(code, period, '拉回中枢确认底背',
                    zs_huila['buy_zs_huila']['date'][i], zs_huila['buy_zs_huila']['data'][i], 'BUY_LONG')
    count = len(zs_huila['sell_zs_huila']['date'])
    for i in range(count):
        save_signal(code, period, '拉回中枢确认顶背', zs_huila['sell_zs_huila']
                    ['date'][i], zs_huila['sell_zs_huila']['data'][i], 'SELL_SHORT')

    count = len(zs_tupo['buy_zs_tupo']['date'])
    for i in range(count):
        save_signal(code, period, '突破中枢预多', zs_tupo['buy_zs_tupo']
                    ['date'][i], zs_tupo['buy_zs_tupo']['data'][i], 'BUY_LONG')
    count = len(zs_tupo['sell_zs_tupo']['date'])
    for i in range(count):
        save_signal(code, period, '突破中枢预空', zs_tupo['sell_zs_tupo']
                    ['date'][i], zs_tupo['sell_zs_tupo']['data'][i], 'SELL_SHORT')

    # 段中枢的回拉和突破
    higher_entaglement_list = entanglement.CalcEntanglements(
        time_series, higher_duan_series, duan_series, high_series, low_series)
    higher_zs_huila = entanglement.la_hui(higher_entaglement_list, time_series, high_series,
                                          low_series, open_series, close_series, duan_series, higher_duan_series)
    higher_zs_tupo = entanglement.tu_po(higher_entaglement_list, time_series, high_series,
                                        low_series, open_series, close_series, duan_series, higher_duan_series)

    count = len(higher_zs_huila['buy_zs_huila']['date'])
    for i in range(count):
        save_signal(code, period, '拉回中枢确认底背', higher_zs_huila['buy_zs_huila']
                    ['date'][i], higher_zs_huila['buy_zs_huila']['data'][i], 'BUY_LONG')
    count = len(higher_zs_huila['sell_zs_huila']['date'])
    for i in range(count):
        save_signal(code, period, '拉回中枢确认顶背', higher_zs_huila['sell_zs_huila']
                    ['date'][i], higher_zs_huila['sell_zs_huila']['data'][i], 'SELL_SHORT')

    count = len(higher_zs_tupo['buy_zs_tupo']['date'])
    for i in range(count):
        save_signal(code, period, '突破中枢预多', higher_zs_tupo['buy_zs_tupo']
                    ['date'][i], higher_zs_tupo['buy_zs_tupo']['data'][i], 'BUY_LONG')
    count = len(higher_zs_tupo['sell_zs_tupo']['date'])
    for i in range(count):
        save_signal(code, period, '突破中枢预空',
                    higher_zs_tupo['sell_zs_tupo']['date'][i], higher_zs_tupo['sell_zs_tupo']['data'][i], 'SELL_SHORT')


def save_signal(code, period, remark, fire_time, price, position):
    logger = logging.getLogger()
    # 股票只是BUY_LONG才记录
    if position == "BUY_LONG":
        logger.info("%s %s %s %s %s" % (code, period, remark, fire_time, price))
        DBPyChanlun['stock_signal'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find_one_and_update({
            "code": code, "period": period, "fire_time": fire_time, "position": position
        }, {
            '$set': {
                'code': code,
                'period': period,
                'remark': remark,
                'fire_time': fire_time,
                'price': price,
                'position': position
            }
        }, upsert=True)
