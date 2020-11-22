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


class MacdStrategy(CtaTemplate):
    author = "用Python的交易员"

    fast_window = 5
    slow_window = 34

    fast_ma0 = 0.0
    fast_ma1 = 0.0

    slow_ma0 = 0.0
    slow_ma1 = 0.0

    middle_ma0 = 0.0
    middle_ma1 = 0.0
    middle_ma2 = 0.0


    parameters = ["fast_window", "slow_window"]

    variables = ["fast_ma0", "fast_ma1", "slow_ma0", "slow_ma1"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(100)

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
        """
        Callback of new bar data update.
        """
        self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        macd = am.macd(12, 26, 9, array=True)

        dif = macd[0]
        dea = macd[1]

        dif1 = dif[-1]
        dif2 = dif[-2]
        dif3 = dif[-4]

        dea1 = dea[-1]
        dea2 = dea[-2]
        dea3 = dea[-4]

        macd = macd[2]

        macd_cross_over = (dif1 > dea1 and dif2 < dea2) or (dif1 > dea1 and dif3 < dea3)
        # macd_cross_over =(dif1 > dea1 and dif2 < dea2)
        macd_cross_below = (dif1 < dea1 and dif2 > dea2) or (dif1 < dea1 and dif3 > dea3)
        # macd_cross_below = (dif1 < dea1 and dif2 > dea2)

        fast_ma = am.sma(self.fast_window, array=True)
        self.fast_ma0 = fast_ma[-1]
        self.fast_ma1 = fast_ma[-2]
        self.fast_ma2 = fast_ma[-4]

        slow_ma = am.sma(self.slow_window, array=True)
        self.slow_ma0 = slow_ma[-1]
        self.slow_ma1 = slow_ma[-2]
        self.slow_ma2 = slow_ma[-4]

        middle_ma = am.sma(self.middle_window, array=True)
        self.middle_ma0 = middle_ma[-1]
        self.middle_ma1 = middle_ma[-2]
        self.middle_ma2 = middle_ma[-4]


        # kd = am.kd(9, 3, array=True)
        # k = kd[0]
        # d = kd[1]
        # long_addition = bar.close_price > self.slow_ma0 and bar.close_price > self.fast_ma0
        long_addition = bar.close_price > self.middle_ma0
        # short_addition = bar.close_price < self.slow_ma0 and bar.close_price < self.fast_ma0
        short_addition = bar.close_price < self.middle_ma0

        ma_cross_over = (self.fast_ma0 > self.slow_ma0 and self.fast_ma1 < self.slow_ma1) or \
                        (self.fast_ma0 > self.slow_ma0 and self.fast_ma2 < self.slow_ma2)
        # ma_cross_over =  (self.fast_ma0 > self.slow_ma0 and self.fast_ma1 < self.slow_ma1)

        ma_cross_below = (self.fast_ma0 < self.slow_ma0 and self.fast_ma1 > self.slow_ma1) or \
                         (self.fast_ma0 < self.slow_ma0 and self.fast_ma2 > self.slow_ma2)
        # ma_cross_below = (self.fast_ma0 < self.slow_ma0 and self.fast_ma1 > self.slow_ma1)

        # if macd_cross_over and long_addition:
        if macd_cross_over and long_addition:
            if self.pos == 0:
                self.buy(bar.close_price, 1)
                print("macd 金叉-做多", bar.datetime)
            elif self.pos < 0:
                self.cover(bar.close_price, 1)
                self.buy(bar.close_price, 1)
                print("macd 金叉-反手-做多", bar.datetime)

        elif macd_cross_below and short_addition:
            if self.pos == 0:
                self.short(bar.close_price, 1)
                print("macd 死叉-做空", bar.datetime)

            elif self.pos > 0:
                self.sell(bar.close_price, 1)
                self.short(bar.close_price, 1)
                print("macd 死叉-反手-做空", bar.datetime)


        # elif ma_cross_over and macd[-1] > 0 and long_addition:
        elif ma_cross_over and macd[-1] > 0:
            if self.pos == 0:
                self.buy(bar.close_price, 1)
                print("ma 金叉-做多", bar.datetime)

            elif self.pos < 0:
                self.cover(bar.close_price, 1)
                self.buy(bar.close_price, 1)
                print("ma 金叉-反手-做多", bar.datetime)


        # elif ma_cross_below and macd[-1] < 0 and short_addition:
        elif ma_cross_below and macd[-1] < 0:
            if self.pos == 0:
                self.short(bar.close_price, 1)
                print("ma 死叉-做空", bar.datetime)

            elif self.pos > 0:
                self.sell(bar.close_price, 1)
                self.short(bar.close_price, 1)
                print("ma 死叉-反手-做空", bar.datetime)

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
