# -*- coding:utf-8 -*-
from json import loads
from re import search
from time import perf_counter, sleep
from urllib.parse import urlparse

from requests import Session

from .base import BasePage
from .chromium_element import ChromiumElementWaiter, ChromeScroll, ChromiumElement, run_script
from .common import get_loc
from .config import cookies_to_tuple
from .session_element import make_session_ele
from .tab import Tab


class ChromiumBase(BasePage):
    """标签页、frame、页面基类"""

    def __init__(self, address, tab_id=None, timeout=None):
        """初始化                                                      \n
        :param address: 浏览器 ip:port
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        :param timeout: 超时时间
        """
        super().__init__(timeout)
        self._is_loading = None
        self._root_id = None
        self._debug = False
        self._debug_recorder = None
        self.timeouts = Timeout(self)
        self._connect_browser(address, tab_id)

    def _connect_browser(self, addr_tab_opts=None, tab_id=None):
        """连接浏览器，在第一次时运行                                    \n
        :param addr_tab_opts: 浏览器地址、Tab对象或DriverOptions对象
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        :return: None
        """
        self._root_id = None
        self._control_session = Session()
        self._control_session.keep_alive = False
        self._first_run = True
        self._is_reading = False  # 用于避免不同线程重复读取document

        self.address = addr_tab_opts
        if not tab_id:
            json = self._control_session.get(f'http://{self.address}/json').json()
            tab_id = [i['id'] for i in json if i['type'] == 'page'][0]
        self._set_options()
        self._init_page(tab_id)
        self._get_document()

    def _init_page(self, tab_id=None):
        """新建页面、页面刷新、切换标签页后要进行的cdp参数初始化
        :param tab_id: 要跳转到的标签页id
        :return: None
        """
        self._is_loading = True
        if tab_id:
            self._tab_obj = Tab(id=tab_id, type='page',
                                webSocketDebuggerUrl=f'ws://{self.address}/devtools/page/{tab_id}')

        self._tab_obj.start()
        self._tab_obj.DOM.enable()
        self._tab_obj.Page.enable()

        self._tab_obj.Page.frameStoppedLoading = self._onFrameStoppedLoading
        self._tab_obj.Page.frameStartedLoading = self._onFrameStartedLoading
        self._tab_obj.DOM.documentUpdated = self._onDocumentUpdated
        self._tab_obj.Page.loadEventFired = self._onLoadEventFired
        self._tab_obj.Page.frameNavigated = self._onFrameNavigated

    def _get_document(self):
        """刷新cdp使用的document数据"""
        if not self._is_reading:
            self._is_reading = True

            if self._debug:
                print('获取document')
                if self._debug_recorder:
                    self._debug_recorder.add_data((perf_counter(), '获取document', '开始'))

            self._wait_loading()
            while True:
                try:
                    root_id = self._tab_obj.DOM.getDocument()['root']['nodeId']
                    if self._debug_recorder:
                        self._debug_recorder.add_data((perf_counter(), '信息', f'root_id：{root_id}'))
                    self._root_id = self._tab_obj.DOM.resolveNode(nodeId=root_id)['object']['objectId']
                    break
                except:
                    if self._debug_recorder:
                        self._debug_recorder.add_data((perf_counter(), 'err', '读取root_id出错'))

            if self._debug:
                print('获取document结束')
                if self._debug_recorder:
                    self._debug_recorder.add_data((perf_counter(), '获取document', '结束'))

            self._is_loading = False
            self._is_reading = False

    def _wait_loading(self, timeout=None):
        """等待页面加载完成
        :param timeout: 超时时间
        :return: 是否成功，超时返回False
        """
        timeout = timeout if timeout is not None else self.timeouts.page_load

        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            state = self.ready_state

            if self._debug_recorder:
                self._debug_recorder.add_data((perf_counter(), 'waiting', state))

            if state == 'complete':
                return True
            elif self.page_load_strategy == 'eager' and state in ('interactive', 'complete'):
                self.stop_loading()
                return True
            elif self.page_load_strategy == 'none':
                self.stop_loading()
                return True
            sleep(.1)

        self.stop_loading()
        return False

    def _onFrameStartedLoading(self, **kwargs):
        """页面开始加载时触发"""
        if kwargs['frameId'] == self.tab_id:
            self._is_loading = True

            if self._debug:
                print('页面开始加载 FrameStartedLoading')
                if self._debug_recorder:
                    self._debug_recorder.add_data((perf_counter(), '加载流程', 'FrameStartedLoading'))

    def _onFrameStoppedLoading(self, **kwargs):
        """页面加载完成后触发"""
        if kwargs['frameId'] == self.tab_id and self._first_run is False and self._is_loading:
            if self._debug:
                print('页面停止加载 FrameStoppedLoading')
                if self._debug_recorder:
                    self._debug_recorder.add_data((perf_counter(), '加载流程', 'FrameStoppedLoading'))

            self._get_document()

    def _onLoadEventFired(self, **kwargs):
        """在页面刷新、变化后重新读取页面内容"""
        if self._debug:
            print('loadEventFired')
            if self._debug_recorder:
                self._debug_recorder.add_data((perf_counter(), '加载流程', 'loadEventFired'))

    def _onDocumentUpdated(self, **kwargs):
        """页面跳转时触发"""
        if self._debug:
            print('documentUpdated')
            if self._debug_recorder:
                self._debug_recorder.add_data((perf_counter(), '加载流程', 'documentUpdated'))

    def _onFrameNavigated(self, **kwargs):
        """页面跳转时触发"""
        if self._debug and not kwargs['frame'].get('parentId', None):
            print('navigated')
            if self._debug_recorder:
                self._debug_recorder.add_data((perf_counter(), '加载流程', 'navigated'))

    def _set_options(self):
        pass

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素                                              \n
        例：ele = page('@id=ele_id')                                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: ChromiumElement对象
        """
        return self.ele(loc_or_str, timeout)

    @property
    def title(self):
        """返回当前页面title"""
        return self._tab_obj.Target.getTargetInfo(targetId=self.tab_id)['targetInfo']['title']

    @property
    def driver(self):
        """返回用于控制浏览器的Tab对象"""
        return self._tab_obj

    @property
    def _driver(self):
        return self._tab_obj

    @property
    def _wait_driver(self):
        """返回用于控制浏览器的Tab对象，会先等待页面加载完毕"""
        while self._is_loading:
            sleep(.1)
        return self._tab_obj

    @property
    def is_loading(self):
        """返回页面是否正在加载状态"""
        return self._is_loading

    @property
    def url(self):
        """返回当前页面url"""
        return self._tab_obj.Target.getTargetInfo(targetId=self.tab_id)['targetInfo']['url']

    @property
    def html(self):
        """返回当前页面html文本"""
        return self._wait_driver.DOM.getOuterHTML(objectId=self._root_id)['outerHTML']

    @property
    def json(self):
        """当返回内容是json格式时，返回对应的字典"""
        return loads(self('t:pre').text)

    @property
    def tab_id(self):
        """返回当前标签页id"""
        return self.driver.id if self.driver.status == 'started' else ''

    @property
    def ready_state(self):
        """返回当前页面加载状态，'loading' 'interactive' 'complete'"""
        return self._tab_obj.Runtime.evaluate(expression='document.readyState;')['result']['value']

    @property
    def size(self):
        """返回页面总长宽，{'height': int, 'width': int}"""
        w = self.run_script('document.body.scrollWidth;', as_expr=True)
        h = self.run_script('document.body.scrollHeight;', as_expr=True)
        return {'height': h, 'width': w}

    @property
    def active_ele(self):
        """返回当前焦点所在元素"""
        return self.run_script('return document.activeElement;')

    @property
    def page_load_strategy(self):
        """返回页面加载策略"""
        return self._page_load_strategy

    @property
    def scroll(self):
        """返回用于滚动滚动条的对象"""
        if not hasattr(self, '_scroll'):
            self._scroll = ChromeScroll(self)
        return self._scroll

    @property
    def set_page_load_strategy(self):
        """返回用于设置页面加载策略的对象"""
        return PageLoadStrategy(self)

    def set_timeouts(self, implicit=None, page_load=None, script=None):
        """设置超时时间，单位为秒                   \n
        :param implicit: 查找元素超时时间
        :param page_load: 页面加载超时时间
        :param script: 脚本运行超时时间
        :return: None
        """
        if implicit is not None:
            self.timeout = implicit

        if page_load is not None:
            self.timeouts.page_load = page_load

        if script is not None:
            self.timeouts.script = script

    def run_script(self, script, as_expr=False, *args):
        """运行javascript代码                                                 \n
        :param script: js文本
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param args: 参数，按顺序在js文本中对应argument[0]、argument[2]...
        :return: 运行的结果
        """
        return run_script(self, script, as_expr, self.timeouts.script, args)

    def run_async_script(self, script, as_expr=False, *args):
        """以异步方式执行js代码                                                 \n
        :param script: js文本
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param args: 参数，按顺序在js文本中对应argument[0]、argument[2]...
        :return: None
        """
        from threading import Thread
        Thread(target=run_script, args=(self, script, as_expr, self.timeouts.script, args)).start()

    def get(self, url, show_errmsg=False, retry=None, interval=None, timeout=None):
        """访问url                                            \n
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param timeout: 连接超时时间
        :return: 目标url是否可用
        """
        self._url_available = self._get(url, show_errmsg, retry, interval, timeout)
        return self._url_available

    def _get(self, url: str, show_errmsg=False, retry=None, interval=None, timeout=None, frame_id=None):
        """访问url                                            \n
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param timeout: 连接超时时间
        :return: 目标url是否可用，返回None表示不确定
        """
        retry, interval = self._before_connect(url, retry, interval)
        return self._d_connect(self._url,
                               times=retry,
                               interval=interval,
                               show_errmsg=show_errmsg,
                               timeout=timeout,
                               frame_id=frame_id)

    def get_cookies(self, as_dict=False):
        """获取cookies信息                                              \n
        :param as_dict: 为True时返回由{name: value}键值对组成的dict
        :return: cookies信息
        """
        cookies = self._wait_driver.Network.getCookies()['cookies']
        if as_dict:
            return {cookie['name']: cookie['value'] for cookie in cookies}
        else:
            return cookies

    def set_cookies(self, cookies):
        """设置cookies值                            \n
        :param cookies: cookies信息
        :return: None
        """
        cookies = cookies_to_tuple(cookies)
        result_cookies = []
        for cookie in cookies:
            if not cookie.get('domain', None):
                continue
            c = {'value': '' if cookie['value'] is None else cookie['value'],
                 'name': cookie['name'],
                 'domain': cookie['domain']}
            result_cookies.append(c)
        self._wait_driver.Network.setCookies(cookies=result_cookies)

    # def set_headers(self, headers: dict) -> None:
    #     """设置固定发送的headers                        \n
    #     :param headers: dict格式的headers数据
    #     :return: None
    #     """
    #     self.run_cdp('Network.setExtraHTTPHeaders', headers=headers)

    def ele(self, loc_or_ele, timeout=None):
        """获取第一个符合条件的元素对象                       \n
        :param loc_or_ele: 定位符或元素对象
        :param timeout: 查找超时时间
        :return: ChromiumElement对象
        """
        return self._ele(loc_or_ele, timeout=timeout)

    def eles(self, loc_or_str, timeout=None):
        """获取所有符合条件的元素对象                         \n
        :param loc_or_str: 定位符或元素对象
        :param timeout: 查找超时时间
        :return: ChromiumElement对象组成的列表
        """
        return self._ele(loc_or_str, timeout=timeout, single=False)

    def s_ele(self, loc_or_ele=None):
        """查找第一个符合条件的元素以SessionElement形式返回，处理复杂页面时效率很高       \n
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        if isinstance(loc_or_ele, ChromiumElement):
            return make_session_ele(loc_or_ele)
        else:
            return make_session_ele(self, loc_or_ele)

    def s_eles(self, loc_or_str=None):
        """查找所有符合条件的元素以SessionElement列表形式返回                       \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象组成的列表
        """
        return make_session_ele(self, loc_or_str, single=False)

    def _ele(self, loc_or_ele, timeout=None, single=True, relative=False):
        """执行元素查找
        :param loc_or_ele: 定位符或元素对象
        :param timeout: 查找超时时间
        :param single: 是否只返回第一个
        :return: ChromiumElement对象或元素对象组成的列表
        """
        if isinstance(loc_or_ele, (str, tuple)):
            loc = get_loc(loc_or_ele)[1]
        elif isinstance(loc_or_ele, ChromiumElement):
            return loc_or_ele
        else:
            raise ValueError('loc_or_str参数只能是tuple、str、ChromiumElement类型。')

        timeout = timeout if timeout is not None else self.timeout
        search_result = self._wait_driver.DOM.performSearch(query=loc, includeUserAgentShadowDOM=True)
        count = search_result['resultCount']

        end_time = perf_counter() + timeout
        while count == 0 and perf_counter() < end_time:
            search_result = self._wait_driver.DOM.performSearch(query=loc, includeUserAgentShadowDOM=True)
            count = search_result['resultCount']

        if count == 0:
            return None if single else []

        count = 1 if single else count
        nodeIds = self._wait_driver.DOM.getSearchResults(searchId=search_result['searchId'], fromIndex=0,
                                                         toIndex=count)
        eles = []
        for i in nodeIds['nodeIds']:
            ele = ChromiumElement(self, node_id=i)
            if ele.tag in ('iframe', 'frame'):
                src = ele.attr('src')
                if src:
                    netloc1 = urlparse(src).netloc
                    netloc2 = urlparse(self.url).netloc
                    if netloc1 != netloc2:
                        ele = ChromiumFrame(self, ele)
            eles.append(ele)

        return eles[0] if single else eles

    def wait_ele(self, loc_or_ele, timeout=None):
        """返回用于等待元素到达某个状态的等待器对象                             \n
        :param loc_or_ele: 可以是元素、查询字符串、loc元组
        :param timeout: 等待超时时间
        :return: 用于等待的ElementWaiter对象
        """
        return ChromiumElementWaiter(self, loc_or_ele, timeout)

    def scroll_to_see(self, loc_or_ele):
        """滚动页面直到元素可见                                                        \n
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串（详见ele函数注释）
        :return: None
        """
        node_id = self.ele(loc_or_ele).node_id
        try:
            self._wait_driver.DOM.scrollIntoViewIfNeeded(nodeId=node_id)
        except Exception:
            self.ele(loc_or_ele).run_script("this.scrollIntoView();")

    def refresh(self, ignore_cache=False):
        """刷新当前页面                      \n
        :param ignore_cache: 是否忽略缓存
        :return: None
        """
        self._is_loading = True
        self._driver.Page.reload(ignoreCache=ignore_cache)

    def forward(self, steps=1):
        """在浏览历史中前进若干步    \n
        :param steps: 前进步数
        :return: None
        """
        self._forward_or_back(steps)

    def back(self, steps=1):
        """在浏览历史中后退若干步    \n
        :param steps: 后退步数
        :return: None
        """
        self._forward_or_back(-steps)

    def _forward_or_back(self, steps):
        """执行浏览器前进或后退，会跳过url相同的历史记录
        :param steps: 步数
        :return: None
        """
        if steps == 0:
            return

        history = self.run_cdp('Page.getNavigationHistory')
        index = history['currentIndex']
        history = history['entries']
        direction = 1 if steps > 0 else -1
        curr_url = history[index]['userTypedURL']
        nid = None
        for num in range(abs(steps)):
            for i in history[index::direction]:
                index += direction
                if i['userTypedURL'] != curr_url:
                    nid = i['id']
                    curr_url = i['userTypedURL']
                    break

        if nid:
            self._is_loading = True
            self.run_cdp('Page.navigateToHistoryEntry', entryId=nid)

    def stop_loading(self):
        """页面停止加载"""
        if self._debug:
            print('停止页面加载')
            if self._debug_recorder:
                self._debug_recorder.add_data((perf_counter(), '操作', '停止页面加载'))

        self._tab_obj.Page.stopLoading()
        while self.ready_state != 'complete':
            sleep(.1)
        # self._get_document()

    def run_cdp(self, cmd, **cmd_args):
        """执行Chrome DevTools Protocol语句     \n
        :param cmd: 协议项目
        :param cmd_args: 参数
        :return: 执行的结果
        """
        try:
            return self._driver.call_method(cmd, **cmd_args)
        except Exception as e:
            if 'Could not find node with given id' in str(e):
                raise RuntimeError('该元素已不在当前页面中。')
            raise

    def set_user_agent(self, ua):
        """为当前tab设置user agent，只在当前tab有效          \n
        :param ua: user agent字符串
        :return: None
        """
        self._wait_driver.Network.setUserAgentOverride(userAgent=ua)

    def get_session_storage(self, item=None):
        """获取sessionStorage信息，不设置item则获取全部       \n
        :param item: 要获取的项，不设置则返回全部
        :return: sessionStorage一个或所有项内容
        """
        js = f'sessionStorage.getItem("{item}");' if item else 'sessionStorage;'
        return self.run_script(js, as_expr=True)

    def get_local_storage(self, item=None):
        """获取localStorage信息，不设置item则获取全部       \n
        :param item: 要获取的项目，不设置则返回全部
        :return: localStorage一个或所有项内容
        """
        js = f'localStorage.getItem("{item}");' if item else 'localStorage;'
        return self.run_script(js, as_expr=True)

    def set_session_storage(self, item, value):
        """设置或删除某项sessionStorage信息                         \n
        :param item: 要设置的项
        :param value: 项的值，设置为False时，删除该项
        :return: None
        """
        js = f'sessionStorage.removeItem("{item}");' if item is False else f'sessionStorage.setItem("{item}","{value}");'
        return self.run_script(js, as_expr=True)

    def set_local_storage(self, item, value):
        """设置或删除某项localStorage信息                           \n
        :param item: 要设置的项
        :param value: 项的值，设置为False时，删除该项
        :return: None
        """
        js = f'localStorage.removeItem("{item}");' if item is False else f'localStorage.setItem("{item}","{value}");'
        return self.run_script(js, as_expr=True)

    def clear_cache(self, session_storage=True, local_storage=True, cache=True, cookies=True):
        """清除缓存，可选要清除的项                            \n
        :param session_storage: 是否清除sessionStorage
        :param local_storage: 是否清除localStorage
        :param cache: 是否清除cache
        :param cookies: 是否清除cookies
        :return: None
        """
        if session_storage:
            self.run_script('sessionStorage.clear();', as_expr=True)
        if local_storage:
            self.run_script('localStorage.clear();', as_expr=True)
        if cache:
            self._wait_driver.Network.clearBrowserCache()
        if cookies:
            self._wait_driver.Network.clearBrowserCookies()

    def _d_connect(self, to_url, times=0, interval=1, show_errmsg=False, timeout=None, frame_id=None):
        """尝试连接，重试若干次                            \n
        :param to_url: 要访问的url
        :param times: 重试次数
        :param interval: 重试间隔（秒）
        :param show_errmsg: 是否抛出异常
        :param timeout: 连接超时时间
        :return: 是否成功，返回None表示不确定
        """
        err = None
        timeout = timeout if timeout is not None else self.timeouts.page_load

        for _ in range(times + 1):
            err = None
            if frame_id:
                result = self._driver.Page.navigate(url=to_url, frameId=frame_id)
            else:
                result = self._driver.Page.navigate(url=to_url)

            is_timeout = not self._wait_loading(timeout)
            while self.is_loading:
                sleep(.1)

            if is_timeout:
                err = TimeoutError('页面连接超时。')
            if 'errorText' in result:
                err = ConnectionError(result['errorText'])

            if not err:
                break

            if _ < times:
                sleep(interval)
                while self.ready_state != 'complete':
                    sleep(.1)
                if self._debug:
                    print('重试')
                if show_errmsg:
                    print(f'重试 {to_url}')

        if err:
            if show_errmsg:
                raise err if err is not None else ConnectionError('连接异常。')
            return False

        return True


class ChromiumFrame(ChromiumBase):
    """实现浏览器frame的类"""

    def __init__(self, page, ele):
        """初始化                                                      \n
        :param page: 页面对象
        :param ele: 页面上的frame元素
        """
        self.page = page
        self._inner_ele = ele
        frame_id = page.run_cdp('DOM.describeNode', nodeId=ele.node_id)['node'].get('frameId', None)
        super().__init__(page.address, frame_id, page.timeout)

    def __repr__(self):
        attrs = self.attrs
        attrs = [f"{attr}='{attrs[attr]}'" for attr in attrs]
        return f'<ChromiumFrame {self.tag} {" ".join(attrs)}>'

    @property
    def tag(self):
        """返回元素tag"""
        return self._inner_ele.tag

    @property
    def html(self):
        """返回元素outerHTML文本"""
        tag = self.tag
        out_html = self.page.run_cdp('DOM.getOuterHTML', nodeId=self._inner_ele.node_id)['outerHTML']
        in_html = super().html
        sign = search(rf'<{tag}.*?>', out_html).group(0)
        return f'{sign}{in_html}</{tag}>'

    @property
    def inner_html(self):
        """返回元素innerHTML文本"""
        return super().html

    @property
    def attrs(self):
        return self._inner_ele.attrs

    @property
    def frame_size(self):
        """返回frame元素大小"""
        return self._inner_ele.size

    def _set_options(self):
        self.set_timeouts(page_load=self.page.timeouts.page_load,
                          script=self.page.timeouts.script,
                          implicit=self.page.timeouts.implicit if self.timeout is None else self.timeout)
        self._page_load_strategy = self.page.page_load_strategy

    @property
    def obj_id(self):
        """返回js中的object id"""
        return self._inner_ele.obj_id

    @property
    def node_id(self):
        """返回cdp中的node id"""
        return self._inner_ele.node_id

    @property
    def location(self):
        """返回frame元素左上角的绝对坐标"""
        return self._inner_ele.location

    @property
    def is_displayed(self):
        """返回frame元素是否显示"""
        return self._inner_ele.is_displayed

    def attr(self, attr):
        """返回frame元素attribute属性值                           \n
        :param attr: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        return self._inner_ele.attr(attr)

    def set_attr(self, attr, value):
        """设置frame元素attribute属性          \n
        :param attr: 属性名
        :param value: 属性值
        :return: None
        """
        self._inner_ele.set_attr(attr, value)

    def remove_attr(self, attr):
        """删除frame元素attribute属性          \n
        :param attr: 属性名
        :return: None
        """
        self._inner_ele.remove_attr(attr)

    def parent(self, level_or_loc=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位              \n
        :param level_or_loc: 第几级父元素，或定位符
        :return: 上级元素对象
        """
        return self._inner_ele.parent(level_or_loc)

    def prev(self, filter_loc='', index=1, timeout=0):
        """返回前面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 前面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素
        """
        return self._inner_ele.prev(filter_loc, index, timeout)

    def next(self, filter_loc='', index=1, timeout=0):
        """返回后面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 后面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素
        """
        return self._inner_ele.next(filter_loc, index, timeout)

    def before(self, filter_loc='', index=1, timeout=None):
        """返回当前元素前面的一个元素，可指定筛选条件和第几个。查找范围不限兄弟元素，而是整个DOM文档        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 前面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 本元素前面的某个元素或节点
        """
        return self._inner_ele.before(filter_loc, index, timeout)

    def after(self, filter_loc='', index=1, timeout=None):
        """返回当前元素后面的一个元素，可指定筛选条件和第几个。查找范围不限兄弟元素，而是整个DOM文档        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 后面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 本元素后面的某个元素或节点
        """
        return self._inner_ele.after(filter_loc, index, timeout)

    def prevs(self, filter_loc='', timeout=0):
        """返回前面全部兄弟元素或节点组成的列表，可用查询语法筛选        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素或节点文本组成的列表
        """
        return self._inner_ele.prevs(filter_loc, timeout)

    def nexts(self, filter_loc='', timeout=0):
        """返回后面全部兄弟元素或节点组成的列表，可用查询语法筛选        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素或节点文本组成的列表
        """
        return self._inner_ele.nexts(filter_loc, timeout)

    def befores(self, filter_loc='', timeout=None):
        """返回当前元素后面符合条件的全部兄弟元素或节点组成的列表，可用查询语法筛选。查找范围不限兄弟元素，而是整个DOM文档        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 本元素前面的元素或节点组成的列表
        """
        return self._inner_ele.befores(filter_loc, timeout)


class Timeout(object):
    """用于保存d模式timeout信息的类"""

    def __init__(self, page):
        self.page = page
        self.page_load = 30
        self.script = 30

    @property
    def implicit(self):
        return self.page.timeout


class PageLoadStrategy(object):
    """用于设置页面加载策略的类"""

    def __init__(self, page):
        """
        :param page: ChromiumBase对象
        """
        self.page = page

    def __call__(self, value):
        """设置加载策略                                  \n
        :param value: 可选 'normal', 'eager', 'none'
        :return: None
        """
        if value.lower() not in ('normal', 'eager', 'none'):
            raise ValueError("只能选择 'normal', 'eager', 'none'。")
        self.page._page_load_strategy = value

    def normal(self):
        """设置页面加载策略为normal"""
        self.page._page_load_strategy = 'normal'

    def eager(self):
        """设置页面加载策略为eager"""
        self.page._page_load_strategy = 'eager'

    def none(self):
        """设置页面加载策略为none"""
        self.page._page_load_strategy = 'none'
