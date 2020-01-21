from back.basic.bi import CalcBi

def testCalcBi():
    count = 5
    bi = [0 for i in range(5)]
    high = [11.1, 11.2, 11.3, 11.4, 11.5]
    low  = [10.1, 10.2, 10.3, 10.4, 10.5]
    CalcBi(count, bi, high, low, high, low)
    assert bi[0] == -1
    assert bi[4] == 1
    for i in range(1,4):
        assert bi[i] == 0
