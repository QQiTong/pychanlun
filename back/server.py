from flask import Flask, request, Response
import json
import os
from jqdatasdk import *
from rqdatac import *
from back.Calc import Calc
from back.monitor.BusinessService import BusinessService
import numpy as np
from back.config import config

import rqdatac as rq

app = Flask(__name__)

@app.route('/')
def hello():
    result = {'sum': 1, 'heh': 2}
    return Response(json.dumps(result), mimetype='application/json')


@app.route('/api/stock_data')
def data():
    calc = Calc()
    period = request.args.get("period") or "1min"
    symbol = request.args.get("symbol") or "BTC_CQ"
    result = calc.calcData(period, symbol)
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
    strategyType = request.args.get("strategyType") or "4"
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

if __name__ == '__main__':
    print("启动服务------------------")

    # auth('13088887055', 'chanlun123456')
    # 聚宽数据源 到期 改成米筐
    init('license',
         'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
         ('rqdatad-pro.ricequant.com', 16011))
    # app.debug = True
    app.run(host = '0.0.0.0')
    # 服务启动的时候 登录聚宽
