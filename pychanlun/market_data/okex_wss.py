import websocket
import zlib    #压缩相关的库
import json
import threading
import hashlib
import time
import logging
from pychanlun.db import DBPyChanlun
from pymongo import UpdateOne
from datetime import datetime, timedelta

import pytz


#输入OKEx账户的api key与secret key（v1版本）
api_key=''
secret_key =''

#解压函数
def inflate(data):
    decompress = zlib.decompressobj(-zlib.MAX_WBITS)
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated

#签名函数，订阅个人信息，买卖等都需要签名
def buildMySign(params,secretKey):
    sign = ''
    for key in sorted(params.keys()):
        sign += key + '=' + str(params[key]) +'&'
    return  hashlib.md5((sign+'secret_key='+secretKey).encode("utf-8")).hexdigest().upper()

#返回签名的信息
def wsGetAccount(channel,api_key,secret_key):
    params = {
      'api_key':api_key,
    }
    sign = buildMySign(params,secret_key)
    return "{'event':'addChannel','channel':'"+channel+"','parameters':{'api_key':'"+api_key+"','sign':'"+sign+"'}}"


#每当有消息推送时，就会触发，信息包含为message，注意在这里也可以使用ws.send()发送新的信息。
def on_message(ws, message):
    try:
        inflated = inflate(message).decode('utf-8')  #将okex发来的数据解压
    except Exception as e:
        print(e)
    if inflated == '{"event":"pong"}':  #判断推送来的消息类型：如果是服务器的心跳
            print("Pong received.")
            return
    global trade
    try:
        msgs = json.loads(inflated)
        # print('消息',msgs)
        handleMsg(msgs)
    except Exception as e:
        print(e)
'''
消息 {'table': 'swap/candle900s', 'data': 
[{'candle': ['2020-03-19T07:0:00.000Z', '5412.8', '5452.9', '5408.9', '5441.2', '58578', '1077.0245'], 'instrument_id': 'BTC-USD-SWAP'}]}
'''
def handleMsg(msg):
    # code = msg['data'][0]['instrument_id']
    code = 'BTC'
    if 'table' not in msg:
        return
    # 1分钟
    if msg['table'] == 'swap/candle60s':
        period = '1m'
    # 3分钟
    if msg['table'] == 'swap/candle180s':
        period = '3m'
    # 5分钟
    if msg['table'] == 'swap/candle300s':
        period = '5m'
    # 15分钟
    if msg['table'] == 'swap/candle900s':
        period = '15m'
    # 30分钟
    if msg['table'] == 'swap/candle1800s':
        period = '30m'
    # 60分钟
    if msg['table'] == 'swap/candle3600s':
        period = '60m'
    # 240分钟
    if msg['table'] == 'swap/candle14400s':
        period = '240m'
    # 1day
    if msg['table'] == 'swap/candle86400s':
        period = '1d'
    # 1week
    if msg['table'] == 'swap/candle604800s':
        period = '1w'
    candle = msg['data'][0]['candle']
    save_data(code,period,candle)

    return


def save_data(code, period, candle):
    logging.info("保存 %s %s %s" % (code, period, candle))
    batch = []
    date = datetime.strptime(candle[0], "%Y-%m-%dT%H:%M:%S.%fZ")
    tz = pytz.timezone('Asia/Shanghai')
    batch.append(UpdateOne({
        "_id": date
    }, {
        "$set": {
            "open": float(candle[1]),
            "close": float(candle[2]),
            "high": float(candle[3]),
            "low": float(candle[4]),
            "volume": float(candle[5])
        }
    }, upsert=True))
    if len(batch) > 0:
        DBPyChanlun["%s_%s" % (code, period)].bulk_write(batch)
        batch = []


#出现错误时执行
def on_error(ws, error):
    print(error)

#关闭连接时执行
def on_close(ws):
    print("### closed ###")

#开始连接时执行，需要订阅的消息和其它操作都要在这里完成
def on_open(ws):
    print('socket已连接：订阅行情数据')
    # 1分钟
    ws.send('{"op": "subscribe", "args": ["swap/candle60s:BTC-USD-SWAP"]}')
    # 3分钟
    ws.send('{"op": "subscribe", "args": ["swap/candle180s:BTC-USD-SWAP"]}')
    # 5分钟
    ws.send('{"op": "subscribe", "args": ["swap/candle300s:BTC-USD-SWAP"]}')
    # 15分钟
    ws.send('{"op": "subscribe", "args": ["swap/candle900s:BTC-USD-SWAP"]}')
    # 30分钟
    ws.send('{"op": "subscribe", "args": ["swap/candle1800s:BTC-USD-SWAP"]}')
    # 1小时
    ws.send('{"op": "subscribe", "args": ["swap/candle3600s:BTC-USD-SWAP"]}')
    # 2小时
    # ws.send('{"op": "subscribe", "args": ["swap/candle7200s:BTC-USD-SWAP"]}')
    # 4小时
    ws.send('{"op": "subscribe", "args": ["swap/candle14400s:BTC-USD-SWAP"]}')
    # 6小时
    # ws.send('{"op": "subscribe", "args": ["swap/candle21600s:BTC-USD-SWAP"]}')
    # 12小时
    # ws.send('{"op": "subscribe", "args": ["swap/candle43200s:BTC-USD-SWAP"]}')
    # 1day
    ws.send('{"op": "subscribe", "args": ["swap/candle86400s:BTC-USD-SWAP"]}')
    # 1week
    ws.send('{"op": "subscribe", "args": ["swap/candle604800s:BTC-USD-SWAP"]}')

#发送心跳数据
def sendHeartBeat(ws):
    ping = '{"event":"ping"}'
    while(True):
        time.sleep(30) #每隔30秒交易所服务器发送心跳信息
        sent = False
        while(sent is False): #如果发送心跳包时出现错误，则再次发送直到发送成功为止
            try:
                ws.send(ping)
                sent = True
                print("Ping sent.")
            except Exception as e:
                print(e)

#创建websocket连接
def ws_main():
    websocket.enableTrace(True)
    host = "wss://real.okex.com:8443/ws/v3"
    ws = websocket.WebSocketApp(host,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    threading.Thread(target=sendHeartBeat, args=(ws,)).start() #新建一个线程来发送心跳包
    ws.run_forever(http_proxy_host='127.0.0.1', http_proxy_port=10809)    #开始运行


if __name__ == "__main__":
    threading.Thread(target=ws_main).start()
