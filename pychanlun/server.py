# -*- coding: utf-8 -*-

import os, sys

from flask import Flask, request, Response
from waitress import serve
import json
import numpy as np
from rqdatac import *
from pychanlun.Calc import Calc
from pychanlun.monitor.BusinessService import BusinessService
from pychanlun.config import config
import rqdatac as rq

app = Flask(__name__)
businessService = BusinessService()


@app.route('/api/stock_data')
def data():
    calc = Calc()
    period = request.args.get("period")
    symbol = request.args.get("symbol")
    endDate = request.args.get("endDate")
    result = calc.calcData(period, symbol, False, endDate)
    return Response(json.dumps(result), mimetype='application/json')


# 获取主力合约
@app.route('/api/dominant')
def dominant():
    dominantSymbolInfoList = businessService.getDoinantSynmbol()
    # print("当前主力合约:",dominantSymbolInfoList)
    return Response(json.dumps(dominantSymbolInfoList), mimetype='application/json')


# 获取所有背驰列表
@app.route('/api/get_beichi_list')
def get_beichi_list():
    strategyType = request.args.get("strategyType") or "0"
    beichiListResult = businessService.getBeichiList(strategyType)
    return Response(json.dumps(beichiListResult), mimetype='application/json')


# 获取涨跌幅信息
@app.route('/api/get_change_list')
def get_change_list():
    changeListResult = businessService.getChangeList()
    return Response(json.dumps(changeListResult), mimetype='application/json')


@app.route('/api/save_stock_data')
def save_stock_date():
    calc = Calc()
    period = request.args.get("period") or "1min"
    symbol = request.args.get("symbol") or "BTC_CQ"
    result = calc.calcData(period, symbol, True)
    return Response(json.dumps(result), mimetype='application/json')


# 获取股票信号列表
@app.route('/api/get_stock_signal_list')
def get_stock_signal_list():
    page = int(request.args.get("page") or "1")
    stockSignalList = businessService.getStockSignalList(page)
    return Response(json.dumps(stockSignalList), mimetype='application/json')


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


# 查询持仓列表
@app.route('/api/get_position_list')
def get_position_list():
    status = request.args.get("status")
    page = int(request.args.get("page") or "1")
    # 每页显示的条目
    size = int(request.args.get("size") or "2")
    print("status--->", status, page,size)
    positionList = businessService.getPositionList(status, page,size)
    return Response(json.dumps(positionList), mimetype='application/json')

# 跟据单个持仓
@app.route('/api/get_position')
def get_position():
    symbol = request.args.get("symbol")
    period = request.args.get("period") or "all"
    status = request.args.get("status")
    singlePosition = businessService.getPosition(symbol, period,status)
    return Response(json.dumps(singlePosition), mimetype='application/json')

def run(**kwargs):
    port = kwargs.get("port", 5000)
    # 程序启动初始化主力合约信息,不需要每次都请求
    businessService.initDoinantSynmbol()
    serve(app, host='0.0.0.0', port=port)


if __name__ == '__main__':
    print(sys.path)
    app.run()
