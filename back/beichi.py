import pydash

def calcBeichi(payload):
    data = {
        'buyMACDBCData': {'date': [], 'data': [], 'value': []},
        'sellMACDBCData': {'date': [], 'data': [], 'value': []},
    }
    macdList = payload['macdList']
    diffList = payload['diffList']
    deaList = payload['deaList']
    timeList = payload['timeList']
    biList = payload['biList']
    # 线底背
    xianDiBei = [0 for i in range(len(timeList))]
    jinCha = [0 for i in range(len(timeList))]
    for i in range(len(macdList)):
        if i > 1 and macdList[i-1] < 0 and macdList[i] >= 0 and diffList[i] < 0:
            jinCha[i] = True

    for i in range(len(jinCha)):
        if jinCha[i] == True:
            iCurrent = 0
            iLast = 0
            iCurrent = pydash.find_index(biList, lambda bi : bi.start < i and bi.end >= i)
            for j in range(i - 1, 0, -1):
                if jinCha[j]:
                    iLast =pydash.find_index(biList, lambda bi : bi.start < j and bi.end >= j)
                    break
            if iCurrent > iLast > 0:
                if biList[iCurrent].low < biList[iLast].low and diffList[i] > diffList[j] and deaList[i] > deaList[j]:
                    xianDiBei[i] = True

    for i in range(len(xianDiBei)):
        if xianDiBei[i]:
            data['sellMACDBCData']['date'].append(timeList[i])
            data['sellMACDBCData']['data'].append(diffList[i])
            data['sellMACDBCData']['value'].append('线底背')
    return data
