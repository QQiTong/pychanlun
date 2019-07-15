import rqdatac as rq
from rqdatac import *
from datetime import datetime
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

test = rq.get_price('RB88',frequency='1m',fields=['open', 'high', 'low', 'close', 'volume'],end_date=datetime.now())
# test = rq.futures.history_bars('RB88', bar_count=300, frequency='1m', fields=['open', 'high', 'low', 'close', 'volume'], skip_suspended=True, include_now=False)('RB88.XSGE',frequency='1m',fields=['open', 'high', 'low', 'close', 'volume'],end_date=datetime.now(),bar_count=300)


# test = rq.futures.get_dominant('rb', end_date=datetime.now())
print(test)
