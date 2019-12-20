# 笔算法

# 判断起点和终点之间是否成笔
# count 数据序列长度
# bi 笔信号输出序列
# high 最高价序列
# low 最低价序列
# from_index 起点(含)
# to_index 终点(含)
# dir 笔方向
def is_bi(count, bi, high, low, from_index, to_index, dir, strict=False):
    candles = []
    for i in range(from_index, to_index + 1):
        if len(candles) == 0:
            candles.append({ 'high': high[i], 'low': low[i] })
        else:
            if high[i] > candles[-1].high and low[i] > candles[-1].low:
                candles.append({ 'high': high[i], 'low': low[i] })
            elif high[i] < candles[-1].high and low[i] < candles[-1].low:
                candles.append({ 'high': high[i], 'low': low[i] })
            elif high[i] <= candles[-1].high and low[i] >= candles[-1].low:
                if dir == 1:
                    candles[-1].low = low[i]
                elif dir == -1:
                    candles[-1].high = high[i]
            elif high[i] >= candles[-1].high and low[i] <= candles[-1].low:
                if dir == 1:
                    candles[-1].high = high[i]
                elif dir == -1:
                    candles[-1].low = low[i]
    if len(candles) >= 5:
        return True
    elif not strict:
        if dir == 1:
            j = 0
            for i in range(from_index - 1, 0, -1):
                if bi[i] == 1:
                    j = i
                    break
            if candles[-1].high > high[j]:
                return True
        elif dir == -1:
            j = 0
            for i in range(from_index - 1, 0, -1):
                if bi[i] == -1:
                    j = i
                    break
            if candles[-1].low < low[j]:
                return True
    return False

# 计算笔信号
# count 数据序列长度
# bi 输出的笔信号序列
# high 最高价的序列
# low 最低价的序列
def calc_bi(count, bi, high, low):
    for i in range(1, count):
        x = i - 1
        for j in range(x, 0, -1):
            if bi[j] == -1:
                x = j
                break
        # x 前底
        h = max(high[x:i])
        # h 前底到前一根K柱为止的最高价
        b1 = high[i] > h
        if b1 and is_bi(count, bi, high, low, x, i, 1, False):
            bi[i] = 1
            # 笔顶成立或者笔顶延伸
            for t in range(x + 1, i):
                bi[t] = 0


        y = i - 1
        for j in range(y, 0, -1):
            if bi[j] == 1:
                y = j
                break
        # y 前顶
        l = min(low[y:i])
        # l 前顶到前一根K柱为止的最低价
        b2 = low[i] < l
        if b2 and is_bi(count, bi, high, low, y, i, -1, False):
            bi[i] = -1
            for t in range(y + 1, i):
                bi[t] = 0
