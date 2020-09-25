from pathlib import Path

from vnpy.vnpy.trader.app import BaseApp
from vnpy.vnpy.trader.constant import Direction
from vnpy.vnpy.trader.object import TickData, BarData, TradeData, OrderData
from vnpy.vnpy.trader.utility import BarGenerator, ArrayManager

from .base import APP_NAME
from .engine import StrategyEngine
from .template import StrategyTemplate
from .backtesting import BacktestingEngine


class PortfolioStrategyApp(BaseApp):
    """"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "组合策略"
    engine_class = StrategyEngine
    widget_name = "PortfolioStrategyManager"
    icon_name = "strategy.ico"
