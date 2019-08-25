import requests
import json

hbdmUrl = "https://api.hbdm.com/market/history/kline"

payload1 = {
    'symbol': 'BTC_CQ',  # 合约类型， 火币季度合约
    'period': '1min',
    'size': 2000
}

r = requests.get(hbdmUrl, params=payload1)
print(json.loads(r.text)['ch'])
