# -*- coding:utf-8 -*-
from typing import Union, Tuple, List, Any

from DataRecorder import Recorder
from requests import Session
from requests.cookies import RequestsCookieJar

from .base import BasePage
from .chromium_element import ChromiumElement
from .chromium_element import ChromiumElementWaiter, ChromeScroll
from .config import DriverOptions
from .session_element import SessionElement
from .tab import Tab


class ChromiumBase(BasePage):
    """标签页、frame、页面基类"""

    def __init__(self,
                 address: str,
                 tab_id: str = ...,
                 timeout: float = ...):
        self._control_session: Session = ...
        self.address: str = ...
        self._tab_obj: Tab = ...
        self._is_reading: bool = ...
        self.timeouts: Timeout = ...
        self._first_run: bool = ...
        self._is_loading: bool = ...
        self._page_load_strategy: str = ...
        self._scroll: ChromeScroll = ...
        self._url: str = ...
        self._root_id: str = ...
        self._debug: bool = ...
        self._debug_recorder: Recorder = ...

    def _connect_browser(self,
                         addr_tab_opts: Union[str, Tab, DriverOptions] = ...,
                         tab_id: str = ...) -> None: ...

    def _init_page(self, tab_id: str = ...) -> None: ...

    def _get_document(self) -> None: ...

    def _wait_loading(self, timeout: float = ...) -> bool: ...

    def _onFrameStartedLoading(self, **kwargs): ...

    def _onFrameStoppedLoading(self, **kwargs): ...

    def _onLoadEventFired(self, **kwargs): ...

    def _onDocumentUpdated(self, **kwargs): ...

    def _onFrameNavigated(self, **kwargs): ...

    def _set_options(self) -> None: ...

    def __call__(self, loc_or_str: Union[Tuple[str, str], str, 'ChromiumElement'],
                 timeout: float = ...) -> Union['ChromiumElement', 'ChromiumFrame', None]: ...

    @property
    def title(self) -> str: ...

    @property
    def driver(self) -> Tab: ...

    @property
    def _driver(self) -> Tab: ...

    @property
    def _wait_driver(self) -> Tab: ...

    @property
    def is_loading(self) -> bool: ...

    @property
    def url(self) -> str: ...

    @property
    def html(self) -> str: ...

    @property
    def json(self) -> dict: ...

    @property
    def tab_id(self) -> str: ...

    @property
    def ready_state(self) -> str: ...

    @property
    def size(self) -> dict: ...

    @property
    def active_ele(self) -> ChromiumElement: ...

    @property
    def page_load_strategy(self) -> str: ...

    @property
    def scroll(self) -> 'ChromeScroll': ...

    @property
    def set_page_load_strategy(self) -> pageLoadStrategy: ...

    def set_timeouts(self, implicit: float = ..., page_load: float = ..., script: float = ...) -> None: ...

    def run_script(self, script: str, as_expr: bool = ..., *args: Any) -> Any: ...

    def run_async_script(self, script: str, as_expr: bool = ..., *args: Any) -> None: ...

    def get(self,
            url: str,
            show_errmsg: bool = ...,
            retry: int = ...,
            interval: float = ...,
            timeout: float = ...) -> Union[None, bool]: ...

    def _get(self,
             url: str,
             show_errmsg: bool = ...,
             retry: int = ...,
             interval: float = ...,
             timeout: float = ...,
             frame_id: str = ...) -> Union[None, bool]: ...

    def get_cookies(self, as_dict: bool = ...) -> Union[list, dict]: ...

    def set_cookies(self, cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> None: ...

    def ele(self,
            loc_or_ele: Union[Tuple[str, str], str, ChromiumElement, 'ChromiumFrame'],
            timeout: float = ...) -> Union[ChromiumElement, 'ChromiumFrame', None]: ...

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = ...) -> List[Union[ChromiumElement, 'ChromiumFrame']]: ...

    def s_ele(self, loc_or_ele: Union[Tuple[str, str], str, ChromiumElement] = ...) \
            -> Union[SessionElement, str, None]: ...

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str] = ...) -> List[Union[SessionElement, str]]: ...

    def _ele(self,
             loc_or_ele: Union[Tuple[str, str], str, ChromiumElement, 'ChromiumFrame'],
             timeout: float = ..., single: bool = ..., relative: bool = ...) \
            -> Union[ChromiumElement, 'ChromiumFrame', None, List[Union[ChromiumElement, 'ChromiumFrame']]]: ...

    def wait_ele(self,
                 loc_or_ele: Union[str, tuple, ChromiumElement],
                 timeout: float = ...) -> 'ChromiumElementWaiter': ...

    def scroll_to_see(self, loc_or_ele: Union[str, tuple, ChromiumElement]) -> None: ...

    def refresh(self, ignore_cache: bool = ...) -> None: ...

    def forward(self, steps: int = ...) -> None: ...

    def back(self, steps: int = ...) -> None: ...

    def _forward_or_back(self, steps: int) -> None: ...

    def stop_loading(self) -> None: ...

    def run_cdp(self, cmd: str, **cmd_args) -> dict: ...

    def set_user_agent(self, ua: str) -> None: ...

    def get_session_storage(self, item: str = None) -> Union[str, dict, None]: ...

    def get_local_storage(self, item: str = None) -> Union[str, dict, None]: ...

    def set_session_storage(self, item: str, value: Union[str, bool]) -> None: ...

    def set_local_storage(self, item: str, value: Union[str, bool]) -> None: ...

    def clear_cache(self,
                    session_storage: bool = True,
                    local_storage: bool = True,
                    cache: bool = True,
                    cookies: bool = True) -> None: ...

    def _d_connect(self,
                   to_url: str,
                   times: int = ...,
                   interval: float = ...,
                   show_errmsg: bool = ...,
                   timeout: float = ...,
                   frame_id: str = ...) -> Union[bool, None]: ...


class ChromiumFrame(ChromiumBase):
    """实现浏览器frame的类"""

    def __init__(self, page: ChromiumBase,
                 ele: ChromiumElement):
        self._inner_ele: ChromiumElement = ...
        self.page: ChromiumBase = ...

    def __repr__(self) -> str: ...

    @property
    def tag(self) -> str: ...

    @property
    def html(self) -> str: ...

    @property
    def inner_html(self) -> str: ...

    @property
    def attrs(self) -> dict: ...

    @property
    def frame_size(self) -> dict: ...

    def _set_options(self) -> None: ...

    @property
    def obj_id(self) -> str: ...

    @property
    def node_id(self) -> str: ...

    @property
    def location(self) -> dict: ...

    @property
    def is_displayed(self) -> bool: ...

    def attr(self, attr: str) -> Union[str, None]: ...

    def set_attr(self, attr: str, value: str) -> None: ...

    def remove_attr(self, attr: str) -> None: ...

    def parent(self, level_or_loc: Union[tuple, str, int] = ...) -> Union['ChromiumElement', None]: ...

    def prev(self,
             filter_loc: Union[tuple, str] = ...,
             index: int = ...,
             timeout: float = ...) -> Union['ChromiumElement', str, None]: ...

    def next(self,
             filter_loc: Union[tuple, str] = ...,
             index: int = ...,
             timeout: float = ...) -> Union['ChromiumElement', str, None]: ...

    def before(self,
               filter_loc: Union[tuple, str] = ...,
               index: int = ...,
               timeout: float = ...) -> Union['ChromiumElement', str, None]: ...

    def after(self,
              filter_loc: Union[tuple, str] = ...,
              index: int = ...,
              timeout: float = ...) -> Union['ChromiumElement', str, None]: ...

    def prevs(self,
              filter_loc: Union[tuple, str] = ...,
              timeout: float = ...) -> List[Union['ChromiumElement', str]]: ...

    def nexts(self,
              filter_loc: Union[tuple, str] = ...,
              timeout: float = ...) -> List[Union['ChromiumElement', str]]: ...

    def befores(self,
                filter_loc: Union[tuple, str] = ...,
                timeout: float = ...) -> List[Union['ChromiumElement', str]]: ...


class Timeout(object):
    """用于保存d模式timeout信息的类"""

    def __init__(self, page: ChromiumBase):
        self.page: ChromiumBase = ...
        self.page_load: float = ...
        self.script: float = ...

    @property
    def implicit(self) -> float: ...


class PageLoadStrategy(object):
    def __init__(self, page: ChromiumBase):
        self.page: ChromiumBase = ...

    def __call__(self, value: str) -> None: ...

    def normal(self) -> None: ...

    def eager(self) -> None: ...

    def none(self) -> None: ...
