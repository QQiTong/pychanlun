import numpy as np
import pydash
import pandas as pd


def merge_candles(klines, from_index, to_index, dir):
    candles = []
    # dir 指笔的运行方向
    # direction 指包含处理的方向
    direction = -dir
    for i in range(from_index, to_index + 1):
        if len(candles) == 0:
            candle = {'high': klines.loc[i, 'high'], 'low': klines.loc[i, 'low'], 'sticks': []}
            candles.append(candle)
        else:
            if klines.loc[i, 'high'] > candles[-1]['high'] and klines.loc[i, 'low'] > candles[-1]['low']:
                candle = { 'high': klines.loc[i, 'high'], 'low': klines.loc[i, 'low'], 'sticks': [] }
                candles.append(candle)
                direction = 1
            elif klines.loc[i, 'high'] < candles[-1]['high'] and klines.loc[i, 'low'] < candles[-1]['low']:
                candle = { 'high': klines.loc[i, 'high'], 'low': klines.loc[i, 'low'], 'sticks': [] }
                candles.append(candle)
                direction = -1
            elif klines.loc[i, 'high'] <= candles[-1]['high'] and klines.loc[i, 'low'] >= candles[-1]['low']:
                if direction == 1:
                    candles[-1]['low'] = klines.loc[i, 'low']
                elif direction == -1:
                    candles[-1]['high'] = klines.loc[i, 'high']
            elif klines.loc[i, 'high'] >= candles[-1]['high'] and klines.loc[i, 'low'] <= candles[-1]['low']:
                if direction == 1:
                    candles[-1]['high'] = klines.loc[i, 'high']
                elif direction == -1:
                    candles[-1]['low'] = klines.loc[i, 'low']
        candles[-1]['sticks'].append({ 'h': max(klines.loc[i, 'open'], klines.loc[i, 'close']), 'l': min(klines.loc[i, 'open'], klines.loc[i, 'close']) })
    return candles


def is_bi(klines, from_index, to_index, dir, strict=False):
    if not strict:
        if dir == 1:
            g1 = pydash.find_last_index(klines.loc[:from_index-1, 'bi'], lambda x: x == 1)
            if g1 >= 0 and klines.loc[to_index, 'high'] > klines.loc[g1, 'high']:
                return True
        elif dir == -1:
            d1 = pydash.find_last_index(klines.loc[:from_index-1, 'bi'], lambda x: x == -1)
            if d1 >= 0 and klines.loc[to_index, 'low'] < klines.loc[d1, 'low']:
                return True
    if to_index - from_index < 4:
        # K柱数量不够不成笔
        return False
    candles = merge_candles(klines, from_index, to_index, dir)
    if len(candles) < 5:
        # 合并后K柱数量不够不成笔
        return False
    if dir == 1:
        if candles[-1]['high'] < candles[-2]['high']:
            return False
    elif dir == -1:
        if candles[-1]['low'] > candles[-2]['low']:
            return False
    if to_index - from_index + 1 >= 13:
        # 满足13K就不看是否重叠了
        return True
    # 查看顶底是否重叠
    if dir == 1:
        bottomHigh = 0
        topLow = 0
        sticks = candles[0]['sticks'] + candles[1]['sticks']
        for idx in range(len(sticks)):
            if bottomHigh == 0:
                bottomHigh = sticks[idx]['h']
            elif sticks[idx]['h'] > bottomHigh:
                bottomHigh = sticks[idx]['h']
        sticks = candles[-2]['sticks'] + candles[-1]['sticks']
        for idx in range(len(sticks)):
            if topLow == 0:
                topLow = sticks[idx]['l']
            elif sticks[idx]['l'] < topLow:
                topLow = sticks[idx]['l']
        # 顶和底有重叠，不能成笔
        if topLow < bottomHigh:
            return False
        # isValid 表示是否有独立K柱不和底或顶重叠
        isValid = False
        for t in range(2, len(candles) - 2):
            for idx in range(len(candles[t]['sticks'])):
                if candles[t]['sticks'][idx]['l'] >= bottomHigh and candles[t]['sticks'][idx]['h'] <= topLow:
                    isValid = True
                    break
            if isValid:
                break
        if not isValid:
            return False
    elif dir == -1:
        topLow = 0
        bottomHigh = 0
        sticks = candles[0]['sticks'] + candles[1]['sticks']
        for idx in range(0, len(sticks)):
            if topLow == 0:
                topLow = sticks[idx]['l']
            elif sticks[idx]['l'] < topLow:
                topLow = sticks[idx]['l']
        sticks = candles[-2]['sticks'] + candles[-1]['sticks']
        for idx in range(0, len(sticks)):
            if bottomHigh == 0:
                bottomHigh = sticks[idx]['h']
            elif sticks[idx]['h'] > bottomHigh:
                bottomHigh = sticks[idx]['h']
        # 顶和底有重叠，不能成笔
        if bottomHigh > topLow:
            return False
        # isValid 表示是否有独立K柱不和底或顶重叠
        isValid = False
        for t in range(2, len(candles) - 2):
            for idx in range(len(candles[t]['sticks'])):
                if candles[t]['sticks'][idx]['l'] >= bottomHigh and candles[t]['sticks'][idx]['h'] <= topLow:
                    isValid = True
                    break
            if isValid:
                break
        if not isValid:
            return False
    return True


def adjust_bi(klines, index):
    if klines.loc[index, 'bi'] == 1:
        i = pydash.find_last_index(klines.loc[:index-1, 'bi'], lambda x: x == -1)
        if i > 0:
            if not is_bi(klines, i, index, 1, True):
                # 不是严格成笔，需要调整
                # g1记录当前笔的高的位置
                # d1记录当前笔的低的位置
                g1 = index
                d1 = i
                # g2记录前一笔的高的位置
                # d2记录前一笔的低的位置
                g2 = pydash.find_last_index(klines.loc[:d1-1, 'bi'], lambda x: x == 1)
                d2 = pydash.find_last_index(klines.loc[:g2-1, 'bi'], lambda x: x == -1)
                if d2 >= 0:
                    # 两笔找全，看看是不是可以合并
                    if klines.loc[g1, 'high'] >= klines.loc[g2, 'high'] and klines.loc[d1, 'low'] >= klines.loc[d2, 'low']:
                        for j in range(d2 + 1, g1):
                            klines.loc[j, 'bi'] = 0
    elif klines.loc[index, 'bi'] == -1:
        i = pydash.find_last_index(klines.loc[:index-1, 'bi'], lambda x: x == 1)
        if i > 0:
            if not is_bi(klines, i, index, -1, True):
                # 不是严格成笔，需要调整
                # d1记录当前笔的低的位置
                # g1记录当前笔的高的位置
                d1 = index
                g1 = i
                # d2记录前一笔的低的位置
                # g2记录前一笔的高的位置
                d2 = pydash.find_last_index(klines.loc[:g1-1, 'bi'], lambda x: x == -1)
                g2 = pydash.find_last_index(klines.loc[:d2-1, 'bi'], lambda x: x == 1)
                if g2 >= 0:
                    # 两笔找全，看看是不是可以合并
                    if klines.loc[d1, 'low'] <= klines.loc[d2, 'low'] and klines.loc[g1, 'high'] <= klines.loc[g2, 'high']:
                        for j in range(g2 + 1, d1):
                            klines.loc[j, 'bi'] = 0


def calculate_bi(klines):
    count = len(klines)
    bi = pd.Series(np.zeros(count))
    klines['bi'] = bi
    for i in range(1, count):
        # x 前一个笔低点
        x = pydash.find_last_index(klines.loc[0:i-1, 'bi'], lambda x: x == -1)
        x = max(0, x)
        # y 前一个笔高点
        y = pydash.find_last_index(klines.loc[0:i-1, 'bi'], lambda x: x == 1)
        y = max(0, y)

        # 前低点到现在的最高价
        max_high = klines.loc[x:i-1, 'high'].max()
        # 前高点到现在的最低价
        min_low = klines.loc[y:i-1, 'low'].min()

        # 是新高
        b1 = klines.loc[i, 'high'] > max_high
        # 是新低
        b2 = klines.loc[i, 'low'] < min_low

        if (b1 and b2):
            # 既是新高又是新低
            for idx in range(i-1, -1, -1):
                if klines.loc[idx, 'bi'] == 1 and klines.loc[idx, 'high'] > klines.loc[i, 'high']:
                    klines.loc[i, 'bi'] = -1
                    for k in range(idx + 1, i):
                        klines.loc[k, 'bi'] = 0
                    break
                elif klines.loc[idx, 'bi'] == -1 and klines.loc[idx, 'low'] < klines.loc[i, 'low']:
                    klines.loc[i, 'bi'] = 1
                    for k in range(idx + 1, i):
                        klines.loc[k, 'bi'] = 0
                    break
        elif b1:
            if (x == y and x == 0)  or y > x or is_bi(klines, x, i, 1, False):
                klines.loc[x, 'bi'] = -1
                klines.loc[i, 'bi'] = 1
                for t in range(x + 1, i):
                    klines.loc[t, 'bi'] = 0
                adjust_bi(klines, x)
        elif b2:
            if (x == y and y == 0) or x > y or is_bi(klines, y, i, -1, False):
                klines.loc[y, 'bi'] = 1
                klines.loc[i, 'bi'] = -1
                for t in range(y + 1, i):
                    klines.loc[t, 'bi'] = 0
                adjust_bi(klines, y)
    return klines
