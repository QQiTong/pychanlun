from flask import Flask, request, Response
import json
from jqdatasdk import *

from back.Calc import Calc

app = Flask(__name__)


@app.route('/')
def hello():
    result = {'sum': 1, 'heh': 2}
    return Response(json.dumps(result), mimetype='application/json')


@app.route('/api/stock_data')
def data():
    calc = Calc()
    kxType = request.args.get("kxType") or "1min"
    symbol = request.args.get("symbol") or "btc"
    result = calc.calcData(kxType, symbol)

    return Response(json.dumps(result), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
    # 服务启动的时候 登录聚宽
    auth('13088887055', '887055')
