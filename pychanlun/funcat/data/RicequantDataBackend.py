
# -*- coding: utf-8 -*-

import rqdatac as rq
import requests
import json
import numpy as np
from pychanlun.funcat.data.backend import DataBackend

from pychanlun.funcat.utils import lru_cache, get_str_date_from_int, get_int_date

class RicequantDataBackend(DataBackend):
    def __init__(self):
        pass

    def get_price(self, code, start, end, period):
        df = rq.get_price(code, frequency=period, fields=['open', 'high', 'low', 'close', 'volume'], start_date=start, end_date=end)
        if df is None:
            return None
        df['time'] = df.index.tz_localize('Asia/Shanghai')
        df.set_index("time", inplace=True)
        return df

    @lru_cache(maxsize=1000)
    def get_trading_hours(self, code, trading_date, market='cn', magic = 0):
        return rq.get_trading_hours(code, trading_date, expected_fmt='datetime', market=market)

    @lru_cache(maxsize=1000)
    def get_trading_dates(self, start_date, end_date, market='cn'):
        return rq.get_trading_dates(start_date, end_date, market)

    @lru_cache(maxsize=1000)
    def get_next_trading_date(self, trading_date, n=1, market='cn'):
        return rq.get_next_trading_date(trading_date)
