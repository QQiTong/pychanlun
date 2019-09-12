import rqdatac as rq
from rqdatac import *
from datetime import datetime,timedelta
# rq.init('license','R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=','rqdatad-pro.ricequant.com', 16011)

init('license', 'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
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
end = datetime.now() + timedelta(1)
df = rq.get_price('RB2001',frequency='240m',fields=['open', 'high', 'low', 'close', 'volume'],start_date='2019-08-28',end_date=end)
print(df)


cols=[x for i,x in enumerate(df.index) if '23:00:00' in str(df.index[i])]
#利用enumerate对row0进行遍历，将含有数字3的列放入cols中
print(cols)
# print(str(df.index[0]))
#
df2 = df.drop(cols)
print(df2)
