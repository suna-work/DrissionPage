# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from pathlib import Path
from typing import Union, Tuple, List, Any

from .chromium_base import ChromiumBase, ChromiumPageScroll
from .chromium_element import ChromiumElement, Locations, ChromiumElementStates
from .setter import ChromiumFrameSetter
from .waiter import FrameWaiter


class ChromiumFrame(ChromiumBase):

    def __init__(self, page: ChromiumBase, ele: ChromiumElement):
        self.page: ChromiumBase = ...
        self.frame_id: str = ...
        self._frame_ele: ChromiumElement = ...
        self._backend_id: str = ...
        self.frame_page: ChromiumBase = ...
        self._doc_ele: ChromiumElement = ...
        self._is_diff_domain: bool = ...
        self.doc_ele: ChromiumElement = ...
        self._states: ChromiumElementStates = ...
        self._ids: ChromiumFrameIds = ...

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str],
                 timeout: float = None) -> Union[ChromiumElement, str]: ...

    def _check_alive(self) -> None: ...

    def __repr__(self) -> str: ...

    def _runtime_settings(self) -> None: ...

    def _driver_init(self, tab_id: str) -> None: ...

    def _reload(self) -> None: ...

    def _check_ok(self) -> None: ...

    def _get_new_document(self) -> None: ...

    def _onFrameAttached(self, **kwargs): ...

    def _onFrameDetached(self, **kwargs): ...

    @property
    def ids(self) -> ChromiumFrameIds: ...

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
    def frame_size(self) -> Tuple[int, int]: ...

    @property
    def size(self) -> Tuple[int, int]: ...

    @property
    def active_ele(self) -> ChromiumElement: ...

    @property
    def location(self) -> Tuple[int, int]: ...

    @property
    def locations(self) -> Locations: ...

    @property
    def xpath(self) -> str: ...

    @property
    def css_path(self) -> str: ...

    @property
    def ready_state(self) -> str: ...

    @property
    def is_alive(self) -> bool: ...

    @property
    def scroll(self) -> ChromiumFrameScroll: ...

    @property
    def set(self) -> ChromiumFrameSetter: ...

    @property
    def states(self) -> ChromiumElementStates: ...

    @property
    def wait(self) -> FrameWaiter: ...

    @property
    def tab_id(self) -> str: ...

    def refresh(self) -> None: ...

    def attr(self, attr: str) -> Union[str, None]: ...

    def remove_attr(self, attr: str) -> None: ...

    def run_js(self, script: str, *args: Any, as_expr: bool = False) -> Any: ...

    def parent(self, level_or_loc: Union[tuple, str, int] = 1, index: int = 1) -> Union[ChromiumElement, None]: ...

    def prev(self, filter_loc: Union[tuple, str, int] = '',
             index: int = 1,
             timeout: float = 0,
             ele_only: bool = True) -> Union[ChromiumElement, str]: ...

    def next(self, filter_loc: Union[tuple, str, int] = '',
             index: int = 1,
             timeout: float = 0,
             ele_only: bool = True) -> Union[ChromiumElement, str]: ...

    def before(self, filter_loc: Union[tuple, str, int] = '',
               index: int = 1,
               timeout: float = None,
               ele_only: bool = True) -> Union[ChromiumElement, str]: ...

    def after(self, filter_loc: Union[tuple, str, int] = '',
              index: int = 1,
              timeout: float = None,
              ele_only: bool = True) -> Union[ChromiumElement, str]: ...

    def prevs(self, filter_loc: Union[tuple, str] = '',
              timeout: float = 0,
              ele_only: bool = True) -> List[Union[ChromiumElement, str]]: ...

    def nexts(self, filter_loc: Union[tuple, str] = '',
              timeout: float = 0,
              ele_only: bool = True) -> List[Union[ChromiumElement, str]]: ...

    def befores(self, filter_loc: Union[tuple, str] = '',
                timeout: float = None,
                ele_only: bool = True) -> List[Union[ChromiumElement, str]]: ...

    def afters(self, filter_loc: Union[tuple, str] = '',
               timeout: float = None,
               ele_only: bool = True) -> List[Union[ChromiumElement, str]]: ...

    def get_screenshot(self, path: [str, Path] = None,
                       as_bytes: [bool, str] = None,
                       as_base64: [bool, str] = None) -> Union[str, bytes]: ...

    def _get_screenshot(self, path: [str, Path] = None,
                        as_bytes: [bool, str] = None, as_base64: [bool, str] = None,
                        full_page: bool = False,
                        left_top: Tuple[int, int] = None,
                        right_bottom: Tuple[int, int] = None,
                        ele: ChromiumElement = None) -> Union[str, bytes]: ...

    def _find_elements(self, loc_or_ele: Union[Tuple[str, str], str, ChromiumElement, ChromiumFrame],
                       timeout: float = None, single: bool = True, relative: bool = False, raise_err: bool = None) \
            -> Union[ChromiumElement, ChromiumFrame, None, List[Union[ChromiumElement, ChromiumFrame]]]: ...

    def _d_connect(self,
                   to_url: str,
                   times: int = 0,
                   interval: float = 1,
                   show_errmsg: bool = False,
                   timeout: float = None) -> Union[bool, None]: ...

    def _is_inner_frame(self) -> bool: ...


class ChromiumFrameIds(object):
    def __init__(self, frame: ChromiumFrame):
        self._frame: ChromiumFrame = ...

    @property
    def tab_id(self) -> str: ...

    @property
    def backend_id(self) -> str: ...

    @property
    def obj_id(self) -> str: ...

    @property
    def node_id(self) -> str: ...


class ChromiumFrameScroll(ChromiumPageScroll):
    def __init__(self, frame: ChromiumFrame) -> None: ...

    def to_see(self, loc_or_ele: Union[str, tuple, ChromiumElement], center: Union[None, bool] = None) -> None: ...
