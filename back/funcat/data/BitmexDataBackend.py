import requests
import json
import numpy as np
from .backend import DataBackend

from ..utils import lru_cache, get_str_date_from_int, get_int_date

class BitmexDataBackend(DataBackend):

    def __init__(self):
        self.endpoint = "https://www.bitmex.com/api/udf/history"

    @lru_cache(maxsize=4096)
    def get_price(self, code, start, end, period):
        payload = {
            'resolution': period,
            'symbol': code,  # 合约类型，如永续合约:XBTUSD
            'from': start,
            'to': end
        }
        header = {"accept": "*/*", "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "origin": "https://static.bitmex.com",
            "referer": "https://static.bitmex.com/",
            }
        r = requests.get(self.endpoint, params=payload, headers=header)
        prices = json.loads(r.text)
        t = prices.get('t', [])
        o = prices.get('o', [])
        c = prices.get('c', [])
        h = prices.get('h', [])
        l = prices.get('l', [])
        v = prices.get('v', [])
        rec = np.zeros((len(t),), dtype=[('time', 'int32'), ('open', 'float32'), ('close', 'float32'), ('high', 'float32'), ('low', 'float32'), ('volume', 'float32')])
        rec[:] = list(zip(t, o, c, h, l, v))
        return rec