# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from typing import Union, Tuple, List, Any

from requests import Session, Response

from .chromium_frame import ChromiumFrame
from .chromium_page import ChromiumPage
from .chromium_tab import WebPageTab
from .session_page import SessionPage
from .._base.base import BasePage
from .._base.chromium_driver import ChromiumDriver
from .._configs.chromium_options import ChromiumOptions
from .._configs.session_options import SessionOptions
from .._elements.chromium_element import ChromiumElement
from .._elements.session_element import SessionElement
from .._units.setter import WebPageSetter


class WebPage(SessionPage, ChromiumPage, BasePage):

    def __init__(self,
                 mode: str = 'd',
                 timeout: float = None,
                 driver_or_options: Union[ChromiumDriver, ChromiumOptions, bool] = None,
                 session_or_options: Union[Session, SessionOptions, bool] = None) -> None:
        self._mode: str = ...
        self._has_driver: bool = ...
        self._has_session: bool = ...
        self._session_options: Union[SessionOptions, None] = ...
        self._driver_options: Union[ChromiumOptions, None] = ...

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str, ChromiumElement, SessionElement],
                 timeout: float = None) -> Union[ChromiumElement, SessionElement]: ...

    # -----------------共有属性和方法-------------------
    @property
    def url(self) -> Union[str, None]: ...

    @property
    def _browser_url(self) -> Union[str, None]: ...

    @property
    def title(self) -> str: ...

    @property
    def html(self) -> str: ...

    @property
    def json(self) -> dict: ...

    @property
    def response(self) -> Response: ...

    @property
    def mode(self) -> str: ...

    @property
    def cookies(self) -> dict: ...

    @property
    def user_agent(self) -> str: ...

    @property
    def session(self) -> Session: ...

    @property
    def _session_url(self) -> str: ...

    @property
    def timeout(self) -> float: ...

    @timeout.setter
    def timeout(self, second: float) -> None: ...

    def get(self,
            url: str,
            show_errmsg: bool = False,
            retry: int | None = None,
            interval: float | None = None,
            timeout: float | None = None,
            params: dict | None = ...,
            data: Union[dict, str, None] = ...,
            json: Union[dict, str, None] = ...,
            headers: dict | None = ...,
            cookies: Any | None = ...,
            files: Any | None = ...,
            auth: Any | None = ...,
            allow_redirects: bool = ...,
            proxies: dict | None = ...,
            hooks: Any | None = ...,
            stream: Any | None = ...,
            verify: Any | None = ...,
            cert: Any | None = ...) -> Union[bool, None]: ...

    def ele(self,
            loc_or_ele: Union[Tuple[str, str], str, ChromiumElement, SessionElement],
            timeout: float = None) -> Union[ChromiumElement, SessionElement, str]: ...

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None) -> List[Union[ChromiumElement, SessionElement, str]]: ...

    def s_ele(self, loc_or_ele: Union[Tuple[str, str], str] = None) \
            -> Union[SessionElement, str, None]: ...

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str]) -> List[Union[SessionElement, str]]: ...

    def change_mode(self, mode: str = None, go: bool = True, copy_cookies: bool = True) -> None: ...

    def cookies_to_session(self, copy_user_agent: bool = True) -> None: ...

    def cookies_to_browser(self) -> None: ...

    def get_cookies(self, as_dict: bool = False, all_domains: bool = False,
                    all_info: bool = False) -> Union[dict, list]: ...

    def get_tab(self, tab_id: Union[str, WebPageTab] = None) -> WebPageTab: ...

    def new_tab(self, url: str = None, switch_to: bool = False) -> WebPageTab: ...

    def close_driver(self) -> None: ...

    def close_session(self) -> None: ...

    # ----------------重写SessionPage的函数-----------------------
    def post(self,
             url: str,
             data: Union[dict, str, None] = None,
             show_errmsg: bool = False,
             retry: int | None = None,
             interval: float | None = None,
             timeout: float | None = ...,
             params: dict | None = ...,
             json: Union[dict, str, None] = ...,
             headers: dict | None = ...,
             cookies: Any | None = ...,
             files: Any | None = ...,
             auth: Any | None = ...,
             allow_redirects: bool = ...,
             proxies: dict | None = ...,
             hooks: Any | None = ...,
             stream: Any | None = ...,
             verify: Any | None = ...,
             cert: Any | None = ...) -> bool: ...

    @property
    def set(self) -> WebPageSetter: ...

    def _find_elements(self, loc_or_ele: Union[Tuple[str, str], str, ChromiumElement, SessionElement, ChromiumFrame],
                       timeout: float = None, single: bool = True, relative: bool = False, raise_err: bool = None) \
            -> Union[ChromiumElement, SessionElement, ChromiumFrame, str, None, List[Union[SessionElement, str]], List[
                Union[ChromiumElement, str, ChromiumFrame]]]: ...

    def _set_start_options(self, dr_opt: Union[ChromiumDriver, bool, None],
                           se_opt: Union[Session, SessionOptions, bool, None]) -> None: ...

    def quit(self) -> None: ...

    def _on_download_begin(self, **kwargs): ...
