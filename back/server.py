from flask import Flask, request, Response
import json
from jqdatasdk import *
# import rqdatac as rq
# from rqdatac import *
from back.Calc import Calc
from apscheduler.schedulers.background import BackgroundScheduler
from back.monitor import strategy3

app = Flask(__name__)


@app.route('/')
def hello():
    result = {'sum': 1, 'heh': 2}
    return Response(json.dumps(result), mimetype='application/json')


@app.route('/api/stock_data')
def data():
    calc = Calc()
    period = request.args.get("period") or "1min"
    symbol = request.args.get("symbol") or "XBTUSD"
    result = calc.calcData(period, symbol)
    return Response(json.dumps(result), mimetype='application/json')

@app.route('/api/save_stock_data')
def save_stock_date():
    calc = Calc()
    period = request.args.get("period") or "1min"
    symbol = request.args.get("symbol") or "XBTUSD"
    result = calc.calcData(period, symbol, True)
    return Response(json.dumps(result), mimetype='application/json')

if __name__ == '__main__':
    print("启动服务------------------")
    auth('13088887055', 'chanlun123456')
    # 聚宽数据源 到期 改成米筐
    # init('license',
    #      'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
    #      ('rqdatad-pro.ricequant.com', 16011))

    # 启动监控任务
    scheduler = BackgroundScheduler({
        'apscheduler.timezone': 'Asia/shanghai'
    })
    scheduler.add_job(strategy3.doMonitor1, 'cron', minute='*/3', hour="*")
    scheduler.add_job(strategy3.doMonitor2, 'cron', minute='*/15', hour="*")
    scheduler.start()

    app.run()
    # 服务启动的时候 登录聚宽

