import rqdatac as rq
import requests
import json
import numpy as np
from .backend import DataBackend

from ..utils import lru_cache, get_str_date_from_int, get_int_date

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

    def get_trading_hours(self, code, trading_date, market='cn'):
        return rq.get_trading_hours(code, trading_date, expected_fmt='datetime', market=market)