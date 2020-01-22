# -*- coding: utf-8 -*-

from datetime import datetime
from pychanlun.monitor.strategy3 import doCaculate
from pychanlun.db import DBPyChanlun

if __name__ == '__main__':
    symbol = DBPyChanlun['symbol'].find_one({ 'code': 'FU2001' })
    inspect_time = datetime(2019, 7, 31)
    doCaculate(symbol, inspect_time, True)
