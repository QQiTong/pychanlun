import json

data_str = open('final.json').read()
data_list = json.loads(data_str)
jsonObj = json.loads(json.loads(data_str)['jsondata'])
stockDate = jsonObj['date']
stockHigh = jsonObj['high']
stockLow = jsonObj['low']
stockOpen = jsonObj['open']
stockClose = jsonObj['close']
volumeData = jsonObj['volume']
bidata = jsonObj['bidata']
duandata = jsonObj['duandata']
zsdata = jsonObj['zsdata']
zsflag = jsonObj['zsflag']
macddata = jsonObj['macd']
diffdata = jsonObj['diff']
deadata = jsonObj['dea']
# boll_up = jsonObj['boll_up']
# boll_middle = jsonObj['boll_middle']
# boll_bottom = jsonObj['boll_bottom']
info = jsonObj['info']
# isTradeTime = jsonObj['isTradeTime']
# basicInfo = jsonObj['basicInfo']
# concept = jsonObj['concept']

buyData = jsonObj['buyData']
sellData = jsonObj['sellData']

# buyData = jsonObj['buyData']['data']
# sellData = jsonObj['sellData']['data']

# buyValue = jsonObj['buyData']['value']
# sellValue = jsonObj['sellData']['value']

buyBCData = jsonObj['buyBCData']
sellBCData = jsonObj['sellBCData']


buyMACDBCData = jsonObj['buyMACDBCData']
sellMACDBCData = jsonObj['sellMACDBCData']



print('stockDate->',stockDate)
print('stockHigh->',stockHigh)
print('stockLow->',stockLow)
print('stockOpen->',stockOpen)
print('stockClose->',stockClose)
print('volumeData->',volumeData)
print('bidata1->',bidata['date'])
print('bidata2->',bidata['data'])
print('duandata->',duandata)
print('zsdata->',zsdata)
print('zsflag->',zsflag)
print('macddata->',macddata)
print('diffdata->',diffdata)
print('deadata->',deadata)
# print('boll_up->',boll_up)
# print('boll_middle->',boll_middle)
# print('boll_bottom->',boll_bottom)
print('info->',info)
# print('isTradeTime->',isTradeTime)
# print('basicInfo->',basicInfo)
# print('concept->',concept)
print('buyDate->', buyData['date'])
print('sellDate->', sellData['date'])
print('buyData->', buyData['data'])
print('sellData->', sellData['data'])
print('buyValue->', buyData['value'])
print('sellValue->', sellData['value'])

print('buyBCDate->', buyBCData['date'])
print('buyBCData->', buyBCData['data'])
print('buyBCValue->', buyBCData['value'])

print('sellBCDate->', sellBCData['date'])
print('sellBCData->', sellBCData['data'])
print('sellBCValue->', sellBCData['value'])

print('buyMACDBCDate->', buyMACDBCData['date'])
print('sellMACDBCDate->', sellMACDBCData['date'])

print('buyMACDBCData->', buyMACDBCData['data'])
print('sellMACDBCData->', sellMACDBCData['data'])

print('buyMACDBCValue->', buyMACDBCData['value'])
print('sellMACDBCValue->', sellMACDBCData['value'])


