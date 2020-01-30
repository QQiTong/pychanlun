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
    if ent:
        duan_start = FindPrevEq(duan_series, 1, ent.start)
        duan_end = FindNextEq(duan_series, -1, duan_start, len(duan_series))
        # 段的开始如果在更大级别的中枢，就是双盘
        higher_ent = FindPrevEntanglement(higher_entaglement_list, fire_time)
        if higher_ent and duan_start > 0:
                if duan_start <= higher_ent.end and duan_start >= higher_ent.start:
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
    if ent:
        duan_start = FindPrevEq(duan_series, -1, ent.start)
        duan_end = FindNextEq(duan_series, 1, duan_start, len(duan_series))
        # 段的开始如果在更大级别的中枢，就是双盘
        higher_ent = FindPrevEntanglement(higher_entaglement_list, fire_time)
        if higher_ent and duan_start > 0:
                if duan_start <= higher_ent.end and duan_start >= higher_ent.start:
                    if fire_price > (higher_ent.zg + higher_ent.zd)/2:
                        return True
    return False
