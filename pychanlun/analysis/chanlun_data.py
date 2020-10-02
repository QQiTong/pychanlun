# -*- coding: utf-8 -*-

from typing import List
from pydash import flat_map, find
from pychanlun.constant import Constant

CONSTANT = Constant()
CONSTANT.DIRECTION_UP = 1
CONSTANT.DIRECTION_DOWN = -1
CONSTANT.FRACTAL_TOP = 1
CONSTANT.FRACTAL_BOTTOM = -1
CONSTANT.VERTEX_TOP = 1
CONSTANT.VERTEX_BOTTOM = -1
CONSTANT.VERTEX_NONE = 0


# K线数据结构
class Stick:

    def __init__(self, idx: int, dt: int, open_price: float, close_price: float, low_price: float, high_price: float):
        self.idx = idx
        self.dt = dt
        self.open_price = open_price
        self.close_price = close_price
        self.low_price = low_price
        self.high_price = high_price


# 合并K线数据结构
class MergedStick:

    def __init__(self, stick: Stick, direction: int):
        self.dt_start = stick.dt
        self.dt_end = stick.dt
        self.low_low_price = stick.low_price
        self.low_price = stick.low_price
        self.high_high_price = stick.high_price
        self.high_price = stick.high_price
        self.direction = direction
        self.stick_list = [stick]

    def add_stick(self, stick: Stick):
        self.dt_end = stick.dt
        self.low_low_price = min(self.low_low_price, stick.low_price)
        self.low_price = min(self.low_price, stick.low_price) if self.direction == CONSTANT.DIRECTION_DOWN else max(self.low_price, stick.low_price)
        self.high_high_price = max(self.high_high_price, stick.high_price)
        self.high_price = max(self.high_price, stick.high_price) if self.direction == CONSTANT.DIRECTION_UP else min(self.high_price, stick.high_price)
        self.stick_list.append(stick)


# 分型
class Fractal:

    def __init__(self, stick1: MergedStick, stick2: MergedStick, stick3: MergedStick, fractal_type: int):
        self.dt_start = stick1.dt_start
        self.dt_end = stick3.dt_end
        self.low_low_price = min(stick1.low_low_price, stick2.low_low_price, stick3.low_low_price)
        self.low_price = min(stick1.low_price, stick2.low_price, stick3.low_price)
        self.high_high_price = max(stick1.high_high_price, stick2.high_high_price, stick3.high_high_price)
        self.high_price = max(stick1.high_price, stick2.high_price, stick3.high_price)
        self.fractal_type = fractal_type
        self.merged_stick_list = [stick1, stick2, stick3]
        stick_list = stick1.stick_list + stick2.stick_list + stick3.stick_list
        vertex_stick = stick_list[0]
        for i in range(1, len(stick_list)):
            if fractal_type == CONSTANT.FRACTAL_BOTTOM:
                if stick_list[i].low_price < vertex_stick.low_price:
                    vertex_stick = stick_list[i]
            else:
                if stick_list[i].high_price > vertex_stick.high_price:
                    vertex_stick = stick_list[i]
        self.vertex_stick = vertex_stick


# 笔
class Bi:

    def __init__(self):
        self.fractal_start = None
        self.connections = []
        self.fractal_end = None
        self.concrete = False


class ChanlunData:

    def __init__(self, dt_list: List[int], open_price_list: List[float], close_price_list: List[float],
                 low_price_list: List[float], high_price_list: List[float], pre_duan_data: List[int] = None):

        length = len(dt_list)
        assert len(open_price_list) == length and len(close_price_list) == length and len(low_price_list) == length and \
            len(high_price_list) == length, "数据长度不一致"
        self.dt_list = dt_list
        self.open_price_list = open_price_list
        self.close_price_list = close_price_list
        self.low_price_list = low_price_list
        self.high_price_list = high_price_list
        self.pre_duan_data = pre_duan_data
        self.stick_list = []
        self.merged_stick_list = []
        self.bi_list = []
        self.bi_signal_list = []
        # 笔数据
        self.bi_data = {"dt": [], "data": [], "type": []}
        # 段数据
        self.duan_data = {"dt": [], "data": [], "type": []}
        # 高级别段数据
        self.higher_duan_data = {"dt": [], "data": [], "type": []}

        self.__prepare_sticks()
        self.__find_bi()

    # 准备K线
    def __prepare_sticks(self):
        length = len(self.dt_list)
        # K线和合并K线
        for i in range(length):
            stick = Stick(i, self.dt_list[i], self.open_price_list[i], self.close_price_list[i], self.low_price_list[i], self.high_price_list[i])
            self.stick_list.append(stick)
            if len(self.merged_stick_list) == 0:
                merged_stick = MergedStick(stick, CONSTANT.DIRECTION_UP)
                self.merged_stick_list.append(merged_stick)
            else:
                last_merged_stick = self.merged_stick_list[-1]
                if stick.high_price > last_merged_stick.high_price and stick.low_price > last_merged_stick.low_price:
                    # 新的向上合并K线
                    self.merged_stick_list.append(MergedStick(stick, CONSTANT.DIRECTION_UP))
                elif stick.high_price < last_merged_stick.high_price and stick.low_price < last_merged_stick.low_price:
                    # 新的向下合并K线
                    self.merged_stick_list.append(MergedStick(stick, CONSTANT.DIRECTION_DOWN))
                else:
                    # 有合并关系
                    last_merged_stick.add_stick(stick)

    # 计算笔
    def __find_bi(self):
        length = len(self.dt_list)
        # 遍历合并K线，生成笔
        if len(self.merged_stick_list) > 5:
            for i in range(2, len(self.merged_stick_list)):
                merged_stick1, merged_stick2, merged_stick3 = self.merged_stick_list[i - 2:i + 1]
                # 有分型产生
                if merged_stick3.direction != merged_stick2.direction:
                    fractal_type = CONSTANT.FRACTAL_BOTTOM if merged_stick3.direction == CONSTANT.DIRECTION_UP else CONSTANT.FRACTAL_TOP
                    fractal = Fractal(merged_stick1, merged_stick2, merged_stick3, fractal_type)
                    self.__on_fractal(fractal)
                # 没有分型产生
                else:
                    self.__on_connect(merged_stick3)

        bi_signal_list = [CONSTANT.VERTEX_NONE for i in range(length)]

        for i in range(len(self.bi_list)):
            bi = self.bi_list[i]
            if i == 0:
                vertex_stick = bi.fractal_start.vertex_stick
                bi_signal_list[vertex_stick.idx] = CONSTANT.VERTEX_BOTTOM if bi.fractal_start.fractal_type == CONSTANT.FRACTAL_BOTTOM else CONSTANT.VERTEX_TOP
            if bi.fractal_end is not None:
                vertex_stick = bi.fractal_end.vertex_stick
                bi_signal_list[vertex_stick.idx] = CONSTANT.VERTEX_BOTTOM if bi.fractal_end.fractal_type == CONSTANT.FRACTAL_BOTTOM else CONSTANT.VERTEX_TOP
        self.bi_signal_list = bi_signal_list

        for i in range(length):
            if bi_signal_list[i] == -1:
                self.bi_data['dt'].append(self.dt_list[i])
                self.bi_data['data'].append(self.low_price_list[i])
                self.bi_data['type'].append(bi_signal_list[i])
            elif bi_signal_list[i] == 1:
                self.bi_data['dt'].append(self.dt_list[i])
                self.bi_data['data'].append(self.high_price_list[i])
                self.bi_data['type'].append(bi_signal_list[i])

    # 分型部分
    def __on_fractal(self, fractal: Fractal):
        length = len(self.bi_list)
        if length == 0:
            bi = Bi()
            bi.fractal_start = fractal
            self.bi_list.append(bi)
        else:
            last_last_bi = self.bi_list[-2] if length > 1 else None
            last_bi = self.bi_list[-1]
            if fractal.fractal_type == last_bi.fractal_start.fractal_type:
                # 最后正式的笔继续延伸
                if fractal.low_low_price < last_bi.fractal_start.low_low_price if \
                        fractal.fractal_type == CONSTANT.FRACTAL_BOTTOM else  \
                        fractal.high_high_price > last_bi.fractal_start.high_high_price:
                    if last_last_bi is not None:
                        last_last_bi.connections = last_last_bi.connections + last_bi.fractal_start.merged_stick_list + \
                            last_bi.connections[:-2]
                        last_last_bi.fractal_end = fractal

                    bi = Bi()
                    bi.fractal_start = fractal
                    self.bi_list.pop()
                    self.bi_list.append(bi)
                # 新的笔酝酿中
                else:
                    last_bi.connections.append(fractal.merged_stick_list[-1])
            else:
                # 破坏了前一笔了，也看成是新的一笔产生了（特殊处理）
                if last_last_bi is not None:
                    if fractal.low_low_price < last_last_bi.fractal_start.low_low_price if fractal.fractal_type == CONSTANT.FRACTAL_BOTTOM else \
                            fractal.high_high_price > last_last_bi.fractal_start.high_high_price:
                        last_bi.fractal_end = fractal
                        last_bi.connections = last_bi.connections[:-2]
                        last_bi.concrete = True
                        bi = Bi()
                        bi.fractal_start = fractal
                        self.bi_list.append(bi)
                        return
                # 正常处理
                connections = last_bi.connections[:-2]
                stick_list = flat_map(connections, lambda x: x.stick_list)
                fractal_start = last_bi.fractal_start
                fractal_end = fractal

                # 计算是否有独立隔离K线的函数
                def isolation_func(s: Stick):
                    return s.high_price <= fractal_start.low_low_price and s.low_price >= fractal_end.high_high_price if \
                            fractal_end.fractal_type == CONSTANT.FRACTAL_BOTTOM else \
                            s.low_price >= fractal_start.high_high_price and s.high_price <= fractal_end.low_low_price
                isolation = find(stick_list, isolation_func)
                if isolation is not None:
                    last_bi.fractal_end = fractal
                    last_bi.connections = connections
                    last_bi.concrete = True
                    # 一笔结束也是一笔的开始
                    bi = Bi()
                    bi.fractal_start = fractal
                    self.bi_list.append(bi)
                else:
                    last_bi.connections.append(fractal.merged_stick_list[-1])

    # 分型之间的连接部分
    def __on_connect(self, merged_stick: MergedStick):
        length = len(self.bi_list)
        if length > 0:
            self.bi_list[-1].connections.append(merged_stick)
