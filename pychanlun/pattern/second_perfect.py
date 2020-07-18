# -*- coding: utf-8 -*-

import pydash

"""
完备第二买卖点
"""


def second_perfect(kline_data):
    result = {
        'buy_second_perfect': {
            'idx': [],
            'date': [],
            'data': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': [],
            'above_ma5': [],
            'above_ma20': []
        },
        'sell_second_perfect': {
            'idx': [],
            'date': [],
            'data': [],
            'stop_lose_price': [],
            'stop_win_price': [],
            'tag': [],
            'above_ma5': [],
            'above_ma20': []
        }
    }
    count = len(kline_data)
    bi_list = list(kline_data['bi'])
    high_list = list(kline_data['high'])
    low_list = list(kline_data['low'])
    time_str_list = list(kline_data['time_str'])
    ma5_list = list(kline_data['ma5'])
    ma20_list = list(kline_data['ma20'])
    for i in range(count):
        if bi_list[i] == -1:
            d1 = i
            g1 = pydash.find_last_index(bi_list[:d1], lambda x: x == 1)
            d2 = pydash.find_last_index(bi_list[:g1], lambda x: x == -1)
            g2 = pydash.find_last_index(bi_list[:d2], lambda x: x == 1)
            d3 = pydash.find_last_index(bi_list[:g2], lambda x: x == -1)
            if low_list[d3] > low_list[d2] or low_list[d3] > low_list[d1]:
                continue
            if min(high_list[g1], high_list[g2]) <= max(low_list[d1], low_list[d2]):
                continue
            n = pydash.find_index(bi_list[i:], lambda x: x == 1)
            if n == -1:
                continue
            g0 = i + n
            if high_list[g0] >= max(high_list[g1], high_list[g2]):
                continue
            n = pydash.find_index(bi_list[g0:], lambda x: x == -1)
            if n == -1:
                continue
            d0 = g0 + n
            for j in range(d0+1, count):
                if high_list[j] > high_list[g0]:
                    # 找到买点
                    result['buy_second_perfect']['idx'].append(j)
                    result['buy_second_perfect']['date'].append(time_str_list[j])
                    result['buy_second_perfect']['data'].append(high_list[j])
                    result['buy_second_perfect']['stop_lose_price'].append(min(low_list[d1], low_list[d2]))
                    result['buy_second_perfect']['tag'].append("完备套")
                    result['buy_second_perfect']['above_ma5'].append(high_list[j] > ma5_list[j])
                    result['buy_second_perfect']['above_ma20'].append(high_list[j] > ma20_list[j])
                    break
                elif bi_list[j] == 1:
                    break
        elif bi_list[i] == 1:
            g1 = i
            d1 = pydash.find_last_index(bi_list[:g1], lambda x: x == -1)
            g2 = pydash.find_last_index(bi_list[:d1], lambda x: x == 1)
            d2 = pydash.find_last_index(bi_list[:g2], lambda x: x == -1)
            g3 = pydash.find_last_index(bi_list[:d2], lambda x: x == 1)
            if high_list[g3] < high_list[g2] or high_list[g3] < high_list[g1]:
                continue
            if min(high_list[g1], high_list[g2]) <= max(low_list[d1], low_list[d2]):
                continue
            n = pydash.find_index(bi_list[i:], lambda x: x == -1)
            if n == -1:
                continue
            d0 = i + n
            if low_list[d0] <= max(low_list[d1], low_list[d2]):
                continue
            n = pydash.find_index(bi_list[d0:], lambda x: x == 1)
            if n == -1:
                continue
            g0 = d0 + n
            for j in range(g0+1, count):
                if low_list[j] < low_list[d0]:
                    # 找到买点
                    result['sell_second_perfect']['idx'].append(j)
                    result['sell_second_perfect']['date'].append(time_str_list[j])
                    result['sell_second_perfect']['data'].append(low_list[j])
                    result['sell_second_perfect']['stop_lose_price'].append(max(high_list[d1], high_list[d2]))
                    result['sell_second_perfect']['tag'].append("完备套")
                    result['sell_second_perfect']['above_ma5'].append(high_list[j] > ma5_list[j])
                    result['sell_second_perfect']['above_ma20'].append(high_list[j] > ma20_list[j])
                    break
                elif bi_list[j] == -1:
                    break

    return result
