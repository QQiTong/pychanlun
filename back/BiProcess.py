from back.ToString import ToString
from back.Tools import Tools


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

    def ifChengbi(self, tempKxianList, direction):
        if len(tempKxianList) < 4:
            # if there is no 4 kline must not bi
            return False
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
                    return False
                # find previous lowest price
                lowestPrice = tempKxianList[i].low
                # if there is lower than lowest price , then become bi
                for j in range(i + 1, len(tempKxianList), 1):
                    if tempKxianList[j].low < lowestPrice:
                        return True
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
                    return False
                # find previous highest price
                highestPrice = tempKxianList[i].low
                # if there is higher than highest price , then become bi
                for j in range(i + 1, len(tempKxianList), 1):
                    if tempKxianList[j].high > highestPrice:
                        return True
                i = i + 1
        return False

    def handle(self, klineList):
        tempklineList = []
        count = len(klineList)
        for i in range(count):
            item = klineList[i]
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
                    if item.high >= lastBi.high:
                        lastBi.high = item.high
                        lastBi.end = item.end
                        # previous not become bi
                        if len(tempklineList) > 0:
                            for j in range(len(tempklineList)):
                                # if tempklineList[j].low < lastBi.low:
                                #     if len(self.biList) > 1:
                                #         # merge last bi into last last bi
                                #         lastLastBi = self.biList[-2]
                                #         for x in range(len(lastBi.klineList)):
                                #             lastLastBi.klineList.append(lastBi.klineList[x])
                                #         lastBi = lastLastBi
                                #         lastBi.low = tempklineList[j].low
                                lastBi.klineList.append(tempklineList[j])
                            tempklineList.clear()
                        lastBi.klineList.append(item)
                    else:
                        tempklineList.append(item)
                        # whether has new down bi
                        if self.ifChengbi(tempklineList, -1):
                            bi = Bi()
                            bi.direction = -1
                            bi.start = lastBi.end
                            bi.end = tempklineList[-1].end
                            bi.low = tempklineList[-1].low
                            bi.high = lastBi.high
                            for k in range(len(tempklineList)):
                                bi.klineList.append(tempklineList[k])
                            tempklineList.clear()
                            self.biList.append(bi)
                elif lastBi.direction == -1:
                    # previous bi is down bi
                    # down bi continue
                    if item.low <= lastBi.low:
                        lastBi.low = item.low
                        lastBi.end = item.end
                        if len(tempklineList) > 0:
                            for l in range(len(tempklineList)):
                                # if tempklineList[l].high > lastBi.high:
                                #     if len(self.biList) > 1:
                                #         # merge last bi into last last bi
                                #         lastLastBi = self.biList[-2]
                                #         for x in range(len(lastBi.klineList)):
                                #             lastLastBi.klineList.append(lastBi.klineList[x])
                                #         lastBi = lastLastBi
                                #         lastBi.high = tempklineList[j].high
                                lastBi.klineList.append(tempklineList[l])
                            tempklineList.clear()
                        lastBi.klineList.append(item)
                    else:
                        tempklineList.append(item)
                        if self.ifChengbi(tempklineList, 1):
                            bi = Bi()
                            bi.direction = 1
                            bi.start = lastBi.end
                            bi.end = tempklineList[-1].end
                            bi.high = tempklineList[-1].high
                            bi.low = lastBi.low
                            for m in range(len(tempklineList)):
                                bi.klineList.append(tempklineList[m])
                            tempklineList.clear()
                            self.biList.append(bi)
        lastBi = self.biList[-1]
        # todo 循环结束了tempKxianList还有值?
        if len(tempklineList) >= 4:
            if lastBi.direction == 1:
                if self.ifChengbi(tempklineList, -1):
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
                if self.ifChengbi(tempklineList, 1):
                    bi = Bi()
                    bi.direction = 1
                    bi.start = lastBi.end
                    bi.end = tempklineList[-1].end
                    bi.high = tempklineList[-1].high
                    bi.low = lastBi.low
                    for i in range(len(tempklineList)):
                        bi.klineList.append(tempklineList[i])
                    tempklineList.clear()
                    self.biList.append(bi)
