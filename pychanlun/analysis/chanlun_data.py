# -*- coding: utf-8 -*-

from enum import Enum
from typing import List


# 方向枚举
class DirectionType(Enum):
    # 向上方向
    UP = 1
    # 向下方向
    DOWN = -1


# 分型类型
class FractalType(Enum):
    # 顶分型
    Top = 1
    # 底分型
    Bottom = -1


# K线数据结构
class Stick:
    dt: int
    open_price: float
    close_price: float
    low_price: float
    high_price: float
    volume: float
    amount: float

    def __int__(self, dt: int, open_price: float, close_price: float, low_price: float, high_price: float, volume: float, amount: float):
        self.dt = dt
        self.open_price = open_price
        self.close_price = close_price
        self.low_price = low_price
        self.high_price = high_price
        self.volume = volume
        self.amount = amount


# 合并K线数据结构
class MergedStick:
    dt_start: int
    dt_end: int
    low_low_price: float
    low_price: float
    high_high_price: float
    high_price: float
    direction: DirectionType
    sticks: List[Stick]

    def __int__(self, stick: Stick, direction: DirectionType):
        self.sticks = [stick]
        self.dt_start = stick.dt
        self.dt_end = stick.dt
        self.low_low_price = stick.low_price
        self.low_price = stick.low_price
        self.high_high_price = stick.high_price
        self.high_price = stick.high_price
        self.direction = direction

    def add(self, stick: Stick):
        self.dt_end = stick.dt
        self.low_low_price = min(self.low_low_price, stick.low_price)
        self.low_price = min(self.low_price, stick.low_price) if self.direction == DirectionType.DOWN else max(self.low_price, stick.low_price)
        self.high_high_price = max(self.high_high_price, stick.high_price)
        self.high_price = max(self.high_price, stick.high_price) if self.direction == DirectionType.UP else min(self.high_price, stick.high_price)


# 分型
class Fractal:
    dt_start: int
    dt_end: int
    low_low_price: float
    low_price: float
    high_high_price: float
    high_price: float
    fractal_type: FractalType
    merged_sticks = List[MergedStick]

    def __init__(self, stick1: MergedStick, stick2: MergedStick, stick3: MergedStick, fractal_type: FractalType):
        self.merged_sticks = [stick1, stick2, stick3]
        self.low_low_price = min(stick1.low_low_price, stick2.low_low_price, stick3.low_low_price)
        self.low_price = min(stick1.low_price, stick2.low_price, stick3.low_price)
        self.high_high_price = max(stick1.high_high_price, stick2.high_high_price, stick3.high_high_price)
        self.high_price = max(stick1.high_price, stick2.high_price, stick3.high_price)
        self.fractal_type = fractal_type
