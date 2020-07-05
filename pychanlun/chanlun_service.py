# -*- coding: utf-8 -*-

import re
import pydash
import logging
import traceback
import datetime

import pandas as pd
import numpy as np
from et_stopwatch import Stopwatch

from pychanlun import Duan

from func_timeout import func_set_timeout

from pychanlun.KlineDataTool import getStockData, getGlobalFutureData, getDigitCoinData, getFutureData
from pychanlun.config import config
from pychanlun.basic.bi import calculate_bi, FindLastFractalRegion
from pychanlun.basic.duan import calculate_duan, split_bi_in_duan
from pychanlun.basic.util import get_required_period_list, get_Line_data, get_zhong_shu_data
import pychanlun.entanglement as entanglement


@func_set_timeout(60)
def get_data(symbol, period, end_date=None):
    stopwatch = Stopwatch('计算数据')
    required_period_list = get_required_period_list(period)
    match_stock = re.match("(sh|sz)(\\d{6})", symbol, re.I)
    if match_stock is not None:
        get_instrument_data = getStockData
    elif symbol in config['global_future_symbol'] or symbol in config['global_stock_symbol']:
        get_instrument_data = getGlobalFutureData
    elif 'BTC' in symbol:
        get_instrument_data = getDigitCoinData
    else:
        get_instrument_data = getFutureData

    # 取数据
    data_list = []
    required_period_list.reverse()
    stopwatch = Stopwatch("%-10s %-10s %-10s" % ('读数据', symbol, period))
    for period_one in required_period_list:
        kline_data = get_instrument_data(symbol, period_one, end_date, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        if kline_data is None or len(kline_data) == 0:
            continue
        kline_data["time_str"] = kline_data["time"] \
            .apply(lambda value: datetime.datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M"))
        data_list.append({"symbol": symbol, "period": period_one, "kline_data": kline_data})
    stopwatch.stop()
    print(stopwatch)

    # data_list包含了计算各个周期需要的K线数据，其中的kline_data是一个DataFrame的数据结构
    # 初始的列有: index time open high low close volume
    # time列是以秒表示的timestamp
    # 周期大的排在前面，周期小的排在后面，方便从大周期开始往小周期计算
    stopwatch = Stopwatch("%-10s %-10s %-10s" % ('信号计算', symbol, period))
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
            data2 = data_list[idx-1]
            data = data_list[idx]
            count = len(data["kline_data"])
            bi_list = [0 for i in range(count)]
            duan_list = [0 for i in range(count)]
            duan_list2 = [0 for i in range(count)]
            calculate_duan(
                duan_list,
                list(data["kline_data"]["time"]),
                list(data2["kline_data"]["bi"]),
                list(data2["kline_data"]["time"]),
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
            data3 = data_list[idx-2]
            data2 = data_list[idx-1]
            data = data_list[idx]
            count = len(data["kline_data"])
            bi_list = [0 for i in range(count)]
            duan_list = [0 for i in range(count)]
            duan_list2 = [0 for i in range(count)]
            calculate_duan(
                duan_list,
                list(data["kline_data"]["time"]),
                list(data2["kline_data"]["bi"]),
                list(data2["kline_data"]["time"]),
                list(data["kline_data"]["high"]),
                list(data["kline_data"]["low"])
            )
            calculate_duan(
                duan_list2,
                list(data["kline_data"]["time"]),
                list(data3["kline_data"]["bi"]),
                list(data3["kline_data"]["time"]),
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
    stopwatch.stop()
    print(stopwatch)
    daily_data = get_instrument_data(symbol, "1d", end_date)
    daily_data = pd.DataFrame(daily_data)
    daily_data = daily_data.set_index("time")
    ma20 = np.round(pd.Series.rolling(daily_data["close"], window=20).mean(), 2)

    data = data_list[-1]

    kline_data = data["kline_data"]

    # 计算笔中枢
    entanglement_list = entanglement.CalcEntanglements(
        list(kline_data["time_str"]),
        list(kline_data["duan"]),
        list(kline_data["bi"]),
        list(kline_data["high"]),
        list(kline_data["low"])
    )
    zs_data, zs_flag = get_zhong_shu_data(entanglement_list)

    # 计算段中枢
    if "duan2" in kline_data.columns:
        entanglement_list2 = entanglement.CalcEntanglements(
            list(kline_data["time_str"]),
            list(kline_data["duan2"]),
            list(kline_data["duan"]),
            list(kline_data["high"]),
            list(kline_data["low"])
        )
        zs_data2, zs_flag2 = get_zhong_shu_data(entanglement_list2)

    bi_data = get_Line_data(
        list(kline_data["time_str"]),
        list(kline_data["bi"]),
        list(kline_data["high"]),
        list(kline_data["low"])
    )
    duan_data = get_Line_data(
        list(kline_data["time_str"]),
        list(kline_data["duan"]),
        list(kline_data["high"]),
        list(kline_data["low"])
    )
    duan_data2 = get_Line_data(
        list(kline_data["time_str"]),
        list(kline_data["duan2"]),
        list(kline_data["high"]),
        list(kline_data["low"])
    )

    # 计算买卖预警信号
    hui_la = entanglement.la_hui(
        entanglement_list,
        list(kline_data["time_str"]),
        list(kline_data["high"]),
        list(kline_data["low"]),
        list(kline_data["open"]),
        list(kline_data["close"]),
        list(kline_data["bi"]),
        list(kline_data["duan"]),
        list(kline_data["duan2"]),
        ma20
    )

    buy_zs_huila = hui_la['buy_zs_huila']
    sell_zs_huila = hui_la['sell_zs_huila']

    tu_po = entanglement.tu_po(
        entanglement_list,
        list(kline_data["time_str"]),
        list(kline_data["high"]),
        list(kline_data["low"]),
        list(kline_data["open"]),
        list(kline_data["close"]),
        list(kline_data["bi"]),
        list(kline_data["duan"]),
        list(kline_data["duan2"]),
        ma20
    )

    buy_zs_tupo = tu_po['buy_zs_tupo']
    sell_zs_tupo = tu_po['sell_zs_tupo']

    v_reverse = entanglement.v_reverse(
        entanglement_list,
        list(kline_data["time_str"]),
        list(kline_data["high"]),
        list(kline_data["low"]),
        list(kline_data["open"]),
        list(kline_data["close"]),
        list(kline_data["bi"]),
        list(kline_data["duan"]),
        list(kline_data["duan2"]),
        ma20
    )

    buy_v_reverse = v_reverse['buy_v_reverse']
    sell_v_reverse = v_reverse['sell_v_reverse']

    five_v_fan = entanglement.five_v_fan(
        list(kline_data["time_str"]),
        list(kline_data["duan"]),
        list(kline_data["bi"]),
        list(kline_data["high"]),
        list(kline_data["low"]),
        list(kline_data["duan2"]),
        ma20
    )

    buy_five_v_reverse = five_v_fan['buy_five_v_reverse']
    sell_five_v_reverse = five_v_fan['sell_five_v_reverse']

    duan_pohuai = entanglement.po_huai(
        list(kline_data["time_str"]),
        list(kline_data["high"]),
        list(kline_data["low"]),
        list(kline_data["open"]),
        list(kline_data["close"]),
        list(kline_data["bi"]),
        list(kline_data["duan"]),
        list(kline_data["duan2"]),
        ma20
    )

    buy_duan_break = duan_pohuai['buy_duan_break']
    sell_duan_break = duan_pohuai['sell_duan_break']

    # 顶底分型
    fractal_region = None
    if len(data_list) > 1:
        data2 = data_list[-2]
        kline_data2 = data2["kline_data"]
        fractal_region = FindLastFractalRegion(
            len(kline_data2),
            kline_data2["bi"],
            kline_data2["time_str"],
            kline_data2["high"],
            kline_data2["low"],
            kline_data2["open"],
            kline_data2["close"]
        )
        if fractal_region is not None:
            fractal_region["period"] = data2["period"]

    fractal_region2 = None
    if len(data_list) > 2:
        data3= data_list[-3]
        kline_data3 = data3["kline_data"]
        fractal_region2 = FindLastFractalRegion(
            len(kline_data3),
            kline_data3["bi"],
            kline_data3["time_str"],
            kline_data3["high"],
            kline_data3["low"],
            kline_data3["open"],
            kline_data3["close"]
        )
        if fractal_region2 is not None:
            fractal_region2["period"] = data3["period"]

    resp = {
        "symbol": data["symbol"],
        "period": data["period"],
        "endDate": end_date,
        "date": list(kline_data["time_str"]),
        "open": list(kline_data["open"]),
        "high": list(kline_data["high"]),
        "low": list(kline_data["low"]),
        "close": list(kline_data["close"]),
        "bidata": bi_data,
        "duandata": duan_data,
        "higherDuanData": duan_data2,
        "higherHigherDuanData": {"data": [], "date": []},
        "zsdata": zs_data,
        "zsflag": zs_flag,
        "duan_zsdata": zs_data2,
        "duan_zsflag": zs_flag2,
        "higher_duan_zsdata": [],
        "higher_duan_zsflag": [],
        "buy_zs_huila": buy_zs_huila,
        "sell_zs_huila": sell_zs_huila,
        "buy_zs_tupo": buy_zs_tupo,
        "sell_zs_tupo": sell_zs_tupo,
        "buy_v_reverse": buy_v_reverse,
        "sell_v_reverse": sell_v_reverse,
        "buy_five_v_reverse": buy_five_v_reverse,
        "sell_five_v_reverse": sell_five_v_reverse,
        "buy_duan_break": buy_duan_break,
        "sell_duan_break": sell_duan_break,
    }

    fractal_region = {} if fractal_region is None else fractal_region
    fractal_region2 = {} if fractal_region2 is None else fractal_region2
    resp['fractal'] = [fractal_region, fractal_region2]

    resp['notLower'] = calcNotLower(list(kline_data["duan"]), list(kline_data["low"]))
    resp['notHigher'] = calcNotHigher(list(kline_data["duan"]), list(kline_data["low"]))

    stopwatch.stop()
    logging.info(stopwatch)

    return resp


def calcNotLower(duanList, lowList):
    if Duan.notLower(duanList, lowList):
        return True
    else:
        return False


def calcNotHigher(duanList, highList):
    if Duan.notHigher(duanList, highList):
        return True
    else:
        return False


# 测试运行: python D:\development\pychanlun\pychanlun\chanlun_service.py
if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        get_data("RB2010", "5m")
    except Exception as e:
        logging.info("Error Occurred: {0}".format(traceback.format_exc()))
    finally:
        exit()
