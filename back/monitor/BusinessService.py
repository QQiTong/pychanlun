import rqdatac as rq
from mongoengine import connect
import os
import json
from back.monitor.BeichiLog import BeichiLog
from back.config import config
from datetime import datetime, timedelta

periodList = ['3min', '5min', '15min', '30min', '60min', '4hour', '1day']


class BusinessService:
    def __init__(self):
        print('beichi List init')

    def getDominantSymbol(self):

        with open(os.path.join(os.path.dirname(__file__), '../../futureSymbol.json'), 'r') as load_f:
            symbolList = json.load(load_f)
            print(symbolList)
        dominantSymbolList = []
        for i in range(len(symbolList)):
            df = rq.futures.get_dominant(symbolList[i], start_date=None, end_date=None, rule=0)
            dominantSymbol = df[-1]
            dominantSymbolList.append(dominantSymbol)
        return dominantSymbolList

    def getBeichiList(self):
        symbolList = self.getDominantSymbol()
        #  把btc eth 加进去
        symbolList.append("BTC_CQ")
        symbolList.append("ETH_CQ")
        symbolListMap = {}
        for i in range(len(symbolList)):
            symbol = symbolList[i]
            symbolListMap[symbol] = {}

            for j in range(len(periodList)):
                period = periodList[j]
                symbolListMap[symbol][period] = ""

        for beichiItem in BeichiLog.objects:
            # todo 以后增加了沪金后 取整需要去掉
            msg = beichiItem.remark, str(round(beichiItem.price, 2)), str(beichiItem.date_created)
            symbolListMap[beichiItem.symbol][beichiItem.period] = msg
        print("背驰列表", symbolListMap)
        return symbolListMap

    # 获取涨跌幅数据
    def getChangeList(self):
        dominantSymbolList = self.getDominantSymbol()
        symbolChangeMap = {}
        end = datetime.now() + timedelta(1)
        start = datetime.now() + timedelta(-1)
        for i in range(len(dominantSymbolList)):
            item = dominantSymbolList[i]
            df1d = rq.get_price(item, frequency='1d', fields=['open', 'high', 'low', 'close', 'volume'],
                                start_date=start, end_date=end)
            df1m = rq.get_price(item, frequency='1m', fields=['open', 'high', 'low', 'close', 'volume'],
                                start_date=start, end_date=end)
            preday = df1d.iloc[len(df1d) - 1, 3]
            today = df1m.iloc[len(df1m) - 1, 3]
            change = (today - preday) / preday
            symbolChangeMap[item] = change
        print("涨跌幅信息",symbolChangeMap)

        return symbolChangeMap
