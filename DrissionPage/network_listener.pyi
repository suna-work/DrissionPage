from queue import Queue
from typing import Union, Dict, List, Iterable, Tuple

from requests.structures import CaseInsensitiveDict

from chromium_base import ChromiumBase
from chromium_driver import ChromiumDriver


class NetworkListener(object):
    def __init__(self, page: ChromiumBase):
        self._page: ChromiumBase = ...
        self._total_count: int = ...
        self._caught_count: int = ...
        self._targets: Union[str, dict] = ...
        self._results: list = ...
        self._method: set = ...
        self._tmp: Queue = ...
        self._is_regex: bool = ...
        self._driver: ChromiumDriver = ...
        self._request_ids: dict = ...
        self.listening: bool = ...
        self._timeout: float = ...
        self._begin_time: float = ...

    def set_targets(self, targets: Union[str, list, tuple, set, None] = None, is_regex: bool = False,
                    count: int = None, method: Union[str, list, tuple, set] = None) -> None: ...

    def start(self) -> None: ...

    def stop(self) -> None: ...

    @property
    def results(self) -> Union[DataPacket, Dict[str, List[DataPacket]], False]: ...

    def clear(self) -> None: ...

    def listen(self, targets: Union[str, List[str], Tuple, bool, None] = ..., count: int = ...,
               timeout: float = ...) -> Union[DataPacket, Dict[str, List[DataPacket]], False]: ...

    def _listen(self, timeout: float = None,
                any_one: bool = False) -> Union[DataPacket, Dict[str, List[DataPacket]], False]: ...

    def _requestWillBeSent(self, **kwargs) -> None: ...

    def _response_received(self, **kwargs) -> None: ...

    def _loading_finished(self, **kwargs) -> None: ...

    def _loading_failed(self, **kwargs) -> None: ...

    def _request_paused(self, **kwargs) -> None: ...

    def _wait_to_stop(self) -> None: ...

    def _is_continue(self) -> bool: ...

    def steps(self, gap=1) -> Iterable[Union[DataPacket, List[DataPacket]]]: ...

    def _set_callback_func(self) -> None: ...

    def _stop(self) -> None: ...


class DataPacket(object):
    """返回的数据包管理类"""

    def __init__(self, tab: str, target: str, raw_info: dict):
        self.tab: str = ...
        self.target: str = ...
        self._raw_request: dict = ...
        self._raw_response: dict = ...
        self._raw_post_data: str = ...
        self._raw_body: str = ...
        self._base64_body: bool = ...
        self._request: Request = ...
        self._response: Response = ...
        self.errorText: str = ...
        self._resource_type: str = ...

    @property
    def url(self) -> str: ...

    @property
    def method(self) -> str: ...

    @property
    def frameId(self) -> str: ...

    @property
    def resourceType(self) -> str: ...

    @property
    def request(self) -> Request: ...

    @property
    def response(self) -> Response: ...


class Request(object):
    url: str = ...
    _headers: Union[CaseInsensitiveDict, None] = ...
    method: str = ...

    # urlFragment: str = ...
    # postDataEntries: list = ...
    # mixedContentType: str = ...
    # initialPriority: str = ...
    # referrerPolicy: str = ...
    # isLinkPreload: bool = ...
    # trustTokenParams: dict = ...
    # isSameSite: bool = ...

    def __init__(self, raw_request: dict, post_data: str):
        self._request: dict = ...
        self._raw_post_data: str = ...
        self._postData: str = ...

    @property
    def headers(self) -> dict: ...

    @property
    def postData(self) -> Union[str, dict]: ...


class Response(object):
    status: str = ...
    statusText: int = ...
    mimeType: str = ...

    def __init__(self, raw_response: dict, raw_body: str, base64_body: bool):
        self._response: dict = ...
        self._raw_body: str = ...
        self._is_base64_body: bool = ...
        self._body: Union[str, dict] = ...
        self._headers: dict = ...

    @property
    def headers(self) -> CaseInsensitiveDict: ...

    @property
    def body(self) -> Union[str, dict, bool]: ...
