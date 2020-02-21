from pychanlun.basic.comm import FindPrevEq, FindNextEq, FindPrevEntanglement
from pychanlun.basic.pivot import FindPivots
import pydash

"""
判断idx前面的形态是不是看多完备形态
"""
def PerfectForBuyLong(signal_serial, high_serial, low_serial, idx):
    d1 = FindPrevEq(signal_serial, -1, idx + 1)
    g1 = FindPrevEq(signal_serial, 1, d1)
    d2 = FindPrevEq(signal_serial, -1, g1)
    g2 = FindPrevEq(signal_serial, 1, d2)
    d3 = FindPrevEq(signal_serial, -1, g2)
    if low_serial[d2] > low_serial[d3] and low_serial[d1] > low_serial[d3]:
        if low_serial[d1] < low_serial[idx] < (high_serial[g2]+low_serial[d2])/2:
            return True
    return False


"""
判断idx前面的形态是不是看跌完备形态
"""
def PerfectForSellShort(signal_serial, high_serial, low_series, idx):
    g1 = FindPrevEq(signal_serial, 1, idx + 1)
    d1 = FindPrevEq(signal_serial, -1, g1)
    g2 = FindPrevEq(signal_serial, 1, d1)
    d2 = FindPrevEq(signal_serial, -1, g2)
    g3 = FindPrevEq(signal_serial, -1, d2)
    if high_serial[g2] < high_serial[g3] and high_serial[g1] < high_serial[g3]:
        if high_serial[g1] > high_serial[idx] > (high_serial[g2]+low_series[d2])/2:
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
判断1, 2, 3买形态位置
"""
def BuyCategory(high_duan_serial, duan_serial, high_serial, low_serial, idx):
    dd1 = FindPrevEq(high_duan_serial, -1, idx + 1)
    gg1 = FindPrevEq(high_duan_serial, 1, idx + 1)
    d1 = FindPrevEq(duan_serial, -1, idx + 1)
    g1 = FindPrevEq(duan_serial, 1, idx + 1)
    category = 0
    if dd1 > gg1:
        if d1 > g1:
            category = 2
        pivots = FindPivots(gg1, dd1, duan_serial, high_serial, low_serial, -1)
        if len(pivots) > 0:
            minZg = pydash.chain(pivots).map(lambda pivot: pivot['high']).min().value()
            if low_serial[d1] > minZg:
                category = 3
    else:
        pass
    return category
