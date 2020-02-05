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
    symbolList = config['symbolList']
    dominantSymbolInfoList = []
    for i in range(len(symbolList)):
        df = rq.futures.get_dominant(symbolList[i], start_date=None, end_date=None, rule=0)
        dominantSymbol = df[-1]
        dominantSymbolInfo = rq.instruments(dominantSymbol)
        dominantSymbolInfoList.append(dominantSymbolInfo.__dict__)
    print("当前主力合约:",dominantSymbolInfoList)
    return Response(json.dumps(dominantSymbolInfoList), mimetype='application/json')

# 获取所有背驰列表
@app.route('/api/get_beichi_list')
def get_beichi_list():
    strategyType = request.args.get("strategyType") or "0"
    businessService = BusinessService()
    beichiListResult = businessService.getBeichiList(strategyType)
    return Response(json.dumps(beichiListResult), mimetype='application/json')

# 获取涨跌幅信息
@app.route('/api/get_change_list')
def get_change_list():
    businessService = BusinessService()
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
    businessService = BusinessService()
    stockSignalList = businessService.getStockSignalList(page)
    return Response(json.dumps(stockSignalList), mimetype='application/json')
# 新增持仓信息
@app.route('/api/create_position',methods = ["POST"])
def create_position():
    position = request.get_json()
    businessService = BusinessService()
    inserted_id = businessService.createPosition(position)
    res = {
        "id":str(inserted_id)
    }
    return Response(json.dumps(res), mimetype='application/json')

# 更新持仓信息
@app.route('/api/update_position',methods = ["POST"])
def update_position():
    position = request.get_json()
    businessService = BusinessService()
    businessService.updatePosition(position)
    res = {
        "code": "ok"
    }
    return Response(json.dumps(res), mimetype='application/json')

# 查询持仓列表
@app.route('/api/get_position')
def get_position():
    businessService = BusinessService()
    positionList = businessService.getPositionList()
    return Response(json.dumps(positionList), mimetype='application/json')

def run(**kwargs):
    port = kwargs.get("port", 5000)
    serve(app, host='0.0.0.0', port=port)


if __name__ == '__main__':
    print(sys.path)
    app.run()
