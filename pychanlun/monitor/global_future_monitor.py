# -*- coding: utf-8 -*-

from logbook import Logger
import traceback
from pychanlun.chanlun_service import get_data
from pychanlun.DingMsg import DingMsg
import signal
import rqdatac as rq
from datetime import datetime, timedelta
from et_stopwatch import Stopwatch
import time
import threading
from pychanlun.Mail import Mail

from pychanlun.db import DBPyChanlun
from pychanlun.config import config
from pychanlun.monitor.BusinessService import businessService
import pytz

import pymongo

log = Logger(__name__)

tz = pytz.timezone('Asia/Shanghai')


'''
综合监控
'''
# 米筐数据 主力连续合约RB88 这个会比实时数据少一天
symbolListDigitCoin = ['BTC'
                       # 'ETH_CQ', 'BCH_CQ', 'LTC_CQ', 'BSV_CQ'
                       ]
global_future_symbol = config['global_future_symbol']
global_stock_symbol = config['global_stock_symbol']
# 内盘期货
periodList1 = ['3m', '5m', '15m', '30m', '60m']
# 数字货币
periodList2 = ['1m', '3m', '5m', '15m', '30m', '60m']
# 外盘期货
periodList3 = ['3m', '5m', '15m', '30m', '60m']
# 高级别 高高级别映射
# 暂时用3d 3d
futureLevelMap = {
    '3m': ['15m', '60m'],
    '5m': ['30m', '180m'],
    '15m': ['60m', '1d'],
    '30m': ['180m', '3d'],
    '60m': ['1d', '3d'],
    '180m': ['3d', '3d'],
}
dominantSymbolInfoList = {}

# 期货公司在原有保证金基础上1%
marginLevelCompany = 0.01
# 期货账户
futuresAccount = 75
# 数字货币手续费0.05% 开平仓0.1%
digitCoinFee = 0.001
# 数字货币账户
digitCoinAccount = 60.80 / 10000
# 外盘期货账户
global_future_account = 6
maxAccountUseRate = 0.1
stopRate = 0.01
mail = Mail()
dingMsg = DingMsg()

filter_tag = ['双盘', '完备买', '完备卖', '扩展完备买', '扩展完备卖', '一类买', '一类卖', '二类买', '二类卖', '三类买', '三类卖', '准三买', '准三卖']


# 初始化业务对象
# businessService = BusinessService()

# 改成钉钉发送
def sendEmail(msg, symbol, period, signal, direction, amount, stop_lose_price, fire_time_str, price, date_created_str,
              close_price, tag):
    print(msg)
    dingMsg.send(msg)


# price 信号触发的价格， close_price 提醒时的收盘价 direction 多B 空S amount 开仓数量
def saveFutureSignal(symbol, period, fire_time_str, direction, signal, tag, price, close_price,
                     stop_lose_price, futureCalcObj):
    #  后面的存储的数据依赖 futureCalcObj
    if futureCalcObj == -1:
        print("symbol ->", symbol, " period->", period)
        return
    # perOrderStopRate 的止损率大于0.3 的信号只保存不再提醒出来，也就是不做止损较大的单子
    perOrderStopRate = futureCalcObj['perOrderStopRate']

    # 更新,实时更新持仓品种的价格
    saveFutureAutoPosition(symbol, period, fire_time_str, direction, signal, tag, price, close_price,
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
                'tag': tag,
                'price': price,
                'close_price': close_price,
                'amount': amount,
                'date_created': datetime.utcnow(),
                'stop_lose_price': stop_lose_price,
                'per_order_stop_rate': round(perOrderStopRate, 3)
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
            'tag': tag,
            'fire_time': fire_time,  # 信号发生的时间
            'price': price,
            'date_created': date_created,  # 记录插入的时间
            'close_price': close_price,  # 提醒时最新价格
            'direction': direction,
            'stop_lose_price': stop_lose_price,  # 当前信号的止损价
            'per_order_stop_rate': round(perOrderStopRate, 3),
            'update_count': 1,  # 这条背驰记录的更新次数
        })
        if abs((date_created - fire_time).total_seconds()) < 60 * 3 and perOrderStopRate <= 0.2:
            # 新增
            remind = saveFutureAutoPosition(symbol, period, fire_time_str, direction, signal, tag, price, close_price,
                                            stop_lose_price, futureCalcObj, True)
            if not remind:
                return
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
                "stop": stop_lose_price,
                "fire_time": fire_time_str,
                "price": price,
                "date_created": date_created_str,
                "close_price": close_price,
                "tag": tag,
                "per_order_stop_rate": round(perOrderStopRate, 3),
                "remind": 'Ding'
            }
            # 简洁版
            # msg = "%s %s %s %s %s %s %s %s %s %s %s" % (
            #     symbol, period, signal, direction + ' ', " [amount]: " + str(amount),这个也怪我
            #     " [stop]: " + str(stop_lose_price), " [fire]: " + fire_time_str, " [price]: " + str(price),
            #     " [create]: " + date_created_str,
            #     str(close_price), tag)
            sendEmail(msg, symbol, period, signal, direction, amount, stop_lose_price, fire_time_str, price,
                      date_created_str,
                      close_price, tag)


# 自动录入持仓列表  新增 status(holding,winEnd,loseEnd 状态) profit(盈利) profit_rate(盈利率)
def saveFutureAutoPosition(symbol, period, fire_time_str, direction, signal, tag, price, close_price,
                           stop_lose_price, futureCalcObj, insert):
    # CT NID CP 老虎无法交易
    if symbol == 'CT' or symbol == 'CP' or symbol == 'NID':
        return False

    remind = False
    temp_fire_time = datetime.strptime(fire_time_str, "%Y-%m-%d %H:%M")
    # 触发时间转换成UTC时间
    fire_time = temp_fire_time - timedelta(hours=8)
    # 查找自动持仓表中状态为holding的， 因为 止盈和止损的单子 还是有可能继续开仓的
    status = 'holding'
    date_created = datetime.utcnow()
    # 如果持仓表中这条记录 那么更新最新价格，如果没有新增

    different_direction = ""
    if direction == 'S' or direction == 'HS':
        direction = 'short'
        different_direction = 'long'
    else:
        direction = 'long'
        different_direction = 'short'

    # 如果是分型动止，方向需要反过来
    if signal == 'fractal':
        # fix bug 一个月才发现这个bug！！！！！导致空单一直无法动止，只有多单提醒了动止
        direction = 'long' if direction == 'short' else 'short'
    if insert is True:
        # 同品种 但是不同周期 的更新也记录下来
        # 同方向的持仓
        last_fire = DBPyChanlun['future_auto_position'].find_one({
            'symbol': symbol,
            'direction': direction,
            'status': status
        })
        # 反方向的持仓
        different_last_fire = DBPyChanlun['future_auto_position'].find_one({
            'symbol': symbol,
            'direction': different_direction,
            'status': status
        })
        # 持仓列表有该方向的记录
        if last_fire is not None:
            # 判断是否满足动止信号：
            if signal == 'fractal':
                stop_win_count = futureCalcObj['stop_win_count']
                stop_win_price = futureCalcObj['stop_win_price']
                fractal_price = futureCalcObj['fractal_price']
                #
                # 取出动止数组，更新动止数组的最后一项，然后再插入到表中
                if last_fire['symbol'] == 'BTC':
                    marginLevel = 1 / (last_fire['margin_rate'])
                elif last_fire['symbol'] in global_future_symbol:
                    # 外盘
                    marginLevel = 1 / last_fire['margin_rate']
                else:
                    # 内盘
                    marginLevel = 1 / (last_fire['margin_rate'] + config['margin_rate_company'])

                if last_fire['direction'] == "long":
                    stop_win_profit_rate = round(((stop_win_price - last_fire['price']) / last_fire['price']) * marginLevel, 2)
                    # print("long",stop_win_profit_rate)
                else:
                    stop_win_profit_rate = round(((last_fire['price'] - stop_win_price) / last_fire['price']) * marginLevel, 2)
                    # print("short",stop_win_profit_rate)
                # 动止盈利
                stop_win_money = round(last_fire['per_order_margin'] * stop_win_count * stop_win_profit_rate, 2)

                DBPyChanlun['future_auto_position'].find_one_and_update({
                    'symbol': symbol, 'direction': direction, 'status': status
                }, {
                    '$set': {
                        'close_price': close_price,  # 只需要更新最新价格，用于判断是否止损
                        'last_update_time': date_created,  # 最后信号更新时间
                        'last_update_signal': signal,  # 最后更新的信号
                        'last_update_period': period,  # 最后更新的周期
                        # 'amount':last_fire['amount'] - stop_win_count # 持仓的数量减去动止的数量
                    },
                    # $addToSet 重复的记录不会插入，只有不同的动止对象才会插入， $push 每次都会插入，  但是date_created 这个时间字段每次都不同，都会作为新纪录插入
                    '$addToSet': {
                        'dynamicPositionList': {
                            'date_created': date_created,  # 动止时间
                            'stop_win_count': stop_win_count,  # 动止的数量
                            'stop_win_price': stop_win_price,  # 动止时的价格
                            'stop_win_money': stop_win_money,  # 动止时的盈利
                            'fractal_price': fractal_price,  # 分型的价格
                            'direction': 'long' if direction == 'short' else 'short'
                        }
                    },
                    '$inc': {
                        'update_count': 1
                    }
                }, upsert=True)
                remind = True
            else:
                DBPyChanlun['future_auto_position'].find_one_and_update({
                    'symbol': symbol, 'direction': direction, 'status': status
                }, {
                    '$set': {
                        'close_price': close_price,  # 只需要更新最新价格，用于判断是否止损
                        'last_update_time': date_created,  # 最后信号更新时间
                        'last_update_signal': signal,  # 最后更新的信号
                        'last_update_period': period  # 最后更新的周期
                    },
                    '$inc': {
                        'update_count': 1
                    }
                }, upsert=True)
        else:
            # 动止信号 不作为新的记录插入持仓表
            # 线段破坏 不作为新的记录插入持仓表
            if signal != 'fractal' and signal != 'break':
                DBPyChanlun['future_auto_position'].insert_one({
                    'symbol': symbol,
                    'period': period,
                    'signal': signal,
                    'amount': futureCalcObj['maxOrderCount'],
                    'tag': tag,
                    'fire_time': fire_time,  # 信号发生的时间
                    'price': price,
                    'date_created': date_created,  # 记录插入的时间
                    'close_price': close_price,  # 提醒时最新价格
                    'direction': direction,
                    'stop_lose_price': stop_lose_price,  # 当前信号的止损价
                    'update_count': 1,  # 这条背驰记录的更新次数
                    'status': status,
                    'per_order_stop_money': futureCalcObj['perOrderStopMoney'],
                    'per_order_stop_rate': round(futureCalcObj['perOrderStopRate'], 2),
                    'per_order_margin': round(futureCalcObj['perOrderMargin'], 2),
                    'predict_stop_money': -round(futureCalcObj['perOrderStopMoney'] * futureCalcObj['maxOrderCount'], 2),
                    'margin_rate': futureCalcObj['marginRate'],
                    'total_margin': round(futureCalcObj['perOrderStopMoney'] * futureCalcObj['maxOrderCount'], 2),
                    'last_update_time': '',
                    'last_update_signal': '',
                    'last_update_period': '',

                })
                remind = True
        # 将之前反方向的持仓止盈 当前为动止信号，不全部止盈
        if signal != 'fractal' and different_last_fire is not None and last_fire is not None:
            if last_fire['direction'] == 'long':
                if different_last_fire['price'] >= last_fire['price']:
                    status = 'winEnd'
                else:
                    status = 'loseEnd'
            else:
                if different_last_fire['price'] <= last_fire['price']:
                    status = 'winEnd'
                else:
                    status = 'loseEnd'

            DBPyChanlun['future_auto_position'].find_one_and_update({
                'symbol': symbol, 'direction': different_direction, 'status': status
            }, {
                '$set': {
                    'close_price': close_price,  # 只需要更新最新价格，用于判断是否止损
                    'last_update_time': date_created,  # 最后信号更新时间
                    'last_update_signal': signal,  # 最后更新的信号
                    'last_update_period': period,  # 最后更新的周期
                    'status': status  # 将之前反方向的持仓状态改为止盈
                },
                '$inc': {
                    'update_count': 1
                }
            }, upsert=True)
    else:
        last_fire = DBPyChanlun['future_auto_position'].find_one({
            'symbol': symbol,
            'direction': direction,
            'status': status
        })
        #  如果当前价格已经触及到止损价，那么就讲状态设置为loseEnd
        if last_fire is not None:
            # print("最后一个", last_fire)
            if last_fire['symbol'] == 'BTC':
                marginLevel = 1 / (last_fire['margin_rate'])
            elif last_fire['symbol'] in global_future_symbol:
                marginLevel = 1 / last_fire['margin_rate']
            else:
                marginLevel = 1 / (last_fire['margin_rate'] + config['margin_rate_company'])
            # 之后价格再涨上来，status又会变成holding ,因此已经被止损的持仓不要再更新状态了
            if last_fire['status'] == 'holding':
                if (direction == 'long' and close_price <= last_fire['stop_lose_price']) or (direction == 'short' and close_price >= last_fire['stop_lose_price']):
                    # print("止损了",direction,close_price,last_fire['stop_lose_price'])
                    # 为了方便后面统计，在这里计算止损总额，如果性能降低就移出去

                    # 计算止损率
                    lose_end_rate = -abs(((close_price - last_fire['price']) / last_fire['price']) * marginLevel)
                    lose_end_money = round(last_fire['per_order_margin'] * last_fire['amount'] * lose_end_rate, 2)
                    lose_end_rate = round(lose_end_rate, 2)
                    DBPyChanlun['future_auto_position'].find_one_and_update({
                        '_id': last_fire['_id'], 'symbol': symbol, 'direction': direction, 'status': 'holding'
                    }, {
                        '$set': {
                            'close_price': close_price,  # 只需要更新最新价格，用于判断是否止损
                            'status': 'loseEnd',
                            'lose_end_price': close_price,  # 止损了需要将止损的价格插入到数据库中
                            'lose_end_time': date_created,  # 把止损触发时间保存起来
                            'lose_end_money': lose_end_money,
                            'lose_end_rate': lose_end_rate
                        },
                        '$inc': {
                            'update_count': 1
                        }
                    }, upsert=True)
                else:
                    # 没有被止损的持仓单更新最新盈利率
                    if last_fire['direction'] == "long":
                        current_profit_rate = round(((close_price - last_fire['price']) / last_fire['price']) * marginLevel, 2)
                        # print("long",current_profit_rate)
                    else:
                        current_profit_rate = round(((last_fire['price'] - close_price) / last_fire['price']) * marginLevel, 2)
                        # print("short",current_profit_rate)
                        # 未实现盈亏
                    current_profit = round(last_fire['per_order_margin'] * last_fire['amount'] * current_profit_rate, 2)
                    # print("持有中", direction, close_price, last_fire['stop_lose_price'])
                    status = 'holding'

                    # 如果有动止 ，计算动止的收益

                    # if signal == 'fractal':
                    #     stop_win_count = futureCalcObj['stop_win_count']
                    #     stop_win_price = futureCalcObj['stop_win_price']
                    #
                    #     if last_fire['direction'] == "long":
                    #         stop_win_profit_rate = round(((stop_win_price - last_fire['price']) / last_fire['price']) * marginLevel, 2)
                    #         # print("long",stop_win_profit_rate)
                    #     else:
                    #         stop_win_profit_rate = round(((last_fire['price'] - stop_win_price) / last_fire['price']) * marginLevel, 2)
                    #         # print("short",stop_win_profit_rate)
                    #         # 未实现盈亏
                    #     stop_win_money = round(last_fire['per_order_margin'] * stop_win_count * stop_win_profit_rate, 2)
                    #
                    #     DBPyChanlun['future_auto_position'].find_one_and_update({
                    #         'symbol': symbol, 'direction': direction, 'status': status
                    #     }, {
                    #         '$set': {
                    #             'close_price': close_price,  # 只需要更新最新价格，用于判断是否止损
                    #             'status': status,
                    #             'current_profit_rate': current_profit_rate,  # 当前浮盈比例
                    #             'current_profit': current_profit,  # 当前浮盈额
                    #             'stop_win_money': stop_win_money,  # 动止的收益
                    #             'stop_win_count': stop_win_count,  # 动止数量
                    #             'stop_win_price': stop_win_price,  # 动止价格
                    #
                    #         },
                    #         '$inc': {
                    #             'update_count': 1
                    #         }
                    #     }, upsert=True)
                    # else:
                    # 没有动止 就不要更新 stop_win_money 字段了
                    DBPyChanlun['future_auto_position'].find_one_and_update({
                        'symbol': symbol, 'direction': direction, 'status': status
                    }, {
                        '$set': {
                            'close_price': close_price,  # 只需要更新最新价格，用于判断是否止损
                            'status': status,
                            'current_profit_rate': current_profit_rate,  # 当前浮盈比例
                            'current_profit': current_profit,  # 当前浮盈额
                        },
                        '$inc': {
                            'update_count': 1
                        }
                    }, upsert=True)
    return remind


# 记录品种当前级别的方向
def saveFutureDirection(symbol, period, direction):
    DBPyChanlun['future_signal'].find_one_and_update({
        'symbol': symbol, 'period': period
    }, {
        '$set': {
            'level_direction': direction
        },
    }, sort=
    [('fire_time', pymongo.DESCENDING)]
    )


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


is_run = True


def signal_hanlder(signalnum, frame):
    log.info("正在停止程序。")
    global is_run
    is_run = False


# 监控期货
# timeScope 监控距离现在多少分钟的
def monitorFuturesAndDigitCoin(type, symbolList):
    if type == "1":
        # auth('13088887055', 'chanlun123456')
        # count = get_query_count()
        # print(count)
        # print("主力合约信息：", dominantSymbolInfoList)
        periodList = periodList1

    elif type == "2":
        symbolList = symbolListDigitCoin
        periodList = periodList2

    elif type == "3":
        # symbolList = global_future_symbol
        periodList = periodList3
    else:
        symbolList = global_stock_symbol
        periodList = periodList3
    while is_run:
        try:
            for i in range(len(symbolList)):
                if not is_run:
                    break
                for j in range(len(periodList)):
                    if not is_run:
                        break
                    symbol = symbolList[i]
                    period = periodList[j]
                    stopwatch = Stopwatch('%-10s %-10s %-10s' % ('耗时', symbol, period))
                    do_monitoring(symbol, period)
                    stopwatch.stop()
                    log.info(stopwatch)
            if type == "1" or type == "3":
                time.sleep(0)
            else:
                time.sleep(5)
        except BaseException as e:
            print("Error Occurred: {0}".format(traceback.format_exc()))
            if type == "1":
                print("期货出异常了", Exception)
            elif type == "2":
                print("OKEX出异常了", Exception)
                time.sleep(10)
            elif type == "3":
                print("外盘期货出异常了", Exception, e, symbol)
            else:
                print("外盘股票出异常了", Exception)


def do_monitoring(symbol, period):
    result = get_data(symbol, period)
    if result.get('close') is not None and len(result['close']) > 0:
        close_price = result['close'][-1]
        # 大级别macd 背驰成功率较高
        # if period != '1m' and period != '3m' and period != '5m':
        #     monitorBeichi(result, symbol, period, close_price)
        monitorHuila(result, symbol, period, close_price)
        monitorTupo(result, symbol, period, close_price)
        monitorVReverse(result, symbol, period, close_price)
        monitorFiveVReverse(result, symbol, period, close_price)
        monitorDuanBreak(result, symbol, period, close_price)
        monitorFractal(result, symbol, period, close_price)


def monitorBeichi(result, symbol, period, closePrice):
    signal = 'beichi'
    # 监控背驰
    if len(result['buyMACDBCData']['date']) > 0:
        # if not notLower:
        #    return
        fire_time = result['buyMACDBCData']['date'][-1]
        price = result['buyMACDBCData']['data'][-1]
        # tag = result['buyMACDBCData']['tag'][-1]
        tag = ""
        stop_lose_price = result['buyMACDBCData']['stop_lose_price'][-1]
        futureCalcObj = calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        direction = 'B'
        saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj,above_ma20)
    if len(result['sellMACDBCData']['date']) > 0:
        # if not notHigher:
        #    return
        fire_time = result['sellMACDBCData']['date'][-1]
        price = result['sellMACDBCData']['data'][-1]
        # tag = result['sellMACDBCData']['tag'][-1]
        tag = ""
        stop_lose_price = result['sellMACDBCData']['stop_lose_price'][-1]
        futureCalcObj = calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        direction = 'S'
        saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj,above_ma20)


'''
监控回拉
'''

# 为提高胜率 小级别 一定要 不破前高和 不破前低才能进场
def monitorHuila(result, symbol, period, closePrice):
    signal = 'huila'
    # big_period = period != '1m' and period != '3m' and period != '5m'
    # notLower = result['notLower']
    # notHigher = result['notHigher']

    # 监控回拉
    if len(result['buy_zs_huila']['date']) > 0:
        fire_time = result['buy_zs_huila']['date'][-1]
        price = result['buy_zs_huila']['data'][-1]
        tag = result['buy_zs_huila']['tag'][-1]
        above_ma20 = result['buy_zs_huila']['above_ma20'][-1]
        stop_lose_price = result['buy_zs_huila']['stop_lose_price'][-1]
        futureCalcObj = calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        direction = 'B'
        # 大级别直接保存
        saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj, above_ma20)
        # else:
        #     # 小级别除非是双盘，否则一定要不破前低
        #     if notLower:
        #         saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj,above_ma20)
        #     elif "双盘" in tag or "完备" in tag:
        #         saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj,above_ma20)

    if len(result['sell_zs_huila']['date']) > 0:
        fire_time = result['sell_zs_huila']['date'][-1]
        price = result['sell_zs_huila']['data'][-1]
        tag = result['sell_zs_huila']['tag'][-1]
        above_ma20 = result['sell_zs_huila']['above_ma20'][-1]
        stop_lose_price = result['sell_zs_huila']['stop_lose_price'][-1]
        futureCalcObj = calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        direction = 'S'
        saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj,above_ma20)
'''
监控突破
'''


# 分析走势发现有很多顶部都是用3m 5m 的反向中枢突破套到的,如果突破失败，反手做多 就行了
# 因此突破单不用 notLower notHigher 过滤
def monitorTupo(result, symbol, period, closePrice):
    signal = 'tupo'
    # 监控突破
    if len(result['buy_zs_tupo']['date']) > 0:
        fire_time = result['buy_zs_tupo']['date'][-1]
        price = result['buy_zs_tupo']['data'][-1]
        stop_lose_price = result['buy_zs_tupo']['stop_lose_price'][-1]
        tag = ''
        above_ma20 = result['buy_zs_tupo']['above_ma20'][-1]
        direction = 'B'
        futureCalcObj = calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj,above_ma20)
    if len(result['sell_zs_tupo']['date']) > 0:
        fire_time = result['sell_zs_tupo']['date'][-1]
        price = result['sell_zs_tupo']['data'][-1]
        stop_lose_price = result['sell_zs_tupo']['stop_lose_price'][-1]
        tag = ''
        above_ma20 = result['sell_zs_tupo']['above_ma20'][-1]
        direction = 'S'
        futureCalcObj = calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj,above_ma20)
'''
监控3买卖 V反
'''


def monitorVReverse(result, symbol, period, closePrice):
    signal = 'v_reverse'
    # 监控V反
    if len(result['buy_v_reverse']['date']) > 0:
        fire_time = result['buy_v_reverse']['date'][-1]
        price = result['buy_v_reverse']['data'][-1]
        stop_lose_price = result['buy_v_reverse']['stop_lose_price'][-1]
        tag = ''
        above_ma20 = result['buy_v_reverse']['above_ma20'][-1]
        direction = 'B'
        futureCalcObj = calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        if above_ma20:
            saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj,above_ma20)
    if len(result['sell_v_reverse']['date']) > 0:
        fire_time = result['sell_v_reverse']['date'][-1]
        price = result['sell_v_reverse']['data'][-1]
        stop_lose_price = result['sell_v_reverse']['stop_lose_price'][-1]
        tag = ''
        above_ma20 = result['sell_v_reverse']['above_ma20'][-1]
        direction = 'S'
        futureCalcObj = calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        if above_ma20:
            saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj,above_ma20)

'''
监控5浪及以上 V反
'''


def monitorFiveVReverse(result, symbol, period, closePrice):
    signal = 'five_v_reverse'
    if len(result['buy_five_v_reverse']['date']) > 0:
        fire_time = result['buy_five_v_reverse']['date'][-1]
        price = result['buy_five_v_reverse']['data'][-1]
        stop_lose_price = result['buy_five_v_reverse']['stop_lose_price'][-1]
        tag = ''
        above_ma20 = result['buy_five_v_reverse']['above_ma20'][-1]
        direction = 'B'
        futureCalcObj = calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        if above_ma20:
            saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj,above_ma20)
    if len(result['sell_five_v_reverse']['date']) > 0:
        fire_time = result['sell_five_v_reverse']['date'][-1]
        price = result['sell_five_v_reverse']['data'][-1]
        stop_lose_price = result['sell_five_v_reverse']['stop_lose_price'][-1]
        tag = ''
        above_ma20 = result['sell_five_v_reverse']['above_ma20'][-1]
        direction = 'S'
        futureCalcObj = calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        if above_ma20:
            saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj,above_ma20)

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
        tag = ''
        above_ma20 = result['buy_duan_break']['above_ma20'][-1]
        direction = 'B'
        futureCalcObj = calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        if above_ma20:
            saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj,above_ma20)
    if len(result['sell_duan_break']['date']) > 0:
        fire_time = result['sell_duan_break']['date'][-1]
        price = result['sell_duan_break']['data'][-1]
        stop_lose_price = result['sell_duan_break']['stop_lose_price'][-1]
        tag = ''
        above_ma20 = result['sell_duan_break']['above_ma20'][-1]
        direction = 'S'
        futureCalcObj = calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        if above_ma20:
            saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj,above_ma20)

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
    if result['fractal'][0] != {}:
        levelDirection = result['fractal'][0]['direction']
        if levelDirection == 1:
            saveFutureDirection(symbol, period, '多')
        else:
            saveFutureDirection(symbol, period, '空')
    signal = 'fractal'
    # 查找是否持有多单
    positionInfoLong = businessService.getPosition(symbol, period, 'holding', 'long')
    # 查找是否持有空单
    positionInfoShort = businessService.getPosition(symbol, period, 'holding', 'short')

    # 多单有持仓
    if positionInfoLong != -1:

        # 多单查找向上笔的顶分型
        # 高级别
        if result['fractal'][0] != {} and result['fractal'][0]['direction'] == 1:
            fire_time = result['fractal'][0]['top_fractal']['date']
            # 顶分型的底
            price = result['fractal'][0]['top_fractal']['bottom']
            stop_lose_price = result['fractal'][0]['top_fractal']['top']
            tag = result['fractal'][0]['period']
            direction = 'S'
            # 顶分型的顶
            top_price = result['fractal'][0]['top_fractal']['top']
            futureCalcObj = calMaxOrderCount(symbol, closePrice, top_price, period, signal)
            # 当前价格低于顶分型的底
            if closePrice <= price:
                stopWinCount = calStopWinCount(symbol, period, positionInfoLong, closePrice)
                # 保存动止手数
                futureCalcObj['stop_win_count'] = stopWinCount
                # 保存动止时的价格
                futureCalcObj['stop_win_price'] = closePrice
                # 保存分型的价格
                futureCalcObj['fractal_price'] = price

                saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice,
                                 stop_lose_price, futureCalcObj)
        # 高高级别
        if result['fractal'][1] != {} and result['fractal'][1]['direction'] == 1:
            fire_time = result['fractal'][1]['top_fractal']['date']
            price = result['fractal'][1]['top_fractal']['bottom']
            stop_lose_price = result['fractal'][1]['top_fractal']['top']
            tag = result['fractal'][1]['period']
            direction = 'HS'
            # 顶分型的顶
            top_price = result['fractal'][1]['top_fractal']['top']
            futureCalcObj = calMaxOrderCount(symbol, closePrice, top_price, period, signal)

            # 当前价格低于顶分型的底
            if closePrice <= price:
                stopWinCount = calStopWinCount(symbol, period, positionInfoLong, closePrice)
                # 保存动止手数
                futureCalcObj['stop_win_count'] = stopWinCount
                # 保存动止时的价格
                futureCalcObj['stop_win_price'] = closePrice
                # 保存分型的价格
                futureCalcObj['fractal_price'] = price
                saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice,
                                 stop_lose_price, futureCalcObj)
    if positionInfoShort != -1:
        # 空单查找向下笔的底分型
        # 高级别
        if result['fractal'][0] != {} and result['fractal'][0]['direction'] == -1:
            fire_time = result['fractal'][0]['bottom_fractal']['date']
            price = result['fractal'][0]['bottom_fractal']['top']
            stop_lose_price = result['fractal'][0]['bottom_fractal']['bottom']
            tag = result['fractal'][0]['period']
            direction = 'B'
            # 底分型的底部
            bottom_price = result['fractal'][0]['bottom_fractal']['bottom']
            futureCalcObj = calMaxOrderCount(symbol, closePrice, bottom_price, period, signal)

            # 当前价格高于底分型的顶
            if closePrice >= price:
                stopWinCount = calStopWinCount(symbol, period, positionInfoShort, closePrice)
                # 保存动止手数
                futureCalcObj['stop_win_count'] = stopWinCount
                # 保存动止时的价格
                futureCalcObj['stop_win_price'] = closePrice
                # 保存分型的价格
                futureCalcObj['fractal_price'] = price
                saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice,
                                 stop_lose_price, futureCalcObj)
        # 高高级别
        if result['fractal'][1] != {} and result['fractal'][1]['direction'] == -1:
            fire_time = result['fractal'][1]['bottom_fractal']['date']
            price = result['fractal'][1]['bottom_fractal']['top']
            stop_lose_price = result['fractal'][1]['bottom_fractal']['bottom']
            tag = result['fractal'][1]['period']
            direction = 'HB'
            # 底分型的底部
            bottom_price = result['fractal'][1]['bottom_fractal']['bottom']
            futureCalcObj = calMaxOrderCount(symbol, closePrice, bottom_price, period, signal)

            # 当前价格高于底分型的顶
            if closePrice >= price:
                stopWinCount = calStopWinCount(symbol, period, positionInfoShort, closePrice)
                # 保存动止手数
                futureCalcObj['stop_win_count'] = stopWinCount
                # 保存动止时的价格
                futureCalcObj['stop_win_price'] = closePrice
                # 保存分型的价格
                futureCalcObj['fractal_price'] = price
                saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice,
                                 stop_lose_price, futureCalcObj)


# 计算出开仓手数（止损系数，资金使用率双控）
# 返回最大开仓手数，1手止损的金额，1手止损的百分比
def calMaxOrderCount(dominantSymbol, openPrice, stopPrice, period, signal):
    # openPrice stopPrice等于历史行情某个stopPrice 会导致除0异常
    if openPrice == stopPrice:
        return -1
    # 兼容数字货币 外盘期货
    if 'BTC' in dominantSymbol:
        account = digitCoinAccount
        margin_rate = 0.05
        # 因为使用20倍杠杆所以 需要除以20
        perOrderMargin = 0.01 * openPrice * margin_rate
        # 1手止损的比率
        perOrderStopRate = (abs(openPrice - stopPrice) / openPrice + digitCoinFee) * 20
        # 1手止损的金额
        perOrderStopMoney = round((perOrderMargin * perOrderStopRate), 4)
        maxAccountUse = account * 10000 * 0.4
        maxStopMoney = account * 10000 * 0.1
    elif dominantSymbol in config['global_future_symbol'] or dominantSymbol in config['global_stock_symbol']:
        account = global_future_account
        margin_rate = config['futureConfig'][dominantSymbol]['margin_rate']
        contract_multiplier = config['futureConfig'][dominantSymbol]['contract_multiplier']
        # 计算1手需要的保证金
        perOrderMargin = int(openPrice * contract_multiplier * margin_rate)
        # 1手止损的金额
        perOrderStopMoney = abs(openPrice - stopPrice) * contract_multiplier
        # 1手止损的百分比
        perOrderStopRate = round((perOrderStopMoney / perOrderMargin), 2)

        maxAccountUse = account * 10000 * 0.2
        maxStopMoney = account * 10000 * 0.1
    # 内盘期货
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

    # print("debug ",dominantSymbol,account,maxStopMoney,maxAccountUse,perOrderStopMoney,"1手保证金：",perOrderMargin,openPrice, stopPrice,"1手止损：",perOrderStopRate,perOrderStopMoney,period,contract_multiplier)
    maxOrderCount1 = round(maxStopMoney / perOrderStopMoney)
    # 根据最大资金使用率算出的开仓手数(四舍五入)
    maxOrderCount2 = round(maxAccountUse / perOrderMargin)
    maxOrderCount = maxOrderCount2 if maxOrderCount1 > maxOrderCount2 else maxOrderCount1
    # print(dominantSymbol,"--> ",period,"--> ",perOrderStopRate,"-->",maxStopMoney,"-->",maxStopMoney / perOrderStopMoney,"-->",maxAccountUse,"-->",maxAccountUse / perOrderMargin ,"->",perOrderMargin)
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
    # if 'BTC' in symbol or symbol in config['global_future_symbol'] or symbol in config['global_stock_symbol']:
    #     return 0
    # 动止公式:  (1 - stopWinPosRate) / stopWinPosRate = winLoseRate
    # stopWinPosRate: 动态止盈多少仓位
    # winLoseRate: 当前的盈亏比
    # 查库耗时 0.005s
    # 该品种有持仓
    open_pos_price = positionInfo['price']
    open_pos_amount = positionInfo['amount']
    stop_lose_price = positionInfo['stop_lose_price']
    stop_win_price = closePrice
    winLoseRate = round(abs(stop_win_price - open_pos_price) /
                        abs(open_pos_price - stop_lose_price), 2)
    # 标准动止 第1次 高级别 走30%  ， 第2次 高高级别再走30%  ，但如果当前盈亏比已经超过 2.3：1，那么第1次就不用动止30%，需要计算
    # if winLoseRate > 2.3:
    stopWinPosRate = round(1 / (winLoseRate + 1), 2)
    # else:
    #     stopWinPosRate = 0.3
    stopWinCount = round(stopWinPosRate * open_pos_amount)
    print("当前盈亏比", winLoseRate, "当前动止仓位百分比",
          stopWinPosRate, "动止手数", stopWinCount)
    return stopWinCount


def run(**kwargs):
    signal.signal(signal.SIGINT, signal_hanlder)
    # 主力合约，主力合约详细信息
    symbolList, dominantSymbolInfoList = getDominantSymbol()
    # 24个品种 拆分成2份  2分16秒 轮完一次
    # symbolListSplit = [symbolList[i:i + 12] for i in range(0, len(symbolList), 12)]
    # 27个品种 拆分3份   1份25秒 轮完一次
    # 外盘 14个品种
    global_future_split = [global_future_symbol[i:i + 4] for i in range(0, len(global_future_symbol), 4)]
    #
    thread_list = [threading.Thread(target=monitorFuturesAndDigitCoin, args=['3', global_future_split[0]]),
                   threading.Thread(target=monitorFuturesAndDigitCoin, args=['3', global_future_split[1]]),
                   threading.Thread(target=monitorFuturesAndDigitCoin, args=['3', global_future_split[2]]),
                   threading.Thread(target=monitorFuturesAndDigitCoin, args=['3', global_future_split[3]])]

    #  测试一：内盘3线程 ，外盘4线程 ，共7线程    内盘 3分10秒 循环一次  外盘 2分34秒 循环一次
    #  测试二：内盘3线程 ，外盘2线程 ，共5线程    内盘 2分30秒 循环一次  外盘 3分24秒 循环一次
    #  测试三：内盘4线程， 外盘4线程 ，共8线程    内盘 2分58秒 循环一次  外盘 3分08秒 循环一次
    stopwatch = Stopwatch("监控")
    for thread in thread_list:
        thread.start()

    while True:
        for thread in thread_list:
            if thread.is_alive():
                break
        else:
            break
    stopwatch.stop()
    print(stopwatch)


if __name__ == '__main__':
    run()
