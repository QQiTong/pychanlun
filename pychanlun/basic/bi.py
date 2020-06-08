# -*- coding: utf-8 -*-

from pychanlun.basic.comm import FindPrevEq
import pydash


def merge_candles(high, low, open_price, close_price, from_index, to_index, dir):
    candles = []
    # dir 指笔的运行方向
    # direction 指包含处理的方向
    direction = -dir
    for i in range(from_index, to_index + 1):
        if len(candles) == 0:
            candle = {'high': high[i], 'low': low[i], 'sticks': []}
            candles.append(candle)
        else:
            if high[i] > candles[-1]['high'] and low[i] > candles[-1]['low']:
                candle = { 'high': high[i], 'low': low[i], 'sticks': [] }
                candles.append(candle)
                direction = 1
            elif high[i] < candles[-1]['high'] and low[i] < candles[-1]['low']:
                candle = { 'high': high[i], 'low': low[i], 'sticks': [] }
                candles.append(candle)
                direction = -1
            elif high[i] <= candles[-1]['high'] and low[i] >= candles[-1]['low']:
                if direction == 1:
                    candles[-1]['low'] = low[i]
                elif direction == -1:
                    candles[-1]['high'] = high[i]
            elif high[i] >= candles[-1]['high'] and low[i] <= candles[-1]['low']:
                if direction == 1:
                    candles[-1]['high'] = high[i]
                elif direction == -1:
                    candles[-1]['low'] = low[i]
        candles[-1]['sticks'].append({ 'h': max(open_price[i], close_price[i]), 'l': min(open_price[i], close_price[i]) })
    return candles


# 判断起点和终点之间是否成笔
# count 数据序列长度
# bi 笔信号输出序列
# high 最高价序列
# low 最低价序列
# from_index 起点(含)
# to_index 终点(含)
# dir 笔方向
# small_period 是否是小级别
def is_bi(bi, high, low, open_price, close_price, from_index, to_index, direction, small_period=False):
    if to_index - from_index < 4:
        # K柱数量不够不成笔
        return False
    # 前一笔的合并K线
    prev_candles = None
    if direction == 1:
        g1 = FindPrevEq(bi, 1, from_index)
        if g1 >= 0:
            prev_candles = merge_candles(high, low, open_price, close_price, g1, from_index, -1)
    if direction == -1:
        d1 = FindPrevEq(bi, -1, from_index)
        if d1 >= 0:
            prev_candles = merge_candles(high, low, open_price, close_price, d1, from_index, 1)
    # 当前笔的合并K线
    candles = merge_candles(high, low, open_price, close_price, from_index, to_index, direction)
    if len(candles) < 5:
        # 合并后K柱数量不够不成笔
        return False
    if direction == 1:
        if candles[-1]['high'] < candles[-2]['high']:
            return False
    elif direction == -1:
        if candles[-1]['low'] > candles[-2]['low']:
            return False
    if not small_period and to_index - from_index + 1 >= 13:
        # 满足13K就不看是否重叠了
        return True

    # 查看顶底是否重叠
    if direction == 1:
        bottom_high = 0
        top_low = 0
        sticks = candles[0]['sticks'] + candles[1]['sticks']
        if prev_candles is not None and len(prev_candles) > 1:
            sticks = prev_candles[-2]['sticks'] + sticks
        for idx in range(len(sticks)):
            if bottom_high == 0:
                bottom_high = sticks[idx]['h']
            elif sticks[idx]['h'] > bottom_high:
                bottom_high = sticks[idx]['h']

        temp_candles = [{
            'high': high[to_index],
            'low': low[to_index],
            'sticks': [{ 'h': max(open_price[to_index], close_price[to_index]), 'l': min(open_price[to_index], close_price[to_index]) }]
        }]
        for k in range(to_index + 1, len(bi)):
            if high[k] > high[to_index]:
                # 没有顶分型
                return False
            else:
                if high[k] < temp_candles[-1]['high'] and low[k] < temp_candles[-1]['low']:
                    temp_candles.append({
                        'high': high[k],
                        'low': low[k],
                        'sticks': [{
                            'h': max(open_price[k], close_price[k]),
                            'l': min(open_price[k], close_price[k])
                        }]
                    })
                    break
                else:
                    temp_candles[-1]['high'] = max(temp_candles[-1]['high'], high[k])
                    temp_candles[-1]['low'] = max(temp_candles[-1]['low'], low[k])
                    temp_candles[-1]['sticks'].append({
                        'h': max(open_price[k], close_price[k]),
                        'l': min(open_price[k], close_price[k])
                    })

        sticks = candles[-2]['sticks'] + candles[-1]['sticks']
        if len(temp_candles) > 1:
            sticks = sticks + temp_candles[1]['sticks']
        for idx in range(len(sticks)):
            if top_low == 0:
                top_low = sticks[idx]['l']
            elif sticks[idx]['l'] < top_low:
                top_low = sticks[idx]['l']

        # 顶和底有重叠，不能成笔
        if top_low < bottom_high:
            return False
        # isValid 表示是否有独立K柱不和底或顶重叠
        isValid = False
        for t in range(2, len(candles) - 2):
            for idx in range(len(candles[t]['sticks'])):
                if candles[t]['sticks'][idx]['l'] > bottom_high and candles[t]['sticks'][idx]['h'] < top_low:
                    isValid = True
                    break
            if isValid:
                break
        if not isValid:
            return False
    elif direction == -1:
        top_low = 0
        bottom_high = 0
        sticks = candles[0]['sticks'] + candles[1]['sticks']
        if prev_candles is not None and len(prev_candles) > 1:
            sticks = prev_candles[-2]['sticks'] + sticks
        for idx in range(0, len(sticks)):
            if top_low == 0:
                top_low = sticks[idx]['l']
            elif sticks[idx]['l'] < top_low:
                top_low = sticks[idx]['l']

        # 后一笔的合并K线
        temp_candles = [{
            'high': high[to_index],
            'low': low[to_index],
            'sticks': [{
                'h': max(open_price[to_index], close_price[to_index]),
                'l': min(open_price[to_index], close_price[to_index])
            }]
        }]
        for k in range(to_index + 1, len(bi)):
            if low[k] < low[to_index]:
                # 没有顶分型
                return False
            else:
                if high[k] > temp_candles[-1]['high'] and low[k] > temp_candles[-1]['low']:
                    temp_candles.append({
                        'high': high[k],
                        'low': low[k],
                        'sticks': [{
                            'h': max(open_price[k], close_price[k]),
                            'l': min(open_price[k], close_price[k])
                        }]
                    })
                    break
                else:
                    temp_candles[-1]['high'] = min(temp_candles[-1]['high'], high[k])
                    temp_candles[-1]['low'] = min(temp_candles[-1]['low'], low[k])
                    temp_candles[-1]['sticks'].append({
                        'h': max(open_price[k], close_price[k]),
                        'l': min(open_price[k], close_price[k])
                    })

        sticks = candles[-2]['sticks'] + candles[-1]['sticks']
        if len(temp_candles) > 1:
            sticks = sticks + temp_candles[1]['sticks']
        for idx in range(0, len(sticks)):
            if bottom_high == 0:
                bottom_high = sticks[idx]['h']
            elif sticks[idx]['h'] > bottom_high:
                bottom_high = sticks[idx]['h']

        # 顶和底有重叠，不能成笔
        if bottom_high > top_low:
            return False
        # isValid 表示是否有独立K柱不和底或顶重叠
        isValid = False
        for t in range(2, len(candles) - 2):
            for idx in range(len(candles[t]['sticks'])):
                if candles[t]['sticks'][idx]['l'] > bottom_high and candles[t]['sticks'][idx]['h'] < top_low:
                    isValid = True
                    break
            if isValid:
                break
        if not isValid:
            return False
    return True


def adjust_bi(bi_list, high_list, low_list, x, y):
    if bi_list[x] == 1 and bi_list[y] == -1:
        # 向下笔
        xx = x
        for t in range(x + 1, y + 1):
            if high_list[t] > high_list[xx]:
                xx = t
        if xx > x:
            bi_list[x] = 0
            bi_list[y] = 0
            bi_list[xx] = 1
            j = pydash.find_last_index(bi_list[:xx], lambda k : k == -1)
            if j >= 0:
                return adjust_bi(bi_list, high_list, low_list, j, xx)
            return xx
    elif bi_list[x] == -1 and bi_list[y] == 1:
        # 向上笔
        xx = x
        for t in range(x + 1, y + 1):
            if low_list[t] < low_list[xx]:
                xx = t
        if xx > x:
            bi_list[x] = 0
            bi_list[y] = 0
            bi_list[xx] = -1
            j = pydash.find_last_index(bi_list[:xx], lambda k: k == 1)
            if j >= 0:
                return adjust_bi(bi_list, high_list, low_list, j, xx)
            return xx
    return y


# 计算笔信号
# count 数据序列长度
# bi 输出的笔信号序列
# high 最高价的序列
# low 最低价的序列
# small_period 是否是小级别
def CalcBi(count, bi, high, low, open_price, close_price, small_period=False):
    # 标记分型的顶底
    for i in range(1, count):
        # x 前一个笔低点
        x = FindPrevEq(bi, -1, i)
        x = max(0, x)
        # y 前一个笔高点
        y = FindPrevEq(bi, 1, i)
        y = max(0, y)

        maxHigh = max(high[x:i])
        minLow = min(low[y:i])

        # 是新高
        b1 = high[i] > maxHigh
        # 是新低
        b2 = low[i] < minLow

        if b1 and b2:
            for idx in range(i-1, -1, -1):
                if bi[idx] == 1 and high[idx] > high[i]:
                    bi[i] = -1
                    for k in range(idx+1, i):
                        bi[k] = 0
                    break
                elif bi[idx] == -1 and low[idx] < low[i]:
                    bi[i] = 1
                    for k in range(idx+1, i):
                        bi[k] = 0
                    break
        elif b1:
            if (x == y and x == 0) or y > x or is_bi(bi, high, low, open_price, close_price, x, i, 1, small_period):
                bi[x] = -1
                bi[i] = 1
                for t in range(x + 1, i):
                    bi[t] = 0
                i = adjust_bi(bi, high, low, x, i)

        elif b2:
            if (x == y and y == 0) or x > y or is_bi(bi, high, low, open_price, close_price, y, i, -1, small_period):
                bi[y] = 1
                bi[i] = -1
                for t in range(y + 1, i):
                    bi[t] = 0
                i = adjust_bi(bi, high, low, y, i)


def CalcBiList(count, bi, high, low):
    biList = []
    for i in range(count):
        candle = { "high": high[i], "low": low[i] }
        if bi[i] == 1:
            if len(biList) > 0:
                biList[-1]["end"] = i
            bi_item = { "start": i, "end": i, "direction": -1, "candleList": [ candle ] }
            biList.append(bi_item)
        elif bi[i] == -1:
            if len(biList) > 0:
                biList[-1]["end"] = i
            bi_item = { "start": i, "end": i, "direction": 1, "candleList": [ candle ] }
            biList.append(bi_item)
        else:
            if len(biList) > 0:
                biList[-1]["end"] = i
                biList[-1]["candleList"].append(candle)
    return biList


def FindLastFractalRegion(count, bi_series, time_series, high_series, low_series, open_series, close_series):
    top_fractal = None
    bottom_fractal = None
    g1 = FindPrevEq(bi_series, 1, count)
    d1 = FindPrevEq(bi_series, -1, count)
    if g1 > d1 > 0: # 最后是向上笔
        g2 = FindPrevEq(bi_series, 1, d1)
        if g2 > 0:
            candles = merge_candles(high_series, low_series, open_series, close_series, d1, g1, 1)
            sticks = candles[-2]["sticks"]
            dt = time_series[g1]
            top = high_series[g1]
            bottom = sticks[0]["l"]
            for idx in range(len(sticks)):
                if sticks[idx]["l"] < bottom:
                    bottom = sticks[idx]["l"]
            top_fractal = { "date": dt, "top": top, "bottom": bottom }
            candles = merge_candles(high_series, low_series, open_series, close_series, g2, d1, -1)
            sticks = candles[-2]["sticks"]
            dt = time_series[d1]
            bottom = low_series[d1]
            top = sticks[0]["h"]
            for idx in range(len(sticks)):
                if sticks[idx]["h"] > top:
                    top = sticks[idx]["h"]
            bottom_fractal = { "date": dt, "top": top, "bottom": bottom }
            return { "direction": 1, "top_fractal": top_fractal, "bottom_fractal": bottom_fractal }
    elif d1 > g1 > 0: # 最后是向下笔
        d2 = FindPrevEq(bi_series, -1, g1)
        if d2 > 0:
            candles = merge_candles(high_series, low_series, open_series, close_series, g1, d1, -1)
            sticks = candles[-2]["sticks"]
            dt = time_series[d1]
            bottom = low_series[d1]
            top = sticks[0]["h"]
            for idx in range(len(sticks)):
                if sticks[idx]["h"] > top:
                    top = sticks[idx]["h"]
            bottom_fractal = { "date": dt, "top": top, "bottom": bottom }

            candles = merge_candles(high_series, low_series, open_series, close_series, d2, g1, 1)
            sticks = candles[-2]["sticks"]

            dt = time_series[g1]
            top = high_series[g1]
            bottom = sticks[0]["l"]
            for idx in range(len(sticks)):
                if sticks[idx]["l"] < bottom:
                    bottom = sticks[idx]["l"]
            top_fractal = { "date": dt, "top": top, "bottom": bottom }
            return { "direction": -1, "top_fractal": top_fractal, "bottom_fractal": bottom_fractal }
