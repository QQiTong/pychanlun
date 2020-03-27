from vnpy.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)

from pychanlun import divergence
import pychanlun.entanglement as entanglement
from numpy import array
import talib as ta
import numpy as np

from pychanlun.Calc import Calc
from pychanlun.basic.bi import CalcBi
from pychanlun.basic.duan import CalcDuan


class ChanLunStrategy(CtaTemplate):
    author = "用Python的交易员"
    amount = 1
    parameters = ["amount"]
    fast_window = 10
    slow_window = 20

    fast_ma0 = 0.0
    fast_ma1 = 0.0

    slow_ma0 = 0.0
    slow_ma1 = 0.0

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self,3,self.on_3min_bar)
        self.am = ArrayManager(200)

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")
        self.put_event()

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

        self.put_event()

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):

        self.bg.update_bar(bar)

    def on_3min_bar(self, bar: BarData):
        """"""
        # self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        openList = am.open_array
        highList = am.high_array
        lowList = am.low_array
        closeList = am.close_array
        timeList = am.time_array

        count = len(timeList)
        # 本级别笔
        biList = [0 for i in range(count)]
        CalcBi(count, biList, highList, lowList, openList, closeList)

        # 本级别段处理
        duanList = [0 for i in range(count)]
        CalcDuan(count, duanList, biList, highList, lowList)

        higherDuanList = [0 for i in range(count)]
        CalcDuan(count, higherDuanList, duanList, highList, lowList)

        # 高高一级别段处理
        higherHigherDuanList = [0 for i in range(count)]
        CalcDuan(count, higherHigherDuanList, higherDuanList, highList, lowList)

        entanglementList = entanglement.CalcEntanglements(timeList, duanList, biList, highList, lowList)
        huila = entanglement.la_hui(entanglementList, timeList, highList, lowList, openList, closeList, biList,
                                    duanList)
        tupo = entanglement.tu_po(entanglementList, timeList, highList, lowList, openList, closeList, biList, duanList)
        v_reverse = entanglement.v_reverse(entanglementList, timeList, highList, lowList, openList, closeList, biList,
                                           duanList)
        duan_pohuai = entanglement.po_huai(timeList, highList, lowList, openList, closeList, biList, duanList)
        # 段中枢
        entanglementHigherList = entanglement.CalcEntanglements(timeList, higherDuanList, duanList, highList, lowList)
        huila_higher = entanglement.la_hui(entanglementHigherList, timeList, highList, lowList, openList, closeList,
                                           duanList, higherDuanList)
        tupo_higher = entanglement.tu_po(entanglementHigherList, timeList, highList, lowList, openList, closeList,
                                         duanList, higherDuanList)
        v_reverse_higher = entanglement.v_reverse(entanglementHigherList, timeList, highList, lowList, openList,
                                                  closeList, duanList, higherDuanList)
        duan_pohuai_higher = entanglement.po_huai(timeList, highList, lowList, openList, closeList, duanList,
                                                  higherDuanList)

        # print("拉回数据:",huila)
        # print("时间：",time_array[-1],close_array[-1])

        if len(huila['buy_zs_huila']['date']) > 0:
            buy_zs_huila = huila['buy_zs_huila']
            # 最后一个信号和当前时间相等, 开始观察
            print("买-当前bar时间：", bar.datetime.strftime("%Y-%m-%d %H:%M"), " 拉回时间：", buy_zs_huila['date'][-1])
            if bar.datetime.strftime("%Y-%m-%d %H:%M") == buy_zs_huila['date'][-1]:
                self.long_stop_lose = buy_zs_huila['stop_lose_price'][-1]
                self.long_stop_win = buy_zs_huila['stop_win_price'][-1]
                self.long_signal_price = buy_zs_huila['data'][-1]
                self.long_signal_date = buy_zs_huila['date'][-1]
                if self.pos == 0:
                    # self.currentPrice = bar.close_price
                    # 同时下停止委托单
                    print("开多:时间 ", self.long_signal_date, " 价格:", self.long_signal_price, " ohlc:", bar.open_price,
                          bar.high_price, bar.low_price, bar.close_price
                          , " 止损：", self.long_stop_lose, " 止盈：", self.long_stop_win)
                    self.buy(bar.close_price, self.amount, False)
                elif self.pos < 0:
                    # 出现反向信号，平掉空单
                    print("出现反向信号，平掉空单,开多单 最新价：", bar.close_price, " ohlc:",
                          bar.open_price, bar.high_price, bar.low_price, bar.close_price,
                          " 止损：", self.long_stop_lose, " 止盈：", self.long_stop_win)
                    self.cover(bar.close_price, abs(self.pos), False)
                    # 开多单
                    self.buy(bar.close_price, self.amount, False)
        if self.pos > 0:
            # print("持有多单：当前价格：", am.close_array[-1], " 止损：", self.long_stop_lose, " 止盈：", self.long_stop_win)
            if am.close_array[-1] <= self.long_stop_lose:
                print("下多单止损单 时间：", timeList[-1], " 价格:", self.long_stop_lose, " ohlc:",
                      bar.open_price, bar.high_price, bar.low_price, bar.close_price)
                self.sell(bar.close_price, abs(self.pos), False)
            # elif am.close_array[-1] >= self.long_stop_win:
            #     print("下多单止赢单 时间：", time_array[-1], " 价格:", self.long_stop_win, " ohlc:",
            #           bar.open_price, bar.high_price, bar.low_price, bar.close_price)
            #     self.sell(self.long_stop_win, abs(self.pos), False)

            if len(duan_pohuai['sell_duan_break']['date']) > 0 and bar.datetime.strftime("%Y-%m-%d %H:%M") == \
                duan_pohuai['sell_duan_break']['date'][-1]:
                print("下多单止赢单 时间：", timeList[-1], " 价格:", self.long_stop_win, " ohlc:",
                      bar.open_price, bar.high_price, bar.low_price, bar.close_price)
                self.sell(bar.close_price, abs(self.pos), False)

            # 本级别出现顶背驰止盈
            # if len(sellMACDBCData['date']) > 0 and sellMACDBCData['date'][-1]

        if len(huila['sell_zs_huila']['date']) > 0:
            sell_zs_huila = huila['sell_zs_huila']
            # 最后一个信号和当前时间相等, 开始观察
            print("卖-当前bar时间：", bar.datetime.strftime("%Y-%m-%d %H:%M"), " 拉回时间：", sell_zs_huila['date'][-1])
            if bar.datetime.strftime("%Y-%m-%d %H:%M") == sell_zs_huila['date'][-1]:
                self.short_stop_lose = sell_zs_huila['stop_lose_price'][-1]
                self.short_stop_win = sell_zs_huila['stop_win_price'][-1]
                self.short_signal_price = sell_zs_huila['data'][-1]
                self.short_signal_date = sell_zs_huila['date'][-1]
                if self.pos == 0:
                    # self.currentPrice = bar.close_price
                    # 同时下停止委托单

                    print("开空:时间 ", self.short_signal_date, " 价格:", self.short_signal_price, " ohlc:", bar.open_price,
                          bar.high_price, bar.low_price, bar.close_price, " 止损：", self.short_stop_lose, " 止盈：",
                          self.short_stop_win)
                    self.short(self.short_signal_price, self.amount, False)
                elif self.pos > 0:
                    # 出现反向信号，平掉多单
                    print("出现反向信号，平掉多单,开空单 最新价：", bar.close_price, " ohlc:",
                          bar.open_price, bar.high_price, bar.low_price, bar.close_price,
                          " 止损：", self.short_stop_lose, " 止盈：", self.short_stop_win)
                    self.sell(bar.close_price, abs(self.pos), False)
                    self.short(bar.close_price, self.amount, False)
        if self.pos < 0:
            # print("持有空单：当前价格：", am.close_array[-1], " 止损：", self.short_stop_lose, " 止盈：", self.short_stop_win)
            if am.close_array[-1] >= self.short_stop_lose:
                print("下空单止损单 时间：", timeList[-1], " 价格:", self.short_stop_lose, " ohlc:",
                      bar.open_price, bar.high_price, bar.low_price, bar.close_price)
                self.cover(bar.close_price, abs(self.pos), False)
            # elif am.close_array[-1] <= self.short_stop_win:
            #     print("下空单止盈单 时间：", time_array[-1], " 价格:", self.short_stop_win, " ohlc:",
            #           bar.open_price, bar.high_price, bar.low_price, bar.close_price)
            #     self.cover(self.short_stop_win, abs(self.pos), False)
            if len(duan_pohuai['buy_duan_break']['date']) > 0 and bar.datetime.strftime("%Y-%m-%d %H:%M") == \
                duan_pohuai['buy_duan_break']['date'][-1]:
                print("下空单止盈单 时间：", timeList[-1], " 价格:", self.short_stop_win, " ohlc:",
                      bar.open_price, bar.high_price, bar.low_price, bar.close_price)
                self.cover(bar.close_price, abs(self.pos), False)

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass
