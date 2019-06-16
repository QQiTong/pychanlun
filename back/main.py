from back.Calc import Calc
from back.KlineDataTool import KlineDataTool
from jqdatasdk import *

# 用于调试
class Main:
    # calc = Calc()
    # calc.calcData('3min')
    auth('13088887055', 'chanlun123456')
    klineDataTool = KlineDataTool()
    klineDataTool.getFutureData('SP9999.XSGE','1m',200)
