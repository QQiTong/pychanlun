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

tz = pytz.timezone('Asia/Shanghai')
'''
综合监控
'''
klineDataTool = KlineDataTool()
# 米筐数据 主力连续合约RB88 这个会比实时数据少一天
symbolListDigitCoin = ['BTC_CQ'
                       # 'ETH_CQ', 'BCH_CQ', 'LTC_CQ', 'BSV_CQ'
                       ]
periodList1 = ['3m', '5m', '15m', '30m', '60m']
periodList2 = ['1m', '3m', '5m', '15m', '30m', '60m']
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
# 账户资金
account = 19
# 期货公司在原有保证金基础上1%
marginLevelCompany = 0.01
# 期货账户
futuresAccount = 19
# 数字货币手续费20倍杠杆
digitCoinFee = 0.0006
# 数字货币账户
digitCoinAccount = 1
maxAccountUseRate = 0.1
stopRate = 0.01
mail = Mail()
# 初始化业务对象
# businessService = BusinessService()


def sendEmail(msg):
    print(msg)
    mailResult = mail.send(json.dumps(msg, ensure_ascii=False, indent=4))
    if not mailResult:
        print("发送失败")
    else:
        print("发送成功")


# price 信号触发的价格， close_price 提醒时的收盘价 direction 多B 空S amount 开仓数量
def saveFutureSignal(symbol, period, fire_time_str, direction, signal, remark, price, close_price, amount,stop_lose_price):
    temp_fire_time = datetime.strptime(fire_time_str, "%Y-%m-%d %H:%M")
    # 触发时间转换成UTC时间
    fire_time = temp_fire_time - timedelta(hours=8)
    last_fire = DBPyChanlun['future_signal'].find_one({
        'symbol': symbol,
        'period': period,
        'fire_time': fire_time,
        'direction': direction
    })
    if last_fire is not None:
        DBPyChanlun['future_signal'].find_one_and_update({
            'symbol': symbol, 'period': period, 'fire_time': fire_time, 'direction': direction
        }, {
            '$set': {
                'signal': signal,
                'remark': remark,
                'price': price,
                'close_price': close_price,
                'amount': amount,
                'date_created': datetime.utcnow(),
                'stop_lose_price':stop_lose_price
            },
            '$inc': {
                'update_count': 1
            }
        }, upsert=True)
    else:
        date_created = datetime.utcnow()
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
            'stop_lose_price': stop_lose_price, # 当前信号的止损价
            'update_count': 1,  # 这条背驰记录的更新次数
        })
        if (date_created - fire_time).total_seconds() < 600:
            # 在10分钟内的触发邮件通知
            # 把数据库的utc时间 转成本地时间
            fire_time_str = (fire_time + timedelta(hours=8)).strftime('%m-%d %H:%M:%S'),
            date_created_str = (date_created + timedelta(hours=8)).strftime('%m-%d %H:%M:%S'),
            # msg = {
            #     "symbol": symbol,
            #     "period": period,
            #     "signal": signal,
            #     "direction": direction,
            #     "amount": amount,
            #     "fire_time": fire_time_str,
            #     "price": price,
            #     "date_created": date_created_str,
            #     "close_price": close_price,
            #     "remark": remark,
            # }
            # 简洁版
            msg = "%s %s %s %s %s %s %s %s %s %s %s" % (symbol,period,signal,direction,amount,stop_lose_price,fire_time_str,price,date_created_str,close_price,remark)
            sendEmail(msg)

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
                'direction':direction
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
def monitorFuturesAndDigitCoin(type):
    logger = logging.getLogger()
    # 扫一遍25个期货品种需要3.5分钟
    if type == "1":
        # auth('13088887055', 'chanlun123456')
        # count = get_query_count()
        # print(count)
        init('license',
             'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
             ('rqdatad-pro.ricequant.com', 16011))
        # 主力合约，主力合约详细信息
        symbolList, dominantSymbolInfoList = getDominantSymbol()
        # print("主力合约信息：", dominantSymbolInfoList)
        periodList = periodList1
        account = futuresAccount
    else:
        symbolList = symbolListDigitCoin
        periodList = periodList2
        account = digitCoinAccount

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
                    monitorHuila(result, symbol, period, close_price)
                    monitorTupo(result, symbol, period, close_price)
                    monitorVfan(result, symbol, period, close_price)
                    monitorDuanBreak(result, symbol, period, close_price)
                    monitorFractal(result, symbol, period, close_price)
            if type == "1":
                time.sleep(0)
            else:
                time.sleep(5)
    except Exception:
        logger.info("Error Occurred: {0}".format(traceback.format_exc()))
        print("Error Occurred: {0}".format(traceback.format_exc()))
        if type == "1":
            print("期货出异常了", Exception)

            # threading.Thread(
            #     target=monitorFuturesAndDigitCoin, args="1").start()
        else:
            print("火币出异常了", Exception)
            time.sleep(5)
            threading.Thread(
                target=monitorFuturesAndDigitCoin, args="2").start()


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
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        direction = 'B'
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)
    if len(result['sell_zs_huila']['date']) > 0:
        fire_time = result['sell_zs_huila']['date'][-1]
        price = result['sell_zs_huila']['data'][-1]
        remark = result['sell_zs_huila']['tag'][-1]
        stop_lose_price = result['sell_zs_huila']['stop_lose_price'][-1]
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        direction = 'S'
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)
    # 监控高级别回拉
    if len(result['buy_zs_huila_higher']['date']) > 0:
        fire_time = result['buy_zs_huila_higher']['date'][-1]
        price = result['buy_zs_huila_higher']['data'][-1]
        remark = result['buy_zs_huila_higher']['tag'][-1]
        stop_lose_price = result['buy_zs_huila_higher']['stop_lose_price'][-1]
        direction = 'HB'
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)
    if len(result['sell_zs_huila_higher']['date']) > 0:
        fire_time = result['sell_zs_huila_higher']['date'][-1]
        price = result['sell_zs_huila_higher']['data'][-1]
        remark = result['sell_zs_huila_higher']['tag'][-1]
        stop_lose_price = result['sell_zs_huila_higher']['stop_lose_price'][-1]
        direction = 'HS'
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)


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
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)
    if len(result['sell_zs_tupo']['date']) > 0:
        fire_time = result['sell_zs_tupo']['date'][-1]
        price = result['sell_zs_tupo']['data'][-1]
        stop_lose_price = result['sell_zs_tupo']['stop_lose_price'][-1]
        remark = ''
        direction = 'S'
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)
    # 监控高级别突破
    if len(result['buy_zs_tupo_higher']['date']) > 0:
        fire_time = result['buy_zs_tupo_higher']['date'][-1]
        price = result['buy_zs_tupo_higher']['data'][-1]
        stop_lose_price = result['buy_zs_tupo_higher']['stop_lose_price'][-1]
        remark = ''
        direction = 'HB'
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)
    if len(result['sell_zs_tupo_higher']['date']) > 0:
        fire_time = result['sell_zs_tupo_higher']['date'][-1]
        price = result['sell_zs_tupo_higher']['data'][-1]
        stop_lose_price = result['sell_zs_tupo_higher']['stop_lose_price'][-1]
        remark = ''
        direction = 'HS'
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)


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
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)
    if len(result['sell_v_reverse']['date']) > 0:
        fire_time = result['sell_v_reverse']['date'][-1]
        price = result['sell_v_reverse']['data'][-1]
        stop_lose_price = result['sell_v_reverse']['stop_lose_price'][-1]
        remark = ''
        direction = 'S'
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)
    # 监控高级别V反
    if len(result['buy_v_reverse_higher']['date']) > 0:
        fire_time = result['buy_v_reverse_higher']['date'][-1]
        price = result['buy_v_reverse_higher']['data'][-1]
        stop_lose_price = result['buy_v_reverse_higher']['stop_lose_price'][-1]
        remark = ''
        direction = 'HB'
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)

    if len(result['sell_v_reverse_higher']['date']) > 0:
        fire_time = result['sell_v_reverse_higher']['date'][-1]
        price = result['sell_v_reverse_higher']['data'][-1]
        stop_lose_price = result['sell_v_reverse_higher']['stop_lose_price'][-1]
        remark = ''
        direction = 'HS'
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)


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
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)
    if len(result['sell_duan_break']['date']) > 0:
        fire_time = result['sell_duan_break']['date'][-1]
        price = result['sell_duan_break']['data'][-1]
        stop_lose_price = result['sell_duan_break']['stop_lose_price'][-1]
        remark = ''
        direction = 'S'
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)
    # 监控高级别线段破坏
    if len(result['buy_duan_break_higher']['date']) > 0:
        fire_time = result['buy_duan_break_higher']['date'][-1]
        price = result['buy_duan_break_higher']['data'][-1]
        stop_lose_price = result['buy_duan_break_higher']['stop_lose_price'][-1]
        remark = ''
        direction = 'HB'
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)

    if len(result['sell_duan_break_higher']['date']) > 0:
        fire_time = result['sell_duan_break_higher']['date'][-1]
        price = result['sell_duan_break_higher']['data'][-1]
        stop_lose_price = result['sell_duan_break_higher']['stop_lose_price'][-1]
        remark = ''
        direction = 'HS'
        maxOrderCount = calMaxOrderCount(symbol, closePrice, stop_lose_price,period)
        saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, maxOrderCount,stop_lose_price)


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
        saveFutureDirection(symbol,period,'多')
    else:
        saveFutureDirection(symbol,period,'空')
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
                saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stopWinCount,stop_lose_price)
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
                saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stopWinCount,stop_lose_price)
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
                saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stopWinCount,stop_lose_price)
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
                saveFutureSignal(symbol, period, fire_time, direction, signal, remark, price, closePrice, stopWinCount,stop_lose_price)


# 计算出开仓手数（止损系数，资金使用率双控）
def calMaxOrderCount(dominantSymbol, openPrice, stopPrice,period):
    # openPrice stopPrice等于历史行情某个stopPrice 会导致除0异常
    if openPrice == stopPrice:
        return -1
    # 兼容数字货币
    if '_CQ' in dominantSymbol:
        perOrderMargin = 5
        # 1手止损的比率
        perOrderStopRate = (abs(openPrice - stopPrice) / openPrice + digitCoinFee) * 20
        # 1手止损的金额
        perOrderStopMoney = round((perOrderMargin * perOrderStopRate), 2)
    # 期货
    else:
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
    return maxOrderCount


# 计算动止手数（盈亏比大于2.3：1 动止30%才能保证不亏）
# 主力合约，开仓价格，开仓数量，止损价格，止盈价格    用最新价来算回更准确，因为触发价可能会有滑点
def calStopWinCount(symbol, period, positionInfo, closePrice):
    if '_CQ' in symbol:
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
    threading.Thread(target=monitorFuturesAndDigitCoin, args="1").start()
    # threading.Thread(target=monitorFuturesAndDigitCoin, args="2").start()
