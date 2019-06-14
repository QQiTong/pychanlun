from back.ZhongShu import ZhongShu


class ZhongShuProcess:
    def initHigh(self, biResult, highList, lowList):
        nCount = len(highList)
        result = [0 for i in range(nCount)]
        zhongShuOne = ZhongShu()
        for i in range(nCount):
            if biResult[i] == 1:
                # 遇到线段高点，推入中枢算法
                if zhongShuOne.pushHigh(i, highList[i]):
                    bValid = True
                    fHighValue = 0
                    nHignIndex = 0
                    nLowIndex = 0
                    nLowIndexTemp = 0
                    nHighCount = 0
                    # 向上中枢被向下终结
                    if zhongShuOne.nDirection == 1 and zhongShuOne.nTerminate == -1:
                        bValid = False
                        for x in range(zhongShuOne.nStart, zhongShuOne.nEnd + 1, 1):
                            if biResult[x] == 1:
                                if nHighCount == 0:
                                    nHighCount = nHighCount + 1
                                    fHighValue = highList[x]
                                    nHignIndex = x
                                else:
                                    nHighCount = nHighCount + 1
                                    if highList[x] >= fHighValue:
                                        if nHighCount > 2:
                                            bValid = True
                                        fHighValue = highList[x]
                                        nHignIndex = x
                                        nLowIndex = nLowIndexTemp
                            elif biResult[x] == -1:
                                nLowIndexTemp = x
                        if bValid:
                            # 中枢结束点移到最高点的前一个低点。
                            zhongShuOne.nEnd = nLowIndex
                        i = nHignIndex - 1
                    else:
                        i = zhongShuOne.nEnd - 1
                    if bValid:
                        # 区段内更新算得的中枢高数据
                        for j in range(zhongShuOne.nStart + 1, zhongShuOne.nEnd, 1):
                            result[j] = zhongShuOne.fHigh
                    zhongShuOne.reset()
            elif biResult[i] == -1:
                # 遇到线段低点，推入中枢算法
                if zhongShuOne.pushLow(i, lowList[i]):
                    bValid = True
                    fLowValue = 0
                    nLowIndex = 0
                    nHighIndex = 0
                    nHighIndexTemp = 0
                    nLowCount = 0
                    if zhongShuOne.nDirection == -1 and zhongShuOne.nTerminate == 1:
                        # 向下中枢被向上终结
                        bValid = False
                        for x in range(zhongShuOne.nStart, zhongShuOne.nEnd + 1, 1):
                            if biResult[x] == -1:
                                if nLowCount == 0:
                                    nLowCount = nLowCount + 1
                                    fLowValue = lowList[x]
                                    nLowIndex = x
                                else:
                                    nLowCount = nLowCount + 1
                                    if lowList[x] <= fLowValue:
                                        if nLowCount > 2:
                                            bValid = True
                                        fLowValue = lowList[x]
                                        nLowIndex = x
                                        nHighIndex = nHighIndexTemp
                            elif biResult[x] == 1:
                                nHighIndexTemp = x
                        if bValid:
                            # 中枢结束点移到最高点的前一个低点。
                            zhongShuOne.nEnd = nHighIndex
                        i = nLowIndex - 1
                    else:
                        i = zhongShuOne.nEnd - 1
                    if bValid:
                        # 区段内更新算得的中枢高数据
                        for j in range(zhongShuOne.nStart + 1, zhongShuOne.nEnd, 1):
                            result[j] = zhongShuOne.fHigh
                    zhongShuOne.reset()
        # 最后一个还没有被终结的中枢。
        if zhongShuOne.bValid:
            # 区段内更新算得的中枢高数据
            for j in range(zhongShuOne.nStart + 1, zhongShuOne.nEnd, 1):
                result[j] = zhongShuOne.fHigh
        return result

    # 计算zhongshu低点数据
    def initLow(self, biResult, highList, lowList):
        nCount = len(highList)
        result = [0 for i in range(nCount)]
        zhongShuOne = ZhongShu()

        for i in range(nCount):
            if biResult[i] == 1:
                # 遇到线段高点，推入中枢算法
                if zhongShuOne.pushHigh(i, highList[i]):
                    bValid = True
                    fHighValue = 0
                    nHignIndex = 0
                    nLowIndex = 0
                    nLowIndexTemp = 0
                    nHighCount = 0
                    # 向上中枢被向下终结
                    if zhongShuOne.nDirection == 1 and zhongShuOne.nTerminate == -1:
                        bValid = False
                        for x in range(zhongShuOne.nStart, zhongShuOne.nEnd + 1, 1):
                            if biResult[x] == 1:
                                if nHighCount == 0:
                                    nHighCount = nHighCount + 1
                                    fHighValue = highList[x]
                                    nHignIndex = x
                                else:
                                    nHighCount = nHighCount + 1
                                    if highList[x] >= fHighValue:
                                        if nHighCount > 2:
                                            bValid = True
                                        fHighValue = highList[x]
                                        nHignIndex = x
                                        nLowIndex = nLowIndexTemp
                            elif biResult[x] == -1:
                                nLowIndexTemp = x
                        if bValid:
                            # 中枢结束点移到最高点的前一个低点。
                            zhongShuOne.nEnd = nLowIndex
                        i = nHignIndex - 1
                    else:
                        i = zhongShuOne.nEnd - 1
                    if bValid:
                        # 区段内更新算得的中枢低数据
                        for j in range(zhongShuOne.nStart + 1, zhongShuOne.nEnd, 1):
                            result[j] = zhongShuOne.fLow
                    zhongShuOne.reset()
            elif biResult[i] == -1:
                # 遇到线段低点，推入中枢算法
                if zhongShuOne.pushLow(i, lowList[i]):
                    bValid = True
                    fLowValue = 0
                    nLowIndex = 0
                    nHighIndex = 0
                    nHighIndexTemp = 0
                    nLowCount = 0
                    # 向下中枢被向上终结
                    if zhongShuOne.nDirection == -1 and zhongShuOne.nTerminate == 1:
                        bValid = False
                        for x in range(zhongShuOne.nStart, zhongShuOne.nEnd + 1, 1):
                            if biResult[x] == -1:
                                if nLowCount == 0:
                                    nLowCount = nLowCount + 1
                                    fLowValue = lowList[x]
                                    nLowIndex = x
                                else:
                                    nLowCount = nLowCount + 1
                                    if lowList[x] <= fLowValue:
                                        if nLowCount > 2:
                                            bValid = True
                                        fLowValue = lowList[x]
                                        nLowIndex = x
                                        nHighIndex = nHighIndexTemp
                            elif biResult[x] == 1:
                                nHighIndexTemp = x
                        if bValid:
                            # 中枢结束点移到最高点的前一个低点。
                            zhongShuOne.nEnd = nHighIndex
                        i = nLowIndex - 1
                    else:
                        i = zhongShuOne.nEnd - 1
                    if bValid:
                        # 区段内更新算得的中枢低数据
                        for j in range(zhongShuOne.nStart + 1, zhongShuOne.nEnd, 1):
                            result[j] = zhongShuOne.fLow
                    zhongShuOne.reset()
        if zhongShuOne.bValid:
            # 区段内更新算得的中枢低数据
            for j in range(zhongShuOne.nStart + 1, zhongShuOne.nEnd, 1):
                result[j] = zhongShuOne.fLow
        return result

    def initStartEnd(self, biResult, highList, lowList):
        nCount = len(highList)
        result = [0 for i in range(nCount)]
        zhongShuOne = ZhongShu()
        for i in range(nCount):
            if biResult[i] == 1:
                # 遇到线段高点，推入中枢算法
                if zhongShuOne.pushHigh(i, highList[i]):
                    print("中枢终结", highList[i])
                    bValid = True
                    fHighValue = 0
                    nHignIndex = 0
                    nLowIndex = 0
                    nLowIndexTemp = 0
                    nHighCount = 0
                    # 向上中枢被向下终结
                    if zhongShuOne.nDirection == 1 and zhongShuOne.nTerminate == -1:
                        print("向上中枢被向下终结")
                        bValid = False
                        for x in range(zhongShuOne.nStart, zhongShuOne.nEnd + 1, 1):
                            if biResult[x] == 1:
                                if nHighCount == 0:
                                    nHighCount = nHighCount + 1
                                    fHighValue = highList[x]
                                    nHignIndex = x
                                else:
                                    nHighCount = nHighCount + 1
                                    if highList[x] >= fHighValue:
                                        if nHighCount > 2:
                                            bValid = True
                                        fHighValue = highList[x]
                                        nHignIndex = x
                                        nLowIndex = nLowIndexTemp
                            elif biResult[x] == -1:
                                nLowIndexTemp = x
                        if bValid:
                            print("同级别分解保留最后中枢")
                            print('中枢结束点移到', lowList[nLowIndex])
                            # 中枢结束点移到最高点的前一个低点。
                            zhongShuOne.nEnd = nLowIndex
                        else:
                            print("同级别分解最后中枢无效")
                        i = nHignIndex - 1
                    else:
                        print("向下中枢被向下终结")
                        i = zhongShuOne.nEnd - 1
                    if bValid:
                        # 进行标记
                        result[zhongShuOne.nStart + 1] = 1
                        result[zhongShuOne.nEnd - 1] = 2
                    zhongShuOne.reset()
            elif biResult[i] == -1:
                # 遇到线段低点，推入中枢算法
                if zhongShuOne.pushLow(i, lowList[i]):
                    print("中枢终结", highList[i])
                    bValid = True
                    fLowValue = 0
                    nLowIndex = 0
                    nHighIndex = 0
                    nHighIndexTemp = 0
                    nLowCount = 0
                    # 向下中枢被向上终结
                    if zhongShuOne.nDirection == -1 and zhongShuOne.nTerminate == 1:
                        print("向下中枢被向上终结")
                        bValid = False
                        for x in range(zhongShuOne.nStart, zhongShuOne.nEnd + 1, 1):
                            if biResult[x] == -1:
                                if nLowCount == 0:
                                    nLowCount = nLowCount + 1
                                    fLowValue = lowList[x]
                                    nLowIndex = x
                                else:
                                    nLowCount = nLowCount + 1
                                    if lowList[x] <= fLowValue:
                                        if nLowCount > 2:
                                            bValid = True
                                        fLowValue = lowList[x]
                                        nLowIndex = x
                                        nHighIndex = nHighIndexTemp
                                print('低点数量', nLowCount)
                            elif biResult[x] == 1:
                                nHighIndexTemp = x
                        if bValid:
                            print("同级别分解保留最后中枢")
                            print("中枢结束点移到", highList[nHighIndex])
                            # 中枢结束点移到最高点的前一个低点
                            zhongShuOne.nEnd = nHighIndex;
                        else:
                            print("同级别分解最后中枢无效")
                        i = nLowIndex - 1;
                    else:
                        print("向上中枢被向上终结")
                        i = zhongShuOne.nEnd - 1
                    if bValid:
                        # 进行标记
                        result[zhongShuOne.nStart + 1] = 1
                        result[zhongShuOne.nEnd - 1] = 2
                    zhongShuOne.reset()
        if zhongShuOne.bValid:
            # 进行标记
            result[zhongShuOne.nStart + 1] = 1
            result[zhongShuOne.nEnd - 1] = 2
        return result
