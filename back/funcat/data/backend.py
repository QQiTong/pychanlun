# -*- coding: utf-8 -*-
#

class DataBackend(object):
    def get_price(self, code, start, end, period):
        """
        :param code: e.g. 000002.XSHE
        :param start: 20160101
        :param end: 20160201
        :param period: 1m 1d 5m 15m ...
        :returns:
        :rtype: numpy.rec.array
        """
        raise NotImplementedError
