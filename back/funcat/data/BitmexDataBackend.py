import requests
import json
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
        klines = json.loads(r.text)
        return klines