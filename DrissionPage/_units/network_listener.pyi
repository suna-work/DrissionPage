# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from queue import Queue
from typing import Union, Dict, List, Iterable, Tuple, Optional

from requests.structures import CaseInsensitiveDict

from .._base.chromium_driver import ChromiumDriver
from .._pages.chromium_base import ChromiumBase


class NetworkListener(object):
    def __init__(self, page: ChromiumBase):
        self._page: ChromiumBase = ...
        self._targets: Union[str, dict] = ...
        self._method: set = ...
        self._caught: Queue = ...
        self._is_regex: bool = ...
        self._driver: ChromiumDriver = ...
        self._request_ids: dict = ...
        self._extra_info_ids: dict = ...
        self.listening: bool = ...

    @property
    def targets(self) -> Optional[set]: ...

    def set_targets(self, targets: Union[str, list, tuple, set, None] = None, is_regex: bool = False,
                    method: Union[str, list, tuple, set] = None) -> None: ...

    def stop(self) -> None: ...

    def pause(self, clear: bool = True) -> None: ...

    def go_on(self) -> None: ...

    def wait(self, count: int = 1, timeout: float = None,
             fix_count: bool = True) -> Union[List[DataPacket], DataPacket, None]: ...

    @property
    def results(self) -> Union[DataPacket, Dict[str, List[DataPacket]], False]: ...

    def clear(self) -> None: ...

    def start(self, targets: Union[str, List[str], Tuple, bool, None] = None, is_regex: bool = False,
              method: Union[str, list, tuple, set] = None) \
            -> Union[DataPacket, Dict[str, List[DataPacket]], False]: ...

    def _requestWillBeSent(self, **kwargs) -> None: ...

    def _requestWillBeSentExtraInfo(self, **kwargs) -> None: ...

    def _response_received(self, **kwargs) -> None: ...

    def _responseReceivedExtraInfo(self, **kwargs) -> None: ...

    def _loading_finished(self, **kwargs) -> None: ...

    def _loading_failed(self, **kwargs) -> None: ...

    def steps(self, count: int = None, timeout: float = None,
              gap=1) -> Iterable[Union[DataPacket, List[DataPacket]]]: ...

    def _set_callback(self) -> None: ...


class DataPacket(object):
    """返回的数据包管理类"""

    def __init__(self, tab_id: str, target: Optional[str]):
        self.tab_id: str = ...
        self.target: str = ...
        self._raw_request: Optional[dict] = ...
        self._raw_response: Optional[dict] = ...
        self._raw_post_data: str = ...
        self._raw_body: str = ...
        self._base64_body: bool = ...
        self._request: Request = ...
        self._response: Response = ...
        self.errorText: str = ...
        self._resource_type: str = ...
        self._requestExtraInfo: Optional[dict] = ...
        self._responseExtraInfo: Optional[dict] = ...

    @property
    def _request_extra_info(self) -> Optional[dict]: ...

    @property
    def _response_extra_info(self) -> Optional[dict]: ...

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

    def wait_extra_info(self, timeout: float = None) -> bool: ...


class Request(object):
    url: str = ...
    _headers: Union[CaseInsensitiveDict, None] = ...
    method: str = ...

    urlFragment = ...
    hasPostData = ...
    postDataEntries = ...
    mixedContentType = ...
    initialPriority = ...
    referrerPolicy = ...
    isLinkPreload = ...
    trustTokenParams = ...
    isSameSite = ...

    def __init__(self, data_packet: DataPacket, raw_request: dict, post_data: str):
        self._data_packet: DataPacket = ...
        self._request: dict = ...
        self._raw_post_data: str = ...
        self._postData: str = ...

    @property
    def headers(self) -> dict: ...

    @property
    def postData(self) -> Union[str, dict]: ...

    @property
    def extra_info(self) -> Optional[RequestExtraInfo]: ...


class Response(object):
    url = ...
    status = ...
    statusText = ...
    headersText = ...
    mimeType = ...
    requestHeaders = ...
    requestHeadersText = ...
    connectionReused = ...
    connectionId = ...
    remoteIPAddress = ...
    remotePort = ...
    fromDiskCache = ...
    fromServiceWorker = ...
    fromPrefetchCache = ...
    encodedDataLength = ...
    timing = ...
    serviceWorkerResponseSource = ...
    responseTime = ...
    cacheStorageCacheName = ...
    protocol = ...
    alternateProtocolUsage = ...
    securityState = ...
    securityDetails = ...

    def __init__(self, data_packet: DataPacket, raw_response: dict, raw_body: str, base64_body: bool):
        self._data_packet: DataPacket = ...
        self._response: dict = ...
        self._raw_body: str = ...
        self._is_base64_body: bool = ...
        self._body: Union[str, dict] = ...
        self._headers: dict = ...

    @property
    def extra_info(self) -> Optional[ResponseExtraInfo]: ...

    @property
    def headers(self) -> CaseInsensitiveDict: ...

    @property
    def raw_body(self) -> str: ...

    @property
    def body(self) -> Union[str, dict, bool]: ...


class ExtraInfo(object):
    def __init__(self, extra_info: dict):
        self._extra_info: dict = ...

    @property
    def all_info(self) -> dict: ...


class RequestExtraInfo(ExtraInfo):
    requestId: str = ...
    associatedCookies: List[dict] = ...
    headers: dict = ...
    connectTiming: dict = ...
    clientSecurityState: dict = ...
    siteHasCookieInOtherPartition: bool = ...


class ResponseExtraInfo(ExtraInfo):
    requestId: str = ...
    blockedCookies: List[dict] = ...
    headers: dict = ...
    resourceIPAddressSpace: str = ...
    statusCode: int = ...
    headersText: str = ...
    cookiePartitionKey: str = ...
    cookiePartitionKeyOpaque: bool = ...
