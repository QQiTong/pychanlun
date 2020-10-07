# -*- coding: utf-8 -*-

from typing import List
from pydash import flat_map, find, min_by, max_by
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

    def __init__(self, idx: int, stick: Stick, direction: int):
        self.idx = idx
        self.dt_start = stick.dt
        self.dt_end = stick.dt
        self.low_low_price = stick.low_price
        self.low_price = stick.low_price
        self.high_high_price = stick.high_price
        self.high_price = stick.high_price
        self.direction = direction
        self.stick_list = [stick]

    def merge_stick(self, stick: Stick):
        self.dt_end = stick.dt
        self.low_low_price = min(self.low_low_price, stick.low_price)
        self.low_price = min(self.low_price, stick.low_price) if self.direction == CONSTANT.DIRECTION_DOWN else max(self.low_price, stick.low_price)
        self.high_high_price = max(self.high_high_price, stick.high_price)
        self.high_price = max(self.high_price, stick.high_price) if self.direction == CONSTANT.DIRECTION_UP else min(self.high_price, stick.high_price)
        self.stick_list.append(stick)


# 分型
class Fractal:

    def __init__(self, merged_stick_list: List[MergedStick], fractal_type: int):
        self.fractal_type = fractal_type
        self.merged_stick_list = merged_stick_list

        self.low_low_price = min_by(self.merged_stick_list, 'low_low_price').low_low_price
        self.high_high_price = max_by(self.merged_stick_list, 'high_high_price').high_high_price
        self.low_price = min_by(self.merged_stick_list, 'low_price').low_price
        self.high_price = max_by(self.merged_stick_list, 'high_price').high_price
        self.__find_vertex_stick()

    def __find_vertex_stick(self):
        stick_list = flat_map(self.merged_stick_list, lambda x: x.stick_list)
        self.dt_start = stick_list[0].dt
        self.dt_end = stick_list[-1].dt
        vertex_stick = stick_list[0]
        for i in range(1, len(stick_list)):
            if self.fractal_type == CONSTANT.FRACTAL_BOTTOM:
                if stick_list[i].low_price <= vertex_stick.low_price:
                    vertex_stick = stick_list[i]
            else:
                if stick_list[i].high_price >= vertex_stick.high_price:
                    vertex_stick = stick_list[i]
        self.vertex_stick = vertex_stick

    def add_additional_stick_list(self, stick_list: List[MergedStick], before=False):
        self.merged_stick_list = (self.merged_stick_list + stick_list) if not before else (stick_list + self.merged_stick_list)
        self.__find_vertex_stick()
        if self.fractal_type == CONSTANT.FRACTAL_BOTTOM:
            self.low_low_price = self.vertex_stick.low_price
        else:
            self.high_high_price = self.vertex_stick.high_price

    def is_non_standard(self):
        return len(self.merged_stick_list) > 3


# 笔
class Bi:

    def __init__(self):
        self.fractal_start = None
        self.fractal_end = None
        self.concrete = False


# 缠论分析
class ChanlunData:

    def __init__(self, dt_list: List[int], open_price_list: List[float], close_price_list: List[float],
                 low_price_list: List[float], high_price_list: List[float], pre_duan_data=None, pre_higher_duan_data=None):
        length = len(dt_list)
        assert len(open_price_list) == length and len(close_price_list) == length and len(low_price_list) == length and \
            len(high_price_list) == length, "数据长度不一致"

        self.dt_list = dt_list
        self.open_price_list = open_price_list
        self.close_price_list = close_price_list
        self.low_price_list = low_price_list
        self.high_price_list = high_price_list
        self.pre_duan_data = pre_duan_data
        self.pre_higher_duan_data = pre_higher_duan_data

        self.stick_list = []
        self.merged_stick_list = []
        self.bi_list = []
        self.bi_signal_list = [CONSTANT.VERTEX_NONE for i in range(length)]
        self.duan_signal_list = [CONSTANT.VERTEX_NONE for i in range(length)]
        self.higher_duan_signal_list = [CONSTANT.VERTEX_NONE for i in range(length)]

        # 笔数据
        self.bi_data = {"dt": [], "data": [], "vertex_type": [], "dt_range": []}

        # 段数据
        self.duan_data = {"dt": [], "data": [], "vertex_type": [], "dt_range": []}
        # 高级别段数据
        self.higher_duan_data = {"dt": [], "data": [], "vertex_type": [], "dt_range": []}

        self.__prepare_sticks()

        if self.pre_duan_data is not None:
            self.__find_duan_with_pre_duan()

        self.__find_bi()

        if self.pre_duan_data is None:
            self.__find_duan_normal()

        # if self.pre_higher_duan_data is not None:
        #     self.__find_higher_duan_with_pre_higher_duan()
        # else:
        #     self.__find_higher_duan_normal()

    # 准备K线
    def __prepare_sticks(self):
        length = len(self.dt_list)
        # K线和合并K线
        for i in range(length):
            stick = Stick(i, self.dt_list[i], self.open_price_list[i], self.close_price_list[i], self.low_price_list[i], self.high_price_list[i])
            self.stick_list.append(stick)
            merged_sticks_len = len(self.merged_stick_list)
            if merged_sticks_len == 0:
                merged_stick = MergedStick(merged_sticks_len, stick, CONSTANT.DIRECTION_UP)
                self.merged_stick_list.append(merged_stick)
            else:
                last_merged_stick = self.merged_stick_list[-1]
                if stick.high_price > last_merged_stick.high_price and stick.low_price > last_merged_stick.low_price:
                    # 新的向上合并K线
                    merged_stick = MergedStick(merged_sticks_len, stick, CONSTANT.DIRECTION_UP)
                    self.merged_stick_list.append(merged_stick)
                elif stick.high_price < last_merged_stick.high_price and stick.low_price < last_merged_stick.low_price:
                    # 新的向下合并K线
                    merged_stick = MergedStick(merged_sticks_len, stick, CONSTANT.DIRECTION_DOWN)
                    self.merged_stick_list.append(merged_stick)
                else:
                    # 有合并关系
                    last_merged_stick.merge_stick(stick)

    # 计算笔
    def __find_bi(self):
        length = len(self.dt_list)
        # 遍历合并K线，生成笔
        merged_sticks_len = len(self.merged_stick_list)
        # 有5根以上合并K线我们才分析笔
        if merged_sticks_len > 5:
            for i in range(2, merged_sticks_len):
                merged_stick1, merged_stick2, merged_stick3 = self.merged_stick_list[i-2:i+1]
                # 有分型产生
                if merged_stick3.direction != merged_stick2.direction:
                    fractal_type = CONSTANT.FRACTAL_BOTTOM if merged_stick3.direction == CONSTANT.DIRECTION_UP else CONSTANT.FRACTAL_TOP
                    fractal = Fractal([merged_stick1, merged_stick2, merged_stick3], fractal_type)
                    self.__on_fractal(fractal)
                # 没有分型产生
                else:
                    if len(self.bi_list) > 0:
                        last_bi = self.bi_list[-1]
                        if last_bi.fractal_start.fractal_type == CONSTANT.FRACTAL_TOP:
                            if merged_stick3.high_high_price > last_bi.fractal_start.high_high_price:
                                if merged_stick3.direction == CONSTANT.DIRECTION_DOWN:
                                    # 分型要进行延伸处理
                                    s_index = last_bi.fractal_start.merged_stick_list[-1].idx + 1
                                    e_index = merged_stick3.idx + 1
                                    addition_merged_sticks = self.merged_stick_list[s_index:e_index]
                                    last_bi.fractal_start.add_additional_stick_list(addition_merged_sticks)
                        else:
                            if merged_stick3.low_low_price < last_bi.fractal_start.low_low_price:
                                if merged_stick3.direction == CONSTANT.DIRECTION_UP:
                                    # 分型要进行延伸处理
                                    s_index = last_bi.fractal_start.merged_stick_list[-1].idx + 1
                                    e_index = merged_stick3.idx + 1
                                    addition_merged_sticks = self.merged_stick_list[s_index:e_index]
                                    last_bi.fractal_start.add_additional_stick_list(addition_merged_sticks)

            # 处理最后一笔不会延伸到顶点的问题
            if len(self.bi_list) > 1:
                last_last_bi, last_bi = self.bi_list[-2:]
                if last_bi.fractal_end is None:
                    if last_bi.fractal_start.fractal_type == CONSTANT.FRACTAL_BOTTOM:
                        if self.merged_stick_list[-1].low_low_price <= last_bi.fractal_start.low_low_price:
                            merged_stick1, merged_stick2, merged_stick3 = self.merged_stick_list[-3:]
                            dummy_fractal = Fractal([merged_stick1, merged_stick2, merged_stick3], CONSTANT.FRACTAL_BOTTOM)
                            last_bi.fractal_start = dummy_fractal
                            last_last_bi.fractal_end = dummy_fractal
                    else:
                        if self.merged_stick_list[-1].high_high_price >= last_bi.fractal_start.high_high_price:
                            merged_stick1, merged_stick2, merged_stick3 = self.merged_stick_list[-3:]
                            dummy_fractal = Fractal([merged_stick1, merged_stick2, merged_stick3], CONSTANT.FRACTAL_TOP)
                            last_bi.fractal_start = dummy_fractal
                            last_last_bi.fractal_end = dummy_fractal

        self.__filter_bi()

        # 去掉尾部的非正式笔
        for i in range(len(self.bi_list) - 1, 0, -1):
            if self.bi_list[i].concrete:
                break
            self.bi_list.pop()

        # 生成笔信号
        for i in range(len(self.bi_list)):
            bi = self.bi_list[i]
            if i == 0:
                vertex_stick = bi.fractal_start.vertex_stick
                idx = vertex_stick.idx
                self.bi_signal_list[idx] = CONSTANT.VERTEX_BOTTOM if bi.fractal_start.fractal_type == CONSTANT.FRACTAL_BOTTOM else CONSTANT.VERTEX_TOP
            if bi.fractal_end is not None:
                vertex_stick = bi.fractal_end.vertex_stick
                idx = vertex_stick.idx
                self.bi_signal_list[idx] = CONSTANT.VERTEX_BOTTOM if bi.fractal_end.fractal_type == CONSTANT.FRACTAL_BOTTOM else CONSTANT.VERTEX_TOP

        # 极特殊情况下，段端点和笔端点不能重合的情况下，把笔的端点调整到段的端点
        for i in range(length):
            if self.duan_signal_list[i] == CONSTANT.VERTEX_BOTTOM and self.bi_signal_list[i] == CONSTANT.VERTEX_NONE:
                for j in range(i, 0, -1):
                    if self.bi_signal_list[j] == CONSTANT.VERTEX_TOP:
                        break
                    if self.bi_signal_list[j] == CONSTANT.VERTEX_BOTTOM:
                        if self.low_price_list[i] <= self.low_price_list[j]:
                            self.bi_signal_list[j] = CONSTANT.VERTEX_NONE
                            self.bi_signal_list[i] = CONSTANT.VERTEX_BOTTOM
                        else:
                            self.duan_signal_list[i] = CONSTANT.VERTEX_NONE
                            self.duan_signal_list[j] = CONSTANT.VERTEX_BOTTOM
                        break
            elif self.duan_signal_list[i] == CONSTANT.VERTEX_TOP and self.bi_signal_list[i] == CONSTANT.VERTEX_NONE:
                for j in range(i, 0, -1):
                    if self.bi_signal_list[j] == CONSTANT.VERTEX_BOTTOM:
                        break
                    if self.bi_signal_list[j] == CONSTANT.VERTEX_TOP:
                        if self.high_price_list[i] >= self.high_price_list[j]:
                            self.bi_signal_list[j] = CONSTANT.VERTEX_NONE
                            self.bi_signal_list[i] = CONSTANT.VERTEX_TOP
                        else:
                            self.duan_signal_list[i] = CONSTANT.VERTEX_NONE
                            self.duan_signal_list[j] = CONSTANT.VERTEX_TOP
                        break

        for idx in range(length):
            if self.bi_signal_list[idx] != CONSTANT.VERTEX_NONE:
                self.bi_data['dt'].append(self.dt_list[idx])
                self.bi_data['data'].append(self.low_price_list[idx] if self.bi_signal_list[idx] == CONSTANT.VERTEX_BOTTOM else self.high_price_list[idx])
                self.bi_data['vertex_type'].append(self.bi_signal_list[idx])
                s = self.dt_list[idx - 1] if idx - 1 >= 0 else self.dt_list[idx]
                e = self.dt_list[idx + 1] if idx + 1 < length else self.dt_list[idx]
                self.bi_data['dt_range'].append([s, e])

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
                if fractal.low_low_price <= last_bi.fractal_start.low_low_price if \
                        fractal.fractal_type == CONSTANT.FRACTAL_BOTTOM else  \
                        fractal.high_high_price >= last_bi.fractal_start.high_high_price:
                    if last_last_bi is not None:
                        concrete = last_last_bi.concrete
                        if not concrete:
                            concrete = self.__is_concrete_bi(last_last_bi.fractal_start, fractal)
                        last_last_bi.fractal_end = fractal
                        last_last_bi.concrete = concrete
                    bi = Bi()
                    bi.fractal_start = fractal
                    self.bi_list.pop()
                    self.bi_list.append(bi)
                elif last_bi.fractal_start.is_non_standard():
                    if last_bi.fractal_start.fractal_type == CONSTANT.FRACTAL_BOTTOM:
                        if fractal.high_high_price < last_bi.fractal_start.high_high_price:
                            s_index = min_by(last_bi.fractal_start.merged_stick_list, 'low_low_price').idx
                            e_index = fractal.merged_stick_list[0].idx
                            additional_sticks = self.merged_stick_list[s_index:e_index]
                            fractal.add_additional_stick_list(additional_sticks, before=True)
                            last_bi.fractal_end = fractal
                            bi = Bi()
                            bi.fractal_start = fractal
                            self.bi_list.pop()
                            self.bi_list.append(bi)
                    else:
                        if fractal.low_low_price > last_bi.fractal_start.low_low_price:
                            s_index = max_by(last_bi.fractal_start.merged_stick_list, 'high_high_price').idx
                            e_index = fractal.merged_stick_list[0].idx
                            additional_sticks = self.merged_stick_list[s_index:e_index]
                            fractal.add_additional_stick_list(additional_sticks, before=True)
                            last_bi.fractal_end = fractal
                            bi = Bi()
                            bi.fractal_start = fractal
                            self.bi_list.pop()
                            self.bi_list.append(bi)
            else:
                # 破坏了前一笔了，也看成是新的一笔产生了（特殊处理）
                if last_last_bi is not None:
                    if fractal.low_low_price <= last_last_bi.fractal_start.low_low_price if fractal.fractal_type == CONSTANT.FRACTAL_BOTTOM else \
                            fractal.high_high_price >= last_last_bi.fractal_start.high_high_price:
                        last_bi.fractal_end = fractal
                        bi = Bi()
                        bi.fractal_start = fractal
                        self.bi_list.append(bi)
                        return

                if self.__is_concrete_bi(last_bi.fractal_start, fractal):
                    last_bi.fractal_end = fractal
                    last_bi.concrete = True
                    # 一笔结束也是一笔的开始
                    bi = Bi()
                    bi.fractal_start = fractal
                    self.bi_list.append(bi)

    def __filter_bi(self):
        length = len(self.bi_list)
        for i in range(length):
            if self.bi_list[i].fractal_start is None or self.bi_list[i].fractal_end is None:
                break
            if not self.bi_list[i].concrete:
                concrete = self.__is_concrete_bi(self.bi_list[i].fractal_start, self.bi_list[i].fractal_end)
                if concrete:
                    self.bi_list[i].concrete = True
                    continue
                if i >= 2:
                    bi1, bi2, bi3 = self.bi_list[i-2:i+1]
                    if bi1.fractal_end is not None and bi3.fractal_end is not None:
                        if bi1.fractal_start.fractal_type == CONSTANT.FRACTAL_TOP:
                            if bi1.fractal_start.high_high_price >= bi3.fractal_start.high_high_price and bi1.fractal_end.low_low_price >= bi3.fractal_end.low_low_price:
                                bi1.fractal_end = bi3.fractal_end
                                self.bi_list.pop(i)
                                self.bi_list.pop(i-1)
                                self.__filter_bi()
                                break
                        else:
                            if bi1.fractal_start.low_low_price <= bi3.fractal_start.low_low_price and bi1.fractal_end.high_high_price <= bi3.fractal_end.high_high_price:
                                bi1.fractal_end = bi3.fractal_end
                                self.bi_list.pop(i)
                                self.bi_list.pop(i-1)
                                self.__filter_bi()
                                break
                if 1 <= i < length - 1:
                    bi1, bi2, bi3 = self.bi_list[i-1:i+2]
                    if bi1.fractal_end is not None and bi3.fractal_end is not None:
                        if bi1.fractal_start.fractal_type == CONSTANT.FRACTAL_TOP:
                            if bi1.fractal_start.high_high_price >= bi3.fractal_start.high_high_price and bi1.fractal_end.low_low_price >= bi3.fractal_end.low_low_price:
                                bi1.fractal_end = bi3.fractal_end
                                self.bi_list.pop(i+1)
                                self.bi_list.pop(i)
                                self.__filter_bi()
                                break
                        else:
                            if bi1.fractal_start.low_low_price <= bi3.fractal_start.low_low_price and bi1.fractal_end.high_high_price <= bi3.fractal_end.high_high_price:
                                bi1.fractal_end = bi3.fractal_end
                                self.bi_list.pop(i+1)
                                self.bi_list.pop(i)
                                self.__filter_bi()
                                break

    def __is_concrete_bi(self, fractal_start: Fractal, fractal_end: Fractal):
        if fractal_start.fractal_type == fractal_end.fractal_type:
            return False
        s_index = fractal_start.merged_stick_list[-1].idx + 1
        e_index = fractal_end.merged_stick_list[0].idx
        if s_index >= e_index:
            return False
        connections = self.merged_stick_list[s_index:e_index]
        stick_list = flat_map(connections, lambda x: x.stick_list)

        # # 顶底波动区间不能接触
        if min(fractal_start.high_high_price, fractal_end.high_high_price) >= max(fractal_start.low_low_price, fractal_end.low_low_price):
            return False

        # 是不是低点
        if len(connections) > 0:
            if fractal_end.fractal_type == CONSTANT.FRACTAL_BOTTOM:
                e = min_by(connections, 'low_low_price')
                # 不是笔中的低点，不会成立笔
                if fractal_end.low_low_price > e.low_low_price:
                    return False
            else:
                e = max_by(connections, 'high_high_price')
                if fractal_end.high_high_price < e.high_high_price:
                    return False
        else:
            return False

        # 计算是否有独立隔离K线的函数
        def isolation_func(s: Stick):
            return s.high_price <= fractal_start.low_price and s.low_price >= fractal_end.high_price if \
                fractal_end.fractal_type == CONSTANT.FRACTAL_BOTTOM else \
                s.low_price >= fractal_start.high_price and s.high_price <= fractal_end.low_price

        def isolation_func2(s: MergedStick):
            return s.high_price <= fractal_start.low_price and s.low_price >= fractal_end.high_price if \
                fractal_end.fractal_type == CONSTANT.FRACTAL_BOTTOM else \
                s.low_price >= fractal_start.high_price and s.high_price <= fractal_end.low_price

        isolation = find(stick_list, isolation_func)
        if isolation is not None:
            return True
        else:
            isolation2 = find(connections, isolation_func2)
            if isolation2 is not None:
                return True
            else:
                return False

    # 高级别的笔作为本级别的段的画法
    def __find_duan_with_pre_duan(self):
        i = 0
        for j in range(len(self.pre_duan_data['dt'])):
            dt_range = self.pre_duan_data['dt_range'][j]
            vertex_type = self.pre_duan_data['vertex_type'][j]
            c_stick_list = []

            def resolve():
                if len(c_stick_list) > 0:
                    if vertex_type == CONSTANT.VERTEX_TOP:
                        vertex_stick = c_stick_list[0]
                        for t in range(len(c_stick_list)):
                            if c_stick_list[t].high_price >= vertex_stick.high_price:
                                vertex_stick = c_stick_list[t]
                        idx = vertex_stick.idx
                        self.duan_data['dt'].append(self.dt_list[idx])
                        self.duan_data['data'].append(self.high_price_list[idx])
                        self.duan_data['dt_range'].append(dt_range)
                        self.duan_data['vertex_type'].append(CONSTANT.VERTEX_TOP)
                        self.duan_signal_list[idx] = CONSTANT.VERTEX_TOP
                    else:
                        vertex_stick = c_stick_list[0]
                        for t in range(len(c_stick_list)):
                            if c_stick_list[t].low_price <= vertex_stick.low_price:
                                vertex_stick = c_stick_list[t]
                        idx = vertex_stick.idx
                        self.duan_data['dt'].append(self.dt_list[idx])
                        self.duan_data['data'].append(self.low_price_list[idx])
                        self.duan_data['dt_range'].append(dt_range)
                        self.duan_data['vertex_type'].append(CONSTANT.VERTEX_BOTTOM)
                        self.duan_signal_list[idx] = CONSTANT.VERTEX_BOTTOM

            for k in range(i, len(self.stick_list)):
                stick = self.stick_list[k]
                if stick.dt < dt_range[0]:
                    continue
                elif stick.dt > dt_range[1]:
                    resolve()
                    i = k
                    c_stick_list = []
                    break
                else:
                    c_stick_list.append(stick)
            resolve()

    def __find_duan_normal(self):
        pass

    def __find_higher_duan_with_pre_higher_duan(self):
        i = 0
        for j in range(len(self.pre_higher_duan_data['dt'])):
            dt_range = self.pre_higher_duan_data['dt_range'][j]
            vertex_type = self.pre_higher_duan_data['vertex_type'][j]
            c_stick_list = []
            for k in range(i, len(self.stick_list)):
                stick = self.stick_list[k]
                if stick.dt < dt_range[0]:
                    continue
                elif stick.dt > dt_range[1]:
                    if len(c_stick_list) > 0:
                        if vertex_type == CONSTANT.VERTEX_TOP:
                            vertex_stick = c_stick_list[0]
                            for t in range(len(c_stick_list)):
                                if c_stick_list[t].high_price >= vertex_stick.high_price:
                                    vertex_stick = c_stick_list[t]
                            idx = vertex_stick.idx
                            self.higher_duan_data['dt'].append(self.dt_list[idx])
                            self.higher_duan_data['data'].append(self.high_price_list[idx])
                            self.higher_duan_data['vertex_type'].append(CONSTANT.VERTEX_TOP)
                            self.higher_duan_signal_list[idx] = CONSTANT.VERTEX_BOTTOM
                        else:
                            vertex_stick = c_stick_list[0]
                            for t in range(len(c_stick_list)):
                                if c_stick_list[t].low_price <= vertex_stick.low_price:
                                    vertex_stick = c_stick_list[t]
                            idx = vertex_stick.idx
                            self.higher_duan_data['dt'].append(self.dt_list[idx])
                            self.higher_duan_data['data'].append(self.low_price_list[idx])
                            self.higher_duan_data['vertex_type'].append(CONSTANT.VERTEX_BOTTOM)
                            self.higher_duan_signal_list[idx] = CONSTANT.VERTEX_BOTTOM
                    i = k
                    c_stick_list = []
                    break
                else:
                    c_stick_list.append(stick)

    def __find_higher_duan_normal(self):
        pass