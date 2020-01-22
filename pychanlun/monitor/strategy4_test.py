# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import sys
from pychanlun.monitor.strategy4 import doCaculate
from pychanlun.db import DBPyChanlun

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format='%(asctime)s %(threadName)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    symbol = DBPyChanlun['symbol'].find_one({ 'code': 'RU2001' })
    doCaculate(symbol, None, True)
