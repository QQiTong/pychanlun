# -*- coding: utf-8 -*-

import pydash
import numpy as np
import json

from pychanlun.funcat.time_series import (fit_series, NumericSeries)
from pychanlun.funcat.api import *
from pychanlun import Duan
from pychanlun.basic.bi import CalcBiList
import datetime


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

def calc_beichi_data(x_data, xx_data, bigLevel = False):
    divergence_down, divergence_up = calc_divergence(x_data, xx_data)
    bi_series = x_data['bi']
    duan_series = x_data['duan']
    time_series = x_data['timestamp']
    high_series = x_data['high']
    low_series = x_data['low']
    open_series = x_data['open']
    close_series = x_data['close']
    diff_series = x_data['diff']
    return note(divergence_down, divergence_up, bi_series, duan_series, time_series, high_series, low_series, open_series, close_series, diff_series, bigLevel)

def calc_divergence(x_data, xx_data):
    length = len(x_data)
    bi_list = CalcBiList(length, x_data['bi'], x_data['high'], x_data['low'])
    # 底背驰信号
    divergence_down = np.zeros(length)
    # 顶背驰信号
    divergence_up = np.zeros(length)
    gold_cross = CROSS(x_data['diff'], x_data['dea'])
    dead_cross = CROSS(x_data['dea'], x_data['diff'])
    time_series = x_data['timestamp']
    diff_series = x_data['diff']
    dea_series = x_data['dea']
    duan_series = x_data['duan']
    high_series = x_data['high']
    low_series = x_data['low']
    close_series = x_data['close']
    big_idx = 0
    for i in range(len(gold_cross.series)):
        big_idx = pydash.find_index(xx_data['timestamp'][big_idx:], lambda x : x >= time_series[i])
        big_direction = 0
        if big_idx > 0 and xx_data['diff'][big_idx] < 0 and xx_data['dea'][big_idx] < 0:
            big_direction = -1
        else:
            big_direction = 1

        if gold_cross.series[i] and diff_series[i] < 0:
            info = Duan.inspect(duan_series, high_series, low_series, close_series, diff_series, dea_series, i)
            if info is not None:
                if info['duan_type'] == -1:
                    duan_start = info['duan_start']
                    duan_end = info['duan_end']
                    down_bi_list = pydash.filter_(bi_list, lambda bi: bi["direction"] == -1 and bi["start"] <= duan_end and bi["end"] >= duan_start)
                    # 要创新低的向下笔
                    target_bi_list = []
                    for k in range(len(down_bi_list)):
                        if len(target_bi_list) == 0:
                            target_bi_list.append(down_bi_list[k])
                        elif low_series[down_bi_list[k]['end']] < low_series[target_bi_list[-1]['end']]:
                            target_bi_list.append(down_bi_list[k])
                    down_bi_list = target_bi_list
                    if len(down_bi_list) > 1:
                        if big_direction == 1:
                            # 大级别在0轴上，2笔就可以
                            if len(down_bi_list) < 2:
                                continue
                            down_bi_list = down_bi_list[-2:]
                        else:
                            # 大级别在0轴下，要3笔
                            if len(down_bi_list) < 3:
                                continue
                            down_bi_list = down_bi_list[-3:]
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
    big_idx = 0
    for i in range(len(dead_cross.series)):
        big_idx = pydash.find_index(xx_data['timestamp'][big_idx:], lambda x : x >= time_series[i])
        big_direction = 0
        if big_idx > 0 and xx_data['diff'][big_idx] < 0 and xx_data['dea'][big_idx] < 0:
            big_direction = -1
        else:
            big_direction = 1
        if dead_cross.series[i] and diff_series[i] > 0:
            info = Duan.inspect(duan_series, high_series, low_series, close_series, diff_series, dea_series, i)
            if info is not None:
                if info['duan_type'] == 1:
                    duan_start = info['duan_start']
                    duan_end = info['duan_end']
                    up_bi_list = pydash.filter_(bi_list, lambda bi: bi["direction"] == 1 and bi["start"] <= duan_end and bi["end"] >= duan_start)
                    for k in range(len(up_bi_list)):
                        if len(target_bi_list) == 0:
                            target_bi_list.append(up_bi_list[k])
                        elif high_series[up_bi_list[k]['end']] > high_series[target_bi_list[-1]['end']]:
                            target_bi_list.append(up_bi_list[k])
                    up_bi_list = target_bi_list
                    if len(up_bi_list) > 1:
                        if big_direction == -1:
                            # 大级别在0轴下，2笔就可以
                            if len(up_bi_list) < 2:
                                continue
                            up_bi_list = up_bi_list[-2:]
                        else:
                            # 大级别在0轴上，要3笔
                            if len(up_bi_list) < 3:
                                continue
                            up_bi_list = up_bi_list[-3:]
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
            data['buyMACDBCData']['date'].append(datetime.datetime.fromtimestamp(time_series[i]).strftime('%Y-%m-%d %H:%M'))
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
                data['buyMACDBCData']['stop_win_price'].append(high_series[bi_index])
            else:
                data['buyMACDBCData']['stop_win_price'].append(0)
    for i in range(len(divergence_up)):
        if divergence_up[i] == 1:
            data['sellMACDBCData']['date'].append(datetime.datetime.fromtimestamp(time_series[i]).strftime('%Y-%m-%d %H:%M'))
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
                data['sellMACDBCData']['stop_win_price'].append(low_series[bi_index])
            else:
                data['sellMACDBCData']['stop_win_price'].append(0)
    return data
