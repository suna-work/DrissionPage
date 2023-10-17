from pathlib import Path
from typing import Dict, Optional, Union

from chromium_page import ChromiumPage


class BrowserDownloadManager(object):
    BROWSERS: Dict[str, BrowserDownloadManager] = ...
    _page: ChromiumPage = ...
    _missions: Dict[str, DownloadMission] = ...
    _tab_missions: dict = ...
    _tabs_settings: Dict[str, TabDownloadSettings] = ...
    _guid_and_tab: Dict[str, str] = ...
    _flags: dict = ...

    def __new__(cls, page: ChromiumPage): ...

    def __init__(self, page: ChromiumPage): ...

    @property
    def missions(self) -> Dict[str, DownloadMission]: ...

    def set_path(self, tab_id: str, path: Union[Path, str]) -> None: ...

    def set_rename(self, tab_id: str, rename: str) -> None: ...

    def set_file_exists(self, tab_id: str, mode: str) -> None: ...

    def set_flag(self, tab_id: str, flag: Optional[bool, DownloadMission]) -> None: ...

    def get_flag(self, tab_id: str) -> Optional[bool, DownloadMission]: ...

    def get_tab_missions(self, tab_id: str) -> list: ...

    def set_mission(self, tab_id: str, guid: str) -> None: ...

    def set_done(self, mission: DownloadMission, state: str, final_path: str = None) -> None: ...

    def cancel(self, mission: DownloadMission, state: str) -> None: ...

    def _onDownloadWillBegin(self, **kwargs) -> None: ...

    def _onDownloadProgress(self, **kwargs) -> None: ...


class TabDownloadSettings(object):
    TABS: dict = ...
    tab_id: str = ...
    waiting_flag: Optional[bool, dict] = ...
    rename: Optional[str] = ...
    path: Optional[str] = ...
    when_file_exists: str = ...

    def __init__(self, tab_id: str): ...


class DownloadMission(object):
    tab_id: str = ...
    _mgr: BrowserDownloadManager = ...
    url: str = ...
    id: str = ...
    path: str = ...
    name: str = ...
    state: str = ...
    total_bytes: Optional[int] = ...
    received_bytes: int = ...
    final_path: Optional[str] = ...

    def __init__(self, mgr: BrowserDownloadManager, tab_id: str, _id: str, path: str, name: str, url: str): ...

    @property
    def rate(self) -> float: ...

    @property
    def is_done(self) -> bool: ...

    def cancel(self) -> None: ...

    def wait(self, show: bool = True, timeout=None, cancel_if_timeout=True) -> Union[bool, str]: ...
