from back.ToString import ToString


class Kline(ToString):
    high = None  # K线包含处理的高
    low = None  # K线包含处理的低
    maxHign = None # K线高高
    maxLow = None # K线低低
    direction = None  # kline direction
    start = None  # start kline position
    end = None  # end kline position
    middle = None
    time = None
    endTime = None

