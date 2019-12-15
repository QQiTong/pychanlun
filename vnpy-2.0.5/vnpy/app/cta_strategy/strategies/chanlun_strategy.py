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

from back import divergence
from back.BiProcess import BiProcess
from back.DuanProcess import DuanProcess
from back.KlineProcess import KlineProcess
import back.entanglement as entanglement
from numpy import array
import talib as ta
import numpy as np

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

        self.bg = BarGenerator(self.on_bar, 15, self.on_15min_bar)
        self.am = ArrayManager()
        self.fixed_size = 1

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
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.bg.update_bar(bar)

    def on_15min_bar(self, bar: BarData):
        """"""
        self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        open_array = am.open_array
        high_array = am.high_array
        low_array = am.low_array
        close_array = am.close_array
        time_array = am.time_array

        klineProcess = KlineProcess()
        count = len(open_array)
        for i in range(count):
            klineProcess.add(high_array[i], low_array[i],time_array)

        # 笔处理
        biProcess = BiProcess()
        biProcess.handle(klineProcess.klineList)

        # 笔结果
        biResult = [0 for i in range(len(close_array))]
        for i in range(len(biProcess.biList)):
            item = biProcess.biList[i]
            biResult[item.klineList[-1].middle] = item.direction

        duanProcess = DuanProcess()
        duanResult = duanProcess.handle(biResult, high_array, low_array)
        entanglementList = entanglement.calcEntanglements(time_array, duanResult, biResult, high_array, low_array)
        huila = entanglement.la_hui(entanglementList, time_array, high_array, low_array, open_array, close_array,
                                    biResult, duanResult)
        diff_array = self.getMacd(close_array)[0].tolist()
        dea_array = self.getMacd(close_array)[1].tolist()
        macd_array = self.getMacd(close_array)[2].tolist()


        beichiData = divergence.calcAndNote(time_array, high_array, low_array, open_array, close_array, macd_array,
                                            diff_array, dea_array, biProcess.biList, biResult, duanResult)
        buyMACDBCData = beichiData['buyMACDBCData']
        sellMACDBCData = beichiData['sellMACDBCData']
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
                    self.buy(close_array[-1], self.amount)
                elif self.pos < 0:
                    # 出现反向信号，平掉空单
                    print("出现反向信号，平掉空单,开多单 最新价：", bar.close_price, " ohlc:",
                          bar.open_price, bar.high_price, bar.low_price, bar.close_price,
                          " 止损：", self.long_stop_lose, " 止盈：", self.long_stop_win)
                    self.cover(bar.close_price, abs(self.pos))
                    # 开多单
                    self.buy(self.long_signal_price, self.amount)
        if self.pos > 0:
            # print("持有多单：当前价格：", am.close_array[-1], " 止损：", self.long_stop_lose, " 止盈：", self.long_stop_win)
            if am.close_array[-1] <= self.long_stop_lose:
                print("下多单止损单 时间：", time_array[-1], " 价格:", self.long_stop_lose, " ohlc:",
                      bar.open_price, bar.high_price, bar.low_price, bar.close_price)
                self.sell(self.long_stop_lose, abs(self.pos), False)
            elif am.close_array[-1] >= self.long_stop_win:
                print("下多单止赢单 时间：", time_array[-1], " 价格:", self.long_stop_win, " ohlc:",
                      bar.open_price, bar.high_price, bar.low_price, bar.close_price)
                self.sell(self.long_stop_win, abs(self.pos), False)
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
                    self.short(close_array[-1], self.amount)
                elif self.pos > 0:
                    # 出现反向信号，平掉多单
                    print("出现反向信号，平掉多单,开空单 最新价：", bar.close_price, " ohlc:",
                          bar.open_price, bar.high_price, bar.low_price, bar.close_price,
                          " 止损：", self.short_stop_lose, " 止盈：", self.short_stop_win)
                    self.sell(bar.close_price, abs(self.pos))
                    self.short(self.short_signal_price, self.amount)
        if self.pos < 0:
            # print("持有空单：当前价格：", am.close_array[-1], " 止损：", self.short_stop_lose, " 止盈：", self.short_stop_win)
            if am.close_array[-1] >= self.short_stop_lose:
                print("下空单止损单 时间：", time_array[-1], " 价格:", self.short_stop_lose, " ohlc:",
                      bar.open_price, bar.high_price, bar.low_price, bar.close_price)
                self.cover(self.short_stop_lose, abs(self.pos), False)
            elif am.close_array[-1] <= self.short_stop_win:
                print("下空单止盈单 时间：", time_array[-1], " 价格:", self.short_stop_win, " ohlc:",
                      bar.open_price, bar.high_price, bar.low_price, bar.close_price)
                self.cover(self.short_stop_win, abs(self.pos), False)


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

    def getMacd(self,closePriceList):
        close = array(closePriceList)
        macd = ta.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        result = np.nan_to_num(macd)
        return result