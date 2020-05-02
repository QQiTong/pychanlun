# -*- coding: utf-8 -*-

import rqdatac as rq
import os
import json
from pychanlun.config import config, cfg
from datetime import datetime, timedelta
from pychanlun.db import DBPyChanlun
from bson.codec_options import CodecOptions
import pytz
import pymongo
import pandas as pd
from bson import ObjectId
import time
import requests
import copy
import string

tz = pytz.timezone('Asia/Shanghai')

# periodList = ['3min', '5min', '15min', '30min', '60min', '4hour', '1day']
periodList = ['3m', '5m', '15m', '30m', '60m']
# 主力合约列表
dominantSymbolList = []
# 主力合约详细信息
dominantSymbolInfoList = []
# CL:原油; GC:黄金;SI:白银; CT:棉花;S:大豆;SM：豆粕; BO:豆油;NID:伦镍; ZSD:伦锌;
# 马棕 日胶
global_future_symbol = config['global_future_symbol']
global_stock_symbol = config['global_stock_symbol']
digit_coin_symbol = config['digit_coin_symbol']
hbSwapUrl = "http://api.btcgateway.pro/swap-ex/market/history/kline?contract_code=BTC-USD"
hbSwapTickUrl = "http://api.btcgateway.pro/swap-ex/market/trade?contract_code=BTC-USD"


class BusinessService:
    def __init__(self):
        print('初始化业务对象...')

    # okex数字货币部分涨跌幅
    def getBTCTicker(self):
        okexUrl = "https://www.okex.me/api/swap/v3/instruments/BTC-USDT-SWAP/ticker"
        r = requests.get(okexUrl, timeout=(15, 15))
        ticker = json.loads(r.text)
        # print("BTC实时价格",ticker)
        okexUrl2 = "https://www.okex.me/api/swap/v3/instruments/BTC-USDT-SWAP/candles?granularity=86400"
        r = requests.get(okexUrl2, timeout=(15, 15))
        data_list = json.loads(r.text)
        dayOpenPrice = data_list[0][1]
        change = round((float(ticker['last']) - float(dayOpenPrice)) / float(dayOpenPrice), 4)
        changeAndPrice = {
            'change': change,
            'price': ticker['last']
        }
        return changeAndPrice

    def getStatisticList(self, dateRange):
        statisticList = {}
        split = dateRange.split(",")
        startDate = split[0]
        endDate = split[1]
        print("dateRange", split)
        # test
        # startDate = '2020-03-29'
        # endDate = '2020-03-31'
        end = datetime.strptime(endDate, "%Y-%m-%d")
        end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
        start = datetime.strptime(startDate, "%Y-%m-%d")
        start = start.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
        data_list = DBPyChanlun['future_auto_position'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({
            "date_created": {"$gte": start, "$lte": end}
        }).sort("_id", pymongo.ASCENDING)
        df = pd.DataFrame(list(data_list))
        # 当持仓表中没有 单子止盈过的的时候 win_end_money字段为空
        if len(df) == 0 or 'win_end_money' not in df.columns.values or 'lose_end_money' not in df.columns.values:
            return {
                'date': [],
                'win_end_list': [],
                'lose_end_list': [],
                'net_profit_list': [],
                'win_money_list': [],
                'lose_money_list': [],
                'win_symbol_list': [],
                'lose_symbol_list': []
        }

        for idx, row in df.iterrows():
            # 根据日期分组
            date_created = df.loc[idx, 'date_created']
            date_created_str = self.formatTime2(date_created)
            df.loc[idx, 'new_date_created'] = date_created_str
            # 根据symbol分组 查询盈利品种排行和亏损品种排行
            symbol = df.loc[idx, 'symbol']
            # RB2010 -> RB
            simple_symbol = symbol.rstrip(string.digits)
            df.loc[idx, 'simple_symbol'] = simple_symbol

        win_end_group_by_date = df['win_end_money'].groupby(df['new_date_created'])
        lose_end_group_by_date = df['lose_end_money'].groupby(df['new_date_created'])
        win_end_group_by_symbol = df['win_end_money'].groupby(df['simple_symbol'])
        lose_end_group_by_symbol = df['lose_end_money'].groupby(df['simple_symbol'])
        # print(win_end_group_by_symbol.sum())
        # print(lose_end_group_by_symbol.sum())

        # print(win_end_group_by_date.sum())
        # print(lose_end_group_by_date.sum())
        # 日期列表
        dateList = []
        # 当日盈利累加
        win_end_list = []
        # 每天亏损累加
        lose_end_list = []
        # 净盈亏
        net_profit_list = []
        # 保存日期
        for name, group in win_end_group_by_date:
            dateList.append(name)
        # 保存品种简称

        for i in range(len(win_end_group_by_date.sum())):
            win_end_list.append(int(win_end_group_by_date.sum()[i]))
            lose_end_list.append(int(lose_end_group_by_date.sum()[i]))
            net_profit_list.append(int(win_end_group_by_date.sum()[i]) + int(lose_end_group_by_date.sum()[i]))

        sorted_win_money_list = win_end_group_by_symbol.mean().sort_values(ascending=False)
        sorted_lose_money_list = lose_end_group_by_symbol.mean().sort_values(ascending=True)

        win_symbol_list = list(sorted_win_money_list.index)
        lose_symbol_list = list(sorted_lose_money_list.index)

        # 取整数
        win_money_list = list(sorted_win_money_list.dropna(axis=0))
        lose_money_list = list(sorted_lose_money_list.dropna(axis=0))
        for i in range(len(win_money_list)):
            win_money_list[i] = int(win_money_list[i])
        for i in range(len(lose_money_list)):
            lose_money_list[i] = int(lose_money_list[i])

        # print(win_symbol_list, win_money_list)
        # print(lose_symbol_list, lose_money_list)

        # print(win_symbol_list, win_money_list)
        # print(lose_symbol_list, lose_money_list)
        statisticList = {
            'date': dateList,
            'win_end_list': win_end_list,
            'lose_end_list': lose_end_list,
            'net_profit_list': net_profit_list,
            'win_money_list': win_money_list,
            'lose_money_list': lose_money_list,
            'win_symbol_list': win_symbol_list,
            'lose_symbol_list': lose_symbol_list
        }
        return statisticList

    # okex数字货币部分涨跌幅
    # def getBTCTicker(self):
    #     dayParam = {
    #         'symbol': 'BTC-USD',  # 合约类型， 火币季度合约
    #         'period': '1day',
    #         'size': 1
    #     }
    #
    #     r = requests.get(hbSwapUrl,params=dayParam, timeout=(15, 15))
    #     daykline = json.loads(r.text)
    #
    #     dayOpenPrice = daykline['data'][-1]['open']
    #
    #     r = requests.get(hbSwapTickUrl, timeout=(15, 15))
    #     minKline = json.loads(r.text)
    #     minClosePrice = minKline['tick']['data'][-1]['price']
    #     change = round((float(minClosePrice) - dayOpenPrice) / dayOpenPrice,4)
    #     changeAndPrice = {
    #         'change':change,
    #         'price':minClosePrice
    #     }
    #     return changeAndPrice

    def getGlobalFutureChangeList(self):
        global_future_symbol = config['global_future_symbol']
        # global_stock_symbol = config['global_stock_symbol']
        combinSymbol = copy.deepcopy(global_future_symbol)
        # combinSymbol.extend(global_stock_symbol)
        changeList = {}
        for i in range(len(combinSymbol)):
            item = combinSymbol[i]
            # 查日线开盘价
            code = "%s_%s" % (item, '1d')
            data_list = list(DBPyChanlun[code].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find(
            ).sort("_id", pymongo.DESCENDING))
            if len(data_list) == 0:
                continue
            dayOpenPrice = data_list[0]['open']
            code = "%s_%s" % (item, '5m')

            # 差5分钟收盘价
            data_list = list(DBPyChanlun[code].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find(
            ).sort("_id", pymongo.DESCENDING))
            if len(data_list) == 0:
                continue
            minClosePrice = data_list[0]['open']

            change = round((minClosePrice - dayOpenPrice) / dayOpenPrice, 4)
            changeItem = {
                'change': change,
                'price': minClosePrice
            }
            # print(item, '-> ', dayOpenPrice, ' -> ', minClosePrice)
            changeList[item] = changeItem
        return changeList

    def initDoinantSynmbol(self):
        symbolList = config['symbolList']
        # 主力合约详细信息
        for i in range(len(symbolList)):
            df = rq.futures.get_dominant(
                symbolList[i], start_date=None, end_date=None, rule=0)
            dominantSymbol = df[-1]
            dominantSymbolList.append(dominantSymbol)
            dominantSymbolInfo = rq.instruments(dominantSymbol)
            dominantSymbolInfoList.append(dominantSymbolInfo.__dict__)
        # print("当前主力合约列表:", dominantSymbolList)
        # print("当前主力合约详细信息:", dominantSymbolInfoList)

    def getDoinantSynmbol(self):
        conbinSymbolInfo = copy.deepcopy(dominantSymbolInfoList)
        #  把外盘 数字货币加进去
        conbinSymbolInfo.extend(config['global_future_symbol_info'])
        conbinSymbolInfo.extend(config['digit_coin_symbol_info'])
        return conbinSymbolInfo

    def getFutureSignalList(self, strategyType):
        if strategyType == "0":
            return self.getNormalSignalList()
        elif strategyType == "3":
            return self.getStrategy3BeichiList()
        else:
            return self.getStrategy4BeichiList()

    def getNormalSignalList(self):
        symbolList = copy.deepcopy(dominantSymbolList)
        #  把外盘加进去
        symbolList.extend(global_future_symbol)
        # symbolList.extend(global_stock_symbol)
        symbolList.extend(digit_coin_symbol)
        symbolListMap = {}
        for i in range(len(symbolList)):
            symbol = symbolList[i]
            symbolListMap[symbol] = {}
            for j in range(len(periodList)):
                period = periodList[j]
                symbolListMap[symbol][period] = ""
        future_signal_list = DBPyChanlun['future_signal'].find().sort(
            "fire_time", pymongo.ASCENDING)
        for signalItem in future_signal_list:
            # print("信号item:", signalItem)
            # utc 转本地时间
            date_created = signalItem['date_created'] + timedelta(hours=8)
            date_created_str = date_created.strftime("%m-%d %H:%M")
            fire_time = signalItem['fire_time'] + timedelta(hours=8)
            fire_time_str = fire_time.strftime("%m-%d %H:%M")
            # str(round(signalItem['price'], 2))
            if 'level_direction' in signalItem:
                level_direction = signalItem['level_direction']
            else:
                level_direction = ""
            msg = "%s %s %s %s %s" % (level_direction,str(signalItem['signal']), str(signalItem['direction']), fire_time_str,
                                   str(signalItem.get('tag', '')))
            if signalItem['symbol'] in symbolListMap:
                symbolListMap[signalItem['symbol']][signalItem['period']] = msg
        # print("期货信号列表", symbolListMap)
        return symbolListMap

    def getStrategy3BeichiList(self):
        symbolList = copy.deepcopy(dominantSymbolList)

        #  把外盘加进去
        symbolList.extend(global_future_symbol)
        # symbolList.extend(global_stock_symbol)
        symbolList.extend(digit_coin_symbol)
        symbolListMap = {}
        for i in range(len(symbolList)):
            symbol = symbolList[i]
            symbolListMap[symbol] = {}

            for j in range(len(periodList)):
                period = periodList[j]
                symbolListMap[symbol][period] = ""
        beichi_log_list = DBPyChanlun['strategy3_log'].find()
        for beichiItem in beichi_log_list:
            msg = beichiItem['tag'], str(
                round(beichiItem['price'], 2)), str(beichiItem['date_created'])
            if beichiItem['symbol'] in symbolListMap:
                symbolListMap[beichiItem['symbol']][beichiItem['period']] = msg
        # print("背驰列表", symbolListMap)
        return symbolListMap

    def getStrategy4BeichiList(self):
        symbolList = copy.deepcopy(dominantSymbolList)
        #  把外盘加进去
        symbolList.extend(global_future_symbol)
        # symbolList.extend(global_stock_symbol)
        symbolList.extend(digit_coin_symbol)
        symbolListMap = {}
        for i in range(len(symbolList)):
            symbol = symbolList[i]
            symbolListMap[symbol] = {}
            for j in range(len(periodList)):
                period = periodList[j]
                symbolListMap[symbol][period] = ""
        beichi_log_list = DBPyChanlun['strategy4_log'].find()
        for beichiItem in beichi_log_list:
            msg = beichiItem['tag'], str(
                round(beichiItem['price'], 2)), str(beichiItem['date_created'])
            if beichiItem['symbol'] in symbolListMap:
                symbolListMap[beichiItem['symbol']][beichiItem['period']] = msg
        # print("背驰列表", symbolListMap)
        return symbolListMap

    # 获取涨跌幅数据
    def getChangeList(self):
        symbolChangeMap = {}
        end = datetime.now() + timedelta(1)
        # 周日weekday 6 取前2天 周一 weekday 0 取前3天
        weekday = datetime.now().weekday()
        if weekday == 0:
            start = datetime.now() + timedelta(-3)
        elif weekday == 6:
            start = datetime.now() + timedelta(-2)
        else:
            start = datetime.now() + timedelta(-1)
        for i in range(len(dominantSymbolList)):
            item = dominantSymbolList[i]
            # print(item)
            df1d = rq.get_price(item, frequency='1d', fields=['open', 'high', 'low', 'close', 'volume'],
                                start_date=start, end_date=end)
            if df1d is None:
                continue
            df1m = rq.current_minute(item)
            preday = df1d.iloc[0, 3]
            today = df1m.iloc[0, 0]
            if df1d is None or df1m is None:
                change = "--"
            else:
                change = round(((today - preday) / preday), 4)
                # print(preday, today, change)
            resultItem = {'change': change, 'price': today}
            symbolChangeMap[item] = resultItem
        # print("涨跌幅信息", symbolChangeMap)
        globalChangeList = self.getGlobalFutureChangeList()
        conbineChangeList = dict(symbolChangeMap, **globalChangeList)
        return conbineChangeList

    def getLevelDirectionList(self):
        symbolList = copy.deepcopy(dominantSymbolList)
        #  把外盘加进去
        symbolList.extend(global_future_symbol)
        # symbolList.extend(global_stock_symbol)
        symbolList.extend(digit_coin_symbol)
        symbolListMap = {}
        for i in range(len(symbolList)):
            symbol = symbolList[i]
            symbolListMap[symbol] = {}
            for j in range(len(periodList)):
                period = periodList[j]
                symbolListMap[symbol][period] = ""
        future_direction_list = DBPyChanlun['future_direction'].find()
        for directionItem in future_direction_list:
            # utc 转本地时间
            # date_created = directionItem['date_created'] + timedelta(hours=8)
            # date_created_str = date_created.strftime("%m-%d %H:%M")
            if directionItem['symbol'] in symbolListMap:
                symbolListMap[directionItem['symbol']
                ][directionItem['period']] = directionItem['direction']
        # print("级别多空列表", symbolListMap)
        return symbolListMap

    # --------------------期货部份----------------------------------------------
    # 为了兼容老合约 保证金率不再从主力合约中取了， 直接拿配置信息
    def getFutureConfig(self):
        return config['futureConfig']

    def getPosition(self, symbol, period, status,direction):
        if period == 'all':
            query = {'symbol': symbol, 'status': status,'direction':direction}
        else:
            query = {'symbol': symbol, 'period': period, 'status': status,'direction':direction}
        # 当多空双开锁仓的时候，获取最新持仓的那个
        result = DBPyChanlun["future_auto_position"].find(
            query).sort("fire_time", pymongo.ASCENDING)
        if result.count() > 0:
            for x in result:
                x['_id'] = str(x['_id'])
                x['fire_time'] = self.formatTime(x['fire_time'])
                x['date_created'] = self.formatTime(x['date_created'])
                if ('last_update_time' in x and x['last_update_time'] != ''):
                    x['last_update_time'] = self.formatTime(x['last_update_time'])
                else:
                    x['last_update_time'] = ''
                if ('win_end_time' in x and x['win_end_time'] != ''):
                    x['win_end_time'] = self.formatTime(x['win_end_time'])
                else:
                    x['win_end_time'] = ''
                if ('lose_end_time' in x and x['lose_end_time'] != ''):
                    x['lose_end_time'] = self.formatTime(x['lose_end_time'])
                else:
                    x['lose_end_time'] = ''

                if 'dynamicPositionList' in x:
                    for y in x['dynamicPositionList']:
                        y['date_created'] = self.formatTime(y['date_created'])

            return x
        else:
            return -1

    def formatTime(self, localTime):
        localTimeStamp = time.localtime(int(time.mktime(localTime.timetuple()) + 8 * 3600))
        localTimeStampStr = time.strftime("%Y-%m-%d %H:%M:%S", localTimeStamp)
        return localTimeStampStr

    def formatTime2(self, localTime):
        date_created_stamp = int(time.mktime(localTime.timetuple()))
        timeArray = time.localtime(date_created_stamp)
        return time.strftime("%Y-%m-%d", timeArray)

    # 持仓列表改成自动录入
    def getPositionList(self, status, page, size, endDate):
        end = datetime.strptime(endDate, "%Y-%m-%d")
        end = end.replace(hour=23, minute=59, second=59, microsecond=999, tzinfo=tz)
        start_date = end + timedelta(-1)
        positionList = []
        collection = DBPyChanlun["future_auto_position"]
        # 查询总记录数
        if status == 'all':
            result = collection.find({'date_created': {"$gte": start_date, "$lte": end}}).skip(
                (page - 1) * size).limit(size).sort("fire_time", pymongo.DESCENDING)
        # 有的单子需要长线拿住，因此持仓单不限制时间
        elif status == 'holding':
            result = collection.find({'status': status}).skip(
                (page - 1) * size).limit(size).sort("fire_time", pymongo.DESCENDING)
        else:
            result = collection.find({'status': status, 'date_created': {"$gte": start_date, "$lte": end}}).skip(
                (page - 1) * size).limit(size).sort("fire_time", pymongo.DESCENDING)
        total = result.count()
        for x in result:
            x['_id'] = str(x['_id'])
            x['fire_time'] = self.formatTime(x['fire_time'])
            x['date_created'] = self.formatTime(x['date_created'])
            if ('last_update_time' in x and x['last_update_time'] != ''):
                x['last_update_time'] = self.formatTime(x['last_update_time'])
            else:
                x['last_update_time'] = ''
            if ('lose_end_time' in x and x['lose_end_time'] != ''):
                x['lose_end_time'] = self.formatTime(x['lose_end_time'])
            else:
                x['lose_end_time'] = ''
            if ('win_end_time' in x and x['win_end_time'] != ''):
                x['win_end_time'] = self.formatTime(x['win_end_time'])
            else:
                x['win_end_time'] = ''
            # 兼容老数据
            if ('total_margin' not in x or x['total_margin'] != ''):
                x['total_margin'] = round(x['per_order_margin'] * x['amount'], 2)


            if 'dynamicPositionList' in x :
                for y in x['dynamicPositionList'] :
                    y['date_created'] = self.formatTime(y['date_created'])

            # 占用保证金
            positionList.append(x)
        positionListResult = {
            'records': positionList,
            'total': total
        }
        return positionListResult

    def createPosition(self, position):
        result = DBPyChanlun['position_record'].insert_one({
            'enterTime': position['enterTime'],
            'symbol': position['symbol'],
            'period': position['period'],
            'signal': position['signal'],
            'status': position['status'],
            'direction': position['direction'],
            'price': position['price'],
            'amount': position['amount'],
            'stopLosePrice': position['stopLosePrice'],
            'margin_rate': position['margin_rate'],
            # 'nestLevel': position['nestLevel'],
            'enterReason': position['enterReason'],
            'holdReason': position['holdReason'],
            # 'importance': position['importance'],
            'dynamicPositionList': position['dynamicPositionList'],
        })
        return result.inserted_id

    def updatePosition(self, position):
        DBPyChanlun['position_record'].update_one({'_id': ObjectId(position['_id'])}, {"$set": {
            'enterTime': position['enterTime'],
            'symbol': position['symbol'],
            'period': position['period'],
            'signal': position['signal'],
            'status': position['status'],
            'direction': position['direction'],
            'price': position['price'],
            'amount': position['amount'],
            'stopLosePrice': position['stopLosePrice'],
            'margin_rate': position['margin_rate'],
            # 'nestLevel': position['nestLevel'],
            'enterReason': position['enterReason'],
            'holdReason': position['holdReason'],
            # 'importance': position['importance'],
            'dynamicPositionList': position['dynamicPositionList']
        }})

    # close_price 最新收盘价 手动进行止盈止损操作
    '''
     status :
      holding 持仓
      loseEnd 止损
      winEnd  止盈
      exception 异常
    '''
    def updatePositionStatus(self, id, status, close_price):
        date_created = datetime.utcnow()
        item = DBPyChanlun['future_auto_position'].find_one({'_id': ObjectId(id)})
        if item['symbol'] is 'BTC':
            marginLevel = 1 / (item['margin_rate'])
        else:
            marginLevel = 1 / (item['margin_rate'] + config['margin_rate_company'])
        if status == 'winEnd':
            winEndPercent = round(((float(close_price) - item['price']) / item['price']) * marginLevel, 2)
            # 止盈已实现盈亏
            win_end_money = round(item['per_order_margin'] * item['amount'] * winEndPercent, 2)
            # 止盈比率
            win_end_rate = round(winEndPercent, 2)
            DBPyChanlun['future_auto_position'].update_one({'_id': ObjectId(id)}, {"$set": {
                'status': status,
                'win_end_price': float(close_price),
                'win_end_money': abs(win_end_money),
                'win_end_rate': abs(win_end_rate),
                'win_end_time': date_created
            }})
        elif status == 'loseEnd':
            loseEndPercent = round(((float(close_price) - item['price']) / item['price']) * marginLevel, 2)
            # 止损已实现盈亏
            lose_end_money = round(item['per_order_margin'] * item['amount'] * loseEndPercent, 2)
            lose_end_rate = round(loseEndPercent, 2)
            DBPyChanlun['future_auto_position'].update_one({'_id': ObjectId(id)}, {"$set": {
                'status': status,
                'lose_end_price': float(close_price),
                'lose_end_money': -abs(lose_end_money),
                'lose_end_rate': -abs(lose_end_rate),
                'lose_end_time': date_created
            }})
        else:
            DBPyChanlun['future_auto_position'].update_one({'_id': ObjectId(id)}, {"$set": {
                'status': status,
            }})

    # 创建预判信息
    def createFuturePrejudgeList(self, endDate, prejudgeList):
        result = DBPyChanlun['prejudge_record'].insert_one({
            'endDate': endDate,
            'prejudgeList': prejudgeList
        })
        return result.inserted_id

    # 获取预判信息
    def getFuturePrejudgeList(self, endDate):
        result = DBPyChanlun['prejudge_record'].find({'endDate': endDate})
        if result.count() != 0:
            for x in result:
                x['_id'] = str(x['_id'])
            return x
        else:
            return -1

    #  更新预判信息
    def updateFuturePrejudgeList(self, id, prejudgeList):
        # print("更新预判参数", id, prejudgeList)
        DBPyChanlun['prejudge_record'].update_one({'_id': ObjectId(id)}, {"$set": {
            'prejudgeList': prejudgeList
        }})

    # --------------------股票部份----------------------------------------------

    def getStockSignalList(self, page=1):
        data_list = DBPyChanlun["stock_signal"].with_options(
            codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find({}).sort(
            "fire_time", pymongo.DESCENDING).skip((page - 1) * 1000).limit(1000)
        df = pd.DataFrame(list(data_list))
        signalList = []
        for idx, row in df.iterrows():
            item = {}
            item['code'] = row["code"]
            item['fire_time'] = row["fire_time"].strftime("%Y-%m-%d %H:%M")
            item['period'] = row["period"]
            item['price'] = row["price"]
            item['stop_lose_price'] = row["stop_lose_price"]
            item['tag'] = row["tag"]
            item['category'] = row["category"]
            item['tags'] = ", ".join(row["tags"])
            signalList.append(item)
        return signalList

    def getStockPositionList(self, status, page, size):
        positionList = []
        collection = DBPyChanlun["stock_position_record"]
        # 查询总记录数
        if status == 'all':
            result = collection.find().skip((page - 1) * size).limit(size).sort("enterTime", pymongo.DESCENDING)
            total = result.count()
        else:
            result = collection.find({'status': status}).skip(
                (page - 1) * size).limit(size).sort("enterTime", pymongo.DESCENDING)
            total = result.count()
        for x in result:
            x['_id'] = str(x['_id'])
            positionList.append(x)
        positionListResult = {
            'records': positionList,
            'total': total
        }
        return positionListResult

    def getStockPosition(self, symbol, period, status):
        if period == 'all':
            query = {'symbol': symbol, 'status': status}
        else:
            query = {'symbol': symbol, 'period': period, 'status': status}
        result = DBPyChanlun["stock_position_record"].find(query)
        if result.count() > 0:
            for x in result:
                x['_id'] = str(x['_id'])
            return x
        else:
            return -1

    # 新增股票持仓
    def createStockPosition(self, position):
        result = DBPyChanlun['stock_position_record'].insert_one({
            'enterTime': position['enterTime'],
            'symbol': position['symbol'],
            'period': position['period'],
            'signal': position['signal'],
            'status': position['status'],
            'direction': position['direction'],
            'positionPercent': position['positionPercent'],
            'price': position['price'],
            'amount': position['amount'],
            'stopLosePrice': position['stopLosePrice'],
            # 'nestLevel': position['nestLevel'],
            'enterReason': position['enterReason'],
            'holdReason': position['holdReason'],
            # 'importance': position['importance'],
            'dynamicPositionList': position['dynamicPositionList'],
        })
        return result.inserted_id

    def updateStockPosition(self, position):
        print("传给后端的positionPercent", position['positionPercent'])
        DBPyChanlun['stock_position_record'].update_one({'_id': ObjectId(position['_id'])}, {"$set": {
            'enterTime': position['enterTime'],
            'symbol': position['symbol'],
            'period': position['period'],
            'signal': position['signal'],
            'status': position['status'],
            'direction': position['direction'],
            'positionPercent': position['positionPercent'],
            'price': position['price'],
            'amount': position['amount'],
            'stopLosePrice': position['stopLosePrice'],
            # 'nestLevel': position['nestLevel'],
            'enterReason': position['enterReason'],
            'holdReason': position['holdReason'],
            # 'importance': position['importance'],
            'dynamicPositionList': position['dynamicPositionList']
        }})

    def updateStockPositionStatus(self, id, status):
        DBPyChanlun['stock_position_record'].update_one({'_id': ObjectId(id)}, {"$set": {
            'status': status,
        }})


businessService = BusinessService()
