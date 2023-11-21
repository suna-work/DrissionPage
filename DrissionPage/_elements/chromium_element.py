# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from os.path import basename, sep
from pathlib import Path
from time import perf_counter, sleep

from .none_element import NoneElement
from .session_element import make_session_ele
from .._base.base import DrissionElement, BaseElement
from .._commons.settings import Settings
from .._commons.keys import keys_to_typing, keyDescriptionForString, keyDefinitions
from .._commons.locator import get_loc
from .._commons.tools import get_usable_path
from .._commons.web import make_absolute_link, get_ele_txt, format_html, is_js_func, offset_scroll
from .._units.clicker import Clicker
from .._units.rect import ElementRect
from .._units.scroller import ElementScroller
from .._units.select_element import SelectElement
from .._units.setter import ChromiumElementSetter
from .._units.states import ElementStates, ShadowRootStates
from .._units.waiter import ElementWaiter
from ..errors import (ContextLossError, ElementLossError, JavaScriptError, ElementNotFoundError,
                      CDPError, NoResourceError, AlertExistsError)

__FRAME_ELEMENT__ = ('iframe', 'frame')


class ChromiumElement(DrissionElement):
    """控制浏览器元素的对象"""

    def __init__(self, page, node_id=None, obj_id=None, backend_id=None):
        """node_id、obj_id和backend_id必须至少传入一个
        :param page: 元素所在页面对象
        :param node_id: cdp中的node id
        :param obj_id: js中的object id
        :param backend_id: backend id
        """
        super().__init__(page)
        self._select = None
        self._scroll = None
        self._rect = None
        self._set = None
        self._states = None
        self._pseudo = None
        self._clicker = None
        self._tag = None
        self._wait = None

        if node_id and obj_id and backend_id:
            self._node_id = node_id
            self._obj_id = obj_id
            self._backend_id = backend_id
        elif node_id:
            self._node_id = node_id
            self._obj_id = self._get_obj_id(node_id)
            self._backend_id = self._get_backend_id(self._node_id)
        elif obj_id:
            self._node_id = self._get_node_id(obj_id)
            self._obj_id = obj_id
            self._backend_id = self._get_backend_id(self._node_id)
        elif backend_id:
            self._obj_id = self._get_obj_id(backend_id=backend_id)
            self._node_id = self._get_node_id(obj_id=self._obj_id)
            self._backend_id = backend_id
        else:
            raise ElementLossError

        doc = self.run_js('return this.ownerDocument;')
        self._doc_id = doc['objectId'] if doc else None

    def __repr__(self):
        attrs = self.attrs
        attrs = [f"{attr}='{attrs[attr]}'" for attr in attrs]
        return f'<ChromiumElement {self.tag} {" ".join(attrs)}>'

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: ChromiumElement对象或属性、文本
        """
        return self.ele(loc_or_str, timeout)

    @property
    def tag(self):
        """返回元素tag"""
        if self._tag is None:
            self._tag = self.page.run_cdp('DOM.describeNode',
                                          backendNodeId=self._backend_id)['node']['localName'].lower()
        return self._tag

    @property
    def html(self):
        """返回元素outerHTML文本"""
        return self.page.run_cdp('DOM.getOuterHTML', backendNodeId=self._backend_id)['outerHTML']

    @property
    def inner_html(self):
        """返回元素innerHTML文本"""
        return self.run_js('return this.innerHTML;')

    @property
    def attrs(self):
        """返回元素所有attribute属性"""
        try:
            attrs = self.page.run_cdp('DOM.getAttributes', nodeId=self._node_id)['attributes']
            return {attrs[i]: attrs[i + 1] for i in range(0, len(attrs), 2)}
        except CDPError:  # 文档根元素不能调用此方法
            return {}

    @property
    def text(self):
        """返回元素内所有文本，文本已格式化"""
        return get_ele_txt(make_session_ele(self.html))

    @property
    def raw_text(self):
        """返回未格式化处理的元素内文本"""
        return self.prop('innerText')

    # -----------------d模式独有属性-------------------

    @property
    def set(self):
        """返回用于设置元素属性的对象"""
        if self._set is None:
            self._set = ChromiumElementSetter(self)
        return self._set

    @property
    def states(self):
        """返回用于获取元素状态的对象"""
        if self._states is None:
            self._states = ElementStates(self)
        return self._states

    @property
    def pseudo(self):
        """返回用于获取伪元素内容的对象"""
        if self._pseudo is None:
            self._pseudo = Pseudo(self)
        return self._pseudo

    @property
    def rect(self):
        """返回用于获取元素位置的对象"""
        if self._rect is None:
            self._rect = ElementRect(self)
        return self._rect

    @property
    def shadow_root(self):
        """返回当前元素的shadow_root元素对象"""
        info = self.page.run_cdp('DOM.describeNode', backendNodeId=self._backend_id)['node']
        if not info.get('shadowRoots', None):
            return None

        return ChromiumShadowRoot(self, backend_id=info['shadowRoots'][0]['backendNodeId'])

    @property
    def sr(self):
        """返回当前元素的shadow_root元素对象"""
        return self.shadow_root

    @property
    def scroll(self):
        """用于滚动滚动条的对象"""
        if self._scroll is None:
            self._scroll = ElementScroller(self)
        return self._scroll

    @property
    def click(self):
        """返回用于点击的对象"""
        if self._clicker is None:
            self._clicker = Clicker(self)
        return self._clicker

    @property
    def wait(self):
        """返回用于等待的对象"""
        if self._wait is None:
            self._wait = ElementWaiter(self.page, self)
        return self._wait

    @property
    def select(self):
        """返回专门处理下拉列表的Select类，非下拉列表元素返回False"""
        if self._select is None:
            if self.tag != 'select':
                self._select = False
            else:
                self._select = SelectElement(self)

        return self._select

    def check(self, uncheck=False):
        """选中或取消选中当前元素
        :param uncheck: 是否取消选中
        :return: None
        """
        js = 'this.checked=false' if uncheck else 'this.checked=true'
        self.run_js(js)

    def parent(self, level_or_loc=1, index=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，或定位符
        :param index: 当level_or_loc传入定位符，使用此参数选择第几个结果
        :return: 上级元素对象
        """
        return super().parent(level_or_loc, index)

    def child(self, filter_loc='', index=1, timeout=0, ele_only=True):
        """返回当前元素的一个符合条件的直接子元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param filter_loc: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本
        """
        return super().child(filter_loc, index, timeout, ele_only=ele_only)

    def prev(self, filter_loc='', index=1, timeout=0, ele_only=True):
        """返回当前元素前面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param filter_loc: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本
        """
        return super().prev(filter_loc, index, timeout, ele_only=ele_only)

    def next(self, filter_loc='', index=1, timeout=0, ele_only=True):
        """返回当前元素后面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param filter_loc: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本
        """
        return super().next(filter_loc, index, timeout, ele_only=ele_only)

    def before(self, filter_loc='', index=1, timeout=None, ele_only=True):
        """返回文档中当前元素前面符合条件的第一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的某个元素或节点
        """
        return super().before(filter_loc, index, timeout, ele_only=ele_only)

    def after(self, filter_loc='', index=1, timeout=None, ele_only=True):
        """返回文档中此当前元素后面符合条件的第一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的某个元素或节点
        """
        return super().after(filter_loc, index, timeout, ele_only=ele_only)

    def children(self, filter_loc='', timeout=0, ele_only=True):
        """返回当前元素符合条件的直接子元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本组成的列表
        """
        return super().children(filter_loc, timeout, ele_only=ele_only)

    def prevs(self, filter_loc='', timeout=0, ele_only=True):
        """返回当前元素前面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本组成的列表
        """
        return super().prevs(filter_loc, timeout, ele_only=ele_only)

    def nexts(self, filter_loc='', timeout=0, ele_only=True):
        """返回当前元素后面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本组成的列表
        """
        return super().nexts(filter_loc, timeout, ele_only=ele_only)

    def befores(self, filter_loc='', timeout=None, ele_only=True):
        """返回文档中当前元素前面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的元素或节点组成的列表
        """
        return super().befores(filter_loc, timeout, ele_only=ele_only)

    def afters(self, filter_loc='', timeout=None, ele_only=True):
        """返回文档中当前元素后面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的元素或节点组成的列表
        """
        return super().afters(filter_loc, timeout, ele_only=ele_only)

    def attr(self, attr):
        """返回一个attribute属性值
        :param attr: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        attrs = self.attrs
        if attr == 'href':  # 获取href属性时返回绝对url
            link = attrs.get('href', None)
            if not link or link.lower().startswith(('javascript:', 'mailto:')):
                return link
            else:
                return make_absolute_link(link, self.page)

        elif attr == 'src':
            return make_absolute_link(attrs.get('src', None), self.page)

        elif attr == 'text':
            return self.text

        elif attr == 'innerText':
            return self.raw_text

        elif attr in ('html', 'outerHTML'):
            return self.html

        elif attr == 'innerHTML':
            return self.inner_html

        else:
            return attrs.get(attr, None)

    def remove_attr(self, attr):
        """删除元素一个attribute属性
        :param attr: 属性名
        :return: None
        """
        self.run_js(f'this.removeAttribute("{attr}");')

    def prop(self, prop):
        """获取一个property属性值
        :param prop: 属性名
        :return: 属性值文本
        """
        try:
            value = self.run_js(f'return this.{prop};')
            return format_html(value) if isinstance(value, str) else value
        except:
            return None

    def run_js(self, script, *args, as_expr=False, timeout=None):
        """对本元素执行javascript代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间，为None则使用页面timeouts.script设置
        :return: 运行的结果
        """
        return run_js(self, script, as_expr, self.page.timeouts.script if timeout is None else timeout, args)

    def run_async_js(self, script, *args, as_expr=False, timeout=None):
        """以异步方式对本元素执行javascript代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间，为None则使用页面timeouts.script设置
        :return: None
        """
        from threading import Thread
        Thread(target=run_js, args=(self, script, as_expr, self.page.timeouts.script if timeout is None else timeout,
                                    args, True)).start()

    def ele(self, loc_or_str, timeout=None):
        """返回当前元素下级符合条件的第一个元素、属性或节点文本
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: ChromiumElement对象或属性、文本
        """
        return self._ele(loc_or_str, timeout, method='ele()')

    def eles(self, loc_or_str, timeout=None):
        """返回当前元素下级所有符合条件的子元素、属性或节点文本
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: ChromiumElement对象或属性、文本组成的列表
        """
        return self._ele(loc_or_str, timeout=timeout, single=False)

    def s_ele(self, loc_or_str=None):
        """查找第一个符合条件的元素，以SessionElement形式返回
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        if self.tag in __FRAME_ELEMENT__:
            r = make_session_ele(self.inner_html, loc_or_str)
        else:
            r = make_session_ele(self, loc_or_str)
        if isinstance(r, NoneElement):
            if Settings.raise_when_ele_not_found:
                raise ElementNotFoundError(None, 's_ele()', {'loc_or_str': loc_or_str})
            else:
                r.method = 's_ele()'
                r.args = {'loc_or_str': loc_or_str}
        return r

    def s_eles(self, loc_or_str=None):
        """查找所有符合条件的元素，以SessionElement列表形式返回
        :param loc_or_str: 定位符
        :return: SessionElement或属性、文本组成的列表
        """
        if self.tag in __FRAME_ELEMENT__:
            return make_session_ele(self.inner_html, loc_or_str, single=False)
        return make_session_ele(self, loc_or_str, single=False)

    def _find_elements(self, loc_or_str, timeout=None, single=True, relative=False, raise_err=None):
        """返回当前元素下级符合条件的子元素、属性或节点文本，默认返回第一个
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :param single: True则返回第一个，False则返回全部
        :param relative: WebPage用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: ChromiumElement对象或文本、属性或其组成的列表
        """
        return find_in_chromium_ele(self, loc_or_str, single, timeout, relative=relative)

    def style(self, style, pseudo_ele=''):
        """返回元素样式属性值，可获取伪元素属性值
        :param style: 样式属性名称
        :param pseudo_ele: 伪元素名称（如有）
        :return: 样式属性的值
        """
        if pseudo_ele:
            pseudo_ele = f', "{pseudo_ele}"' if pseudo_ele.startswith(':') else f', "::{pseudo_ele}"'
        return self.run_js(f'return window.getComputedStyle(this{pseudo_ele}).getPropertyValue("{style}");')

    def get_src(self, timeout=None, base64_to_bytes=True):
        """返回元素src资源，base64的可转为bytes返回，其它返回str
        :param timeout: 等待资源加载的超时时间
        :param base64_to_bytes: 为True时，如果是base64数据，转换为bytes格式
        :return: 资源内容
        """
        timeout = self.page.timeout if timeout is None else timeout
        if self.tag == 'img':  # 等待图片加载完成
            js = ('return this.complete && typeof this.naturalWidth != "undefined" '
                  '&& this.naturalWidth > 0 && typeof this.naturalHeight != "undefined" '
                  '&& this.naturalHeight > 0')
            end_time = perf_counter() + timeout
            while not self.run_js(js) and perf_counter() < end_time:
                sleep(.1)

        src = self.attr('src')
        is_blob = src.startswith('blob')
        result = None
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if is_blob:
                js = """
                           function fetchData(url) {
                          return new Promise((resolve, reject) => {
                            var xhr = new XMLHttpRequest();
                            xhr.responseType = 'blob';
                            xhr.onload = function() {
                              var reader  = new FileReader();
                              reader.onloadend = function() {resolve(reader.result);}
                              reader.readAsDataURL(xhr.response);
                            };
                            xhr.open('GET', url, true);
                            xhr.send();
                          });
                        }
                    """
                try:
                    result = self.page.run_js(js, src)
                    break
                except:
                    continue

            else:
                src = self.prop('currentSrc')
                if not src:
                    continue

                node = self.page.run_cdp('DOM.describeNode', backendNodeId=self._backend_id)['node']
                frame = node.get('frameId', None)
                frame = frame or self.page._target_id

                try:
                    result = self.page.run_cdp('Page.getResourceContent', frameId=frame, url=src)
                    break
                except CDPError:
                    sleep(.1)

        if not result:
            return None

        if is_blob:
            if base64_to_bytes:
                from base64 import b64decode
                return b64decode(result.split(',', 1)[-1])
            else:
                return result

        else:
            if result['base64Encoded'] and base64_to_bytes:
                from base64 import b64decode
                return b64decode(result['content'])
            else:
                return result['content']

    def save(self, path=None, name=None, timeout=None):
        """保存图片或其它有src属性的元素的资源
        :param path: 文件保存路径，为None时保存到当前文件夹
        :param name: 文件名称，为None时从资源url获取
        :param timeout: 等待资源加载的超时时间
        :return: 返回保存路径
        """
        data = self.get_src(timeout=timeout)
        if not data:
            raise NoResourceError

        path = path or '.'
        name = name or basename(self.prop('currentSrc'))
        path = get_usable_path(f'{path}{sep}{name}').absolute()
        write_type = 'wb' if isinstance(data, bytes) else 'w'

        with open(path, write_type) as f:
            f.write(data)

        return str(path)

    def get_screenshot(self, path=None, name=None, as_bytes=None, as_base64=None, scroll_to_center=True):
        """对当前元素截图，可保存到文件，或以字节方式返回
        :param path: 文件保存路径
        :param name: 完整文件名，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否以字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数和as_base64参数无效
        :param as_base64: 是否以base64字符串形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :param scroll_to_center: 截图前是否滚动到视口中央
        :return: 图片完整路径或字节文本
        """
        if self.tag == 'img':  # 等待图片加载完成
            js = ('return this.complete && typeof this.naturalWidth != "undefined" && this.naturalWidth > 0 '
                  '&& typeof this.naturalHeight != "undefined" && this.naturalHeight > 0')
            end_time = perf_counter() + self.page.timeout
            while not self.run_js(js) and perf_counter() < end_time:
                sleep(.1)
        if scroll_to_center:
            self.scroll.to_see(center=True)

        left, top = self.rect.location
        width, height = self.rect.size
        left_top = (left, top)
        right_bottom = (left + width, top + height)
        if not name:
            name = f'{self.tag}.jpg'

        return self.page._get_screenshot(path, name, as_bytes=as_bytes, as_base64=as_base64, full_page=False,
                                         left_top=left_top, right_bottom=right_bottom, ele=self)

    def input(self, vals, clear=True, by_js=False):
        """输入文本或组合键，也可用于输入文件路径到input元素（路径间用\n间隔）
        :param vals: 文本值或按键组合
        :param clear: 输入前是否清空文本框
        :param by_js: 是否用js方式输入，不能输入组合键
        :return: None
        """
        if self.tag == 'input' and self.attr('type') == 'file':
            return self._set_file_input(vals)

        if by_js:
            if clear:
                self.clear(True)
            if isinstance(vals, (list, tuple)):
                vals = ''.join([str(i) for i in vals])
            self.set.prop('value', str(vals))
            return

        if clear and vals not in ('\n', '\ue007'):
            self.clear(by_js=False)
        else:
            self._input_focus()

        # ------------处理字符-------------
        if not isinstance(vals, (tuple, list)):
            vals = (str(vals),)
        modifier, vals = keys_to_typing(vals)

        if modifier != 0:  # 包含修饰符
            for key in vals:
                send_key(self, modifier, key)
            return

        if vals.endswith(('\n', '\ue007')):
            self.page.run_cdp('Input.insertText', text=vals[:-1])
            send_key(self, modifier, '\n')
        else:
            self.page.run_cdp('Input.insertText', text=vals)

    def clear(self, by_js=False):
        """清空元素文本
        :param by_js: 是否用js方式清空，为False则用全选+del模拟输入删除
        :return: None
        """
        if by_js:
            self.run_js("this.value='';")

        else:
            self._input_focus()
            self.input(('\ue009', 'a', '\ue017'), clear=False)

    def _input_focus(self):
        """输入前使元素获取焦点"""
        try:
            self.page.run_cdp('DOM.focus', backendNodeId=self._backend_id)
        except Exception:
            self.click(by_js=None)

    def focus(self):
        """使元素获取焦点"""
        try:
            self.page.run_cdp('DOM.focus', backendNodeId=self._backend_id)
        except Exception:
            self.run_js('this.focus();')

    def hover(self, offset_x=None, offset_y=None):
        """鼠标悬停，可接受偏移量，偏移量相对于元素左上角坐标。不传入x或y值时悬停在元素中点
        :param offset_x: 相对元素左上角坐标的x轴偏移量
        :param offset_y: 相对元素左上角坐标的y轴偏移量
        :return: None
        """
        self.page.scroll.to_see(self)
        x, y = offset_scroll(self, offset_x, offset_y)
        self.page.run_cdp('Input.dispatchMouseEvent', type='mouseMoved', x=x, y=y)

    def drag(self, offset_x=0, offset_y=0, duration=.5):
        """拖拽当前元素到相对位置
        :param offset_x: x变化值
        :param offset_y: y变化值
        :param duration: 拖动用时，传入0即瞬间到j达
        :return: None
        """
        curr_x, curr_y = self.rect.midpoint
        offset_x += curr_x
        offset_y += curr_y
        self.drag_to((offset_x, offset_y), duration)

    def drag_to(self, ele_or_loc, duration=.5):
        """拖拽当前元素，目标为另一个元素或坐标元组(x, y)
        :param ele_or_loc: 另一个元素或坐标元组，坐标为元素中点的坐标
        :param duration: 拖动用时，传入0即瞬间到达
        :return: None
        """
        if isinstance(ele_or_loc, ChromiumElement):
            ele_or_loc = ele_or_loc.rect.midpoint
        elif not isinstance(ele_or_loc, (list, tuple)):
            raise TypeError('需要ChromiumElement对象或坐标。')

        self.page.actions.hold(self).move_to(ele_or_loc, duration=duration).release()

    def _get_obj_id(self, node_id=None, backend_id=None):
        """根据传入node id或backend id获取js中的object id
        :param node_id: cdp中的node id
        :param backend_id: backend id
        :return: js中的object id
        """
        if node_id:
            return self.page.run_cdp('DOM.resolveNode', nodeId=node_id)['object']['objectId']
        else:
            return self.page.run_cdp('DOM.resolveNode', backendNodeId=backend_id)['object']['objectId']

    def _get_node_id(self, obj_id=None, backend_id=None):
        """根据传入object id或backend id获取cdp中的node id
        :param obj_id: js中的object id
        :param backend_id: backend id
        :return: cdp中的node id
        """
        if obj_id:
            return self.page.run_cdp('DOM.requestNode', objectId=obj_id)['nodeId']
        else:
            return self.page.run_cdp('DOM.describeNode', backendNodeId=backend_id)['node']['nodeId']

    def _get_backend_id(self, node_id):
        """根据传入node id获取backend id
        :param node_id:
        :return: backend id
        """
        return self.page.run_cdp('DOM.describeNode', nodeId=node_id)['node']['backendNodeId']

    def _get_ele_path(self, mode):
        """返获取绝对的css路径或xpath路径"""
        if mode == 'xpath':
            txt1 = 'var tag = el.nodeName.toLowerCase();'
            txt3 = ''' && sib.nodeName.toLowerCase()==tag'''
            txt4 = '''
            if(nth>1){path = '/' + tag + '[' + nth + ']' + path;}
                    else{path = '/' + tag + path;}'''
            txt5 = '''return path;'''

        elif mode == 'css':
            txt1 = ''
            txt3 = ''
            txt4 = '''path = '>' + ":nth-child(" + nth + ")" + path;'''
            txt5 = '''return path.substr(1);'''

        else:
            raise ValueError(f"mode参数只能是'xpath'或'css'，现在是：'{mode}'。")

        js = '''function(){
        function e(el) {
            if (!(el instanceof Element)) return;
            var path = '';
            while (el.nodeType === Node.ELEMENT_NODE) {
                ''' + txt1 + '''
                    var sib = el, nth = 0;
                    while (sib) {
                        if(sib.nodeType === Node.ELEMENT_NODE''' + txt3 + '''){nth += 1;}
                        sib = sib.previousSibling;
                    }
                    ''' + txt4 + '''
                el = el.parentNode;
            }
            ''' + txt5 + '''
        }
        return e(this);}
        '''
        t = self.run_js(js)
        return f':root{t}' if mode == 'css' else t

    def _set_file_input(self, files):
        """对上传控件写入路径
        :param files: 文件路径列表或字符串，字符串时多个文件用回车分隔
        :return: None
        """
        if isinstance(files, str):
            files = files.split('\n')
        files = [str(Path(i).absolute()) for i in files]
        self.page.run_cdp('DOM.setFileInputFiles', files=files, backendNodeId=self._backend_id)

    # -------------即将废弃-------------

    @property
    def location(self):
        """返回元素左上角的绝对坐标"""
        return self.rect.location

    @property
    def size(self):
        """返回元素宽和高组成的元组"""
        return self.rect.size


class ChromiumShadowRoot(BaseElement):
    """ChromiumShadowRoot是用于处理ShadowRoot的类，使用方法和ChromiumElement基本一致"""

    def __init__(self, parent_ele, obj_id=None, backend_id=None):
        """
        :param parent_ele: shadow root 所在父元素
        :param obj_id: js中的object id
        :param backend_id: cdp中的backend id
        """
        super().__init__(parent_ele.page)
        self.parent_ele = parent_ele
        if backend_id:
            self._backend_id = backend_id
            self._obj_id = self._get_obj_id(backend_id)
            self._node_id = self._get_node_id(self._obj_id)
        elif obj_id:
            self._obj_id = obj_id
            self._node_id = self._get_node_id(obj_id)
            self._backend_id = self._get_backend_id(self._node_id)
        self._states = None

    def __repr__(self):
        return f'<ChromiumShadowRoot in {self.parent_ele}>'

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素
        例：ele2 = ele1('@id=ele_id')
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: 元素对象或属性、文本
        """
        return self.ele(loc_or_str, timeout)

    @property
    def tag(self):
        """返回元素标签名"""
        return 'shadow-root'

    @property
    def html(self):
        """返回outerHTML文本"""
        return f'<shadow_root>{self.inner_html}</shadow_root>'

    @property
    def inner_html(self):
        """返回内部的html文本"""
        return self.run_js('return this.innerHTML;')

    @property
    def states(self):
        """返回用于获取元素状态的对象"""
        if self._states is None:
            self._states = ShadowRootStates(self)
        return self._states

    def run_js(self, script, *args, as_expr=False, timeout=None):
        """运行javascript代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间，为None则使用页面timeouts.script设置
        :return: 运行的结果
        """
        return run_js(self, script, as_expr, self.page.timeouts.script if timeout is None else timeout, args)

    def run_async_js(self, script, *args, as_expr=False, timeout=None):
        """以异步方式执行js代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间，为None则使用页面timeouts.script设置
        :return: None
        """
        from threading import Thread
        Thread(target=run_js, args=(self, script, as_expr,
                                    self.page.timeouts.script if timeout is None else timeout, args)).start()

    def parent(self, level_or_loc=1, index=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，或定位符
        :param index: 当level_or_loc传入定位符，使用此参数选择第几个结果
        :return: ChromiumElement对象
        """
        if isinstance(level_or_loc, int):
            loc = f'xpath:./ancestor-or-self::*[{level_or_loc}]'

        elif isinstance(level_or_loc, (tuple, str)):
            loc = get_loc(level_or_loc, True)

            if loc[0] == 'css selector':
                raise ValueError('此css selector语法不受支持，请换成xpath。')

            loc = f'xpath:./ancestor-or-self::{loc[1].lstrip(". / ")}[{index}]'

        else:
            raise TypeError('level_or_loc参数只能是tuple、int或str。')

        return self.parent_ele._ele(loc, timeout=0, relative=True, raise_err=False, method='parent()')

    def child(self, filter_loc='', index=1):
        """返回直接子元素元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :return: 直接子元素或节点文本组成的列表
        """
        nodes = self.children(filter_loc=filter_loc)
        if not nodes:
            if Settings.raise_when_ele_not_found:
                raise ElementNotFoundError(None, 'child()', {'filter_loc': filter_loc, 'index': index})
            else:
                return NoneElement('child()', {'filter_loc': filter_loc, 'index': index})

        try:
            return nodes[index - 1]
        except IndexError:
            if Settings.raise_when_ele_not_found:
                raise ElementNotFoundError(None, 'child()', {'filter_loc': filter_loc, 'index': index})
            else:
                return NoneElement('child()', {'filter_loc': filter_loc, 'index': index})

    def next(self, filter_loc='', index=1):
        """返回当前元素后面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param filter_loc: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :return: ChromiumElement对象
        """
        nodes = self.nexts(filter_loc=filter_loc)
        if nodes:
            return nodes[index - 1]
        if Settings.raise_when_ele_not_found:
            raise ElementNotFoundError(None, 'next()', {'filter_loc': filter_loc, 'index': index})
        else:
            return NoneElement('next()', {'filter_loc': filter_loc, 'index': index})

    def before(self, filter_loc='', index=1):
        """返回文档中当前元素前面符合条件的第一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :return: 本元素前面的某个元素或节点
        """
        nodes = self.befores(filter_loc=filter_loc)
        if nodes:
            return nodes[index - 1]
        if Settings.raise_when_ele_not_found:
            raise ElementNotFoundError(None, 'before()', {'filter_loc': filter_loc, 'index': index})
        else:
            return NoneElement('before()', {'filter_loc': filter_loc, 'index': index})

    def after(self, filter_loc='', index=1):
        """返回文档中此当前元素后面符合条件的第一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :param index: 后面第几个查询结果，1开始
        :return: 本元素后面的某个元素或节点
        """
        nodes = self.afters(filter_loc=filter_loc)
        if nodes:
            return nodes[index - 1]
        if Settings.raise_when_ele_not_found:
            raise ElementNotFoundError(None, 'after()', {'filter_loc': filter_loc, 'index': index})
        else:
            return NoneElement('after()', {'filter_loc': filter_loc, 'index': index})

    def children(self, filter_loc=''):
        """返回当前元素符合条件的直接子元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :return: 直接子元素或节点文本组成的列表
        """
        if not filter_loc:
            loc = '*'
        else:
            loc = get_loc(filter_loc, True)  # 把定位符转换为xpath
            if loc[0] == 'css selector':
                raise ValueError('此css selector语法不受支持，请换成xpath。')
            loc = loc[1].lstrip('./')

        loc = f'xpath:./{loc}'
        return self._ele(loc, single=False, relative=True)

    def nexts(self, filter_loc=''):
        """返回当前元素后面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :return: ChromiumElement对象组成的列表
        """
        loc = get_loc(filter_loc, True)
        if loc[0] == 'css selector':
            raise ValueError('此css selector语法不受支持，请换成xpath。')

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./{loc}'
        return self.parent_ele._ele(xpath, single=False, relative=True)

    def befores(self, filter_loc=''):
        """返回文档中当前元素前面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :return: 本元素前面的元素或节点组成的列表
        """
        loc = get_loc(filter_loc, True)
        if loc[0] == 'css selector':
            raise ValueError('此css selector语法不受支持，请换成xpath。')

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./preceding::{loc}'
        return self.parent_ele._ele(xpath, single=False, relative=True)

    def afters(self, filter_loc=''):
        """返回文档中当前元素后面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :return: 本元素后面的元素或节点组成的列表
        """
        eles1 = self.nexts(filter_loc)
        loc = get_loc(filter_loc, True)[1].lstrip('./')
        xpath = f'xpath:./following::{loc}'
        return eles1 + self.parent_ele._ele(xpath, single=False, relative=True)

    def ele(self, loc_or_str, timeout=None):
        """返回当前元素下级符合条件的第一个元素
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: ChromiumElement对象
        """
        return self._ele(loc_or_str, timeout, method='ele()')

    def eles(self, loc_or_str, timeout=None):
        """返回当前元素下级所有符合条件的子元素
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: ChromiumElement对象组成的列表
        """
        return self._ele(loc_or_str, timeout=timeout, single=False)

    def s_ele(self, loc_or_str=None):
        """查找第一个符合条件的元素以SessionElement形式返回，处理复杂页面时效率很高
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        r = make_session_ele(self, loc_or_str)
        if isinstance(r, NoneElement):
            r.method = 's_ele()'
            r.args = {'loc_or_str': loc_or_str}
        return r

    def s_eles(self, loc_or_str):
        """查找所有符合条件的元素以SessionElement列表形式返回，处理复杂页面时效率很高
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象
        """
        return make_session_ele(self, loc_or_str, single=False)

    def _find_elements(self, loc_or_str, timeout=None, single=True, relative=False, raise_err=None):
        """返回当前元素下级符合条件的子元素、属性或节点文本，默认返回第一个
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :param single: True则返回第一个，False则返回全部
        :param relative: WebPage用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: ChromiumElement对象或其组成的列表
        """
        loc = get_loc(loc_or_str)
        if loc[0] == 'css selector' and str(loc[1]).startswith(':root'):
            loc = loc[0], loc[1][5:]

        timeout = timeout if timeout is not None else self.page.timeout
        end_time = perf_counter() + timeout
        eles = make_session_ele(self.html).eles(loc)
        while not eles and perf_counter() <= end_time:
            eles = make_session_ele(self.html).eles(loc)

        if not eles:
            return NoneElement() if single else eles

        css_paths = [i.css_path[47:] for i in eles]
        if single:
            node_id = self.page.run_cdp('DOM.querySelector', nodeId=self._node_id, selector=css_paths[0])['nodeId']
            return make_chromium_ele(self.page, node_id=node_id) if node_id else NoneElement()

        else:
            results = []
            for i in css_paths:
                node_id = self.page.run_cdp('DOM.querySelector', nodeId=self._node_id, selector=i)['nodeId']
                if node_id:
                    results.append(make_chromium_ele(self.page, node_id=node_id))
            return results

    def _get_node_id(self, obj_id):
        """返回元素node id"""
        return self.page.run_cdp('DOM.requestNode', objectId=obj_id)['nodeId']

    def _get_obj_id(self, back_id):
        """返回元素object id"""
        return self.page.run_cdp('DOM.resolveNode', backendNodeId=back_id)['object']['objectId']

    def _get_backend_id(self, node_id):
        """返回元素object id"""
        r = self.page.run_cdp('DOM.describeNode', nodeId=node_id)['node']
        self._tag = r['localName'].lower()
        return r['backendNodeId']


def find_in_chromium_ele(ele, loc, single=True, timeout=None, relative=True):
    """在chromium元素中查找
    :param ele: ChromiumElement对象
    :param loc: 元素定位元组
    :param single: True则返回第一个，False则返回全部
    :param timeout: 查找元素超时时间
    :param relative: WebPage用于标记是否相对定位使用
    :return: 返回ChromiumElement元素或它们组成的列表
    """
    # ---------------处理定位符---------------
    if isinstance(loc, (str, tuple)):
        loc = get_loc(loc)
    else:
        raise ValueError(f"定位符必须为str或长度为2的tuple对象。现在是：{loc}")

    loc_str = loc[1]
    if loc[0] == 'xpath' and loc[1].lstrip().startswith('/'):
        loc_str = f'.{loc_str}'
    elif loc[0] == 'css selector' and loc[1].lstrip().startswith('>'):
        loc_str = f'{ele.css_path}{loc[1]}'
    loc = loc[0], loc_str

    timeout = timeout if timeout is not None else ele.page.timeout

    # ---------------执行查找-----------------
    if loc[0] == 'xpath':
        return find_by_xpath(ele, loc[1], single, timeout, relative=relative)

    else:
        return find_by_css(ele, loc[1], single, timeout)


def find_by_xpath(ele, xpath, single, timeout, relative=True):
    """执行用xpath在元素中查找元素
    :param ele: 在此元素中查找
    :param xpath: 查找语句
    :param single: 是否只返回第一个结果
    :param timeout: 超时时间
    :param relative: 是否相对定位
    :return: ChromiumElement或其组成的列表
    """
    type_txt = '9' if single else '7'
    node_txt = 'this.contentDocument' if ele.tag in __FRAME_ELEMENT__ and not relative else 'this'
    js = make_js_for_find_ele_by_xpath(xpath, type_txt, node_txt)
    r = ele.page.run_cdp_loaded('Runtime.callFunctionOn', functionDeclaration=js, objectId=ele._obj_id,
                                returnByValue=False, awaitPromise=True, userGesture=True)
    if r['result']['type'] == 'string':
        return r['result']['value']

    if 'exceptionDetails' in r:
        if 'The result is not a node set' in r['result']['description']:
            js = make_js_for_find_ele_by_xpath(xpath, '1', node_txt)
            r = ele.page.run_cdp_loaded('Runtime.callFunctionOn', functionDeclaration=js, objectId=ele._obj_id,
                                        returnByValue=False, awaitPromise=True, userGesture=True)
            return r['result']['value']
        else:
            raise SyntaxError(f'查询语句错误：\n{r}')

    end_time = perf_counter() + timeout
    while (r['result']['subtype'] == 'null'
           or r['result']['description'] == 'NodeList(0)') and perf_counter() < end_time:
        r = ele.page.run_cdp_loaded('Runtime.callFunctionOn', functionDeclaration=js, objectId=ele._obj_id,
                                    returnByValue=False, awaitPromise=True, userGesture=True)

    if single:
        return NoneElement() if r['result']['subtype'] == 'null' \
            else make_chromium_ele(ele.page, obj_id=r['result']['objectId'])

    if r['result']['description'] == 'NodeList(0)':
        return []
    else:
        r = ele.page.run_cdp_loaded('Runtime.getProperties', objectId=r['result']['objectId'],
                                    ownProperties=True)['result']
        return [make_chromium_ele(ele.page, obj_id=i['value']['objectId'])
                if i['value']['type'] == 'object' else i['value']['value']
                for i in r[:-1]]


def find_by_css(ele, selector, single, timeout):
    """执行用css selector在元素中查找元素
    :param ele: 在此元素中查找
    :param selector: 查找语句
    :param single: 是否只返回第一个结果
    :param timeout: 超时时间
    :return: ChromiumElement或其组成的列表
    """
    selector = selector.replace('"', r'\"')
    find_all = '' if single else 'All'
    node_txt = 'this.contentDocument' if ele.tag in ('iframe', 'frame', 'shadow-root') else 'this'
    js = f'function(){{return {node_txt}.querySelector{find_all}("{selector}");}}'
    r = ele.page.run_cdp_loaded('Runtime.callFunctionOn', functionDeclaration=js, objectId=ele._obj_id,
                                returnByValue=False, awaitPromise=True, userGesture=True)

    end_time = perf_counter() + timeout
    while ('exceptionDetails' in r or r['result']['subtype'] == 'null' or
           r['result']['description'] == 'NodeList(0)') and perf_counter() < end_time:
        r = ele.page.run_cdp_loaded('Runtime.callFunctionOn', functionDeclaration=js, objectId=ele._obj_id,
                                    returnByValue=False, awaitPromise=True, userGesture=True)

    if 'exceptionDetails' in r:
        raise SyntaxError(f'查询语句错误：\n{r}')

    if single:
        return NoneElement() if r['result']['subtype'] == 'null' \
            else make_chromium_ele(ele.page, obj_id=r['result']['objectId'])

    if r['result']['description'] == 'NodeList(0)':
        return []
    else:
        r = ele.page.run_cdp_loaded('Runtime.getProperties', objectId=r['result']['objectId'],
                                    ownProperties=True)['result']
        return [make_chromium_ele(ele.page, obj_id=i['value']['objectId']) for i in r]


def make_chromium_ele(page, node_id=None, obj_id=None):
    """根据node id或object id生成相应元素对象
    :param page: ChromiumPage对象
    :param node_id: 元素的node id
    :param obj_id: 元素的object id
    :return: ChromiumElement对象或ChromiumFrame对象
    """
    if node_id:
        node = page.run_cdp('DOM.describeNode', nodeId=node_id)
        if node['node']['nodeName'] in ('#text', '#comment'):
            return node['node']['nodeValue']
        backend_id = node['node']['backendNodeId']
        obj_id = page.run_cdp('DOM.resolveNode', nodeId=node_id)['object']['objectId']

    elif obj_id:
        node = page.run_cdp('DOM.describeNode', objectId=obj_id)
        if node['node']['nodeName'] in ('#text', '#comment'):
            return node['node']['nodeValue']
        backend_id = node['node']['backendNodeId']
        node_id = node['node']['nodeId']

    else:
        raise ElementLossError

    ele = ChromiumElement(page, obj_id=obj_id, node_id=node_id, backend_id=backend_id)
    if ele.tag in __FRAME_ELEMENT__:
        from .._pages.chromium_frame import ChromiumFrame
        ele = ChromiumFrame(page, ele)

    return ele


def make_js_for_find_ele_by_xpath(xpath, type_txt, node_txt):
    """生成用xpath在元素中查找元素的js文本
    :param xpath: xpath文本
    :param type_txt: 查找类型
    :param node_txt: 节点类型
    :return: js文本
    """
    for_txt = ''

    # 获取第一个元素、节点或属性
    if type_txt == '9':
        return_txt = '''
if(e.singleNodeValue==null){return null;}
else if(e.singleNodeValue.constructor.name=="Text"){return e.singleNodeValue.data;}
else if(e.singleNodeValue.constructor.name=="Attr"){return e.singleNodeValue.nodeValue;}
else if(e.singleNodeValue.constructor.name=="Comment"){return e.singleNodeValue.nodeValue;}
else{return e.singleNodeValue;}'''

    # 按顺序获取所有元素、节点或属性
    elif type_txt == '7':
        for_txt = """
var a=new Array();
for(var i = 0; i <e.snapshotLength ; i++){
if(e.snapshotItem(i).constructor.name=="Text"){a.push(e.snapshotItem(i).data);}
else if(e.snapshotItem(i).constructor.name=="Attr"){a.push(e.snapshotItem(i).nodeValue);}
else if(e.snapshotItem(i).constructor.name=="Comment"){a.push(e.snapshotItem(i).nodeValue);}
else{a.push(e.snapshotItem(i));}}"""
        return_txt = 'return a;'

    elif type_txt == '2':
        return_txt = 'return e.stringValue;'
    elif type_txt == '1':
        return_txt = 'return e.numberValue;'
    else:
        return_txt = 'return e.singleNodeValue;'

    xpath = xpath.replace(r"'", r"\'")
    js = f'function(){{var e=document.evaluate(\'{xpath}\',{node_txt},null,{type_txt},null);\n{for_txt}\n{return_txt}}}'

    return js


def run_js(page_or_ele, script, as_expr=False, timeout=None, args=None):
    """运行javascript代码
    :param page_or_ele: 页面对象或元素对象
    :param script: js文本
    :param as_expr: 是否作为表达式运行，为True时args无效
    :param timeout: 超时时间
    :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
    :return: js执行结果
    """
    if isinstance(page_or_ele, (ChromiumElement, ChromiumShadowRoot)):
        page = page_or_ele.page
        obj_id = page_or_ele._obj_id
        is_page = False
    else:
        page = page_or_ele
        obj_id = page_or_ele._root_id
        is_page = True

    if page.has_alert:
        raise AlertExistsError

    try:
        if as_expr:
            res = page.run_cdp('Runtime.evaluate', expression=script, returnByValue=False,
                               awaitPromise=True, userGesture=True, _timeout=timeout)

        else:
            args = args or ()
            if not is_js_func(script):
                script = f'function(){{{script}}}'
            res = page.run_cdp('Runtime.callFunctionOn', functionDeclaration=script, objectId=obj_id,
                               arguments=[convert_argument(arg) for arg in args], returnByValue=False,
                               awaitPromise=True, userGesture=True, _timeout=timeout)

    except ContextLossError:
        if is_page:
            raise ContextLossError('页面已被刷新，请尝试等待页面加载完成再执行操作。')
        else:
            raise ElementLossError('原来获取到的元素对象已不在页面内。')

    if res is None and page.driver.has_alert:  # 存在alert的情况
        return None

    exceptionDetails = res.get('exceptionDetails')
    if exceptionDetails:
        raise JavaScriptError(f'\njavascript运行错误：\n{script}\n错误信息: \n{exceptionDetails}')

    try:
        return parse_js_result(page, page_or_ele, res.get('result'))
    except Exception:
        return res


def parse_js_result(page, ele, result):
    """解析js返回的结果"""
    if 'unserializableValue' in result:
        return result['unserializableValue']

    the_type = result['type']

    if the_type == 'object':
        sub_type = result.get('subtype', None)
        if sub_type == 'null':
            return None

        elif sub_type == 'node':
            class_name = result['className']
            if class_name == 'ShadowRoot':
                return ChromiumShadowRoot(ele, obj_id=result['objectId'])
            elif class_name == 'HTMLDocument':
                return result
            else:
                return make_chromium_ele(page, obj_id=result['objectId'])

        elif sub_type == 'array':
            r = page.run_cdp('Runtime.getProperties', objectId=result['objectId'],
                             ownProperties=True)['result']
            return [parse_js_result(page, ele, result=i['value']) for i in r[:-1]]

        elif 'objectId' in result and result['className'].lower() == 'object':  # dict
            r = page.run_cdp('Runtime.getProperties', objectId=result['objectId'],
                             ownProperties=True)['result']
            return {i['name']: parse_js_result(page, ele, result=i['value']) for i in r}

        else:
            return result['value']

    elif the_type == 'undefined':
        return None

    else:
        return result['value']


def convert_argument(arg):
    """把参数转换成js能够接收的形式"""
    if isinstance(arg, ChromiumElement):
        return {'objectId': arg._obj_id}

    elif isinstance(arg, (int, float, str, bool)):
        return {'value': arg}

    from math import inf
    if arg == inf:
        return {'unserializableValue': 'Infinity'}
    if arg == -inf:
        return {'unserializableValue': '-Infinity'}


def send_enter(ele):
    """发送回车"""
    data = {'type': 'keyDown', 'modifiers': 0, 'windowsVirtualKeyCode': 13, 'code': 'Enter', 'key': 'Enter',
            'text': '\r', 'autoRepeat': False, 'unmodifiedText': '\r', 'location': 0, 'isKeypad': False}

    ele.page.run_cdp('Input.dispatchKeyEvent', **data)
    data['type'] = 'keyUp'
    ele.page.run_cdp('Input.dispatchKeyEvent', **data)


def send_key(ele, modifier, key):
    """发送一个字，在键盘中的字符触发按键，其它直接发送文本"""
    if key not in keyDefinitions:
        ele.page.run_cdp('Input.insertText', text=key)

    else:
        description = keyDescriptionForString(modifier, key)
        text = description['text']
        data = {'type': 'keyDown' if text else 'rawKeyDown',
                'modifiers': modifier,
                'windowsVirtualKeyCode': description['keyCode'],
                'code': description['code'],
                'key': description['key'],
                'text': text,
                'autoRepeat': False,
                'unmodifiedText': text,
                'location': description['location'],
                'isKeypad': description['location'] == 3}

        ele.page.run_cdp('Input.dispatchKeyEvent', **data)
        data['type'] = 'keyUp'
        ele.page.run_cdp('Input.dispatchKeyEvent', **data)


class Pseudo(object):
    def __init__(self, ele):
        """
        :param ele: ChromiumElement
        """
        self._ele = ele

    @property
    def before(self):
        """返回当前元素的::before伪元素内容"""
        return self._ele.style('content', 'before')

    @property
    def after(self):
        """返回当前元素的::after伪元素内容"""
        return self._ele.style('content', 'after')
