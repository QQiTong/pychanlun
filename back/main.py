from back.Calc import Calc
from back.KlineDataTool import KlineDataTool
from jqdatasdk import *
from datetime import datetime
import time


# 用于调试
class Main:
    # calc = Calc()
    # calc.calcData('3min')
    auth('13088887055', 'chanlun123456')
    klineDataTool = KlineDataTool()
    # result = klineDataTool.getFutureData('RB1910.XSGE', '240m', 200)
    # result = klineDataTool.getKlineData('3min',200)

    df = get_price('RB1910.XSGE', frequency='1d', end_date=datetime.now(), count=200,
                   fields=['open', 'high', 'low', 'close', 'volume'])

    # un_time = time.mktime(df.index[-1].timetuple())
    # un_time1 = time.mktime(df.index[-2].timetuple())
    # un_time2 = time.mktime(df.index[-3].timetuple())
    # un_time3 = time.mktime(df.index[-4].timetuple())
    # print(result[-4])
    # print(result[-3])
    # for i in range(len(df.index)):
    # print(un_time)
    # print(un_time1)
    # print(result[-1])
    print(df)
