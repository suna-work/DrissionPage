# -*- coding: utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from queue import Queue
from threading import Thread, Event
from typing import Union, Callable, Dict, Optional

from websocket import WebSocket


class GenericAttr(object):
    def __init__(self, name: str, tab: ChromiumDriver): ...

    def __getattr__(self, item: str) -> Callable: ...

    def __setattr__(self, key: str, value: Callable) -> None: ...


class ChromiumDriver(object):
    id: str
    address: str
    type: str
    _debug: bool
    alert_flag: bool
    _websocket_url: str
    _cur_id: int
    _ws: Optional[WebSocket]
    _recv_th: Thread
    _handle_event_th: Thread
    _stopped: Event
    event_handlers: dict
    method_results: dict
    event_queue: Queue

    def __init__(self, tab_id: str, tab_type: str, address: str): ...

    def _send(self, message: dict, timeout: float = None) -> dict: ...

    def _recv_loop(self) -> None: ...

    def _handle_event_loop(self) -> None: ...

    def __getattr__(self, item: str) -> Callable: ...

    def call_method(self, _method: str, **kwargs) -> dict: ...

    def start(self) -> bool: ...

    def stop(self) -> bool: ...

    def set_listener(self, event: str, callback: Union[Callable, None]) -> None: ...

    def __str__(self) -> str: ...


class BrowserDriver(ChromiumDriver):
    BROWSERS: Dict[str, ChromiumDriver] = ...