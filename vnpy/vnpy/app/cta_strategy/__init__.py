from pathlib import Path

from vnpy.vnpy.trader.app import BaseApp
from vnpy.vnpy.trader.constant import Direction
from vnpy.vnpy.trader.object import TickData, BarData, TradeData, OrderData
from vnpy.vnpy.trader.utility import BarGenerator, ArrayManager

from .base import APP_NAME, StopOrder
from .engine import CtaEngine
from .template import CtaTemplate, CtaSignal, TargetPosTemplate


class CtaStrategyApp(BaseApp):
    """"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "CTA策略"
    engine_class = CtaEngine
    widget_name = "CtaManager"
    icon_name = "cta.ico"
