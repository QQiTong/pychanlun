# -*- coding: utf-8 -*-
import logging
import traceback
from pychanlun.Calc import Calc
from pychanlun.KlineDataTool import KlineDataTool
import rqdatac as rq
from datetime import datetime, timedelta
from rqdatac import *
import time
import threading
from pychanlun.Mail import Mail
import json
from pychanlun.db import DBPyChanlun
from pychanlun.config import config
from pychanlun.monitor.BusinessService import businessService
import pytz
import requests

tz = pytz.timezone('Asia/Shanghai')
'''
综合监控
'''
klineDataTool = KlineDataTool()
# 米筐数据 主力连续合约RB88 这个会比实时数据少一天
symbolListDigitCoin = ['BTC'
                       # 'ETH_CQ', 'BCH_CQ', 'LTC_CQ', 'BSV_CQ'
                       ]
globalFutureSymbol = config['globalFutureSymbol']
# 内盘期货
periodList1 = ['3m', '5m', '15m', '30m', '60m']
# 数字货币
periodList2 = ['1m', '3m', '5m', '15m', '30m', '60m']
# 外盘期货
periodList3 = ['5m', '15m', '30m', '60m']
# 高级别 高高级别映射
# 暂时用3d 3d
futureLevelMap = {
    '3m': ['15m', '60m'],
    '5m': ['30m', '240m'],
    '15m': ['60m', '1d'],
    '30m': ['240m', '3d'],
    '60m': ['1d', '3d'],
    '240m': ['3d', '3d'],
}
dominantSymbolInfoList = {}

# 期货公司在原有保证金基础上1%
marginLevelCompany = 0.01
# 期货账户
futuresAccount = 50
# 数字货币手续费0.05% 开平仓0.1%
digitCoinFee = 0.001
# 数字货币账户
digitCoinAccount = 60.80 / 10000
maxAccountUseRate = 0.1
stopRate = 0.01
mail = Mail()


# 初始化业务对象
# businessService = BusinessService()

# 改成钉钉发送
def sendEmail(msg, symbol, period, signal, direction, amount, stop_lose_price, fire_time_str, price, date_created_str,
              close_price, remark):
    print(msg)
    # mailResult = mail.send(json.dumps(msg, ensure_ascii=False, indent=4))

    # url = "http://www.yutiansut.com/signal?user_id=oL-C4w2KYo5DB486YBwAK2M69uo4&template=xiadan_report&strategy_id=%s" \
    #       "&realaccount=%s&code=%s&order_direction=%s&order_offset=%s&price=%s&volume=%s&order_time=%s" \
    #       % (signal, remark, symbol + '_' + period, signal, direction,
    #          '开:' + str(close_price) + ' 止:' + str(stop_lose_price) + ' 触:' + str(price), amount,
    #          '开:' + fire_time_str + ' 触:' + date_created_str)
    # requests.post(url)

    url = 'https://oapi.dingtalk.com/robot/send?access_token=39474549996bad7e584523a02236d69b68be8963e2937274e4e0c57fbb629477'
    program = {
        "msgtype": "text",
        "text": {"content": json.dumps(msg, ensure_ascii=False, indent=4)},
    }
    headers = {'Content-Type': 'application/json'}
    f = requests.post(url, data=json.dumps(program), headers=headers)
    # if not mailResult:
    #     print("发送失败")
    # else:
    #     print("发送成功")


# price 信号触发的价格， close_price 提醒时的收盘价 direction 多B 空S amount 开仓数量
def saveFutureSignal(symbol, period, fire_time_str, direction, signal, remark, price, close_price,
                     stop_lose_price, futureCalcObj):
    # 更新,实时更新持仓品种的价格
    saveFutureAutoPosition(symbol, period, fire_time_str, direction, signal, remark, price, close_price,
                           stop_lose_price, futureCalcObj, False)
    amount = futureCalcObj['maxOrderCount']
    temp_fire_time = datetime.strptime(fire_time_str, "%Y-%m-%d %H:%M")
    # 触发时间转换成UTC时间
    fire_time = temp_fire_time - timedelta(hours=8)
    last_fire = DBPyChanlun['future_signal'].find_one({
        'symbol': symbol,
        'period': period,
        'fire_time': fire_time,
        'direction': direction,
        'signal': signal,
    })
    date_created = datetime.utcnow()
    if last_fire is not None:
        DBPyChanlun['future_signal'].find_one_and_update({
            'symbol': symbol, 'period': period, 'fire_time': fire_time, 'direction': direction, 'signal': signal
        }, {
            '$set': {
                'signal': signal,
                'remark': remark,
                'price': price,
                'close_price': close_price,
                'amount': amount,
                'date_created': datetime.utcnow(),
                'stop_lose_price': stop_lose_price
            },
            '$inc': {
                'update_count': 1
            }
        }, upsert=True)
    else:
        DBPyChanlun['future_signal'].insert_one({
            'symbol': symbol,
            'period': period,
            'signal': signal,
            'amount': amount,
            'remark': remark,
            'fire_time': fire_time,  # 信号发生的时间
            'price': price,
            'date_created': date_created,  # 记录插入的时间
            'close_price': close_price,  # 提醒时最新价格
            'direction': direction,
            'stop_lose_price': stop_lose_price,  # 当前信号的止损价
            'update_count': 1,  # 这条背驰记录的更新次数
        })
        if (date_created - fire_time).total_seconds() < 60 * 4:
            # 新增
            saveFutureAutoPosition(symbol, period, fire_time_str, direction, signal, remark, price, close_price,
                                   stop_lose_price, futureCalcObj, True)

            # 在3分钟内的触发邮件通知  3分钟就能扫内盘+外盘
            # 把数据库的utc时间 转成本地时间
            fire_time_str = (fire_time + timedelta(hours=8)).strftime('%m-%d %H:%M:%S')
            date_created_str = (date_created + timedelta(hours=8)).strftime('%m-%d %H:%M:%S')
            msg = {
                "symbol": symbol,
                "period": period,
                "signal": signal,
                "direction": direction,
                "amount": amount,
                "stop":stop_lose_price,
                "fire_time": fire_time_str,
                "price": price,
                "date_created": date_created_str,
                "close_price": close_price,
                "remark": remark,
                "remind": 'Ding'
            }
            # 简洁版
            # msg = "%s %s %s %s %s %s %s %s %s %s %s" % (
            #     symbol, period, signal, direction + ' ', " [amount]: " + str(amount),
            #     " [stop]: " + str(stop_lose_price), " [fire]: " + fire_time_str, " [price]: " + str(price),
            #     " [create]: " + date_created_str,
            #     str(close_price), remark)
            sendEmail(msg, symbol, period, signal, direction, amount, stop_lose_price, fire_time_str, price,
                      date_created_str,
                      close_price, remark)


# 自动录入持仓列表  新增 status(holding,winEnd,loseEnd 状态) profit(盈利) profit_rate(盈利率)
def saveFutureAutoPosition(symbol, period, fire_time_str, direction, signal, remark, price, close_price,
                           stop_lose_price, futureCalcObj, insert):
    # 外盘不录入持仓列表
    if symbol in globalFutureSymbol:
        return
    temp_fire_time = datetime.strptime(fire_time_str, "%Y-%m-%d %H:%M")
    # 触发时间转换成UTC时间
    fire_time = temp_fire_time - timedelta(hours=8)
    # 查找自动持仓表中状态为holding的， 因为 止盈结束和止损结束的单子 还是有可能继续开仓的
    status = 'holding'
    date_created = datetime.utcnow()
    # 如果持仓表中这条记录 那么更新最新价格，如果没有新增
    if direction == 'S' or direction == 'HS':
        direction = 'short'
    else:
        direction = 'long'
    if insert is True:
        last_fire = DBPyChanlun['future_auto_position'].find_one({
            'symbol': symbol,
            'direction': direction,
            'status': status
        })
        if last_fire is not None:
            DBPyChanlun['future_auto_position'].find_one_and_update({
                'symbol': symbol, 'direction': direction, 'status': status
            }, {
                '$set': {
                    'close_price': close_price,  # 只需要更新最新价格，用于判断是否止损
                    'last_update_time': date_created,  # 最后更新时间
                    'last_update_signal': signal,  # 最后更新的信号
                    'last_update_period': period  # 最后更新的周期
                },
                '$inc': {
                    'update_count': 1
                }
            }, upsert=True)
        else:
            DBPyChanlun['future_auto_position'].insert_one({
                'symbol': symbol,
                'period': period,
                'signal': signal,
                'amount': futureCalcObj['maxOrderCount'],
                'remark': remark,
                'fire_time': fire_time,  # 信号发生的时间
                'price': price,
                'date_created': date_created,  # 记录插入的时间
                'close_price': close_price,  # 提醒时最新价格
                'direction': direction,
                'stop_lose_price': stop_lose_price,  # 当前信号的止损价
                'update_count': 1,  # 这条背驰记录的更新次数
                'profit': 0,  # 盈利
                'profit_rate': 0,  # 盈利率
                'status': status,
                'per_order_stop_money': futureCalcObj['perOrderStopMoney'],
                'per_order_stop_rate': round(futureCalcObj['perOrderStopRate'], 2),
                'per_order_margin': round(futureCalcObj['perOrderMargin'], 2),
                'predict_stop_money': -round(futureCalcObj['perOrderStopMoney'] * futureCalcObj['maxOrderCount'], 2),
                'margin_rate': futureCalcObj['marginRate'],
                'last_update_time': '',
                'last_update_signal': '',
                'last_update_period': '',

            })
    else:
        last_fire = DBPyChanlun['future_auto_position'].find_one({
            'symbol': symbol,
            'direction': direction,
            'status': status
        })
        #  如果当前价格已经触及到止损价，那么就讲状态设置为loseEnd
        # print("最后一个",last_fire)
        if last_fire is not None:
            # 之后价格再涨上来，status又会变成holding ,因此已经被止损的持仓不要再更新状态了
            if last_fire['status'] == 'holding':
                if (direction == 'long' and close_price <= last_fire['stop_lose_price']) or (direction == 'short' and close_price >= last_fire['stop_lose_price']):
                    # print("止损了",direction,close_price,last_fire['stop_lose_price'])
                    DBPyChanlun['future_auto_position'].find_one_and_update({
                        '_id':last_fire['_id'],'symbol': symbol, 'direction': direction, 'status': 'holding'
                    }, {
                        '$set': {
                            'close_price': close_price,  # 只需要更新最新价格，用于判断是否止损
                            'status': 'loseEnd',
                            'lose_end_price':close_price  # 止损了需要将止损结束的价格插入到数据库中
                        },
                        '$inc': {
                            'update_count': 1
                        }
                    }, upsert=True)
                else:
                    # print("持有中", direction, close_price, last_fire['stop_lose_price'])
                    status = 'holding'
                    DBPyChanlun['future_auto_position'].find_one_and_update({
                        'symbol': symbol, 'direction': direction, 'status': status
                    }, {
                        '$set': {
                            'close_price': close_price,  # 只需要更新最新价格，用于判断是否止损
                            'status': status
                        },
                        '$inc': {
                            'update_count': 1
                        }
                    }, upsert=True)


# 记录品种当前级别的方向
def saveFutureDirection(symbol, period, direction):
    last_fire = DBPyChanlun['future_direction'].find_one({
        'symbol': symbol,
        'period': period,
    })
    if last_fire is not None:
        DBPyChanlun['future_direction'].find_one_and_update({
            'symbol': symbol, 'period': period
        }, {
            '$set': {
                'date_created': datetime.utcnow(),
                'direction': direction
            },
            '$inc': {
                'update_count': 1
            }
        }, upsert=True)
    else:
        date_created = datetime.utcnow()
        DBPyChanlun['future_direction'].insert_one({
            'symbol': symbol,
            'period': period,
            'date_created': date_created,  # 记录插入的时间
            'direction': direction,
            'update_count': 1,
        })


def getDominantSymbol():
    symbolList = config['symbolList']
    # 主力合约列表
    dominantSymbolList = []
    for i in range(len(symbolList)):
        df = rq.futures.get_dominant(
            symbolList[i], start_date=None, end_date=None, rule=0)
        dominantSymbol = df[-1]
        dominantSymbolList.append(dominantSymbol)
        dominantSymbolInfo = rq.instruments(dominantSymbol)
        dominantSymbolInfoList[dominantSymbol] = dominantSymbolInfo.__dict__
    return dominantSymbolList, dominantSymbolInfoList


# 监控期货
# timeScope 监控距离现在多少分钟的
def monitorFuturesAndDigitCoin(type, symbolList):
    logger = logging.getLogger()
    if type == "1":
        # auth('13088887055', 'chanlun123456')
        # count = get_query_count()
        # print(count)
        # print("主力合约信息：", dominantSymbolInfoList)
        periodList = periodList1

    elif type == "2":
        symbolList = symbolListDigitCoin
        periodList = periodList1

    else:
        symbolList = globalFutureSymbol
        periodList = periodList3

    try:
        while True:
            for i in range(len(symbolList)):
                for j in range(len(periodList)):
                    symbol = symbolList[i]
                    period = periodList[j]
                    calc = Calc()
                    print("current:", symbol, period, datetime.now())
                    result = calc.calcData(period, symbol)
                    close_price = result['close'][-1]
                    monitorBeichi(result, symbol, period, close_price)
                    monitorHuila(result, symbol, period, close_price)
                    monitorTupo(result, symbol, period, close_price)
                    monitorVfan(result, symbol, period, close_price)
                    monitorDuanBreak(result, symbol, period, close_price)
                    monitorFractal(result, symbol, period, close_price)
            if type == "1" or type == "3":
                time.sleep(0)
            else:
                time.sleep(5)
    except Exception:
        logger.info("Error Occurred: {0}".format(traceback.format_exc()))
        print("Error Occurred: {0}".format(traceback.format_exc()))
        if type == "1":
            print("期货出异常了", Exception)
            threading.Thread(target=monitorFuturesAndDigitCoin, args=['1', symbolList]).start()
        elif type == "3":
            print("外盘期货出异常了", Exception)
            threading.Thread(target=monitorFuturesAndDigitCoin, args=['3', globalFutureSymbol]).start()
        else:
            print("OKEX出异常了", Exception)
            time.sleep(10)
            threading.Thread(target=monitorFuturesAndDigitCoin, args=["2", symbolListDigitCoin]).start()


'''
监控背驰
'''


def monitorBeichi(result, symbol, period, closePrice):
    signal = 'beichi'
    notLower = result['notLower']
    notHigher = result['notHigher']
    # 监控背驰
    if len(result['buyMACDBCData']['date']) > 0:
        if not notLower:
           return
        fire_time = result['buyMACDBCData']['date'][-1]
        price = result['buyMACDBCData']['data'][-1]
        # remark = result['buyMACDBCData']['tag'][-1]
        remark = ""
        stop_lose_price = result['buyMACDBCData']['stop_lose_price'][-1]
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        direction = 'B'
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)
    if len(result['sellMACDBCData']['date']) > 0:
        if not notHigher:
           return
        fire_time = result['sellMACDBCData']['date'][-1]
        price = result['sellMACDBCData']['data'][-1]
        # remark = result['sellMACDBCData']['tag'][-1]
        remark = ""
        stop_lose_price = result['sellMACDBCData']['stop_lose_price'][-1]
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        direction = 'S'
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)
    # 监控高级别背驰
    # if len(result['buy_zs_huila_higher']['date']) > 0:
    #     fire_time = result['buy_zs_huila_higher']['date'][-1]
    #     price = result['buy_zs_huila_higher']['data'][-1]
    #     remark = result['buy_zs_huila_higher']['tag'][-1]
    #     stop_lose_price = result['buy_zs_huila_higher']['stop_lose_price'][-1]
    #     direction = 'HB'
    #     maxOrderCount,perOrderStopMoney,perOrderStopRate = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
    #     saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,
    #                      stop_lose_price)
    # if len(result['sell_zs_huila_higher']['date']) > 0:
    #     fire_time = result['sell_zs_huila_higher']['date'][-1]
    #     price = result['sell_zs_huila_higher']['data'][-1]
    #     remark = result['sell_zs_huila_higher']['tag'][-1]
    #     stop_lose_price = result['sell_zs_huila_higher']['stop_lose_price'][-1]
    #     direction = 'HS'
    #     maxOrderCount,perOrderStopMoney,perOrderStopRate = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
    #     saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,
    #                      stop_lose_price)


'''
监控回拉
'''


def monitorHuila(result, symbol, period, closePrice):
    signal = 'huila'
    # 监控回拉
    if len(result['buy_zs_huila']['date']) > 0:
        fire_time = result['buy_zs_huila']['date'][-1]
        price = result['buy_zs_huila']['data'][-1]
        remark = result['buy_zs_huila']['tag'][-1]
        stop_lose_price = result['buy_zs_huila']['stop_lose_price'][-1]
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        direction = 'B'
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)
    if len(result['sell_zs_huila']['date']) > 0:
        fire_time = result['sell_zs_huila']['date'][-1]
        price = result['sell_zs_huila']['data'][-1]
        remark = result['sell_zs_huila']['tag'][-1]
        stop_lose_price = result['sell_zs_huila']['stop_lose_price'][-1]
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        direction = 'S'
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)
    # 监控高级别回拉
    if len(result['buy_zs_huila_higher']['date']) > 0:
        fire_time = result['buy_zs_huila_higher']['date'][-1]
        price = result['buy_zs_huila_higher']['data'][-1]
        remark = result['buy_zs_huila_higher']['tag'][-1]
        stop_lose_price = result['buy_zs_huila_higher']['stop_lose_price'][-1]
        direction = 'HB'
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)
    if len(result['sell_zs_huila_higher']['date']) > 0:
        fire_time = result['sell_zs_huila_higher']['date'][-1]
        price = result['sell_zs_huila_higher']['data'][-1]
        remark = result['sell_zs_huila_higher']['tag'][-1]
        stop_lose_price = result['sell_zs_huila_higher']['stop_lose_price'][-1]
        direction = 'HS'
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)


'''
监控突破
'''


def monitorTupo(result, symbol, period, closePrice):
    signal = 'tupo'
    # 监控突破
    if len(result['buy_zs_tupo']['date']) > 0:
        fire_time = result['buy_zs_tupo']['date'][-1]
        price = result['buy_zs_tupo']['data'][-1]
        stop_lose_price = result['buy_zs_tupo']['stop_lose_price'][-1]
        remark = ''
        direction = 'B'
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)
    if len(result['sell_zs_tupo']['date']) > 0:
        fire_time = result['sell_zs_tupo']['date'][-1]
        price = result['sell_zs_tupo']['data'][-1]
        stop_lose_price = result['sell_zs_tupo']['stop_lose_price'][-1]
        remark = ''
        direction = 'S'
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)
    # 监控高级别突破
    if len(result['buy_zs_tupo_higher']['date']) > 0:
        fire_time = result['buy_zs_tupo_higher']['date'][-1]
        price = result['buy_zs_tupo_higher']['data'][-1]
        stop_lose_price = result['buy_zs_tupo_higher']['stop_lose_price'][-1]
        remark = ''
        direction = 'HB'
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)
    if len(result['sell_zs_tupo_higher']['date']) > 0:
        fire_time = result['sell_zs_tupo_higher']['date'][-1]
        price = result['sell_zs_tupo_higher']['data'][-1]
        stop_lose_price = result['sell_zs_tupo_higher']['stop_lose_price'][-1]
        remark = ''
        direction = 'HS'
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)


'''
监控3买卖 V反
'''


def monitorVfan(result, symbol, period, closePrice):
    signal = 'vfan'
    # 监控V反
    if len(result['buy_v_reverse']['date']) > 0:
        fire_time = result['buy_v_reverse']['date'][-1]
        price = result['buy_v_reverse']['data'][-1]
        stop_lose_price = result['buy_v_reverse']['stop_lose_price'][-1]
        remark = ''
        direction = 'B'
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)
    if len(result['sell_v_reverse']['date']) > 0:
        fire_time = result['sell_v_reverse']['date'][-1]
        price = result['sell_v_reverse']['data'][-1]
        stop_lose_price = result['sell_v_reverse']['stop_lose_price'][-1]
        remark = ''
        direction = 'S'
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)
    # 监控高级别V反
    if len(result['buy_v_reverse_higher']['date']) > 0:
        fire_time = result['buy_v_reverse_higher']['date'][-1]
        price = result['buy_v_reverse_higher']['data'][-1]
        stop_lose_price = result['buy_v_reverse_higher']['stop_lose_price'][-1]
        remark = ''
        direction = 'HB'
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)

    if len(result['sell_v_reverse_higher']['date']) > 0:
        fire_time = result['sell_v_reverse_higher']['date'][-1]
        price = result['sell_v_reverse_higher']['data'][-1]
        stop_lose_price = result['sell_v_reverse_higher']['stop_lose_price'][-1]
        remark = ''
        direction = 'HS'
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)


'''
监控 线段破坏
'''


def monitorDuanBreak(result, symbol, period, closePrice):
    signal = 'break'
    # 监控线段破坏
    if len(result['buy_duan_break']['date']) > 0:
        fire_time = result['buy_duan_break']['date'][-1]
        price = result['buy_duan_break']['data'][-1]
        stop_lose_price = result['buy_duan_break']['stop_lose_price'][-1]
        remark = ''
        direction = 'B'
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)
    if len(result['sell_duan_break']['date']) > 0:
        fire_time = result['sell_duan_break']['date'][-1]
        price = result['sell_duan_break']['data'][-1]
        stop_lose_price = result['sell_duan_break']['stop_lose_price'][-1]
        remark = ''
        direction = 'S'
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)
    # 监控高级别线段破坏
    if len(result['buy_duan_break_higher']['date']) > 0:
        fire_time = result['buy_duan_break_higher']['date'][-1]
        price = result['buy_duan_break_higher']['data'][-1]
        stop_lose_price = result['buy_duan_break_higher']['stop_lose_price'][-1]
        remark = ''
        direction = 'HB'
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)

    if len(result['sell_duan_break_higher']['date']) > 0:
        fire_time = result['sell_duan_break_higher']['date'][-1]
        price = result['sell_duan_break_higher']['data'][-1]
        stop_lose_price = result['sell_duan_break_higher']['stop_lose_price'][-1]
        remark = ''
        direction = 'HS'
        futureCalcObj = calMaxOrderCount(symbol, closePrice, stop_lose_price, period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stop_lose_price, futureCalcObj)


'''
监控 持仓品种的向上两个级别的顶底分型
'''
temp = {
    "fractal": [{
        "direction": 1,
        "top_fractal": {
            "date": "2020-02-07 15:00",
            "top": 3340.0,
            "bottom": 3312.0
        },
        "bottom_fractal": {
            "date": "2020-02-04 09:15",
            "top": 3258.0,
            "bottom": 3207.0
        },
        "period": "15m"
    }, {
        "direction": 1,
        "top_fractal": {
            "date": "2020-02-07 15:00",
            "top": 3340.0,
            "bottom": 3306.0
        },
        "bottom_fractal": {
            "date": "2020-02-04 10:00",
            "top": 3500.0,
            "bottom": 3207.0
        },
        "period": "60m"
    }]
}


def monitorFractal(result, symbol, period, closePrice):
    # 将当前级别的的方向插入到数据库，用于前端展示当前级别的状态
    # 15m向上成笔，代表3F级别多， 15m向下成笔，代表3F级别空
    levelDirection = result['fractal'][0]['direction']
    if levelDirection == 1:
        saveFutureDirection(symbol, period, '多')
    else:
        saveFutureDirection(symbol, period, '空')
    signal = 'fractal'
    # 查询数据库该品种是否有持仓
    positionInfo = businessService.getPosition(symbol, period, 'holding')
    if positionInfo == -1:
        return
    # 持仓方向
    direction = positionInfo['direction']
    if direction == 'long':
        # 多单查找向上笔的顶分型
        # 高级别
        if result['fractal'][0]['direction'] == 1:
            fire_time = result['fractal'][0]['top_fractal']['date']
            price = result['fractal'][0]['top_fractal']['bottom']
            stop_lose_price = result['fractal'][0]['top_fractal']['top']
            remark = result['fractal'][0]['period']
            direction = 'S'
            # 当前价格低于顶分型的底
            if closePrice <= price:
                stopWinCount = calStopWinCount(symbol, period, positionInfo, closePrice)
                futureCalcObj = {
                    'maxOrderCount': stopWinCount,
                    # 'perOrderStopMoney': perOrderStopMoney,
                    # 'perOrderStopRate': perOrderStopRate,
                    # 'perOrderMargin': perOrderMargin,
                    # 'marginRate': margin_rate
                }
                saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice,
                                 stop_lose_price,futureCalcObj)
        # 高高级别
        if result['fractal'][1]['direction'] == 1:
            fire_time = result['fractal'][1]['top_fractal']['date']
            price = result['fractal'][1]['top_fractal']['bottom']
            stop_lose_price = result['fractal'][1]['top_fractal']['top']
            remark = result['fractal'][1]['period']
            direction = 'HS'
            # 当前价格低于顶分型的底
            if closePrice <= price:
                stopWinCount = calStopWinCount(symbol, period, positionInfo, closePrice)
                futureCalcObj = {
                    'maxOrderCount': stopWinCount,
                    # 'perOrderStopMoney': perOrderStopMoney,
                    # 'perOrderStopRate': perOrderStopRate,
                    # 'perOrderMargin': perOrderMargin,
                    # 'marginRate': margin_rate
                }
                saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice,
                                 stop_lose_price, futureCalcObj)
    else:
        # 空单查找向下笔的底分型
        # 高级别
        if result['fractal'][0]['direction'] == -1:
            fire_time = result['fractal'][0]['bottom_fractal']['date']
            price = result['fractal'][0]['bottom_fractal']['top']
            stop_lose_price = result['fractal'][0]['bottom_fractal']['bottom']
            remark = result['fractal'][0]['period']
            direction = 'B'
            # 当前价格高于底分型的顶
            if closePrice >= price:
                stopWinCount = calStopWinCount(symbol, period, positionInfo, closePrice)
                futureCalcObj = {
                    'maxOrderCount': stopWinCount,
                    # 'perOrderStopMoney': perOrderStopMoney,
                    # 'perOrderStopRate': perOrderStopRate,
                    # 'perOrderMargin': perOrderMargin,
                    # 'marginRate': margin_rate
                }
                saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice,
                                 stop_lose_price, futureCalcObj)
        # 高高级别
        if result['fractal'][1]['direction'] == -1:
            fire_time = result['fractal'][1]['bottom_fractal']['date']
            price = result['fractal'][1]['bottom_fractal']['top']
            stop_lose_price = result['fractal'][1]['bottom_fractal']['bottom']
            remark = result['fractal'][1]['period']
            direction = 'HB'
            # 当前价格高于底分型的顶
            if closePrice >= price:
                stopWinCount = calStopWinCount(symbol, period, positionInfo, closePrice)
                futureCalcObj = {
                    'maxOrderCount': stopWinCount,
                    # 'perOrderStopMoney': perOrderStopMoney,
                    # 'perOrderStopRate': perOrderStopRate,
                    # 'perOrderMargin': perOrderMargin,
                    # 'marginRate': margin_rate
                }
                saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice,
                                 stop_lose_price, futureCalcObj)


# 计算出开仓手数（止损系数，资金使用率双控）
# 返回最大开仓手数，1手止损的金额，1手止损的百分比
def calMaxOrderCount(dominantSymbol, openPrice, stopPrice, period):
    # openPrice stopPrice等于历史行情某个stopPrice 会导致除0异常
    if openPrice == stopPrice:
        return -1
    # 兼容数字货币
    if 'BTC' in dominantSymbol or dominantSymbol in config['globalFutureSymbol']:
        account = digitCoinAccount
        margin_rate = 0.05
        # 因为使用20倍杠杆所以 需要除以20
        perOrderMargin = 0.01 * openPrice * margin_rate
        # 1手止损的比率
        perOrderStopRate = (abs(openPrice - stopPrice) / openPrice + digitCoinFee) * 20
        # 1手止损的金额
        perOrderStopMoney = round((perOrderMargin * perOrderStopRate),4)
        maxAccountUse = account * 10000 * 0.4
        maxStopMoney = account * 10000 * 0.1
    # 期货
    else:
        account = futuresAccount
        margin_rate = dominantSymbolInfoList[dominantSymbol]['margin_rate']
        contract_multiplier = dominantSymbolInfoList[dominantSymbol]['contract_multiplier']
        # 计算1手需要的保证金
        perOrderMargin = int(openPrice * contract_multiplier * (margin_rate + marginLevelCompany))
        # 1手止损的金额
        perOrderStopMoney = abs(openPrice - stopPrice) * contract_multiplier
        # 1手止损的百分比
        perOrderStopRate = round((perOrderStopMoney / perOrderMargin), 2)
        # 计算最大能使用的资金
        maxAccountUse = account * 10000 * maxAccountUseRate
        # 计算最大止损金额
        maxStopMoney = account * 10000 * stopRate
    # 根据止损算出的开仓手数(四舍五入)
    # print("debug ",dominantSymbol,maxStopMoney,perOrderStopMoney,openPrice, stopPrice,period,contract_multiplier)
    maxOrderCount1 = round(maxStopMoney / perOrderStopMoney)
    # 根据最大资金使用率算出的开仓手数(四舍五入)
    maxOrderCount2 = round(maxAccountUse / perOrderMargin)
    maxOrderCount = maxOrderCount2 if maxOrderCount1 > maxOrderCount2 else maxOrderCount1
    # print("-->",maxStopMoney,"-->",maxStopMoney / perOrderStopMoney,"-->",maxAccountUse,"-->",maxAccountUse / perOrderMargin ,"->",perOrderMargin)
    # 返回最大开仓手数，1手止损的金额，1手止损的百分比,1手保证金,保证金率
    futureCalcObj = {
        'maxOrderCount': maxOrderCount,
        'perOrderStopMoney': perOrderStopMoney,
        'perOrderStopRate': perOrderStopRate,
        'perOrderMargin': perOrderMargin,
        'marginRate': margin_rate
    }
    return futureCalcObj


# 计算动止手数（盈亏比大于2.3：1 动止30%才能保证不亏）
# 主力合约，开仓价格，开仓数量，止损价格，止盈价格    用最新价来算回更准确，因为触发价可能会有滑点
def calStopWinCount(symbol, period, positionInfo, closePrice):
    # 兼容数字货币和外盘期货
    if 'BTC' in symbol or symbol in config['globalFutureSymbol']:
        return 0
    # 动止公式:  (1 - stopWinPosRate) / stopWinPosRate = winLoseRate
    # stopWinPosRate: 动态止盈多少仓位
    # winLoseRate: 当前的盈亏比
    # 查库耗时 0.005s
    # 该品种有持仓
    open_pos_price = positionInfo['price']
    open_pos_amount = positionInfo['amount']
    stop_lose_price = positionInfo['stopLosePrice']
    stop_win_price = closePrice
    winLoseRate = round(abs(stop_win_price - open_pos_price) /
                        abs(open_pos_price - stop_lose_price), 2)
    # 标准动止 第1次 高级别 走30%  ， 第2次 高高级别再走30%  ，但如果当前盈亏比已经超过 2.3：1，那么第1次就不用动止30%，需要计算
    if winLoseRate > 2.3:
        stopWinPosRate = round(1 / (winLoseRate + 1), 2)
    else:
        stopWinPosRate = 0.3
    stopWinCount = round(stopWinPosRate * open_pos_amount)
    print("当前盈亏比", winLoseRate, "当前动止仓位百分比",
          stopWinPosRate, "动止手数", stopWinCount)
    return stopWinCount


def run(**kwargs):
    init('license',
         'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
         ('rqdatad-pro.ricequant.com', 16011))
    # 主力合约，主力合约详细信息
    symbolList, dominantSymbolInfoList = getDominantSymbol()
    # 24个品种 拆分成8份
    # symbolListSplit = [symbolList[i:i + 3] for i in range(0, len(symbolList), 3)]
    # threading.Thread(target=monitorFuturesAndDigitCoin, args=['1', symbolListSplit[0]]).start()
    # threading.Thread(target=monitorFuturesAndDigitCoin, args=['1', symbolListSplit[1]]).start()
    # threading.Thread(target=monitorFuturesAndDigitCoin, args=['1', symbolListSplit[2]]).start()
    # threading.Thread(target=monitorFuturesAndDigitCoin, args=['1', symbolListSplit[3]]).start()
    # threading.Thread(target=monitorFuturesAndDigitCoin, args=['1', symbolListSplit[4]]).start()
    # threading.Thread(target=monitorFuturesAndDigitCoin, args=['1', symbolListSplit[5]]).start()
    # threading.Thread(target=monitorFuturesAndDigitCoin, args=['1', symbolListSplit[6]]).start()
    # threading.Thread(target=monitorFuturesAndDigitCoin, args=['1', symbolListSplit[7]]).start()
    threading.Thread(target=monitorFuturesAndDigitCoin, args=['1',symbolList]).start()

    # 外盘监控
    threading.Thread(target=monitorFuturesAndDigitCoin, args=['3', globalFutureSymbol]).start()

    # threading.Thread(target=monitorFuturesAndDigitCoin, args=["2", symbolListDigitCoin]).start()


if __name__ == '__main__':
    run()
