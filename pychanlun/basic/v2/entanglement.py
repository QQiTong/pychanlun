# -*- coding: utf-8 -*-

import pydash

from pychanlun.funcat.time_series import (fit_series)
from pychanlun import series_tool
from pychanlun.basic.comm import FindPrevEq
from pychanlun.basic.pattern import PerfectForBuyLong, PerfectForSellShort

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


def find_entanglements(time_series, duan_series, bi_series, high_series, low_series):
    count = len(time_series)
    entanglements = []
    for i in range(count):
        if duan_series[i] == -1:
            # i是线段低点
            j = FindPrevEq(duan_series, 1, i)
            if j >= 0 and j < i:
                # j是线段高点
                e_down_list = []
                for x in range(j, i):
                    if bi_series[x] == -1 and x < i:
                        e = Entanglement()
                        e.start = x
                        e.startTime = time_series[x]
                        e.bottom = low_series[x]
                        e.zd = low_series[x]
                        e.dd = low_series[x]
                        e.direction = -1
                        e_down_list.append(e)
                    if bi_series[x] == 1 and len(e_down_list) > 0:
                        e_down_list[-1].end = x
                        e_down_list[-1].endTime = time_series[x]
                        e_down_list[-1].top = high_series[x]
                        e_down_list[-1].zg = high_series[x]
                        e_down_list[-1].gg = high_series[x]
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
                                    e_down_list[-2].endTime = time_series[e_down_list[-2].end]
                                    e_down_list[-2].formal = True
                                else:
                                    e_down_list[-2].gg = max(e_down_list[-1].gg, e_down_list[-2].gg)
                                    e_down_list[-2].dd = min(e_down_list[-1].dd, e_down_list[-2].dd)
                                    e_down_list[-2].end = e_down_list[-1].end
                                    e_down_list[-2].endTime = time_series[e_down_list[-2].end]
                                e_down_list.pop()
                for r in range(len(e_down_list)):
                    if e_down_list[r].formal:
                        entanglements.append(e_down_list[r])
        if duan_series[i] == 1:
            # i是线段高点
            j = FindPrevEq(duan_series, -1, i)
            if j >= 0 and j < i:
                # j是线段低点
                e_up_list = []
                for x in range(j, i):
                    if bi_series[x] == 1 and x < i:
                        e = Entanglement()
                        e.start = x
                        e.startTime = time_series[x]
                        e.top = high_series[x]
                        e.zg = high_series[x]
                        e.gg = high_series[x]
                        e.direction = 1
                        e_up_list.append(e)
                    if bi_series[x] == -1 and len(e_up_list) > 0:
                        e_up_list[-1].end = x
                        e_up_list[-1].endTime = time_series[x]
                        e_up_list[-1].bottom = low_series[x]
                        e_up_list[-1].zd = low_series[x]
                        e_up_list[-1].dd = low_series[x]
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
                                    e_up_list[-2].endTime = time_series[e_up_list[-2].end]
                                    e_up_list[-2].formal = True
                                else:
                                    e_up_list[-2].gg = max(e_up_list[-1].gg, e_up_list[-2].gg)
                                    e_up_list[-2].dd = min(e_up_list[-1].dd, e_up_list[-2].dd)
                                    e_up_list[-2].end = e_up_list[-1].end
                                    e_up_list[-2].endTime = time_series[e_up_list[-2].end]
                                e_up_list.pop()
                for r in range(len(e_up_list)):
                    if e_up_list[r].formal:
                        entanglements.append(e_up_list[r])
    return entanglements


def la_hui(klines, entanglements):
    time_series = klines['timestamp']
    high_series = klines['high']
    low_series = klines['low']
    open_series = klines['open']
    close_series = klines['close']
    bi_series = klines['bi']
    duan_series = klines['duan']
    result = {
        'buy_zs_huila': {
            'idx': [],
            'date': [],
            'data': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': []
        },
        'sell_zs_huila': {
            'idx': [],
            'date': [],
            'data': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': []
        }
    }
    for i in range(len(entanglements)):
        e = entanglements[i]
        e_next = entanglements[i+1] if i+1 < len(entanglements) else None
        if e.direction == 1:
            # 上涨中枢，找第一次的拉回
            # 离开中枢后的第一个笔结束
            leave = e.end
            for x in range(e.end + 1, len(high_series)):
                if high_series[x] > e.zg and bi_series[x] == 1:
                    leave = x
                    break
                if duan_series[x] == -1:
                    break
            if leave - e.end >= 5:
                r = -1
                k = len(low_series)
                if i < len(entanglements) - 1:
                    k = entanglements[i+1].start
                for x in range(leave + 1, k):
                    if e_next is not None and x >= e_next.start:
                        break
                    if low_series[x] < e.top and (
                            len(pydash.chain(low_series[e.end+1:x]).filter_(lambda a: a > e.top).value()) > 0 or
                            len(pydash.chain(high_series[e.end+1:x]).filter_(lambda a: a > e.gg).value()) > 0):
                        r = x
                        break
                    if duan_series[x] == -1:
                        break
                if r >= 0:
                    result['sell_zs_huila']['idx'].append(r)
                    result['sell_zs_huila']['date'].append(time_series[r])
                    result['sell_zs_huila']['data'].append(e.top)
                    top_index = pydash.find_last_index(duan_series[:r+1], lambda a: a == 1)
                    if top_index > -1:
                        result['sell_zs_huila']['stop_lose_price'].append(high_series[top_index])
                        stop_win_price = e.top - (high_series[top_index] - e.top)
                        result['sell_zs_huila']['stop_win_price'].append(stop_win_price)
                    else:
                        result['sell_zs_huila']['stop_lose_price'].append(0)
                        result['sell_zs_huila']['stop_win_price'].append(0)

                    if PerfectForSellShort(duan_series, high_series, low_series, r):
                        result['sell_zs_huila']['tag'].append('完备')
                    else:
                        result['sell_zs_huila']['tag'].append('')
        if e.direction == -1:
            # 下跌中枢，找第一次的拉回
            leave = e.end
            for x in range(e.end + 1, len(low_series)):
                if low_series[x] < e.zd and bi_series[x] == -1:
                    leave = x
                    break
                if duan_series[x] == 1:
                    break
            if leave - e.end >= 5 :
                r = -1
                for x in range(leave + 1, len(high_series)):
                    if e_next is not None and x >= e_next.start:
                        break
                    if high_series[x] > e.bottom and (
                            len(pydash.chain(high_series[e.end+1:x]).filter_(lambda a: a < e.bottom).value()) > 0 or
                            len(pydash.chain(low_series[e.end+1:x]).filter_(lambda a: a < e.dd).value()) > 0):
                        r = x
                        break
                    if duan_series[x] == 1:
                        break
                if r >= 0:
                    result['buy_zs_huila']['idx'].append(r)
                    result['buy_zs_huila']['date'].append(time_series[r])
                    result['buy_zs_huila']['data'].append(e.bottom)
                    bottom_index = pydash.find_last_index(duan_series[:r+1], lambda a: a == -1)
                    if bottom_index > -1:
                        result['buy_zs_huila']['stop_lose_price'].append(low_series[bottom_index])
                        stop_win_price = e.bottom + (e.bottom - low_series[bottom_index])
                        result['buy_zs_huila']['stop_win_price'].append(stop_win_price)
                    else:
                        result['buy_zs_huila']['stop_lose_price'].append(0)
                        result['buy_zs_huila']['stop_win_price'].append(0)

                    if PerfectForBuyLong(duan_series, high_series, low_series, r):
                        result['buy_zs_huila']['tag'].append('完备')
                    else:
                        result['buy_zs_huila']['tag'].append('')
    return result


def tu_po(klines, entanglements):
    time_series = klines['timestamp']
    high_series = klines['high']
    low_series = klines['low']
    open_series = klines['open']
    close_series = klines['close']
    bi_series = klines['bi']
    duan_series = klines['duan']
    result = {
        'buy_zs_tupo': {
            'idx': [],
            'date': [],
            'data': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': []
        },
        'sell_zs_tupo': {
            'idx': [],
            'date': [],
            'data': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': []
        }
    }
    for i in range(len(entanglements)):
        e = entanglements[i]
        e_next = entanglements[i+1] if i+1 < len(entanglements) else None
        if e.direction == 1:
            r = -1
            for x in range(e.end+1, len(high_series)):
                if high_series[x] > e.gg:
                    r = x
                    break
                if duan_series[x] == 1:
                    break
            if r > 0:
                result['buy_zs_tupo']['idx'].append(r)
                result['buy_zs_tupo']['date'].append(time_series[r])
                result['buy_zs_tupo']['data'].append(e.gg)
                result['buy_zs_tupo']['stop_lose_price'].append(e.zg)
                if PerfectForBuyLong(duan_series, high_series, low_series, r):
                    result['buy_zs_tupo']['tag'].append('完备')
                else:
                    result['buy_zs_tupo']['tag'].append('')
        if e.direction == -1:
            r = -1
            for x in range(e.end+1, len(low_series)):
                if low_series[x] < e.dd:
                    r = x
                    break
                if duan_series[x] == -1:
                    break
            if r > 0:
                result['sell_zs_tupo']['idx'].append(r)
                result['sell_zs_tupo']['date'].append(time_series[r])
                result['sell_zs_tupo']['data'].append(e.dd)
                result['sell_zs_tupo']['stop_lose_price'].append(e.zd)
                if PerfectForSellShort(duan_series, high_series, low_series, r):
                    result['sell_zs_tupo']['tag'].append('完备')
                else:
                    result['sell_zs_tupo']['tag'].append('')
    return result

def v_reverse(klines, entanglements):
    time_series = klines['timestamp']
    high_series = klines['high']
    low_series = klines['low']
    open_series = klines['open']
    close_series = klines['close']
    bi_series = klines['bi']
    duan_series = klines['duan']
    result = {
        'buy_v_reverse': {
            'idx': [],
            'date': [],
            'data': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': []
        },
        'sell_v_reverse': {
            'idx': [],
            'date': [],
            'data': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': []
        }
    }
    for i in range(len(entanglements)):
        e = entanglements[i]
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
                    for k in range(leave_end_index+1, len(low_series)):
                        if bi_series[k] == -1:
                            break
                        if low_series[k] < resist_price:
                            if pydash.find_last_index(result['sell_v_reverse']['date'], lambda x: x == time_series[k]) == -1:
                                result['sell_v_reverse']['idx'].append(k)
                                result['sell_v_reverse']['date'].append(time_series[k])
                                result['sell_v_reverse']['data'].append(resist_price)
                                result['sell_v_reverse']['stop_lose_price'].append(high_series[leave_end_index])
                                if PerfectForSellShort(duan_series, high_series, low_series, k):
                                    result['sell_v_reverse']['tag'].append('完备')
                                else:
                                    result['sell_v_reverse']['tag'].append('')
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
                    for k in range(leave_end_index+1, len(high_series)):
                        if bi_series[k] == 1:
                            break
                        if high_series[k] > resist_price:
                            if pydash.find_last_index(result['buy_v_reverse']['date'], lambda x: x == time_series[k]) == -1:
                                result['buy_v_reverse']['idx'].append(k)
                                result['buy_v_reverse']['date'].append(time_series[k])
                                result['buy_v_reverse']['data'].append(resist_price)
                                result['buy_v_reverse']['stop_lose_price'].append(low_series[leave_end_index])
                                if PerfectForBuyLong(duan_series, high_series, low_series, k):
                                    result['buy_v_reverse']['tag'].append('完备')
                                else:
                                    result['buy_v_reverse']['tag'].append('')
                            break

    return result


def po_huai(klines):
    time_series = klines['timestamp']
    high_series = klines['high']
    low_series = klines['low']
    open_series = klines['open']
    close_series = klines['close']
    bi_series = klines['bi']
    duan_series = klines['duan']
    result = {
        'buy_duan_break': {
            'idx': [],
            'date': [],
            'data': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': []
        },
        'sell_duan_break': {
            'idx': [],
            'date': [],
            'data': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': []
        }
    }
    for i in range(len(duan_series)):
        if duan_series[i] == 1:
            anchor = 0
            for j in range(i + 1, len(time_series)):
                if duan_series[j] == -1:
                    break
                if bi_series[j] == -1:
                     anchor = j
                     break
            if anchor > 0:
                for k in range(anchor + 1, len(time_series)):
                    if duan_series[k] == -1:
                        break
                    if low_series[k] < low_series[anchor]:
                        result['sell_duan_break']['idx'].append(k)
                        result['sell_duan_break']['date'].append(time_series[k])
                        result['sell_duan_break']['data'].append(low_series[anchor])
                        result['sell_duan_break']['stop_lose_price'].append(high_series[i])
                        if PerfectForSellShort(duan_series, high_series, low_series, k):
                            result['sell_duan_break']['tag'].append('完备')
                        else:
                            result['sell_duan_break']['tag'].append('')
                        break
        elif duan_series[i] == -1:
            anchor = 0
            for j in range(i + 1, len(time_series)):
                if duan_series[j] == 1:
                    break
                if bi_series[j] == 1:
                     anchor = j
                     break
            if anchor > 0:
                for k in range(anchor + 1, len(time_series)):
                    if duan_series[k] == 1:
                        break
                    if high_series[k] > high_series[anchor]:
                        result['buy_duan_break']['idx'].append(k)
                        result['buy_duan_break']['date'].append(time_series[k])
                        result['buy_duan_break']['data'].append(high_series[anchor])
                        result['buy_duan_break']['stop_lose_price'].append(low_series[i])
                        if PerfectForBuyLong(duan_series, high_series, low_series, k):
                            result['buy_duan_break']['tag'].append('完备')
                        else:
                            result['buy_duan_break']['tag'].append('')
                        break
    return result
