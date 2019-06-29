# -*- coding: utf-8 -*-

import pydash
import numpy as np
import json
from .funcat.time_series import (fit_series, NumericSeries)
from .funcat.func import CrossOver

def calc(time_s, macd_s, diff_s, dea_s, bi_list, duan_s):
    time_s, macd_s, diff_s, dea_s, duan_s = fit_series(time_s, macd_s, diff_s, dea_s, duan_s)
    divergence_down = np.zeros(len(time_s))
    divergence_up = np.zeros(len(time_s))
    for i in range(len(duan_s)):
        if duan_s[i] == -1:
            duan_start = pydash.find_last_index(duan_s[:i], lambda d: d == 1)
            duan_end = i
            down_bi_list = pydash.filter_(bi_list, lambda bi: bi.direction == -1 and bi.end <= duan_end+1 and bi.start >= duan_start)
            min_diffs = pydash.map_(down_bi_list, lambda bi: np.amin(diff_s[bi.start:bi.end]))
            if len(min_diffs) > 1 and min_diffs[-1] > np.amin(min_diffs[:-1]):
                divergence_down[i] = 1
        if duan_s[i] == 1:
            duan_start = pydash.find_last_index(duan_s[:i], lambda d: d == -1)
            duan_end = i
            up_bi_list = pydash.filter_(bi_list, lambda bi: bi.direction == 1 and bi.end <= duan_end+1 and bi.start >= duan_start)
            max_diffs = pydash.map_(up_bi_list, lambda bi: np.amax(diff_s[bi.start:bi.end]))
            if len(max_diffs) > 1 and max_diffs[-1] < np.amax(max_diffs[:-1]):
                divergence_up[i] = 1

    data = {
        'buyMACDBCData': {'date': [], 'data': [], 'value': []},
        'sellMACDBCData': {'date': [], 'data': [], 'value': []},
    }
    for i in range(len(divergence_down)):
        if divergence_down[i]:
            data['sellMACDBCData']['date'].append(time_s[i])
            data['sellMACDBCData']['data'].append(diff_s[i])
            data['sellMACDBCData']['value'].append('线底背')
    for i in range(len(divergence_up)):
        if divergence_up[i]:
            data['buyMACDBCData']['date'].append(time_s[i])
            data['buyMACDBCData']['data'].append(diff_s[i])
            data['buyMACDBCData']['value'].append('线顶背')
    return data

def calc_bak(payload):
    data = {
        'buyMACDBCData': {'date': [], 'data': [], 'value': []},
        'sellMACDBCData': {'date': [], 'data': [], 'value': []},
    }
    macdList = payload['macdList']
    diffList = payload['diffList']
    deaList = payload['deaList']
    timeList = payload['timeList']
    biList = payload['biList']
    # 线底背
    xianDiBei = [0 for i in range(len(timeList))]
    jinCha = [0 for i in range(len(timeList))]
    for i in range(len(macdList)):
        if i > 1 and macdList[i-1] < 0 and macdList[i] >= 0 and diffList[i] < 0:
            jinCha[i] = True

    for i in range(len(jinCha)):
        if jinCha[i] == True:
            iCurrent = 0
            iLast = 0
            iCurrent = pydash.find_index(
                biList, lambda bi: bi.start < i and bi.end >= i)
            for j in range(i - 1, 0, -1):
                if jinCha[j]:
                    iLast = pydash.find_index(
                        biList, lambda bi: bi.start < j and bi.end >= j)
                    break
            if iCurrent > iLast > 0:
                if biList[iCurrent].low < biList[iLast].low and diffList[i] > diffList[j] and deaList[i] > deaList[j]:
                    xianDiBei[i] = True

    for i in range(len(xianDiBei)):
        if xianDiBei[i]:
            data['sellMACDBCData']['date'].append(timeList[i])
            data['sellMACDBCData']['data'].append(diffList[i])
            data['sellMACDBCData']['value'].append('线底背')
    return data
