from pathlib import Path
from typing import Dict, Optional, Union, Literal

from .._base.browser import Browser
from .._pages.chromium_page import ChromiumPage


class BrowserDownloadManager(object):
    _browser: Browser = ...
    _page: ChromiumPage = ...
    _missions: Dict[str, DownloadMission] = ...
    _tab_missions: dict = ...
    _flags: dict = ...

    def __init__(self, browser: Browser): ...

    @property
    def missions(self) -> Dict[str, DownloadMission]: ...

    def set_path(self, tab_id: str, path: Union[Path, str]) -> None: ...

    def set_rename(self, tab_id: str, rename: str) -> None: ...

    def set_file_exists(self, tab_id: str, mode: Literal['rename', 'skip', 'overwrite']) -> None: ...

    def set_flag(self, tab_id: str, flag: Optional[bool, DownloadMission]) -> None: ...

    def get_flag(self, tab_id: str) -> Optional[bool, DownloadMission]: ...

    def get_tab_missions(self, tab_id: str) -> list: ...

    def set_done(self, mission: DownloadMission, state: str, final_path: str = None) -> None: ...

    def cancel(self, mission: DownloadMission) -> None: ...

    def skip(self, mission: DownloadMission) -> None: ...

    def clear_tab_info(self, tab_id: str) -> None: ...

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
    save_path: str = ...
    _is_done: bool = ...

    def __init__(self, mgr: BrowserDownloadManager, tab_id: str, _id: str, path: str, name: str, url: str,
                 save_path: str): ...

    @property
    def rate(self) -> float: ...

    @property
    def is_done(self) -> bool: ...

    def cancel(self) -> None: ...

    def wait(self, show: bool = True, timeout=None, cancel_if_timeout=True) -> Union[bool, str]: ...