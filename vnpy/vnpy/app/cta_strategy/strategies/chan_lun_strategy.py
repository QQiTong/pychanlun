from pychanlun import entanglement
from pychanlun.basic.bi import CalcBi
from pychanlun.basic.duan import CalcDuan
from vnpy.vnpy.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)


class ChanLunStrategy(CtaTemplate):
    """"""
    author = "用Python的交易员"
    # 本级别
    openList = []
    highList = []
    lowList = []
    closeList = []
    timeList = []
    timeIndexList = []

    amount = 1
    # 高级别
    openPriceListBigLevel = []
    highListBigLevel = []
    lowListBigLevel = []
    closePriceListBigLevel = []
    timeListBigLevel = []
    timeIndexListBigLevel = []

    # 高高级别
    openPriceListBigLevel2 = []
    highListBigLevel2 = []
    lowListBigLevel2 = []
    closePriceListBigLevel2 = []
    timeListBigLevel2 = []
    timeIndexListBigLevel2 = []
    parameters = ["amount"]
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg5 = BarGenerator(self.on_bar, 5, self.on_5min_bar)
        self.am5 = ArrayManager(1000)


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

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg5.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.bg5.update_bar(bar)

    def on_5min_bar(self, bar: BarData):
        """"""
        self.cancel_all()

        self.am5.update_bar(bar)
        if not self.am5.inited:
            return

        self.openList = self.am5.open_array
        self.highList = self.am5.high_array
        self.lowList = self.am5.low_array
        self.closeList = self.am5.close_array
        self.timeList = self.am5.time_array
        self.timeIndexList = self.am5.time_index_array

        count = len(self.timeList)
        print("on_5min_bar",count)
        # 本级别笔
        self.biList = [0 for i in range(count)]
        CalcBi(count, self.timeList, self.highList, self.lowList, self.openList, self.closeList)

        # 本级别段处理
        self.duanList = [0 for i in range(count)]
        CalcDuan(count, self.duanList, self.timeList, self.highList, self.lowList)

        self.higherDuanList = [0 for i in range(count)]
        CalcDuan(count, self.higherDuanList, self.duanList, self.highList, self.lowList)

        # 高高一级别段处理
        self.higherHigherDuanList = [0 for i in range(count)]
        CalcDuan(count, self.higherHigherDuanList, self.higherDuanList, self.highList, self.lowList)

        entanglementList = entanglement.CalcEntanglements(self.timeList, self.duanList, self.timeList, self.highList, self.lowList)
        huila = entanglement.la_hui(entanglementList, self.timeList, self.highList, self.lowList, self.openList, self.closeList, self.timeList,
                                    self.duanList)
        tupo = entanglement.tu_po(entanglementList, self.timeList, self.highList, self.lowList, self.openList, self.closeList, self.timeList, self.duanList)
        v_reverse = entanglement.v_reverse(entanglementList, self.timeList, self.highList, self.lowList, self.openList, self.closeList, self.timeList,
                                           self.duanList)
        duan_pohuai = entanglement.po_huai(self.timeList, self.highList, self.lowList, self.openList, self.closeList, self.timeList, self.duanList)
        # 段中枢
        entanglementHigherList = entanglement.CalcEntanglements(self.timeList, self.higherDuanList, self.duanList, self.highList, self.lowList)
        huila_higher = entanglement.la_hui(entanglementHigherList, self.timeList, self.highList, self.lowList, self.openList, self.closeList,
                                           self.duanList, self.higherDuanList)
        tupo_higher = entanglement.tu_po(entanglementHigherList, self.timeList, self.highList, self.lowList, self.openList, self.closeList,
                                         self.duanList, self.higherDuanList)
        v_reverse_higher = entanglement.v_reverse(entanglementHigherList, self.timeList, self.highList, self.lowList, self.openList,
                                                  self.closeList, self.duanList, self.higherDuanList)
        duan_pohuai_higher = entanglement.po_huai(self.timeList, self.highList, self.lowList, self.openList, self.closeList, self.duanList,
                                                  self.higherDuanList)

        print("拉回数据:",huila)

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
            # print("持有多单：当前价格：", self.am5.close_array[-1], " 止损：", self.long_stop_lose, " 止盈：", self.long_stop_win)
            if self.am5.close_array[-1] <= self.long_stop_lose:
                print("下多单止损单 时间：", self.timeList[-1], " 价格:", self.long_stop_lose, " ohlc:",
                      bar.open_price, bar.high_price, bar.low_price, bar.close_price)
                self.sell(bar.close_price, abs(self.pos), False)
            # elif self.am5.close_array[-1] >= self.long_stop_win:
            #     print("下多单止赢单 时间：", time_array[-1], " 价格:", self.long_stop_win, " ohlc:",
            #           bar.open_price, bar.high_price, bar.low_price, bar.close_price)
            #     self.sell(self.long_stop_win, abs(self.pos), False)

            if len(duan_pohuai['sell_duan_break']['date']) > 0 and bar.datetime.strftime("%Y-%m-%d %H:%M") == \
                duan_pohuai['sell_duan_break']['date'][-1]:
                print("下多单止赢单 时间：", self.timeList[-1], " 价格:", self.long_stop_win, " ohlc:",
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
            # print("持有空单：当前价格：", self.am5.close_array[-1], " 止损：", self.short_stop_lose, " 止盈：", self.short_stop_win)
            if self.am5.close_array[-1] >= self.short_stop_lose:
                print("下空单止损单 时间：", self.timeList[-1], " 价格:", self.short_stop_lose, " ohlc:",
                      bar.open_price, bar.high_price, bar.low_price, bar.close_price)
                self.cover(bar.close_price, abs(self.pos), False)
            # elif self.am5.close_array[-1] <= self.short_stop_win:
            #     print("下空单止盈单 时间：", time_array[-1], " 价格:", self.short_stop_win, " ohlc:",
            #           bar.open_price, bar.high_price, bar.low_price, bar.close_price)
            #     self.cover(self.short_stop_win, abs(self.pos), False)
            if len(duan_pohuai['buy_duan_break']['date']) > 0 and bar.datetime.strftime("%Y-%m-%d %H:%M") == \
                duan_pohuai['buy_duan_break']['date'][-1]:
                print("下空单止盈单 时间：", self.timeList[-1], " 价格:", self.short_stop_win, " ohlc:",
                      bar.open_price, bar.high_price, bar.low_price, bar.close_price)
                self.cover(bar.close_price, abs(self.pos), False)

        self.put_event()



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
