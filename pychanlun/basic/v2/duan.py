import numpy as np
import pydash
import pandas as pd


def calculate_duan(klines):
    count = len(klines)
    duan = pd.Series(np.zeros(count))
    klines['duan'] = duan

    first_bi_d = pydash.find_index(klines['bi'], lambda x: x == -1)
    first_bi_g = pydash.find_index(klines['bi'], lambda x: x == 1)
    if first_bi_d == -1 or first_bi_g == -1:
        return klines

    klines.loc[first_bi_d, 'duan'] = -1
    klines.loc[first_bi_g, 'duan'] = 1
    i = max(first_bi_d, first_bi_g) + 1

    for i in range(i, count):
        if klines.loc[i, 'bi'] != 1 and klines.loc[i, 'bi'] != -1:
            continue
        G1 = pydash.find_last_index(klines.loc[:i-1, 'duan'], lambda x: x == 1)
        D1 = pydash.find_last_index(klines.loc[:i-1, 'duan'], lambda x: x == -1)
        if G1 > D1:
            # 最近已确认的线段是向上线段
            if klines.loc[i, 'bi'] == 1:
                # 遇到笔的高点
                if klines.loc[i, 'high'] > klines.loc[G1, 'high']:
                    # 笔高点创了新高，原线段继续延伸
                    klines.loc[G1, 'duan'] = 0
                    klines.loc[i, 'duan'] = 1
            elif klines.loc[i, 'bi'] == -1:
                # 遇到笔的低点
                if klines.loc[i, 'low'] < klines.loc[D1, 'low']:
                    # 笔低点反向直接破线段最低点了，直接确认段成立，就算只有一笔，该笔也升级成段
                    klines.loc[i, 'duan'] = -1
                else:
                    # i1 反向的第一个低点
                    i1 = pydash.find_index(klines.loc[G1+1:i-1, 'bi'], lambda x: x == -1)
                    if i1 >= 0 and i > i1:
                        # 前面已出现了反向的第一个低点
                        if klines.loc[i, 'low'] < klines.loc[i1, 'low']:
                            # 破坏了反向的第一个低点，直接确认线段成立了。
                            klines.loc[i, 'duan'] = -1
                        else:
                            # 没有破坏第一个低点的情况，如果最近的下上下符合线段条件，那么也确认线段的成立。
                            # 处理前面可能有笔可以升级成段的情况。
                            d1 = i
                            g1 = pydash.find_last_index(klines.loc[:d1-1, 'bi'], lambda x: x == 1)
                            d2 = pydash.find_last_index(klines.loc[:g1-1, 'bi'], lambda x: x == -1)
                            g2 = pydash.find_last_index(klines.loc[:d2-1, 'bi'], lambda x: x == 1)
                            if klines.loc[d1, 'low'] < klines.loc[d2, 'low'] and klines.loc[g1, 'high'] <= klines.loc[g2, 'high']:
                                i2 = i1
                                for x in range(i1, i+1):
                                    if klines.loc[x, 'low'] < klines.loc[i2, 'low']:
                                        i2 = x
                                klines.loc[i2, 'duan'] = -1
                                if i2 < i:
                                    i = i2
        else:
            # 最近已确认的线段是向下线段
            if klines.loc[i, 'bi'] == -1:
                # 遇到笔的低点
                if klines.loc[i, 'low'] < klines.loc[D1, 'low']:
                    # 笔低点创新低，原来线段继续延伸
                    klines.loc[D1, 'duan'] = 0
                    klines.loc[i, 'duan'] = -1
            elif klines.loc[i, 'bi'] == 1:
                # 遇到笔的高点
                if klines.loc[i, 'high'] > klines.loc[G1, 'high']:
                    # 笔高点直接破前面段高点了，笔升级为段
                    klines.loc[i, 'duan'] = 1
                else:
                    # i1 反向的第一个高点
                    i1 = pydash.find_index(klines.loc[D1+1:i-1, 'bi'], lambda x: x == 1)
                    if i1 >= 0 and i > i1:
                        if klines.loc[i, 'high'] > klines.loc[i1, 'high']:
                            # 破坏反向的第一个高点，线段就确认成立了。
                            klines.loc[i, 'duan'] = 1
                        else:
                            # 没有破坏第一个高点的情况，如果最近的上下上符合线段条件，那么也确认线段的成立。
                            # 处理前面可能有笔可以升级成段的情况。
                            g1 = i
                            d1 = pydash.find_last_index(klines.loc[:g1-1, 'bi'], lambda x: x == -1)
                            g2 = pydash.find_last_index(klines.loc[:d1-1, 'bi'], lambda x: x == 1)
                            d2 = pydash.find_last_index(klines.loc[:g2-1, 'bi'], lambda x: x == -1)
                            if klines.loc[g1, 'high'] > klines.loc[g2, 'high'] and klines.loc[d1, 'low'] >= klines.loc[d2, 'low']:
                                i2 = i1
                                for x in range(i1, i+1):
                                    if klines.loc[x, 'high'] > klines.loc[i2, 'high']:
                                        i2 = x
                                klines.loc[i2, 'duan'] = 1
                                if i2 < i:
                                    i = i2
    return klines
