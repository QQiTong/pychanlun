from typing import Sequence, Type

from vnpy.vnpy.event import EventEngine, Event
from vnpy.vnpy.trader.engine import MainEngine
from vnpy.vnpy.trader.gateway import BaseGateway
from vnpy.vnpy.trader.event import EVENT_LOG

from .engine import ScriptEngine


def process_log_event(event: Event):
    """"""
    log = event.data
    print(f"{log.time}\t{log.msg}")


def init_cli_trading(gateways: Sequence[Type[BaseGateway]]):
    """"""
    event_engine = EventEngine()
    event_engine.register(EVENT_LOG, process_log_event)

    main_engine = MainEngine(event_engine)
    for gateway in gateways:
        main_engine.add_gateway(gateway)

    script_engine = main_engine.add_engine(ScriptEngine)

    return script_engine
