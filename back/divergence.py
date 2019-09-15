# -*- coding: utf-8 -*-

import pydash
import numpy as np
import json

from .funcat.time_series import (fit_series, NumericSeries)
from .funcat.api import *
from . import Duan


'''
     High 高级别 H
     Top  顶 T
     Bottom 底 B
     Xian   黄白线 X
     Ji     面积 J
'''
signalMap = {
    '高级别线底背': 'HXB',
    '线底背': 'XB',
    '高级别线顶背': 'HXT',
    '线顶背': 'XT',

    '高级别积底背': 'HJB',
    '积底背': 'JB',
    '高级别积顶背': 'HJT',
    '积顶背': 'JT',
}


def calc(time_series, high_series, low_series, open_series, close_series, macd_series, diff_series, dea_series, bi_list, duan_series):
    time_series, macd_series, diff_series, dea_series, duan_series = fit_series(time_series, macd_series, diff_series, dea_series, duan_series)
    # 底背驰信号
    divergence_down = np.zeros(len(time_series))
    # 顶背驰信号
    divergence_up = np.zeros(len(time_series))
    gold_cross = CROSS(diff_series, dea_series)
    dead_cross = CROSS(dea_series, diff_series)
    for i in range(len(gold_cross.series)):
        if gold_cross.series[i]:
            info = Duan.inspect(duan_series, high_series, low_series, close_series, diff_series, dea_series, i)
            if info is not None:
                if info['duan_type'] == -1:
                    # 前面是向下段，才是背驰点
                    # 要向下段后的第一次金叉
                    if info['duan_end'] == i:
                        divergence_down[i] = 1
                    elif len(pydash.filter_(gold_cross.series[info['duan_end']:i], lambda x: x == 1)) == 0:
                        divergence_down[i] = 1
    for i in range(len(dead_cross.series)):
        if dead_cross.series[i]:
            info = Duan.inspect(duan_series, high_series, low_series, close_series, diff_series, dea_series, i)
            if info is not None:
                if info['duan_type'] == 1:
                    # 前面是向上段，才是背驰点
                    # 要向上段后的第一次死叉
                    if info['duan_end'] == i:
                        divergence_up[i] = 1
                    elif len(pydash.filter_(dead_cross.series[info['duan_end']:i], lambda x: x == 1)) == 0:
                        divergence_up[i] = 1
    return divergence_down, divergence_up


def note(divergence_down, divergence_up, duan_series, time_series, high_series, low_series, open_series, close_series, diff_series, bigLevel = False):
    data = {
        'buyMACDBCData': {'date': [], 'data': [], 'value': [], 'duan_price': [], 'beichi_price': []},
        'sellMACDBCData': {'date': [], 'data': [], 'value': [], 'duan_price': [], 'beichi_price': []},
    }
    for i in range(len(divergence_down)):
        if divergence_down[i] == 1:
            data['buyMACDBCData']['date'].append(time_series[i])
            data['buyMACDBCData']['data'].append(diff_series[i])
            if bigLevel:
                data['buyMACDBCData']['value'].append(signalMap['高级别线底背'])
            else:
                data['buyMACDBCData']['value'].append(signalMap['线底背'])
            bottom_index = pydash.find_last_index(duan_series[:i], lambda x: x == -1)
            if bottom_index > -1:
                data['buyMACDBCData']['duan_price'].append(low_series[bottom_index])
            else:
               data['buyMACDBCData']['duan_price'].append(0)
            data['buyMACDBCData']['beichi_price'].append(open_series[i])
    for i in range(len(divergence_up)):
        if divergence_up[i] == 1:
            data['sellMACDBCData']['date'].append(time_series[i])
            data['sellMACDBCData']['data'].append(diff_series[i])
            if bigLevel:
                data['sellMACDBCData']['value'].append(signalMap['高级别线顶背'])
            else:
                data['sellMACDBCData']['value'].append(signalMap['线顶背'])
            top_index = pydash.find_last_index(duan_series[:i], lambda x: x == 1)
            if top_index > -1:
                data['sellMACDBCData']['duan_price'].append(high_series[top_index])
            else:
               data['sellMACDBCData']['duan_price'].append(0)
            data['sellMACDBCData']['beichi_price'].append(open_series[i])
    return data


def calcAndNote(time_series, high_series, low_series, open_series, close_series, macd_series, diff_series, dea_series, bi_list, duan_series, bigLevel = False):
    divergence_down, divergence_up = calc(time_series, high_series, low_series, open_series, close_series, macd_series, diff_series, dea_series, bi_list, duan_series)
    return note(divergence_down, divergence_up, duan_series, time_series, high_series, low_series, open_series, close_series, diff_series, bigLevel)
