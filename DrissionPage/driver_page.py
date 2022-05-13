# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   driver_page.py
"""
from glob import glob
from os import sep
from pathlib import Path
from time import sleep, perf_counter
from typing import Union, List, Any, Tuple

from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from .base import BasePage
from .common import get_usable_path
from .driver_element import DriverElement, make_driver_ele, Scroll, ElementWaiter
from .session_element import make_session_ele, SessionElement


class DriverPage(BasePage):
    """DriverPage封装了页面操作的常用功能，使用selenium来获取、解析、操作网页"""

    def __init__(self, driver: RemoteWebDriver, timeout: float = 10) -> None:
        """初始化函数，接收一个WebDriver对象，用来操作网页"""
        super().__init__(timeout)
        self._driver = driver
        self._wait_object = None
        self._scroll = None

    def __call__(self, loc_or_str: Union[Tuple[str, str], str, DriverElement, WebElement],
                 timeout: float = None) -> Union[DriverElement, str, None]:
        """在内部查找元素                                           \n
        例：ele = page('@id=ele_id')                              \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: DriverElement对象或属性、文本
        """
        return self.ele(loc_or_str, timeout)

    # -----------------共有属性和方法-------------------
    @property
    def url(self) -> Union[str, None]:
        """返回当前网页url"""
        if not self._driver or not self.driver.current_url.startswith('http'):
            return None
        else:
            return self.driver.current_url

    @property
    def html(self) -> str:
        """返回页面的html文本"""
        return self.driver.find_element('xpath', "//*").get_attribute("outerHTML")

    @property
    def json(self) -> dict:
        """当返回内容是json格式时，返回对应的字典"""
        from json import loads
        return loads(self('t:pre').text)

    def get(self,
            url: str,
            show_errmsg: bool = False,
            retry: int = None,
            interval: float = None) -> Union[None, bool]:
        """访问url                                            \n
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :return: 目标url是否可用，返回None表示不确定
        """
        retry, interval = self._before_connect(url, retry, interval)
        self._url_available = self._d_connect(self._url, times=retry, interval=interval, show_errmsg=show_errmsg)

        try:
            self._driver.execute_script('Object.defineProperty(navigator,"webdriver",{get:() => undefined,});')
        except Exception:
            pass

        return self._url_available

    def ele(self,
            loc_or_ele: Union[Tuple[str, str], str, DriverElement, WebElement],
            timeout: float = None) -> Union[DriverElement, str, None]:
        """返回页面中符合条件的第一个元素                                          \n
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与页面等待时间一致
        :return: DriverElement对象或属性、文本
        """
        return self._ele(loc_or_ele, timeout)

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None) -> List[Union[DriverElement, str]]:
        """返回页面中所有符合条件的元素                                     \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与页面等待时间一致
        :return: DriverElement对象或属性、文本组成的列表
        """
        return self._ele(loc_or_str, timeout, single=False)

    def s_ele(self, loc_or_ele: Union[Tuple[str, str], str, DriverElement] = None) -> Union[SessionElement, str, None]:
        """查找第一个符合条件的元素以SessionElement形式返回，处理复杂页面时效率很高       \n
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        if isinstance(loc_or_ele, DriverElement):
            return make_session_ele(loc_or_ele)
        else:
            return make_session_ele(self, loc_or_ele)

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str] = None) -> List[Union[SessionElement, str]]:
        """查找所有符合条件的元素以SessionElement列表形式返回                       \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象组成的列表
        """
        return make_session_ele(self, loc_or_str, single=False)

    def _ele(self,
             loc_or_ele: Union[Tuple[str, str], str, DriverElement, WebElement],
             timeout: float = None,
             single: bool = True) -> Union[DriverElement, str, None, List[Union[DriverElement, str]]]:
        """返回页面中符合条件的元素，默认返回第一个                                   \n
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :param single: True则返回第一个，False则返回全部
        :return: DriverElement对象
        """
        # 接收到字符串或元组，获取定位loc元组
        if isinstance(loc_or_ele, (str, tuple)):
            return make_driver_ele(self, loc_or_ele, single, timeout)

        # 接收到DriverElement对象直接返回
        elif isinstance(loc_or_ele, DriverElement):
            return loc_or_ele

        # 接收到WebElement对象打包成DriverElement对象返回
        elif isinstance(loc_or_ele, WebElement):
            return DriverElement(loc_or_ele, self)

        # 接收到的类型不正确，抛出异常
        else:
            raise ValueError('loc_or_str参数只能是tuple、str、DriverElement 或 WebElement类型。')

    def get_cookies(self, as_dict: bool = False) -> Union[list, dict]:
        """返回当前网站cookies"""
        if as_dict:
            return {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
        else:
            return self.driver.get_cookies()

    @property
    def timeout(self) -> float:
        """返回查找元素时等待的秒数"""
        return self._timeout

    @timeout.setter
    def timeout(self, second: float) -> None:
        """设置查找元素时等待的秒数"""
        self._timeout = second
        self._wait_object = None

    def _d_connect(self,
                   to_url: str,
                   times: int = 0,
                   interval: float = 1,
                   show_errmsg: bool = False) -> Union[bool, None]:
        """尝试连接，重试若干次                            \n
        :param to_url: 要访问的url
        :param times: 重试次数
        :param interval: 重试间隔（秒）
        :param show_errmsg: 是否抛出异常
        :return: 是否成功，返回None表示不确定
        """
        err = None
        is_ok = False

        for _ in range(times + 1):
            try:
                self.driver.get(to_url)
                go_ok = True
            except Exception as e:
                err = e
                go_ok = False

            is_ok = self.check_page() if go_ok else False

            if is_ok is not False:
                break

            if _ < times:
                sleep(interval)
                if show_errmsg:
                    print(f'重试 {to_url}')

        if is_ok is False and show_errmsg:
            raise err if err is not None else ConnectionError('连接异常。')

        return is_ok

    # ----------------driver独有属性和方法-----------------------
    @property
    def driver(self) -> WebDriver:
        return self._driver

    @property
    def wait_object(self) -> WebDriverWait:
        """返回WebDriverWait对象，重用避免每次新建对象"""
        if self._wait_object is None:
            self._wait_object = WebDriverWait(self.driver, timeout=self.timeout)

        return self._wait_object

    @property
    def timeouts(self) -> dict:
        """返回三种超时时间，selenium4以上版本可用"""
        return {'implicit': self.timeout,
                'pageLoad': self.driver.timeouts.page_load,
                'script': self.driver.timeouts.script}

    @property
    def tabs_count(self) -> int:
        """返回标签页数量"""
        try:
            return len(self.driver.window_handles)
        except Exception:
            return 0

    @property
    def tab_handles(self) -> list:
        """返回所有标签页handle列表"""
        return self.driver.window_handles

    @property
    def current_tab_index(self) -> int:
        """返回当前标签页序号"""
        return self.driver.window_handles.index(self.driver.current_window_handle)

    @property
    def current_tab_handle(self) -> str:
        """返回当前标签页handle"""
        return self.driver.current_window_handle

    @property
    def active_ele(self) -> DriverElement:
        """返回当前焦点所在元素"""
        return DriverElement(self.driver.switch_to.active_element, self)

    @property
    def scroll(self) -> Scroll:
        """用于滚动滚动条的对象"""
        if self._scroll is None:
            self._scroll = Scroll(self)
        return self._scroll

    @property
    def to_frame(self) -> 'ToFrame':
        """用于跳转到frame的对象，调用其方法实现跳转                                             \n
        示例：                                                                               \n
            page.to_frame.by_loc('tag:iframe')               - 通过传入frame的查询字符串定位   \n
            page.to_frame.by_loc((By.TAG_NAME, 'iframe'))    - 通过传入定位符定位             \n
            page.to_frame.by_id('iframe_id')                 - 通过frame的id属性定位          \n
            page.to_frame('iframe_name')                     - 通过frame的name属性定位        \n
            page.to_frame(iframe_element)                    - 通过传入元素对象定位            \n
            page.to_frame(0)                                 - 通过frame的序号定位            \n
            page.to_frame.main()                             - 跳到最顶层                    \n
            page.to_frame.parent()                           - 跳到上一层
        """
        return ToFrame(self)

    def set_timeouts(self, implicit: float = None, pageLoad: float = None, script: float = None) -> None:
        """设置超时时间，单位为秒，selenium4以上版本有效       \n
        :param implicit: 查找元素超时时间
        :param pageLoad: 页面加载超时时间
        :param script: 脚本运行超时时间
        :return: None
        """
        if implicit is not None:
            self.timeout = implicit

        if pageLoad is not None:
            self.driver.set_page_load_timeout(pageLoad)

        if script is not None:
            self.driver.set_script_timeout(script)

    def wait_ele(self,
                 loc_or_ele: Union[str, tuple, DriverElement, WebElement],
                 timeout: float = None) -> 'ElementWaiter':
        """等待元素从dom删除、显示、隐藏                             \n
        :param loc_or_ele: 可以是元素、查询字符串、loc元组
        :param timeout: 等待超时时间
        :return: 用于等待的ElementWaiter对象
        """
        return ElementWaiter(self, loc_or_ele, timeout)

    def check_page(self) -> Union[bool, None]:
        """检查页面是否符合预期            \n
        由子类自行实现各页面的判定规则
        """
        return None

    def run_script(self, script: str, *args) -> Any:
        """执行js代码                 \n
        :param script: js文本
        :param args: 传入的参数
        :return: js执行结果
        """
        return self.driver.execute_script(script, *args)

    def run_async_script(self, script: str, *args) -> Any:
        """以异步方式执行js代码                 \n
        :param script: js文本
        :param args: 传入的参数
        :return: js执行结果
        """
        return self.driver.execute_async_script(script, *args)

    def run_cdp(self, cmd: str, cmd_args: dict) -> Any:
        """执行Chrome DevTools Protocol语句
        :param cmd: 协议项目
        :param cmd_args: 参数
        :return: 执行的结果
        """
        return self.driver.execute_cdp_cmd(cmd, cmd_args)

    def create_tab(self, url: str = '') -> None:
        """新建并定位到一个标签页,该标签页在最后面       \n
        :param url: 新标签页跳转到的网址
        :return: None
        """
        self.driver.switch_to.new_window('tab')
        if url:
            self.get(url)

    def close_tabs(self, num_or_handles: Union[int, str, list, tuple] = None) -> None:
        """关闭传入的标签页，默认关闭当前页。可传入多个                                                     \n
        注意：当程序使用的是接管的浏览器，获取到的 handle 顺序和视觉效果不一致，不能按序号关闭。                 \n
        :param num_or_handles:要关闭的标签页序号或handle，可传入handle和序号组成的列表或元组，为None时关闭当前页
        :return: None
        """
        tabs = (self.current_tab_handle,) if num_or_handles is None else _get_handles(self.tab_handles, num_or_handles)
        for i in tabs:
            self.driver.switch_to.window(i)
            self.driver.close()

        self.to_tab(0)

    def close_other_tabs(self, num_or_handles: Union[int, str, list, tuple] = None) -> None:
        """关闭传入的标签页以外标签页，默认保留当前页。可传入多个                                              \n
        注意：当程序使用的是接管的浏览器，获取到的 handle 顺序和视觉效果不一致，不能按序号关闭。                   \n
        :param num_or_handles: 要保留的标签页序号或handle，可传入handle和序号组成的列表或元组，为None时保存当前页
        :return: None
        """
        all_tabs = self.driver.window_handles
        reserve_tabs = {self.current_tab_handle} if num_or_handles is None else _get_handles(all_tabs, num_or_handles)

        for i in set(all_tabs) - reserve_tabs:
            self.driver.switch_to.window(i)
            self.driver.close()

        self.to_tab(0)

    def to_tab(self, num_or_handle: Union[int, str] = 0) -> None:
        """跳转到标签页                                                         \n
        注意：当程序使用的是接管的浏览器，获取到的 handle 顺序和视觉效果不一致         \n
        :param num_or_handle: 标签页序号或handle字符串，序号第一个为0，最后为-1
        :return: None
        """
        try:
            tab = int(num_or_handle)
        except (ValueError, TypeError):
            tab = num_or_handle

        tab = self.driver.window_handles[tab] if isinstance(tab, int) else tab
        self.driver.switch_to.window(tab)

    def set_ua_to_tab(self, ua: str) -> None:
        """为当前tab设置user agent，只在当前tab有效          \n
        :param ua: user agent字符串
        :return: None
        """
        self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": ua})

    def screenshot(self, path: str, filename: str = None) -> str:
        """截取页面可见范围截图                                  \n
        :param path: 保存路径
        :param filename: 图片文件名，不传入时以页面title命名
        :return: 图片完整路径
        """
        name = filename or self.title
        if not name.lower().endswith('.png'):
            name = f'{name}.png'
        path = Path(path).absolute()
        path.mkdir(parents=True, exist_ok=True)
        img_path = str(get_usable_path(f'{path}{sep}{name}'))
        self.driver.save_screenshot(img_path)
        return img_path

    def scroll_to_see(self, loc_or_ele: Union[str, tuple, WebElement, DriverElement]) -> None:
        """滚动页面直到元素可见                                                        \n
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串（详见ele函数注释）
        :return: None
        """
        ele = self.ele(loc_or_ele)
        ele.run_script("arguments[0].scrollIntoView();")

    def refresh(self) -> None:
        """刷新当前页面"""
        self.driver.refresh()

    def back(self) -> None:
        """在浏览历史中后退一步"""
        self.driver.back()

    def forward(self) -> None:
        """在浏览历史中前进一步"""
        self.driver.forward()

    def set_window_size(self, width: int = None, height: int = None) -> None:
        """设置浏览器窗口大小，默认最大化，任一参数为0最小化  \n
        :param width: 浏览器窗口高
        :param height: 浏览器窗口宽
        :return: None
        """
        if width is None and height is None:
            self.driver.maximize_window()

        elif width == 0 or height == 0:
            self.driver.minimize_window()

        else:
            if width < 0 or height < 0:
                raise ValueError('x 和 y参数必须大于0。')

            new_x = width or self.driver.get_window_size()['width']
            new_y = height or self.driver.get_window_size()['height']
            self.driver.set_window_size(new_x, new_y)

    def chrome_downloading(self, download_path: str) -> list:
        """返回浏览器下载中的文件列表             \n
        :param download_path: 下载文件夹路径
        :return: 文件列表
        """
        return glob(f'{download_path}{sep}*.crdownload')

    def process_alert(self, ok: bool = True, send: str = None, timeout: float = None) -> Union[str, None]:
        """处理提示框                                                            \n
        :param ok: True表示确认，False表示取消，其它值不会按按钮但依然返回文本值
        :param send: 处理prompt提示框时可输入文本
        :param timeout: 等待提示框出现的超时时间
        :return: 提示框内容文本，未等到提示框则返回None
        """

        def do_it():
            try:
                return self.driver.switch_to.alert
            except NoAlertPresentException:
                return False

        timeout = timeout if timeout is not None else self.timeout
        t1 = perf_counter()
        alert = do_it()
        while alert is False and perf_counter() - t1 <= timeout:
            alert = do_it()

        if alert is False:
            return None

        res_text = alert.text

        if send is not None:
            alert.send_keys(send)

        if ok is True:
            alert.accept()
        elif ok is False:
            alert.dismiss()

        return res_text


class ToFrame(object):
    """用于处理焦点跳转到页面框架的类"""

    def __init__(self, page: DriverPage):
        self.page = page

    def __call__(self, condition: Union[int, str, tuple, WebElement, DriverElement] = 'main'):
        """跳转到(i)frame，可传入id、name、序号、元素对象、定位符                  \n
        :param condition: (i)frame，可传入id、name、序号、元素对象、定位符
        :return: 当前页面对象
        """
        if isinstance(condition, (DriverElement, WebElement)):
            self.by_ele(condition)
        elif isinstance(condition, int):
            self.by_index(condition)
        elif ':' not in condition and '=' not in condition and not condition.startswith(('#', '.', '@')):
            self.by_id(condition)
        else:
            self.by_loc(condition)

        return self.page

    def main(self) -> DriverPage:
        """焦点跳转到最高层级框架"""
        self.page.driver.switch_to.default_content()
        return self.page

    def parent(self, level: int = 1) -> DriverPage:
        """焦点跳转到上级框架，可指定上级层数       \n
        :param level: 上面第几层框架
        :return: 框架所在页面对象
        """
        if level < 1:
            raise ValueError('level参数须是大于0的整数。')
        for _ in range(level):
            self.page.driver.switch_to.parent_frame()
        return self.page

    def by_id(self, id_: str) -> DriverPage:
        """焦点跳转到id为该值的(i)frame              \n
        :param id_: (i)frame的id属性值
        :return: 框架所在页面对象
        """
        self.page.driver.switch_to.frame(id_)
        return self.page

    def by_name(self, name: str) -> DriverPage:
        """焦点跳转到name为该值的(i)frame              \n
        :param name: (i)frame的name属性值
        :return: 框架所在页面对象
        """
        self.page.driver.switch_to.frame(name)
        return self.page

    def by_index(self, index: int) -> DriverPage:
        """焦点跳转到页面中第几个(i)frame              \n
        :param index: 页面中第几个(i)frame
        :return: 框架所在页面对象
        """
        self.page.driver.switch_to.frame(index)
        return self.page

    def by_loc(self, loc: Union[str, tuple]) -> DriverPage:
        """焦点跳转到根据定位符获取到的(i)frame                   \n
        :param loc: 定位符，支持selenium原生和DriverPage定位符
        :return: 框架所在页面对象
        """
        self.page.driver.switch_to.frame(self.page(loc).inner_ele)
        return self.page

    def by_ele(self, ele: Union[DriverElement, WebElement]) -> DriverPage:
        """焦点跳转到传入的(i)frame元素对象              \n
        :param ele: (i)frame元素对象
        :return: 框架所在页面对象
        """
        if isinstance(ele, DriverElement):
            ele = ele.inner_ele
        self.page.driver.switch_to.frame(ele)
        return self.page


def _get_handles(handles: list, num_or_handles: Union[int, str, list, tuple]) -> set:
    """返回指定标签页组成的set
    :param handles: handles列表
    :param num_or_handles: 指定的标签页，可以是多个
    :return: 指定标签页组成的set
    """
    if isinstance(num_or_handles, (int, str)):
        num_or_handles = (num_or_handles,)
    elif not isinstance(num_or_handles, (list, tuple)):
        raise TypeError('num_or_handle参数只能是int、str、list 或 tuple类型。')

    return set(i if isinstance(i, str) else handles[i] for i in num_or_handles)
