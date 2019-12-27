# 笔算法

def MergeCandles(high, low, from_index, to_index, dir):
    candles = []
    for i in range(from_index, to_index + 1):
        if len(candles) == 0:
            candles.append({'high': high[i], 'low': low[i]})
        else:
            if high[i] > candles[-1]['high'] and low[i] > candles[-1]['low']:
                candles.append({'high': high[i], 'low': low[i]})
            elif high[i] < candles[-1]['high'] and low[i] < candles[-1]['low']:
                candles.append({'high': high[i], 'low': low[i]})
            elif high[i] <= candles[-1]['high'] and low[i] >= candles[-1]['low']:
                if dir == 1:
                    candles[-1]['low'] = low[i]
                elif dir == -1:
                    candles[-1]['high'] = high[i]
            elif high[i] >= candles[-1]['high'] and low[i] <= candles[-1]['low']:
                if dir == 1:
                    candles[-1]['high'] = high[i]
                elif dir == -1:
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
    candles = MergeCandles(high, low, from_index, to_index, dir)
    if len(candles) >= 5:
        return True
    elif not strict:
        if dir == 1:
            j = 0
            for i in range(from_index - 1, 0, -1):
                if bi[i] == 1:
                    j = i
                    break
            if candles[-1]['high'] > high[j]:
                return True
        elif dir == -1:
            j = 0
            for i in range(from_index - 1, 0, -1):
                if bi[i] == -1:
                    j = i
                    break
            if candles[-1]['low'] < low[j]:
                return True
    return False


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
                            for j in range(d2 + 1, g1):
                                bi[j] = 0


# 计算笔信号
# count 数据序列长度
# bi 输出的笔信号序列
# high 最高价的序列
# low 最低价的序列
def CalcBi(count, bi, high, low):
    # gIndex 记录搜寻的第一个高点位置
    gIndex = 0
    # dIndex 记录搜寻的第一个低点位置
    dIndex = 0
    # start 记录第一笔找到后，后面继续开始计算的起点
    start = 0
    for i in range(1, count):
        if high[i] > high[gIndex]:
            gIndex = i
            if gIndex > dIndex:
                # 新高后看是否成立向上笔
                if IsBi(count, bi, high, low, dIndex, gIndex, 1, True):
                    bi[dIndex] = -1
                    bi[gIndex] = 1
                    start = i + 1
                    break
        if low[i] < low[dIndex]:
            dIndex = i
            if dIndex > gIndex:
                # 新低后看是否成立向下笔
                if IsBi(count, bi, high, low, gIndex, dIndex, -1, True):
                    bi[gIndex] = 1
                    bi[dIndex] = -1
                    start = i + 1
                    break
    # 前面我们计算出了第一笔的位置
    # 后面开始计算后面的笔
    for i in range(start, count):
        x = i - 1
        for j in range(x, 0, -1):
            if bi[j] == -1:
                x = j
                break
        # x 前底
        h = max(high[x:i])
        # h 前底到前一根K柱为止的最高价
        b1 = high[i] > h
        if b1 and IsBi(count, bi, high, low, x, i, 1, False):
            bi[i] = 1
            # 笔顶成立或者笔顶延伸
            for t in range(x + 1, i):
                bi[t] = 0
            AdjustBi(count, bi, high, low, x)

        y = i - 1
        for j in range(y, 0, -1):
            if bi[j] == 1:
                y = j
                break
        # y 前顶
        l = min(low[y:i])
        # l 前顶到前一根K柱为止的最低价
        b2 = low[i] < l
        if b2 and IsBi(count, bi, high, low, y, i, -1, False):
            bi[i] = -1
            for t in range(y + 1, i):
                bi[t] = 0
            AdjustBi(count, bi, high, low, y)
