# -*- coding: utf-8 -*-
import pydash

from .funcat.time_series import (fit_series)
from . import series_tool

class Entanglement:
    def __init__(self):
        self.start = 0
        self.end = 0
        self.startTime = 0
        self.endTime = 0
        self.top = 0
        self.zg = 0 #中枢高
        self.bottom = 0
        self.zd = 0 #中枢低
        self.gg = 0 #中枢高高
        self.dd = 0 #中枢低低
        self.direction = 0
        self.formal = False


def calcEntanglements(time_data, duan_data, bi_data, high_data, low_data):
    time_data, duan_data, bi_data, high_data, low_data = fit_series(time_data, duan_data, bi_data, high_data, low_data)
    count = len(time_data)
    e_list = []
    for i in range(count):
        if duan_data[i] == -1:
            # i是线段低点
            j = 0
            for j in range(i, 0, -1):
                if duan_data[j] == 1:
                    break
            if j >= 0 and j < i:
                # j是线段高点
                e_down_list = []
                for x in range(j, i):
                    if bi_data[x] == -1 and x < i:
                        e = Entanglement()
                        e.start = x
                        e.startTime = time_data[x]
                        e.bottom = low_data[x]
                        e.zd = low_data[x]
                        e.dd = low_data[x]
                        e.direction = -1
                        e_down_list.append(e)
                    if bi_data[x] == 1 and len(e_down_list) > 0:
                        e_down_list[-1].end = x
                        e_down_list[-1].endTime = time_data[x]
                        e_down_list[-1].top = high_data[x]
                        e_down_list[-1].zg = high_data[x]
                        e_down_list[-1].gg = high_data[x]
                        if len(e_down_list) > 1:
                            # 看是否有重叠区间
                            if e_down_list[-1].top >= e_down_list[-2].bottom and e_down_list[-1].bottom <= e_down_list[-2].top:
                            # 有重叠区间
                                if not e_down_list[-2].formal:
                                    e_down_list[-2].top = min(e_down_list[-1].top, e_down_list[-2].top)
                                    e_down_list[-2].zg = min(e_down_list[-1].zg, e_down_list[-2].zg)
                                    e_down_list[-2].gg = max(e_down_list[-1].gg, e_down_list[-2].gg)
                                    e_down_list[-2].bottom = max(e_down_list[-1].bottom, e_down_list[-2].bottom)
                                    e_down_list[-2].zd = max(e_down_list[-1].zd, e_down_list[-2].zd)
                                    e_down_list[-2].dd = min(e_down_list[-1].dd, e_down_list[-2].dd)
                                    e_down_list[-2].end = e_down_list[-1].end
                                    e_down_list[-2].endTime = time_data[e_down_list[-2].end]
                                    e_down_list[-2].formal = True
                                else:
                                    e_down_list[-2].gg = max(e_down_list[-1].gg, e_down_list[-2].gg)
                                    e_down_list[-2].dd = min(e_down_list[-1].dd, e_down_list[-2].dd)
                                    e_down_list[-2].end = e_down_list[-1].end
                                    e_down_list[-2].endTime = time_data[e_down_list[-2].end]
                                e_down_list.pop()
                for r in range(len(e_down_list)):
                    if e_down_list[r].formal:
                        e_list.append(e_down_list[r])
        if duan_data[i] == 1:
            # i是线段高点
            j = 0
            for j in range(i, 0, -1):
                if duan_data[j] == -1:
                    break
            if j >= 0 and j < i:
                # j是线段低点
                e_up_list = []
                for x in range(j, i):
                    if bi_data[x] == 1 and x < i:
                        e = Entanglement()
                        e.start = x
                        e.startTime = time_data[x]
                        e.top = high_data[x]
                        e.zg = high_data[x]
                        e.gg = high_data[x]
                        e.direction = 1
                        e_up_list.append(e)
                    if bi_data[x] == -1 and len(e_up_list) > 0:
                        e_up_list[-1].end = x
                        e_up_list[-1].endTime = time_data[x]
                        e_up_list[-1].bottom = low_data[x]
                        e_up_list[-1].zd = low_data[x]
                        e_up_list[-1].dd = low_data[x]
                        if len(e_up_list) > 1:
                            # 看是否有重叠区间
                            if e_up_list[-1].bottom <= e_up_list[-2].top and e_up_list[-1].top >= e_up_list[-2].bottom:
                            # 有重叠区间
                                if not e_up_list[-2].formal:
                                    e_up_list[-2].top = min(e_up_list[-1].top, e_up_list[-2].top)
                                    e_up_list[-2].zg = min(e_up_list[-1].zg, e_up_list[-2].zg)
                                    e_up_list[-2].gg = max(e_up_list[-1].gg, e_up_list[-2].gg)
                                    e_up_list[-2].bottom = max(e_up_list[-1].bottom, e_up_list[-2].bottom)
                                    e_up_list[-2].zd = max(e_up_list[-1].zd, e_up_list[-2].zd)
                                    e_up_list[-2].dd = min(e_up_list[-1].dd, e_up_list[-2].dd)
                                    e_up_list[-2].end = e_up_list[-1].end
                                    e_up_list[-2].endTime = time_data[e_up_list[-2].end]
                                    e_up_list[-2].formal = True
                                else:
                                    e_up_list[-2].gg = max(e_up_list[-1].gg, e_up_list[-2].gg)
                                    e_up_list[-2].dd = min(e_up_list[-1].dd, e_up_list[-2].dd)
                                    e_up_list[-2].end = e_up_list[-1].end
                                    e_up_list[-2].endTime = time_data[e_up_list[-2].end]
                                e_up_list.pop()
                for r in range(len(e_up_list)):
                    if e_up_list[r].formal:
                        e_list.append(e_up_list[r])
    return e_list


def la_hui(e_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series):
    result = {
        'buy_zs_huila': {
            'date': [],
            'data': [],
            'stop_lose_price': [],
            'beichi_price': []
        },
        'sell_zs_huila': {
            'date': [],
            'data': [],
            'stop_lose_price': [],
            'beichi_price': []
        }
    }
    for i in range(len(e_list)):
        e = e_list[i]
        e_next = e_list[i+1] if i+1 < len(e_list) else None
        if e.direction == 1:
            # 上涨中枢，找第一次的拉回
            e_end = e.end
            # 离开中枢后的第一个笔结束
            leave = series_tool.find_index(bi_series, lambda x: x == 1, e_end)
            if leave >= 0:
                r = -1
                for x in range(leave + 1, len(close_series)):
                    if close_series[x] < e.top:
                        r = x
                        break
                    if duan_series[x] == -1:
                        break
                    # if e_next is not None and x >= e_next.end:
                    #     break
                if r >= 0:
                    result['sell_zs_huila']['date'].append(time_series[r])
                    result['sell_zs_huila']['data'].append(e.top)
                    top_index = pydash.find_last_index(duan_series[:r+1], lambda x: x == 1)
                    if top_index > -1:
                        result['sell_zs_huila']['stop_lose_price'].append(high_series[top_index])
                    else:
                        result['sell_zs_huila']['stop_lose_price'].append(0)
        if e.direction == -1:
            # 下跌中枢，找第一次的拉回
            e_end = e.end
            leave = pydash.index_of(bi_series, -1, e_end)
            leave = series_tool.find_index(bi_series, lambda x: x == -1, e_end)
            if leave >= 0:
                r = -1
                for x in range(leave + 1, len(close_series)):
                    if close_series[x] > e.bottom:
                        r = x
                        break
                    if duan_series[x] == -1:
                        break
                    # if e_next is not None and x >= e_next.end:
                    #     break
                if r >= 0:
                    result['buy_zs_huila']['date'].append(time_series[r])
                    result['buy_zs_huila']['data'].append(e.bottom)
                    bottom_index = pydash.find_last_index(duan_series[:r+1], lambda x: x == -1)
                    if bottom_index > -1:
                        result['buy_zs_huila']['stop_lose_price'].append(low_series[bottom_index])
                    else:
                        result['buy_zs_huila']['stop_lose_price'].append(0)
    return result


def tu_po(e_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series):
    result = {
        'buy_zs_tupo': {
            'date': [],
            'data': []
        },
        'sell_zs_tupo': {
            'date': [],
            'data': []
        }
    }
    for i in range(len(e_list)):
        e = e_list[i]
        e_next = e_list[i+1] if i+1 < len(e_list) else None
        if e.direction == 1:
            r = -1
            for x in range(e.end+1, len(close_series)):
                if close_series[x] > e.gg:
                    r = x
                    break
                if duan_series[x] == 1:
                    break
            if r > 0:
                result['buy_zs_tupo']['date'].append(time_series[r])
                result['buy_zs_tupo']['data'].append(e.gg)
        if e.direction == -1:
            r = -1
            for x in range(e.end+1, len(close_series)):
                if close_series[x] < e.dd:
                    r = x
                    break
                if duan_series[x] == -1:
                    break
            if r > 0:
                result['sell_zs_tupo']['date'].append(time_series[r])
                result['sell_zs_tupo']['data'].append(e.dd)
    return result

def v_reverse(e_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series):
    result = {
        'buy_v_reverse': {
            'date': [],
            'data': []
        },
        'sell_v_reverse': {
            'date': [],
            'data': []
        }
    }
    for i in range(len(e_list)):
        e = e_list[i]
        if e.direction == 1:
            # 离开中枢后的第一段结束
            leave_end_index = pydash.index_of(duan_series, 1, e.end)
            if leave_end_index >= 0:
                # 存在强3买
                buy3 = False
                resist_index = -1
                resist_price = 0
                for j in range(e.end+1, leave_end_index):
                    if bi_series[j] == -1 and low_series[j] > e.gg:
                        buy3 = True
                        resist_index = j
                        resist_price = low_series[resist_index]
                        break
                if buy3:
                    for k in range(leave_end_index+1, len(close_series)):
                        if bi_series[k] == -1:
                            break
                        if close_series[k] < resist_price:
                            if pydash.find_last_index(result['sell_v_reverse']['date'], lambda x: x == time_series[k]) == -1:
                                result['sell_v_reverse']['date'].append(time_series[k])
                                result['sell_v_reverse']['data'].append(resist_price)
                            break
        if e.direction == -1:
            # 离开中枢后的第一段结束
            leave_end_index = pydash.index_of(duan_series, -1, e.end)
            if leave_end_index >= 0:
                # 存在3卖
                sell3 = False
                resist_index = -1
                resist_price = 0
                for j in range(e.end+1, leave_end_index):
                    if bi_series[j] == 1 and high_series[j] > e.dd:
                        sell3 = True
                        resist_index = j
                        resist_price = high_series[resist_index]
                        break
                if sell3:
                    for k in range(leave_end_index+1, len(close_series)):
                        if bi_series[k] == 1:
                            break
                        if close_series[k] > resist_price:
                            if pydash.find_last_index(result['buy_v_reverse']['date'], lambda x: x == time_series[k]) == -1:
                                result['buy_v_reverse']['date'].append(time_series[k])
                                result['buy_v_reverse']['data'].append(resist_price)
                            break

    return result