from datetime import datetime
from .strategy4 import doCaculate
from ..db import DBPyChanlun

if __name__ == '__main__':
    symbol = DBPyChanlun['symbol'].find_one({ 'code': 'HC2001' })
    doCaculate(symbol, None, True)