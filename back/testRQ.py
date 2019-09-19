import rqdatac as rq
from rqdatac import *
import numpy as np

import json
from datetime import datetime, timedelta

# rq.init('license','R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=','rqdatad-pro.ricequant.com', 16011)

init('license',
     'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
     ('rqdatad-pro.ricequant.com', 16011))

'''
 rq_symbol,
            frequency=rq_interval,
            fields=["open", "high", "low", "close", "volume"],
            start_date=start,
            end_date=end,
            adjust_type="none"
            
df = get_price(symbol, frequency=period, end_date=datetime.now(), count=size,
                       fields=['open', 'high', 'low', 'close', 'volume'])            
'''
period = '3m'
# timeDeltaMap = {
#     '1m':-31,
#     '60m':-31,
#     '1d':-180
# }
# end = datetime.now() + timedelta(1)
end = datetime.now() + timedelta(1)
df = rq.get_price('AU1912', frequency='240m', fields=['open', 'high', 'low', 'close', 'volume'],
                  start_date='2019-08-28', end_date='2019-09-12')
ohlc_dict = {
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
}
# df.index = pd.DatetimeIndex(df.index)

# 聚合k线
# df = df.resample('4H', closed='left', label='left') \
#     .agg(ohlc_dict).dropna(how='any')
print(df)

# 品种列表

symbolListFuture = ['RB2001', 'HC2001', 'RU2001', 'NI1911', 'FU2001', 'ZN1911', 'SP2001', 'BU1912',
                    # 'CU1910', 'AL1910','AU1912', 'AG1912',
                    'MA2001', 'TA2001', 'SR2001', 'OI2001', 'AP1910', 'CF2001',
                    'M2001', 'I2001', 'EG2001', 'J2001', 'JM2001', 'PP2001', 'L2001'
                    # 'RM2001','FG2001', 'ZC1911','CJ1912','Y2001', 'P2001','L2001', 'C2001','V2001', 'A2001', 'B1910'
                    ]
symbolList = ['RB', 'HC', 'RU', 'NI', 'FU', 'ZN', 'SP', 'BU',
              'MA', 'TA', 'SR', 'OI', 'AP', 'CF',
              'M', 'I', 'EG', 'J', 'JM', 'PP', 'L'
              ]

# dominantSymbolInfoList = []
# for i in range(len(symbolList)):
#     df = rq.futures.get_dominant(symbolList[i], start_date=None, end_date=None,rule=0)
#     dominantSymbol = df[-1]
#     dominantSymbolInfo = rq.instruments(dominantSymbol)
#     dominantSymbolInfoList.append(dominantSymbolInfo.__dict__)
# print(json.dumps(dominantSymbolInfoList))


# for i in range(len(dominantSymbolInfoList)):
#     print(dominantSymbolInfoList[i])
# print(json.dumps(dominantSymbolInfoList))
# cols=[x for i,x in enumerate(df.index) if '23:00:00' in str(df.index[i])]
# 利用enumerate对row0进行遍历，将含有数字3的列放入cols中
# print(cols)
# # print(str(df.index[0]))
# #
# df2 = df.drop(cols)
# print(df2)
