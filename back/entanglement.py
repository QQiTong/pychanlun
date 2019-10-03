# -*- coding: utf-8 -*-
import pydash

from .funcat.time_series import (fit_series)

class Entanglement:
    def __init__(self):
        self.start = 0
        self.end = 0
        self.startTime = 0
        self.endTime = 0
        self.top = 0
        self.bottom = 0
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
                        e.direction = -1
                        e_down_list.append(e)
                    if bi_data[x] == 1 and len(e_down_list) > 0:
                        e_down_list[-1].end = x
                        e_down_list[-1].endTime = time_data[x]
                        e_down_list[-1].top = high_data[x]
                        if len(e_down_list) > 1:
                            # 看是否有重叠区间
                            if e_down_list[-1].top >= e_down_list[-2].bottom and e_down_list[-1].bottom <= e_down_list[-2].top:
                                # 有重叠区间
                                e_down_list[-2].top = min(e_down_list[-1].top, e_down_list[-2].top)
                                e_down_list[-2].bottom = max(e_down_list[-1].bottom, e_down_list[-2].bottom)
                                e_down_list[-2].end = e_down_list[-1].end
                                e_down_list[-2].endTime = time_data[e_down_list[-2].end]
                                e_down_list[-2].formal = True
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
                        e.direction = 1
                        e_up_list.append(e)
                    if bi_data[x] == -1 and len(e_up_list) > 0:
                        e_up_list[-1].end = x
                        e_up_list[-1].endTime = time_data[x]
                        e_up_list[-1].bottom = low_data[x]
                        if len(e_up_list) > 1:
                            # 看是否有重叠区间
                            if e_up_list[-1].bottom <= e_up_list[-2].top and e_up_list[-1].top >= e_up_list[-2].bottom:
                                # 有重叠区间
                                e_up_list[-2].top = min(e_up_list[-1].top, e_up_list[-2].top)
                                e_up_list[-2].bottom = max(e_up_list[-1].bottom, e_up_list[-2].bottom)
                                e_up_list[-2].end = e_up_list[-1].end
                                e_up_list[-2].endTime = time_data[e_up_list[-2].end]
                                e_up_list[-2].formal = True
                                e_up_list.pop()
                for r in range(len(e_up_list)):
                    if e_up_list[r].formal:
                        e_list.append(e_up_list[r])
    return e_list


def la_hui(e_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series):
    result = {
        'buy_zs_huila': {
            'date': [],
            'data': []
        },
        'sell_zs_huila': {
            'date': [],
            'data': []
        }
    }
    for i in range(len(e_list)):
        e = e_list[i]
        e_next = e_list[i+1] if i+1 < len(e_list) else None
        if e.direction == 1:
            # 上涨中枢，找第一次的拉回
            e_end = e.end
            # 离开中枢后的第一个笔结束
            leave = pydash.index_of(bi_series, 1, e_end)
            if leave >= 0:
                r = -1
                for x in range(leave + 1, len(close_series)):
                    if close_series[x] < e.top:
                        r = x
                        break
                    if duan_series[x] == -1:
                        break
                    if e_next is not None and x >= e_next.end:
                        break
                if r >= 0:
                    result['sell_zs_huila']['date'].append(time_series[r])
                    result['sell_zs_huila']['data'].append(e.top)
        if e.direction == -1:
            # 下跌中枢，找第一次的拉回
            e_end = e.end
            leave = pydash.index_of(bi_series, -1, e_end)
            if leave >= 0:
                r = -1
                for x in range(leave + 1, len(close_series)):
                    if close_series[x] > e.bottom:
                        r = x
                        break
                    if duan_series[x] == -1:
                        break
                    if e_next is not None and x >= e_next.end:
                        break
                if r >= 0:
                    result['buy_zs_huila']['date'].append(time_series[r])
                    result['buy_zs_huila']['data'].append(e.bottom)
    return result