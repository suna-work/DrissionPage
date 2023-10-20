# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from typing import Union

from .browser_download_manager import DownloadMission
from .._elements.chromium_element import ChromiumElement
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_frame import ChromiumFrame
from .._pages.chromium_page import ChromiumPage


class ChromiumBaseWaiter(object):
    def __init__(self, page: ChromiumBase):
        self._driver: ChromiumBase = ...

    def __call__(self, second: float) -> None: ...

    def ele_delete(self, loc_or_ele: Union[str, tuple, ChromiumElement], timeout: float = None,
                   raise_err: bool = None) -> bool: ...

    def ele_display(self, loc_or_ele: Union[str, tuple, ChromiumElement], timeout: float = None,
                    raise_err: bool = None) -> bool: ...

    def ele_hidden(self, loc_or_ele: Union[str, tuple, ChromiumElement], timeout: float = None,
                   raise_err: bool = None) -> bool: ...

    def ele_load(self, loc: Union[str, tuple], timeout: float = None,
                 raise_err: bool = None) -> Union[bool, ChromiumElement]: ...

    def _loading(self, timeout: float = None, start: bool = True, gap: float = .01, raise_err: bool = None) -> bool: ...

    def load_start(self, timeout: float = None, raise_err: bool = None) -> bool: ...

    def load_complete(self, timeout: float = None, raise_err: bool = None) -> bool: ...

    def upload_paths_inputted(self) -> None: ...

    def download_begin(self, timeout: float = None, cancel_it: bool = False) -> Union[DownloadMission, bool]: ...

    def downloads_done(self, timeout: float = None, cancel_if_timeout: bool = True) -> bool: ...

    def url_change(self, text: str, exclude: bool = False, timeout: float = None, raise_err: bool = None) -> bool: ...

    def title_change(self, text: str, exclude: bool = False, timeout: float = None, raise_err: bool = None) -> bool: ...

    def _change(self, arg: str, text: str, exclude: bool = False, timeout: float = None,
                raise_err: bool = None) -> bool: ...


class ChromiumTabWaiter(ChromiumBaseWaiter):

    def downloads_done(self, timeout: float = None, cancel_if_timeout: bool = True) -> bool: ...


class ChromiumPageWaiter(ChromiumTabWaiter):
    _driver: ChromiumPage = ...

    def new_tab(self, timeout: float = None, raise_err: bool = None) -> bool: ...

    def all_downloads_done(self, timeout: float = None, cancel_if_timeout: bool = True) -> bool: ...


class ChromiumElementWaiter(object):
    def __init__(self,
                 page: ChromiumBase,
                 ele: ChromiumElement):
        self._ele: ChromiumElement = ...
        self._page: ChromiumBase = ...

    def __call__(self, second: float) -> None: ...

    def delete(self, timeout: float = None, raise_err: bool = None) -> bool: ...

    def display(self, timeout: float = None, raise_err: bool = None) -> bool: ...

    def hidden(self, timeout: float = None, raise_err: bool = None) -> bool: ...

    def covered(self, timeout: float = None, raise_err: bool = None) -> bool: ...

    def not_covered(self, timeout: float = None, raise_err: bool = None) -> bool: ...

    def enabled(self, timeout: float = None, raise_err: bool = None) -> bool: ...

    def disabled(self, timeout: float = None, raise_err: bool = None) -> bool: ...

    def disabled_or_delete(self, timeout: float = None, raise_err: bool = None) -> bool: ...

    def _wait_state(self, attr: str, mode: bool = False, timeout: float = None, raise_err: bool = None) -> bool: ...


class FrameWaiter(ChromiumBaseWaiter, ChromiumElementWaiter):
    def __init__(self, frame: ChromiumFrame): ...
