import requests
import json
import time
import pydash
from datetime import datetime
from back.funcat.api import *
# hbdmUrl = "https://api.hbdm.com/market/history/kline"
#
# payload1 = {
#     'symbol': 'BTC_CQ',  # 合约类型， 火币季度合约
#     'period': '1min',
#     'size': 2000
# }
#
# r = requests.get(hbdmUrl, params=payload1)
# print(json.loads(r.text)['ch'])

# currentTime = int(time.time())
# print(currentTime)
#
# dateStamp = int(time.mktime(time.strptime("2019-08-25 12:55", "%Y-%m-%d %H:%M")))
# print(dateStamp)
# a = [1,2,3,4,3]
#
# result = pydash.find_index(a,lambda i:i ==3)
# print(result)

# result = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
# print(result)
a = [0,1,2,3,4,5,6]
b = [9,8,7,6,5,4,3]
r = CROSS(a, b)
print(r.series)