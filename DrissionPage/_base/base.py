# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from abc import abstractmethod
from re import sub
from urllib.parse import quote

from DownloadKit import DownloadKit

from .._commons.settings import Settings
from .._commons.locator import get_loc
from .._commons.web import format_html
from .._elements.none_element import NoneElement
from ..errors import ElementNotFoundError


class BaseParser(object):
    """所有页面、元素类的基类"""

    def __call__(self, loc_or_str):
        return self.ele(loc_or_str)

    def ele(self, loc_or_ele, timeout=None):
        return self._ele(loc_or_ele, timeout, True, method='ele()')

    def eles(self, loc_or_str, timeout=None):
        return self._ele(loc_or_str, timeout, False)

    # ----------------以下属性或方法待后代实现----------------
    @property
    def html(self):
        return ''

    def s_ele(self, loc_or_ele):
        pass

    def s_eles(self, loc_or_str):
        pass

    def _ele(self, loc_or_ele, timeout=None, single=True, raise_err=None, method=None):
        pass

    @abstractmethod
    def _find_elements(self, loc_or_ele, timeout=None, single=True, raise_err=None):
        pass


class BaseElement(BaseParser):
    """各元素类的基类"""

    def __init__(self, page=None):
        self.page = page

    # ----------------以下属性或方法由后代实现----------------
    @property
    def tag(self):
        return

    def parent(self, level_or_loc=1):
        pass

    def next(self, index=1):
        pass

    def nexts(self):
        pass

    def _ele(self, loc_or_str, timeout=None, single=True, relative=False, raise_err=None, method=None):
        r = self._find_elements(loc_or_str, timeout=timeout, single=single, relative=relative, raise_err=raise_err)
        if not single:
            return r
        if isinstance(r, NoneElement):
            if Settings.raise_when_ele_not_found or raise_err is True:
                raise ElementNotFoundError(None, method, {'loc_or_str': loc_or_str})
            else:
                r.method = method
                r.args = {'loc_or_str': loc_or_str}
        return r

    @abstractmethod
    def _find_elements(self, loc_or_str, timeout=None, single=True, relative=False, raise_err=None):
        pass


class DrissionElement(BaseElement):
    """ChromiumElement 和 SessionElement的基类
    但不是ShadowRootElement的基类"""

    @property
    def link(self):
        """返回href或src绝对url"""
        return self.attr('href') or self.attr('src')

    @property
    def css_path(self):
        """返回css path路径"""
        return self._get_ele_path('css')

    @property
    def xpath(self):
        """返回xpath路径"""
        return self._get_ele_path('xpath')

    @property
    def comments(self):
        """返回元素注释文本组成的列表"""
        return self.eles('xpath:.//comment()')

    def texts(self, text_node_only=False):
        """返回元素内所有直接子节点的文本，包括元素和文本节点
        :param text_node_only: 是否只返回文本节点
        :return: 文本列表
        """
        if text_node_only:
            texts = self.eles('xpath:/text()')
        else:
            texts = [x if isinstance(x, str) else x.text for x in self.eles('xpath:./text() | *')]

        return [format_html(x.strip(' ').rstrip('\n')) for x in texts if x and sub('[\r\n\t ]', '', x) != '']

    def parent(self, level_or_loc=1, index=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，或定位符
        :param index: 当level_or_loc传入定位符，使用此参数选择第几个结果
        :return: 上级元素对象
        """
        if isinstance(level_or_loc, int):
            loc = f'xpath:./ancestor::*[{level_or_loc}]'

        elif isinstance(level_or_loc, (tuple, str)):
            loc = get_loc(level_or_loc, True)

            if loc[0] == 'css selector':
                raise ValueError('此css selector语法不受支持，请换成xpath。')

            loc = f'xpath:./ancestor::{loc[1].lstrip(". / ")}[{index}]'

        else:
            raise TypeError('level_or_loc参数只能是tuple、int或str。')

        return self._ele(loc, timeout=0, relative=True, raise_err=False, method='parent()')

    def child(self, filter_loc='', index=1, timeout=None, ele_only=True):
        """返回直接子元素元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本组成的列表
        """
        if isinstance(filter_loc, int):
            index = filter_loc
            filter_loc = ''
        nodes = self.children(filter_loc=filter_loc, timeout=timeout, ele_only=ele_only)
        if not nodes:
            if Settings.raise_when_ele_not_found:
                raise ElementNotFoundError(None, 'child()', {'filter_loc': filter_loc,
                                                             'index': index, 'ele_only': ele_only})
            else:
                return NoneElement(self.page, 'child()', {'filter_loc': filter_loc,
                                                          'index': index, 'ele_only': ele_only})

        try:
            return nodes[index - 1]
        except IndexError:
            if Settings.raise_when_ele_not_found:
                raise ElementNotFoundError(None, 'child()', {'filter_loc': filter_loc,
                                                             'index': index, 'ele_only': ele_only})
            else:
                return NoneElement(self.page, 'child()', {'filter_loc': filter_loc,
                                                          'index': index, 'ele_only': ele_only})

    def prev(self, filter_loc='', index=1, timeout=0, ele_only=True):
        """返回前面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param filter_loc: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素
        """
        if isinstance(filter_loc, int):
            index = filter_loc
            filter_loc = ''
        nodes = self._get_brothers(index, filter_loc, 'preceding', timeout=timeout, ele_only=ele_only)
        if nodes:
            return nodes[-1]
        if Settings.raise_when_ele_not_found:
            raise ElementNotFoundError(None, 'prev()', {'filter_loc': filter_loc,
                                                        'index': index, 'ele_only': ele_only})
        else:
            return NoneElement(self.page, 'prev()', {'filter_loc': filter_loc, 'index': index, 'ele_only': ele_only})

    def next(self, filter_loc='', index=1, timeout=0, ele_only=True):
        """返回后面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param filter_loc: 用于筛选的查询语法
        :param index: 后面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素
        """
        if isinstance(filter_loc, int):
            index = filter_loc
            filter_loc = ''
        nodes = self._get_brothers(index, filter_loc, 'following', timeout=timeout, ele_only=ele_only)
        if nodes:
            return nodes[0]
        if Settings.raise_when_ele_not_found:
            raise ElementNotFoundError(None, 'next()', {'filter_loc': filter_loc,
                                                        'index': index, 'ele_only': ele_only})
        else:
            return NoneElement(self.page, 'next()', {'filter_loc': filter_loc, 'index': index, 'ele_only': ele_only})

    def before(self, filter_loc='', index=1, timeout=None, ele_only=True):
        """返回前面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param filter_loc: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的某个元素或节点
        """
        if isinstance(filter_loc, int):
            index = filter_loc
            filter_loc = ''
        nodes = self._get_brothers(index, filter_loc, 'preceding', False, timeout=timeout, ele_only=ele_only)
        if nodes:
            return nodes[-1]
        if Settings.raise_when_ele_not_found:
            raise ElementNotFoundError(None, 'before()', {'filter_loc': filter_loc,
                                                          'index': index, 'ele_only': ele_only})
        else:
            return NoneElement(self.page, 'before()', {'filter_loc': filter_loc, 'index': index, 'ele_only': ele_only})

    def after(self, filter_loc='', index=1, timeout=None, ele_only=True):
        """返回后面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param filter_loc: 用于筛选的查询语法
        :param index: 后面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的某个元素或节点
        """
        if isinstance(filter_loc, int):
            index = filter_loc
            filter_loc = ''
        nodes = self._get_brothers(index, filter_loc, 'following', False, timeout, ele_only=ele_only)
        if nodes:
            return nodes[0]
        if Settings.raise_when_ele_not_found:
            raise ElementNotFoundError(None, 'after()', {'filter_loc': filter_loc,
                                                         'index': index, 'ele_only': ele_only})
        else:
            return NoneElement(self.page, 'after()', {'filter_loc': filter_loc, 'index': index, 'ele_only': ele_only})

    def children(self, filter_loc='', timeout=None, ele_only=True):
        """返回直接子元素元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本组成的列表
        """
        if not filter_loc:
            loc = '*' if ele_only else 'node()'
        else:
            loc = get_loc(filter_loc, True)  # 把定位符转换为xpath
            if loc[0] == 'css selector':
                raise ValueError('此css selector语法不受支持，请换成xpath。')
            loc = loc[1].lstrip('./')

        loc = f'xpath:./{loc}'
        nodes = self._ele(loc, timeout=timeout, single=False, relative=True)
        return [e for e in nodes if not (isinstance(e, str) and sub('[ \n\t\r]', '', e) == '')]

    def prevs(self, filter_loc='', timeout=0, ele_only=True):
        """返回前面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本组成的列表
        """
        return self._get_brothers(filter_loc=filter_loc, direction='preceding', timeout=timeout, ele_only=ele_only)

    def nexts(self, filter_loc='', timeout=0, ele_only=True):
        """返回后面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本组成的列表
        """
        return self._get_brothers(filter_loc=filter_loc, direction='following', timeout=timeout, ele_only=ele_only)

    def befores(self, filter_loc='', timeout=None, ele_only=True):
        """返回后面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的元素或节点组成的列表
        """
        return self._get_brothers(filter_loc=filter_loc, direction='preceding',
                                  brother=False, timeout=timeout, ele_only=ele_only)

    def afters(self, filter_loc='', timeout=None, ele_only=True):
        """返回前面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的元素或节点组成的列表
        """
        return self._get_brothers(filter_loc=filter_loc, direction='following',
                                  brother=False, timeout=timeout, ele_only=ele_only)

    def _get_brothers(self, index=None, filter_loc='', direction='following',
                      brother=True, timeout=.5, ele_only=True):
        """按要求返回兄弟元素或节点组成的列表
        :param index: 获取第几个，该参数不为None时只获取该编号的元素
        :param filter_loc: 用于筛选的查询语法
        :param direction: 'following' 或 'preceding'，查找的方向
        :param brother: 查找范围，在同级查找还是整个dom前后查找
        :param timeout: 查找等待时间
        :return: 元素对象或字符串
        """
        if index is not None and index < 1:
            raise ValueError('index必须大于等于1。')

        brother = '-sibling' if brother else ''

        if not filter_loc:
            loc = '*' if ele_only else 'node()'

        else:
            loc = get_loc(filter_loc, True)  # 把定位符转换为xpath
            if loc[0] == 'css selector':
                raise ValueError('此css selector语法不受支持，请换成xpath。')
            loc = loc[1].lstrip('./')

        loc = f'xpath:./{direction}{brother}::{loc}'

        nodes = self._ele(loc, timeout=timeout, single=False, relative=True)
        nodes = [e for e in nodes if not (isinstance(e, str) and sub('[ \n\t\r]', '', e) == '')]

        if nodes and index is not None:
            index = index - 1 if direction == 'following' else -index
            try:
                return [nodes[index]]
            except IndexError:
                return []
        else:
            return nodes

    # ----------------以下属性或方法由后代实现----------------
    @property
    def attrs(self):
        return

    @property
    def text(self):
        return

    @property
    def raw_text(self):
        return

    @abstractmethod
    def attr(self, attr: str):
        return ''

    def _get_ele_path(self, mode):
        return ''


class BasePage(BaseParser):
    """页面类的基类"""

    def __init__(self):
        """初始化函数"""
        self._url = None
        self._timeout = 10
        self._url_available = None
        self.retry_times = 3
        self.retry_interval = 2
        self._DownloadKit = None
        self._download_path = None
        self._none_ele_return_value = False
        self._none_ele_value = None

    @property
    def title(self):
        """返回网页title"""
        ele = self._ele('xpath://title', raise_err=False, method='title')
        return ele.text if ele else None

    @property
    def timeout(self):
        """返回查找元素时等待的秒数"""
        return self._timeout

    @timeout.setter
    def timeout(self, second):
        """设置查找元素时等待的秒数"""
        self._timeout = second

    @property
    def cookies(self):
        """返回cookies"""
        return self.get_cookies(True)

    @property
    def url_available(self):
        """返回当前访问的url有效性"""
        return self._url_available

    @property
    def download_path(self):
        """返回默认下载路径"""
        return self._download_path

    @property
    def download(self):
        """返回下载器对象"""
        if self._DownloadKit is None:
            self._DownloadKit = DownloadKit(driver=self, goal_path=self.download_path)
        return self._DownloadKit

    def _before_connect(self, url, retry, interval):
        """连接前的准备
        :param url: 要访问的url
        :param retry: 重试次数
        :param interval: 重试间隔
        :return: 重试次数和间隔组成的tuple
        """
        self._url = quote(url, safe='-_.~!*\'"();:@&=+$,/\\?#[]%')
        retry = retry if retry is not None else self.retry_times
        interval = interval if interval is not None else self.retry_interval
        return retry, interval

    # ----------------以下属性或方法由后代实现----------------
    @property
    def url(self):
        return

    @property
    def json(self):
        return

    @property
    def user_agent(self):
        return

    @abstractmethod
    def get_cookies(self, as_dict=False, all_info=False):
        return {}

    @abstractmethod
    def get(self, url, show_errmsg=False, retry=None, interval=None):
        pass

    def _ele(self, loc_or_ele, timeout=None, single=True, raise_err=None, method=None):
        if not loc_or_ele:
            raise ElementNotFoundError(None, method, {'loc_or_str': loc_or_ele})

        r = self._find_elements(loc_or_ele, timeout=timeout, single=single, raise_err=raise_err)

        if not single:
            return r
        if isinstance(r, NoneElement):
            if Settings.raise_when_ele_not_found or raise_err is True:
                raise ElementNotFoundError(None, method, {'loc_or_str': loc_or_ele})
            else:
                r.method = method
                r.args = {'loc_or_str': loc_or_ele}
        return r

    @abstractmethod
    def _find_elements(self, loc_or_ele, timeout=None, single=True, raise_err=None):
        pass
