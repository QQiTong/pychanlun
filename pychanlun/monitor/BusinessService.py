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

tz = pytz.timezone('Asia/Shanghai')

# periodList = ['3min', '5min', '15min', '30min', '60min', '4hour', '1day']
periodList = ['3m', '5m', '15m', '30m', '60m']
# 主力合约列表
dominantSymbolList = []
# 主力合约详细信息
dominantSymbolInfoList = []
# CL:原油; GC:黄金;SI:白银; CT:棉花;S:大豆;SM：豆粕; BO:豆油;NID:伦镍; ZSD:伦锌;
# 马棕 日胶
otherSymbol = ["BTC", "CL", "GC", "SI", "CT", "S", "SM", "BO", "NID", "ZSD"]
hbSwapUrl = "http://api.btcgateway.pro/swap-ex/market/history/kline?contract_code=BTC-USD"
hbSwapTickUrl = "http://api.btcgateway.pro/swap-ex/market/trade?contract_code=BTC-USD"


class BusinessService:
    def __init__(self):
        print('初始化业务对象...')

    # okex数字货币部分涨跌幅
    def getBTCTicker(self):
        okexUrl = "https://www.okex.me/api/swap/v3/instruments/BTC-USDT-SWAP/ticker"
        r = requests.get(okexUrl)
        ticker = json.loads(r.text)
        # print("BTC实时价格",ticker)
        okexUrl2 = "https://www.okex.me/api/swap/v3/instruments/BTC-USDT-SWAP/candles?granularity=86400"
        r = requests.get(okexUrl2)
        data_list = json.loads(r.text)
        dayOpenPrice = data_list[0][1]
        change = round((float(ticker['last']) - float(dayOpenPrice)) / float(dayOpenPrice), 4)
        changeAndPrice = {
            'change': change,
            'price': ticker['last']
        }
        return changeAndPrice

    # okex数字货币部分涨跌幅
    # def getBTCTicker(self):
    #     dayParam = {
    #         'symbol': 'BTC-USD',  # 合约类型， 火币季度合约
    #         'period': '1day',
    #         'size': 1
    #     }
    #
    #     r = requests.get(hbSwapUrl,params=dayParam)
    #     daykline = json.loads(r.text)
    #
    #     dayOpenPrice = daykline['data'][-1]['open']
    #
    #     r = requests.get(hbSwapTickUrl)
    #     minKline = json.loads(r.text)
    #     minClosePrice = minKline['tick']['data'][-1]['price']
    #     change = round((float(minClosePrice) - dayOpenPrice) / dayOpenPrice,4)
    #     changeAndPrice = {
    #         'change':change,
    #         'price':minClosePrice
    #     }
    #     return changeAndPrice

    def getGlobalFutureChangeList(self):
        globalFutureSymbol = ["CL", "GC", "SI", "CT", "S", "SM", "BO", "NID", "ZSD"]
        changeList = {}
        for i in range(len(globalFutureSymbol)):
            item = globalFutureSymbol[i]
            # 查日线开盘价
            code = "%s_%s" % (item, '1d')
            data_list = DBPyChanlun[code].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find(
            ).sort("_id", pymongo.DESCENDING)
            dayOpenPrice = data_list[0]['open']
            code = "%s_%s" % (item, '5m')

            # 差5分钟收盘价
            data_list = DBPyChanlun[code].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)).find(
            ).sort("_id", pymongo.DESCENDING)
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
        return dominantSymbolInfoList

    def getFutureSignalList(self, strategyType):
        if strategyType == "0":
            return self.getNormalSignalList()
        elif strategyType == "3":
            return self.getStrategy3BeichiList()
        else:
            return self.getStrategy4BeichiList()

    def getNormalSignalList(self):
        symbolList = dominantSymbolList
        #  把外盘加进去

        symbolList.extend(otherSymbol)
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
            # utc 转本地时间
            date_created = signalItem['date_created'] + timedelta(hours=8)
            date_created_str = date_created.strftime("%m-%d %H:%M")
            fire_time = signalItem['fire_time'] + timedelta(hours=8)
            fire_time_str = fire_time.strftime("%m-%d %H:%M")
            # str(round(signalItem['price'], 2))
            msg = "%s %s %s %s" % (str(signalItem['signal']), str(signalItem['direction']), fire_time_str,
                                   str(signalItem['remark']))
            if signalItem['symbol'] in symbolListMap:
                symbolListMap[signalItem['symbol']][signalItem['period']] = msg
        # print("期货信号列表", symbolListMap)
        return symbolListMap

    def getStrategy3BeichiList(self):
        symbolList = dominantSymbolList
        #  把外盘加进去
        symbolList.extend(otherSymbol)
        symbolListMap = {}
        for i in range(len(symbolList)):
            symbol = symbolList[i]
            symbolListMap[symbol] = {}

            for j in range(len(periodList)):
                period = periodList[j]
                symbolListMap[symbol][period] = ""
        beichi_log_list = DBPyChanlun['strategy3_log'].find()
        for beichiItem in beichi_log_list:
            msg = beichiItem['remark'], str(
                round(beichiItem['price'], 2)), str(beichiItem['date_created'])
            if beichiItem['symbol'] in symbolListMap:
                symbolListMap[beichiItem['symbol']][beichiItem['period']] = msg
        # print("背驰列表", symbolListMap)
        return symbolListMap

    def getStrategy4BeichiList(self):
        symbolList = dominantSymbolList
        #  把外盘加进去
        symbolList.extend(otherSymbol)
        symbolListMap = {}
        for i in range(len(symbolList)):
            symbol = symbolList[i]
            symbolListMap[symbol] = {}
            for j in range(len(periodList)):
                period = periodList[j]
                symbolListMap[symbol][period] = ""
        beichi_log_list = DBPyChanlun['strategy4_log'].find()
        for beichiItem in beichi_log_list:
            msg = beichiItem['remark'], str(
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
        #     找出持仓列表中的老合约 和 主力合约 求集合的差
        positionList = self.getPositionList('holding', 1, 10)['records']
        # 找出持仓列表中的老合约
        diff = []
        for i in range(len(positionList)):
            item = positionList[i]
            if item not in dominantSymbolList:
                diff.append(item['symbol'])
        union = list(set(dominantSymbolList) | set(diff))
        for i in range(len(union)):
            item = union[i]
            # print(item)
            if item not in otherSymbol:
                df1d = rq.get_price(item, frequency='1d', fields=['open', 'high', 'low', 'close', 'volume'],
                                    start_date=start, end_date=end)
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
        symbolList = dominantSymbolList
        #  把外盘加进去
        symbolList.extend(otherSymbol)
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

    def getPosition(self, symbol, period, status):
        if period == 'all':
            query = {'symbol': symbol, 'status': status}
        else:
            query = {'symbol': symbol, 'period': period, 'status': status}
        # 当多空双开锁仓的时候，获取最新持仓的那个
        result = DBPyChanlun["future_auto_position"].find(
            query).sort("fire_time", pymongo.ASCENDING)
        if result.count() > 0:
            for x in result:
                x['_id'] = str(x['_id'])
            return x
        else:
            return -1
    def formatTime(self,localTime):
        localTimeStamp = time.localtime(int(time.mktime(localTime.timetuple()) + 8 * 3600))
        localTimeStampStr = time.strftime("%Y-%m-%d %H:%M:%S", localTimeStamp)
        return localTimeStampStr

    # 持仓列表改成自动录入
    def getPositionList(self, status, page, size):
        # positionList = []
        # collection = DBPyChanlun["position_record"]
        # # 查询总记录数
        # if status == 'all':
        #     result = collection.find().skip(
        #         (page - 1) * size).limit(size).sort("enterTime", pymongo.DESCENDING)
        #     total = result.count()
        # else:
        #     result = collection.find({'status': status}).skip(
        #         (page - 1) * size).limit(size).sort("enterTime", pymongo.DESCENDING)
        #     total = result.count()
        # for x in result:
        #     x['_id'] = str(x['_id'])
        #     positionList.append(x)
        # positionListResult = {
        #     'records': positionList,
        #     'total': total
        # }
        # return positionListResult
        positionList = []
        collection = DBPyChanlun["future_auto_position"]
        # 查询总记录数
        if status == 'all':
            result = collection.find().skip(
                (page - 1) * size).limit(size).sort("fire_time", pymongo.DESCENDING)
            total = result.count()
        else:
            result = collection.find({'status': status}).skip(
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
            #
            if x['symbol'] is 'BTC':
                marginLevel = 1 / (x['margin_rate'] )
            else:
                marginLevel = 1 / (x['margin_rate'] + 0.01)
            currentPercent = 0
            winEndPercent = 0
            loseEndPercent = 0
            if x['direction'] == "long":
                currentPercent = round(((x['close_price'] - x['price']) / x['price']) * marginLevel , 2)
                if x['status'] == 'winEnd':
                    winEndPercent = round(((x['win_end_price'] - x['price']) / x['price']) * marginLevel , 2)
                elif x['status'] == 'loseEnd':
                    loseEndPercent = round(((x['lose_end_price'] - x['price']) / x['price']) * marginLevel , 2)
                # print("long",currentPercent)
            else:
                currentPercent = round(((x['price'] - x['close_price']) / x['close_price'])* marginLevel, 2)
                if x['status'] == 'winEnd':
                    winEndPercent = round(((x['price'] - x['win_end_price']) / x['win_end_price']) * marginLevel, 2)
                elif x['status'] == 'loseEnd':
                    loseEndPercent = round(((x['price']-x['lose_end_price']) / x['price']) * marginLevel , 2)
                # print("short",currentPercent)
            # 未实现盈亏
            x['current_profit'] = round(x['per_order_margin'] * x['amount'] * currentPercent,2)
            # 止盈已实现盈亏
            x['win_end_money'] = round(x['per_order_margin'] * x['amount'] * winEndPercent,2)
            # 止盈比率
            x['win_end_rate'] = round(winEndPercent, 2)
            # 止损已实现盈亏
            x['lose_end_money'] = round(x['per_order_margin'] * x['amount'] * loseEndPercent,2)
            x['lose_end_rate'] = round(loseEndPercent, 2)
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
    # close_price 最新收盘价
    def updatePositionStatus(self, id, status,close_price):
        if status == 'winEnd':
            DBPyChanlun['future_auto_position'].update_one({'_id': ObjectId(id)}, {"$set": {
                'status': status,
                'win_end_price': float(close_price),
            }})
        elif status == 'loseEnd':
            DBPyChanlun['future_auto_position'].update_one({'_id': ObjectId(id)}, {"$set": {
                'status': status,
                'lose_end_price': float(close_price)
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
        print("更新预判参数", id, prejudgeList)
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
            item['remark'] = row["remark"]
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
