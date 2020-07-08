# -*- coding: utf-8 -*-

import pytz
import os
from logbook import Logger
import signal
import threading
import pydash

from pytdx.hq import TdxHq_API
from pychanlun.db import DBPyChanlun
from pychanlun.db import DBQuantAxis
from bson.codec_options import CodecOptions

from pychanlun import entanglement as entanglement
from pychanlun.basic.comm import FindPrevEq, FindNextEq, FindPrevEntanglement
from pychanlun.basic.pattern import DualEntangleForBuyLong, perfect_buy_long, buy_category
import pandas as pd
import datetime
from pychanlun.zerodegree.notify import send_ding_message
from pychanlun.basic.bi import calculate_bi
from pychanlun.basic.duan import calculate_duan, split_bi_in_duan
from et_stopwatch import Stopwatch


tz = pytz.timezone('Asia/Shanghai')
log = Logger(__name__)

is_run = True
period_map = {
    '5m': 0,
    '15m': 1,
    '30m': 2,
    '60m': 3,
    '1d': 4,
    '1w': 5
}


def monitoring_stock():
    TDX_HOME = os.environ.get("TDX_HOME")
    if TDX_HOME is None:
        log.error("没有指定通达信安装目录环境遍历（TDX_HOME）")
        return
    stocks = []
    block_path = os.path.join(TDX_HOME, "T0002\\blocknew\\ZXG.blk")
    if os.path.exists(block_path):
        with open(block_path, "r") as fo:
            lines = fo.readlines()
            stocks = stocks + pydash.chain(lines).map(lambda v: v.strip()).filter(lambda v: len(v) > 0).value()
    for x in range(0, 33):
        block_path = os.path.join(TDX_HOME, "T0002\\blocknew\\CL%s.blk" % str(x).zfill(2))
        if os.path.exists(block_path):
            with open(block_path, "r") as fo:
                lines = fo.readlines()
                stocks = stocks + pydash.chain(lines).map(lambda v: v.strip()).filter(lambda v: len(v) > 0).value()
    stocks = pydash.uniq(stocks)

    log.info("监控股票数量: {}".format(len(stocks)))

    api = TdxHq_API(heartbeat=True, auto_retry=True)

    with api.connect('119.147.212.81', 7709):
        while is_run:
            for stock in stocks:
                market = int(stock[0:1])
                code = stock[1:]
                if market == 0:
                    sse = 'sz'
                    symbol = 'sz%s' % code
                elif market == 1:
                    sse = 'sh'
                    symbol = 'sh%s' % code
                for period in ['5m', '15m']:
                    stopwatch = Stopwatch('%s %3s' % (symbol, period))
                    calculate_and_notify(api, market, sse, symbol, code, period)
                    stopwatch.stop()
                    log.info(stopwatch)
                    if not is_run:
                        break
                if not is_run:
                    break


def calculate_and_notify(api, market, sse, symbol, code, period):
    if period not in ['5m', '15m']:
        return
    if period == '5m':
        required_period_list = ['5m', '30m', '1d']
    elif period == '15m':
        required_period_list = ['15m', '60m', '1w']

    data_list = []
    required_period_list.reverse()
    for period_one in required_period_list:
        kline_data = api.get_security_bars(period_map[period_one], market, code, 0, 800)

        if kline_data is None or len(kline_data) == 0:
            return
        kline_data = pd.DataFrame(kline_data)
        kline_data["time_str"] = kline_data['datetime']
        kline_data['datetime'] = kline_data['time_str'] \
            .apply(lambda value: datetime.datetime.strptime(value, '%Y-%m-%d %H:%M').replace(tzinfo=tz))
        kline_data['time_stamp'] = kline_data['datetime'].apply(lambda value: value.timestamp())
        data_list.append({"symbol": code, "period": period_one, "kline_data": kline_data})
    data_list = pydash.take_right_while(data_list, lambda value: len(value["kline_data"]) > 0)

    for idx in range(len(data_list)):
        if idx == 0:
            data = data_list[idx]
            count = len(data["kline_data"])
            bi_list = [0 for i in range(count)]
            duan_list = [0 for i in range(count)]
            duan_list2 = [0 for i in range(count)]
            calculate_bi(
                bi_list,
                list(data["kline_data"]["high"]),
                list(data["kline_data"]["low"]),
                list(data["kline_data"]["open"]),
                data["kline_data"]["close"]
            )
            data["kline_data"]["bi"] = bi_list
            data["kline_data"]["duan"] = duan_list
            data["kline_data"]["duan2"] = duan_list2
        elif idx == 1:
            data2 = data_list[idx - 1]
            data = data_list[idx]
            count = len(data["kline_data"])
            bi_list = [0 for i in range(count)]
            duan_list = [0 for i in range(count)]
            duan_list2 = [0 for i in range(count)]
            calculate_duan(
                duan_list,
                list(data["kline_data"]["time_stamp"]),
                list(data2["kline_data"]["bi"]),
                list(data2["kline_data"]["time_stamp"]),
                list(data["kline_data"]["high"]),
                list(data["kline_data"]["low"])
            )
            split_bi_in_duan(
                bi_list,
                duan_list,
                list(data["kline_data"]["high"]),
                list(data["kline_data"]["low"]),
                list(data["kline_data"]["open"]),
                list(data["kline_data"]["close"])
            )
            data["kline_data"]["bi"] = bi_list
            data["kline_data"]["duan"] = duan_list
            data["kline_data"]["duan2"] = duan_list2
        else:
            data3 = data_list[idx - 2]
            data2 = data_list[idx - 1]
            data = data_list[idx]
            count = len(data["kline_data"])
            bi_list = [0 for i in range(count)]
            duan_list = [0 for i in range(count)]
            duan_list2 = [0 for i in range(count)]
            calculate_duan(
                duan_list,
                list(data["kline_data"]["time_stamp"]),
                list(data2["kline_data"]["bi"]),
                list(data2["kline_data"]["time_stamp"]),
                list(data["kline_data"]["high"]),
                list(data["kline_data"]["low"])
            )
            calculate_duan(
                duan_list2,
                list(data["kline_data"]["time_stamp"]),
                list(data3["kline_data"]["bi"]),
                list(data3["kline_data"]["time_stamp"]),
                list(data["kline_data"]["high"]),
                list(data["kline_data"]["low"])
            )
            split_bi_in_duan(
                bi_list,
                duan_list,
                list(data["kline_data"]["high"]),
                list(data["kline_data"]["low"]),
                list(data["kline_data"]["open"]),
                list(data["kline_data"]["close"])
            )
            data["kline_data"]["bi"] = bi_list
            data["kline_data"]["duan"] = duan_list
            data["kline_data"]["duan2"] = duan_list2

    data = data_list[-1]
    df = data["kline_data"]

    time_series = list(df['datetime'])
    high_series = list(df['high'])
    low_series = list(df['low'])
    open_series = list(df['open'])
    close_series = list(df['close'])
    bi_series = list(df['bi'])
    duan_series = list(df['duan'])

    higher_duan_series = list(df['duan2'])

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
    #
    # count = len(duan_pohuai['buy_duan_break']['date'])
    # for i in range(count):
    #     idx = duan_pohuai['buy_duan_break']['idx'][i]
    #     fire_time = duan_pohuai['buy_duan_break']['date'][i]
    #     price = duan_pohuai['buy_duan_break']['data'][i]
    #     stop_lose_price = duan_pohuai['buy_duan_break']['stop_lose_price'][i]
    #     category = buy_category(higher_duan_series, duan_series, high_series, low_series, idx)
    #     save_signal(sse, symbol, code, period, '线段破坏看涨', fire_time,
    #                 price, stop_lose_price, 'BUY_LONG', [], category)


def save_signal(sse, symbol, code, period, remark, fire_time, price, stop_lose_price, position, tags=[], category=""):
    # 股票只是BUY_LONG才记录
    if position == "BUY_LONG":
        stock_one = DBQuantAxis['stock_list'].find_one({"code": code, "sse": sse})
        name = stock_one['name'] if stock_one is not None else None
        x = DBPyChanlun['stock_signal'] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find_one_and_update({
                "symbol": symbol,
                "code": code,
                "period": period,
                "fire_time": fire_time,
                "position": position
            }, {
                '$set': {
                    "symbol": symbol,
                    'code': code,
                    'name': name,
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
            content = "【事件通知】%s-%s-%s-%s-%s-%s-%s-%s" \
                      % (symbol, name, period, remark, fire_time.strftime("%m%d%H%M"), price, tags, category)
            log.info(content)
            send_ding_message(content)


def signal_handler(signal_num, frame):
    log.info("正在停止程序。")
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
