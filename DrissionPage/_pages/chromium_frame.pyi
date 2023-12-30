# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from pathlib import Path
from typing import Union, Tuple, List, Any

from .chromium_base import ChromiumBase
from .chromium_page import ChromiumPage
from .chromium_tab import ChromiumTab
from .web_page import WebPage
from .._elements.chromium_element import ChromiumElement
from .._elements.none_element import NoneElement
from .._units.listener import FrameListener
from .._units.rect import FrameRect
from .._units.scroller import FrameScroller
from .._units.setter import ChromiumFrameSetter
from .._units.states import FrameStates
from .._units.waiter import FrameWaiter


class ChromiumFrame(ChromiumBase):

    def __init__(self,
                 page: Union[ChromiumPage, WebPage, ChromiumTab, ChromiumFrame],
                 ele: ChromiumElement,
                 info: dict = None):
        self._page: ChromiumPage = ...
        self._target_page: ChromiumBase = ...
        self.tab: ChromiumTab = ...
        self._tab_id: str = ...
        self._frame_ele: ChromiumElement = ...
        self._backend_id: int = ...
        self._doc_ele: ChromiumElement = ...
        self._is_diff_domain: bool = ...
        self.doc_ele: ChromiumElement = ...
        self._states: FrameStates = ...
        self._reloading: bool = ...
        self._rect: FrameRect = ...
        self._listener: FrameListener = ...

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str],
                 timeout: float = None) -> Union[ChromiumElement, NoneElement]: ...

    def __eq__(self, other: ChromiumFrame) -> bool: ...

    def _check_alive(self) -> None: ...

    def __repr__(self) -> str: ...

    def _d_set_runtime_settings(self) -> None: ...

    def _driver_init(self, tab_id: str) -> None: ...

    def _reload(self) -> None: ...

    def _get_document(self, timeout: float = 10) -> bool: ...

    def _onFrameStoppedLoading(self, **kwargs): ...

    def _onInspectorDetached(self, **kwargs): ...

    @property
    def page(self) -> Union[ChromiumPage, WebPage]: ...

    @property
    def frame_ele(self) -> ChromiumElement: ...

    @property
    def tag(self) -> str: ...

    @property
    def url(self) -> str: ...

    @property
    def html(self) -> str: ...

    @property
    def inner_html(self) -> str: ...

    @property
    def title(self) -> str: ...

    @property
    def cookies(self) -> dict: ...

    @property
    def attrs(self) -> dict: ...

    @property
    def rect(self) -> FrameRect: ...

    @property
    def listen(self) -> FrameListener: ...

    @property
    def _obj_id(self) -> str: ...

    @property
    def _node_id(self) -> int: ...

    @property
    def active_ele(self) -> ChromiumElement: ...

    @property
    def xpath(self) -> str: ...

    @property
    def css_path(self) -> str: ...

    @property
    def scroll(self) -> FrameScroller: ...

    @property
    def set(self) -> ChromiumFrameSetter: ...

    @property
    def states(self) -> FrameStates: ...

    @property
    def wait(self) -> FrameWaiter: ...

    @property
    def tab_id(self) -> str: ...

    @property
    def download_path(self) -> str: ...

    def refresh(self) -> None: ...

    def attr(self, attr: str) -> Union[str, None]: ...

    def remove_attr(self, attr: str) -> None: ...

    def run_js(self,
               script: str,
               *args,
               as_expr: bool = False,
               timeout: float = None) -> Any: ...

    def parent(self,
               level_or_loc: Union[tuple, str, int] = 1,
               index: int = 1) -> Union[ChromiumElement, NoneElement]: ...

    def prev(self,
             filter_loc: Union[tuple, str, int] = '',
             index: int = 1,
             timeout: float = 0,
             ele_only: bool = True) -> Union[ChromiumElement, NoneElement, str]: ...

    def next(self,
             filter_loc: Union[tuple, str, int] = '',
             index: int = 1,
             timeout: float = 0,
             ele_only: bool = True) -> Union[ChromiumElement, NoneElement, str]: ...

    def before(self,
               filter_loc: Union[tuple, str, int] = '',
               index: int = 1,
               timeout: float = None,
               ele_only: bool = True) -> Union[ChromiumElement, NoneElement, str]: ...

    def after(self,
              filter_loc: Union[tuple, str, int] = '',
              index: int = 1,
              timeout: float = None,
              ele_only: bool = True) -> Union[ChromiumElement, NoneElement, str]: ...

    def prevs(self,
              filter_loc: Union[tuple, str] = '',
              timeout: float = 0,
              ele_only: bool = True) -> List[Union[ChromiumElement, str]]: ...

    def nexts(self,
              filter_loc: Union[tuple, str] = '',
              timeout: float = 0,
              ele_only: bool = True) -> List[Union[ChromiumElement, str]]: ...

    def befores(self,
                filter_loc: Union[tuple, str] = '',
                timeout: float = None,
                ele_only: bool = True) -> List[Union[ChromiumElement, str]]: ...

    def afters(self,
               filter_loc: Union[tuple, str] = '',
               timeout: float = None,
               ele_only: bool = True) -> List[Union[ChromiumElement, str]]: ...

    def get_screenshot(self,
                       path: [str, Path] = None,
                       name: str = None,
                       as_bytes: [bool, str] = None,
                       as_base64: [bool, str] = None) -> Union[str, bytes]: ...

    def _get_screenshot(self,
                        path: [str, Path] = None,
                        name: str = None,
                        as_bytes: [bool, str] = None,
                        as_base64: [bool, str] = None,
                        full_page: bool = False,
                        left_top: Tuple[int, int] = None,
                        right_bottom: Tuple[int, int] = None,
                        ele: ChromiumElement = None) -> Union[str, bytes]: ...

    def _find_elements(self,
                       loc_or_ele: Union[Tuple[str, str], str, ChromiumElement, ChromiumFrame],
                       timeout: float = None,
                       single: bool = True,
                       relative: bool = False,
                       raise_err: bool = None) \
            -> Union[ChromiumElement, ChromiumFrame, None, List[Union[ChromiumElement, ChromiumFrame]]]: ...

    def _is_inner_frame(self) -> bool: ...
