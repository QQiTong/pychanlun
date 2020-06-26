# -*- coding: utf-8 -*-

import re
import pydash
import logging
import traceback
import datetime

import pandas as pd
from et_stopwatch import Stopwatch

from pychanlun.KlineDataTool import KlineDataTool
from pychanlun.config import config
from pychanlun.basic.bi import calculate_bi
from pychanlun.basic.duan import calculate_duan, split_bi_in_duan
from pychanlun.basic.util import get_required_period_list, get_Line_data, get_zhong_shu_data
import pychanlun.entanglement as entanglement


def get_data(symbol, period, end_date=None):
    stopwatch = Stopwatch('计算数据')
    klineDataTool = KlineDataTool()
    required_period_list = get_required_period_list(period)
    match_stock = re.match("(sh|sz)(\\d{6})", symbol, re.I)
    if match_stock is not None:
        get_instrument_data = klineDataTool.getStockData
    elif symbol in config['global_future_symbol'] or symbol in config['global_stock_symbol']:
        get_instrument_data = klineDataTool.getGlobalFutureData
    elif 'BTC' in symbol:
        get_instrument_data = klineDataTool.getDigitCoinData
    else:
        get_instrument_data = klineDataTool.getFutureData

    # 取数据
    data_list = []
    required_period_list.reverse()
    for period_one in required_period_list:
        kline_data = get_instrument_data(symbol, period_one, end_date)
        kline_data = pd.DataFrame(kline_data)
        data_list.append({"symbol": symbol, "period": period_one, "kline_data": kline_data})

    # data_list包含了计算各个周期需要的K线数据，其中的kline_data是一个DataFrame的数据结构
    # 初始的列有: index time open high low close volume
    # time列是以秒表示的timestamp
    # 周期大的排在前面，周期小的排在后面，方便从大周期开始往小周期计算
    small_period_list = ['1m', '3m', '5m', '15m', '30m', '60m']

    data_list = pydash.take_right_while(data_list, lambda value: len(value["kline_data"]) > 0)
    for idx in range(len(data_list)):
        if idx == 0:
            data = data_list[idx]
            count = len(data["kline_data"])
            bi_list = [0 for i in range(count)]
            duan_list = [0 for i in range(count)]
            calculate_bi(
                bi_list,
                list(data["kline_data"]["high"]),
                list(data["kline_data"]["low"]),
                list(data["kline_data"]["open"]),
                data["kline_data"]["close"],
                True if period in small_period_list else False
            )
            data["kline_data"]["bi"] = bi_list
            data["kline_data"]["duan"] = duan_list
        elif idx == 1:
            data2 = data_list[idx-1]
            data = data_list[idx]
            count = len(data["kline_data"])
            bi_list = [0 for i in range(count)]
            duan_list = [0 for i in range(count)]
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

    data = data_list[-1]
    kline_data = data["kline_data"]

    time_str = kline_data["time"].apply(lambda value: datetime.datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M"))

    # 计算笔中枢
    entanglement_list = entanglement.CalcEntanglements(
        list(time_str),
        list(kline_data["duan"]),
        list(kline_data["bi"]),
        list(kline_data["high"]),
        list(kline_data["low"])
    )
    zs_data, zs_flag = get_zhong_shu_data(entanglement_list)

    # 计算段中枢
    if "duan2" in kline_data.columns:
        entanglement_list2 = entanglement.CalcEntanglements(
            list(time_str),
            list(kline_data["duan2"]),
            list(kline_data["duan"]),
            list(kline_data["high"]),
            list(kline_data["low"])
        )
        zs_data2, zs_flag2 = get_zhong_shu_data(entanglement_list2)

    bi_data = get_Line_data(
        list(time_str),
        list(kline_data["bi"]),
        list(kline_data["high"]),
        list(kline_data["low"])
    )
    duan_data = get_Line_data(
        list(time_str),
        list(kline_data["duan"]),
        list(kline_data["high"]),
        list(kline_data["low"])
    )
    duan_data2 = get_Line_data(
        list(time_str),
        list(kline_data["duan2"]),
        list(kline_data["high"]),
        list(kline_data["low"])
    )

    resp = {
        "symbol": data["symbol"],
        "period": data["period"],
        "endDate": end_date,
        "date": list(time_str),
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
        "buy_zs_huila": {"data": [], "date": []},
        "sell_zs_huila": {"data": [], "date": []},
        "buy_zs_tupo": {"data": [], "date": []},
        "sell_zs_tupo": {"data": [], "date": []},
        "buy_v_reverse": {"data": [], "date": []},
        "sell_v_reverse": {"data": [], "date": []},
        "buy_five_v_reverse": {"data": [], "date": []},
        "sell_five_v_reverse": {"data": [], "date": []},
        "buy_duan_break": {"data": [], "date": []},
        "sell_duan_break": {"data": [], "date": []},
    }
    stopwatch.stop()
    logging.info(stopwatch)

    return resp


# 测试运行: python D:\development\pychanlun\pychanlun\chanlun_controller.py
if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        get_data("RB2010", "5m")
    except Exception as e:
        logging.info("Error Occurred: {0}".format(traceback.format_exc()))
    finally:
        exit()
