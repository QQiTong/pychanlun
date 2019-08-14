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


class ChanLunStrategy(CtaTemplate):
    """"""

    author = "parker"

    fast_window = 12
    slow_window = 26
    signal_window = 9

    fast_ma0 = 0.0
    fast_ma1 = 0.0

    slow_ma0 = 0.0
    slow_ma1 = 0.0
    change = 0.0002

    parameters = ["fast_window", "slow_window","change"]
    variables = ["fast_ma0", "fast_ma1", "slow_ma0", "slow_ma1"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(ChanLunStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

        self.bg = BarGenerator(self.on_bar, 3, self.on_3min_bar)
        self.am = ArrayManager(2000)
        #added
        self.buyFlag = False
        self.sellFlag = False
        # 当前价格
        self.currentPrice = 0
        # 止损价格
        self.stopPrice = 0
        # 止赢价格
        self.targetPrice = 0

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

    def on_3min_bar(self, bar: BarData):
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

        diff_array,dea_array,macd_array = am.macd(self.fast_window, self.slow_window, self.signal_window, array=True)


        beichiData = divergence.calc(time_array, macd_array, diff_array, dea_array, biProcess.biList, duanResult)

        print("背驰数据:",beichiData)
        if len(beichiData.buyMACDBCData) > 0:
            lastBeichiData = beichiData.buyMACDBCData[-1]
            # 最后一个信号和当前时间相等, 开始观察
            if bar.datetime.strftime("%Y-%m-%d %H:%M") == lastBeichiData['date'][-1]:
                self.buyFlag = True
                self.sellFlag = False
                self.currentPrice = bar.close_price
                print(lastBeichiData['date'][-1],"线顶背->当前价格",)

        if len(beichiData.sellMACDBCData) > 0:
            lastBeichiData = beichiData.sellMACDBCData[-1]
            # 最后一个信号和当前时间相等, 开始观察
            if bar.datetime.strftime("%Y-%m-%d %H:%M") == lastBeichiData['date'][-1]:
                self.sellFlag = True
                self.buyFlag = False
                self.currentPrice = bar.close_price

                print(lastBeichiData['date'][-1],"线顶背",)

        # dif, dea, macd = am.macd(self.fast_window, self.slow_window,self.signal_window,array=True)
        # self.fast_ma0 = dif[-1]
        # self.fast_ma1 = dif[-2]
        #
        # self.slow_ma0 = dea[-1]
        # self.slow_ma1 = dea[-2]
        #
        # cross_over = self.fast_ma0 > self.slow_ma0 and self.fast_ma1 < self.slow_ma1
        # cross_below = self.fast_ma0 < self.slow_ma0 and self.fast_ma1 > self.slow_ma1
        #
        # # 涨跌幅
        # buy_condition = (bar.close_price - bar.open_price) / bar.open_price >= self.change
        # sell_condition = (bar.close_price - bar.open_price) / bar.open_price <= -self.change
        # # print("am长度:",len(am.close))
        # # and buy_condition and sell_condition
        # if cross_over:
        #     if self.pos == 0 and buy_condition :
        #         print("开多:", bar.datetime, bar.open_price,bar.high_price,bar.low_price,bar.close_price, dif[-1], dea[-1], macd[-1])
        #         self.buy(bar.close_price, 1)
        #     elif self.pos < 0:
        #         print("平空:", bar.datetime, bar.open_price,bar.high_price,bar.low_price,bar.close_price, dif[-1], dea[-1], macd[-1])
        #         self.cover(bar.close_price, 1)
        #         # self.buy(bar.close_price, 1)
        #
        # elif cross_below:
        #     if self.pos == 0 and sell_condition:
        #         print("开空:",bar.datetime, bar.open_price,bar.high_price,bar.low_price,bar.close_price, dif[-1], dea[-1], macd[-1])
        #
        #         self.short(bar.close_price, 1)
        #     elif self.pos > 0:
        #         print("平多:", bar.datetime, bar.open_price,bar.high_price,bar.low_price,bar.close_price, dif[-1], dea[-1], macd[-1])
        #         self.sell(bar.close_price, 1)
        #         # self.short(bar.close_price, 1)
        # self.put_event()

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
