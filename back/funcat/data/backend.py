# -*- coding: utf-8 -*-
#

class DataBackend(object):
    def get_price(self, code, start, end, period):
        raise NotImplementedError

    def get_trading_hours(self, code, trading_date, market='cn'):
        raise NotImplementedError

    def get_trading_dates(self, start_date, end_date, market='cn'):
        raise NotImplementedError