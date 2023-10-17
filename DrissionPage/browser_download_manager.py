# -*- coding:utf-8 -*-
from pathlib import Path
from shutil import move
from time import sleep, perf_counter

from .commons.tools import get_usable_path


class BrowserDownloadManager(object):
    BROWSERS = {}

    def __new__(cls, page):
        """
        :param page: ChromiumPage对象
        """
        if page.browser_driver.id in cls.BROWSERS:
            return cls.BROWSERS[page.browser_driver.id]
        return object.__new__(cls)

    def __init__(self, page):
        """
        :param page: ChromiumPage对象
        """
        if hasattr(self, '_created'):
            return
        self._created = True

        self._page = page
        self._when_download_file_exists = 'rename'

        t = TabDownloadSettings(page.tab_id)
        t.path = page.download_path
        self._tabs_settings = {page.tab_id: t}  # {tab_id: TabDownloadSettings}
        self._missions = {}  # {guid: DownloadMission}
        self._tab_missions = {}  # {tab_id: DownloadMission}
        self._guid_and_tab = {}  # 记录guid在哪个tab
        self._flags = {}  # {tab_id: [bool, DownloadMission]}

        self._page.browser_driver.set_listener('Browser.downloadProgress', self._onDownloadProgress)
        self._page.browser_driver.set_listener('Browser.downloadWillBegin', self._onDownloadWillBegin)
        self._page.browser_driver.call_method('Browser.setDownloadBehavior',
                                              downloadPath=self._page.download_path,
                                              behavior='allowAndName', eventsEnabled=True)

        BrowserDownloadManager.BROWSERS[page.browser_driver.id] = self

    @property
    def missions(self):
        """返回所有未完成的下载任务"""
        return self._missions

    def set_path(self, tab_id, path):
        """设置某个tab的下载路径
        :param tab_id: tab id
        :param path: 下载路径
        :return: None
        """
        self._tabs_settings.setdefault(tab_id, TabDownloadSettings(tab_id)).path = str(Path(path).absolute())
        if tab_id == self._page.tab_id:
            self._page.browser_driver.call_method('Browser.setDownloadBehavior',
                                                  downloadPath=str(Path(path).absolute()),
                                                  behavior='allowAndName', eventsEnabled=True)

    def set_rename(self, tab_id, rename):
        """设置某个tab的重命名文件名
        :param tab_id: tab id
        :param rename: 文件名
        :return: None
        """
        self._tabs_settings.setdefault(tab_id, TabDownloadSettings(tab_id)).rename = rename

    def set_file_exists(self, tab_id, mode):
        """设置某个tab下载文件重名时执行的策略
        :param tab_id: tab id
        :param mode: 下载路径
        :return: None
        """
        self._tabs_settings.setdefault(tab_id, TabDownloadSettings(tab_id)).when_file_exists = mode

    def set_flag(self, tab_id, flag):
        """设置某个tab的重命名文件名
        :param tab_id: tab id
        :param flag: 等待标志
        :return: None
        """
        self._flags[tab_id] = flag

    def get_flag(self, tab_id):
        """获取tab下载等待标记
        :param tab_id: tab id
        :return: 任务对象或False
        """
        return self._flags.get(tab_id, None)

    def get_tab_missions(self, tab_id):
        """获取某个tab正在下载的任务
        :param tab_id:
        :return: 下载任务组成的列表
        """
        return self._tab_missions.get(tab_id, [])

    def set_mission(self, tab_id, guid):
        """绑定tab和下载任务信息
        :param tab_id: tab id
        :param guid: 下载任务id
        :return: None
        """
        self._guid_and_tab[guid] = tab_id

    def set_done(self, mission, state, final_path=None):
        """设置任务结束
        :param mission: 任务对象
        :param state: 任务状态
        :param final_path: 最终路径
        :return: None
        """
        if mission.state not in ('canceled', 'skipped'):
            mission.state = state
        mission.final_path = final_path
        if mission.tab_id in self._tab_missions:
            self._tab_missions[mission.tab_id].remove(mission.id)
        self._missions.pop(mission.id)

    def cancel(self, mission, state):
        """取消任务
        :param mission: 任务对象
        :param state: 任务状态
        :return: None
        """
        mission.state = state
        self._page.browser_driver.call_method('Browser.cancelDownload', guid=mission.id)
        if mission.final_path:
            Path(mission.final_path).unlink(True)

    def _onDownloadWillBegin(self, **kwargs):
        """用于获取弹出新标签页触发的下载任务"""
        guid = kwargs['guid']
        end = perf_counter() + .3
        while perf_counter() < end:
            tab_id = self._guid_and_tab.get(guid, None)
            if tab_id:
                break
            sleep(.005)
        else:
            tab_id = self._page.tab_id

        settings = TabDownloadSettings(tab_id)
        if settings.rename:
            tmp = kwargs['suggestedFilename'].rsplit('.', 1)
            ext_name = tmp[-1] if len(tmp) > 1 else ''
            tmp = settings.rename.rsplit('.', 1)
            ext_rename = tmp[-1] if len(tmp) > 1 else ''
            name = settings.rename if ext_rename == ext_name else f'{settings.rename}.{ext_name}'
            settings.rename = None

        else:
            name = kwargs['suggestedFilename']

        skip = False
        goal_path = Path(settings.path) / name
        if goal_path.exists():
            if settings.when_file_exists == 'skip':
                skip = True
            elif settings.when_file_exists == 'overwrite':
                goal_path.unlink()

        m = DownloadMission(self, tab_id, guid, settings.path, name, kwargs['url'])
        self._missions[guid] = m

        if self.get_flag(tab_id) is False:  # 取消该任务
            self.cancel(m, 'canceled')
        elif skip:
            self.cancel(m, 'skipped')
        else:
            self._tab_missions.setdefault(tab_id, []).append(guid)

        self._flags[tab_id] = m

    def _onDownloadProgress(self, **kwargs):
        """下载状态变化时执行"""
        if kwargs['guid'] in self._missions:
            mission = self._missions[kwargs['guid']]
            if kwargs['state'] == 'inProgress':
                mission.state = 'running'
                mission.received_bytes = kwargs['receivedBytes']
                mission.total_bytes = kwargs['totalBytes']

            elif kwargs['state'] == 'completed':
                mission.received_bytes = kwargs['receivedBytes']
                mission.total_bytes = kwargs['totalBytes']
                form_path = f'{self._page.download_path}\\{mission.id}'
                to_path = str(get_usable_path(f'{mission.path}\\{mission.name}'))
                move(form_path, to_path)
                self.set_done(mission, 'completed', final_path=to_path)

            else:  # 'canceled'
                self.set_done(mission, 'canceled')


class TabDownloadSettings(object):
    TABS = {}

    def __new__(cls, tab_id):
        """
        :param tab_id: tab id
        """
        if tab_id in cls.TABS:
            return cls.TABS[tab_id]
        return object.__new__(cls)

    def __init__(self, tab_id):
        """
        :param tab_id: tab id
        """
        if hasattr(self, '_created'):
            return
        self._created = True
        self.tab_id = tab_id
        self.rename = None
        self.path = ''
        self.when_file_exists = 'rename'

        TabDownloadSettings.TABS[tab_id] = self


class DownloadMission(object):
    def __init__(self, mgr, tab_id, _id, path, name, url):
        self._mgr = mgr
        self.url = url
        self.tab_id = tab_id
        self.id = _id
        self.path = path
        self.name = name
        self.state = 'waiting'
        self.total_bytes = None
        self.received_bytes = 0
        self.final_path = None

    def __repr__(self):
        return f'<DownloadMission {id(self)} {self.rate}>'

    @property
    def rate(self):
        """以百分比形式返回下载进度"""
        return round((self.received_bytes / self.total_bytes) * 100, 2) if self.total_bytes else None

    @property
    def is_done(self):
        """返回任务是否在运行中"""
        return self.state == 'completed'

    def cancel(self):
        """取消该任务，如任务已完成，删除已下载的文件"""
        self._mgr.cancel(self, state='canceled')

    def wait(self, show=True, timeout=None, cancel_if_timeout=True):
        """等待任务结束
        :param show: 是否显示下载信息
        :param timeout: 超时时间，为None则无限等待
        :param cancel_if_timeout: 超时时是否取消任务
        :return: 等待成功返回完整路径，否则返回False
        """
        if show:
            print(f'url：{self.url}')
            t2 = perf_counter()
            while self.name is None and perf_counter() - t2 < 4:
                sleep(0.01)
            print(f'文件名：{self.name}')
            print(f'目标路径：{self.path}')

        if timeout is None:
            while self.id in self._mgr.missions:
                if show:
                    print(f'\r{self.rate}% ', end='')
                sleep(.2)

        else:
            running = True
            end_time = perf_counter() + timeout
            while perf_counter() < end_time:
                if show:
                    print(f'\r{self.rate}% ', end='')
                if self.id not in self._mgr.missions:
                    running = False
                    break
                sleep(.2)

            if running and cancel_if_timeout:
                self.cancel()

        if show:
            if self.state == 'completed':
                print(f'下载完成 {self.final_path}')
            elif self.state == 'canceled':
                print(f'下载取消')
            elif self.state == 'skipped':
                print(f'已跳过')
            print()

        return self.final_path if self.final_path else False
