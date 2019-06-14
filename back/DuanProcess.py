class DuanProcess:
    def __init__(self):
        self.result = []

    def handle(self, biResult, highList, lowList):
        nCount = len(highList)
        self.result = [0 for i in range(nCount)]

        nState = 0
        nLastD = 0  # previous down duan's bottom
        nLastG = 0  # previous up duan's top
        fTop0 = 0
        fTop1 = 0
        fTop2 = 0
        fBot0 = 0
        fBot1 = 0
        fBot2 = 0
        for i in range(nCount):
            if biResult[i] == 1:
                fTop1 = fTop2
                fTop2 = highList[i]
            elif biResult[i] == -1:
                fBot1 = fBot2
                fBot2 = lowList[i]

            if nState == 0:
                if biResult[i] == 1:
                    nState = 1
                    nLastG = i
                    self.result[nLastG] = 1
                    fTop0 = 0
                    fBot0 = 0
                elif biResult[i] == -1:
                    nState = -1
                    nLastD = i
                    self.result[nLastD] = -1
                    fTop0 = 0
                    fBot0 = 0

            elif nState == 1:  # 向上线段运行中
                if biResult[i] == 1:  # 遇到高点
                    if highList[i] > highList[nLastG]:  # 比线段最高点还高，高点后移
                        self.result[nLastG] = 0
                        nLastG = i
                        self.result[nLastG] = 1
                        fTop0 = 0
                        fBot0 = 0
                elif biResult[i] == -1:  # 遇到低点
                    if lowList[i] < lowList[nLastD]:  # 低点比向上线段最低点还低了，当一段处理，也是终结。
                        nState = -1
                        nLastD = i
                        self.result[nLastD] = -1
                        fTop0 = 0
                        fBot0 = 0
                    elif fTop1 > 0 and fTop2 > 0 and fBot1 > 0 and fBot2 > 0 and fTop2 < fTop1 and fBot2 < fBot1:
                        # 向上线段终结
                        nState = -1
                        nLastD = i
                        self.result[nLastD] = -1
                        fTop0 = 0
                        fBot0 = 0
                    else:
                        if fBot0 == 0:
                            fBot0 = lowList[i]
                        elif lowList[i] < fBot0:  # 向上线段终结
                            nState = -1
                            nLastD = i
                            self.result[nLastD] = -1
                            fTop0 = 0
                            fBot0 = 0
            elif nState == -1:  # 向下线段运行中
                if biResult[i] == -1:  # 遇到低点
                    if lowList[i] < lowList[nLastD]:  # 比线段最低点还低，低点后移
                        self.result[nLastD] = 0
                        nLastD = i
                        self.result[nLastD] = -1
                        fTop0 = 0
                        fBot0 = 0
                elif biResult[i] == 1:  # 遇到高点
                    if highList[i] > highList[nLastG]:  # 高点比向下线段最高点还高了，当一段处理，也是终结。
                        nState = 1
                        nLastG = i
                        self.result[nLastG] = 1
                        fTop0 = 0
                        fBot0 = 0
                    elif fTop1 > 0 and fTop2 > 0 and fBot1 > 0 and fBot2 > 0 and fTop2 > fTop1 and fBot2 > fBot1:
                        # 向下线段终结
                        nState = 1
                        nLastG = i
                        self.result[nLastG] = 1
                        fTop0 = 0
                        fBot0 = 0
                    else:
                        if fTop0 == 0:
                            fTop0 = highList[i]
                        elif highList[i] > fTop0:
                            nState = 1
                            nLastG = i
                            self.result[nLastG] = 1
                            fTop0 = 0
                            fBot0 = 0
        return self.result
