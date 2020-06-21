# -*- coding: utf-8 -*-

import re
import pydash
import logging
import traceback

import pandas as pd

from pychanlun.basic.comm import get_required_period_list
from pychanlun.KlineDataTool import KlineDataTool
from pychanlun.config import config


def get_data(symbol, period, end_date=None):
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

    data_list = pydash.take_right_while(data_list, lambda value: len(value["kline_data"]) > 0)
    for idx in range(len(data_list)):
        data = data_list[idx]


if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        get_data("RB2010", "5m")
    except Exception as e:
        logging.info("Error Occurred: {0}".format(traceback.format_exc()))
    finally:
        exit()
