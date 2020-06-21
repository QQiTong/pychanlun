# -*- coding: utf-8 -*-

import re

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
    for period_one in required_period_list:
        kline_data = get_instrument_data(symbol, period_one, end_date)
        kline_data = pd.DataFrame(kline_data)
        print(kline_data)


if __name__ == '__main__':
    try:
        get_data("RB2010", "5m")
    finally:
        exit()
