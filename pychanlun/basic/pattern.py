from pychanlun.basic.comm import FindPrevEq


"""
判断idx前面的形态是不是看多完备形态
"""
def PerfectForBuyLong(signal_series, high_series, low_series, idx):
    d1 = FindPrevEq(signal_series, -1, idx)
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
    g1 = FindPrevEq(signal_series, 1, idx)
    d1 = FindPrevEq(signal_series, -1, g1)
    g2 = FindPrevEq(signal_series, 1, d1)
    d2 = FindPrevEq(signal_series, -1, g2)
    g3 = FindPrevEq(signal_series, -1, d2)
    if high_series[g2] < high_series[g3] and high_series[g1] < high_series[g3]:
        if high_series[g1] > (high_series[g2]+low_series[d2])/2:
            return True
    return False

