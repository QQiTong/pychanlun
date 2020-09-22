# -*- coding: utf-8 -*-

from enum import Enum


# 方向枚举
class Direction(Enum):
    UP = 1
    DOWN = -1


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
    direction: Direction

    def __int__(self, dt_start: int, dt_end: int, low_price: float, high_price: float, direction: Direction):
        self.dt_start = dt_start
        self.dt_end = dt_end
        self.low_price = low_price
        self.high_price = high_price
        self.direction = direction
