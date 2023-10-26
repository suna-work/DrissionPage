# -*- coding: utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from json import dumps, loads
from queue import Queue, Empty
from threading import Thread, Event
from time import perf_counter, sleep

from requests import get
from websocket import WebSocketTimeoutException, WebSocketException, WebSocketConnectionClosedException, \
    create_connection


class ChromiumDriver(object):
    def __init__(self, tab_id, tab_type, address):
        """
        :param tab_id: 标签页id
        :param tab_type: 标签页类型
        :param address: 浏览器连接地址
        """
        self.id = tab_id
        self.address = address
        self.type = tab_type
        self._debug = False
        self.alert_flag = False  # 标记alert出现，跳过一条请求后复原

        self._websocket_url = f'ws://{address}/devtools/{tab_type}/{tab_id}'
        self._cur_id = 0
        self._ws = None

        self._recv_th = Thread(target=self._recv_loop)
        self._handle_event_th = Thread(target=self._handle_event_loop)
        self._recv_th.daemon = True
        self._handle_event_th.daemon = True

        self._stopped = Event()

        self.event_handlers = {}
        self.method_results = {}
        self.event_queue = Queue()

        self.start()

    def _send(self, message, timeout=None):
        """发送信息到浏览器，并返回浏览器返回的信息
        :param message: 发送给浏览器的数据
        :param timeout: 超时时间，为None表示无限
        :return: 浏览器返回的数据
        """
        if 'id' not in message:
            self._cur_id += 1
            message['id'] = self._cur_id

        message_json = dumps(message)

        if self._debug:
            if self._debug is True or (
                    isinstance(self._debug, str) and message.get('method', '').startswith(self._debug)):
                print(f'发> {message_json}')
            elif isinstance(self._debug, (list, tuple, set)):
                for m in self._debug:
                    if message.get('method', '').startswith(m):
                        print(f'发> {message_json}')
                        break

        if timeout is not None:
            timeout = perf_counter() + timeout

        try:
            self.method_results[message['id']] = Queue()
            self._ws.send(message_json)

            while not self._stopped.is_set():
                try:
                    return self.method_results[message['id']].get_nowait()

                except Empty:
                    if self.alert_flag:
                        self.alert_flag = False
                        return {'result': []}

                    if timeout is not None and perf_counter() > timeout:
                        return {'error': {'message': 'timeout'}}

                    sleep(.02)
                    continue

        except Exception:
            return None

        finally:
            self.method_results.pop(message['id'], None)

    def _recv_loop(self):
        """接收浏览器信息的守护线程方法"""
        while not self._stopped.is_set():
            try:
                self._ws.settimeout(1)
                msg_json = self._ws.recv()
                msg = loads(msg_json)
            except WebSocketTimeoutException:
                continue
            except (WebSocketException, OSError, WebSocketConnectionClosedException):
                self.stop()
                return

            if self._debug:
                if self._debug is True or 'id' in msg or (isinstance(self._debug, str)
                                                          and msg.get('method', '').startswith(self._debug)):
                    print(f'<收 {msg_json}')
                elif isinstance(self._debug, (list, tuple, set)):
                    for m in self._debug:
                        if msg.get('method', '').startswith(m):
                            print(f'<收 {msg_json}')
                            break

            if 'method' in msg:
                if msg['method'].startswith('Page.javascriptDialog'):
                    self.alert_flag = msg['method'].endswith('Opening')

                self.event_queue.put(msg)

            elif msg.get('id') in self.method_results:
                self.method_results[msg['id']].put(msg)

            elif self._debug:
                print(f'未知信息：{msg}')

    def _handle_event_loop(self):
        """当接收到浏览器信息，执行已绑定的方法"""
        while not self._stopped.is_set():
            try:
                event = self.event_queue.get(timeout=1)
            except Empty:
                continue

            function = self.event_handlers.get(event['method'])
            if function:
                function(**event['params'])

            self.event_queue.task_done()

    def call_method(self, _method, **kwargs):
        """执行cdp方法
        :param _method: cdp方法名
        :param args: cdp参数
        :param kwargs: cdp参数
        :return: 执行结果
        """
        if self._stopped.is_set():
            return {'error': 'tab closed', 'type': 'tab_closed'}

        timeout = kwargs.pop("_timeout", None)
        result = self._send({"method": _method, "params": kwargs}, timeout=timeout)
        if result is None:
            return {'error': 'tab closed', 'type': 'tab_closed'}
        if 'result' not in result and 'error' in result:
            return {'error': result['error']['message'],
                    'type': result.get('type', 'call_method_error'),
                    'method': _method,
                    'args': kwargs}

        return result['result']

    def start(self):
        """启动连接"""
        self._stopped.clear()
        self._ws = create_connection(self._websocket_url, enable_multithread=True)
        self._recv_th.start()
        self._handle_event_th.start()
        return True

    def stop(self):
        """中断连接"""
        if self._stopped.is_set():
            return False

        self._stopped.set()
        if self._ws:
            self._ws.close()
            self._ws = None
        self.event_handlers.clear()
        self.method_results.clear()
        self.event_queue.queue.clear()
        return True

    def set_listener(self, event, callback):
        """绑定cdp event和回调方法
        :param event: cdp event
        :param callback: 绑定到cdp event的回调方法
        :return: None
        """
        if callback:
            self.event_handlers[event] = callback
        else:
            self.event_handlers.pop(event, None)

    def __str__(self):
        return f"<ChromiumDriver {self.id}>"

    __repr__ = __str__


class BrowserDriver(ChromiumDriver):
    BROWSERS = {}

    def __new__(cls, tab_id, tab_type, address):
        if tab_id in cls.BROWSERS:
            return cls.BROWSERS[tab_id]
        return object.__new__(cls)

    def __init__(self, tab_id, tab_type, address):
        if hasattr(self, '_created'):
            return
        self._created = True
        BrowserDriver.BROWSERS[tab_id] = self
        super().__init__(tab_id, tab_type, address)

    def __repr__(self):
        return f"<BrowserDriver {self.id}>"

    def get(self, url):
        return get(url, headers={'Connection': 'close'})