# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from base64 import b64decode
from html import unescape
from http.cookiejar import Cookie
from json import JSONDecodeError, loads
from re import sub
from urllib.parse import urlparse, urljoin, urlunparse

from requests.cookies import RequestsCookieJar
from requests.structures import CaseInsensitiveDict
from tldextract import extract


class DataPacket(object):
    """返回的数据包管理类"""
    __slots__ = ('requestId', 'request', 'response', 'rawBody', 'tab', 'target', '_requestHeaders', '_body',
                 '_base64_body', '_rawPostData', '_postData',

                 'url', 'urlFragment', 'method', 'postDataEntries', 'mixedContentType', 'initialPriority',
                 'referrerPolicy', 'isLinkPreload', 'trustTokenParams', 'isSameSite',


                 'status', 'statusText',
                 'securityDetails', 'headersText', 'mimeType', 'requestHeadersText', 'connectionReused', 'connectionId',
                 'remoteIPAddress', 'remotePort', 'fromDiskCache', 'fromServiceWorker', 'fromPrefetchCache',
                 'encodedDataLength', 'timing', 'serviceWorkerResponseSource', 'responseTime', 'cacheStorageCacheName',
                 'protocol', 'securityState',
                 )

    def __init__(self, request_id, request, response, body, tab, target):
        """
        :param request: request的数据
        :param response: response的数据
        :param body: response包含的内容
        :param tab: 产生这个数据包的tab的id
        :param target: 监听目标
        """
        self.requestId = request_id
        self.response = CaseInsensitiveDict(response)
        self.request = CaseInsensitiveDict(request)
        self.rawBody = body
        self.tab = tab
        self.target = target
        self._requestHeaders = None
        self._postData = None
        self._body = None
        self._base64_body = False
        self._rawPostData = None

    def __getattr__(self, item):
        return self.response.get(item, None)

    def __repr__(self):
        return f'<ResponseData target={self.target} request_id={self.requestId}>'

    @property
    def responseHeaders(self):
        """以大小写不敏感字典返回headers数据"""
        headers = self.response.get('headers', None)
        return CaseInsensitiveDict(headers) if headers else None

    @property
    def requestHeaders(self):
        """以大小写不敏感字典返回requestHeaders数据"""
        if self._requestHeaders:
            return self._requestHeaders
        headers = self.response.get('requestHeaders', None)
        return CaseInsensitiveDict(headers) if headers else None

    @property
    def postData(self):
        """返回postData数据"""
        if self._postData is None and self._rawPostData:
            try:
                self._postData = loads(self._rawPostData)
            except JSONDecodeError:
                self._postData = self._rawPostData
        return self._postData

    def set_postData(self, val):
        """设置postData，当hasPostData为True但数据太长时使用"""
        self._rawPostData = val

    @property
    def body(self):
        """返回body内容，如果是json格式，自动进行转换，如果时图片格式，进行base64转换，其它格式直接返回文本"""
        if self._body is None:
            if self._base64_body:
                self._body = b64decode(self.rawBody)

            else:
                try:
                    self._body = loads(self.rawBody)
                except JSONDecodeError:
                    self._body = self.rawBody

        return self._body


def get_ele_txt(e):
    """获取元素内所有文本
    :param e: 元素对象
    :return: 元素内所有文本
    """
    # 前面无须换行的元素
    nowrap_list = ('br', 'sub', 'sup', 'em', 'strong', 'a', 'font', 'b', 'span', 's', 'i', 'del', 'ins', 'img', 'td',
                   'th', 'abbr', 'bdi', 'bdo', 'cite', 'code', 'data', 'dfn', 'kbd', 'mark', 'q', 'rp', 'rt', 'ruby',
                   'samp', 'small', 'time', 'u', 'var', 'wbr', 'button', 'slot', 'content')
    # 后面添加换行的元素
    wrap_after_list = ('p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'li', 'blockquote', 'header',
                       'footer', 'address' 'article', 'aside', 'main', 'nav', 'section', 'figcaption', 'summary')
    # 不获取文本的元素
    noText_list = ('script', 'style', 'video', 'audio', 'iframe', 'embed', 'noscript', 'canvas', 'template')
    # 用/t分隔的元素
    tab_list = ('td', 'th')

    if e.tag in noText_list:
        return e.raw_text

    def get_node_txt(ele, pre: bool = False):
        tag = ele.tag
        if tag == 'br':
            return [True]
        if not pre and tag == 'pre':
            pre = True

        str_list = []
        if tag in noText_list and not pre:  # 标签内的文本不返回
            return str_list

        nodes = ele.eles('xpath:./text() | *')
        prev_ele = ''
        for el in nodes:
            if isinstance(el, str):  # 字符节点
                if pre:
                    str_list.append(el)

                else:
                    if sub('[ \n\t\r]', '', el) != '':  # 字符除了回车和空格还有其它内容
                        txt = el
                        if not pre:
                            txt = txt.replace('\n', ' ').strip(' ')
                            txt = sub(r' {2,}', ' ', txt)
                        str_list.append(txt)

            else:  # 元素节点
                if el.tag not in nowrap_list and str_list and str_list[-1] != '\n':  # 元素间换行的情况
                    str_list.append('\n')
                if el.tag in tab_list and prev_ele in tab_list:  # 表格的行
                    str_list.append('\t')

                str_list.extend(get_node_txt(el, pre))
                prev_ele = el.tag

        if tag in wrap_after_list and str_list and str_list[-1] not in ('\n', True):  # 有些元素后面要添加回车
            str_list.append('\n')

        return str_list

    re_str = get_node_txt(e)
    if re_str and re_str[-1] == '\n':
        re_str.pop()
    re_str = ''.join([i if i is not True else '\n' for i in re_str])
    return format_html(re_str)


def format_html(text):
    """处理html编码字符
    :param text: html文本
    :return: 格式化后的html文本
    """
    return unescape(text).replace('\xa0', ' ') if text else text


def location_in_viewport(page, loc_x, loc_y):
    """判断给定的坐标是否在视口中          |n
    :param page: ChromePage对象
    :param loc_x: 页面绝对坐标x
    :param loc_y: 页面绝对坐标y
    :return:
    """
    js = f'''function(){{var x = {loc_x}; var y = {loc_y};
    const scrollLeft = document.documentElement.scrollLeft;
    const scrollTop = document.documentElement.scrollTop;
    const vWidth = document.documentElement.clientWidth;
    const vHeight = document.documentElement.clientHeight;
    if (x< scrollLeft || y < scrollTop || x > vWidth + scrollLeft || y > vHeight + scrollTop){{return false;}}
    return true;}}'''
    return page.run_js(js)
    # const vWidth = window.innerWidth || document.documentElement.clientWidth;
    # const vHeight = window.innerHeight || document.documentElement.clientHeight;


def offset_scroll(ele, offset_x, offset_y):
    """接收元素及偏移坐标，把坐标滚动到页面中间，返回该点在视口中的坐标
    有偏移量时以元素左上角坐标为基准，没有时以click_point为基准
    :param ele: 元素对象
    :param offset_x: 偏移量x
    :param offset_y: 偏移量y
    :return: 视口中的坐标
    """
    loc_x, loc_y = ele.location
    cp_x, cp_y = ele.locations.click_point
    lx = loc_x + offset_x if offset_x else cp_x
    ly = loc_y + offset_y if offset_y else cp_y
    if not location_in_viewport(ele.page, lx, ly):
        clientWidth = ele.page.run_js('return document.body.clientWidth;')
        clientHeight = ele.page.run_js('return document.body.clientHeight;')
        ele.page.scroll.to_location(lx - clientWidth // 2, ly - clientHeight // 2)
    cl_x, cl_y = ele.locations.viewport_location
    ccp_x, ccp_y = ele.locations.viewport_click_point
    cx = cl_x + offset_x if offset_x else ccp_x
    cy = cl_y + offset_y if offset_y else ccp_y
    return cx, cy


def make_absolute_link(link, page=None):
    """获取绝对url
    :param link: 超链接
    :param page: 页面对象
    :return: 绝对链接
    """
    if not link:
        return link

    parsed = urlparse(link)._asdict()

    # 是相对路径，与页面url拼接并返回
    if not parsed['netloc']:
        return urljoin(page.url, link) if page else link

    # 是绝对路径但缺少协议，从页面url获取协议并修复
    if not parsed['scheme'] and page:
        parsed['scheme'] = urlparse(page.url).scheme
        parsed = tuple(v for v in parsed.values())
        return urlunparse(parsed)

    # 绝对路径且不缺协议，直接返回
    return link


def is_js_func(func):
    """检查文本是否js函数"""
    func = func.strip()
    if func.startswith('function') or func.startswith('async '):
        return True
    elif '=>' in func:
        return True
    return False


def cookie_to_dict(cookie):
    """把Cookie对象转为dict格式
    :param cookie: Cookie对象
    :return: cookie字典
    """
    if isinstance(cookie, Cookie):
        cookie_dict = cookie.__dict__.copy()
        cookie_dict.pop('rfc2109')
        cookie_dict.pop('_rest')
        return cookie_dict

    elif isinstance(cookie, dict):
        cookie_dict = cookie

    elif isinstance(cookie, str):
        cookie = cookie.split(',' if ',' in cookie else ';')
        cookie_dict = {}

        for key, attr in enumerate(cookie):
            attr_val = attr.lstrip().split('=', 1)

            if key == 0:
                cookie_dict['name'] = attr_val[0]
                cookie_dict['value'] = attr_val[1] if len(attr_val) == 2 else ''
            else:
                cookie_dict[attr_val[0]] = attr_val[1] if len(attr_val) == 2 else ''

        return cookie_dict

    else:
        raise TypeError('cookie参数必须为Cookie、str或dict类型。')

    return cookie_dict


def cookies_to_tuple(cookies):
    """把cookies转为tuple格式
    :param cookies: cookies信息，可为CookieJar, list, tuple, str, dict
    :return: 返回tuple形式的cookies
    """
    if isinstance(cookies, (list, tuple, RequestsCookieJar)):
        cookies = tuple(cookie_to_dict(cookie) for cookie in cookies)

    elif isinstance(cookies, str):
        cookies = tuple(cookie_to_dict(cookie.lstrip()) for cookie in cookies.split(";"))

    elif isinstance(cookies, dict):
        cookies = tuple({'name': cookie, 'value': cookies[cookie]} for cookie in cookies)

    else:
        raise TypeError('cookies参数必须为RequestsCookieJar、list、tuple、str或dict类型。')

    return cookies


def set_session_cookies(session, cookies):
    """设置Session对象的cookies
    :param session: Session对象
    :param cookies: cookies信息
    :return: None
    """
    cookies = cookies_to_tuple(cookies)
    for cookie in cookies:
        if cookie['value'] is None:
            cookie['value'] = ''

        kwargs = {x: cookie[x] for x in cookie
                  if x.lower() in ('version', 'port', 'domain', 'path', 'secure',
                                   'expires', 'discard', 'comment', 'comment_url', 'rest')}

        if 'expiry' in cookie:
            kwargs['expires'] = cookie['expiry']

        session.cookies.set(cookie['name'], cookie['value'], **kwargs)


def set_browser_cookies(page, cookies):
    """设置cookies值
    :param page: 页面对象
    :param cookies: cookies信息
    :return: None
    """
    cookies = cookies_to_tuple(cookies)
    for cookie in cookies:
        if 'expiry' in cookie:
            cookie['expires'] = int(cookie['expiry'])
            cookie.pop('expiry')
        if 'expires' in cookie:
            cookie['expires'] = int(cookie['expires'])
        if cookie['value'] is None:
            cookie['value'] = ''

        if cookie.get('domain', None):
            try:
                page.run_cdp_loaded('Network.setCookie', **cookie)
                if is_cookie_in_driver(page, cookie):
                    continue
            except Exception:
                pass

        ex_url = extract(page._browser_url)
        d_list = ex_url.subdomain.split('.')
        d_list.append(f'{ex_url.domain}.{ex_url.suffix}' if ex_url.suffix else ex_url.domain)

        tmp = [d_list[0]]
        if len(d_list) > 1:
            for i in d_list[1:]:
                tmp.append('.')
                tmp.append(i)

        for i in range(len(tmp)):
            d = ''.join(tmp[i:])
            cookie['domain'] = d
            page.run_cdp_loaded('Network.setCookie', **cookie)
            if is_cookie_in_driver(page, cookie):
                break


def is_cookie_in_driver(page, cookie):
    """查询cookie是否在浏览器内
    :param page: BasePage对象
    :param cookie: dict格式cookie
    :return: bool
    """
    for c in page.get_cookies():
        if cookie['name'] == c['name'] and cookie['value'] == c['value']:
            return True
    return False
