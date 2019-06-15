from flask import Flask, request, Response
import json

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

    result = calc.calcData(kxType)

    return Response(json.dumps(result), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
