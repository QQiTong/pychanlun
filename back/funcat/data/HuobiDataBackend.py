import requests
import json
import pandas as pd
import numpy as np
from .backend import DataBackend

from ..utils import lru_cache, get_str_date_from_int, get_int_date

class HuobiDataBackend(DataBackend):

    def __init__(self):
        '''
        period 1min, 5min, 15min, 30min, 60min,4hour,1day, 1mon
        symbol BTC_CW 当周合约 BTC_NW 次周合约 BTC_CQ 季度合约
        '''
        self.endpoint = "https://api.hbdm.com/market/history/kline"

    @lru_cache(maxsize=4096)
    def get_price(self, code, start, end, period):
        proxies = {'http': '127.0.0.1:10809', 'https': '127.0.0.1:10809'}
        payload = {
            'period': period,
            'symbol': code,
            'size': end - start
        }
        r = requests.get(self.endpoint, params=payload,proxies=proxies, verify=False)
        retJson = json.loads(r.text)
        data = retJson['data']
        recdata = []
        for item in data:
            recdata.append((item['id'], item['open'], item['close'], item['high'], item['low'], item['vol']))
        rec = np.rec.array(recdata, dtype=[('time', 'int32'), ('open', 'float32'), ('close', 'float32'), ('high', 'float32'), ('low', 'float32'), ('volume', 'float32')])
        df = pd.DataFrame.from_records(rec)
        df['time'] = pd.to_datetime(df.time.values, unit='s', utc=True).tz_convert('Asia/Shanghai')
        df.set_index("time", inplace=True)
        return df