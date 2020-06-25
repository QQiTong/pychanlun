# -*- coding: utf-8 -*-

import pytz
import os
import logging
import signal
import threading
import pydash
import pymongo

from pytdx.hq import TdxHq_API
from pymongo import UpdateOne
from pychanlun.db import DBPyChanlun
from bson.codec_options import CodecOptions

from pychanlun.basic.bi import CalcBi
from pychanlun.basic.duan import CalcDuan
from pychanlun import entanglement as entanglement
from pychanlun.basic.comm import FindPrevEq, FindNextEq, FindPrevEntanglement
from pychanlun.basic.pattern import DualEntangleForBuyLong, perfect_buy_long, buy_category
import pandas as pd
import datetime
from pychanlun.zerodegree.notify import send_ding_message


tz = pytz.timezone('Asia/Shanghai')

is_run = True
period_map = {'5m': 0, '15m': 1, '30m': 2}


def monitoring_stock():
    TDX_HOME = os.environ.get("TDX_HOME")
    if TDX_HOME is None:
        logging.error("没有指定通达信安装目录环境遍历（TDX_HOME）")
        return
    stocks = []
    with open(os.path.join(TDX_HOME, "T0002\\blocknew\\ZXG.blk"), "r") as fo:
        lines = fo.readlines()
        stocks = stocks + pydash.chain(lines).map(lambda v: v.strip()).filter(lambda v: len(v) > 0).value()
    for x in range(0, 33):
        block = "T0002\\blocknew\\CL%s.blk" % str(x).zfill(2)
        with open(os.path.join(TDX_HOME, block), "r") as fo:
            lines = fo.readlines()
            stocks = stocks + pydash.chain(lines).map(lambda v: v.strip()).filter(lambda v: len(v) > 0).value()
    stocks = pydash.uniq(stocks)

    logging.info("监控股票数量: {}".format(len(stocks)))

    api = TdxHq_API(heartbeat=True, auto_retry=True)

    with api.connect('119.147.212.81', 7709):
        while is_run:
            for stock in stocks:
                market = int(stock[0:1])
                code = stock[1:]
                if market == 0:
                    symbol = 'sz%s' % code
                elif market == 1:
                    symbol = 'sh%s' % code
                for period in period_map:
                    bars = api.get_security_bars(period_map[period], market, code, 0, 200)
                    if bars is not None:
                        save_bars(symbol, period, bars)
                        calculate_and_notify(symbol, period)
                    else:
                        print("No bars")
                    if not is_run:
                        break
                if not is_run:
                    break


def calculate_and_notify(code, period):
    bars = DBPyChanlun['%s_%s' % (code, period)] \
        .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
        .find() \
        .sort('_id', pymongo.DESCENDING) \
        .limit(1000)
    bars = list(bars)
    bars.reverse()
    if len(bars) < 13:
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
    CalcBi(count, bi_series, high_series, low_series, open_series, close_series)
    duan_series = [0 for i in range(count)]
    CalcDuan(count, duan_series, bi_series, high_series, low_series)

    higher_duan_series = [0 for i in range(count)]
    CalcDuan(count, higher_duan_series, duan_series, high_series, low_series)

    entanglement_list = entanglement.CalcEntanglements(time_series, duan_series, bi_series, high_series, low_series)
    zs_huila = entanglement.la_hui(entanglement_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series)
    zs_tupo = entanglement.tu_po(entanglement_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series)
    v_reverse = entanglement.v_reverse(entanglement_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series)
    duan_pohuai = entanglement.po_huai(time_series, high_series, low_series, open_series, close_series, bi_series, duan_series)

    higher_entaglement_list = entanglement.CalcEntanglements(time_series, higher_duan_series, duan_series, high_series, low_series)

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
        save_signal(code, period, '拉回笔中枢看涨',
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
        save_signal(code, period, '升破笔中枢看涨',
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
        save_signal(code, period, '笔中枢三卖V看涨', fire_time,
                    price, stop_lose_price, 'BUY_LONG', tags, category)

    count = len(duan_pohuai['buy_duan_break']['date'])
    for i in range(count):
        idx = duan_pohuai['buy_duan_break']['idx'][i]
        fire_time = duan_pohuai['buy_duan_break']['date'][i]
        price = duan_pohuai['buy_duan_break']['data'][i]
        stop_lose_price = duan_pohuai['buy_duan_break']['stop_lose_price'][i]
        category = buy_category(higher_duan_series, duan_series, high_series, low_series, idx)
        save_signal(code, period, '线段反看涨', fire_time,
                    price, stop_lose_price, 'BUY_LONG', [], category)


def save_bars(code, period, bars):
    batch = []
    for idx in range(len(bars)):
        bar = bars[idx]
        t = datetime.datetime.strptime(bar['datetime'], '%Y-%m-%d %H:%M')
        batch.append(UpdateOne({
            "_id": t.replace(tzinfo=tz)
        }, {
            "$set": {
                "open": bar['open'],
                "close": bar['close'],
                "high": bar['high'],
                "low": bar['low'],
                "volume": bar['vol'],
                "amount": bar['amount']
            }
        }, upsert=True))
        if len(batch) >= 100:
            DBPyChanlun["%s_%s" % (code, period)].bulk_write(batch)
            batch = []
    if len(batch) > 0:
        DBPyChanlun["%s_%s" % (code, period)].bulk_write(batch)
        batch = []


def save_signal(code, period, remark, fire_time, price, stop_lose_price, position, tags=[], category=""):
    # 股票只是BUY_LONG才记录
    if position == "BUY_LONG":
        x = DBPyChanlun['stock_signal'] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find_one_and_update({
                "code": code,
                "period": period,
                "fire_time": fire_time,
                "position": position
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
        if x is None and fire_time > datetime.datetime.now(tz=tz) - datetime.timedelta(hours=1):
            # 首次信号，做通知
            content = "【事件通知】%s-%s-%s-%s-%s-%s-%s" % (code, period, remark, tags, category, fire_time, price)
            logging.info(content)
            send_ding_message(content)


def signal_handler(signal_num, frame):
    logging.info("正在停止程序。")
    global is_run
    is_run = False


def run(**kwargs):
    signal.signal(signal.SIGINT, signal_handler)
    thread_list = [threading.Thread(target=monitoring_stock)]
    for thread in thread_list:
        thread.start()

    while True:
        for thread in thread_list:
            if thread.isAlive():
                break
        else:
            break


if __name__ == '__main__':
    try:
        run()
    finally:
        exit()
