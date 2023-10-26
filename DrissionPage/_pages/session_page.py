# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from re import search
from time import sleep
from urllib.parse import urlparse

from requests import Session
from requests.structures import CaseInsensitiveDict
from tldextract import extract

from .._base.base import BasePage
from .._commons.web import cookie_to_dict
from .._configs.session_options import SessionOptions
from .._elements.session_element import SessionElement, make_session_ele
from .._units.setter import SessionPageSetter


class SessionPage(BasePage):
    """SessionPage封装了页面操作的常用功能，使用requests来获取、解析网页"""

    def __init__(self, session_or_options=None, timeout=None):
        """
        :param session_or_options: Session对象或SessionOptions对象
        :param timeout: 连接超时时间，为None时从ini文件读取
        """
        super(SessionPage, SessionPage).__init__(self)
        self._response = None
        self._session = None
        self._set = None
        self._s_set_start_options(session_or_options, None)
        self._s_set_runtime_settings()
        self._create_session()
        if timeout is not None:
            self.timeout = timeout

    def _s_set_start_options(self, session_or_options, none):
        """启动配置
        :param session_or_options: Session、SessionOptions
        :param none: 用于后代继承
        :return: None
        """
        if not session_or_options or isinstance(session_or_options, SessionOptions):
            self._session_options = session_or_options or SessionOptions(session_or_options)

        elif isinstance(session_or_options, Session):
            self._session_options = SessionOptions()
            self._session = session_or_options

    def _s_set_runtime_settings(self):
        """设置运行时用到的属性"""
        self._timeout = self._session_options.timeout
        self._download_path = self._session_options.download_path

    def _create_session(self):
        """创建内建Session对象"""
        if not self._session:
            self._session = self._session_options.make_session()

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素
        例：ele2 = ele1('@id=ele_id')
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和ChromiumElement对应，便于无差别调用
        :return: SessionElement对象或属性文本
        """
        return self.ele(loc_or_str)

    # -----------------共有属性和方法-------------------
    @property
    def title(self):
        """返回网页title"""
        ele = self._ele('xpath://title', raise_err=False)
        return ele.text if ele else None

    @property
    def url(self):
        """返回当前访问url"""
        return self._url

    @property
    def _session_url(self):
        """返回当前访问url"""
        return self._url

    @property
    def html(self):
        """返回页面的html文本"""
        return self.response.text if self.response else ''

    @property
    def json(self):
        """当返回内容是json格式时，返回对应的字典，非json格式时返回None"""
        try:
            return self.response.json()
        except Exception:
            return None

    @property
    def user_agent(self):
        """返回user agent"""
        return self.session.headers.get('user-agent', '')

    @property
    def session(self):
        """返回session对象"""
        return self._session

    @property
    def response(self):
        """返回访问url得到的response对象"""
        return self._response

    @property
    def set(self):
        """返回用于等待的对象"""
        if self._set is None:
            self._set = SessionPageSetter(self)
        return self._set

    def get(self, url, show_errmsg=False, retry=None, interval=None, timeout=None, **kwargs):
        """用get方式跳转到url
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param timeout: 连接超时时间（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        return self._s_connect(url, 'get', None, show_errmsg, retry, interval, **kwargs)

    def ele(self, loc_or_ele, timeout=None):
        """返回页面中符合条件的第一个元素、属性或节点文本
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和ChromiumElement对应，便于无差别调用
        :return: SessionElement对象或属性、文本
        """
        return self._ele(loc_or_ele)

    def eles(self, loc_or_str, timeout=None):
        """返回页面中所有符合条件的元素、属性或节点文本
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和ChromiumElement对应，便于无差别调用
        :return: SessionElement对象或属性、文本组成的列表
        """
        return self._ele(loc_or_str, single=False)

    def s_ele(self, loc_or_ele=None):
        """返回页面中符合条件的第一个元素、属性或节点文本
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self.html) if loc_or_ele is None else self._ele(loc_or_ele)

    def s_eles(self, loc_or_str):
        """返回页面中符合条件的所有元素、属性或节点文本
        :param loc_or_str: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return self._ele(loc_or_str, single=False)

    def _find_elements(self, loc_or_ele, timeout=None, single=True, raise_err=None):
        """返回页面中符合条件的元素、属性或节点文本，默认返回第一个
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和父类对应
        :param single: True则返回第一个，False则返回全部
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: SessionElement对象
        """
        return loc_or_ele if isinstance(loc_or_ele, SessionElement) else make_session_ele(self, loc_or_ele, single)

    def get_cookies(self, as_dict=False, all_domains=False, all_info=False):
        """返回cookies
        :param as_dict: 是否以字典方式返回，False则以list返回
        :param all_domains: 是否返回所有域的cookies
        :param all_info: 是否返回所有信息，False则只返回name、value、domain
        :return: cookies信息
        """
        if all_domains:
            cookies = self.session.cookies
        else:
            if self.url:
                ex_url = extract(self._session_url)
                domain = f'{ex_url.domain}.{ex_url.suffix}' if ex_url.suffix else ex_url.domain

                cookies = tuple(x for x in self.session.cookies if domain in x.domain or x.domain == '')
            else:
                cookies = tuple(x for x in self.session.cookies)

        if as_dict:
            return {x.name: x.value for x in cookies}
        elif all_info:
            return [cookie_to_dict(cookie) for cookie in cookies]
        else:
            r = []
            for c in cookies:
                c = cookie_to_dict(c)
                r.append({'name': c['name'], 'value': c['value'], 'domain': c['domain']})
            return r

    def post(self, url, data=None, show_errmsg=False, retry=None, interval=None, **kwargs):
        """用post方式跳转到url
        :param url: 目标url
        :param data: 提交的数据
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        return self._s_connect(url, 'post', data, show_errmsg, retry, interval, **kwargs)

    def _s_connect(self, url, mode, data=None, show_errmsg=False, retry=None, interval=None, **kwargs):
        """执行get或post连接
        :param url: 目标url
        :param mode: 'get' 或 'post'
        :param data: 提交的数据
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        retry, interval = self._before_connect(url, retry, interval)
        self._response, info = self._make_response(self._url, mode, data, retry, interval, show_errmsg, **kwargs)

        if self._response is None:
            self._url_available = False

        else:
            if self._response.ok:
                self._url_available = True

            else:
                if show_errmsg:
                    raise ConnectionError(f'状态码：{self._response.status_code}.')
                self._url_available = False

        return self._url_available

    def _make_response(self, url, mode='get', data=None, retry=None, interval=None, show_errmsg=False, **kwargs):
        """生成Response对象
        :param url: 目标url
        :param mode: 'get' 或 'post'
        :param data: post方式要提交的数据
        :param show_errmsg: 是否显示和抛出异常
        :param kwargs: 其它参数
        :return: tuple，第一位为Response或None，第二位为出错信息或'Success'
        """
        kwargs = CaseInsensitiveDict(kwargs)
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        else:
            kwargs['headers'] = CaseInsensitiveDict(kwargs['headers'])

        # 设置referer和host值
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        scheme = parsed_url.scheme
        if not check_headers(kwargs, self.session.headers, 'Referer'):
            kwargs['headers']['Referer'] = self.url if self.url else f'{scheme}://{hostname}'
        if 'Host' not in kwargs['headers']:
            kwargs['headers']['Host'] = hostname

        if not check_headers(kwargs, self.session.headers, 'timeout'):
            kwargs['timeout'] = self.timeout

        r = err = None
        retry = retry if retry is not None else self.retry_times
        interval = interval if interval is not None else self.retry_interval
        for i in range(retry + 1):
            try:
                if mode == 'get':
                    r = self.session.get(url, **kwargs)
                elif mode == 'post':
                    r = self.session.post(url, data=data, **kwargs)

                if r:
                    return set_charset(r), 'Success'

            except Exception as e:
                err = e

            # if r and r.status_code in (403, 404):
            #     break

            if i < retry:
                sleep(interval)
                if show_errmsg:
                    print(f'重试 {url}')

        if r is None:
            if show_errmsg:
                if err:
                    raise err
                else:
                    raise ConnectionError('连接失败')
            return None, '连接失败' if err is None else err

        if not r.ok:
            if show_errmsg:
                raise ConnectionError(f'状态码：{r.status_code}')
            return r, f'状态码：{r.status_code}'


def check_headers(kwargs, headers, arg):
    """检查kwargs或headers中是否有arg所示属性"""
    return arg in kwargs['headers'] or arg in headers


def set_charset(response):
    """设置Response对象的编码"""
    # 在headers中获取编码
    content_type = response.headers.get('content-type', '').lower()
    if not content_type.endswith(';'):
        content_type += ';'
    charset = search(r'charset[=: ]*(.*)?;?', content_type)

    if charset:
        response.encoding = charset.group(1)

    # 在headers中获取不到编码，且如果是网页
    elif content_type.replace(' ', '').startswith('text/html'):
        re_result = search(b'<meta.*?charset=[ \\\'"]*([^"\\\' />]+).*?>', response.content)

        if re_result:
            charset = re_result.group(1).decode()
        else:
            charset = response.apparent_encoding

        response.encoding = charset

    return response