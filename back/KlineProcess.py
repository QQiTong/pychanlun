import json
from back.Kline import Kline

class KlineRaw:
    high = None
    low = None
    time = None


# K线处理
# class Kline:
#     high = None  # kline high
#     low = None  # kline low
#     direction = None  # kline direction
#     start = None  # start kline position
#     end = None  # end kline position
#     middle = None
#     time = None
#     endTime = None


class KlineProcess:
    # origin kline list
    # klineRawList = []
    # include process kline list
    # klineList = []

    def __init__(self):
        self.klineRawList = []
        self.klineList = []


    def add(self, high, low, time):
        # origin kline
        klineRaw = KlineRaw()
        klineRaw.high = high
        klineRaw.low = low
        klineRaw.time = time
        self.klineRawList.append(klineRaw)
        if len(self.klineList) == 0:
            kline = Kline()
            kline.high = high
            kline.low = low
            kline.time = time
            kline.endTime = time

            kline.direction = 1  # 假设初始方向向上
            kline.start = 0
            kline.end = 0
            kline.middle = 0
            self.klineList.append(kline)
        else:
            lastkline = self.klineList[-1]
            if high > lastkline.high and low > lastkline.low:
                kline = Kline()
                kline.high = high
                kline.low = low
                kline.time = time
                kline.endTime = time

                kline.direction = 1
                kline.start = lastkline.end + 1
                kline.end = kline.start
                kline.middle = kline.start
                # the new kline
                self.klineList.append(kline)
            elif high < lastkline.high and low < lastkline.low:
                kline = Kline()
                kline.high = high
                kline.low = low
                kline.time = time
                kline.endTime = time
                kline.direction = -1
                kline.start = lastkline.end + 1
                kline.end = kline.start
                kline.middle = kline.start
                # the new kline
                self.klineList.append(kline)
            elif high < lastkline.high and low > lastkline.low:
                # pre include
                if lastkline.direction == 1:
                    lastkline.low = low
                else:
                    lastkline.high = high

                # lastkline.middle = lastkline.end
                lastkline.end = lastkline.end + 1
                lastkline.endTime = time

            else:
                # after include
                if lastkline.direction == 1:
                    lastkline.high = high
                else:
                    lastkline.low = low
                lastkline.end = lastkline.end + 1
                lastkline.endTime = time
                # todo 这个middle值作用:  因为经过包含处理后笔的端点不是最低点了,因此要
                lastkline.middle = lastkline.end
