from back.KlineDataTool import KlineDataTool
from jqdatasdk import *
import numpy as np
import pandas as pd
from numpy import array
import talib as ta
import time

from back.Mail import Mail


def getMacd(closeList):
    close = array(closeList)
    macd = ta.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    result = np.nan_to_num(macd)
    return result


def cross(arr1, arr2):  # 参数个数为2个，从参数名可以看出，这两个 参数应该都是 数组类型，数组就
    # 好比是 在X轴为 数组索引值，Y轴为 指标值的 坐标系中的 线段， 该函数就是判断 两条线的 交叉情况
    if (len(arr1) != len(arr2)):  # 首先要判断 比较的两个 数组 长度是否相等
        print("array length not equal")  # 如果不相等 抛出错误，对于 不相等 的指标线  无法 判断相交
    n = 0
    # 遍历 数组 arr1， 遍历顺序 为 从最后一个元素 向前 遍历
    for i in range(len(arr1) - 1, -1, -1):  # 声明 变量 n  用来记录  交叉状态 ，初始  0 ，未相交
        # 如果 arr1 小于 arr2 则 n-- ， 会记录 开始时 arr1、arr2 的相对 状态，（即 开始时  n 会根据 arr1[i] 、 arr2[i] 相对大小 自行调整，一旦出现 另一种 和 n 状态 相反的 arr1[i]、arr2[i] 大小关系， 即发生了 两条线交叉。）
        if arr1[i] < arr2[i]:
            if n > 0:
                break
            n = n - 1
        elif arr1[i] > arr2[i]:  # 如果 arr1 大于 arr2 则 n++
            if n < 0:
                break
            n = n + 1
        else:  # arr1[i] == arr2[i] ，则立即 跳出
            break
            # 返回 n 值，代表 已经交叉了多少周期， 0 即 指标值相等。
    return n


auth('13088887055', 'chanlun123456')

klineDataTool = KlineDataTool()
symbolList1 = ['RB1910.XSGE', 'HC1910.XSGE', 'RU1909.XSGE', 'NI1907.XSGE', 'FU1909.XSGE', 'ZN1908.XSGE',
               'SP1909.XSGE', 'MA1909.XZCE', 'SR1909.XZCE', 'AP1910.XZCE', 'J1909.XDCE', 'JM1909.XDCE', 'PP1909.XDCE']

# 23:30结束的  甲醇 白糖 玻璃
symbolList2 = ['MA1909.XZCE', 'SR1909.XZCE', 'FG1909.XZCE']
# 1:00 结束的锌 镍
symbolList3 = ['NI1907.XSGE', 'ZN1907.XSGE']

periodList = ['3m', '5m', '15m', '30m', '60m']

symbolList = symbolList1
mail = Mail()

lastTimeMap = {}
for i in range(len(symbolList)):
    symbol = symbolList[i]
    lastTimeMap[symbol] = {}
    for j in range(len(periodList)):
        period = periodList[j]
        lastTimeMap[symbol][period] = 0

print(lastTimeMap)
while True:
    for i in range(len(symbolList)):
        for j in range(len(periodList)):
            symbol = symbolList[i]
            period = periodList[j]
            klineData = klineDataTool.getFutureData(symbol, period, 200)
            price = klineData[-1]['open']
            currentTime = klineData[-1]['time']
            precurrentTime = klineData[-2]['time']
            df = pd.DataFrame(klineData, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            closeList = df['close']
            macdList = getMacd(closeList)
            dif = macdList[0]
            dea = macdList[1]
            macd = macdList[2]
            n = cross(dif, dea)
            difDeaAvg = (dif[-1] + dea[-1]) / 2
            msg = ""
            lastTime = lastTimeMap[symbol][period]
            # print("当前:", symbol, period, lastTime, currentTime, difDeaAvg)

            # 过滤重复提醒的
            if periodList[j] == '1m':
                if currentTime - lastTime < 1000 * 60:
                    continue
            elif periodList[j] == '3m':
                if currentTime - lastTime < 1000 * 60 * 3:
                    continue
            elif periodList[j] == '5m':
                if currentTime - lastTime < 1000 * 60 * 5:
                    continue
            elif periodList[j] == '15m':
                if currentTime - lastTime < 1000 * 60 * 15:
                    continue
            elif periodList[j] == '30m':
                if currentTime - lastTime < 1000 * 60 * 30:
                    continue
            elif periodList[j] == '60m':

                if currentTime - lastTime < 1000 * 60 * 60:
                    print("continue->", symbolList[i], "->", n, periodList[j])
                    continue
            elif periodList[j] == '240m':
                if currentTime - lastTime < 1000 * 60 * 240:
                    continue

            if n == 1 and lastTime != currentTime and difDeaAvg <= 0:

                msg = symbolList[i], "->", n, periodList[j], ":金叉,价格:", price, "时间:", time.strftime("%Y-%m-%d %H:%M:%S",
                                                                                                    time.localtime(
                                                                                                        currentTime)),

                lastTimeMap[symbol][period] = currentTime
                result = mail.send(str(msg))
                if not result:
                    print("发送失败")
                print(msg)
            elif n == -1 and lastTime != currentTime and difDeaAvg >= 0:
                msg = symbolList[i], "->", periodList[j], ":死叉,价格", n, price, "时间:", time.strftime("%Y-%m-%d %H:%M:%S",
                                                                                                   time.localtime(
                                                                                                       currentTime)),
                result = mail.send(str(msg))
                if not result:
                    print("发送失败")
                lastTimeMap[symbol][period] = currentTime
                print(msg)
            time.sleep(5)
        # time.sleep(10)
