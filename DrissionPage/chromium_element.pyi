# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from pathlib import Path
from typing import Union, Tuple, List, Any

from .common.constants import NoneElement
from .base import DrissionElement, BaseElement
from .chromium_base import ChromiumBase
from .chromium_frame import ChromiumFrame
from .chromium_page import ChromiumPage
from .session_element import SessionElement
from .web_page import WebPage


class ChromiumElement(DrissionElement):

    def __init__(self,
                 page: ChromiumBase,
                 node_id: str = None, obj_id: str = None, backend_id: str = None):
        self._tag: str = ...
        self.page: Union[ChromiumPage, WebPage] = ...
        self._node_id: str = ...
        self._obj_id: str = ...
        self._backend_id: str = ...
        self._doc_id: str = ...
        self._scroll: ChromiumScroll = ...
        self._click: Click = ...
        self._select: ChromiumSelect = ...
        self._wait: ChromiumWaiter = ...
        self._locations: Locations = ...
        self._set: ChromiumElementSetter = ...
        self._states: ChromiumElementStates = ...
        self._pseudo: Pseudo = ...

    def __repr__(self) -> str: ...

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str],
                 timeout: float = None) -> Union[ChromiumElement, ChromiumFrame, str, None]: ...

    @property
    def tag(self) -> str: ...

    @property
    def html(self) -> str: ...

    @property
    def inner_html(self) -> str: ...

    @property
    def attrs(self) -> dict: ...

    @property
    def text(self) -> str: ...

    @property
    def raw_text(self) -> str: ...

    # -----------------d模式独有属性-------------------
    @property
    def obj_id(self) -> str: ...

    @property
    def node_id(self) -> str: ...

    @property
    def backend_id(self) -> str: ...

    @property
    def doc_id(self) -> str: ...

    @property
    def size(self) -> Tuple[int, int]: ...

    @property
    def set(self) -> ChromiumElementSetter: ...

    @property
    def states(self) -> ChromiumElementStates: ...

    @property
    def location(self) -> Tuple[int, int]: ...

    @property
    def locations(self) -> Locations: ...

    @property
    def pseudo(self) -> Pseudo: ...

    @property
    def client_location(self) -> Tuple[int, int]: ...

    @property
    def client_midpoint(self) -> Tuple[int, int]: ...

    @property
    def midpoint(self) -> Tuple[int, int]: ...

    @property
    def _client_click_point(self) -> Tuple[int, int]: ...

    @property
    def _click_point(self) -> Tuple[int, int]: ...

    @property
    def shadow_root(self) -> Union[None, ChromiumShadowRootElement]: ...

    @property
    def sr(self) -> Union[None, ChromiumShadowRootElement]: ...

    @property
    def pseudo_before(self) -> str: ...

    @property
    def pseudo_after(self) -> str: ...

    @property
    def scroll(self) -> ChromiumScroll: ...

    @property
    def click(self) -> Click: ...

    def parent(self, level_or_loc: Union[tuple, str, int] = 1) -> Union[ChromiumElement, None]: ...

    def prev(self,
             filter_loc: Union[tuple, str] = '',
             index: int = 1,
             timeout: float = 0) -> Union[ChromiumElement, str, None]: ...

    def next(self,
             filter_loc: Union[tuple, str] = '',
             index: int = 1,
             timeout: float = 0) -> Union[ChromiumElement, str, None]: ...

    def before(self,
               filter_loc: Union[tuple, str] = '',
               index: int = 1,
               timeout: float = None) -> Union[ChromiumElement, str, None]: ...

    def after(self,
              filter_loc: Union[tuple, str] = '',
              index: int = 1,
              timeout: float = None) -> Union[ChromiumElement, str, None]: ...

    def prevs(self,
              filter_loc: Union[tuple, str] = '',
              timeout: float = 0) -> List[Union[ChromiumElement, str]]: ...

    def nexts(self,
              filter_loc: Union[tuple, str] = '',
              timeout: float = 0) -> List[Union[ChromiumElement, str]]: ...

    def befores(self,
                filter_loc: Union[tuple, str] = '',
                timeout: float = None) -> List[Union[ChromiumElement, str]]: ...

    def afters(self,
               filter_loc: Union[tuple, str] = '',
               timeout: float = None) -> List[Union[ChromiumElement, str]]: ...

    def wait_ele(self,
                 loc_or_ele: Union[str, tuple, ChromiumElement],
                 timeout: float = None) -> ChromiumWaiter: ...

    @property
    def wait(self) -> ChromiumWaiter: ...

    @property
    def select(self) -> ChromiumSelect: ...

    @property
    def is_selected(self) -> bool: ...

    @property
    def is_displayed(self) -> bool: ...

    @property
    def is_enabled(self) -> bool: ...

    @property
    def is_alive(self) -> bool: ...

    @property
    def is_in_viewport(self) -> bool: ...

    def attr(self, attr: str) -> Union[str, None]: ...

    def remove_attr(self, attr: str) -> None: ...

    def prop(self, prop: str) -> Union[str, int, None]: ...

    def set_attr(self, attr: str, value: str) -> None: ...

    def set_prop(self, prop: str, value: str) -> None: ...

    def set_innerHTML(self, html: str) -> None: ...

    def run_js(self, script: str, as_expr: bool = False, *args: Any) -> Any: ...

    def run_async_js(self, script: str, as_expr: bool = False, *args: Any) -> None: ...

    def ele(self,
            loc_or_str: Union[Tuple[str, str], str],
            timeout: float = None) -> Union[ChromiumElement, ChromiumFrame, str, NoneElement]: ...

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None) -> List[Union[ChromiumElement, ChromiumFrame, str]]: ...

    def s_ele(self, loc_or_str: Union[Tuple[str, str], str] = None) -> Union[SessionElement, str, NoneElement]: ...

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str] = None) -> List[Union[SessionElement, str]]: ...

    def _ele(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None, single: bool = True, relative: bool = False) \
            -> Union[ChromiumElement, ChromiumFrame, str, NoneElement,
                     List[Union[ChromiumElement, ChromiumFrame, str]]]: ...

    def style(self, style: str, pseudo_ele: str = '') -> str: ...

    def get_src(self) -> Union[bytes, str, None]: ...

    def save(self, path: [str, bool] = None, rename: str = None) -> None: ...

    def get_screenshot(self, path: [str, Path] = None, as_bytes: [bool, str] = None) -> Union[str, bytes]: ...

    def input(self, vals: Any, clear: bool = True) -> None: ...

    def _set_file_input(self, files: Union[str, list, tuple]) -> None: ...

    def clear(self, by_js: bool = False) -> None: ...

    def click_at(self, offset_x: int = None, offset_y: int = None, button: str = 'left') -> None: ...

    def r_click(self) -> None: ...

    def r_click_at(self, offset_x: int = None, offset_y: int = None) -> None: ...

    def m_click(self) -> None: ...

    def hover(self, offset_x: int = None, offset_y: int = None) -> None: ...

    def drag(self, offset_x: int = 0, offset_y: int = 0, speed: int = 40, shake: bool = True) -> None: ...

    def drag_to(self,
                ele_or_loc: Union[tuple, ChromiumElement],
                speed: int = 40,
                shake: bool = True) -> None: ...

    def _get_obj_id(self, node_id: str = None, backend_id: str = None) -> str: ...

    def _get_node_id(self, obj_id: str = None, backend_id: str = None) -> str: ...

    def _get_backend_id(self, node_id: str) -> str: ...

    def _get_ele_path(self, mode: str) -> str: ...


class ChromiumElementStates(object):
    def __init__(self, ele: ChromiumElement):
        self._ele: ChromiumElement = ...

    @property
    def is_selected(self) -> bool: ...

    @property
    def is_displayed(self) -> bool: ...

    @property
    def is_enabled(self) -> bool: ...

    @property
    def is_alive(self) -> bool: ...

    @property
    def is_in_viewport(self) -> bool: ...


class ChromiumShadowRootElement(BaseElement):

    def __init__(self,
                 parent_ele: ChromiumElement,
                 obj_id: str = None,
                 backend_id: str = None):
        self._obj_id: str = ...
        self._node_id: str = ...
        self._backend_id: str = ...
        self.page: ChromiumPage = ...
        self.parent_ele: ChromiumElement = ...

    def __repr__(self) -> str: ...

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str],
                 timeout: float = None) -> Union[ChromiumElement, ChromiumFrame, None]: ...

    @property
    def is_enabled(self) -> bool: ...

    @property
    def is_alive(self) -> bool: ...

    @property
    def node_id(self) -> str: ...

    @property
    def obj_id(self) -> str: ...

    @property
    def backend_id(self) -> str: ...

    @property
    def tag(self) -> str: ...

    @property
    def html(self) -> str: ...

    @property
    def inner_html(self) -> str: ...

    def run_js(self, script: str, as_expr: bool = False, *args: Any) -> Any: ...

    def run_async_js(self, script: str, as_expr: bool = False, *args: Any) -> None: ...

    def parent(self, level_or_loc: Union[str, int] = 1) -> ChromiumElement: ...

    def next(self,
             filter_loc: Union[tuple, str] = '',
             index: int = 1) -> Union[ChromiumElement, str, None]: ...

    def before(self,
               filter_loc: Union[tuple, str] = '',
               index: int = 1) -> Union[ChromiumElement, str, None]: ...

    def after(self,
              filter_loc: Union[tuple, str] = '',
              index: int = 1) -> Union[ChromiumElement, str, None]: ...

    def nexts(self, filter_loc: Union[tuple, str] = '') -> List[Union[ChromiumElement, str]]: ...

    def befores(self, filter_loc: Union[tuple, str] = '') -> List[Union[ChromiumElement, str]]: ...

    def afters(self, filter_loc: Union[tuple, str] = '') -> List[Union[ChromiumElement, str]]: ...

    def ele(self,
            loc_or_str: Union[Tuple[str, str], str],
            timeout: float = None) -> Union[ChromiumElement, ChromiumFrame, NoneElement]: ...

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None) -> List[Union[ChromiumElement, ChromiumFrame]]: ...

    def s_ele(self, loc_or_str: Union[Tuple[str, str], str] = None) -> Union[SessionElement, str, NoneElement]: ...

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str]) -> List[Union[SessionElement, str]]: ...

    def _ele(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None,
             single: bool = True, relative: bool = False) \
            -> Union[
                ChromiumElement, ChromiumFrame, NoneElement, str, List[Union[ChromiumElement, ChromiumFrame, str]]]: ...

    def _get_node_id(self, obj_id: str) -> str: ...

    def _get_obj_id(self, back_id: str) -> str: ...

    def _get_backend_id(self, node_id: str) -> str: ...


def find_in_chromium_ele(ele: ChromiumElement,
                         loc: Union[str, Tuple[str, str]],
                         single: bool = True,
                         timeout: float = None,
                         relative: bool = True) \
        -> Union[ChromiumElement, str, NoneElement, List[Union[ChromiumElement, str]]]: ...


def find_by_xpath(ele: ChromiumElement,
                  xpath: str,
                  single: bool,
                  timeout: float,
                  relative: bool = True) -> Union[ChromiumElement, List[ChromiumElement], NoneElement]: ...


def find_by_css(ele: ChromiumElement,
                selector: str,
                single: bool,
                timeout: float) -> Union[ChromiumElement, List[ChromiumElement], NoneElement]: ...


def make_chromium_ele(page: ChromiumBase, node_id: str = ..., obj_id: str = ...) -> Union[
    ChromiumElement, ChromiumFrame]: ...


def make_js_for_find_ele_by_xpath(xpath: str, type_txt: str, node_txt: str) -> str: ...


def run_js(page_or_ele: Union[ChromiumBase, ChromiumElement, ChromiumShadowRootElement], script: str,
           as_expr: bool = False, timeout: float = None, args: tuple = ...) -> Any: ...


def parse_js_result(page: ChromiumBase, ele: ChromiumElement, result: dict): ...


def convert_argument(arg: Any) -> dict: ...


def send_enter(ele: ChromiumElement) -> None: ...


def send_key(ele: ChromiumElement, modifier: int, key: str) -> None: ...


class ChromiumElementSetter(object):
    def __init__(self, ele: ChromiumElement):
        self._ele: ChromiumElement = ...

    def attr(self, attr: str, value: str) -> None: ...

    def prop(self, prop: str, value: str) -> None: ...

    def innerHTML(self, html: str) -> None: ...


class Locations(object):
    def __init__(self, ele: ChromiumElement):
        self._ele: ChromiumElement = ...

    @property
    def page_location(self) -> Tuple[int, int]: ...

    @property
    def viewport_location(self) -> Tuple[int, int]: ...

    @property
    def viewport_midpoint(self) -> Tuple[int, int]: ...

    @property
    def midpoint(self) -> Tuple[int, int]: ...

    @property
    def viewport_click_point(self) -> Tuple[int, int]: ...

    @property
    def click_point(self) -> Tuple[int, int]: ...

    @property
    def screen_location(self) -> Tuple[int, int]: ...

    def _get_viewport_rect(self, quad: str) -> Union[list, None]: ...

    def _get_page_coord(self, x: int, y: int) -> Tuple[int, int]: ...


class Click(object):
    def __init__(self, ele: ChromiumElement):
        self._ele: ChromiumElement = ...

    def __call__(self, by_js: bool = None, retry: bool = False, timeout: float = 0.2,
                 wait_loading: Union[bool, float] = 0) -> bool: ...

    def left(self, by_js: bool = None, retry: bool = False, timeout: float = 0.2,
             wait_loading: Union[bool, float] = 0) -> bool: ...

    def left_at(self, offset_x: int = None, offset_y: int = None, button: str = 'left') -> None: ...

    def right(self): ...

    def right_at(self, offset_x: int = None, offset_y: int = None) -> None: ...

    def middle(self): ...

    def _click(self, client_x: int, client_y: int, button: str = 'left') -> None: ...


class ChromiumScroll(object):

    def __init__(self, page_or_ele: Union[ChromiumBase, ChromiumElement, ChromiumFrame]):
        self.t1: str = ...
        self.t2: str = ...
        self._driver: Union[ChromiumPage, ChromiumElement, ChromiumFrame] = ...

    def _run_js(self, js: str): ...

    def to_top(self) -> None: ...

    def to_bottom(self) -> None: ...

    def to_half(self) -> None: ...

    def to_rightmost(self) -> None: ...

    def to_leftmost(self) -> None: ...

    def to_location(self, x: int, y: int) -> None: ...

    def up(self, pixel: int = 300) -> None: ...

    def down(self, pixel: int = 300) -> None: ...

    def left(self, pixel: int = 300) -> None: ...

    def right(self, pixel: int = 300) -> None: ...


class ChromiumSelect(object):

    def __init__(self, ele: ChromiumElement):
        self._ele: ChromiumElement = ...

    def __call__(self, text_or_index: Union[str, int, list, tuple], timeout: float = None) -> bool: ...

    @property
    def is_multi(self) -> bool: ...

    @property
    def options(self) -> List[ChromiumElement]: ...

    @property
    def selected_option(self) -> Union[ChromiumElement, None]: ...

    @property
    def selected_options(self) -> List[ChromiumElement]: ...

    def clear(self) -> None: ...

    def by_text(self, text: Union[str, list, tuple], timeout: float = None) -> bool: ...

    def by_value(self, value: Union[str, list, tuple], timeout: float = None) -> bool: ...

    def by_index(self, index: Union[int, list, tuple], timeout: float = None) -> bool: ...

    def cancel_by_text(self, text: Union[str, list, tuple], timeout: float = None) -> bool: ...

    def cancel_by_value(self, value: Union[str, list, tuple], timeout: float = None) -> bool: ...

    def cancel_by_index(self, index: Union[int, list, tuple], timeout: float = None) -> bool: ...

    def invert(self) -> None: ...

    def _select(self,
                text_value_index: Union[str, int, list, tuple] = None,
                para_type: str = 'text',
                deselect: bool = False,
                timeout: float = None) -> bool: ...

    def _select_multi(self,
                      text_value_index: Union[list, tuple] = None,
                      para_type: str = 'text',
                      deselect: bool = False) -> bool: ...


class ChromiumWaiter(object):
    def __init__(self, page_or_ele):
        self._driver: Union[ChromiumBase, ChromiumElement] = ...

    def ele_delete(self, loc_or_ele: Union[str, tuple, ChromiumElement], timeout: Union[int, float] = None) -> bool: ...

    def ele_display(self, loc_or_ele: Union[str, tuple, ChromiumElement],
                    timeout: Union[int, float] = None) -> bool: ...

    def ele_hidden(self, loc_or_ele: Union[str, tuple, ChromiumElement], timeout: Union[int, float] = None) -> bool: ...


class ChromiumElementWaiter(object):

    def __init__(self,
                 page_or_ele: Union[ChromiumBase, ChromiumElement],
                 loc_or_ele: Union[str, tuple, ChromiumElement],
                 timeout: Union[int, float] = None):
        self.loc_or_ele: Union[str, tuple, ChromiumElement] = ...
        self.timeout: float = ...
        self.driver: Union[ChromiumPage, ChromiumPage] = ...

    def delete(self) -> bool: ...

    def display(self) -> bool: ...

    def hidden(self) -> bool: ...

    def _wait_ele(self, mode: str) -> Union[None, bool]: ...


class Pseudo(object):
    def __init__(self, ele: ChromiumElement):
        self._ele: ChromiumElement = ...

    @property
    def before(self) -> str: ...

    @property
    def after(self) -> str: ...
