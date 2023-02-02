# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from pathlib import Path
from time import sleep
from warnings import warn

from requests import Session
from tldextract import extract

from .base import BasePage
from .chromium_base import ChromiumBase, Timeout
from .chromium_driver import ChromiumDriver, CallMethodException
from .chromium_page import ChromiumPage, ChromiumDownloadSetter
from .configs.chromium_options import ChromiumOptions
from .configs.driver_options import DriverOptions
from .configs.session_options import SessionOptions
from .functions.web import cookies_to_tuple
from .session_page import SessionPage


class WebPage(SessionPage, ChromiumPage, BasePage):
    """整合浏览器和request的页面类"""

    def __init__(self, mode='d', timeout=None, driver_or_options=None, session_or_options=None):
        """初始化函数
        :param mode: 'd' 或 's'，即driver模式和session模式
        :param timeout: 超时时间，d模式时为寻找元素时间，s模式时为连接时间，默认10秒
        :param driver_or_options: ChromiumDriver对象或DriverOptions对象，只使用s模式时应传入False
        :param session_or_options: Session对象或SessionOptions对象，只使用d模式时应传入False
        """
        self._mode = mode.lower()
        if self._mode not in ('s', 'd'):
            raise ValueError('mode参数只能是s或d。')
        self._has_driver, self._has_session = (None, True) if self._mode == 's' else (True, None)

        self._debug = False
        self._debug_recorder = None
        self.address = None

        self._session = None
        self._tab_obj = None
        self._driver_options = None
        self._session_options = None
        self._response = None
        self._download_set = None

        self._set_both_options(driver_or_options, session_or_options)

        if self._mode == 'd':
            self._to_d_mode()

        t = timeout if isinstance(timeout, (int, float)) else self.timeouts.implicit
        super(ChromiumBase, self).__init__(t)  # 调用Base的__init__()

    def _set_both_options(self, dr_opt, se_opt):
        """处理两种模式的设置
        :param dr_opt: ChromiumDriver或DriverOptions对象，为None则从ini读取，为False用默认信息创建
        :param se_opt: Session、SessionOptions对象或配置信息，为None则从ini读取，为False用默认信息创建
        :return: None
        """
        # 浏览器配置
        if isinstance(dr_opt, ChromiumDriver):
            self._connect_browser(dr_opt)
            self._has_driver = True
            # self._driver_options = None
            dr_opt = False

        else:
            if dr_opt is None:
                self._driver_options = ChromiumOptions()

            elif dr_opt is False:
                self._driver_options = ChromiumOptions(read_file=False)

            elif isinstance(dr_opt, (ChromiumOptions, DriverOptions)):
                self._driver_options = dr_opt

            else:
                raise TypeError('driver_or_options参数只能接收ChromiumDriver, ChromiumOptions、None或False。')

        # Session配置
        if isinstance(se_opt, Session):
            self._session = se_opt
            self._has_session = True
            self._session_options = SessionOptions(read_file=False)
            se_opt = False

        else:
            if se_opt is None:
                self._session_options = SessionOptions()

            elif se_opt is False:
                self._session_options = SessionOptions(read_file=False)

            elif isinstance(se_opt, SessionOptions):
                self._session_options = se_opt

            else:
                raise TypeError('session_or_options参数只能接收Session, SessionOptions、None或False。')

        # 通用配置
        self._timeouts = Timeout(self)
        self._page_load_strategy = self._driver_options.page_load_strategy
        self._download_path = None
        if se_opt is not False:
            self.set_timeouts(implicit=self._session_options.timeout)
            self._download_path = self._session_options.download_path

        if dr_opt is not False:
            t = self._driver_options.timeouts
            self.set_timeouts(t['implicit'], t['pageLoad'], t['script'])
            self._download_path = self._driver_options.download_path

    def _set_options(self):
        """覆盖父类同名方法"""
        pass

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素
        例：ele = page('@id=ele_id')
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: 子元素对象
        """
        if self._mode == 'd':
            return super(SessionPage, self).__call__(loc_or_str, timeout)
        elif self._mode == 's':
            return super().__call__(loc_or_str)

    @property
    def url(self):
        """返回当前url"""
        if self._mode == 'd':
            return super(SessionPage, self).url if self._tab_obj else None
        elif self._mode == 's':
            return self._session_url

    @property
    def html(self):
        """返回页面html文本"""
        if self._mode == 's':
            return super().html
        elif self._mode == 'd':
            return super(SessionPage, self).html if self._has_driver else ''

    @property
    def json(self):
        """当返回内容是json格式时，返回对应的字典"""
        if self._mode == 's':
            return super().json
        elif self._mode == 'd':
            return super(SessionPage, self).json

    @property
    def response(self):
        """返回 s 模式获取到的 Response 对象，切换到 s 模式"""
        self.change_mode('s')
        return self._response

    @property
    def mode(self):
        """返回当前模式，'s'或'd' """
        return self._mode

    @property
    def cookies(self):
        if self._mode == 's':
            return super().get_cookies()
        elif self._mode == 'd':
            return super(SessionPage, self).get_cookies()

    @property
    def session(self):
        """返回Session对象，如未初始化则按配置信息创建"""
        if self._session is None:
            self._set_session(self._session_options)

        return self._session

    @property
    def driver(self):
        """返回纯粹的ChromiumDriver对象"""
        return self._tab_obj

    @property
    def _wait_driver(self):
        """返回用于控制浏览器的ChromiumDriver对象，会先等待页面加载完毕"""
        while self._is_loading:
            sleep(.1)
        return self._driver

    @property
    def _driver(self):
        """返回纯粹的ChromiumDriver对象，调用时切换到d模式，并连接浏览器"""
        self.change_mode('d')
        if self._tab_obj is None:
            self._connect_browser(self._driver_options)
        return self._tab_obj

    @_driver.setter
    def _driver(self, tab):
        self._tab_obj = tab

    @property
    def _session_url(self):
        """返回 session 保存的url"""
        return self._response.url if self._response else None

    @property
    def timeout(self):
        """返回通用timeout设置"""
        return self.timeouts.implicit

    @timeout.setter
    def timeout(self, second):
        """设置通用超时时间
        :param second: 秒数
        :return: None
        """
        self.set_timeouts(implicit=second)

    @property
    def download_path(self):
        """返回默认下载路径"""
        return super(SessionPage, self).download_path

    @property
    def download_set(self):
        """返回下载设置对象"""
        if self._download_set is None:
            self._download_set = WebPageDownloadSetter(self)
        return self._download_set

    @property
    def download(self):
        """返回下载器对象"""
        return self.download_set._switched_DownloadKit

    def get(self, url, show_errmsg=False, retry=None, interval=None, timeout=None, **kwargs):
        """跳转到一个url
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param timeout: 连接超时时间（秒）
        :param kwargs: 连接参数，s模式专用
        :return: url是否可用，d模式返回None时表示不确定
        """
        if self._mode == 'd':
            return super(SessionPage, self).get(url, show_errmsg, retry, interval, timeout)
        elif self._mode == 's':
            if timeout is None:
                timeout = self.timeouts.page_load if self._has_driver else self.timeout
            return super().get(url, show_errmsg, retry, interval, timeout, **kwargs)

    def post(self, url: str, data=None, show_errmsg=False, retry=None, interval=None, **kwargs):
        """用post方式跳转到url，会切换到s模式
        :param url: 目标url
        :param data: post方式时提交的数据
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        self.change_mode('s', go=False)
        return super().post(url, data, show_errmsg, retry, interval, **kwargs)

    def ele(self, loc_or_ele, timeout=None):
        """返回第一个符合条件的元素、属性或节点文本
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与页面等待时间一致
        :return: 元素对象或属性、文本节点文本
        """
        if self._mode == 's':
            return super().ele(loc_or_ele)
        elif self._mode == 'd':
            return super(SessionPage, self).ele(loc_or_ele, timeout=timeout)

    def eles(self, loc_or_str, timeout=None):
        """返回页面中所有符合条件的元素、属性或节点文本
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与页面等待时间一致
        :return: 元素对象或属性、文本组成的列表
        """
        if self._mode == 's':
            return super().eles(loc_or_str)
        elif self._mode == 'd':
            return super(SessionPage, self).eles(loc_or_str, timeout=timeout)

    def s_ele(self, loc_or_ele=None):
        """查找第一个符合条件的元素以SessionElement形式返回，d模式处理复杂页面时效率很高
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        if self._mode == 's':
            return super().s_ele(loc_or_ele)
        elif self._mode == 'd':
            return super(SessionPage, self).s_ele(loc_or_ele)

    def s_eles(self, loc_or_str):
        """查找所有符合条件的元素以SessionElement形式返回，d模式处理复杂页面时效率很高
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本组成的列表
        """
        if self._mode == 's':
            return super().s_eles(loc_or_str)
        elif self._mode == 'd':
            return super(SessionPage, self).s_eles(loc_or_str)

    def change_mode(self, mode=None, go=True, copy_cookies=True):
        """切换模式，接收's'或'd'，除此以外的字符串会切换为 d 模式
        如copy_cookies为True，切换时会把当前模式的cookies复制到目标模式
        切换后，如果go是True，调用相应的get函数使访问的页面同步
        :param mode: 模式字符串
        :param go: 是否跳转到原模式的url
        :param copy_cookies: 是否复制cookies到目标模式
        :return: None
        """
        if mode is not None and mode.lower() == self._mode:
            return

        self._mode = 's' if self._mode == 'd' else 'd'

        # s模式转d模式
        if self._mode == 'd':
            if self._tab_obj is None:
                self._connect_browser(self._driver_options)

            self._url = None if not self._has_driver else super(SessionPage, self).url
            self._has_driver = True

            if self._session_url:
                if copy_cookies:
                    self.cookies_to_driver()

                if go:
                    self.get(self._session_url)

        # d模式转s模式
        elif self._mode == 's':
            self._has_session = True
            self._url = self._session_url

            if self._has_driver:
                if copy_cookies:
                    self.cookies_to_session()

                if go:
                    url = super(SessionPage, self).url
                    if url.startswith('http'):
                        self.get(url)

    def cookies_to_session(self, copy_user_agent=True):
        """把driver对象的cookies复制到session对象
        :param copy_user_agent: 是否复制ua信息
        :return: None
        """
        if copy_user_agent:
            selenium_user_agent = self._tab_obj.Runtime.evaluate(expression='navigator.userAgent;')['result']['value']
            self.session.headers.update({"User-Agent": selenium_user_agent})

        self.set_cookies(self._get_driver_cookies(as_dict=True), set_session=True)

    def cookies_to_driver(self):
        """把session对象的cookies复制到driver对象"""
        ex_url = extract(self._session_url)
        domain = f'{ex_url.domain}.{ex_url.suffix}'
        cookies = []
        for cookie in super().get_cookies():
            if cookie.get('domain', '') == '':
                cookie['domain'] = domain

            if domain in cookie['domain']:
                cookies.append(cookie)
        self.set_cookies(cookies, set_driver=True)

    def get_cookies(self, as_dict=False, all_domains=False):
        """返回cookies
        :param as_dict: 是否以字典方式返回
        :param all_domains: 是否返回所有域的cookies
        :return: cookies信息
        """
        if self._mode == 's':
            return super().get_cookies(as_dict, all_domains)
        elif self._mode == 'd':
            return self._get_driver_cookies(as_dict)

    def _get_driver_cookies(self, as_dict=False):
        """获取浏览器cookies
        :param as_dict: 以dict形式返回
        :return: cookies信息
        """
        cookies = self._tab_obj.Network.getCookies()['cookies']
        if as_dict:
            return {cookie['name']: cookie['value'] for cookie in cookies}
        else:
            return cookies

    def set_cookies(self, cookies, set_session=False, set_driver=False):
        """添加cookies信息到浏览器或session对象
        :param cookies: 可以接收`CookieJar`、`list`、`tuple`、`str`、`dict`格式的`cookies`
        :param set_session: 是否设置到Session对象
        :param set_driver: 是否设置到浏览器
        :return: None
        """
        # 添加cookie到driver
        if set_driver:
            cookies = cookies_to_tuple(cookies)
            result_cookies = []
            for cookie in cookies:
                if not cookie.get('domain', None):
                    continue
                c = {'value': '' if cookie['value'] is None else cookie['value'],
                     'name': cookie['name'],
                     'domain': cookie['domain']}
                result_cookies.append(c)
            self._tab_obj.Network.setCookies(cookies=result_cookies)

        # 添加cookie到session
        if set_session:
            super().set_cookies(cookies)

    def set_headers(self, headers: dict) -> None:
        """设置固定发送的headers
        :param headers: dict格式的headers数据
        :return: None
        """
        if self._has_session:
            return super().set_headers(headers)
        if self._has_driver:
            super(SessionPage, self).set_headers(headers)

    def close_driver(self):
        """关闭driver及浏览器"""
        if self._has_driver:
            self.change_mode('s')
            try:
                self.driver.Browser.close()
            except Exception:
                pass
            self._has_driver = None

    def close_session(self):
        """关闭session"""
        if self._has_session:
            self.change_mode('d')
            self._session.close()
            self._session = None
            self._response = None
            self._has_session = None

    def _ele(self, loc_or_ele, timeout=None, single=True, relative=False):
        """返回页面中符合条件的元素、属性或节点文本，默认返回第一个
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 查找元素超时时间，d模式专用
        :param single: True则返回第一个，False则返回全部
        :return: 元素对象或属性、文本节点文本
        """
        if self._mode == 's':
            return super()._ele(loc_or_ele, single=single)
        elif self._mode == 'd':
            return super(SessionPage, self)._ele(loc_or_ele, timeout=timeout, single=single, relative=relative)

    def quit(self):
        """关闭浏览器，关闭session"""
        if self._has_session:
            self._session.close()
            self._session = None
            self._response = None
            self._has_session = None
        if self._has_driver:
            self._tab_obj.Browser.close()
            self._tab_obj.stop()
            self._tab_obj = None
            self._has_driver = None


class WebPageDownloadSetter(ChromiumDownloadSetter):
    """用于设置下载参数的类"""

    def __init__(self, page):
        super().__init__(page)
        self._session = page.session

    @property
    def _switched_DownloadKit(self):
        """返回从浏览器同步cookies后的Session对象"""
        if self._page.mode == 'd':
            self._cookies_to_session()
        return self.DownloadKit

    def save_path(self, path):
        """设置下载路径
        :param path: 下载路径
        :return: None
        """
        path = path or ''
        path = Path(path).absolute()
        path.mkdir(parents=True, exist_ok=True)
        path = str(path)
        self._page._download_path = path
        self.DownloadKit.goal_path = path

        if self._page._has_driver:
            try:
                self._page.browser_driver.Browser.setDownloadBehavior(behavior=self._behavior, downloadPath=path,
                                                                      eventsEnabled=True)
            except CallMethodException:
                warn('\n您的浏览器版本太低，用新标签页下载文件可能崩溃，建议升级。')
                self._page.run_cdp('Page.setDownloadBehavior', behavior=self._behavior, downloadPath=path,
                                   not_change=True)

    def by_browser(self):
        """设置使用浏览器下载文件"""
        if not self._page._has_driver:
            raise RuntimeError('浏览器未连接。')

        try:
            self._page.browser_driver.Browser.setDownloadBehavior(behavior='allow', eventsEnabled=True,
                                                                  downloadPath=self._page.download_path)
            self._page.browser_driver.Browser.downloadWillBegin = self._download_by_browser

        except CallMethodException:
            warn('\n您的浏览器版本太低，用新标签页下载文件可能崩溃，建议升级。')
            self._page.driver.Page.setDownloadBehavior(behavior='allow', downloadPath=self._page.download_path)
            self._page.driver.Page.downloadWillBegin = self._download_by_browser

        self._behavior = 'allow'

    def by_DownloadKit(self):
        """设置使用DownloadKit下载文件"""
        if self._page._has_driver:
            try:
                self._page.browser_driver.Browser.setDownloadBehavior(behavior='deny', eventsEnabled=True)
                self._page.browser_driver.Browser.downloadWillBegin = self._download_by_DownloadKit
            except CallMethodException:
                raise RuntimeError('您的浏览器版本太低，不支持此方法，请升级。')

        self._behavior = 'deny'
