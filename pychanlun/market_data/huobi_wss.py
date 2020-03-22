import gzip

import websocket
import zlib    #压缩相关的库
import json
import threading
import hashlib
import time

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
        inflated = gzip.decompress(message).decode('utf-8')
        jsonObj = json.loads(inflated)
    except Exception as e:
        print(e)
    if inflated == '{"ping":1584593987417}':  #判断推送来的消息类型：如果是服务器的心跳
            print("Ping received.")

            return
    global trade
    try:
        # msgs = json.loads(inflated)
        print('消息',inflated)
        # for msg in msgs:
        #     if 'addChannel' == msg["channel"]: #判断推送来的消息类型：如果是订阅成功信息
        #         print(msg["data"]["channel"] + " subscribed.")
        #     if 'ok_sub_futureusd_btc_trade_quarter' == msg["channel"]: #判断推送来的消息类型：如果是订阅的数据
        #         for data in msg["data"]:
        #             trade = data
                    # print(trade[3], trade[1]) #打印价格和时间信息到控制台
    except Exception as e:
        print(e)

#出现错误时执行
def on_error(ws, error):
    print(error)

#关闭连接时执行
def on_close(ws):
    print("### closed ###")

#开始连接时执行，需要订阅的消息和其它操作都要在这里完成
def on_open(ws):
    print('haha')
    # 订阅1根k线 推送
    ws.send('{ "sub": "market.BTC.kline.1min", "id": "id1" }')
    # 订阅1根k线 推送


#发送心跳数据
def sendHeartBeat(ws):
    ping = '{"pong": 18212558000}'
    while(True):
        time.sleep(5) #每隔30秒交易所服务器发送心跳信息
        sent = False
        while(sent is False): #如果发送心跳包时出现错误，则再次发送直到发送成功为止
            try:
                ws.send(ping)
                sent = True
                print("Pong sent.")
            except Exception as e:
                print(e)

#创建websocket连接
def ws_main():
    websocket.enableTrace(True)
    # 这个地址要翻墙
    # host = "wss://www.hbdm.com/ws"
    # 这个地址不用翻墙
    host = "wss://www.btcgateway.pro/ws"
    ws = websocket.WebSocketApp(host,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    threading.Thread(target=sendHeartBeat, args=(ws,)).start() #新建一个线程来发送心跳包
    # ws.run_forever(http_proxy_host='127.0.0.1', http_proxy_port=10809)    #开始运行
    ws.run_forever()

if __name__ == "__main__":
    trade = 0
    threading.Thread(target=ws_main).start()
    while True:
        #这里是需要进行的任务，下单的策略可以安排在这里
        time.sleep(3)
        # print(trade[3], trade[1]) #打印价格和时间信息到控制台
        # Do something