# -*- coding:utf-8 -*-
from time import sleep, perf_counter

from .commons.constants import Settings
from .errors import WaitTimeoutError


class ChromiumBaseWaiter(object):
    def __init__(self, page_or_ele):
        """
        :param page_or_ele: 页面对象或元素对象
        """
        self._driver = page_or_ele

    def ele_delete(self, loc_or_ele, timeout=None, raise_err=None):
        """等待元素从DOM中删除
        :param loc_or_ele: 要等待的元素，可以是已有元素、定位符
        :param timeout: 超时时间，默认读取页面超时时间
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        ele = self._driver._ele(loc_or_ele, raise_err=False, timeout=0)
        return ele.wait.delete(timeout, raise_err=raise_err) if ele else True

    def ele_display(self, loc_or_ele, timeout=None, raise_err=None):
        """等待元素变成显示状态
        :param loc_or_ele: 要等待的元素，可以是已有元素、定位符
        :param timeout: 超时时间，默认读取页面超时时间
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        ele = self._driver._ele(loc_or_ele, raise_err=False, timeout=0)
        return ele.wait.display(timeout, raise_err=raise_err)

    def ele_hidden(self, loc_or_ele, timeout=None, raise_err=None):
        """等待元素变成隐藏状态
        :param loc_or_ele: 要等待的元素，可以是已有元素、定位符
        :param timeout: 超时时间，默认读取页面超时时间
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        ele = self._driver._ele(loc_or_ele, raise_err=False, timeout=0)
        return ele.wait.hidden(timeout, raise_err=raise_err)

    def ele_load(self, loc, timeout=None, raise_err=None):
        """等待元素加载到DOM
        :param loc: 要等待的元素，输入定位符
        :param timeout: 超时时间，默认读取页面超时时间
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ele = self._driver._ele(loc, raise_err=False, timeout=timeout)
        if ele:
            return True
        if raise_err is True or Settings.raise_when_wait_failed is True:
            raise WaitTimeoutError('等待元素加载失败。')
        else:
            return False

    def load_start(self, timeout=None, raise_err=None):
        """等待页面开始加载
        :param timeout: 超时时间，为None时使用页面timeout属性
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        return self._loading(timeout=timeout, gap=.002, raise_err=raise_err)

    def load_complete(self, timeout=None, raise_err=None):
        """等待页面开始加载
        :param timeout: 超时时间，为None时使用页面timeout属性
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        return self._loading(timeout=timeout, start=False, raise_err=raise_err)

    def upload_paths_inputted(self):
        """等待自动填写上传文件路径"""
        while self._driver._upload_list:
            sleep(.01)

    def _loading(self, timeout=None, start=True, gap=.01, raise_err=None):
        """等待页面开始加载或加载完成
        :param timeout: 超时时间，为None时使用页面timeout属性
        :param start: 等待开始还是结束
        :param gap: 间隔秒数
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        if timeout != 0:
            if timeout is None or timeout is True:
                timeout = self._driver.timeout
            end_time = perf_counter() + timeout
            while perf_counter() < end_time:
                if self._driver.is_loading == start:
                    return True
                sleep(gap)

            if raise_err is True or Settings.raise_when_wait_failed is True:
                raise WaitTimeoutError('等待页面加载失败。')
            else:
                return False


class ChromiumPageWaiter(ChromiumBaseWaiter):
    def __init__(self, page):
        super().__init__(page)
        # self._listener = None

    def new_tab(self, timeout=None, raise_err=None):
        """等待新标签页出现
        :param timeout: 等待超时时间，为None则使用页面对象timeout属性
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等到新标签页出现
        """
        timeout = timeout if timeout is not None else self._driver.timeout
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if self._driver.tab_id != self._driver.latest_tab:
                return True
            sleep(.01)

        if raise_err is True or Settings.raise_when_wait_failed is True:
            raise WaitTimeoutError('等待新标签页失败。')
        else:
            return False


class ChromiumElementWaiter(object):
    """等待元素在dom中某种状态，如删除、显示、隐藏"""

    def __init__(self, page, ele):
        """等待元素在dom中某种状态，如删除、显示、隐藏
        :param page: 元素所在页面
        :param ele: 要等待的元素
        """
        self._page = page
        self._ele = ele

    def delete(self, timeout=None, raise_err=None):
        """等待元素从dom删除
        :param timeout: 超时时间，为None使用元素所在页面timeout属性
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        return self._wait_state('is_alive', False, timeout, raise_err)

    def display(self, timeout=None, raise_err=None):
        """等待元素从dom显示
        :param timeout: 超时时间，为None使用元素所在页面timeout属性
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        return self._wait_state('is_displayed', True, timeout, raise_err)

    def hidden(self, timeout=None, raise_err=None):
        """等待元素从dom隐藏
        :param timeout: 超时时间，为None使用元素所在页面timeout属性
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        return self._wait_state('is_displayed', False, timeout, raise_err)

    def covered(self, timeout=None, raise_err=None):
        """等待当前元素被遮盖
        :param timeout:超时时间，为None使用元素所在页面timeout属性
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        return self._wait_state('is_covered', True, timeout, raise_err)

    def not_covered(self, timeout=None, raise_err=None):
        """等待当前元素被遮盖
        :param timeout:超时时间，为None使用元素所在页面timeout属性
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        return self._wait_state('is_covered', False, timeout, raise_err)

    def enabled(self, timeout=None, raise_err=None):
        """等待当前元素变成可用
        :param timeout:超时时间，为None使用元素所在页面timeout属性
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        return self._wait_state('is_enabled', True, timeout, raise_err)

    def disabled(self, timeout=None, raise_err=None):
        """等待当前元素变成可用
        :param timeout:超时时间，为None使用元素所在页面timeout属性
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        return self._wait_state('is_enabled', False, timeout, raise_err)

    def disabled_or_delete(self, timeout=None, raise_err=None):
        """等待当前元素变成不可用或从DOM移除
        :param timeout:超时时间，为None使用元素所在页面timeout属性
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        if timeout is None:
            timeout = self._page.timeout
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if not self._ele.states.is_enabled or not self._ele.states.is_alive:
                return True
            sleep(.05)

        if raise_err is True or Settings.raise_when_wait_failed is True:
            raise WaitTimeoutError('等待元素隐藏或删除失败。')
        else:
            return False

    def _wait_state(self, attr, mode=False, timeout=None, raise_err=None):
        """等待元素某个bool状态到达指定状态
        :param attr: 状态名称
        :param mode: True或False
        :param timeout: 超时时间，为None使用元素所在页面timeout属性
        :param raise_err: 等待识别时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        if timeout is None:
            timeout = self._page.timeout
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if self._ele.states.__getattribute__(attr) == mode:
                return True
            sleep(.05)

        if raise_err is True or Settings.raise_when_wait_failed is True:
            raise WaitTimeoutError('等待元素状态改变失败。')
        else:
            return False


class FrameWaiter(ChromiumBaseWaiter, ChromiumElementWaiter):
    def __init__(self, frame):
        """
        :param frame: ChromiumFrame对象
        """
        super().__init__(frame)
        super(ChromiumBaseWaiter, self).__init__(frame, frame.frame_ele)