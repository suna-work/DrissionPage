# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from http.cookiejar import Cookie
from pathlib import Path
from typing import Union, Tuple, Literal

from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from requests.cookies import RequestsCookieJar

from .chromium_base import ChromiumBase, ChromiumPageScroll
from .chromium_element import ChromiumElement
from .chromium_frame import ChromiumFrame
from .chromium_page import ChromiumPage
from .chromium_tab import ChromiumTab
from .session_page import SessionPage
from .web_page import WebPage

FILE_EXISTS = Literal['skip', 'rename', 'overwrite', 's', 'r', 'o']


class ChromiumBaseSetter(object):
    def __init__(self, page):
        self._page: ChromiumBase = ...

    @property
    def load_strategy(self) -> PageLoadStrategy: ...

    @property
    def scroll(self) -> PageScrollSetter: ...

    def retry_times(self, times: int) -> None: ...

    def retry_interval(self, interval: float) -> None: ...

    def timeouts(self, implicit: float = None, page_load: float = None, script: float = None) -> None: ...

    def user_agent(self, ua: str, platform: str = None) -> None: ...

    def session_storage(self, item: str, value: Union[str, bool]) -> None: ...

    def local_storage(self, item: str, value: Union[str, bool]) -> None: ...

    def cookie(self, cookies: Union[RequestsCookieJar, str, dict]) -> None: ...

    def cookies(self, cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> None: ...

    def headers(self, headers: dict) -> None: ...

    def upload_files(self, files: Union[str, list, tuple]) -> None: ...


class TabSetter(ChromiumBaseSetter):
    def __init__(self, page): ...

    def download_path(self, path: Union[str, Path]) -> None: ...

    def download_file_name(self, name: str) -> None: ...

    def when_download_file_exists(self, mode: FILE_EXISTS) -> None: ...


class ChromiumPageSetter(TabSetter):
    _page: ChromiumPage = ...

    def main_tab(self, tab_id: str = None) -> None: ...

    @property
    def window(self) -> WindowSetter: ...

    def tab_to_front(self, tab_or_id: Union[str, ChromiumTab] = None) -> None: ...


class SessionPageSetter(object):
    def __init__(self, page: SessionPage):
        self._page: SessionPage = ...

    def retry_times(self, times: int) -> None: ...

    def retry_interval(self, interval: float) -> None: ...

    def download_path(self, path: Union[str, Path]) -> None: ...

    def timeout(self, second: float) -> None: ...

    def cookie(self, cookie: Union[Cookie, str, dict]) -> None: ...

    def cookies(self, cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> None: ...

    def headers(self, headers: dict) -> None: ...

    def header(self, attr: str, value: str) -> None: ...

    def user_agent(self, ua: str) -> None: ...

    def proxies(self, http: str = None, https: str = None) -> None: ...

    def auth(self, auth: Union[Tuple[str, str], HTTPBasicAuth, None]) -> None: ...

    def hooks(self, hooks: Union[dict, None]) -> None: ...

    def params(self, params: Union[dict, None]) -> None: ...

    def verify(self, on_off: Union[bool, None]) -> None: ...

    def cert(self, cert: Union[str, Tuple[str, str], None]) -> None: ...

    def stream(self, on_off: Union[bool, None]) -> None: ...

    def trust_env(self, on_off: Union[bool, None]) -> None: ...

    def max_redirects(self, times: Union[int, None]) -> None: ...

    def add_adapter(self, url: str, adapter: HTTPAdapter) -> None: ...


class WebPageSetter(ChromiumPageSetter):
    _page: WebPage = ...
    _session_setter: SessionPageSetter = ...
    _chromium_setter: ChromiumPageSetter = ...

    def user_agent(self, ua: str, platform: str = None) -> None: ...

    def headers(self, headers: dict) -> None: ...

    def cookies(self, cookies) -> None: ...


class WebPageTabSetter(TabSetter):
    _page: WebPage = ...
    _session_setter: SessionPageSetter = ...
    _chromium_setter: ChromiumBaseSetter = ...

    def user_agent(self, ua: str, platform: str = None) -> None: ...

    def headers(self, headers: dict) -> None: ...

    def cookies(self, cookies) -> None: ...


class ChromiumElementSetter(object):
    def __init__(self, ele: ChromiumElement):
        self._ele: ChromiumElement = ...

    def attr(self, attr: str, value: str) -> None: ...

    def prop(self, prop: str, value: str) -> None: ...

    def innerHTML(self, html: str) -> None: ...


class ChromiumFrameSetter(ChromiumBaseSetter):
    _page: ChromiumFrame = ...

    def attr(self, attr: str, value: str) -> None: ...


class PageLoadStrategy(object):
    def __init__(self, page: ChromiumBase):
        self._page: ChromiumBase = ...

    def __call__(self, value: str) -> None: ...

    def normal(self) -> None: ...

    def eager(self) -> None: ...

    def none(self) -> None: ...


class PageScrollSetter(object):
    def __init__(self, scroll: ChromiumPageScroll):
        self._scroll: ChromiumPageScroll = ...

    def wait_complete(self, on_off: bool = True): ...

    def smooth(self, on_off: bool = True): ...


class WindowSetter(object):

    def __init__(self, page: ChromiumPage):
        self._page: ChromiumPage = ...
        self._window_id: str = ...

    def maximized(self) -> None: ...

    def minimized(self) -> None: ...

    def fullscreen(self) -> None: ...

    def normal(self) -> None: ...

    def size(self, width: int = None, height: int = None) -> None: ...

    def location(self, x: int = None, y: int = None) -> None: ...

    def hide(self) -> None: ...

    def show(self) -> None: ...

    def _get_info(self) -> dict: ...

    def _perform(self, bounds: dict) -> None: ...
