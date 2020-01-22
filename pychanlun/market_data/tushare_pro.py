# -*- coding: utf-8 -*-

from pychanlun.market_data.api import MarketDataApi
import tushare as ts

ts.set_token('e5260ca117a89e6dbf87c7288c688c6665ea97f7ae6d498dc3b3544f')

class TushareProDataApi:

    def __init__(self):
        self.pro = ts.pro_api()

    def trade_cal(self, exchange, start_date, end_date, is_open):
        return self.pro.query('trade_cal', exchange=exchange, start_date=start_date, end_date=end_date, is_open=is_open)

    def stock_basic(self, is_hs='', list_status='L', exchange=''):
        return self.pro.query('stock_basic', is_hs=is_hs, list_status=list_status, exchange=exchange)

    def price_bar(self, ts_code, start_date='', end_date='', asset='E', adj=None, freq='1min'):
        return ts.pro_bar(ts_code=ts_code, start_date=start_date, end_date=end_date, adj=adj, freq=freq)
