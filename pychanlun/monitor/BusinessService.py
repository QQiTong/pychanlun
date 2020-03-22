# -*- coding: utf-8 -*-

import rqdatac as rq
import os
import json
from pychanlun.config import config
from datetime import datetime, timedelta
from pychanlun.db import DBPyChanlun
from bson.codec_options import CodecOptions
import pytz
import pymongo
import pandas as pd
from bson import ObjectId
import time

tz = pytz.timezone('Asia/Shanghai')

# periodList = ['3min', '5min', '15min', '30min', '60min', '4hour', '1day']
periodList = ['3m', '5m', '15m', '30m', '60m']
# 主力合约列表
dominantSymbolList = []
# 主力合约详细信息
dominantSymbolInfoList = []
# CL:原油; GC:黄金;SI:白银; CT:棉花;S:大豆;SM：豆粕; BO:豆油;NID:伦镍; ZSD:伦锌;
# 马棕 日胶
otherSymbol = ["BTC", "CL", "GC", "SI", "CT","S", "SM", "BO", "NID", "ZSD"]


class BusinessService:
    def __init__(self):
        print('初始化业务对象...')

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
        for i in range(len(dominantSymbolList)):
            item = dominantSymbolList[i]
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
        return symbolChangeMap

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
        result = DBPyChanlun["position_record"].find(
            query).sort("enterTime", pymongo.ASCENDING)
        if result.count() > 0:
            for x in result:
                x['_id'] = str(x['_id'])
            return x
        else:
            return -1

    def getPositionList(self, status, page, size):
        positionList = []
        collection = DBPyChanlun["position_record"]
        # 查询总记录数
        if status == 'all':
            result = collection.find().skip(
                (page - 1) * size).limit(size).sort("enterTime", pymongo.DESCENDING)
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

    def updatePositionStatus(self, id, status):
        DBPyChanlun['position_record'].update_one({'_id': ObjectId(id)}, {"$set": {
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
