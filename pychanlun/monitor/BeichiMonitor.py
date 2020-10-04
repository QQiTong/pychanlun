# -*- coding: utf-8 -*-

import asyncio
import math
import queue
import signal
import threading
import traceback
from datetime import datetime, timedelta

import time
import pymongo
import pytz
import rqdatac as rq
from et_stopwatch import Stopwatch
from loguru import logger

from pychanlun.DingMsg import DingMsg
from pychanlun.Mail import Mail
from pychanlun.chanlun_service import get_data_v2
from pychanlun.config import config
from pychanlun.db import DBPyChanlun
from pychanlun.monitor.BusinessService import businessService

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
dominant_symbol_info_list = {}

# 期货公司在原有保证金基础上1%
marginLevelCompany = 0.01
# 期货账户
futuresAccount = 58
# 数字货币手续费0.05% 开平仓0.1%
digitCoinFee = 0.001
# 数字货币账户
digitCoinAccount = 60.80 / 10000
# 外盘期货账户
global_future_account = 6
maxAccountUseRate = 0.10
stopRate = 0.004
mail = Mail()
dingMsg = DingMsg()

filter_tag = ['双盘', '完备买', '完备卖', '扩展完备买', '扩展完备卖', '一类买', '一类卖', '二类买', '二类卖', '三类买', '三类卖', '准三买', '准三卖']


# price 信号触发的价格， close_price 提醒时的收盘价 direction 多B 空S amount 开仓数量
async def saveFutureSignal(symbol, period, fire_time_str, direction, signal, tag, price, close_price,
                           stop_lose_price, futureCalcObj):
    #  后面的存储的数据依赖 futureCalcObj
    if futureCalcObj == -1:
        print("symbol ->", symbol, " period->", period)
        return
    # perOrderStopRate 的止损率大于0.3 的信号只保存不再提醒出来，也就是不做止损较大的单子
    perOrderStopRate = futureCalcObj['perOrderStopRate']
    above_ma5, above_ma20, not_lower, not_higher, fractal, power = await getFormatNotifyMsg(direction, signal, futureCalcObj)
    # 更新,实时更新持仓品种的价格
    await saveFutureAutoPosition(symbol, period, fire_time_str, direction, signal, tag, price, close_price,
                                 stop_lose_price, futureCalcObj, False)

    if signal == 'fractal':
        amount = futureCalcObj['stop_win_count']
    else:
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
            'above_ma5': above_ma5,
            'above_ma20': above_ma20,
            'not_lower': not_lower,
            'not_higher': not_higher,
            "fractal": fractal,  # 信号触发时是否在大级别分型确立
            "power": power  # 5个指标综合判断当前信号强度
        })
        max_stop_rate = 0.1
        if signal == 'fractal':
            max_stop_rate = 0.3
            print(signal, symbol, period, futureCalcObj, perOrderStopRate)

        if abs((date_created - fire_time).total_seconds()) < 60 * 4 and perOrderStopRate <= max_stop_rate:
            # 新增
            remind = await saveFutureAutoPosition(symbol, period, fire_time_str, direction, signal, tag, price, close_price,
                                                  stop_lose_price, futureCalcObj, True)
            if not remind:
                return
            # 在3分钟内的触发邮件通知  3分钟就能扫内盘+外盘
            # 把数据库的utc时间 转成本地时间
            fire_time_str = (fire_time + timedelta(hours=8)).strftime('%m-%d %H:%M:%S')
            date_created_str = (date_created + timedelta(hours=8)).strftime('%m-%d %H:%M:%S')

            signalCN = ''
            if signal == 'beichi':
                signalCN = "背驰"
            elif signal == 'huila':
                signalCN = "拉回"
            elif signal == 'tupo':
                signalCN = "突破"
            elif signal == 'break':
                signalCN = "破坏"
            elif signal == 'fractal':
                signalCN = "分型动止"
            elif signal == 'v_reverse' or signal == 'five_v_reverse':
                signalCN = "V反"

            msg = {
                "品种": symbol,
                "周期": period,
                "信号": signalCN,
                "方向": '买' if direction == 'B' else '卖',
                "数量": amount,
                "止损价": stop_lose_price,
                "止损率": str(int(perOrderStopRate * 100)) + '%',
                "分类": tag,
                "触发价格": price,
                "触发时间": fire_time_str,
                "提醒价格": close_price,
                "提醒时间": date_created_str,
                "5日线": above_ma5,
                "20日线": above_ma20,
                '线段前低': not_lower,
                '线段前高': not_higher,
                "大级别分型": fractal,
                "动力": (str(power) + "%") if power != "" else ""
            }
            dingMsg.send(msg)

# 获取格式化后的指标
async def getFormatNotifyMsg(direction, signal, futureCalcObj):
    not_lower = futureCalcObj['not_lower']
    if not_lower:
        not_lower = '上'
    else:
        not_lower = '下'

    not_higher = futureCalcObj['not_higher']
    if not_higher:
        not_higher = '下'
    else:
        not_higher = '上'

    # 分型信号 这两个值为空
    above_ma5 = ""
    above_ma20 = ""
    if 'above_ma5' in futureCalcObj:
        above_ma5 = futureCalcObj['above_ma5']
        if above_ma5:
            above_ma5 = '上'
        else:
            above_ma5 = '下'
    if 'above_ma20' in futureCalcObj:
        above_ma20 = futureCalcObj['above_ma20']
        if above_ma20:
            above_ma20 = '上'
        else:
            above_ma20 = '下'
    # 分型信号 这两个值为空
    fractal = ""
    power = ""
    if 'fractal' in futureCalcObj:
        fractal = futureCalcObj['fractal']
    if 'power' in futureCalcObj:
        power = futureCalcObj['power']
    # 有分型字段  并且当前信号不是分型动止信号
    if fractal != "" and signal != 'fractal':
        if fractal:
            if direction == 'B':
                fractal = '上'
            else:
                fractal = '下'
        else:
            if direction == 'S':
                fractal = '上'
            else:
                fractal = '下'
    return above_ma5, above_ma20, not_lower, not_higher, fractal, power


# 自动录入持仓列表  新增 status(holding,winEnd,loseEnd 状态) profit(盈利) profit_rate(盈利率)
async def saveFutureAutoPosition(symbol, period, fire_time_str, direction, signal, tag, price, close_price,
                                 stop_lose_price, futureCalcObj, insert):
    # CT NID CP 老虎无法交易
    if symbol == 'CT' or symbol == 'CP':
        return False

    remind = False
    temp_fire_time = datetime.strptime(fire_time_str, "%Y-%m-%d %H:%M")
    # 触发时间转换成UTC时间
    fire_time = temp_fire_time - timedelta(hours=8)
    # 查找自动持仓表中状态为holding的， 因为 止盈和止损的单子 还是有可能继续开仓的
    status = 'holding'
    date_created = datetime.utcnow()
    above_ma5, above_ma20, not_lower, not_higher, fractal, power = await getFormatNotifyMsg(direction, signal, futureCalcObj)
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
                fractal_period = tag
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
                stop_win_money = int(last_fire['per_order_margin'] * stop_win_count * stop_win_profit_rate)
                # 动止后剩下的数量
                available_amount = last_fire['amount'] - stop_win_count
                if available_amount > 0:

                    DBPyChanlun['future_auto_position'].find_one_and_update({
                        'symbol': symbol, 'direction': direction, 'status': status
                    }, {
                        '$set': {
                            'close_price': close_price,  # 只需要更新最新价格，用于判断是否止损
                            'last_update_time': date_created,  # 最后信号更新时间
                            'last_update_signal': signal,  # 最后更新的信号
                            'last_update_period': period,  # 最后更新的周期
                            'amount': available_amount  # 持仓的数量减去动止的数量
                        },
                        # $addToSet 重复的记录不会插入，只有不同的动止对象才会插入， $push 每次都会插入，  但是date_created 这个时间字段每次都不同，都会作为新纪录插入
                        '$addToSet': {
                            'dynamicPositionList': {
                                'date_created': date_created,  # 动止时间
                                'stop_win_count': stop_win_count,  # 动止的数量
                                'stop_win_price': stop_win_price,  # 动止时的价格
                                'stop_win_money': stop_win_money,  # 动止时的盈利
                                'fractal_price': fractal_price,  # 分型的价格
                                'direction': 'long' if direction == 'short' else 'short',
                                'fractal_period': fractal_period  # 大级别分型周期
                            }
                        },
                        '$inc': {
                            'update_count': 1
                        }
                    }, upsert=True)
                else:
                    # 如果 动止后 剩余数量 小于1手，将持仓状态设置为止盈
                    print(symbol, period, "动止后数量为小于1直接止盈")
                    winEndPercent = abs(round(((float(close_price) - last_fire['price']) / last_fire['price']) * marginLevel, 2))
                    # 止盈已实现盈亏
                    win_end_money = round(last_fire['per_order_margin'] * last_fire['amount'] * winEndPercent, 2)
                    # 止盈比率
                    win_end_rate = round(winEndPercent, 2)

                    DBPyChanlun['future_auto_position'].find_one_and_update({
                        'symbol': symbol, 'direction': direction, 'status': status
                    }, {
                        '$set': {
                            'close_price': close_price,  # 只需要更新最新价格，用于判断是否止损
                            'last_update_time': date_created,  # 最后信号更新时间
                            'last_update_signal': signal,  # 最后更新的信号
                            'last_update_period': period,  # 最后更新的周期
                            'status': 'winEnd',  # 将之前反方向的持仓状态改为止盈
                            'win_end_price': close_price,
                            'win_end_money': win_end_money,
                            'win_end_rate': win_end_rate,
                            'win_end_time': date_created,
                        },
                        '$inc': {
                            'update_count': 1
                        }
                    }, upsert=True)
                # 提醒
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
            # 线段破坏 不作为新的记录插入持仓表 and signal != 'break'
            if signal != 'fractal':
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
                    'above_ma5': above_ma5,
                    'above_ma20': above_ma20,
                    'not_lower': not_lower,
                    'not_higher': not_higher,
                    'fractal': fractal,
                    'power': power
                })
                remind = True
        # 将之前反方向的持仓止盈 当前为动止信号，不全部止盈
        print("反向仓：", different_last_fire, " 当前仓：", last_fire)
        if signal != 'fractal' and different_last_fire is not None and last_fire is None:
            status = 'winEnd'
            print("进入了反向仓 ：", different_direction, " 当前仓 ", last_fire)
            # 计算之前的反向仓的盈利
            win_end_money = different_last_fire['current_profit']
            win_end_price = close_price
            win_end_rate = different_last_fire['current_profit_rate']
            DBPyChanlun['future_auto_position'].find_one_and_update({
                'symbol': symbol, 'direction': different_direction, 'status': 'holding'
            }, {
                '$set': {
                    'close_price': close_price,  # 只需要更新最新价格，用于判断是否止损
                    'last_update_time': date_created,  # 最后信号更新时间
                    'last_update_signal': signal,  # 最后更新的信号
                    'last_update_period': period,  # 最后更新的周期
                    'status': status,  # 将之前反方向的持仓状态改为止盈
                    'win_end_price': win_end_price,
                    'win_end_money': win_end_money,
                    'win_end_rate': win_end_rate,
                    'win_end_time': date_created,
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
                    current_profit = int(last_fire['per_order_margin'] * last_fire['amount'] * current_profit_rate)
                    # print("持有中", direction, close_price, last_fire['stop_lose_price'])
                    status = 'holding'

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
async def saveFutureDirection(symbol, period, direction):
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
    # 将43个品种分成2组
    firstGroup = symbolList[:28]
    secondGroup = symbolList[-15:]
    currentGroup = firstGroup

    # 主力合约列表
    dominantSymbolList = []
    for i in range(len(currentGroup)):
        df = rq.futures.get_dominant(
            currentGroup[i], start_date=None, end_date=None, rule=0)
        dominantSymbol = df[-1]
        dominantSymbolList.append(dominantSymbol)
        dominantSymbolInfo = rq.instruments(dominantSymbol)
        dominant_symbol_info_list[dominantSymbol] = dominantSymbolInfo.__dict__
    return dominantSymbolList, dominant_symbol_info_list


is_run = True


def signal_handler(signalnum, frame):
    logger.info("正在停止程序。", signalnum, frame)
    global is_run
    is_run = False


def monitor_futures_and_digitcoin(symbol_list, period_list):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    tasks = []
    for i in range(len(symbol_list)):
        for j in range(len(period_list)):
            task = asyncio.ensure_future(do_monitoring(symbol_list[i], period_list[j]))
            tasks.append(task)
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


async def get_chanlun_data(symbol, period):
    return get_data_v2(symbol, period)


async def do_monitoring(symbol, period):
    stop_watch = Stopwatch('%-10s %-10s %-10s' % ('耗时', symbol, period))
    try:
        result = await get_chanlun_data(symbol, period)
        if result is not None and result.get('close') is not None and len(result['close']) > 0:
            close_price = result['close'][-1]
            # await monitorBeichi(result, symbol, period, close_price)
            await monitorHuila(result, symbol, period, close_price)
            # await monitorTupo(result, symbol, period, close_price)
            # await monitorVReverse(result, symbol, period, close_price)
            # await monitorFiveVReverse(result, symbol, period, close_price)
            # await monitorDuanBreak(result, symbol, period, close_price)
            await monitorFractal(result, symbol, period, close_price)
    except BaseException as e:
        logger.error("Error Occurred: {0}".format(traceback.format_exc()))
    stop_watch.stop()
    logger.info(stop_watch)


# 组合综合指标
async def combineIndicator(direction, above_ma5, above_ma20, not_lower, not_higher, fractal, futureCalcObj):
    if futureCalcObj == -1:
        return -1
    # 计算动力
    power = 0
    if direction == 'B':
        if above_ma5:
            power = power + 1
        if above_ma20:
            power = power + 1
        if not_lower:
            power = power + 1
        if not not_higher:
            power = power + 1
        if fractal != "" and fractal:
            power = power + 1
    else:
        if not above_ma5:
            power = power + 1
        if not above_ma20:
            power = power + 1
        if not not_lower:
            power = power + 1
        if not_higher:
            power = power + 1
        if fractal != "" and fractal:
            power = power + 1
    power = power * 20
    futureCalcObj['above_ma5'] = above_ma5
    futureCalcObj['above_ma20'] = above_ma20
    futureCalcObj['not_lower'] = not_lower
    futureCalcObj['not_higher'] = not_higher
    futureCalcObj['fractal'] = fractal
    futureCalcObj['power'] = power
    return futureCalcObj


async def monitorBeichi(result, symbol, period, closePrice):
    signal = 'beichi'
    # 使用notlower notHigher 过滤确保当前只做2买，完备，3买
    not_lower = result['notLower']
    not_higher = result['notHigher']
    # 监控背驰
    if len(result['buyMACDBCData']['date']) > 0:
        fire_time = result['buyMACDBCData']['date'][-1]
        price = result['buyMACDBCData']['data'][-1]
        above_ma5 = result['buyMACDBCData']['above_ma5'][-1]
        above_ma20 = result['buyMACDBCData']['above_ma20'][-1]
        # tag = result['buyMACDBCData']['tag'][-1]
        tag = ""
        direction = 'B'
        stop_lose_price = result['buyMACDBCData']['stop_lose_price'][-1]
        futureCalcObj = await calMaxOrderCount(symbol, price, stop_lose_price, period, signal)

        fractal = ""
        # 借助大级别分型信号进行过滤
        if result['fractal'][0] != {} and result['fractal'][0]['direction'] == -1:
            # 底分型的顶部
            top_price = result['fractal'][0]['bottom_fractal']['top']
            fractal = True if closePrice >= top_price else False
        futureCalcObj = await combineIndicator(direction, above_ma5, above_ma20, not_lower, not_higher, fractal, futureCalcObj)
        if above_ma5 or not_lower:
            await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)
    if len(result['sellMACDBCData']['date']) > 0:
        fire_time = result['sellMACDBCData']['date'][-1]
        price = result['sellMACDBCData']['data'][-1]
        above_ma5 = result['sellMACDBCData']['above_ma5'][-1]
        above_ma20 = result['sellMACDBCData']['above_ma20'][-1]
        # tag = result['sellMACDBCData']['tag'][-1]
        tag = ""
        direction = 'S'
        stop_lose_price = result['sellMACDBCData']['stop_lose_price'][-1]
        futureCalcObj = await calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        fractal = ""
        if result['fractal'][0] != {} and result['fractal'][0]['direction'] == 1:
            # 顶分型的底部
            bottom_price = result['fractal'][0]['top_fractal']['bottom']
            fractal = True if closePrice <= bottom_price else False
        futureCalcObj = await combineIndicator(direction, above_ma5, above_ma20, not_lower, not_higher, fractal, futureCalcObj)

        if not above_ma5 or not_higher:
            await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)


'''
监控回拉
'''


# 为提高胜率 小级别 一定要 不破前高和 不破前低才能进场
async def monitorHuila(result, symbol, period, closePrice):
    signal = 'huila'
    not_lower = result['notLower']
    not_higher = result['notHigher']
    # 监控回拉
    if len(result['buy_zs_huila']['date']) > 0:
        fire_time = result['buy_zs_huila']['date'][-1]
        price = result['buy_zs_huila']['data'][-1]
        tag = result['buy_zs_huila']['tag'][-1]
        above_ma5 = result['buy_zs_huila']['above_ma5'][-1]
        above_ma20 = result['buy_zs_huila']['above_ma20'][-1]
        stop_lose_price = result['buy_zs_huila']['stop_lose_price'][-1]
        futureCalcObj = await calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        direction = 'B'
        fractal = ""
        # 借助大级别分型信号进行过滤
        if result['fractal'][0] != {} and result['fractal'][0]['direction'] == -1:
            # 底分型的顶部
            top_price = result['fractal'][0]['bottom_fractal']['top']
            fractal = True if closePrice >= top_price else False
        futureCalcObj = await combineIndicator(direction, above_ma5, above_ma20, not_lower, not_higher, fractal, futureCalcObj)
        await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)

    if len(result['sell_zs_huila']['date']) > 0:
        fire_time = result['sell_zs_huila']['date'][-1]
        price = result['sell_zs_huila']['data'][-1]
        tag = result['sell_zs_huila']['tag'][-1]
        above_ma5 = result['sell_zs_huila']['above_ma5'][-1]
        above_ma20 = result['sell_zs_huila']['above_ma20'][-1]
        stop_lose_price = result['sell_zs_huila']['stop_lose_price'][-1]
        futureCalcObj = await calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        direction = 'S'
        fractal = ""
        if result['fractal'][0] != {} and result['fractal'][0]['direction'] == 1:
            # 顶分型的底部
            bottom_price = result['fractal'][0]['top_fractal']['bottom']
            fractal = True if closePrice <= bottom_price else False
        futureCalcObj = await combineIndicator(direction, above_ma5, above_ma20, not_lower, not_higher, fractal, futureCalcObj)
        await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)


'''
监控突破
'''


# 分析走势发现有很多顶部都是用3m 5m 的反向中枢突破套到的,如果突破失败，反手做多 就行了
# 因此突破单不用 notLower notHigher 过滤
async def monitorTupo(result, symbol, period, closePrice):
    signal = 'tupo'
    not_lower = result['notLower']
    not_higher = result['notHigher']
    # 监控突破
    if len(result['buy_zs_tupo']['date']) > 0:
        fire_time = result['buy_zs_tupo']['date'][-1]
        price = result['buy_zs_tupo']['data'][-1]
        stop_lose_price = result['buy_zs_tupo']['stop_lose_price'][-1]
        tag = ''
        above_ma5 = result['buy_zs_tupo']['above_ma5'][-1]
        above_ma20 = result['buy_zs_tupo']['above_ma20'][-1]
        direction = 'B'
        futureCalcObj = await calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        fractal = ""
        # 借助大级别分型信号进行过滤
        if result['fractal'][0] != {} and result['fractal'][0]['direction'] == -1:
            # 底分型的顶部
            top_price = result['fractal'][0]['bottom_fractal']['top']
            fractal = True if closePrice >= top_price else False
        futureCalcObj = await combineIndicator(direction, above_ma5, above_ma20, not_lower, not_higher, fractal, futureCalcObj)
        if above_ma5 or not_lower:
            await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)

    if len(result['sell_zs_tupo']['date']) > 0:
        fire_time = result['sell_zs_tupo']['date'][-1]
        price = result['sell_zs_tupo']['data'][-1]
        stop_lose_price = result['sell_zs_tupo']['stop_lose_price'][-1]
        tag = ''
        above_ma5 = result['sell_zs_tupo']['above_ma5'][-1]
        above_ma20 = result['sell_zs_tupo']['above_ma20'][-1]
        direction = 'S'
        futureCalcObj = await calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        fractal = ""
        if result['fractal'][0] != {} and result['fractal'][0]['direction'] == 1:
            # 顶分型的底部
            bottom_price = result['fractal'][0]['top_fractal']['bottom']
            fractal = True if closePrice <= bottom_price else False
        futureCalcObj = await combineIndicator(direction, above_ma5, above_ma20, not_lower, not_higher, fractal, futureCalcObj)
        if not above_ma5 or not_higher:
            await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)


'''
监控3买卖 V反
'''


async def monitorVReverse(result, symbol, period, closePrice):
    signal = 'v_reverse'
    not_lower = result['notLower']
    not_higher = result['notHigher']
    # 监控V反
    if len(result['buy_v_reverse']['date']) > 0:
        fire_time = result['buy_v_reverse']['date'][-1]
        price = result['buy_v_reverse']['data'][-1]
        stop_lose_price = result['buy_v_reverse']['stop_lose_price'][-1]
        tag = ''
        above_ma5 = result['buy_v_reverse']['above_ma5'][-1]
        above_ma20 = result['buy_v_reverse']['above_ma20'][-1]
        direction = 'B'
        futureCalcObj = await calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        fractal = ""
        # 借助大级别分型信号进行过滤
        if result['fractal'][0] != {} and result['fractal'][0]['direction'] == -1:
            # 底分型的顶部
            top_price = result['fractal'][0]['bottom_fractal']['top']
            fractal = True if closePrice >= top_price else False
        # else 大级别已经向上成笔，说明该级别走势已经完美

        futureCalcObj = await combineIndicator(direction, above_ma5, above_ma20, not_lower, not_higher, fractal, futureCalcObj)
        await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)
    if len(result['sell_v_reverse']['date']) > 0:
        fire_time = result['sell_v_reverse']['date'][-1]
        price = result['sell_v_reverse']['data'][-1]
        stop_lose_price = result['sell_v_reverse']['stop_lose_price'][-1]
        tag = ''
        above_ma5 = result['sell_v_reverse']['above_ma5'][-1]
        above_ma20 = result['sell_v_reverse']['above_ma20'][-1]
        direction = 'S'
        futureCalcObj = await calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        fractal = ""
        if result['fractal'][0] != {} and result['fractal'][0]['direction'] == 1:
            # 顶分型的底部
            bottom_price = result['fractal'][0]['top_fractal']['bottom']
            fractal = True if closePrice <= bottom_price else False
        futureCalcObj = await combineIndicator(direction, above_ma5, above_ma20, not_lower, not_higher, fractal, futureCalcObj)
        await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)


'''
监控5浪及以上 V反
'''


async def monitorFiveVReverse(result, symbol, period, closePrice):
    signal = 'five_v_reverse'
    not_lower = result['notLower']
    not_higher = result['notHigher']
    if len(result['buy_five_v_reverse']['date']) > 0:
        fire_time = result['buy_five_v_reverse']['date'][-1]
        price = result['buy_five_v_reverse']['data'][-1]
        stop_lose_price = result['buy_five_v_reverse']['stop_lose_price'][-1]
        tag = ''
        above_ma5 = result['buy_five_v_reverse']['above_ma5'][-1]
        above_ma20 = result['buy_five_v_reverse']['above_ma20'][-1]
        direction = 'B'
        futureCalcObj = await calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        fractal = ""
        # 借助大级别分型信号进行过滤
        if result['fractal'][0] != {} and result['fractal'][0]['direction'] == -1:
            # 底分型的顶部
            top_price = result['fractal'][0]['bottom_fractal']['top']
            fractal = True if closePrice >= top_price else False
        futureCalcObj = await combineIndicator(direction, above_ma5, above_ma20, not_lower, not_higher, fractal, futureCalcObj)
        await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)
    if len(result['sell_five_v_reverse']['date']) > 0:
        fire_time = result['sell_five_v_reverse']['date'][-1]
        price = result['sell_five_v_reverse']['data'][-1]
        stop_lose_price = result['sell_five_v_reverse']['stop_lose_price'][-1]
        tag = ''
        above_ma5 = result['sell_five_v_reverse']['above_ma5'][-1]
        above_ma20 = result['sell_five_v_reverse']['above_ma20'][-1]
        direction = 'S'
        futureCalcObj = await calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        fractal = ""
        if result['fractal'][0] != {} and result['fractal'][0]['direction'] == 1:
            # 顶分型的底部
            bottom_price = result['fractal'][0]['top_fractal']['bottom']
            fractal = True if closePrice <= bottom_price else False

        futureCalcObj = await combineIndicator(direction, above_ma5, above_ma20, not_lower, not_higher, fractal, futureCalcObj)
        await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)


'''
监控 线段破坏
'''


async def monitorDuanBreak(result, symbol, period, closePrice):
    signal = 'break'
    not_lower = result['notLower']
    not_higher = result['notHigher']
    # 监控线段破坏
    if len(result['buy_duan_break']['date']) > 0:
        fire_time = result['buy_duan_break']['date'][-1]
        price = result['buy_duan_break']['data'][-1]
        stop_lose_price = result['buy_duan_break']['stop_lose_price'][-1]
        tag = ''
        above_ma5 = result['buy_duan_break']['above_ma5'][-1]
        above_ma20 = result['buy_duan_break']['above_ma20'][-1]
        direction = 'B'
        futureCalcObj = await calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        fractal = ""
        # 借助大级别分型信号进行过滤
        if result['fractal'][0] != {} and result['fractal'][0]['direction'] == -1:
            # 底分型的顶部
            top_price = result['fractal'][0]['bottom_fractal']['top']
            fractal = True if closePrice >= top_price else False
        futureCalcObj = await combineIndicator(direction, above_ma5, above_ma20, not_lower, not_higher, fractal, futureCalcObj)
        await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)
    if len(result['sell_duan_break']['date']) > 0:
        fire_time = result['sell_duan_break']['date'][-1]
        price = result['sell_duan_break']['data'][-1]
        stop_lose_price = result['sell_duan_break']['stop_lose_price'][-1]
        tag = ''
        above_ma5 = result['sell_duan_break']['above_ma5'][-1]
        above_ma20 = result['sell_duan_break']['above_ma20'][-1]
        direction = 'S'
        futureCalcObj = await calMaxOrderCount(symbol, price, stop_lose_price, period, signal)
        fractal = ""
        if result['fractal'][0] != {} and result['fractal'][0]['direction'] == 1:
            # 顶分型的底部
            bottom_price = result['fractal'][0]['top_fractal']['bottom']
            fractal = True if closePrice <= bottom_price else False
        futureCalcObj = await combineIndicator(direction, above_ma5, above_ma20, not_lower, not_higher, fractal, futureCalcObj)
        await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)


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

'''
计算分型止损率的时候不能 使用 close_price 因为监控性能的问题 扫描到信号的时候
close_price 和触发价格 price 已经相差很多，此时计算的止损率会偏高 导致被信号过滤器给过滤掉
'''


async def monitorFractal(result, symbol, period, closePrice):
    # 将当前级别的的方向插入到数据库，用于前端展示当前级别的状态
    # 15m向上成笔，代表3F级别多， 15m向下成笔，代表3F级别空
    if result['fractal'][0] != {}:
        levelDirection = result['fractal'][0]['direction']
        if levelDirection == 1:
            await saveFutureDirection(symbol, period, '多')
        else:
            await saveFutureDirection(symbol, period, '空')
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
            futureCalcObj = await calMaxOrderCount(symbol, price, top_price, period, signal)
            futureCalcObj['not_lower'] = ""
            futureCalcObj['not_higher'] = ""
            # 当前价格低于顶分型的底
            if closePrice <= price:
                stopWinCount = await calStopWinCount(symbol, period, positionInfoLong, closePrice)

                if stopWinCount == 0:
                    print(symbol, period, "动止手数为0")
                    return
                # 保存动止手数
                futureCalcObj['stop_win_count'] = stopWinCount
                # 保存动止时的价格
                futureCalcObj['stop_win_price'] = closePrice
                # 保存分型的价格
                futureCalcObj['fractal_price'] = price

                await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)
        # 高高级别
        if result['fractal'][1] != {} and result['fractal'][1]['direction'] == 1:
            fire_time = result['fractal'][1]['top_fractal']['date']
            price = result['fractal'][1]['top_fractal']['bottom']
            stop_lose_price = result['fractal'][1]['top_fractal']['top']
            tag = result['fractal'][1]['period']
            direction = 'HS'
            # 顶分型的顶
            top_price = result['fractal'][1]['top_fractal']['top']
            futureCalcObj = await calMaxOrderCount(symbol, price, top_price, period, signal)
            futureCalcObj['not_lower'] = ""
            futureCalcObj['not_higher'] = ""
            # 当前价格低于顶分型的底
            if closePrice <= price:
                stopWinCount = await calStopWinCount(symbol, period, positionInfoLong, closePrice)
                if stopWinCount == 0:
                    print(symbol, period, "动止手数为0")
                    return
                # 保存动止手数
                futureCalcObj['stop_win_count'] = stopWinCount
                # 保存动止时的价格
                futureCalcObj['stop_win_price'] = closePrice
                # 保存分型的价格
                futureCalcObj['fractal_price'] = price
                await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)
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
            futureCalcObj = await calMaxOrderCount(symbol, price, bottom_price, period, signal)
            futureCalcObj['not_lower'] = ""
            futureCalcObj['not_higher'] = ""
            # 当前价格高于底分型的顶
            if closePrice >= price:
                stopWinCount = await calStopWinCount(symbol, period, positionInfoShort, closePrice)
                if stopWinCount == 0:
                    print(symbol, period, "动止手数为0")
                    return
                # 保存动止手数
                futureCalcObj['stop_win_count'] = stopWinCount
                # 保存动止时的价格
                futureCalcObj['stop_win_price'] = closePrice
                # 保存分型的价格
                futureCalcObj['fractal_price'] = price
                await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)
        # 高高级别
        if result['fractal'][1] != {} and result['fractal'][1]['direction'] == -1:
            fire_time = result['fractal'][1]['bottom_fractal']['date']
            price = result['fractal'][1]['bottom_fractal']['top']
            stop_lose_price = result['fractal'][1]['bottom_fractal']['bottom']
            tag = result['fractal'][1]['period']
            direction = 'HB'
            # 底分型的底部
            bottom_price = result['fractal'][1]['bottom_fractal']['bottom']
            futureCalcObj = await calMaxOrderCount(symbol, price, bottom_price, period, signal)
            futureCalcObj['not_lower'] = ""
            futureCalcObj['not_higher'] = ""
            # 当前价格高于底分型的顶
            if closePrice >= price:
                stopWinCount = await calStopWinCount(symbol, period, positionInfoShort, closePrice)
                if stopWinCount == 0:
                    print(symbol, period, "动止手数为0")
                    return
                # 保存动止手数
                futureCalcObj['stop_win_count'] = stopWinCount
                # 保存动止时的价格
                futureCalcObj['stop_win_price'] = closePrice
                # 保存分型的价格
                futureCalcObj['fractal_price'] = price
                await saveFutureSignal(symbol, period, fire_time, direction, signal, tag, price, closePrice, stop_lose_price, futureCalcObj)


# 计算出开仓手数（止损系数，资金使用率双控）
# 返回最大开仓手数，1手止损的金额，1手止损的百分比
async def calMaxOrderCount(dominantSymbol, openPrice, stopPrice, period, signal):
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
        margin_rate = dominant_symbol_info_list[dominantSymbol]['margin_rate']
        contract_multiplier = dominant_symbol_info_list[dominantSymbol]['contract_multiplier']
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
async def calStopWinCount(symbol, period, positionInfo, closePrice):
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
    # 避免出现动止手数为0的情况
    stopWinCount = math.ceil(stopWinPosRate * open_pos_amount)
    print(symbol, period, "当前盈亏比", winLoseRate, "当前动止仓位百分比",
          stopWinPosRate, "动止手数", stopWinCount, "持仓信息：", positionInfo)
    return stopWinCount


def run(**kwargs):
    global dominant_symbol_info_list
    is_loop = kwargs.get("loop")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    symbol_list, dominant_symbol_info_list = getDominantSymbol()

    logger.info("监控标的数量: {}".format(len(symbol_list)))

    stop_watch = Stopwatch("总监控耗时")

    length = len(symbol_list)
    maxsize = 100 if length > 100 else length

    q = queue.Queue(length)
    for i in range(length):
        q.put(symbol_list[i])

    def worker():
        while is_run:
            symbol_item = q.get()
            monitor_futures_and_digitcoin([symbol_item], ['1m', '3m', '5m', '15m'])
            q.task_done()

    def dispatcher():
        while is_run:
            for j in range(len(symbol_list)):
                q.put(symbol_list[j])

    if is_loop:
        t = threading.Thread(target=dispatcher)
        t.setDaemon(True)
        t.start()
    for i in range(maxsize):
        t = threading.Thread(target=worker)
        t.setDaemon(True)
        t.start()

    if is_loop:
        while is_run:
            time.sleep(3)

    q.join()

    stop_watch.stop()
    logger.info(stop_watch)


if __name__ == '__main__':
    run(**{"loop": True})
