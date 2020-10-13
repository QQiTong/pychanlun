# -*- coding: utf-8 -*-

import datetime
import re
import traceback

import numpy as np
import pandas as pd
import pydash
import pytz
from func_timeout import func_set_timeout
from loguru import logger

import pychanlun.entanglement as entanglement
from pychanlun import Duan, divergence
from pychanlun.KlineDataTool import getStockData, getGlobalFutureData, getDigitCoinData, getFutureData
from pychanlun.basic.bi import calculate_bi, FindLastFractalRegion
from pychanlun.basic.duan import calculate_duan, split_bi_in_duan
from pychanlun.basic.util import get_required_period_list, get_Line_data, get_zhong_shu_data
from pychanlun.config import config
from pychanlun.analysis.chanlun_data import ChanlunData
import pychanlun.placeholder as placeholder
from pychanlun.basic.util import str_from_timestamp

tz = pytz.timezone('Asia/Shanghai')


@func_set_timeout(120)
def get_data_v2(symbol, period, end_date=None):
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

    data_list = []
    required_period_list.reverse()
    for period_one in required_period_list:
        kline_data = get_instrument_data(symbol, period_one, end_date, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        if kline_data is None or len(kline_data) == 0:
            continue
        kline_data["time_str"] = kline_data["time"] \
            .apply(lambda value: datetime.datetime.fromtimestamp(value, tz=tz).strftime("%Y-%m-%d %H:%M"))
        length = len(data_list)
        higher_chanlun_data = data_list[-1] if length > 0 else None
        pre_duan_data = higher_chanlun_data['chanlun_data'].bi_data if higher_chanlun_data is not None else None
        pre_higher_duan_data = higher_chanlun_data['chanlun_data'].duan_data if higher_chanlun_data is not None else None
        chanlunData = ChanlunData(kline_data.time.to_list(), kline_data.open.to_list(), kline_data.close.to_list(),
                                  kline_data.low.to_list(), kline_data.high.to_list(), pre_duan_data, pre_higher_duan_data)
        kline_data['bi'] = chanlunData.bi_signal_list
        kline_data['duan'] = chanlunData.duan_signal_list
        kline_data['duan2'] = chanlunData.higher_duan_signal_list
        data_list.append({"symbol": symbol, "period": period_one, "kline_data": kline_data, "chanlun_data": chanlunData})
    if len(data_list) == 0:
        return None

    data = data_list[-1]
    kline_data = data['kline_data']

    bi_data = {'date': list(map(str_from_timestamp, chanlunData.bi_data['dt'])), 'data': chanlunData.bi_data['data']}
    duan_data = {'date': list(map(str_from_timestamp, chanlunData.duan_data['dt'])), 'data': chanlunData.duan_data['data']}
    higher_chanlun_data = {'date': list(map(str_from_timestamp, chanlunData.higher_duan_data['dt'])), 'data': chanlunData.higher_duan_data['data']}

    # 计算笔中枢
    entanglement_list = entanglement.CalcEntanglements(
        kline_data.time_str.to_list(),
        kline_data.duan.to_list(),
        kline_data.bi.to_list(),
        kline_data.high.to_list(),
        kline_data.low.to_list()
    )
    zs_data, zs_flag = get_zhong_shu_data(entanglement_list)

    # 计算段中枢
    if "duan2" in kline_data.columns:
        entanglement_list2 = entanglement.CalcEntanglements(
            kline_data.time_str.to_list(),
            kline_data.duan2.to_list(),
            kline_data.duan.to_list(),
            kline_data.high.to_list(),
            kline_data.low.to_list()
        )
    zs_data2, zs_flag2 = get_zhong_shu_data(entanglement_list2)

    daily_data = get_instrument_data(symbol, "1d", end_date)
    daily_data = pd.DataFrame(daily_data)
    daily_data = daily_data.set_index("time")
    ma5 = np.round(pd.Series.rolling(daily_data["close"], window=5).mean(), 2)
    ma20 = np.round(pd.Series.rolling(daily_data["close"], window=20).mean(), 2)

    # 计算买卖预警信号
    hui_la = entanglement.la_hui(
        entanglement_list,
        kline_data.time_str.to_list(),
        kline_data.high.to_list(),
        kline_data.low.to_list(),
        kline_data.open.to_list(),
        kline_data.close.to_list(),
        kline_data.bi.to_list(),
        kline_data.duan.to_list(),
        kline_data.duan2.to_list(),
        ma5,
        ma20
    )
    buy_zs_huila = hui_la['buy_zs_huila']
    sell_zs_huila = hui_la['sell_zs_huila']

    tu_po = entanglement.tu_po(
        entanglement_list,
        kline_data.time_str.to_list(),
        kline_data.high.to_list(),
        kline_data.low.to_list(),
        kline_data.open.to_list(),
        kline_data.close.to_list(),
        kline_data.bi.to_list(),
        kline_data.duan.to_list(),
        kline_data.duan2.to_list(),
        ma5,
        ma20
    )

    buy_zs_tupo = tu_po['buy_zs_tupo']
    sell_zs_tupo = tu_po['sell_zs_tupo']

    v_reverse = entanglement.v_reverse(
        entanglement_list,
        kline_data.time_str.to_list(),
        kline_data.high.to_list(),
        kline_data.low.to_list(),
        kline_data.open.to_list(),
        kline_data.close.to_list(),
        kline_data.bi.to_list(),
        kline_data.duan.to_list(),
        kline_data.duan2.to_list(),
        ma5,
        ma20
    )

    buy_v_reverse = v_reverse['buy_v_reverse']
    sell_v_reverse = v_reverse['sell_v_reverse']

    five_v_fan = entanglement.five_v_fan(
        kline_data.time_str.to_list(),
        kline_data.duan.to_list(),
        kline_data.bi.to_list(),
        kline_data.high.to_list(),
        kline_data.low.to_list(),
        kline_data.duan2.to_list(),
        ma5,
        ma20,
    )

    buy_five_v_reverse = five_v_fan['buy_five_v_reverse']
    sell_five_v_reverse = five_v_fan['sell_five_v_reverse']

    duan_pohuai = entanglement.po_huai(
        kline_data.time_str.to_list(),
        kline_data.high.to_list(),
        kline_data.low.to_list(),
        kline_data.open.to_list(),
        kline_data.close.to_list(),
        kline_data.bi.to_list(),
        kline_data.duan.to_list(),
        kline_data.duan2.to_list(),
        ma5,
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
            kline_data2.bi.to_list(),
            kline_data2.time_str.to_list(),
            kline_data2.high.to_list(),
            kline_data2.low.to_list(),
            kline_data2.open.to_list(),
            kline_data2.close.to_list()
        )
        if fractal_region is not None:
            fractal_region["period"] = data2["period"]

    fractal_region2 = None
    if len(data_list) > 2:
        data3 = data_list[-3]
        kline_data3 = data3["kline_data"]
        fractal_region2 = FindLastFractalRegion(
            len(kline_data3),
            kline_data3.bi.to_list(),
            kline_data3.time_str.to_list(),
            kline_data3.high.to_list(),
            kline_data3.low.to_list(),
            kline_data3.open.to_list(),
            kline_data3.close.to_list()
        )
        if fractal_region2 is not None:
            fractal_region2["period"] = data3["period"]

    resp = {
        "symbol": symbol,
        "period": period,
        "endDate": end_date,
        "dateBigLevel": [],
        "date": kline_data.time_str.to_list(),
        "open": kline_data.open.to_list(),
        "high": kline_data.high.to_list(),
        "low": kline_data.low.to_list(),
        "close": kline_data.close.to_list(),
        "bidata": bi_data,
        "duandata": duan_data,
        "higherDuanData": higher_chanlun_data,
        "higherHigherDuanData": placeholder.higherHigherDuanData,
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
        'fractal': placeholder.fractal
    }

    fractal_region = {} if fractal_region is None else fractal_region
    fractal_region2 = {} if fractal_region2 is None else fractal_region2
    resp['fractal'] = [fractal_region, fractal_region2]
    resp['notLower'] = calcNotLower(kline_data.duan.to_list(), kline_data.low.to_list())
    resp['notHigher'] = calcNotHigher(kline_data.duan.to_list(), kline_data.low.to_list())

    return resp


@func_set_timeout(60)
def get_data(symbol, period, end_date=None):
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
    for period_one in required_period_list:
        kline_data = get_instrument_data(symbol, period_one, end_date,
                                         datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        if kline_data is None or len(kline_data) == 0:
            continue

        kline_data = kline_data.iloc[:, -1000:]
        kline_data = pd.DataFrame(kline_data)
        kline_data["time_str"] = kline_data["time"] \
            .apply(lambda value: datetime.datetime.fromtimestamp(value, tz=tz).strftime("%Y-%m-%d %H:%M"))

        # 加上MACD数据
        # MACD = QA.MACD(kline_data['close'], 12, 26, 9)
        # kline_data['diff'] = MACD['DIFF'].fillna(0)
        # kline_data['dea'] = MACD['DEA'].fillna(0)
        # kline_data['macd'] = MACD['MACD'].fillna(0)
        # kline_data['jc'] = QA.CROSS(MACD['DIFF'], MACD['DEA']).fillna(0)
        # kline_data['sc'] = QA.CROSS(MACD['DEA'], MACD['DIFF']).fillna(0)

        data_list.append({"symbol": symbol, "period": period_one, "kline_data": kline_data})

    if len(data_list) == 0:
        return None

    # data_list包含了计算各个周期需要的K线数据，其中的kline_data是一个DataFrame的数据结构
    # 初始的列有: index time open high low close volume
    # time列是以秒表示的timestamp
    # 周期大的排在前面，周期小的排在后面，方便从大周期开始往小周期计算
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
            data3 = data_list[idx - 2]
            data2 = data_list[idx - 1]
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

    daily_data = get_instrument_data(symbol, "1d", end_date)
    daily_data = pd.DataFrame(daily_data)
    daily_data = daily_data.set_index("time")
    ma5 = np.round(pd.Series.rolling(daily_data["close"], window=5).mean(), 2)
    ma20 = np.round(pd.Series.rolling(daily_data["close"], window=20).mean(), 2)

    data = data_list[-1]
    data2 = data_list[-2]

    kline_data = data["kline_data"]
    kline_data2 = data2["kline_data"]

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
        ma5,
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
        ma5,
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
        ma5,
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
        ma5,
        ma20,
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
        ma5,
        ma20
    )

    buy_duan_break = duan_pohuai['buy_duan_break']
    sell_duan_break = duan_pohuai['sell_duan_break']

    # beichiData = divergence.calc_beichi_data(kline_data, kline_data2, ma5, ma20)
    # buyMACDBCData = beichiData['buyMACDBCData']
    # sellMACDBCData = beichiData['sellMACDBCData']
    #
    # buyHigherMACDBCData = {'date': [], 'data': [], 'value': [], "stop_lose_price": [], "stop_win_price": []}
    # sellHigherMACDBCData = {'date': [], 'data': [], 'value': [], "stop_lose_price": [], "stop_win_price": []}

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
        data3 = data_list[-3]
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
    time_list = list(kline_data["time"])
    time_list2 = list(kline_data2["time"])
    big_level_idx = pydash.find_index(time_list2, lambda v: v >= time_list[0])
    resp = {
        "symbol": data["symbol"],
        "period": data["period"],
        "endDate": end_date,
        "date": list(kline_data["time_str"]),
        "dateBigLevel": list(kline_data2["time_str"])[big_level_idx:],
        "open": list(kline_data["open"]),
        "high": list(kline_data["high"]),
        "low": list(kline_data["low"]),
        "close": list(kline_data["close"]),
        # "diff": list(kline_data["diff"]),
        # "dea": list(kline_data["dea"]),
        # "macd": list(kline_data["macd"]),
        # "diffBigLevel": list(kline_data2["diff"])[big_level_idx:],
        # "deaBigLevel": list(kline_data2["dea"])[big_level_idx:],
        # "macdBigLevel": list(kline_data2["macd"])[big_level_idx:],
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
        # "buyMACDBCData": buyMACDBCData,
        # "sellMACDBCData": sellMACDBCData,
        # "buyHigherMACDBCData": buyHigherMACDBCData,
        # "sellHigherMACDBCData": sellHigherMACDBCData
    }

    fractal_region = {} if fractal_region is None else fractal_region
    fractal_region2 = {} if fractal_region2 is None else fractal_region2
    resp['fractal'] = [fractal_region, fractal_region2]

    resp['notLower'] = calcNotLower(list(kline_data["duan"]), list(kline_data["low"]))
    resp['notHigher'] = calcNotHigher(list(kline_data["duan"]), list(kline_data["low"]))

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
        get_data("sz000001", "3m")
    except Exception as e:
        logger.info("Error Occurred: {0}".format(traceback.format_exc()))
    finally:
        exit()
