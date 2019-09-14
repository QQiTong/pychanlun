import rqdatac as rq
import requests
import json
import numpy as np
from .backend import DataBackend

from ..utils import lru_cache, get_str_date_from_int, get_int_date

class RicequantDataBackend(DataBackend):
    def __init__(self):
        pass

    @lru_cache(maxsize=4096)
    def get_price(self, code, start, end, period):
        df = rq.get_price(code, frequency=period, fields=['open', 'high', 'low', 'close', 'volume'], start_date=start, end_date=end)
        df['time'] = df.index.tz_localize('Asia/Shanghai')
        df.set_index("time", inplace=True)
        return df