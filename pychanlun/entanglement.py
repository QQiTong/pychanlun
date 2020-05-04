# -*- coding: utf-8 -*-

import pydash

from pychanlun.basic.comm import FindPrevEq
from pychanlun.basic.pattern import perfect_buy_long, perfect_sell_short
from pychanlun.basic.pattern import buy_category, sell_category


class Entanglement:
    def __init__(self):
        self.start = 0
        self.end = 0
        self.startTime = 0
        self.endTime = 0
        # 中枢高
        self.top = 0
        # 中枢高
        self.zg = 0
        # 中枢低
        self.bottom = 0
        # 中枢低
        self.zd = 0
        # 中枢高高
        self.gg = 0
        # 中枢低低
        self.dd = 0
        self.direction = 0
        self.formal = False


def CalcEntanglements(time_serial, duan_serial, bi_serial, high_serial, low_serial):
    count = len(time_serial)
    e_list = []
    for i in range(count):
        if duan_serial[i] == -1:
            # i是线段低点
            j = FindPrevEq(duan_serial, 1, i)
            if j >= 0 and j < i:
                # j是线段高点
                e_down_list = []
                for x in range(j, i):
                    if bi_serial[x] == -1 and x < i:
                        e = Entanglement()
                        e.start = x
                        e.startTime = time_serial[x]
                        e.bottom = low_serial[x]
                        e.zd = low_serial[x]
                        e.dd = low_serial[x]
                        e.direction = -1
                        e_down_list.append(e)
                    if bi_serial[x] == 1 and len(e_down_list) > 0:
                        e_down_list[-1].end = x
                        e_down_list[-1].endTime = time_serial[x]
                        e_down_list[-1].top = high_serial[x]
                        e_down_list[-1].zg = high_serial[x]
                        e_down_list[-1].gg = high_serial[x]
                        if len(e_down_list) > 1:
                            # 看是否有重叠区间
                            if e_down_list[-1].top >= e_down_list[-2].bottom and e_down_list[-1].bottom <= e_down_list[
                                -2].top:
                                # 有重叠区间
                                if not e_down_list[-2].formal:
                                    e_down_list[-2].top = min(e_down_list[-1].top, e_down_list[-2].top)
                                    e_down_list[-2].zg = min(e_down_list[-1].zg, e_down_list[-2].zg)
                                    e_down_list[-2].gg = max(e_down_list[-1].gg, e_down_list[-2].gg)
                                    e_down_list[-2].bottom = max(e_down_list[-1].bottom, e_down_list[-2].bottom)
                                    e_down_list[-2].zd = max(e_down_list[-1].zd, e_down_list[-2].zd)
                                    e_down_list[-2].dd = min(e_down_list[-1].dd, e_down_list[-2].dd)
                                    e_down_list[-2].end = e_down_list[-1].end
                                    e_down_list[-2].endTime = time_serial[e_down_list[-2].end]
                                    e_down_list[-2].formal = True
                                else:
                                    e_down_list[-2].gg = max(e_down_list[-1].gg, e_down_list[-2].gg)
                                    e_down_list[-2].dd = min(e_down_list[-1].dd, e_down_list[-2].dd)
                                    e_down_list[-2].end = e_down_list[-1].end
                                    e_down_list[-2].endTime = time_serial[e_down_list[-2].end]
                                e_down_list.pop()
                for r in range(len(e_down_list)):
                    if e_down_list[r].formal:
                        e_list.append(e_down_list[r])
        if duan_serial[i] == 1:
            # i是线段高点
            j = FindPrevEq(duan_serial, -1, i)
            if j >= 0 and j < i:
                # j是线段低点
                e_up_list = []
                for x in range(j, i):
                    if bi_serial[x] == 1 and x < i:
                        e = Entanglement()
                        e.start = x
                        e.startTime = time_serial[x]
                        e.top = high_serial[x]
                        e.zg = high_serial[x]
                        e.gg = high_serial[x]
                        e.direction = 1
                        e_up_list.append(e)
                    if bi_serial[x] == -1 and len(e_up_list) > 0:
                        e_up_list[-1].end = x
                        e_up_list[-1].endTime = time_serial[x]
                        e_up_list[-1].bottom = low_serial[x]
                        e_up_list[-1].zd = low_serial[x]
                        e_up_list[-1].dd = low_serial[x]
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
                                    e_up_list[-2].endTime = time_serial[e_up_list[-2].end]
                                    e_up_list[-2].formal = True
                                else:
                                    e_up_list[-2].gg = max(e_up_list[-1].gg, e_up_list[-2].gg)
                                    e_up_list[-2].dd = min(e_up_list[-1].dd, e_up_list[-2].dd)
                                    e_up_list[-2].end = e_up_list[-1].end
                                    e_up_list[-2].endTime = time_serial[e_up_list[-2].end]
                                e_up_list.pop()
                for r in range(len(e_up_list)):
                    if e_up_list[r].formal:
                        e_list.append(e_up_list[r])
    return e_list


def la_hui(e_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series,
           higher_duan_series=None):
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
    for i in range(len(e_list)):
        e = e_list[i]
        e_next = e_list[i + 1] if i + 1 < len(e_list) else None
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
                if i < len(e_list) - 1:
                    k = e_list[i + 1].start
                for x in range(leave + 1, k):
                    if e_next is not None and x >= e_next.start:
                        break
                    if low_series[x] < e.top and (
                        len(pydash.chain(low_series[e.end + 1:x]).filter_(lambda a: a > e.top).value()) > 0 or
                        len(pydash.chain(high_series[e.end + 1:x]).filter_(lambda a: a > e.gg).value()) > 0):
                        r = x
                        break
                    if duan_series[x] == -1:
                        break
                if r >= 0:
                    tags = []
                    result['sell_zs_huila']['idx'].append(r)
                    result['sell_zs_huila']['date'].append(time_series[r])
                    result['sell_zs_huila']['data'].append(e.top)
                    top_index = pydash.find_last_index(duan_series[:r + 1], lambda a: a == 1)
                    if top_index > -1:
                        result['sell_zs_huila']['stop_lose_price'].append(high_series[top_index])
                        stop_win_price = e.top - (high_series[top_index] - e.top)
                        result['sell_zs_huila']['stop_win_price'].append(stop_win_price)
                    else:
                        result['sell_zs_huila']['stop_lose_price'].append(0)
                        result['sell_zs_huila']['stop_win_price'].append(0)

                    if perfect_sell_short(duan_series, high_series, low_series, r):
                        tags.append('完备卖')
                    if higher_duan_series is not None:
                        category = sell_category(higher_duan_series, duan_series, high_series, low_series, r)
                        if len(category) > 0:
                            if category not in tags:
                                tags.append(category)
                    result['sell_zs_huila']['tag'].append(','.join(tags))
        if e.direction == -1:
            # 下跌中枢，找第一次的拉回
            leave = e.end
            for x in range(e.end + 1, len(low_series)):
                if low_series[x] < e.zd and bi_series[x] == -1:
                    leave = x
                    break
                if duan_series[x] == 1:
                    break
            if leave - e.end >= 5:
                r = -1
                for x in range(leave + 1, len(high_series)):
                    if e_next is not None and x >= e_next.start:
                        break
                    if high_series[x] > e.bottom and (
                        len(pydash.chain(high_series[e.end + 1:x]).filter_(lambda a: a < e.bottom).value()) > 0 or
                        len(pydash.chain(low_series[e.end + 1:x]).filter_(lambda a: a < e.dd).value()) > 0):
                        r = x
                        break
                    if duan_series[x] == 1:
                        break
                if r >= 0:
                    tags = []
                    result['buy_zs_huila']['idx'].append(r)
                    result['buy_zs_huila']['date'].append(time_series[r])
                    result['buy_zs_huila']['data'].append(e.bottom)
                    bottom_index = pydash.find_last_index(duan_series[:r + 1], lambda a: a == -1)
                    if bottom_index > -1:
                        result['buy_zs_huila']['stop_lose_price'].append(low_series[bottom_index])
                        stop_win_price = e.bottom + (e.bottom - low_series[bottom_index])
                        result['buy_zs_huila']['stop_win_price'].append(stop_win_price)
                    else:
                        result['buy_zs_huila']['stop_lose_price'].append(0)
                        result['buy_zs_huila']['stop_win_price'].append(0)
                    if perfect_buy_long(duan_series, high_series, low_series, r):
                        tags.append('完备买')
                    if higher_duan_series is not None:
                        category = buy_category(higher_duan_series, duan_series, high_series, low_series, r)
                        if len(category) > 0:
                            if category not in tags:
                                tags.append(category)
                    result['buy_zs_huila']['tag'].append(','.join(tags))
    return result


def tu_po(e_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series,
          higher_duan_series=None):
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
    for i in range(len(e_list)):
        e = e_list[i]
        e_next = e_list[i + 1] if i + 1 < len(e_list) else None
        if e.direction == 1:
            r = -1
            for x in range(e.end + 1, len(high_series)):
                if high_series[x] > e.gg:
                    r = x
                    break
                if duan_series[x] == 1:
                    break
            if r > 0:
                tags = []
                result['buy_zs_tupo']['idx'].append(r)
                result['buy_zs_tupo']['date'].append(time_series[r])
                result['buy_zs_tupo']['data'].append(e.gg)
                result['buy_zs_tupo']['stop_lose_price'].append(e.zg)
                if perfect_buy_long(duan_series, high_series, low_series, r):
                    tags.append('完备买')
                if higher_duan_series is not None:
                    category = buy_category(higher_duan_series, duan_series, high_series, low_series, r)
                    if len(category) > 0:
                        if category not in tags:
                            tags.append(category)
                result['buy_zs_tupo']['tag'].append(','.join(tags))
        if e.direction == -1:
            r = -1
            for x in range(e.end + 1, len(low_series)):
                if low_series[x] < e.dd:
                    r = x
                    break
                if duan_series[x] == -1:
                    break
            if r > 0:
                tags = []
                result['sell_zs_tupo']['idx'].append(r)
                result['sell_zs_tupo']['date'].append(time_series[r])
                result['sell_zs_tupo']['data'].append(e.dd)
                result['sell_zs_tupo']['stop_lose_price'].append(e.zd)
                if perfect_sell_short(duan_series, high_series, low_series, r):
                    tags.append('完备卖')
                if higher_duan_series is not None:
                    category = sell_category(higher_duan_series, duan_series, high_series, low_series, r)
                    if len(category) > 0:
                        if category not in tags:
                            tags.append(category)
                result['sell_zs_tupo']['tag'].append(','.join(tags))
    return result


def five_v_fan(time_series, duan_series, bi_series, high_series, low_series, higher_duan_series):
    result = {
        'sell_five_v_reverse': {
            'idx': [],
            'date': [],
            'data': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': []
        },
        'buy_five_v_reverse': {
            'idx': [],
            'date': [],
            'data': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': []
        }
    }
    for i in range(len(bi_series)):
        if bi_series[i] == 1:
            g1 = i
            d1 = pydash.find_last_index(bi_series[:g1], lambda x: x == -1)
            g2 = pydash.find_last_index(bi_series[:d1], lambda x: x == 1)
            d2 = pydash.find_last_index(bi_series[:g2], lambda x: x == -1)
            g3 = pydash.find_last_index(bi_series[:d2], lambda x: x == 1)
            d3 = pydash.find_last_index(bi_series[:g3], lambda x: x == -1)
            if d3 >= 0 and high_series[g1] > high_series[g2] > high_series[g3] and \
                    low_series[d1] > low_series[d2] > low_series[d3] and low_series[d1] > high_series[g3]:
                for k in range(i + 1, len(bi_series)):
                    if low_series[k] < low_series[d1]:
                        # v fan
                        tags = []
                        if pydash.find_last_index(result['sell_five_v_reverse']['date'], lambda x: x == time_series[k]) == -1:
                            result['sell_five_v_reverse']['idx'].append(k)
                            result['sell_five_v_reverse']['date'].append(time_series[k])
                            result['sell_five_v_reverse']['data'].append(low_series[d1])
                            result['sell_five_v_reverse']['stop_lose_price'].append(high_series[g1])
                            if perfect_sell_short(duan_series, high_series, low_series, k):
                                tags.append('完备卖')
                            if higher_duan_series is not None:
                                category = sell_category(higher_duan_series, duan_series, high_series, low_series, k)
                                if len(category) > 0:
                                    if category not in tags:
                                        tags.append(category)
                            result['sell_five_v_reverse']['tag'].append(','.join(tags))
                        break
                    if bi_series[k] == -1:
                        break

        elif bi_series[i] == -1:
            d1 = i
            g1 = pydash.find_last_index(bi_series[:d1], lambda x: x == 1)
            d2 = pydash.find_last_index(bi_series[:g1], lambda x: x == -1)
            g2 = pydash.find_last_index(bi_series[:d2], lambda x: x == 1)
            d3 = pydash.find_last_index(bi_series[:g2], lambda x: x == -1)
            g3 = pydash.find_last_index(bi_series[:d3], lambda x: x == 1)
            if g3 >= 0 and high_series[g1] < high_series[g2] < high_series[g3] and \
                    low_series[d1] < low_series[d2] < low_series[d3] and high_series[g1] < low_series[d3]:
                for k in range(i + 1, len(bi_series)):
                    if high_series[k] > high_series[g1]:
                        # v fan
                        tags = []
                        if pydash.find_last_index(result['buy_five_v_reverse']['date'], lambda x: x == time_series[k]) == -1:
                            result['buy_five_v_reverse']['idx'].append(k)
                            result['buy_five_v_reverse']['date'].append(time_series[k])
                            result['buy_five_v_reverse']['data'].append(high_series[g1])
                            result['buy_five_v_reverse']['stop_lose_price'].append(low_series[d1])
                            if perfect_buy_long(duan_series, high_series, low_series, k):
                                tags.append('完备买')
                            if higher_duan_series is not None:
                                category = buy_category(higher_duan_series, duan_series, high_series, low_series, k)
                                if len(category) > 0:
                                    if category not in tags:
                                        tags.append(category)
                            result['buy_five_v_reverse']['tag'].append(','.join(tags))
                        break
                    if bi_series[k] == -1:
                        break
    return result


def v_reverse(e_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series,
              higher_duan_series=None):
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
    count = len(time_series)
    for i in range(len(e_list)):
        e = e_list[i]
        next_e = e_list[i+1] if i < len(e_list) - 1 else None
        if e.direction == 1:
            # 离开中枢后的第一段结束
            leave_end_index = -1
            for x in range(e.end+1, count):
                if duan_series == 1:
                    leave_end_index = x
                    break
                if next_e is not None and x >= e.start:
                    break
            if leave_end_index >= 0:
                # 存在强3买
                buy3 = False
                resist_index = -1
                resist_price = 0
                for j in range(e.end + 1, leave_end_index):
                    if bi_series[j] == -1 and low_series[j] > e.gg:
                        buy3 = True
                        resist_index = j
                        resist_price = low_series[resist_index]
                        break
                if buy3:
                    for k in range(leave_end_index + 1, len(low_series)):
                        if bi_series[k] == -1:
                            break
                        if low_series[k] < resist_price:
                            tags = []
                            if pydash.find_last_index(result['sell_v_reverse']['date'],
                                                      lambda x: x == time_series[k]) == -1:
                                result['sell_v_reverse']['idx'].append(k)
                                result['sell_v_reverse']['date'].append(time_series[k])
                                result['sell_v_reverse']['data'].append(resist_price)
                                result['sell_v_reverse']['stop_lose_price'].append(high_series[leave_end_index])
                                if perfect_sell_short(duan_series, high_series, low_series, k):
                                    tags.append('完备卖')
                                if higher_duan_series is not None:
                                    category = sell_category(higher_duan_series, duan_series, high_series, low_series,
                                                             k)
                                    if len(category) > 0:
                                        if category not in tags:
                                            tags.append(category)
                                result['sell_v_reverse']['tag'].append(','.join(tags))
                            break
        if e.direction == -1:
            # 离开中枢后的第一段结束
            leave_end_index = -1
            for x in range(e.end+1, count):
                if duan_series == -1:
                    leave_end_index = x
                    break
                if next_e is not None and x >= e.start:
                    break
            if leave_end_index >= 0:
                # 存在3卖
                sell3 = False
                resist_index = -1
                resist_price = 0
                for j in range(e.end + 1, leave_end_index):
                    if bi_series[j] == 1 and high_series[j] > e.dd:
                        sell3 = True
                        resist_index = j
                        resist_price = high_series[resist_index]
                        break
                if sell3:
                    for k in range(leave_end_index + 1, len(high_series)):
                        if bi_series[k] == 1:
                            break
                        if high_series[k] > resist_price:
                            tags = []
                            if pydash.find_last_index(result['buy_v_reverse']['date'],
                                                      lambda x: x == time_series[k]) == -1:
                                result['buy_v_reverse']['idx'].append(k)
                                result['buy_v_reverse']['date'].append(time_series[k])
                                result['buy_v_reverse']['data'].append(resist_price)
                                result['buy_v_reverse']['stop_lose_price'].append(low_series[leave_end_index])
                                if perfect_buy_long(duan_series, high_series, low_series, k):
                                    tags.append('完备买')
                                if higher_duan_series is not None:
                                    category = buy_category(higher_duan_series, duan_series, high_series, low_series, k)
                                    if len(category) > 0:
                                        if category not in tags:
                                            tags.append(category)
                                result['buy_v_reverse']['tag'].append(','.join(tags))
                            break
    return result


def po_huai(time_series, high_series, low_series, open_series, close_series, bi_series, duan_series,
            higher_duan_series=None):
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
                        tags = []
                        result['sell_duan_break']['idx'].append(k)
                        result['sell_duan_break']['date'].append(time_series[k])
                        result['sell_duan_break']['data'].append(low_series[anchor])
                        result['sell_duan_break']['stop_lose_price'].append(high_series[i])
                        if perfect_sell_short(duan_series, high_series, low_series, k):
                            tags.append('完备卖')
                        if higher_duan_series is not None:
                            category = sell_category(higher_duan_series, duan_series, high_series, low_series,
                                                     k)
                            if len(category) > 0:
                                if category not in tags:
                                    tags.append(category)
                        result['sell_duan_break']['tag'].append(','.join(tags))
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
                        tags = []
                        result['buy_duan_break']['idx'].append(k)
                        result['buy_duan_break']['date'].append(time_series[k])
                        result['buy_duan_break']['data'].append(high_series[anchor])
                        result['buy_duan_break']['stop_lose_price'].append(low_series[i])
                        if perfect_buy_long(duan_series, high_series, low_series, k):
                            tags.append('完备买')
                        if higher_duan_series is not None:
                            category = buy_category(higher_duan_series, duan_series, high_series, low_series, k)
                            if len(category) > 0:
                                if category not in tags:
                                    tags.append(category)
                        result['buy_duan_break']['tag'].append(','.join(tags))
                        break
    return result
