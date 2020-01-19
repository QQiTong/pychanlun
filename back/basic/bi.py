from back.basic.comm import FindPrevEq

def MergeCandles(high, low, from_index, to_index, dir):
    candles = []
    # dir 指笔的运行方向
    # direction 指包含处理的方向
    direction = -dir
    for i in range(from_index, to_index + 1):
        if len(candles) == 0:
            candles.append({'high': high[i], 'low': low[i]})
        else:
            if high[i] > candles[-1]['high'] and low[i] > candles[-1]['low']:
                candles.append({'high': high[i], 'low': low[i]})
                direction = 1
            elif high[i] < candles[-1]['high'] and low[i] < candles[-1]['low']:
                candles.append({'high': high[i], 'low': low[i]})
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
    return candles

# 判断起点和终点之间是否成笔
# count 数据序列长度
# bi 笔信号输出序列
# high 最高价序列
# low 最低价序列
# from_index 起点(含)
# to_index 终点(含)
# dir 笔方向
def IsBi(count, bi, high, low, from_index, to_index, dir, strict=False):
    if not strict:
        if dir == 1:
            g1 = FindPrevEq(bi, 1, from_index)
            if g1 >= 0 and high[to_index] > high[g1]:
                return True
        elif dir == -1:
            d1 = FindPrevEq(bi, -1, from_index)
            if d1 >= 0 and low[to_index] < low[d1]:
                return True
    if to_index - from_index < 4:
        # K柱数量不够不成笔
        return False
    candles = MergeCandles(high, low, from_index, to_index, dir)
    if len(candles) < 5:
        # 合并后K柱数量不够不成笔
        return False
    if len(candles) >= 13:
        # 满足13K就不看是否重叠了
        return True
    # 查看顶底是否重叠
    if dir == 1:
        i = FindPrevEq(bi, 1, from_index)
        i = max(0, i)
        candlesPrev = MergeCandles(high, low, i, from_index, -1)
        candlesCurr = candles
        candlesNext = []
        k = to_index
        for j in range(to_index + 1, count):
            if high[j] > high[k]:
                k = j
                candlesCurr = MergeCandles(high, low, from_index, k, 1)
            else:
                candlesNext = MergeCandles(high, low, k, j, -1)
                if len(candlesNext) >= 2:
                    break
        if len(candlesPrev) >= 2  and len(candlesCurr) >= 2 and len(candlesNext) >= 2:
            bottomHigh = max(candlesCurr[1]['high'], candlesPrev[-2]['high'])
            topLow = min(candlesCurr[-2]['low'], candlesNext[1]['low'])
            # 顶和底有重叠，不能成笔
            if topLow < bottomHigh:
                return False
            # isValid 表示是否有独立K柱不和底或顶重叠
            isValid1 = False
            isValid2 = False
            for t in range(2, len(candlesCurr) - 2):
                if not isValid1 and candlesCurr[t]['high'] > bottomHigh:
                    isValid1 = True
                if not isValid2 and candlesCurr[t]['low'] < topLow:
                    isValid2 = True
                if isValid1 and isValid2:
                    break
            if not isValid1 or not isValid2:
                return False
    elif dir == -1:
        i = FindPrevEq(bi, -1, from_index)
        i = max(0, 1)
        candlesPrev = MergeCandles(high, low, i, from_index, 1)
        candlesCurr = candles
        candlesNext = []
        k = to_index
        for j in range(to_index + 1, count):
            if low[j] < low[k]:
                k = j
                candlesCurr = MergeCandles(high, low, from_index, k, -1)
            else:
                candlesNext = MergeCandles(high, low, k, j, 1)
                if len(candlesNext) >= 2:
                    break
        if len(candlesPrev) >= 2  and len(candlesCurr) >= 2 and len(candlesNext) >= 2:
            topLow = min(candlesCurr[1]['low'], candlesPrev[-2]['low'])
            bottomHigh = max(candlesCurr[-2]['high'], candlesNext[1]['high'])
            # 顶和底有重叠，不能成笔
            if bottomHigh > topLow:
                return False
            # isValid 表示是否有独立K柱不和底或顶重叠
            isValid1 = False
            isValid2 = False
            for t in range(2, len(candlesCurr) - 2):
                if not isValid1 and candlesCurr[t]['high'] > bottomHigh:
                    isValid1 = True
                if not isValid2 and candlesCurr[t]['low'] < topLow:
                    isValid2 = True
                if isValid1 and isValid2:
                    break
            if not isValid1 or not isValid2:
                return False
    return True

# index传入前一笔的结束位置，如果前一笔不是严格的笔，进行合并。
# 合并要符合闪电形态，而且只合一次。
def AdjustBi(count, bi, high, low, index):
    if bi[index] == 1:
        i = FindPrevEq(bi, -1, index)
        if i > 0:
            if not IsBi(count, bi, high, low, i, index, 1, True):
                # 不是严格成笔，需要调整
                # g1记录当前笔的高的位置
                # d1记录当前笔的低的位置
                g1 = index
                d1 = i
                # g2记录前一笔的高的位置
                # d2记录前一笔的低的位置
                g2 = FindPrevEq(bi, 1, d1)
                d2 = FindPrevEq(bi, -1, g2)
                if d2 >= 0:
                    # 两笔找全，看看是不是可以合并
                    if high[g1] >= high[g2] and low[d1] >= low[d2]:
                        for j in range(d2 + 1, g1):
                            bi[j] = 0
    elif bi[index] == -1:
        i = FindPrevEq(bi, 1, index)
        if i > 0:
            if not IsBi(count, bi, high, low, i, index, -1, True):
                # 不是严格成笔，需要调整
                # d1记录当前笔的低的位置
                # g1记录当前笔的高的位置
                d1 = index
                g1 = i
                # d2记录前一笔的低的位置
                # g2记录前一笔的高的位置
                d2 = FindPrevEq(bi, -1, g1)
                g2 = FindPrevEq(bi, 1, d2)
                if g2 >= 0:
                    # 两笔找全，看看是不是可以合并
                    if low[d1] <= low[d2] and high[g1] <= high[g2]:
                        for j in range(g2 + 1, d1):
                            bi[j] = 0


# 计算笔信号
# count 数据序列长度
# bi 输出的笔信号序列
# high 最高价的序列
# low 最低价的序列
def CalcBi(count, bi, high, low):
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

        if (b1 and b2):
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
            if y > x or IsBi(count, bi, high, low, x, i, 1, False):
                bi[x] = -1
                bi[i] = 1
                for t in range(x + 1, i):
                    bi[t] = 0
                AdjustBi(count, bi, high, low, x)
        elif b2:
            if x > y or IsBi(count, bi, high, low, y, i, -1, False):
                bi[y] = 1
                bi[i] = -1
                for t in range(y + 1, i):
                    bi[t] = 0
                AdjustBi(count, bi, high, low, y)
