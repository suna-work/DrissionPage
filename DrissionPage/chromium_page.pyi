# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from typing import Union, Tuple, List

from .browser_download_manager import BrowserDownloadManager
from .chromium_base import ChromiumBase
from .chromium_driver import ChromiumDriver
from .chromium_tab import ChromiumTab
from .configs.chromium_options import ChromiumOptions
from .setter import ChromiumPageSetter
from .waiter import ChromiumPageWaiter


class ChromiumPage(ChromiumBase):

    def __init__(self,
                 addr_driver_opts: Union[str, int, ChromiumOptions, ChromiumDriver] = None,
                 tab_id: str = None,
                 timeout: float = None):
        self._driver_options: ChromiumOptions = ...
        self._process_id: str = ...
        self._dl_mgr: BrowserDownloadManager = ...
        self._main_tab: str = ...
        self._alert: Alert = ...
        self._browser_driver: ChromiumDriver = ...
        self._rect: ChromiumTabRect = ...

    def _connect_browser(self,
                         addr_driver_opts: Union[str, ChromiumDriver] = None,
                         tab_id: str = None) -> None: ...

    def _set_start_options(self, addr_driver_opts: Union[str, ChromiumDriver], none) -> None: ...

    def _page_init(self) -> None: ...

    @property
    def browser_driver(self) -> ChromiumDriver: ...

    @property
    def tabs_count(self) -> int: ...

    @property
    def tabs(self) -> List[str]: ...

    @property
    def rect(self) -> ChromiumTabRect: ...

    @property
    def wait(self) -> ChromiumPageWaiter: ...

    @property
    def main_tab(self) -> str: ...

    @property
    def latest_tab(self) -> str: ...

    @property
    def process_id(self) -> Union[None, int]: ...

    @property
    def set(self) -> ChromiumPageSetter: ...

    def get_tab(self, tab_id: str = None) -> ChromiumTab: ...

    def find_tabs(self, title: str = None, url: str = None,
                  tab_type: Union[str, list, tuple, set] = None, single: bool = True) -> Union[str, List[str]]: ...

    def new_tab(self, url: str = None, switch_to: bool = False) -> str: ...

    def to_main_tab(self) -> None: ...

    def to_tab(self, tab_or_id: Union[str, ChromiumTab] = None, activate: bool = True) -> None: ...

    def _to_tab(self, tab_or_id: Union[str, ChromiumTab] = None, activate: bool = True,
                read_doc: bool = True) -> None: ...

    def close_tabs(self, tabs_or_ids: Union[
        str, ChromiumTab, List[Union[str, ChromiumTab]], Tuple[Union[str, ChromiumTab]]] = None,
                   others: bool = False) -> None: ...

    def close_other_tabs(self, tabs_or_ids: Union[
        str, ChromiumTab, List[Union[str, ChromiumTab]], Tuple[Union[str, ChromiumTab]]] = None) -> None: ...

    def handle_alert(self, accept: bool = True, send: str = None, timeout: float = None) -> Union[str, False]: ...

    def quit(self) -> None: ...

    def _on_alert_close(self, **kwargs): ...

    def _on_alert_open(self, **kwargs): ...


class ChromiumTabRect(object):
    def __init__(self, page: ChromiumPage):
        self._page: ChromiumPage = ...

    @property
    def window_state(self) -> str: ...

    @property
    def browser_location(self) -> Tuple[int, int]: ...

    @property
    def page_location(self) -> Tuple[int, int]: ...

    @property
    def viewport_location(self) -> Tuple[int, int]: ...

    @property
    def browser_size(self) -> Tuple[int, int]: ...

    @property
    def page_size(self) -> Tuple[int, int]: ...

    @property
    def viewport_size(self) -> Tuple[int, int]: ...

    @property
    def viewport_size_with_scrollbar(self) -> Tuple[int, int]: ...

    def _get_page_rect(self) -> dict: ...

    def _get_browser_rect(self) -> dict: ...


class Alert(object):

    def __init__(self):
        self.activated: bool = ...
        self.text: str = ...
        self.type: str = ...
        self.defaultPrompt: str = ...
        self.response_accept: str = ...
        self.response_text: str = ...


def get_rename(original: str, rename: str) -> str: ...
