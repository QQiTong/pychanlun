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
from pychanlun.BiProcess import BiProcess
from pychanlun.DuanProcess import DuanProcess
from pychanlun.KlineProcess import KlineProcess
import pychanlun.entanglement as entanglement
from numpy import array
import talib as ta
import numpy as np
from pychanlun.basic.bi import CalcBi

class ChanLunStrategy(CtaTemplate):
    """"""
    author = "parker"
    amount = 1
    parameters = ["amount"]
    # variables = ["fast_ma0", "fast_ma1", "slow_ma0", "slow_ma1"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(ChanLunStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

        self.bg = BarGenerator(self.on_bar, 3, self.on_3min_bar)
        self.am = ArrayManager(200)
        self.fixed_size = 1

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(5)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
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

        # klineProcess = KlineProcess()
        # count = len(open_array)
        # for i in range(count):
        #     klineProcess.add(high_array[i], low_array[i],time_array)
        #
        # # 笔处理
        # biProcess = BiProcess()
        # biProcess.handle(klineProcess.klineList)
        #
        # # 笔结果
        # biResult = [0 for i in range(len(close_array))]
        # for i in range(len(biProcess.biList)):
        #     item = biProcess.biList[i]
        #     biResult[item.klineList[-1].middle] = item.direction
        #
        # duanProcess = DuanProcess()
        # duanResult = duanProcess.handle(biResult, high_array, low_array)
        # entanglementList = entanglement.CalcEntanglements(time_array, duanResult, biResult, high_array, low_array)
        # huila = entanglement.la_hui(entanglementList, time_array, high_array, low_array, open_array, close_array,
        #                             biResult, duanResult)
        #
        # duan_pohuai = entanglement.po_huai(time_array, high_array, low_array, open_array, close_array, biResult,
        #                                    duanResult)
        # k线处理
        count = len(timeList)
        # 笔结果
        biList = [0 for i in range(count)]
        CalcBi(count, biList, highList, lowList, openList, closeList)

        # 段处理
        duanProcess = DuanProcess()
        duanResult = duanProcess.handle(biList, highList, lowList)

        # 高一级别段处理
        higherDuanProcess = DuanProcess()
        higherDuanResult = higherDuanProcess.handle(duanResult, highList, lowList)

        # 高高一级别段处理
        higherHigherDuanProcess = DuanProcess()
        higherHigherDuanResult = higherHigherDuanProcess.handle(higherDuanResult, highList, lowList)

        # print("段结果:", len(biResult), len(duanResult))
        entanglementList = entanglement.CalcEntanglements(timeList, duanResult, biList, highList, lowList)
        huila = entanglement.la_hui(entanglementList, timeList, highList, lowList, openList, closeList,
                                    biList, duanResult)
        tupo = entanglement.tu_po(entanglementList, timeList, highList, lowList, openList, closeList, biList,
                                  duanResult)
        v_reverse = entanglement.v_reverse(entanglementList, timeList, highList, lowList, openList, closeList,
                                           biList, duanResult)
        duan_pohuai = entanglement.po_huai(timeList, highList, lowList, openList, closeList, biList,
                                           duanResult)


        # print("拉回数据:",huila)
        # print("时间：",time_array[-1],close_array[-1])

        if len(huila['buy_zs_huila']['date']) > 0:
            buy_zs_huila = huila['buy_zs_huila']
            # 最后一个信号和当前时间相等, 开始观察
            print("买-当前bar时间：",bar.datetime.strftime("%Y-%m-%d %H:%M")," 拉回时间：",buy_zs_huila['date'][-1])
            if bar.datetime.strftime("%Y-%m-%d %H:%M") == buy_zs_huila['date'][-1]:
                self.long_stop_lose = buy_zs_huila['stop_lose_price'][-1]
                self.long_stop_win = buy_zs_huila['stop_win_price'][-1]
                self.long_signal_price = buy_zs_huila['data'][-1]
                self.long_signal_date = buy_zs_huila['date'][-1]
                if self.pos == 0:
                    # self.currentPrice = bar.close_price
                    # 同时下停止委托单
                    print("开多:时间 ", self.long_signal_date," 价格:",self.long_signal_price," ohlc:", bar.open_price,bar.high_price,bar.low_price,bar.close_price
                          ," 止损：",self.long_stop_lose," 止盈：",self.long_stop_win)
                    self.buy(bar.close_price, self.amount,False)
                elif self.pos < 0:
                    # 出现反向信号，平掉空单
                    print("出现反向信号，平掉空单,开多单 最新价：", bar.close_price, " ohlc:",
                          bar.open_price, bar.high_price, bar.low_price, bar.close_price,
                          " 止损：", self.long_stop_lose, " 止盈：", self.long_stop_win)
                    self.cover(bar.close_price, abs(self.pos),False)
                    # 开多单
                    self.buy(bar.close_price, self.amount,False)
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

            if len(duan_pohuai['sell_duan_break']['date']) > 0 and bar.datetime.strftime("%Y-%m-%d %H:%M") == duan_pohuai['sell_duan_break']['date'][-1]:
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
                          bar.high_price, bar.low_price, bar.close_price," 止损：",self.short_stop_lose," 止盈：",self.short_stop_win)
                    self.short(self.short_signal_price, self.amount,False)
                elif self.pos > 0:
                    # 出现反向信号，平掉多单
                    print("出现反向信号，平掉多单,开空单 最新价：", bar.close_price, " ohlc:",
                          bar.open_price, bar.high_price, bar.low_price, bar.close_price,
                          " 止损：", self.short_stop_lose, " 止盈：", self.short_stop_win)
                    self.sell(bar.close_price, abs(self.pos),False)
                    self.short(bar.close_price, self.amount,False)
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
        # orderId = trade.orderid
        # # 多单成交后
        # if self.pos > 0:
        #     print("多单成交 orderId:", orderId, "止损：",self.long_stop_lose," 止盈：", self.long_stop_win,
        #           "当前价格：",self.am.close_array[-1])
        #     self.sell(self.long_stop_lose, abs(self.pos), True)
        #     self.sell(self.long_stop_win, abs(self.pos), True)
        # elif self.pos < 0:
        #     print("空单成交 orderId:", orderId, "止损：",self.short_stop_lose," 止盈：", self.short_stop_win,
        #           "当前价格：",self.am.close_array[-1])
        #     self.cover(self.short_stop_lose, abs(self.pos), True)
        #     self.cover(self.short_stop_lose, abs(self.pos), True)
        # else:
        #     # 本身的止盈止损单也会触发而成交
        #     print("止盈止损单触发回调orderId",orderId)

        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        print("on_stop_order",stop_order)
        pass

