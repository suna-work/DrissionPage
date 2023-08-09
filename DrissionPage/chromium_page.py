# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from time import perf_counter, sleep

from .chromium_base import ChromiumBase, Timeout
from .chromium_driver import ChromiumDriver
from .chromium_tab import ChromiumTab
from .commons.browser import connect_browser
from .commons.tools import port_is_using
from .configs.chromium_options import ChromiumOptions
from .errors import BrowserConnectError
from .setter import ChromiumPageSetter
from .waiter import ChromiumPageWaiter


class ChromiumPage(ChromiumBase):
    """用于管理浏览器的类"""

    def __init__(self, addr_driver_opts=None, tab_id=None, timeout=None):
        """
        :param addr_driver_opts: 浏览器地址:端口、ChromiumDriver对象或ChromiumOptions对象
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        :param timeout: 超时时间
        """
        super().__init__(addr_driver_opts, tab_id, timeout)

    def _set_start_options(self, addr_driver_opts, none):
        """设置浏览器启动属性
        :param addr_driver_opts: 'ip:port'、ChromiumOptions
        :param none: 用于后代继承
        :return: None
        """
        if not addr_driver_opts or isinstance(addr_driver_opts, ChromiumOptions):
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

        self.address = self._driver_options.debugger_address.replace('localhost',
                                                                     '127.0.0.1').lstrip('http://').lstrip('https://')

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
        self._chromium_init()

        if not self._tab_obj:  # 不是传入driver的情况
            connect_browser(self._driver_options)
            if not tab_id:
                u = f'http://{self.address}/json'
                json = self._control_session.get(u).json()
                self._control_session.get(u, headers={'Connection': 'close'})
                tab_id = [i['id'] for i in json if i['type'] == 'page']
                if not tab_id:
                    raise BrowserConnectError('浏览器连接失败，可能是浏览器版本原因。')
                tab_id = tab_id[0]

            self._driver_init(tab_id)

        self._page_init()
        self._get_document()
        self._first_run = False

    def _page_init(self):
        """页面相关设置"""
        u = f'http://{self.address}/json/version'
        ws = self._control_session.get(u).json()['webSocketDebuggerUrl']
        self._control_session.get(u, headers={'Connection': 'close'})
        self._browser_driver = ChromiumDriver(ws.split('/')[-1], 'browser', self.address)
        self._browser_driver.start()

        self._alert = Alert()
        self._tab_obj.set_listener('Page.javascriptDialogOpening', self._on_alert_open)
        self._tab_obj.set_listener('Page.javascriptDialogClosed', self._on_alert_close)

        self._rect = None
        self._main_tab = self.tab_id
        # try:
        #     self.download_set.by_browser()
        # except CDPError:
        #     pass

        self._process_id = None
        r = self.browser_driver.call_method('SystemInfo.getProcessInfo')
        if 'processInfo' not in r:
            return None
        for i in r['processInfo']:
            if i['type'] == 'browser':
                self._process_id = i['id']
                break

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
        u = f'http://{self.address}/json'
        j = self._control_session.get(u).json()  # 不要改用cdp
        self._control_session.get(u, headers={'Connection': 'close'})
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
        return self._process_id

    @property
    def set(self):
        """返回用于等待的对象"""
        if self._set is None:
            self._set = ChromiumPageSetter(self)
        return self._set

    @property
    def rect(self):
        if self._rect is None:
            self._rect = ChromiumTabRect(self)
        return self._rect

    @property
    def wait(self):
        """返回用于等待的对象"""
        if self._wait is None:
            self._wait = ChromiumPageWaiter(self)
        return self._wait

    def get_tab(self, tab_id=None):
        """获取一个标签页对象
        :param tab_id: 要获取的标签页id，为None时获取当前tab
        :return: 标签页对象
        """
        tab_id = tab_id or self.tab_id
        return ChromiumTab(self, tab_id)

    def find_tabs(self, title=None, url=None, tab_type=None, single=True):
        """查找符合条件的tab，返回它们的id组成的列表
        :param title: 要匹配title的文本
        :param url: 要匹配url的文本
        :param tab_type: tab类型，可用列表输入多个
        :param single: 是否返回首个结果的id，为False返回所有信息
        :return: tab id或tab dict
        """
        u = f'http://{self.address}/json'
        tabs = self._control_session.get(u).json()  # 不要改用cdp
        self._control_session.get(u, headers={'Connection': 'close'})
        if isinstance(tab_type, str):
            tab_type = {tab_type}
        elif isinstance(tab_type, (list, tuple, set)):
            tab_type = set(tab_type)
        elif tab_type is not None:
            raise TypeError('tab_type只能是set、list、tuple、str、None。')

        r = [i for i in tabs if ((title is None or title in i['title']) and (url is None or url in i['url'])
                                 and (tab_type is None or i['type'] in tab_type))]
        return r[0]['id'] if r and single else r

    def new_tab(self, url=None, switch_to=False):
        """新建一个标签页,该标签页在最后面
        :param url: 新标签页跳转到的网址
        :param switch_to: 新建标签页后是否把焦点移过去
        :return: 新标签页的id
        """
        if switch_to:
            begin_tabs = set(self.tabs)
            len_tabs = len(begin_tabs)
            tid = self.run_cdp('Target.createTarget', url='')['targetId']

            tabs = self.tabs
            while len(tabs) == len_tabs:
                tabs = self.tabs
                sleep(.005)

            new_tab = set(tabs) - begin_tabs
            self._to_tab(new_tab.pop(), read_doc=False)
            if url:
                self.get(url)

        elif url:
            tid = self.run_cdp('Target.createTarget', url=url)['targetId']

        else:
            tid = self.run_cdp('Target.createTarget', url='')['targetId']

        return tid

    def to_main_tab(self):
        """跳转到主标签页"""
        self.to_tab(self._main_tab)

    def to_tab(self, tab_or_id=None, activate=True):
        """跳转到标签页
        :param tab_or_id: 标签页对象或id，默认跳转到main_tab
        :param activate: 切换后是否变为活动状态
        :return: None
        """
        self._to_tab(tab_or_id, activate)

    def _to_tab(self, tab_or_id=None, activate=True, read_doc=True):
        """跳转到标签页
        :param tab_or_id: 标签页对象或id，默认跳转到main_tab
        :param activate: 切换后是否变为活动状态
        :param read_doc: 切换后是否读取文档
        :return: None
        """
        tabs = self.tabs
        if not tab_or_id:
            tab_id = self._main_tab
        elif isinstance(tab_or_id, ChromiumTab):
            tab_id = tab_or_id.tab_id
        else:
            tab_id = tab_or_id

        if tab_id not in tabs:
            tab_id = self.latest_tab

        if activate:
            self._control_session.get(f'http://{self.address}/json/activate/{tab_id}')

        if tab_id == self.tab_id:
            return

        self.driver.stop()
        self._driver_init(tab_id)
        if read_doc and self.ready_state in ('complete', None):
            self._get_document()

    def close_tabs(self, tabs_or_ids=None, others=False):
        """关闭传入的标签页，默认关闭当前页。可传入多个
        :param tabs_or_ids: 要关闭的标签页对象或id，可传入列表或元组，为None时关闭当前页
        :param others: 是否关闭指定标签页之外的
        :return: None
        """
        all_tabs = set(self.tabs)
        if isinstance(tabs_or_ids, str):
            tabs = {tabs_or_ids}
        elif isinstance(tabs_or_ids, ChromiumTab):
            tabs = {tabs_or_ids.tab_id}
        elif tabs_or_ids is None:
            tabs = {self.tab_id}
        elif isinstance(tabs_or_ids, (list, tuple)):
            tabs = set(i.tab_id if isinstance(i, ChromiumTab) else i for i in tabs_or_ids)
        else:
            raise TypeError('tabs_or_ids参数只能传入标签页对象或id。')

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

    def close_other_tabs(self, tabs_or_ids=None):
        """关闭传入的标签页以外标签页，默认保留当前页。可传入多个
        :param tabs_or_ids: 要保留的标签页对象或id，可传入列表或元组，为None时保存当前页
        :return: None
        """
        self.close_tabs(tabs_or_ids, True)

    def handle_alert(self, accept=True, send=None, timeout=None):
        """处理提示框，可以自动等待提示框出现
        :param accept: True表示确认，False表示取消，其它值不会按按钮但依然返回文本值
        :param send: 处理prompt提示框时可输入文本
        :param timeout: 等待提示框出现的超时时间，为None则使用self.timeout属性的值
        :return: 提示框内容文本，未等到提示框则返回False
        """
        timeout = self.timeout if timeout is None else timeout
        timeout = .1 if timeout <= 0 else timeout
        end_time = perf_counter() + timeout
        while not self._alert.activated and perf_counter() < end_time:
            sleep(.1)
        if not self._alert.activated:
            return False

        res_text = self._alert.text
        if self._alert.type == 'prompt':
            self.driver.call_method('Page.handleJavaScriptDialog', accept=accept, promptText=send)
        else:
            self.driver.call_method('Page.handleJavaScriptDialog', accept=accept)
        return res_text

    def quit(self):
        """关闭浏览器"""
        self._tab_obj.call_method('Browser.close')
        self._tab_obj.stop()
        ip, port = self.address.split(':')
        while port_is_using(ip, port):
            sleep(.1)

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


class ChromiumTabRect(object):
    def __init__(self, page):
        self._page = page

    @property
    def window_state(self):
        """返回窗口状态：normal、fullscreen、maximized、 minimized"""
        return self._get_browser_rect()['windowState']

    @property
    def browser_location(self):
        """返回浏览器在屏幕上的坐标，左上角为(0, 0)"""
        r = self._get_browser_rect()
        if r['windowState'] in ('maximized', 'fullscreen'):
            return 0, 0
        return r['left'] + 7, r['top']

    @property
    def page_location(self):
        """返回页面左上角在屏幕中坐标，左上角为(0, 0)"""
        w, h = self.viewport_location
        r = self._get_page_rect()['layoutViewport']
        return w - r['pageX'], h - r['pageY']

    @property
    def viewport_location(self):
        """返回视口在屏幕中坐标，左上角为(0, 0)"""
        w_bl, h_bl = self.browser_location
        w_bs, h_bs = self.browser_size
        w_vs, h_vs = self.viewport_size_with_scrollbar
        return w_bl + w_bs - w_vs, h_bl + h_bs - h_vs

    @property
    def browser_size(self):
        """返回浏览器大小"""
        r = self._get_browser_rect()
        if r['windowState'] == 'fullscreen':
            return r['width'], r['height']
        elif r['windowState'] == 'maximized':
            return r['width'] - 16, r['height'] - 16
        else:
            return r['width'] - 16, r['height'] - 7

    @property
    def page_size(self):
        """返回页面总宽高，格式：(宽, 高)"""
        r = self._get_page_rect()['contentSize']
        return r['width'], r['height']

    @property
    def viewport_size(self):
        """返回视口宽高，不包括滚动条，格式：(宽, 高)"""
        r = self._get_page_rect()['visualViewport']
        return r['clientWidth'], r['clientHeight']

    @property
    def viewport_size_with_scrollbar(self):
        """返回视口宽高，包括滚动条，格式：(宽, 高)"""
        r = self._page.run_js('return window.innerWidth.toString() + " " + window.innerHeight.toString();')
        w, h = r.split(' ')
        return int(w), int(h)

    def _get_page_rect(self):
        """获取页面范围信息"""
        return self._page.run_cdp_loaded('Page.getLayoutMetrics')

    def _get_browser_rect(self):
        """获取浏览器范围信息"""
        return self._page.browser_driver.call_method('Browser.getWindowForTarget', targetId=self._page.tab_id)['bounds']


# class BaseDownloadSetter(DownloadSetter):
#     """用于设置下载参数的类"""
#
#     def __init__(self, page):
#         """
#         :param page: ChromiumPage对象
#         """
#         super().__init__(page)
#         self._behavior = 'allowAndName'
#         self._session = None
#         self._save_path = ''
#         self._rename = None
#         self._waiting_download = False
#         self._download_begin = False
#         self._browser_missions = {}
#         self._browser_downloading_count = 0
#         self._show_msg = True
#
#     @property
#     def session(self):
#         """返回用于DownloadKit的Session对象"""
#         if self._session is None:
#             self._session = Session()
#         return self._session
#
#     @property
#     def browser_missions(self):
#         """返回浏览器下载任务"""
#         return list(self._browser_missions.values())
#
#     @property
#     def DownloadKit_missions(self):
#         """返回DownloadKit下载任务"""
#         return list(self.DownloadKit.missions.values())
#
#     @property
#     def _switched_DownloadKit(self):
#         """返回从浏览器同步cookies后的Session对象"""
#         self._cookies_to_session()
#         return self.DownloadKit
#
#     def save_path(self, path):
#         """设置下载路径
#         :param path: 下载路径
#         :return: None
#         """
#         path = path or ''
#         path = Path(path).absolute()
#         path.mkdir(parents=True, exist_ok=True)
#         path = str(path)
#         self._save_path = path
#         self._page._download_path = path
#         try:
#             self._page.browser_driver.Browser.setDownloadBehavior(behavior='allowAndName', downloadPath=path,
#                                                                   eventsEnabled=True)
#         except CDPError:
#             warn('\n您的浏览器版本太低，用新标签页下载文件可能崩溃，建议升级。')
#             self._page.run_cdp('Page.setDownloadBehavior', behavior='allowAndName', downloadPath=path)
#
#         self.DownloadKit.goal_path = path
#
#     def rename(self, name):
#         """设置浏览器下一个下载任务的文件名
#         :param name: 文件名，不带后缀时自动使用原后缀
#         :return: None
#         """
#         self._rename = name
#
#     def by_browser(self):
#         """设置使用浏览器下载文件"""
#         try:
#             self._page.browser_driver.Browser.setDownloadBehavior(behavior='allowAndName', eventsEnabled=True,
#                                                                   downloadPath=self._page.download_path)
#             self._page.browser_driver.Browser.downloadWillBegin = self._download_will_begin
#             self._page.browser_driver.Browser.downloadProgress = self._download_progress
#         except CDPError:
#             self._page.driver.Page.setDownloadBehavior(behavior='allowAndName', downloadPath=self._page.download_path)
#             self._page.driver.Page.downloadWillBegin = self._download_will_begin
#             self._page.driver.Page.downloadProgress = self._download_progress
#
#         self._behavior = 'allowAndName'
#
#     def by_DownloadKit(self):
#         """设置使用DownloadKit下载文件"""
#         try:
#             self._page.browser_driver.Browser.setDownloadBehavior(behavior='deny', eventsEnabled=True)
#             self._page.browser_driver.Browser.downloadWillBegin = self._download_by_DownloadKit
#         except CDPError:
#             raise RuntimeError('您的浏览器版本太低，不支持此方法，请升级。')
#
#         self._behavior = 'deny'
#
#     def wait_download_begin(self, timeout=None):
#         """等待浏览器下载开始
#         :param timeout: 等待超时时间，为None则使用页面对象timeout属性
#         :return: 是否等到下载开始
#         """
#         self._waiting_download = True
#         result = False
#         timeout = timeout if timeout is not None else self._page.timeout
#         end_time = perf_counter() + timeout
#         while perf_counter() < end_time:
#             if self._download_begin:
#                 result = True
#                 break
#             sleep(.05)
#         self._download_begin = False
#         self._waiting_download = False
#         return result
#
#     def wait_download_finish(self, timeout=None):
#         """等待所有下载结束
#         :param timeout: 超时时间
#         :return: 是否等待到下载完成
#         """
#         timeout = timeout if timeout is not None else self._page.timeout
#         end_time = perf_counter() + timeout
#         while perf_counter() < end_time:
#             if (self._DownloadKit is None or not self.DownloadKit.is_running) and self._browser_downloading_count == 0:
#                 return True
#             sleep(.5)
#         return False
#
#     def show_msg(self, on_off=True):
#         """是否显示下载信息
#         :param on_off: bool表示开或关
#         :return: None
#         """
#         self._show_msg = on_off
#
#     def _cookies_to_session(self):
#         """把driver对象的cookies复制到session对象"""
#         ua = self._page.run_cdp('Runtime.evaluate', expression='navigator.userAgent;')['result']['value']
#         self.session.headers.update({"User-Agent": ua})
#         set_session_cookies(self.session, self._page.get_cookies(as_dict=False, all_info=False))
#
#     def _download_by_DownloadKit(self, **kwargs):
#         """拦截浏览器下载并用downloadKit下载"""
#         url = kwargs['url']
#         if url.startswith('blob:'):
#             raise TypeError('bolb:开头的链接无法使用DownloadKit下载，请用浏览器下载功能。')
#
#         self._page.browser_driver.Browser.cancelDownload(guid=kwargs['guid'])
#
#         if self._rename:
#             rename = get_rename(kwargs['suggestedFilename'], self._rename)
#             self._rename = None
#         else:
#             rename = kwargs['suggestedFilename']
#
#         mission = self._page.download.add(file_url=url, goal_path=self._page.download_path, rename=rename)
#         Thread(target=self._wait_download_complete, args=(mission,), daemon=False).start()
#
#         if self._waiting_download:
#             self._download_begin = True
#
#         self._browser_downloading_count += 1
#
#         if self._show_msg:
#             print(f'(DownloadKit)开始下载：{Path(self._save_path) / rename}')
#
#     def _download_will_begin(self, **kwargs):
#         """浏览器下载即将开始时调用"""
#         if self._rename:
#             rename = get_rename(kwargs['suggestedFilename'], self._rename)
#             self._rename = None
#         else:
#             rename = kwargs['suggestedFilename']
#
#         m = BrowserDownloadMission(kwargs['guid'], kwargs['url'], rename)
#         self._browser_missions[kwargs['guid']] = m
#         aid_path = Path(self._save_path) / rename
#
#         if self._show_msg:
#             print(f'(Browser)开始下载：{rename}')
#         self._browser_downloading_count += 1
#
#         if self._file_exists == 'skip' and aid_path.exists():
#             m.state = 'skipped'
#             m.save_path = aid_path.absolute()
#             self._page.browser_driver.call_method('Browser.cancelDownload', guid=kwargs['guid'])
#             (Path(self._save_path) / kwargs["guid"]).unlink(missing_ok=True)
#             return
#
#         if self._waiting_download:
#             self._download_begin = True
#
#     def _download_progress(self, **kwargs):
#         """下载状态产生变化时调用"""
#         guid = kwargs['guid']
#         m = self._browser_missions.get(guid, None)
#         if m:
#             m.size = kwargs['totalBytes']
#             m.received = kwargs['receivedBytes']
#             m.state = kwargs['state']
#
#             if m.state == 'completed':
#                 path = Path(self._save_path) / m.name
#                 from_path = Path(self._save_path) / guid
#                 if path.exists():
#                     if self._file_exists == 'rename':
#                         path = get_usable_path(path)
#                     else:  # 'overwrite'
#                         path.unlink()
#                 from_path.rename(path)
#                 m.save_path = path.absolute()
#
#         if kwargs['state'] != 'inProgress':
#             if self._show_msg and m:
#                 if kwargs['state'] == 'completed':
#                     print(f'(Browser)下载完成：{m.save_path}')
#                 elif m.state != 'skipped':
#                     print(f'(Browser)下载失败：{m.save_path}')
#                 else:
#                     print(f'(Browser)已跳过：{m.save_path}')
#             self._browser_downloading_count -= 1
#
#     def _wait_download_complete(self, mission):
#         """等待DownloadKit下载完成"""
#         mission.wait(show=False)
#         if self._show_msg:
#             if mission.result == 'skip':
#                 print(f'(DownloadKit)已跳过：{mission.path}')
#             elif not mission.result:
#                 print(f'(DownloadKit)下载失败：{mission.path}')
#             else:
#                 print(f'(DownloadKit)下载完成：{mission.path}')


class BrowserDownloadMission(object):
    def __init__(self, guid, url, name):
        self.id = guid
        self.url = url
        self.name = name
        self.save_path = None
        self.state = None
        self.size = None
        self.received = None

    def __repr__(self):
        return f'<BrowserDownloadMission {self.save_path}>'


class Alert(object):
    """用于保存alert信息的类"""

    def __init__(self):
        self.activated = False
        self.text = None
        self.type = None
        self.defaultPrompt = None
        self.response_accept = None
        self.response_text = None


def get_rename(original, rename):
    if '.' in rename:
        return rename
    else:
        suffix = original[original.rfind('.'):] if '.' in original else ''
        return f'{rename}{suffix}'
