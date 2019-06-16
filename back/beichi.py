def calcBeichi(timeList, highList, lowList, directionList, desList, diffList, macdList):
    data = {
        'buyMACDBCData': {'date': [], 'data': [], 'value': []},
        'sellMACDBCData': {'date': [], 'data': [], 'value': []},
    }
    for i in range(len(macdList)):
        if i > 1 and macdList[i-1] < 0 and macdList[i] >= 0 and diffList[i] < 0:
            data['sellMACDBCData']['date'].append(timeList[i])
            data['sellMACDBCData']['data'].append(diffList[i])
            data['sellMACDBCData']['value'].append('金叉')
    return data
