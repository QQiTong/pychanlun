from back.ToString import ToString
from back.Tools import Tools
import numpy as np

class Bi(ToString):
    direction = None  # direction
    start = None  # bi start
    end = None  # bi end
    high = None  # bi high price
    low = None  # bi low price

    # klineList = []  # bi 's kline list
    def __init__(self):
        self.klineList = []


class BiProcess(ToString):
    # 此处biList 如果直接写 类的成员变量会报错
    # biList = []
    def __init__(self):
        self.biList = []

    def mergeBi(self):
        count = len(self.biList)
        if (count >= 4 and self.biList[-2].biType == "Dummy"):
            dummyBi = self.biList[-2]
            if dummyBi.direction == 1:
                dummyBiLow = dummyBi.low
                iMerge = -1
                i = count - 4
                if self.biList[i].low <= dummyBiLow:
                    iMerge = i
                # 从iMerge笔开始合并
                if iMerge > -1:
                    bi = self.biList[i]
                    for j in range(i + 1, count - 1):
                        bi2 = self.biList[j]
                        for x in range(len(bi2.klineList)):
                            bi.klineList.append(bi2.klineList[x])
                        if bi2.high > bi.high:
                            bi.high = bi2.high
                        bi.end = bi2.end
                    for d in range(count - 2, i, -1):
                        del self.biList[d]
            elif dummyBi.direction == -1:
                dummyBiHigh = dummyBi.high
                iMerge = -1
                i = count - 4
                if self.biList[i].high >= dummyBiHigh:
                    iMerge = i
                # 从iMerge笔开始合并
                if iMerge > -1:
                    bi = self.biList[i]
                    for j in range(i + 1, count - 1):
                        bi2 = self.biList[j]
                        for x in range(len(bi2.klineList)):
                            bi.klineList.append(bi2.klineList[x])
                        if bi2.low > bi.low:
                            bi.low = bi2.low
                        bi.end = bi2.end
                    for d in range(count - 2, i, -1):
                        del self.biList[d]


    # 为了能调整笔的高低点，有时候我们需要把不满足条件的情况也零时算一笔
    def isDummyBi(self, tempKxianList, direction):
        if direction == -1:
            # 向下运行时候，如果比前一笔的最低点还低了，临时先算它为一笔
            if len(tempKxianList) > 0 and len(self.biList) > 0 and tempKxianList[-1].low < self.biList[-1].low:
                return True
        if direction == 1:
            # 向上运行时候，如果比前一笔的最高点还高了，零时先算它为一笔
            if len(tempKxianList) > 0 and len(self.biList) > 0 and tempKxianList[-1].high > self.biList[-1].high:
                return True
        return False

    def isChengbi(self, tempKxianList, direction):
        if len(tempKxianList) < 4:
            # if there is no 4 kline must not bi
            return (True, 'Dummy') if self.isDummyBi(tempKxianList, direction) else (False, None)

        if direction == -1:
            # whether become down bi
            # first to find if there is down kline
            i = 2
            while True:
                while i < len(tempKxianList):
                    if tempKxianList[i].low < tempKxianList[i - 1].low < tempKxianList[i - 2].low:
                        break
                    i = i + 1
                if i >= len(tempKxianList):
                    return (True, 'Dummy') if self.isDummyBi(tempKxianList, direction) else (False, None)
                # find previous lowest price
                lowestPrice = tempKxianList[i].low
                # if there is lower than lowest price , then become bi
                for j in range(i + 1, len(tempKxianList), 1):
                    if tempKxianList[j].low < lowestPrice:
                        return True, 'Formal'
                i = i + 1
        elif direction == 1:
            i = 2
            while True:
                # for j in range(i, len(tempKxianList), 1):
                while i < len(tempKxianList):
                    if tempKxianList[i].high > tempKxianList[i - 1].high > tempKxianList[i - 2].high:
                        break
                    i = i + 1
                if i >= len(tempKxianList):
                    return (True, 'Dummy') if self.isDummyBi(tempKxianList, direction) else (False, None)
                # find previous highest price
                highestPrice = tempKxianList[i].high
                # if there is higher than highest price , then become bi
                for j in range(i + 1, len(tempKxianList), 1):
                    if tempKxianList[j].high > highestPrice:
                        return True, 'Formal'
                i = i + 1
        return (True, 'Dummy') if self.isDummyBi(tempKxianList, direction) else (False, None)

    def handle(self, klineList):
        tempklineList = []
        count = len(klineList)
        for i in range(count):
            item = klineList[i]
            item.i = i # 记录下索引后面有需要用到
            if len(self.biList) == 0:
                # create first bi ,suppose first bi is up
                bi = Bi()
                bi.direction = 1
                bi.start = item.start
                bi.end = item.end
                bi.high = item.high
                bi.low = item.low
                bi.klineList.append(item)
                self.biList.append(bi)
                # Tools.prn_obj(item)
            else:
                lastBi = self.biList[-1]
                # previous bi is up
                if lastBi.direction == 1:
                    # up bi continue
                    if item.maxHigh >= lastBi.high:
                        lastBi.high = item.maxHigh
                        lastBi.end = item.end
                        # previous not become bi
                        if len(tempklineList) > 0:
                            for j in range(len(tempklineList)):
                                lastBi.klineList.append(tempklineList[j])
                            tempklineList.clear()
                        lastBi.klineList.append(item)
                    else:
                        tempklineList.append(item)
                        # whether has new down bi
                        biResult, biType = self.isChengbi(tempklineList, -1)
                        if biResult:
                            bi = Bi()
                            bi.biType = biType
                            bi.direction = -1
                            bi.start = lastBi.end
                            bi.end = tempklineList[-1].end
                            bi.low = tempklineList[-1].low
                            bi.high = lastBi.high
                            for k in range(len(tempklineList)):
                                bi.klineList.append(tempklineList[k])
                            tempklineList.clear()
                            self.biList.append(bi)
                            # self.mergeBi()
                elif lastBi.direction == -1:
                    # previous bi is down bi
                    # down bi continue
                    if item.maxLow <= lastBi.low:
                        lastBi.low = item.maxLow
                        lastBi.end = item.end
                        if len(tempklineList) > 0:
                            for l in range(len(tempklineList)):
                                lastBi.klineList.append(tempklineList[l])
                            tempklineList.clear()
                        lastBi.klineList.append(item)
                    else:
                        tempklineList.append(item)
                        biResult, biType = self.isChengbi(tempklineList, 1)
                        if biResult:
                            bi = Bi()
                            bi.biType = biType
                            bi.direction = 1
                            bi.start = lastBi.end
                            bi.end = tempklineList[-1].end
                            bi.high = tempklineList[-1].high
                            bi.low = lastBi.low
                            for m in range(len(tempklineList)):
                                bi.klineList.append(tempklineList[m])
                            tempklineList.clear()
                            self.biList.append(bi)
                            # self.mergeBi()
        lastBi = self.biList[-1]
        # todo 循环结束了tempKxianList还有值?
        if len(tempklineList) >= 4:
            if lastBi.direction == 1:
                biResult, biType = self.isChengbi(tempklineList, -1)
                if biResult:
                    bi.biType = biType
                    bi = Bi()
                    bi.direction = -1
                    bi.start = lastBi.end
                    bi.end = tempklineList[-1].end
                    bi.low = tempklineList[-1].low
                    bi.high = lastBi.high
                    for i in range(len(tempklineList)):
                        bi.klineList.append(tempklineList[i])
                    tempklineList.clear()
                    self.biList.append(tempklineList)
            elif lastBi.direction == -1:
                biResult, biType = self.isChengbi(tempklineList, 1)
                if biResult:
                    bi = Bi()
                    bi.biType = biType
                    bi.direction = 1
                    bi.start = lastBi.end
                    bi.end = tempklineList[-1].end
                    bi.high = tempklineList[-1].high
                    bi.low = lastBi.low
                    for i in range(len(tempklineList)):
                        bi.klineList.append(tempklineList[i])
                    tempklineList.clear()
                    self.biList.append(bi)

    def biResult(self, count):
        r = np.zeros(count, dtype=np.int)
        for i in range(len(self.biList)):
            bi = self.biList[i]
            r[bi.klineList[-1].middle] = bi.direction
        return r
