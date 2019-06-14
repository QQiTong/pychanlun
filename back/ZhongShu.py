class ZhongShu:
    def __init__(self):
        self.bValid = False
        self.nTop1 = 0
        self.nTop2 = 0
        self.nTop3 = 0
        self.nBot1 = 0
        self.nBot2 = 0
        self.nBot3 = 0
        self.fTop1 = 0
        self.fTop2 = 0
        self.fTop3 = 0
        self.fBot1 = 0
        self.fBot2 = 0
        self.fBot3 = 0
        self.nLines = 0
        self.nStart = 0
        self.nEnd = 0
        self.fHigh = 0
        self.fLow = 0
        self.fPHigh = 0
        self.fPLow = 0
        self.nDirection = 0
        self.nTerminate = 0

    def reset(self):
        self.bValid = False
        self.nTop1 = 0
        self.nTop2 = 0
        self.nTop3 = 0
        self.nBot1 = 0
        self.nBot2 = 0
        self.nBot3 = 0
        self.fTop1 = 0
        self.fTop2 = 0
        self.fTop3 = 0
        self.fBot1 = 0
        self.fBot2 = 0
        self.fBot3 = 0
        self.nLines = 0
        self.nStart = 0
        self.nEnd = 0
        self.fHigh = 0
        self.fLow = 0
        self.nDirection = 0
        self.nTerminate = 0

    # 推入高点并计算状态
    def pushHigh(self, nIndex, fValue):
        self.nTop3 = self.nTop2
        self.fTop3 = self.fTop2
        self.nTop2 = self.nTop1
        self.fTop2 = self.fTop1
        self.nTop1 = nIndex
        self.fTop1 = fValue
        if self.bValid:
            if self.fTop1 < self.fLow:  # 中枢终结
                self.nTerminate = -1
                if self.nTop2 > self.nEnd:
                    self.nEnd = self.nTop2
                return True
            else:
                if self.nBot1 > self.nEnd:
                    self.nEnd = self.nBot1  # 中枢终结点后移
        else:
            # 有两个高点和两个低点
            if self.nTop3 > 0 and self.nTop2 > 0 and self.nTop1 > 0 and self.nBot2 > 0 and self.nBot1 > 0:
                fTempHigh = self.fTop1 if self.fTop1 < self.fTop2 else self.fTop2
                fTempLow = self.fBot1 if self.fBot1 > self.fBot2 else self.fBot2
                if self.fTop3 > self.fTop2 and fTempHigh > fTempLow:  # 有中枢
                    self.nDirection = -1  # 向下中枢
                    self.nStart = self.nBot2
                    self.nEnd = self.nTop1
                    self.fHigh = fTempHigh
                    self.fLow = fTempLow
                    self.bValid = True
        return False

    def pushLow(self, nIndex, fValue):
        self.nBot3 = self.nBot2
        self.fBot3 = self.fBot2
        self.nBot2 = self.nBot1
        self.fBot2 = self.fBot1
        self.nBot1 = nIndex
        self.fBot1 = fValue
        if self.bValid:
            if self.fBot1 > self.fHigh:  # 中枢终结
                self.nTerminate = 1
                if self.nBot2 > self.nEnd:
                    self.nEnd = self.nBot2
                return True
            else:
                if self.nTop1 > self.nEnd:
                    self.nEnd = self.nTop1  # 中枢终结点后移
        else:
            # 有两个高点和两个低点
            if self.nTop2 > 0 and self.nTop1 > 0 and self.nBot3 > 0 and self.nBot2 > 0 and self.nBot1 > 0:
                fTempHigh = self.fTop1 if self.fTop1 < self.fTop2 else self.fTop2
                fTempLow = self.fBot1 if self.fBot1 > self.fBot2 else self.fBot2
                if self.fBot3 < self.fBot2 and fTempHigh > fTempLow:  # 有中枢
                    self.nDirection = 1  # 向上中枢
                    self.nStart = self.nTop2
                    self.nEnd = self.nBot1
                    self.fHigh = fTempHigh
                    self.fLow = fTempLow
                    self.bValid = True
        return False
