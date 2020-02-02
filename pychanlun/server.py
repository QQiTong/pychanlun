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
    period = request.args.get("period") or "1min"
    symbol = request.args.get("symbol") or "BTC_CQ"
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
    businessService = BusinessService()
    stockSignalList = businessService.getStockSignalList()
    return Response(json.dumps(stockSignalList), mimetype='application/json')

def run(**kwargs):
    serve(app, host='0.0.0.0', port=5000)
