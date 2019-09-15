# -*- coding: utf-8 -*-

import pydash
import numpy as np
import json
from .funcat.time_series import (fit_series, NumericSeries)
from .funcat.func import CrossOver

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


def calc(time_s, macd_s, diff_s, dea_s, bi_list, duan_s):
    time_s, macd_s, diff_s, dea_s, duan_s = fit_series(time_s, macd_s, diff_s, dea_s, duan_s)
    divergence_down = np.zeros(len(time_s)) # 底背驰信号
    divergence_up = np.zeros(len(time_s)) # 顶背驰信号
    for i in range(len(duan_s)):
        if duan_s[i] == -1:
            duan_start = pydash.find_last_index(duan_s[:i], lambda d: d == 1)
            duan_end = i
            down_bi_list = pydash.filter_(bi_list,
                                        lambda bi: bi.direction == -1 and bi.klineList[-1].start <= duan_end and
                                                    bi.klineList[0].end >= duan_start)
            if len(down_bi_list) > 1:
                min_diffs = pydash.map_(down_bi_list, lambda bi: np.amin(diff_s[bi.start:bi.end + 1]))
                if len(min_diffs) > 1 and min_diffs[-1] > np.amin(min_diffs[:-1]):
                    divergence_down[i] = 1
        if duan_s[i] == 1:
            duan_start = pydash.find_last_index(duan_s[:i], lambda d: d == -1)
            duan_end = i
            up_bi_list = pydash.filter_(bi_list, lambda bi: bi.direction == 1 and bi.klineList[-1].start <= duan_end and
                                                            bi.klineList[0].end >= duan_start)
            if len(up_bi_list) > 1:
                max_diffs = pydash.map_(up_bi_list, lambda bi: np.amax(diff_s[bi.start:bi.end + 1]))
                if len(max_diffs) > 1 and max_diffs[-1] < np.amax(max_diffs[:-1]):
                    divergence_up[i] = 1
    return divergence_down, divergence_up


def note(divergence_down, divergence_up, time_s, diff_s, bigLevel = False):
    data = {
        'buyMACDBCData': {'date': [], 'data': [], 'value': []},
        'sellMACDBCData': {'date': [], 'data': [], 'value': []},
    }
    for i in range(len(divergence_down)):
        if divergence_down[i]:
            data['buyMACDBCData']['date'].append(time_s[i])
            data['buyMACDBCData']['data'].append(diff_s[i])
            if bigLevel:
                data['buyMACDBCData']['value'].append(signalMap['高级别线底背'])
            else:
                data['buyMACDBCData']['value'].append(signalMap['线底背'])
    for i in range(len(divergence_up)):
        if divergence_up[i]:
            data['sellMACDBCData']['date'].append(time_s[i])
            data['sellMACDBCData']['data'].append(diff_s[i])
            if bigLevel:
                data['sellMACDBCData']['value'].append(signalMap['高级别线顶背'])
            else:
                data['sellMACDBCData']['value'].append(signalMap['线顶背'])
    return data


def calcAndNote(time_s, macd_s, diff_s, dea_s, bi_list, duan_s, bigLevel = False):
    divergence_down, divergence_up = calc(time_s, macd_s, diff_s, dea_s, bi_list, duan_s)
    return note(divergence_down, divergence_up, time_s, diff_s, bigLevel)
