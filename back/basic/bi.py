# 笔算法

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
            i = from_index - 1
            for i in range(from_index - 1, 0, -1):
                if bi[i] == 1:
                    break
            if high[to_index] > high[i]:
                return True
        elif dir == -1:
            i = from_index - 1
            for i in range(from_index - 1, 0, -1):
                if bi[i] == -1:
                    break
            if low[to_index] < low[i]:
                return True
    if to_index - from_index < 4:
        # K柱数量不够不成笔
        return False
    candles = MergeCandles(high, low, from_index, to_index, dir)
    if len(candles) < 5:
        # 合并后K柱数量不够不成笔
        return False
    # 查看顶底是否重叠
    if dir == 1:
        i = from_index - 1
        for i in range(from_index - 1, 0, -1):
            if bi[i] == 1:
                break
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
            isValid = False
            for t in range(2, len(candlesCurr) - 2):
                if (candlesCurr[t]['low'] >= bottomHigh and candlesCurr[t]['low'] <= topLow) or (candlesCurr[t]['high'] <= topLow and candlesCurr[t]['high'] >= bottomHigh):
                    isValid = True
            if not isValid:
                return False
    elif dir == -1:
        i = from_index - 1
        for i in range(from_index, 0, -1):
            if bi[i] == -1:
                break
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
            isValid = False
            for t in range(2, len(candlesCurr) - 2):
                if (candlesCurr[t]['low'] >= bottomHigh and candlesCurr[t]['low'] <= topLow) or (candlesCurr[t]['high'] <= topLow and candlesCurr[t]['high'] >= bottomHigh):
                    isValid = True
            if not isValid:
                return False
    return True

# index传入前一笔的结束位置，如果前一笔不是严格的笔，进行合并。
# 合并要符合闪电形态，而且只合一次。
def AdjustBi(count, bi, high, low, index):
    if bi[index] == 1:
        i = 0
        for i in range(index - 1, 0, -1):
            if bi[i] == -1:
                break
        if i > 0:
            if not IsBi(count, bi, high, low, i, index, 1, True):
                # 不是严格成笔，需要调整
                # g1记录当前笔的高的位置
                # d1记录当前笔的低的位置
                g1 = index
                d1 = i
                # g2记录前一笔的高的位置
                # d2记录前一笔的低的位置
                g2 = 0
                d2 = 0
                for i in range(i - 1, 0, -1):
                    if bi[i] == 1:
                        g2 = i
                        break
                if i > 0:
                    for i in range(i - 1, 0, -1):
                        if bi[i] == -1:
                            d2 = i
                            break
                    if i > 0:
                        # 两笔找全，看看是不是可以合并
                        if high[g1] >= high[g2] and low[d1] >= low[d2]:
                            for j in range(d2 + 1, g1):
                                bi[j] = 0
    elif bi[index] == -1:
        i = 0
        for i in range(index - 1, 0, -1):
            if bi[i] == 1:
                # 找到前面的高点
                break
        if i > 0:
            if not IsBi(count, bi, high, low, i, index, -1, True):
                # 不是严格成笔，需要调整
                # d1记录当前笔的低的位置
                # g1记录当前笔的高的位置
                d1 = index
                g1 = i
                # d2记录前一笔的低的位置
                # g2记录前一笔的高的位置
                g2 = 0
                d2 = 0
                for i in range(i - 1, 0, -1):
                    if bi[i] == -1:
                        d2 = i
                        break
                if i > 0:
                    for i in range(i - 1, 0, -1):
                        if bi[i] == 1:
                            g2 = i
                            break
                    if i > 0:
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
        x = i - 1
        for x in range(i - 1, -1, -1):
            if bi[x] == -1:
                break
        maxHigh = max(high[x:i])
        # 是新高
        b1 = high[i] > maxHigh
        if b1 and IsBi(count, bi, high, low, x, i, 1, False):
            bi[x] = -1
            bi[i] = 1
            for t in range(x + 1, i):
                bi[t] = 0
            AdjustBi(count, bi, high, low, x)

        y = i - 1
        for y in range(i -1, -1, -1):
            if bi[y] == 1:
                break
        minLow = min(low[y:i])
        # 是新低
        b2 = low[i] < minLow
        if b2 and IsBi(count, bi, high, low, y, i, -1, False):
            bi[y] = 1
            bi[i] = -1
            for t in range(y + 1, i):
                bi[t] = 0
            AdjustBi(count, bi, high, low, y)
