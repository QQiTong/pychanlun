import requests
import json

url = "http://api.zb.cn/data/v1/kline?market=btc_usdt"


def getKlineData():
    para = {"type": "1min"}
    header = {}
    r = requests.get(url, params=para, headers=header, )
    # verify=True适用于服务端的ssl证书验证，verify=False为关闭ssl验证
    # print('get请求获取的响应结果json类型', r.text)
    # print("get请求获取响应头", r.headers['Content-Type'])
    if r.status_code == 200:
        json_r = r.json()
        print("接口请求结果:", json_r)
        return json_r
    else:
        print("接口请求出错!")
