'''
合成任意周期K线
'''
from math import *
from datetime import datetime
import json
import os
import time


class ComposeKline:

    def timeFilter(self, records, since, to=1000000000000000):
        bars = []
        for i in records:
            if i['id'] >= since and i['id'] <= to:
                bars.append(i)

        return bars

    def calcRecords(self, records, period=30, start=None):
        try:
            records[0]
        except IndexError:
            return []

        period_ms = period * 60  # 以秒记的K线周期
        end_in = records[len(records) - 1]['id']  # K线的结束时间
        start_at = records[0]['id']  # K线的开始时间

        # 获得可以用于计算目标K线的开始时间
        r_offest = start_at % period_ms
        start_at = start_at - r_offest + period_ms
        if start is not None:
            start_at = start

        target_count = int((end_in - start_at) / period_ms)  # 目标K线的数量
        # target_count = int(target_count)
        n_records = []

        for i in range(0, target_count):
            bars = self.timeFilter(records, start_at + i * period_ms, start_at + (i + 1) * period_ms - 1)
            try:
                bars[0]
            except IndexError:
                continue
            # 初始化新的Bar
            Time = bars[0]['id']
            Open = bars[0]['open']
            High = bars[0]['high']
            Low = bars[0]['low']
            Close = bars[0]['close']
            Amount = 0
            for item in bars:
                High = max(High, item['high'])
                Low = min(Low, item['low'])
                Close = item['close']
                Amount += item['amount']

            # 将Bar添加添加到新的K线中
            n_records.append(dict({
                'id': Time,
                'open': Open,
                'high': High,
                'low': Low,
                'close': Close,
                'amount': Amount
            }))

        return n_records

    # src 原始k线 target 需要转换的级别
    def compose(self, src, target):
        klineList = []
        for i in range(len(src)):
            item = src[i]
            newItem = {}
            newItem['amount'] = round(float(item['amount']), 2)
            newItem['open'] = round(float(item['open']), 2)
            newItem['high'] = round(float(item['high']), 2)
            newItem['low'] = round(float(item['low']), 2)
            newItem['close'] = round(float(item['close']), 2)
            newItem['id'] = item['id']
            klineList.append(newItem)

        result = self.calcRecords(klineList, target)
        return result
