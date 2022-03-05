# -*- coding: utf-8 -*-

import json
import logging

from et_stopwatch import Stopwatch
from flask import Flask, request, Response
from func_timeout import func_timeout
from waitress import serve

import pychanlun.stock_service as stock_service
from pychanlun.chanlun_service import get_data_v2
from pychanlun.monitor.BusinessService import businessService
from gevent.pywsgi import WSGIServer
from pychanlun.util.encoder import MyJsonEncoder

app = Flask(__name__)


@app.route('/api/stock_data')
def stock_data():
    period = request.args.get("period")
    symbol = request.args.get("symbol")
    end_date = request.args.get("endDate")
    stopwatch = Stopwatch('/api/stock_data {} {}'.format(symbol, period, end_date))
    # result = get_data(symbol, period, end_date)
    result = get_data_v2(symbol, period, end_date, 0)
    stopwatch.stop()
    logging.info(stopwatch)
    return Response(json.dumps(result, cls=MyJsonEncoder), mimetype='application/json')


@app.route('/api/stock_data_v2')
def stock_data_v2():
    period = request.args.get("period")
    symbol = request.args.get("symbol")
    end_date = request.args.get("endDate")
    stopwatch = Stopwatch('/api/stock_data_v2 {} {}'.format(symbol, period, end_date))
    result = get_data_v2(symbol, period, end_date)
    stopwatch.stop()
    logging.info(stopwatch)
    return Response(json.dumps(result), mimetype='application/json')\

@app.route('/api/get_account_info')
def get_account_info():
    account_info = func_timeout(30, businessService.get_account_info)
    return Response(json.dumps(account_info), mimetype='application/json')\


@app.route('/api/get_global_future_symbol')
def get_global_future_symbol():
    global_future_symbol = func_timeout(30, businessService.get_global_future_symbol)
    return Response(json.dumps(global_future_symbol), mimetype='application/json')
# --------------------------------数字货币部分------------------------------------


@app.route('/api/get_btc_ticker')
def get_btc_ticker():
    btcTicker = businessService.getBTCTicker()
    return Response(json.dumps(btcTicker), mimetype='application/json')


# --------------------------------期货部分------------------------------------

# 获取当前价格在MA20上还是下
@app.route('/api/get_day_ma_up_down_list')
def get_day_ma_up_down_list():
    day_ma_up_down_list = func_timeout(30, businessService.get_day_ma_up_down_list)
    return Response(json.dumps(day_ma_up_down_list), mimetype='application/json')

# 获取当前品种3条均线
@app.route('/api/get_day_ma_list')
def get_day_ma_list():
    symbol = request.args.get("symbol")
    day_ma_list = func_timeout(30, businessService.get_day_ma_list,args=(symbol,))
    return Response(json.dumps(day_ma_list), mimetype='application/json')

# 获取期货统计信息
@app.route('/api/get_statistic_list')
def get_statistic_list():
    date_range = request.args.get("dateRange")
    statistic_list = func_timeout(30, businessService.getStatisticList, args=(date_range,))
    return Response(json.dumps(statistic_list), mimetype='application/json')


# 获取外盘涨跌幅列表
@app.route('/api/get_global_future_change_list')
def get_global_future_change_list():
    globalFutureChangeList = func_timeout(30, businessService.getGlobalFutureChangeList)
    return Response(json.dumps(globalFutureChangeList), mimetype='application/json')


# 获取保证金率
@app.route('/api/get_future_config')
def get_future_margin_rate():
    futureConfig = func_timeout(30, businessService.getFutureConfig)
    return Response(json.dumps(futureConfig), mimetype='application/json')


# 获取主力合约
# curl -X GET http://127.0.0.1:5000/api/dominant
@app.route('/api/dominant')
def dominant():
    dominant_symbol_info_list = func_timeout(30, businessService.get_dominant_symbol_list)
    return Response(json.dumps(dominant_symbol_info_list), mimetype='application/json')


# 获取所有背驰列表
@app.route('/api/get_future_signal_list')
def get_future_signal_list():
    futureSignalList = func_timeout(30, businessService.getFutureSignalList)
    return Response(json.dumps(futureSignalList), mimetype='application/json')


# 获取涨跌幅信息
@app.route('/api/get_change_list')
def get_change_list():
    changeListResult = func_timeout(30, businessService.get_future_change_list)
    return Response(json.dumps(changeListResult), mimetype='application/json')


# 新增持仓信息
@app.route('/api/create_position', methods=["POST"])
def create_position():
    position = request.get_json()
    inserted_id = func_timeout(30, businessService.createPosition, args=(position,))
    res = {
        "id": str(inserted_id)
    }
    return Response(json.dumps(res), mimetype='application/json')


# 更新持仓信息
@app.route('/api/update_position', methods=["POST"])
def update_position():
    position = request.get_json()
    func_timeout(30, businessService.updatePosition, args=(position,))
    res = {
        "code": "ok"
    }
    return Response(json.dumps(res), mimetype='application/json')


# 更新持仓状态
@app.route('/api/update_position_status')
def update_position_status():
    id = request.args.get("id")
    status = request.args.get("status")
    close_price = request.args.get("close_price")
    func_timeout(30, businessService.updatePositionStatus, args=(id, status, close_price))
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
    endDate = request.args.get("endDate")
    positionList = func_timeout(30, businessService.getPositionList, args=(status, page,size, endDate))
    return Response(json.dumps(positionList), mimetype='application/json')


# 跟据单个持仓
@app.route('/api/get_position')
def get_position():
    symbol = request.args.get("symbol")
    period = request.args.get("period") or "all"
    status = request.args.get("status")
    direction = request.args.get("direction")
    singlePosition = func_timeout(30, businessService.getPosition, args=(symbol, period, status, direction))
    return Response(json.dumps(singlePosition), mimetype='application/json')


# 查询期货级别多空方向列表
@app.route('/api/get_future_level_direction_list')
def get_future_level_direction():
    levelDirectionList = func_timeout(30, businessService.getLevelDirectionList)
    return Response(json.dumps(levelDirectionList), mimetype='application/json')


# 新增预判信息
@app.route('/api/create_future_prejudge_list', methods=["POST"])
def create_prejudge_list():
    futurePrejudgeData = request.get_json()
    inserted_id = func_timeout(30, businessService.createFuturePrejudgeList,
                               args=(futurePrejudgeData['endDate'], futurePrejudgeData['prejudgeList']))
    res = {
        "id": str(inserted_id)
    }
    return Response(json.dumps(res), mimetype='application/json')


# 获取预判信息列表
@app.route('/api/get_future_prejudge_list')
def get_future_prejudge_list():
    endDate = request.args.get("endDate")
    futurePrejudgeList = func_timeout(30, businessService.getFuturePrejudgeList, args=(endDate,))
    return Response(json.dumps(futurePrejudgeList), mimetype='application/json')


# 更新预判信息列表
@app.route('/api/update_future_prejudge_list', methods=["POST"])
def update_future_prejudge_list():
    futurePrejudgeData = request.get_json()
    func_timeout(30, businessService.updateFuturePrejudgeList,
                 args=(futurePrejudgeData['id'], futurePrejudgeData['prejudgeList']))
    res = {
        "code": "ok"
    }
    return Response(json.dumps(res), mimetype='application/json')


# --------------------股票部分----------------------------------------------

# 获取股票信号列表
@app.route('/api/get_stock_signal_list')
def get_stock_signal_list():
    page = int(request.args.get("page", "1"))
    if page <= 0:
        page = 1
    signal_list = stock_service.get_stock_signal_list(page)
    return Response(json.dumps(signal_list), mimetype='application/json')


# 查询股票持仓列表
@app.route('/api/get_stock_position_list')
def get_stock_position_list():
    status = request.args.get("status")
    page = int(request.args.get("page") or "1")
    # 每页显示的条目
    size = int(request.args.get("size") or "10")
    # print("status--->", status, page, size)
    stockPositionList = func_timeout(30, businessService.getStockPositionList, args=(status, page, size))
    return Response(json.dumps(stockPositionList), mimetype='application/json')


# 查询单个股票持仓
@app.route('/api/get_stock_position')
def get_stock_position():
    symbol = request.args.get("symbol")
    period = request.args.get("period") or "all"
    status = request.args.get("status")
    singlePosition = func_timeout(30, businessService.getStockPosition, args=(symbol, period, status))
    return Response(json.dumps(singlePosition), mimetype='application/json')


# 新增股票持仓信息
@app.route('/api/create_stock_position', methods=["POST"])
def create_stock_position():
    position = request.get_json()
    inserted_id = func_timeout(30, businessService.createStockPosition, args=(position,))
    res = {
        "id": str(inserted_id)
    }
    return Response(json.dumps(res), mimetype='application/json')


# 更新股票持仓信息
@app.route('/api/update_stock_position', methods=["POST"])
def update_stock_position():
    position = request.get_json()
    func_timeout(30, businessService.updateStockPosition, args=(position,))
    res = {
        "code": "ok"
    }
    return Response(json.dumps(res), mimetype='application/json')


# 更新股票持仓状态
@app.route('/api/update_stock_position_status')
def update_stock_position_status():
    id = request.args.get("id")
    status = request.args.get("status")
    func_timeout(30, businessService.updateStockPositionStatus, args=(id, status))
    res = {
        "code": "ok"
    }
    return Response(json.dumps(res), mimetype='application/json')


def run(**kwargs):
    port = kwargs.get("port", 5000)
    http_serv = WSGIServer(("0.0.0.0", port), app)
    http_serv.serve_forever()


if __name__ == '__main__':
    # 开发模式运行，用内置服务器
    run()
