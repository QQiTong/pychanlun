# -*- coding: utf-8 -*-

import pydash


def la_hui(e_list, datetime_list, time_str_array, high_array, low_array, bi_array, duan_array,second_chance):
    count = len(time_str_array)
    result = {
        'signal_array': [0 for i in range(count)],
        'buy_zs_huila': {
            'idx': [],
            'date': [],
            'datetime': [],
            'time_str': [],
            'data': [],
            'price': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': [],
            'above_ma5': [],
            'above_ma20': [],
        },
        'sell_zs_huila': {
            'idx': [],
            'date': [],
            'datetime': [],
            'time_str': [],
            'data': [],
            'price': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': [],
            'above_ma5': [],
            'above_ma20': []
        }
    }
    for i in range(len(e_list)):
        e = e_list[i]
        e_next = e_list[i + 1] if i + 1 < len(e_list) else None
        if e.direction == 1:
            # 上涨中枢，找第一次的拉回
            # 离开中枢后的第一个笔结束
            leave = e.end
            for x in range(e.end + 1, len(high_array)):
                if high_array[x] > e.zg and bi_array[x] == 1:
                    leave = x
                    break
                if duan_array[x] == -1:
                    break
            if leave - e.end >= 5:
                r = -1
                k = len(low_array)
                if i < len(e_list) - 1:
                    k = e_list[i + 1].start
                for x in range(leave + 1, k):
                    if e_next is not None and x >= e_next.start:
                        break
                    # if low_array[x] < e.top and (len(pydash.chain(low_array[e.end + 1:x]).filter_(lambda a: a > e.top).value()) > 0 or \
                    #     len(pydash.chain(high_array[e.end + 1:x]).filter_(lambda a: a > e.gg).value()) > 0):
                    if low_array[x] < e.gg and (len(pydash.chain(low_array[e.end + 1:x]).filter_(lambda a: a > e.gg).value()) > 0 or \
                        len(pydash.chain(high_array[e.end + 1:x]).filter_(lambda a: a > e.gg).value()) > 0):
                        r = x
                        break
                    if duan_array[x] == -1:
                        break
                if r >= 0:
                    tags = []
                    result['signal_array'][r] = -1
                    result['sell_zs_huila']['idx'].append(r)
                    result['sell_zs_huila']['date'].append(time_str_array[r])
                    result['sell_zs_huila']['datetime'].append(datetime_list[r])
                    result['sell_zs_huila']['time_str'].append(time_str_array[r])
                    result['sell_zs_huila']['data'].append(e.gg)
                    result['sell_zs_huila']['price'].append(e.gg)
                    top_index = pydash.find_last_index(duan_array[:r + 1], lambda a: a == 1)
                    if top_index > -1:
                        result['sell_zs_huila']['stop_lose_price'].append(high_array[top_index])
                        stop_win_price = e.top - (high_array[top_index] - e.top)
                        result['sell_zs_huila']['stop_win_price'].append(stop_win_price)
                    else:
                        result['sell_zs_huila']['stop_lose_price'].append(0)
                        result['sell_zs_huila']['stop_win_price'].append(0)
                    result['sell_zs_huila']['tag'].append(','.join(tags))
                    if top_index >= 0 and second_chance == 1:
                        for k in range(r + 6, len(datetime_list) - 2):
                            if high_array[k] > high_array[top_index] or duan_array[k] == -1:
                                break
                            if high_array[k] < high_array[k-2] and high_array[k-1] < high_array[k-2] and low_array[k] > (e.top+high_array[top_index])/2:
                                result['signal_array'][k] = -1
                                result['sell_zs_huila']['idx'].append(k)
                                result['sell_zs_huila']['date'].append(time_str_array[k])
                                result['sell_zs_huila']['datetime'].append(datetime_list[k])
                                result['sell_zs_huila']['time_str'].append(time_str_array[k])
                                result['sell_zs_huila']['data'].append(low_array[k])
                                result['sell_zs_huila']['price'].append(low_array[k])
                                if top_index > -1:
                                    result['sell_zs_huila']['stop_lose_price'].append(high_array[top_index])
                                    stop_win_price = e.top - (high_array[top_index] - e.top)
                                    result['sell_zs_huila']['stop_win_price'].append(stop_win_price)
                                else:
                                    result['sell_zs_huila']['stop_lose_price'].append(0)
                                    result['sell_zs_huila']['stop_win_price'].append(0)
                                result['sell_zs_huila']['tag'].append(','.join(tags))
                                break
        if e.direction == -1:
            # 下跌中枢，找第一次的拉回
            leave = e.end
            for x in range(e.end + 1, len(low_array)):
                if low_array[x] < e.zd and bi_array[x] == -1:
                    leave = x
                    break
                if duan_array[x] == 1:
                    break
            if leave - e.end >= 5:
                r = -1
                for x in range(leave + 1, len(high_array)):
                    if e_next is not None and x >= e_next.start:
                        break
                    # if high_array[x] > e.bottom and (len(pydash.chain(high_array[e.end + 1:x]).filter_(lambda a: a < e.bottom).value()) > 0 or \
                    #     len(pydash.chain(low_array[e.end + 1:x]).filter_(lambda a: a < e.dd).value()) > 0):
                    if high_array[x] > e.dd and (
                        len(pydash.chain(high_array[e.end + 1:x]).filter_(lambda a: a < e.dd).value()) > 0 or \
                        len(pydash.chain(low_array[e.end + 1:x]).filter_(lambda a: a < e.dd).value()) > 0):
                        r = x
                        break
                    if duan_array[x] == 1:
                        break
                if r >= 0:
                    tags = []
                    result['signal_array'][r] = 1
                    result['buy_zs_huila']['idx'].append(r)
                    result['buy_zs_huila']['date'].append(time_str_array[r])
                    result['buy_zs_huila']['datetime'].append(datetime_list[r])
                    result['buy_zs_huila']['time_str'].append(time_str_array[r])
                    result['buy_zs_huila']['data'].append(e.dd)
                    result['buy_zs_huila']['price'].append(e.dd)
                    bottom_index = pydash.find_last_index(duan_array[:r + 1], lambda a: a == -1)
                    if bottom_index > -1:
                        result['buy_zs_huila']['stop_lose_price'].append(low_array[bottom_index])
                        stop_win_price = e.bottom + (e.bottom - low_array[bottom_index])
                        result['buy_zs_huila']['stop_win_price'].append(stop_win_price)
                    else:
                        result['buy_zs_huila']['stop_lose_price'].append(0)
                        result['buy_zs_huila']['stop_win_price'].append(0)
                    result['buy_zs_huila']['tag'].append(','.join(tags))

                    if bottom_index >= 0 and second_chance == 1:
                        for k in range(r + 6, len(datetime_list) - 2):
                            if low_array[k] < low_array[bottom_index] or duan_array[k] == 1:
                                break
                            if low_array[k] > low_array[k-2] and low_array[k-1] > low_array[k-2] and high_array[k] < (e.bottom+low_array[bottom_index])/2:
                                result['signal_array'][k] = 1
                                result['buy_zs_huila']['idx'].append(k)
                                result['buy_zs_huila']['date'].append(time_str_array[k])
                                result['buy_zs_huila']['datetime'].append(datetime_list[k])
                                result['buy_zs_huila']['time_str'].append(time_str_array[k])
                                result['buy_zs_huila']['data'].append(high_array[k])
                                result['buy_zs_huila']['price'].append(high_array[k])
                                if bottom_index > -1:
                                    result['buy_zs_huila']['stop_lose_price'].append(low_array[bottom_index])
                                    stop_win_price = e.bottom + (e.bottom - low_array[bottom_index])
                                    result['buy_zs_huila']['stop_win_price'].append(stop_win_price)
                                else:
                                    result['buy_zs_huila']['stop_lose_price'].append(0)
                                    result['buy_zs_huila']['stop_win_price'].append(0)
                                result['buy_zs_huila']['tag'].append(','.join(tags))
                                break
    return result


def tu_po(e_list, datetime_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series,second_chance):
    result = {
        'buy_zs_tupo': {
            'idx': [],
            'date': [],
            'datetime': [],
            'time_str': [],
            'data': [],
            'price': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': [],
            'above_ma5': [],
            'above_ma20': []
        },
        'sell_zs_tupo': {
            'idx': [],
            'date': [],
            'datetime': [],
            'time_str': [],
            'data': [],
            'price': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': [],
            'above_ma5': [],
            'above_ma20': []
        }
    }
    for i in range(len(e_list)):
        e = e_list[i]
        e_pre = e_list[i - 1] if i > 0 else None
        if e.direction == 1:
            duan_start = pydash.find_last_index(duan_series[:e.start], lambda t: t == -1)
            if duan_start >= 0:
                pre_duan_start = pydash.find_last_index(duan_series[:duan_start], lambda t: t == 1)
                if pre_duan_start >= 0:
                    middle_price = (high_series[pre_duan_start] + low_series[duan_start]) / 2
                    if e.gg > middle_price:
                        continue
            if e_pre is not None and 0 <= duan_start < e_pre.start:
                continue
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
                result['buy_zs_tupo']['datetime'].append(datetime_list[r])
                result['buy_zs_tupo']['time_str'].append(time_series[r])
                result['buy_zs_tupo']['data'].append(e.gg)
                result['buy_zs_tupo']['price'].append(e.gg)
                result['buy_zs_tupo']['stop_lose_price'].append(e.zg)
                result['buy_zs_tupo']['tag'].append(','.join(tags))

                if second_chance == 1:
                    for kk in range(r + 6, len(time_series)):
                        if low_series[kk] < e.zg or duan_series[kk] == -1:
                            break
                        if low_series[kk] > low_series[kk-2] and low_series[kk-1] > low_series[kk-2] and high_series[kk] < (e.zg+e.gg)/2:
                            result['buy_zs_tupo']['idx'].append(kk)
                            result['buy_zs_tupo']['date'].append(time_series[kk])
                            result['buy_zs_tupo']['datetime'].append(datetime_list[kk])
                            result['buy_zs_tupo']['time_str'].append(time_series[kk])
                            result['buy_zs_tupo']['data'].append(high_series[kk])
                            result['buy_zs_tupo']['price'].append(high_series[kk])
                            result['buy_zs_tupo']['stop_lose_price'].append(e.zg)
                            result['buy_zs_tupo']['tag'].append(','.join(tags))
                            break

        if e.direction == -1:
            duan_start = pydash.find_last_index(duan_series[:e.start], lambda t: t == 1)
            if duan_start >= 0:
                pre_duan_start = pydash.find_last_index(duan_series[:duan_start], lambda t: t == -1)
                if pre_duan_start >= 0:
                    middle_price = (low_series[pre_duan_start] + high_series[duan_start]) / 2
                    if e.gg < middle_price:
                        continue
            if e_pre is not None and 0 <= duan_start < e_pre.start:
                continue
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
                result['sell_zs_tupo']['datetime'].append(datetime_list[r])
                result['sell_zs_tupo']['time_str'].append(time_series[r])
                result['sell_zs_tupo']['data'].append(e.dd)
                result['sell_zs_tupo']['price'].append(e.dd)
                result['sell_zs_tupo']['stop_lose_price'].append(e.zd)
                result['sell_zs_tupo']['tag'].append(','.join(tags))

                if second_chance == 1:
                    for kk in range(r + 6, len(time_series)):
                        if high_series[kk] > e.zd or duan_series[kk] == 1:
                            break
                        if high_series[kk] < high_series[kk-2] and high_series[kk-1] < high_series[kk-2] and low_series[kk] > (e.zd+e.dd)/2:
                            result['sell_zs_tupo']['idx'].append(kk)
                            result['sell_zs_tupo']['date'].append(time_series[kk])
                            result['sell_zs_tupo']['datetime'].append(datetime_list[kk])
                            result['sell_zs_tupo']['time_str'].append(time_series[kk])
                            result['sell_zs_tupo']['data'].append(low_series[kk])
                            result['sell_zs_tupo']['price'].append(low_series[kk])
                            result['sell_zs_tupo']['stop_lose_price'].append(e.zd)
                            result['sell_zs_tupo']['tag'].append(','.join(tags))
                            break
    return result


def five_v_fan(datetime_list, time_series, duan_series, bi_series, high_series, low_series,second_chance):
    result = {
        'sell_five_v_reverse': {
            'idx': [],
            'date': [],
            'datetime': [],
            'time_str': [],
            'data': [],
            'price': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': [],
            'above_ma5': [],
            'above_ma20': []
        },
        'buy_five_v_reverse': {
            'idx': [],
            'date': [],
            'datetime': [],
            'time_str': [],
            'data': [],
            'price': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': [],
            'above_ma5': [],
            'above_ma20': []
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
                            result['sell_five_v_reverse']['datetime'].append(datetime_list[k])
                            result['sell_five_v_reverse']['time_str'].append(time_series[k])
                            result['sell_five_v_reverse']['data'].append(low_series[d1])
                            result['sell_five_v_reverse']['price'].append(low_series[d1])
                            result['sell_five_v_reverse']['stop_lose_price'].append(high_series[g1])
                            result['sell_five_v_reverse']['tag'].append(','.join(tags))

                            if second_chance == 1:
                                for kk in range(k + 6, len(time_series)):
                                    if high_series[kk] > high_series[g1] or duan_series[kk] == -1:
                                        break
                                    if high_series[kk] < high_series[kk-2] and high_series[kk-1] < high_series[kk-2] and low_series[kk] > (high_series[g1]+low_series[d1])/2:
                                        result['sell_five_v_reverse']['idx'].append(kk)
                                        result['sell_five_v_reverse']['date'].append(time_series[kk])
                                        result['sell_five_v_reverse']['datetime'].append(datetime_list[kk])
                                        result['sell_five_v_reverse']['time_str'].append(time_series[kk])
                                        result['sell_five_v_reverse']['data'].append(low_series[kk])
                                        result['sell_five_v_reverse']['price'].append(low_series[kk])
                                        result['sell_five_v_reverse']['stop_lose_price'].append(high_series[g1])
                                        result['sell_five_v_reverse']['tag'].append(','.join(tags))
                                        break
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
                            result['buy_five_v_reverse']['datetime'].append(datetime_list[k])
                            result['buy_five_v_reverse']['time_str'].append(time_series[k])
                            result['buy_five_v_reverse']['data'].append(high_series[g1])
                            result['buy_five_v_reverse']['price'].append(high_series[g1])
                            result['buy_five_v_reverse']['stop_lose_price'].append(low_series[d1])
                            result['buy_five_v_reverse']['tag'].append(','.join(tags))

                            if second_chance == 1:
                                for kk in range(k + 6, len(time_series)):
                                    if low_series[kk] < low_series[d1] or duan_series[kk] == 1:
                                        break
                                    if low_series[kk] > low_series[kk-2] and low_series[kk-1] > low_series[kk-2] and high_series[kk] < (low_series[d1]+high_series[g1])/2:
                                        result['buy_five_v_reverse']['idx'].append(kk)
                                        result['buy_five_v_reverse']['date'].append(time_series[kk])
                                        result['buy_five_v_reverse']['datetime'].append(datetime_list[kk])
                                        result['buy_five_v_reverse']['time_str'].append(time_series[kk])
                                        result['buy_five_v_reverse']['data'].append(high_series[kk])
                                        result['buy_five_v_reverse']['price'].append(high_series[kk])
                                        result['buy_five_v_reverse']['stop_lose_price'].append(low_series[d1])
                                        result['buy_five_v_reverse']['tag'].append(','.join(tags))
                                        break
                        break
                    if bi_series[k] == -1:
                        break
    return result


def v_reverse(e_list, datetime_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series,second_chance):
    result = {
        'buy_v_reverse': {
            'idx': [],
            'date': [],
            'datetime': [],
            'time_str': [],
            'data': [],
            'price': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': [],
            'above_ma5': [],
            'above_ma20': []
        },
        'sell_v_reverse': {
            'idx': [],
            'date': [],
            'datetime': [],
            'time_str': [],
            'data': [],
            'price': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': [],
            'above_ma5': [],
            'above_ma20': []
        }
    }
    count = len(time_series)
    for i in range(len(e_list)):
        e = e_list[i]
        next_e = e_list[i + 1] if i < len(e_list) - 1 else None
        if e.direction == 1:
            # 离开中枢后的第一段结束
            leave_end_index = -1
            for x in range(e.end + 1, count):
                if duan_series[x] == 1:
                    leave_end_index = x
                    break
                if next_e is not None and x >= next_e.start:
                    break
            if leave_end_index >= 0:
                # 存在强3买
                buy3 = False
                resist_index = -1
                resist_price = 0
                for j in range(leave_end_index, e.end + 1, -1):
                    if bi_series[j] == -1 and low_series[j] > e.zg:
                        buy3 = True
                        resist_index = j
                        resist_price = low_series[resist_index]
                        break
                if buy3:
                    for k in range(leave_end_index + 1, count):
                        if bi_series[k] == -1:
                            break
                        if low_series[k] < resist_price:
                            tags = []
                            if pydash.find_last_index(result['sell_v_reverse']['date'], lambda x: x == time_series[k]) == -1:
                                result['sell_v_reverse']['idx'].append(k)
                                result['sell_v_reverse']['date'].append(time_series[k])
                                result['sell_v_reverse']['datetime'].append(datetime_list[k])
                                result['sell_v_reverse']['time_str'].append(time_series[k])
                                result['sell_v_reverse']['data'].append(resist_price)
                                result['sell_v_reverse']['price'].append(resist_price)
                                result['sell_v_reverse']['stop_lose_price'].append(high_series[leave_end_index])
                                result['sell_v_reverse']['tag'].append(','.join(tags))

                                if second_chance == 1:
                                    for kk in range(k + 6, len(time_series)):
                                        if high_series[kk] > high_series[leave_end_index] or duan_series[kk] == -1:
                                            break
                                        if high_series[kk] < high_series[kk-2] and high_series[kk-1] < high_series[kk-2] and low_series[kk] > (high_series[leave_end_index]+resist_price)/2:
                                            result['sell_v_reverse']['idx'].append(kk)
                                            result['sell_v_reverse']['date'].append(time_series[kk])
                                            result['sell_v_reverse']['datetime'].append(datetime_list[kk])
                                            result['sell_v_reverse']['time_str'].append(time_series[kk])
                                            result['sell_v_reverse']['data'].append(low_series[kk])
                                            result['sell_v_reverse']['price'].append(low_series[kk])
                                            result['sell_v_reverse']['stop_lose_price'].append(high_series[leave_end_index])
                                            result['sell_v_reverse']['tag'].append(','.join(tags))
                                            break
                            break
        if e.direction == -1:
            # 离开中枢后的第一段结束
            leave_end_index = -1
            for x in range(e.end + 1, count):
                if duan_series[x] == -1:
                    leave_end_index = x
                    break
                if next_e is not None and x >= next_e.start:
                    break
            if leave_end_index >= 0:
                # 存在3卖
                sell3 = False
                resist_index = -1
                resist_price = 0
                for j in range(leave_end_index, e.end, -1):
                    if bi_series[j] == 1 and high_series[j] < e.zd:
                        sell3 = True
                        resist_index = j
                        resist_price = high_series[resist_index]
                        break
                if sell3:
                    for k in range(leave_end_index + 1, count):
                        if bi_series[k] == 1:
                            break
                        if high_series[k] > resist_price:
                            tags = []
                            if pydash.find_last_index(result['buy_v_reverse']['date'], lambda x: x == time_series[k]) == -1:
                                result['buy_v_reverse']['idx'].append(k)
                                result['buy_v_reverse']['date'].append(time_series[k])
                                result['buy_v_reverse']['datetime'].append(datetime_list[k])
                                result['buy_v_reverse']['time_str'].append(time_series[k])
                                result['buy_v_reverse']['data'].append(resist_price)
                                result['buy_v_reverse']['price'].append(resist_price)
                                result['buy_v_reverse']['stop_lose_price'].append(low_series[leave_end_index])
                                result['buy_v_reverse']['tag'].append(','.join(tags))

                                if second_chance == 1:
                                    for kk in range(k + 6, count):
                                        if low_series[kk] < low_series[leave_end_index] or duan_series[kk] == 1:
                                            break
                                        if low_series[kk] > low_series[kk-2] and low_series[kk-1] > low_series[kk-2] and high_series[kk] < (low_series[leave_end_index]+resist_price)/2:
                                            result['buy_v_reverse']['idx'].append(kk)
                                            result['buy_v_reverse']['date'].append(time_series[kk])
                                            result['buy_v_reverse']['datetime'].append(datetime_list[kk])
                                            result['buy_v_reverse']['time_str'].append(time_series[kk])
                                            result['buy_v_reverse']['data'].append(high_series[kk])
                                            result['buy_v_reverse']['price'].append(high_series[kk])
                                            result['buy_v_reverse']['stop_lose_price'].append(low_series[leave_end_index])
                                            result['buy_v_reverse']['tag'].append(','.join(tags))
                                            break
                            break
    return result


def po_huai(datetime_list, time_series, high_series, low_series, open_series, close_series, bi_series, duan_series,second_chance):
    result = {
        'buy_duan_break': {
            'idx': [],
            'date': [],
            'datetime': [],
            'time_str': [],
            'data': [],
            'price': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': [],
            'above_ma5': [],
            'above_ma20': []
        },
        'sell_duan_break': {
            'idx': [],
            'date': [],
            'datetime': [],
            'time_str': [],
            'data': [],
            'price': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': [],
            'above_ma5': [],
            'above_ma20': []
        }
    }
    for i in range(len(duan_series)):
        if duan_series[i] == 1:
            count = 0
            for j in range(i - 1, -1, -1):
                if duan_series[j] == -1:
                    break
                if bi_series[j] == -1:
                    count = count + 1
            if count < 2:
                continue
            anchor = 0
            anchor2 = 0
            for j in range(i + 1, len(time_series)):
                if duan_series[j] == -1:
                    break
                if bi_series[j] == -1:
                    anchor = j
                if bi_series[j] == 1:
                    anchor2 = j
                if anchor > 0 and anchor2 > 0:
                    break
            if anchor > 0:
                for k in range(anchor + 1, len(time_series)):
                    if duan_series[k] == -1:
                        break
                    if low_series[k] < low_series[anchor]:
                        tags = []
                        result['sell_duan_break']['idx'].append(k)
                        result['sell_duan_break']['date'].append(time_series[k])
                        result['sell_duan_break']['datetime'].append(datetime_list[k])
                        result['sell_duan_break']['time_str'].append(time_series[k])
                        result['sell_duan_break']['data'].append(low_series[anchor])
                        result['sell_duan_break']['price'].append(low_series[anchor])
                        result['sell_duan_break']['stop_lose_price'].append(high_series[anchor2])
                        result['sell_duan_break']['tag'].append(','.join(tags))

                        if second_chance == 1:
                            for kk in range(k + 6, len(time_series)):
                                if high_series[kk] > high_series[i] or duan_series[kk] == -1:
                                    break
                                if high_series[kk] < high_series[kk-2] and high_series[kk-1] < high_series[kk-2] and low_series[kk] > (high_series[i]+low_series[anchor])/2:
                                    result['sell_duan_break']['idx'].append(kk)
                                    result['sell_duan_break']['date'].append(time_series[kk])
                                    result['sell_duan_break']['datetime'].append(datetime_list[kk])
                                    result['sell_duan_break']['time_str'].append(time_series[kk])
                                    result['sell_duan_break']['data'].append(low_series[kk])
                                    result['sell_duan_break']['price'].append(low_series[kk])
                                    result['sell_duan_break']['stop_lose_price'].append(high_series[i])
                                    result['sell_duan_break']['tag'].append(','.join(tags))
                                    break
                        break
        elif duan_series[i] == -1:
            count = 0
            for j in range(i - 1, -1, -1):
                if duan_series[j] == 1:
                    break
                if bi_series[j] == 1:
                    count = count + 1
            if count < 2:
                continue
            anchor = 0
            anchor2 = 0
            for j in range(i + 1, len(time_series)):
                if duan_series[j] == 1:
                    break
                if bi_series[j] == 1:
                    anchor = j
                if bi_series[j] == -1:
                    anchor2 = j
                if anchor > 0 and anchor2 > 0:
                    break;
            if anchor > 0:
                for k in range(anchor + 1, len(time_series)):
                    if duan_series[k] == 1:
                        break
                    if high_series[k] > high_series[anchor]:
                        tags = []
                        result['buy_duan_break']['idx'].append(k)
                        result['buy_duan_break']['date'].append(time_series[k])
                        result['buy_duan_break']['datetime'].append(datetime_list[k])
                        result['buy_duan_break']['time_str'].append(time_series[k])
                        result['buy_duan_break']['data'].append(high_series[anchor])
                        result['buy_duan_break']['price'].append(high_series[anchor])
                        result['buy_duan_break']['stop_lose_price'].append(low_series[anchor2])
                        result['buy_duan_break']['tag'].append(','.join(tags))

                        if second_chance == 1:
                            for kk in range(k + 6, len(time_series)):
                                if low_series[kk] < low_series[i] or duan_series[kk] == 1:
                                    break
                                if low_series[kk] > low_series[kk-2] and low_series[kk-1] > low_series[kk-2] and high_series[kk] < (low_series[i]+high_series[anchor])/2:
                                    result['buy_duan_break']['idx'].append(kk)
                                    result['buy_duan_break']['date'].append(time_series[kk])
                                    result['buy_duan_break']['datetime'].append(datetime_list[kk])
                                    result['buy_duan_break']['time_str'].append(time_series[kk])
                                    result['buy_duan_break']['data'].append(high_series[kk])
                                    result['buy_duan_break']['price'].append(high_series[kk])
                                    result['buy_duan_break']['stop_lose_price'].append(low_series[i])
                                    result['buy_duan_break']['tag'].append(','.join(tags))
                                    break
                        break
    return result
