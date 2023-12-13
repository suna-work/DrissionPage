# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from pathlib import Path
from typing import Union, Tuple, List, Any, Optional, Literal

from .._base.base import BasePage
from .._base.browser import Browser
from .._base.chromium_driver import ChromiumDriver
from .._elements.chromium_element import ChromiumElement
from .._elements.none_element import NoneElement
from .._elements.session_element import SessionElement
from .._pages.chromium_frame import ChromiumFrame
from .._pages.chromium_page import ChromiumPage
from .._units.actions import Actions
from .._units.listener import Listener
from .._units.rect import TabRect
from .._units.screencast import Screencast
from .._units.scroller import Scroller, PageScroller
from .._units.setter import ChromiumBaseSetter
from .._units.states import PageStates
from .._units.waiter import BaseWaiter

PIC_TYPE = Literal['jpg', 'jpeg', 'png', 'webp', True]


class ChromiumBase(BasePage):
    def __init__(self,
                 address: Union[str, int],
                 tab_id: str = None,
                 timeout: float = None):
        self._browser: Browser = ...
        self._page: ChromiumPage = ...
        self.address: str = ...
        self._driver: ChromiumDriver = ...
        self._frame_id: str = ...
        self._is_reading: bool = ...
        self._is_timeout: bool = ...
        self._timeouts: Timeout = ...
        self._first_run: bool = ...
        self._is_loading: bool = ...
        self._load_mode: str = ...
        self._scroll: Scroller = ...
        self._url: str = ...
        self._root_id: str = ...
        self._debug: bool = ...
        self._upload_list: list = ...
        self._wait: BaseWaiter = ...
        self._set: ChromiumBaseSetter = ...
        self._screencast: Screencast = ...
        self._actions: Actions = ...
        self._listener: Listener = ...
        self._states: PageStates = ...
        self._alert: Alert = ...
        self._has_alert: bool = ...
        self._doc_got: bool = ...
        self._load_end_time: float = ...
        self._ready_state: Optional[str] = ...
        self._rect: TabRect = ...

    def _connect_browser(self, tab_id: str = None) -> None: ...

    def _driver_init(self, tab_id: str) -> None: ...

    def _get_document(self, timeout: float = 10) -> bool: ...

    def _wait_loaded(self, timeout: float = None) -> bool: ...

    def _onFrameDetached(self, **kwargs) -> None: ...

    def _onFrameAttached(self, **kwargs) -> None: ...

    def _onFrameStartedLoading(self, **kwargs): ...

    def _onFrameNavigated(self, **kwargs): ...

    def _onDomContentEventFired(self, **kwargs): ...

    def _onLoadEventFired(self, **kwargs): ...

    def _onFrameStoppedLoading(self, **kwargs): ...

    def _onFileChooserOpened(self, **kwargs): ...

    def _wait_to_stop(self): ...

    def _d_set_start_options(self, address) -> None: ...

    def _d_set_runtime_settings(self) -> None: ...

    def __call__(self, loc_or_str: Union[Tuple[str, str], str, ChromiumElement],
                 timeout: float = None) -> ChromiumElement: ...

    @property
    def _js_ready_state(self) -> str: ...

    @property
    def browser(self) -> Browser: ...

    @property
    def title(self) -> str: ...

    @property
    def driver(self) -> ChromiumDriver: ...

    @property
    def url(self) -> str: ...

    @property
    def _browser_url(self) -> str: ...

    @property
    def html(self) -> str: ...

    @property
    def json(self) -> Union[dict, None]: ...

    @property
    def _target_id(self) -> str: ...

    @property
    def tab_id(self) -> str: ...

    @property
    def active_ele(self) -> ChromiumElement: ...

    @property
    def load_mode(self) -> str: ...

    @property
    def user_agent(self) -> str: ...

    @property
    def scroll(self) -> PageScroller: ...

    @property
    def rect(self) -> TabRect: ...

    @property
    def timeouts(self) -> Timeout: ...

    @property
    def upload_list(self) -> list: ...

    @property
    def wait(self) -> BaseWaiter: ...

    @property
    def set(self) -> ChromiumBaseSetter: ...

    @property
    def screencast(self) -> Screencast: ...

    @property
    def actions(self) -> Actions: ...

    @property
    def listen(self) -> Listener: ...

    @property
    def states(self) -> PageStates: ...

    def run_js(self, script: str, *args, as_expr: bool = False, timeout: float = None) -> Any: ...

    def run_js_loaded(self, script: str, *args, as_expr: bool = False, timeout: float = None) -> Any: ...

    def run_async_js(self, script: str, *args, as_expr: bool = False, timeout: float = None) -> None: ...

    def get(self, url: str, show_errmsg: bool = False, retry: int = None,
            interval: float = None, timeout: float = None) -> Union[None, bool]: ...

    def get_cookies(self, as_dict: bool = False, all_domains: bool = False,
                    all_info: bool = False) -> Union[list, dict]: ...

    def ele(self, loc_or_ele: Union[Tuple[str, str], str, ChromiumElement, ChromiumFrame],
            timeout: float = None) -> Union[ChromiumElement, str]: ...

    def eles(self, loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None) -> List[Union[ChromiumElement, str]]: ...

    def s_ele(self, loc_or_ele: Union[Tuple[str, str], str] = None) \
            -> Union[SessionElement, str, NoneElement]: ...

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str]) -> List[Union[SessionElement, str]]: ...

    def _find_elements(self, loc_or_ele: Union[Tuple[str, str], str, ChromiumElement, ChromiumFrame],
                       timeout: float = None, single: bool = True, relative: bool = False, raise_err: bool = None) \
            -> Union[ChromiumElement, ChromiumFrame, NoneElement, List[Union[ChromiumElement, ChromiumFrame]]]: ...

    def refresh(self, ignore_cache: bool = False) -> None: ...

    def forward(self, steps: int = 1) -> None: ...

    def back(self, steps: int = 1) -> None: ...

    def _forward_or_back(self, steps: int) -> None: ...

    def stop_loading(self) -> None: ...

    def remove_ele(self, loc_or_ele: Union[ChromiumElement, ChromiumFrame, str, Tuple[str, str]]) -> None: ...

    def get_frame(self, loc_ind_ele: Union[str, int, tuple, ChromiumFrame], timeout: float = None) -> ChromiumFrame: ...

    def get_frames(self, loc: Union[str, tuple] = None, timeout: float = None) -> List[ChromiumFrame]: ...

    def run_cdp(self, cmd: str, **cmd_args) -> dict: ...

    def run_cdp_loaded(self, cmd: str, **cmd_args) -> dict: ...

    def get_session_storage(self, item: str = None) -> Union[str, dict, None]: ...

    def get_local_storage(self, item: str = None) -> Union[str, dict, None]: ...

    def get_screenshot(self, path: [str, Path] = None, name: str = None, as_bytes: PIC_TYPE = None,
                       as_base64: PIC_TYPE = None, full_page: bool = False, left_top: Tuple[int, int] = None,
                       right_bottom: Tuple[int, int] = None) -> Union[str, bytes]: ...

    def _get_screenshot(self, path: [str, Path] = None, name: str = None, as_bytes: PIC_TYPE = None,
                        as_base64: PIC_TYPE = None, full_page: bool = False, left_top: Tuple[float, float] = None,
                        right_bottom: Tuple[float, float] = None, ele: ChromiumElement = None) -> Union[str, bytes]: ...

    def clear_cache(self, session_storage: bool = True, local_storage: bool = True, cache: bool = True,
                    cookies: bool = True) -> None: ...

    def handle_alert(self, accept: bool = True, send: str = None, timeout: float = None,
                     next_one: bool = False) -> Union[str, False]: ...

    def _on_alert_close(self, **kwargs): ...

    def _on_alert_open(self, **kwargs): ...

    def _before_connect(self, url: str, retry: int, interval: float) -> tuple: ...

    def _d_connect(self, to_url: str, times: int = 0, interval: float = 1, show_errmsg: bool = False,
                   timeout: float = None) -> Union[bool, None]: ...


class Timeout(object):

    def __init__(self, page: ChromiumBase, base=None, page_load=None, script=None):
        self._page: ChromiumBase = ...
        self.base: float = ...
        self.page_load: float = ...
        self.script: float = ...


class Alert(object):

    def __init__(self):
        self.activated: bool = ...
        self.text: str = ...
        self.type: str = ...
        self.defaultPrompt: str = ...
        self.response_accept: str = ...
        self.response_text: str = ...
        self.handle_next: Optional[bool] = ...
        self.next_text: str = ...
        self.auto: Optional[bool] = ...
