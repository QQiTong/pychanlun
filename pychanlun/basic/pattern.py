from pychanlun.basic.comm import FindPrevEq, FindNextEq, FindPrevEntanglement


"""
判断idx前面的形态是不是看多完备形态
"""
def PerfectForBuyLong(signal_series, high_series, low_series, idx):
    d1 = FindPrevEq(signal_series, -1, idx + 1)
    g1 = FindPrevEq(signal_series, 1, d1)
    d2 = FindPrevEq(signal_series, -1, g1)
    g2 = FindPrevEq(signal_series, 1, d2)
    d3 = FindPrevEq(signal_series, -1, g2)
    if low_series[d2] > low_series[d3] and low_series[d1] > low_series[d3]:
        if low_series[d1] < (high_series[g2]+low_series[d2])/2:
            return True
    return False


"""
判断idx前面的形态是不是看跌完备形态
"""
def PerfectForSellShort(signal_series, high_series, low_series, idx):
    g1 = FindPrevEq(signal_series, 1, idx + 1)
    d1 = FindPrevEq(signal_series, -1, g1)
    g2 = FindPrevEq(signal_series, 1, d1)
    d2 = FindPrevEq(signal_series, -1, g2)
    g3 = FindPrevEq(signal_series, -1, d2)
    if high_series[g2] < high_series[g3] and high_series[g1] < high_series[g3]:
        if high_series[g1] > (high_series[g2]+low_series[d2])/2:
            return True
    return False


"""
判断是不是双盘结构，下跌中的双盘
"""
def DualEntangleForBuyLong(duan_series, entanglement_list, higher_entaglement_list, fire_time, fire_price):
    # 当前级别的中枢
    ent = FindPrevEntanglement(entanglement_list, fire_time)
    # 中枢开始的段
    if ent and ent.direction == -1:
        duan_start = FindPrevEq(duan_series, 1, ent.start)
        duan_end = FindNextEq(duan_series, -1, duan_start, len(duan_series))
        # 段的开始如果在更大级别的中枢，就是双盘
        higher_ent = FindPrevEntanglement(higher_entaglement_list, fire_time)
        if higher_ent and higher_ent.direction == -1 and duan_start > 0:
                if ent.zg >= higher_ent.zd and duan_start <= higher_ent.end and duan_start >= higher_ent.start:
                    if fire_price < (higher_ent.zg + higher_ent.zd)/2:
                        return True
    return False


"""
判断是不是双盘结构，上涨中的双盘
"""
def DualEntangleForSellShort(duan_series, entanglement_list, higher_entaglement_list, fire_time, fire_price):
    # 当前级别的中枢
    ent = FindPrevEntanglement(entanglement_list, fire_time)
    # 中枢开始的段
    if ent and ent.direction == 1:
        duan_start = FindPrevEq(duan_series, -1, ent.start)
        duan_end = FindNextEq(duan_series, 1, duan_start, len(duan_series))
        # 段的开始如果在更大级别的中枢，就是双盘
        higher_ent = FindPrevEntanglement(higher_entaglement_list, fire_time)
        if higher_ent and higher_ent.direction == 1 and duan_start > 0:
                if ent.zd <= higher_ent.zg and duan_start <= higher_ent.end and duan_start >= higher_ent.start:
                    if fire_price > (higher_ent.zg + higher_ent.zd)/2:
                        return True
    return False


"""
判断1,2,3买形态位置
"""
def BuyPosition(e_list, duan_series, bi_series, high_series, low_series, idx):
    d1 = FindPrevEq(duan_series, -1, idx+1)
    g1 = FindPrevEq(duan_series, 1, idx+1)
    d2 = FindPrevEq(duan_series, -1, g1)
    if g1 > d1:
        return 0
    e = None
    for i in range(len(e_list)-1, -1, -1):
        if e_list[i].start > idx:
            continue
        elif e_list[i].start <= idx and e_list[i].end >= idx:
            # 在中枢中
            e = e_list[i]
            break
        elif e_list[i].end < idx:
            # 找到前面的中枢
            e = e_list[i]
            break
    if e:
        if low_series[d1] > e.zg:
            return 3
        elif low_series[d1] >= low_series[d2] or low_series[idx] >= low_series[d2]:
            return 2
        else:
            return 1
    return 0
