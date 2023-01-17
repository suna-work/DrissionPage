# -*- coding:utf-8 -*-

from configparser import RawConfigParser
from typing import Any


class OptionsManager(object):
    ini_path: str = ...
    _conf: RawConfigParser = ...
    paths: dict = ...
    chrome_options: dict = ...
    session_options: dict = ...
    timeouts: dict = ...
    proxies: dict = ...

    def __init__(self, path: str = None): ...

    def __getattr__(self, item) -> dict: ...

    def get_value(self, section: str, item: str) -> Any: ...

    def get_option(self, section: str) -> dict: ...

    def set_item(self, section: str, item: str, value: Any) -> None: ...

    def remove_item(self, section: str, item: str) -> None: ...

    def save(self, path: str = None) -> str: ...

    def save_to_default(self) -> str: ...
