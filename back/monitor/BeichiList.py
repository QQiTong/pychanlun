import rqdatac as rq
from mongoengine import connect
import os
import json
from back.monitor.BeichiLog import BeichiLog
from back.config import config

periodList = ['3min', '5min', '15min', '30min', '60min', '4hour', '1day']


class BeichiList:
    def __init__(self):
        print('beichi List init')

    def getDominantSymbol(self):
        symbolList = ['RB', 'HC', 'RU', 'NI', 'FU', 'ZN', 'SP', 'BU',
                      'MA', 'TA', 'SR', 'OI', 'AP', 'CF',
                      'M', 'I', 'EG', 'J', 'JM', 'PP', 'L'
                      ]
        dominantSymbolList = []
        for i in range(len(symbolList)):
            df = rq.futures.get_dominant(symbolList[i], start_date=None, end_date=None, rule=0)
            dominantSymbol = df[-1]
            dominantSymbolList.append(dominantSymbol)
        return dominantSymbolList

    def getBeichiList(self):

        cfg = config[os.environ.get('PYCHANLUN_CONFIG_ENV', 'default')]
        mongodbSettings = cfg.MONGODB_SETTINGS
        connect('pychanlun', host=mongodbSettings['host'], port=mongodbSettings['port'],
                username=mongodbSettings['username'], password=mongodbSettings['password'],
                authentication_source='admin')
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
            msg = beichiItem.remark,str(round(beichiItem.price)),str(beichiItem.date_created)
            symbolListMap[beichiItem.symbol][beichiItem.period] = msg
        print("背驰列表", symbolListMap)
        return symbolListMap
