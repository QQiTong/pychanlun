# -*- coding: utf-8 -*-

import pydash
import numpy as np
import json

from pychanlun.funcat.time_series import (fit_series, NumericSeries)
from pychanlun.funcat.api import *
from pychanlun import Duan
from pychanlun.basic.bi import CalcBiList


'''
     High 高级别 H
     Sell  顶 S
     Buy   底 B
     Xian   黄白线 X
     Ji     面积 J
'''
signalMap = {
    '高级别线底背': 'HXB',
    '线底背': 'XB',
    '高级别线顶背': 'HXT',
    '线顶背': 'XS',

    '高级别积底背': 'HJB',
    '积底背': 'JB',
    '高级别积顶背': 'HJT',
    '积顶背': 'JS',
}


def calc(time_series, high_series, low_series, open_series, close_series, macd_series, diff_series, dea_series, bi_series, duan_series):
    time_series, macd_series, diff_series, dea_series, bi_series, duan_series = fit_series(time_series, macd_series, diff_series, dea_series, bi_series, duan_series)
    bi_list = CalcBiList(len(time_series), bi_series, high_series, low_series)
    # 底背驰信号
    divergence_down = np.zeros(len(time_series))
    # 顶背驰信号
    divergence_up = np.zeros(len(time_series))
    gold_cross = CROSS(diff_series, dea_series)
    dead_cross = CROSS(dea_series, diff_series)
    for i in range(len(gold_cross.series)):
        if gold_cross.series[i] and diff_series[i] < 0:
            info = Duan.inspect(duan_series, high_series, low_series, close_series, diff_series, dea_series, i)
            if info is not None:
                if info['duan_type'] == -1:
                    duan_start = info['duan_start']
                    duan_end = info['duan_end']
                    down_bi_list = pydash.filter_(bi_list, lambda bi: bi["direction"] == -1 and bi["start"] <= duan_end and bi["end"] >= duan_start)
                    if len(down_bi_list) > 1:
                        down_bi_list = down_bi_list[-2:]
                        diff1 = np.amin(diff_series[down_bi_list[-1]['start']:i+1])
                        x = down_bi_list[-2]['end']
                        for y in range(down_bi_list[-2]['end'], down_bi_list[-1]['start']):
                            if gold_cross.series[y]:
                                x = y
                        diff2 = np.amin(diff_series[down_bi_list[-2]['start']:x+1])
                        if diff1 > diff2:
                            # 前面是向下段，才是背驰点
                            # 要向下段后的第一次金叉
                            if info['duan_end'] == i:
                                divergence_down[i] = 1
                            elif len(pydash.filter_(gold_cross.series[info['duan_end']:i], lambda x: x == 1)) == 0:
                                divergence_down[i] = 1
    for i in range(len(dead_cross.series)):
        if dead_cross.series[i] and diff_series[i] > 0:
            info = Duan.inspect(duan_series, high_series, low_series, close_series, diff_series, dea_series, i)
            if info is not None:
                if info['duan_type'] == 1:
                    duan_start = info['duan_start']
                    duan_end = info['duan_end']
                    up_bi_list = pydash.filter_(bi_list, lambda bi: bi["direction"] == 1 and bi["start"] <= duan_end and bi["end"] >= duan_start)
                    if len(up_bi_list) > 1:
                        up_bi_list = up_bi_list[-2:]
                        diff1 = np.amax(diff_series[up_bi_list[-1]['start']:i+1])
                        x = up_bi_list[-2]['end']
                        for y in range(up_bi_list[-2]['end'], up_bi_list[-1]['start']):
                            if dead_cross.series[y]:
                                x = y
                        diff2 = np.amax(diff_series[up_bi_list[-2]['start']:x+1])
                        if diff1 < diff2:
                            # 前面是向上段，才是背驰点
                            # 要向上段后的第一次死叉
                            if info['duan_end'] == i:
                                divergence_up[i] = 1
                            elif len(pydash.filter_(dead_cross.series[info['duan_end']:i], lambda x: x == 1)) == 0:
                                divergence_up[i] = 1
    return divergence_down, divergence_up

def note(divergence_down, divergence_up, bi_series, duan_series, time_series, high_series, low_series, open_series, close_series, diff_series, bigLevel = False):
    data = {
        'buyMACDBCData': {'date': [], 'data': [], 'value': [], 'stop_lose_price': [], 'diff': [], 'stop_win_price': []},
        'sellMACDBCData': {'date': [], 'data': [], 'value': [], 'stop_lose_price': [], 'diff': [], 'stop_win_price': []},
    }
    for i in range(len(divergence_down)):
        if divergence_down[i] == 1:
            data['buyMACDBCData']['date'].append(time_series[i])
            # data属性保持和其他信号统一使用触发背驰的价格 便于前端统一标出开仓横线
            data['buyMACDBCData']['data'].append(open_series[i])
            if bigLevel:
                data['buyMACDBCData']['value'].append(signalMap['高级别线底背'])
            else:
                data['buyMACDBCData']['value'].append(signalMap['线底背'])
            bottom_index = pydash.find_last_index(duan_series[:i+1], lambda x: x == -1)
            if bottom_index > -1:
                data['buyMACDBCData']['stop_lose_price'].append(low_series[bottom_index])
            else:
               data['buyMACDBCData']['stop_lose_price'].append(0)
            data['buyMACDBCData']['diff'].append(diff_series[i])

            # 底背驰，往后找第一次成笔的位置
            bi_index = pydash.find_index(bi_series[i:], lambda x: x == 1)
            if bi_index > -1:
                data['buyMACDBCData']['stop_win_price'].append(high_series[i + bi_index])
            else:
                data['buyMACDBCData']['stop_win_price'].append(0)
    for i in range(len(divergence_up)):
        if divergence_up[i] == 1:
            data['sellMACDBCData']['date'].append(time_series[i])
            data['sellMACDBCData']['data'].append(open_series[i])
            if bigLevel:
                data['sellMACDBCData']['value'].append(signalMap['高级别线顶背'])
            else:
                data['sellMACDBCData']['value'].append(signalMap['线顶背'])
            top_index = pydash.find_last_index(duan_series[:i+1], lambda x: x == 1)
            if top_index > -1:
                data['sellMACDBCData']['stop_lose_price'].append(high_series[top_index])
            else:
               data['sellMACDBCData']['stop_lose_price'].append(0)
            data['sellMACDBCData']['diff'].append(diff_series[i])

            # 顶背驰，往后找第一次成笔的位置
            bi_index = pydash.find_index(bi_series[i:], lambda x: x == -1)
            if bi_index > -1:
                data['sellMACDBCData']['stop_win_price'].append(low_series[i + bi_index])
            else:
                data['sellMACDBCData']['stop_win_price'].append(0)
    return data


def calcAndNote(time_series, high_series, low_series, open_series, close_series, macd_series, diff_series, dea_series, bi_series, duan_series, bigLevel = False):
    divergence_down, divergence_up = calc(time_series, high_series, low_series, open_series, close_series, macd_series, diff_series, dea_series, bi_series, duan_series)
    return note(divergence_down, divergence_up, bi_series, duan_series, time_series, high_series, low_series, open_series, close_series, diff_series, bigLevel)
