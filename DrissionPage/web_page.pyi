# -*- coding:utf-8 -*-
from time import sleep
from typing import Union, Tuple, List

from DownloadKit import DownloadKit
from requests import Session, Response
from tldextract import extract

from .chromium_base import ChromiumBase, ChromiumFrame
from .base import BasePage
from .chromium_element import ChromiumElement  # , ChromiumBase
from .chromium_page import ChromiumPage
from .config import DriverOptions, SessionOptions, _cookies_to_tuple
from .session_element import SessionElement
from .session_page import SessionPage
from .tab import Tab


class WebPage(SessionPage, ChromiumPage, BasePage):
    """整合浏览器和request的页面类"""

    def __init__(self,
                 mode: str = ...,
                 timeout: float = ...,
                 tab_id: str = ...,
                 driver_or_options: Union[Tab, DriverOptions, bool] = ...,
                 session_or_options: Union[Session, SessionOptions, bool] = ...) -> None: ...

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str, ChromiumElement, SessionElement],
                 timeout: float = ...) -> Union[ChromiumElement, SessionElement, ChromiumFrame, None]: ...

    # -----------------共有属性和方法-------------------
    @property
    def url(self) -> Union[str, None]: ...

    @property
    def html(self) -> str: ...

    @property
    def json(self) -> dict: ...

    @property
    def response(self) -> Response: ...

    @property
    def mode(self) -> str: ...

    @property
    def cookies(self): ...

    @property
    def session(self) -> Session: ...

    @property
    def driver(self) -> Tab: ...

    @property
    def _wait_driver(self) -> Tab: ...

    @property
    def _driver(self) -> Tab: ...

    @_driver.setter
    def _driver(self, tab): ...

    @property
    def _session_url(self) -> str: ...

    def get(self,
            url: str,
            show_errmsg: bool = ...,
            retry: int = ...,
            interval: float = ...,
            timeout: float = ...,
            **kwargs) -> Union[bool, None]: ...

    def ele(self,
            loc_or_ele: Union[Tuple[str, str], str, ChromiumElement, SessionElement],
            timeout: float = ...) -> Union[ChromiumElement, SessionElement, ChromiumFrame, str, None]: ...

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = ...) -> List[Union[ChromiumElement, SessionElement, ChromiumFrame, str]]: ...

    def s_ele(self, loc_or_ele: Union[Tuple[str, str], str, ChromiumElement, SessionElement] = ...) \
            -> Union[SessionElement, str, None]: ...

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str] = ...) -> List[Union[SessionElement, str]]: ...

    def change_mode(self, mode: str = ..., go: bool = ..., copy_cookies: bool = ...) -> None: ...

    def cookies_to_session(self, copy_user_agent: bool = ...) -> None: ...

    def cookies_to_driver(self) -> None: ...

    def get_cookies(self, as_dict: bool = ..., all_domains: bool = ...) -> Union[dict, list]: ...

    def _get_driver_cookies(self, as_dict: bool = ...): ...

    def set_cookies(self, cookies, set_session: bool = ..., set_driver: bool = ...): ...

    def check_page(self, by_requests: bool = ...) -> Union[bool, None]: ...

    def close_driver(self) -> None: ...

    def close_session(self) -> None: ...

    # ----------------重写SessionPage的函数-----------------------
    def post(self,
             url: str,
             data: Union[dict, str] = ...,
             show_errmsg: bool = ...,
             retry: int = ...,
             interval: float = ...,
             **kwargs) -> bool: ...

    @property
    def download(self) -> DownloadKit: ...

    def _ele(self,
             loc_or_ele: Union[Tuple[str, str], str, ChromiumElement, SessionElement],
             timeout: float = ..., single: bool = ..., relative: bool = ...) \
            -> Union[ChromiumElement, SessionElement, ChromiumFrame, str, None, List[Union[SessionElement, str]], List[
                Union[ChromiumElement, str, ChromiumFrame]]]: ...

    def _set_driver_options(self, Tab_or_Options): ...

    def _set_session_options(self, Session_or_Options): ...

    def quit(self) -> None: ...
