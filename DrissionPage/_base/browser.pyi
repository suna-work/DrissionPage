# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from typing import List, Optional, Union

from .chromium_driver import BrowserDriver
from .._pages.chromium_page import ChromiumPage
from .._units.download_manager import BrowserDownloadManager


class Browser(object):
    BROWSERS: dict = ...
    page: ChromiumPage = ...
    _driver: BrowserDriver = ...
    id: str = ...
    address: str = ...
    _frames: dict = ...
    _process_id: Optional[int] = ...
    _dl_mgr: BrowserDownloadManager = ...
    _connected: bool = ...

    def __new__(cls, address: str, browser_id: str, page: ChromiumPage): ...

    def __init__(self, address: str, browser_id: str, page: ChromiumPage): ...

    def run_cdp(self, cmd, **cmd_args) -> dict: ...

    @property
    def driver(self) -> BrowserDriver: ...

    @property
    def tabs_count(self) -> int: ...

    @property
    def tabs(self) -> List[str]: ...

    @property
    def process_id(self) -> Optional[int]: ...

    def find_tabs(self, title: str = None, url: str = None,
                  tab_type: Union[str, list, tuple] = None, single: bool = True) -> Union[str, List[str]]: ...

    def close_tab(self, tab_id: str) -> None: ...

    def activate_tab(self, tab_id: str) -> None: ...

    def get_window_bounds(self, tab_id: str = None) -> dict: ...

    def connect_to_page(self) -> None: ...

    def _onTargetDestroyed(self, **kwargs): ...

    def quit(self) -> None: ...
