# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from pathlib import Path
from platform import system
from threading import Thread
from time import perf_counter, sleep
from warnings import warn

from requests import Session

from .chromium_base import ChromiumBase, Timeout, ChromiumBaseSetter
from .chromium_driver import ChromiumDriver
from .chromium_tab import ChromiumTab
from .configs.chromium_options import ChromiumOptions
from .configs.driver_options import DriverOptions
from .common.browser import connect_browser
from .common.errors import CallMethodError
from .common.web import set_session_cookies
from .session_page import DownloadSetter


class ChromiumPage(ChromiumBase):
    """用于管理浏览器的类"""

    def __init__(self, addr_driver_opts=None, tab_id=None, timeout=None):
        """
        :param addr_driver_opts: 浏览器地址:端口、ChromiumDriver对象或ChromiumOptions对象
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        :param timeout: 超时时间
        """
        self._download_set = None
        self._download_path = None
        super().__init__(addr_driver_opts, tab_id, timeout)

    def _set_start_options(self, addr_driver_opts, none):
        """设置浏览器启动属性
        :param addr_driver_opts: 'ip:port'、ChromiumDriver、ChromiumOptions
        :param none: 用于后代继承
        :return: None
        """
        if not addr_driver_opts or isinstance(addr_driver_opts, (ChromiumOptions, DriverOptions)):
            self._driver_options = addr_driver_opts or ChromiumOptions(addr_driver_opts)

        # 接收浏览器地址和端口
        elif isinstance(addr_driver_opts, str):
            self._driver_options = ChromiumOptions()
            self._driver_options.debugger_address = addr_driver_opts

        # 接收传递过来的ChromiumDriver，浏览器
        elif isinstance(addr_driver_opts, ChromiumDriver):
            self._driver_options = ChromiumOptions(read_file=False)
            self._driver_options.debugger_address = addr_driver_opts.address
            self._tab_obj = addr_driver_opts

        else:
            raise TypeError('只能接收ChromiumDriver或ChromiumOptions类型参数。')

        self.address = self._driver_options.debugger_address

    def _set_runtime_settings(self):
        """设置运行时用到的属性"""
        self._timeouts = Timeout(self,
                                 page_load=self._driver_options.timeouts['pageLoad'],
                                 script=self._driver_options.timeouts['script'],
                                 implicit=self._driver_options.timeouts['implicit'])
        self._page_load_strategy = self._driver_options.page_load_strategy
        self._download_path = self._driver_options.download_path

    def _connect_browser(self, tab_id=None):
        """连接浏览器，在第一次时运行
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        :return: None
        """
        self._chromium_init()  # todo: 传递驱动器时是否须要
        if self._tab_obj:
            self.process = None

        else:
            self.process = connect_browser(self._driver_options)[1]
            if not tab_id:
                json = self._control_session.get(f'http://{self.address}/json').json()
                tab_id = [i['id'] for i in json if i['type'] == 'page'][0]

            self._driver_init(tab_id)
            self._get_document()
            self._first_run = False

    def _chromium_init(self):
        """添加ChromiumPage独有的运行配置"""
        super()._chromium_init()
        self._alert = Alert()

    def _driver_init(self, tab_id):
        """新建页面、页面刷新、切换标签页后要进行的cdp参数初始化
        :param tab_id: 要跳转到的标签页id
        :return: None
        """
        super()._driver_init(tab_id)
        ws = self._control_session.get(f'http://{self.address}/json/version').json()['webSocketDebuggerUrl']
        self._browser_driver = ChromiumDriver(ws.split('/')[-1], 'browser', self.address)
        self._browser_driver.start()
        self._tab_obj.Page.javascriptDialogOpening = self._on_alert_open
        self._tab_obj.Page.javascriptDialogClosed = self._on_alert_close
        self._main_tab = self.tab_id
        try:
            self.download_set.by_DownloadKit()
        except RuntimeError:
            pass

    @property
    def browser_driver(self):
        """返回用于控制浏览器cdp的driver"""
        return self._browser_driver

    @property
    def tabs_count(self):
        """返回标签页数量"""
        return len(self.tabs)

    @property
    def tabs(self):
        """返回所有标签页id组成的列表"""
        j = self._control_session.get(f'http://{self.address}/json').json()  # 不要改用cdp
        return [i['id'] for i in j if i['type'] == 'page']

    @property
    def main_tab(self):
        return self._main_tab

    @property
    def latest_tab(self):
        """返回最新的标签页id，最新标签页指最后创建或最后被激活的"""
        return self.tabs[0]

    @property
    def process_id(self):
        """返回浏览器进程id"""
        if self.process:
            return self.process.pid

        r = self.browser_driver.SystemInfo.getProcessInfo()['processInfo']
        for i in r:
            if i['type'] == 'browser':
                return i['id']
        return None

    @property
    def set(self):
        """返回用于等待的对象"""
        if self._set is None:
            self._set = ChromiumPageSetter(self)
        return self._set

    @property
    def download_path(self):
        """返回默认下载路径"""
        p = self._download_path or ''
        return str(Path(p).absolute())

    @property
    def download_set(self):
        """返回用于设置下载参数的对象"""
        if self._download_set is None:
            self._download_set = ChromiumDownloadSetter(self)
        return self._download_set

    @property
    def download(self):
        """返回下载器对象"""
        return self.download_set._switched_DownloadKit

    def get_tab(self, tab_id=None):
        """获取一个标签页对象
        :param tab_id: 要获取的标签页id，为None时获取当前tab
        :return: 标签页对象
        """
        tab_id = tab_id or self.tab_id
        return ChromiumTab(self, tab_id)

    def to_front(self):
        """激活当前标签页使其处于最前面"""
        self._control_session.get(f'http://{self.address}/json/activate/{self.tab_id}')

    def new_tab(self, url=None, switch_to=True):
        """新建一个标签页,该标签页在最后面
        :param url: 新标签页跳转到的网址
        :param switch_to: 新建标签页后是否把焦点移过去
        :return: None
        """
        if switch_to:
            begin_tabs = set(self.tabs)
            len_tabs = len(begin_tabs)
            self.run_cdp('Target.createTarget', url='')

            tabs = self.tabs
            while len(tabs) == len_tabs:
                tabs = self.tabs
                sleep(.005)

            new_tab = set(tabs) - begin_tabs
            self._to_tab(new_tab.pop(), read_doc=False)
            if url:
                self.get(url)

        elif url:
            self.run_cdp('Target.createTarget', url=url)

        else:
            self.run_cdp('Target.createTarget', url='')

    def to_main_tab(self):
        """跳转到主标签页"""
        self.to_tab(self._main_tab)

    def to_tab(self, tab_id=None, activate=True):
        """跳转到标签页
        :param tab_id: 标签页id字符串，默认跳转到main_tab
        :param activate: 切换后是否变为活动状态
        :return: None
        """
        self._to_tab(tab_id, activate)

    def _to_tab(self, tab_id=None, activate=True, read_doc=True):
        """跳转到标签页
        :param tab_id: 标签页id字符串，默认跳转到main_tab
        :param activate: 切换后是否变为活动状态
        :param read_doc: 切换后是否读取文档
        :return: None
        """
        tabs = self.tabs
        if not tab_id:
            tab_id = self._main_tab
        if tab_id not in tabs:
            tab_id = tabs[0]

        if activate:
            self._control_session.get(f'http://{self.address}/json/activate/{tab_id}')

        if tab_id == self.tab_id:
            return

        self.driver.stop()
        self._driver_init(tab_id)
        if read_doc and self.ready_state == 'complete':
            self._get_document()

    def wait_download_begin(self, timeout=None):
        """等待浏览器下载开始
        :param timeout: 等待超时时间，为None则使用页面对象timeout属性
        :return: 是否等到下载开始
        """
        return self.download_set.wait_download_begin(timeout)

    def close_tabs(self, tab_ids=None, others=False):
        """关闭传入的标签页，默认关闭当前页。可传入多个
        :param tab_ids: 要关闭的标签页id，可传入id组成的列表或元组，为None时关闭当前页
        :param others: 是否关闭指定标签页之外的
        :return: None
        """
        all_tabs = set(self.tabs)
        if isinstance(tab_ids, str):
            tabs = {tab_ids}
        elif tab_ids is None:
            tabs = {self.tab_id}
        else:
            tabs = set(tab_ids)

        if others:
            tabs = all_tabs - tabs

        end_len = len(all_tabs) - len(tabs)
        if end_len <= 0:
            self.quit()
            return

        if self.tab_id in tabs:
            self.driver.stop()

        for tab in tabs:
            self._control_session.get(f'http://{self.address}/json/close/{tab}')
        while len(self.tabs) != end_len:
            sleep(.1)

        if self._main_tab in tabs:
            self._main_tab = self.tabs[0]

        self.to_tab()

    def close_other_tabs(self, tab_ids=None):
        """关闭传入的标签页以外标签页，默认保留当前页。可传入多个
        :param tab_ids: 要保留的标签页id，可传入id组成的列表或元组，为None时保存当前页
        :return: None
        """
        self.close_tabs(tab_ids, True)

    def handle_alert(self, accept=True, send=None, timeout=None):
        """处理提示框，可以自动等待提示框出现
        :param accept: True表示确认，False表示取消，其它值不会按按钮但依然返回文本值
        :param send: 处理prompt提示框时可输入文本
        :param timeout: 等待提示框出现的超时时间，为None则使用self.timeout属性的值
        :return: 提示框内容文本，未等到提示框则返回None
        """
        timeout = timeout or self.timeout
        timeout = .1 if timeout <= 0 else timeout
        end_time = perf_counter() + timeout
        while not self._alert.activated and perf_counter() < end_time:
            sleep(.1)
        if not self._alert.activated:
            return None

        res_text = self._alert.text
        if self._alert.type == 'prompt':
            self.driver.Page.handleJavaScriptDialog(accept=accept, promptText=send)
        else:
            self.driver.Page.handleJavaScriptDialog(accept=accept)
        return res_text

    def hide_browser(self):
        """隐藏浏览器窗口，只在Windows系统可用"""
        show_or_hide_browser(self, hide=True)

    def show_browser(self):
        """显示浏览器窗口，只在Windows系统可用"""
        show_or_hide_browser(self, hide=False)

    def quit(self):
        """关闭浏览器"""
        self._tab_obj.Browser.close()
        self._tab_obj.stop()

    def _on_alert_close(self, **kwargs):
        """alert关闭时触发的方法"""
        self._alert.activated = False
        self._alert.text = None
        self._alert.type = None
        self._alert.defaultPrompt = None
        self._alert.response_accept = kwargs.get('result')
        self._alert.response_text = kwargs['userInput']
        self._tab_obj.has_alert = False

    def _on_alert_open(self, **kwargs):
        """alert出现时触发的方法"""
        self._alert.activated = True
        self._alert.text = kwargs['message']
        self._alert.type = kwargs['message']
        self._alert.defaultPrompt = kwargs.get('defaultPrompt', None)
        self._alert.response_accept = None
        self._alert.response_text = None
        self._tab_obj.has_alert = True

    def set_main_tab(self, tab_id=None):
        """设置主tab
        :param tab_id: 标签页id，不传入则设置当前tab
        :return: None
        """
        warn("此方法即将弃用，请用set.main_tab()方法代替。", DeprecationWarning)
        self.set.main_tab(tab_id)

    @property
    def set_window(self):
        """返回用于设置窗口大小的对象"""
        warn("此方法即将弃用，请用set.window.xxxx()方法代替。", DeprecationWarning)
        return WindowSetter(self)


class ChromiumDownloadSetter(DownloadSetter):
    """用于设置下载参数的类"""

    def __init__(self, page):
        """
        :param page: ChromiumPage对象
        """
        super().__init__(page)
        self._behavior = 'allow'
        self._download_th = None
        self._session = None
        self._waiting_download = False
        self._download_begin = False

    @property
    def session(self):
        """返回用于DownloadKit的Session对象"""
        if self._session is None:
            self._session = Session()
        return self._session

    @property
    def _switched_DownloadKit(self):
        """返回从浏览器同步cookies后的Session对象"""
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
        try:
            self._page.browser_driver.Browser.setDownloadBehavior(behavior='allow', downloadPath=path,
                                                                  eventsEnabled=True)
        except CallMethodError:
            warn('\n您的浏览器版本太低，用新标签页下载文件可能崩溃，建议升级。')
            self._page.run_cdp('Page.setDownloadBehavior', behavior='allow', downloadPath=path)

        self.DownloadKit.goal_path = path

    def by_browser(self):
        """设置使用浏览器下载文件"""
        try:
            self._page.browser_driver.Browser.setDownloadBehavior(behavior='allow', eventsEnabled=True,
                                                                  downloadPath=self._page.download_path)
            self._page.browser_driver.Browser.downloadWillBegin = self._download_by_browser
        except CallMethodError:
            self._page.driver.Page.setDownloadBehavior(behavior='allow', downloadPath=self._page.download_path)
            self._page.driver.Page.downloadWillBegin = self._download_by_browser

        self._behavior = 'allow'

    def by_DownloadKit(self):
        """设置使用DownloadKit下载文件"""
        try:
            self._page.browser_driver.Browser.setDownloadBehavior(behavior='deny', eventsEnabled=True)
            self._page.browser_driver.Browser.downloadWillBegin = self._download_by_DownloadKit
        except CallMethodError:
            raise RuntimeError('您的浏览器版本太低，不支持此方法，请升级。')
        self._behavior = 'deny'

    def wait_download_begin(self, timeout=None):
        """等待浏览器下载开始
        :param timeout: 等待超时时间，为None则使用页面对象timeout属性
        :return: 是否等到下载开始
        """
        self._waiting_download = True
        result = False
        timeout = timeout if timeout is not None else self._page.timeout
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if self._download_begin:
                result = True
                break
            sleep(.05)
        self._download_begin = False
        self._waiting_download = False
        return result

    def _cookies_to_session(self):
        """把driver对象的cookies复制到session对象"""
        ua = self._page.driver.Runtime.evaluate(expression='navigator.userAgent;')['result']['value']
        self.session.headers.update({"User-Agent": ua})
        set_session_cookies(self.session, self._page.get_cookies(as_dict=True))

    def _download_by_DownloadKit(self, **kwargs):
        """拦截浏览器下载并用downloadKit下载"""
        self._page.browser_driver.Browser.cancelDownload(guid=kwargs['guid'])
        self._page.download.add(file_url=kwargs['url'], goal_path=self._page.download_path,
                                rename=kwargs['suggestedFilename'])
        if self._download_th is None or not self._download_th.is_alive():
            self._download_th = Thread(target=self._wait_download_complete, daemon=False)
            self._download_th.start()
        if self._waiting_download:
            self._download_begin = True

    def _download_by_browser(self, **kwargs):
        """使用浏览器下载时调用"""
        if self._waiting_download:
            self._download_begin = True

    def _wait_download_complete(self):
        """等待下载完成"""
        self._page.download.wait()


class Alert(object):
    """用于保存alert信息的类"""

    def __init__(self):
        self.activated = False
        self.text = None
        self.type = None
        self.defaultPrompt = None
        self.response_accept = None
        self.response_text = None


class WindowSetter(object):
    """用于设置窗口大小的类"""

    def __init__(self, page):
        self._page = page
        self._window_id = self._get_info()['windowId']

    def maximized(self):
        """窗口最大化"""
        s = self._get_info()['bounds']['windowState']
        if s in ('fullscreen', 'minimized'):
            self._perform({'windowState': 'normal'})
        self._perform({'windowState': 'maximized'})

    def minimized(self):
        """窗口最小化"""
        s = self._get_info()['bounds']['windowState']
        if s == 'fullscreen':
            self._perform({'windowState': 'normal'})
        self._perform({'windowState': 'minimized'})

    def fullscreen(self):
        """设置窗口为全屏"""
        s = self._get_info()['bounds']['windowState']
        if s == 'minimized':
            self._perform({'windowState': 'normal'})
        self._perform({'windowState': 'fullscreen'})

    def normal(self):
        """设置窗口为常规模式"""
        s = self._get_info()['bounds']['windowState']
        if s == 'fullscreen':
            self._perform({'windowState': 'normal'})
        self._perform({'windowState': 'normal'})

    def size(self, width=None, height=None):
        """设置窗口大小
        :param width: 窗口宽度
        :param height: 窗口高度
        :return: None
        """
        if width or height:
            s = self._get_info()['bounds']['windowState']
            if s != 'normal':
                self._perform({'windowState': 'normal'})
            info = self._get_info()['bounds']
            width = width or info['width']
            height = height or info['height']
            self._perform({'width': width, 'height': height})

    def location(self, x=None, y=None):
        """设置窗口在屏幕中的位置，相对左上角坐标
        :param x: 距离顶部距离
        :param y: 距离左边距离
        :return: None
        """
        if x is not None or y is not None:
            self.normal()
            info = self._get_info()['bounds']
            x = x if x is not None else info['left']
            y = y if y is not None else info['top']
            self._perform({'left': x, 'top': y})

    def _get_info(self):
        """获取窗口位置及大小信息"""
        return self._page.run_cdp('Browser.getWindowForTarget')

    def _perform(self, bounds):
        """执行改变窗口大小操作
        :param bounds: 控制数据
        :return: None
        """
        self._page.run_cdp('Browser.setWindowBounds', windowId=self._window_id, bounds=bounds)


class ChromiumPageSetter(ChromiumBaseSetter):
    def main_tab(self, tab_id=None):
        """设置主tab
        :param tab_id: 标签页id，不传入则设置当前tab
        :return: None
        """
        self._page._main_tab = tab_id or self._page.tab_id

    @property
    def windows(self):
        """返回用于设置浏览器窗口的对象"""
        return WindowSetter(self._page)


def show_or_hide_browser(page, hide=True):
    """执行显示或隐藏浏览器窗口
    :param page: ChromePage对象
    :param hide: 是否隐藏
    :return: None
    """
    if not page.address.startswith(('localhost', '127.0.0.1')):
        return

    if system().lower() != 'windows':
        raise OSError('该方法只能在Windows系统使用。')

    try:
        from win32gui import ShowWindow
        from win32con import SW_HIDE, SW_SHOW
    except ImportError:
        raise ImportError('请先安装：pip install pypiwin32')

    pid = page.process_id or get_browser_progress_id(page.process, page.address)
    if not pid:
        return None
    hds = get_chrome_hwnds_from_pid(pid, page.title)
    sw = SW_HIDE if hide else SW_SHOW
    for hd in hds:
        ShowWindow(hd, sw)


def get_browser_progress_id(progress, address):
    """获取浏览器进程id
    :param progress: 已知的进程对象，没有时传入None
    :param address: 浏览器管理地址，含端口
    :return: 进程id或None
    """
    if progress:
        return progress.pid

    from os import popen
    port = address.split(':')[-1]
    txt = ''
    progresses = popen(f'netstat -nao | findstr :{port}').read().split('\n')
    for progress in progresses:
        if 'LISTENING' in progress:
            txt = progress
            break
    if not txt:
        return None

    return txt.split(' ')[-1]


def get_chrome_hwnds_from_pid(pid, title):
    """通过PID查询句柄ID
    :param pid: 进程id
    :param title: 窗口标题
    :return: 进程句柄组成的列表
    """
    try:
        from win32gui import IsWindow, GetWindowText, EnumWindows
        from win32process import GetWindowThreadProcessId
    except ImportError:
        raise ImportError('请先安装win32gui，pip install pypiwin32')

    def callback(hwnd, hds):
        if IsWindow(hwnd) and title in GetWindowText(hwnd):
            _, found_pid = GetWindowThreadProcessId(hwnd)
            if str(found_pid) == str(pid):
                hds.append(hwnd)
            return True

    hwnds = []
    EnumWindows(callback, hwnds)
    return hwnds
