# -*- coding: utf-8 -*-

import os
import sys
import time

import geventwebsocket
from flask import Flask, request, Response
from gevent.pywsgi import WSGIServer
from waitress import serve

import json
import numpy as np
from rqdatac import *
from pychanlun.Calc import Calc
from pychanlun.config import config
import rqdatac as rq
from pychanlun.monitor.BusinessService import businessService
from flask_sockets import Sockets
from geventwebsocket.handler import WebSocketHandler

app = Flask(__name__)
sockets = Sockets(app)
# curl -X GET 'http://127.0.0.1:5000/api/stock_data?symbol=RB2005&period=5m'

# socket 路由，访问url是： ws://localhost:5000/echo
@sockets.route('/control')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        clientEvent = json.loads(message)['event']
        try:
            if clientEvent == 'changeList':
                while True:
                    changeListResult = businessService.getChangeList()
                    result = {
                        'event': 'changeList',
                        'data': changeListResult
                    }
                    # 每隔1秒更新价格信息
                    ws.send(json.dumps(result))
                    time.sleep(5)
        except geventwebsocket.exceptions.WebSocketError as e:
            pass
# -------------------------------通用接口-----------------------------------
@app.route('/api/stock_data')
def data():
    calc = Calc()
    period = request.args.get("period")
    symbol = request.args.get("symbol")
    endDate = request.args.get("endDate")
    result = calc.calcData(period, symbol, False, endDate)
    return Response(json.dumps(result), mimetype='application/json')
@app.route('/api/save_stock_data')
def save_stock_date():
    calc = Calc()
    period = request.args.get("period") or "1min"
    symbol = request.args.get("symbol") or "BTC_CQ"
    result = calc.calcData(period, symbol, True)
    return Response(json.dumps(result), mimetype='application/json')

# --------------------------------期货部分------------------------------------
# 获取主力合约
# curl -X GET http://127.0.0.1:5000/api/dominant
@app.route('/api/dominant')
def dominant():
    dominantSymbolInfoList = businessService.getDoinantSynmbol()
    return Response(json.dumps(dominantSymbolInfoList), mimetype='application/json')


# 获取所有背驰列表
@app.route('/api/get_future_signal_list')
def get_future_signal_list():
    strategyType = request.args.get("strategyType") or "0"
    futureSignalList = businessService.getFutureSignalList(strategyType)
    return Response(json.dumps(futureSignalList), mimetype='application/json')


# 获取涨跌幅信息
@app.route('/api/get_change_list')
def get_change_list():
    changeListResult = businessService.getChangeList()
    return Response(json.dumps(changeListResult), mimetype='application/json')


# 新增持仓信息
@app.route('/api/create_position', methods=["POST"])
def create_position():
    position = request.get_json()
    inserted_id = businessService.createPosition(position)
    res = {
        "id": str(inserted_id)
    }
    return Response(json.dumps(res), mimetype='application/json')


# 更新持仓信息
@app.route('/api/update_position', methods=["POST"])
def update_position():
    position = request.get_json()
    businessService.updatePosition(position)
    res = {
        "code": "ok"
    }
    return Response(json.dumps(res), mimetype='application/json')
# 更新持仓状态
@app.route('/api/update_position_status')
def update_position_status():
    id = request.args.get("id")
    status = request.args.get("status")
    businessService.updatePositionStatus(id,status)
    res = {
        "code": "ok"
    }
    return Response(json.dumps(res), mimetype='application/json')


# 查询持仓列表
@app.route('/api/get_position_list')
def get_position_list():
    status = request.args.get("status")
    page = int(request.args.get("page") or "1")
    # 每页显示的条目
    size = int(request.args.get("size") or "10")
    positionList = businessService.getPositionList(status, page,size)
    return Response(json.dumps(positionList), mimetype='application/json')

# 跟据单个持仓
@app.route('/api/get_position')
def get_position():
    symbol = request.args.get("symbol")
    period = request.args.get("period") or "all"
    status = request.args.get("status")
    singlePosition = businessService.getPosition(symbol, period, status)
    return Response(json.dumps(singlePosition), mimetype='application/json')

# 查询期货级别多空方向列表
@app.route('/api/get_future_level_direction_list')
def get_future_level_direction():
    levelDirectionList = businessService.getLevelDirectionList()
    return Response(json.dumps(levelDirectionList), mimetype='application/json')


# 新增预判信息
@app.route('/api/create_future_prejudge_list', methods=["POST"])
def create_prejudge_list():
    futurePrejudgeData = request.get_json()
    inserted_id = businessService.createFuturePrejudgeList(futurePrejudgeData['endDate'],futurePrejudgeData['prejudgeList'])
    res = {
        "id": str(inserted_id)
    }
    return Response(json.dumps(res), mimetype='application/json')

# 获取预判信息列表
@app.route('/api/get_future_prejudge_list')
def get_future_prejudge_list():
    endDate = request.args.get("endDate")
    futurePrejudgeList = businessService.getFuturePrejudgeList(endDate)
    return Response(json.dumps(futurePrejudgeList), mimetype='application/json')

# 更新预判信息列表
@app.route('/api/update_future_prejudge_list', methods=["POST"])
def update_future_prejudge_list():
    futurePrejudgeData = request.get_json()
    businessService.updateFuturePrejudgeList(futurePrejudgeData['id'],futurePrejudgeData['prejudgeList'])
    res = {
        "code": "ok"
    }
    return Response(json.dumps(res), mimetype='application/json')



# --------------------股票部分----------------------------------------------
# 获取股票信号列表
@app.route('/api/get_stock_signal_list')
def get_stock_signal_list():
    page = int(request.args.get("page") or "1")
    if page <= 0: page = 1
    stockSignalList = businessService.getStockSignalList(page)
    return Response(json.dumps(stockSignalList), mimetype='application/json')


# 查询股票持仓列表
@app.route('/api/get_stock_position_list')
def get_stock_position_list():
    status = request.args.get("status")
    page = int(request.args.get("page") or "1")
    # 每页显示的条目
    size = int(request.args.get("size") or "10")
    # print("status--->", status, page, size)
    stockPositionList = businessService.getStockPositionList(status, page,size)
    return Response(json.dumps(stockPositionList), mimetype='application/json')


# 查询单个股票持仓
@app.route('/api/get_stock_position')
def get_stock_position():
    symbol = request.args.get("symbol")
    period = request.args.get("period") or "all"
    status = request.args.get("status")
    singlePosition = businessService.getStockPosition(symbol, period,status)
    return Response(json.dumps(singlePosition), mimetype='application/json')

# 新增股票持仓信息
@app.route('/api/create_stock_position', methods=["POST"])
def create_stock_position():
    position = request.get_json()
    inserted_id = businessService.createStockPosition(position)
    res = {
        "id": str(inserted_id)
    }
    return Response(json.dumps(res), mimetype='application/json')


# 更新股票持仓信息
@app.route('/api/update_stock_position', methods=["POST"])
def update_stock_position():
    position = request.get_json()
    businessService.updateStockPosition(position)
    res = {
        "code": "ok"
    }
    return Response(json.dumps(res), mimetype='application/json')

# 更新股票持仓状态
@app.route('/api/update_stock_position_status')
def update_stock_position_status():
    id = request.args.get("id")
    status = request.args.get("status")
    businessService.updateStockPositionStatus(id,status)
    res = {
        "code": "ok"
    }
    return Response(json.dumps(res), mimetype='application/json')


def run(**kwargs):
    port = kwargs.get("port", 5000)
    # 程序启动初始化主力合约信息,不需要每次都请求
    businessService.initDoinantSynmbol()
    # 生产模式运行，用waitress服务器
    serve(app, host='0.0.0.0', port=port)
    # 实际测试发现waitress比WSGIServer快一点
    # http_serv = WSGIServer(("0.0.0.0", port), app, handler_class=WebSocketHandler)
    # http_serv.serve_forever()


if __name__ == '__main__':
    # 开发模式运行，用内置服务器
    run()
