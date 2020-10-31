# -*- coding: utf-8 -*-

import datetime
import os
import random
import signal
import threading
import time

import QUANTAXIS as QA
import pandas as pd
import pydash
import pytz
from et_stopwatch import Stopwatch
from func_timeout import func_set_timeout
from loguru import logger
from pytdx.hq import TdxHq_API

from pychanlun import entanglement as entanglement
from pychanlun.basic.kline_analyse import calculate_bi_duan
from pychanlun.monitor.a_stock_common import save_a_stock_signal
from pychanlun.divergence import calc_beichi_data

tz = pytz.timezone('Asia/Shanghai')

is_run = True
is_loop = True

period_map = {
    '1m': 7,
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
        logger.error("没有指定通达信安装目录环境遍历（TDX_HOME）")
        return
    stocks = []
    block_path = os.path.join(TDX_HOME, "T0002\\blocknew\\ZXG.blk")
    if os.path.exists(block_path):
        with open(block_path, "r") as fo:
            lines = fo.readlines()
            stocks = stocks + pydash.chain(lines).map(lambda v: v.strip()).filter(lambda v: len(v) > 0).value()
    for x in range(0, 32):
        block_path = os.path.join(TDX_HOME, "T0002\\blocknew\\CL%s.blk" % str(x).zfill(2))
        if os.path.exists(block_path):
            with open(block_path, "r") as fo:
                lines = fo.readlines()
                stocks = stocks + pydash.chain(lines).map(lambda v: v.strip()).filter(lambda v: len(v) > 0).value()
        if x == 0 and len(stocks) >= 100:
            break
    stocks = pydash.uniq(stocks)
    random.shuffle(stocks)
    logger.info("监控股票数量: {}".format(len(stocks)))

    api = TdxHq_API(heartbeat=True, auto_retry=True)
    global is_run
    global is_loop
    stop_watch = Stopwatch("monitoring_stock")
    monitoring_periods = os.environ.get("PYCHANLUN_STOCK_MONITORING_PERIODS") if os.environ.get(
        "PYCHANLUN_STOCK_MONITORING_PERIODS") is not None else "5m,15m"
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
                for period in monitoring_periods.split(","):
                    stopwatch = Stopwatch('%s %3s' % (symbol, period))
                    calculate_and_notify(api, market, sse, symbol, code, period)
                    stopwatch.stop()
                    logger.info(stopwatch)
                    if not is_run:
                        break
                if not is_run:
                    break
            if not is_loop:
                break
    stop_watch.stop()
    logger.info(stop_watch)


@func_set_timeout(60)
def calculate_and_notify(api, market, sse, symbol, code, period):
    if period not in ['1m', '5m', '15m']:
        return
    if period == '1m':
        required_period_list = ['1m', '5m', '30m']
    elif period == '5m':
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

        MACD = QA.MACD(kline_data['close'], 12, 26, 9)
        kline_data['diff'] = MACD['DIFF']
        kline_data['dea'] = MACD['DEA']
        kline_data['macd'] = MACD['MACD']
        kline_data['jc'] = QA.CROSS(MACD['DIFF'], MACD['DEA'])
        kline_data['sc'] = QA.CROSS(MACD['DEA'], MACD['DIFF'])
        ma5 = QA.MA(kline_data['close'], 5)
        ma20 = QA.MA(kline_data['close'], 20)
        kline_data['ma5'] = ma5
        kline_data['ma20'] = ma20
        kline_data["time_str"] = kline_data['datetime']
        kline_data['datetime'] = kline_data['time_str'] \
            .apply(lambda value: datetime.datetime.strptime(value, '%Y-%m-%d %H:%M').replace(tzinfo=tz))
        kline_data['time_stamp'] = kline_data['datetime'].apply(lambda value: value.timestamp())
        kline_data['time'] = kline_data['time_stamp']

        data_list.append({
            "sse": sse,
            "symbol": symbol,
            "code": code,
            "period": period_one,
            "kline_data": kline_data
        })

    data_list = pydash.take_right_while(data_list, lambda value: len(value["kline_data"]) > 0)
    data_list = calculate_bi_duan(data_list)

    data = data_list[-1]
    df = data["kline_data"]
    data2 = data_list[-2]
    df2 = data2["kline_data"]
    # create_charts(df, page_title="%s %s" % (data["symbol"], data["period"]),
    #               file="E:\\charts\\%s-%s.html" % (data["symbol"], data["period"]))

    time_str_series = list(df['time_str'])
    high_series = list(df['high'])
    low_series = list(df['low'])
    open_series = list(df['open'])
    close_series = list(df['close'])
    bi_series = list(df['bi'])
    duan_series = list(df['duan'])
    ma5 = list(df['ma5'])
    ma20 = list(df['ma20'])

    entanglement_list = entanglement.CalcEntanglements(time_str_series, duan_series, bi_series, high_series, low_series)
    zs_huila = entanglement.la_hui(entanglement_list, time_str_series, high_series, low_series, bi_series, duan_series)
    zs_tupo = entanglement.tu_po(entanglement_list, time_str_series, high_series, low_series, open_series, close_series, bi_series, duan_series)
    v_reverse = entanglement.v_reverse(entanglement_list, time_str_series, high_series, low_series, open_series, close_series, bi_series, duan_series)
    five_v_fan = entanglement.five_v_fan(
        time_str_series,
        duan_series,
        bi_series,
        high_series,
        low_series,
        list(df["duan2"]),
        ma5,
        ma20,
    )
    beichi = calc_beichi_data(df, df2)

    resp = {
        "buy_zs_huila": zs_huila['buy_zs_huila'],
        "buy_zs_tupo": zs_tupo['buy_zs_tupo'],
        "buy_v_reverse": v_reverse['buy_v_reverse'],
        "buy_five_v_reverse": five_v_fan['buy_five_v_reverse'],
        "buyMACDBCData": beichi['buyMACDBCData']
    }

    signal_map = {
        "buy_zs_huila": "回拉中枢上涨",
        "buy_zs_tupo": "突破中枢上涨",
        "buy_v_reverse": "V反上涨",
        "buy_five_v_reverse": "五浪V反上涨",
        "buyMACDBCData": "底背驰"
    }
    for signal_type in signal_map:
        signals = resp[signal_type]
        for idx in range(len(signals["date"])):
            fire_time = signals["date"][idx]
            fire_time = tz.localize(datetime.datetime.strptime(fire_time, "%Y-%m-%d %H:%M"))
            price = signals["data"][idx]
            stop_lose_price = signals["stop_lose_price"][idx]
            tag = signals["tag"][idx]
            tags = [] if tag is None else tag.split(",")
            save_a_stock_signal(
                sse,
                symbol,
                code,
                period,
                signal_map[signal_type],
                fire_time,
                price,
                stop_lose_price,
                'BUY_LONG',
                tags,
                "N/A"
            )


def signal_handler(signal_num, frame):
    logger.info("正在停止程序。")
    global is_run
    is_run = False


def run(**kwargs):
    global is_loop
    is_loop = kwargs.get("loop")
    signal.signal(signal.SIGINT, signal_handler)
    thread_list = [threading.Thread(target=monitoring_stock)]
    for thread in thread_list:
        thread.start()

    while True:
        for thread in thread_list:
            if thread.is_alive():
                time.sleep(60)
                break
        else:
            break


if __name__ == '__main__':
    try:
        run()
    finally:
        exit()
