# -*- coding: utf-8 -*-

from pychanlun.basic.comm import FindPrevEq, FindNextEq
from datetime import datetime
import pytz

tz = pytz.timezone('Asia/Shanghai')

def CalcDuan(count, duan, bi, high, low):
    firstBiD = FindNextEq(bi, -1, 0, count)
    firstBiG = FindNextEq(bi, 1, 0, count)
    if firstBiD == -1 or firstBiG == -1:
        return
    duan[firstBiD] = -1
    duan[firstBiG] = 1
    i = max(firstBiD, firstBiG) + 1
    for i in range(i, count):
        if bi[i] != 1 and bi[i] != -1:
            continue
        G1 = FindPrevEq(duan, 1, i)
        D1 = FindPrevEq(duan, -1, i)
        if G1 > D1:
            # 最近已确认的线段是向上线段
            if bi[i] == 1:
                # 遇到笔的高点
                if high[i] > high[G1]:
                    # 笔高点创了新高，原线段继续延伸
                    duan[G1] = 0
                    duan[i] = 1
            elif bi[i] == -1:
                # 遇到笔的低点
                if low[i] < low[D1]:
                    # 笔低点反向直接破线段最低点了，直接确认段成立，就算只有一笔，该笔也升级成段
                    duan[i] = -1
                else:
                    # i1 反向的第一个低点
                    i1 = FindNextEq(bi, -1, G1 + 1, i)
                    if i1 >= 0 and i > i1:
                        # 前面已出现了反向的第一个低点
                        if low[i] < low[i1]:
                            # 破坏了反向的第一个低点，直接确认线段成立了。
                            duan[i] = -1
                        else:
                            # 没有破坏第一个低点的情况，如果最近的下上下符合线段条件，那么也确认线段的成立。
                            # 处理前面可能有笔可以升级成段的情况。
                            d1 = i
                            g1 = FindPrevEq(bi, 1, d1)
                            d2 = FindPrevEq(bi, -1, g1)
                            g2 = FindPrevEq(bi, 1, d2)
                            if low[d1] < low[d2] and high[g1] <= high[g2]:
                                i2 = i1
                                for x in range(i1, i+1):
                                    if low[x] < low[i2]:
                                        i2 = x
                                duan[i2] = -1
                                if i2 < i:
                                    i = i2
        else:
            # 最近已确认的线段是向下线段
            if bi[i] == -1:
                # 遇到笔的低点
                if low[i] < low[D1]:
                    # 笔低点创新低，原来线段继续延伸
                    duan[D1] = 0
                    duan[i] = -1
            elif bi[i] == 1:
                # 遇到笔的高点
                if high[i] > high[G1]:
                    # 笔高点直接破前面段高点了，笔升级为段
                    duan[i] = 1
                else:
                    # i1 反向的第一个高点
                    i1 = FindNextEq(bi, 1, D1 + 1, i)
                    if i1 >= 0 and i > i1:
                        if high[i] > high[i1]:
                            # 破坏反向的第一个高点，线段就确认成立了。
                            duan[i] = 1
                        else:
                            # 没有破坏第一个高点的情况，如果最近的上下上符合线段条件，那么也确认线段的成立。
                            # 处理前面可能有笔可以升级成段的情况。
                            g1 = i
                            d1 = FindPrevEq(bi, -1, g1)
                            g2 = FindPrevEq(bi, 1, d1)
                            d2 = FindPrevEq(bi, -1, g2)
                            if high[g1] > high[g2] and low[d1] >= low[d2]:
                                i2 = i1
                                for x in range(i1, i+1):
                                    if high[x] > high[i2]:
                                        i2 = x
                                duan[i2] = 1
                                if i2 < i:
                                    i = i2

def CalcDuanExp(count, duanList, biListBigLevel, timeIndexListBigLevel, timeIndexList, highList, lowList, bigLevelPeriod=""):
    idx = 0
    for i in range(len(biListBigLevel)):
        if i < len(timeIndexListBigLevel) - 2:
            bigT2 = timeIndexListBigLevel[i+1]
        else:
            bigT2 = datetime.now(tz=tz).timestamp()
        # if bigLevelPeriod == "1d" or bigLevelPeriod == "3d":
            # bigT2 = bigT2 + 64800
        if biListBigLevel[i] == 1:
            h = highList[idx]
            x = idx
            for x in range(idx, count):
                if timeIndexList[x] < bigT2:
                    if highList[x] >= h:
                        h = highList[x]
                        idx = x
                else:
                    break
            duanList[idx] = 1
        elif biListBigLevel[i] == -1:
            l = lowList[idx]
            x = idx
            for x in range(idx, count):
                if timeIndexList[x] < bigT2:
                    if lowList[x] <= l:
                        l = lowList[x]
                        idx = x
                else:
                    break
            duanList[idx] = -1
