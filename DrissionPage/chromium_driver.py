# -*- coding: utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from json import dumps, loads
from queue import Queue, Empty
from threading import Thread, Event

from websocket import WebSocketTimeoutException, WebSocketException, WebSocketConnectionClosedException, \
    create_connection


class ChromiumDriver(object):
    _INITIAL_ = 'initial'
    _STARTED_ = 'started'
    _STOPPED_ = 'stopped'

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
        self.has_alert = False

        self._websocket_url = f'ws://{address}/devtools/{tab_type}/{tab_id}'
        self._cur_id = 0
        self._ws = None

        self._recv_th = Thread(target=self._recv_loop)
        self._handle_event_th = Thread(target=self._handle_event_loop)
        self._recv_th.daemon = True
        self._handle_event_th.daemon = True

        self._stopped = Event()
        self._started = False
        self.status = self._INITIAL_

        self.event_handlers = {}
        self.method_results = {}
        self.event_queue = Queue()

    def _send(self, message, timeout=None):
        """发送信息到浏览器，并返回浏览器返回的信息
        :param message: 发送给浏览器的数据
        :param timeout: 超时时间
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

        if not isinstance(timeout, (int, float)) or timeout > 1:
            q_timeout = 1
        else:
            q_timeout = timeout / 2.0

        try:
            self.method_results[message['id']] = Queue()
            self._ws.send(message_json)

            while not self._stopped.is_set():
                try:
                    if isinstance(timeout, (int, float)):
                        if timeout < q_timeout:
                            q_timeout = timeout
                        timeout -= q_timeout

                    return self.method_results[message['id']].get(timeout=q_timeout)

                except Empty:
                    if self.has_alert:
                        return {'error': {'message': 'alert exists'}, 'type': 'alert_exists'}

                    if isinstance(timeout, (int, float)) and timeout <= 0:
                        raise TimeoutError(f"调用{message['method']}超时。")

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
                message_json = self._ws.recv()
                mes = loads(message_json)
            except WebSocketTimeoutException:
                continue
            except (WebSocketException, OSError, WebSocketConnectionClosedException):
                self.stop()
                return

            if self._debug:
                if self._debug is True or 'id' in mes or (isinstance(self._debug, str)
                                                          and mes.get('method', '').startswith(self._debug)):
                    print(f'<收 {message_json}')
                elif isinstance(self._debug, (list, tuple, set)):
                    for m in self._debug:
                        if mes.get('method', '').startswith(m):
                            print(f'<收 {message_json}')
                            break

            if "method" in mes:
                self.event_queue.put(mes)

            elif "id" in mes:
                if mes["id"] in self.method_results:
                    self.method_results[mes['id']].put(mes)

            elif self._debug:
                print(f'未知信息：{mes}')

    def _handle_event_loop(self):
        """当接收到浏览器信息，执行已绑定的方法"""
        while not self._stopped.is_set():
            try:
                event = self.event_queue.get(timeout=1)
            except Empty:
                continue

            if event['method'] in self.event_handlers:
                try:
                    self.event_handlers[event['method']](**event['params'])
                except Exception as e:
                    raise
                    # raise RuntimeError(f"\n回调函数错误：\n{e}")

            self.event_queue.task_done()

    def call_method(self, _method, **kwargs):
        """执行cdp方法
        :param _method: cdp方法名
        :param args: cdp参数
        :param kwargs: cdp参数
        :return: 执行结果
        """
        if not self._started:
            self.start()
            # raise RuntimeError("不能在启动前调用方法。")

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
        if self._started:
            return False
        if not self._websocket_url:
            raise RuntimeError("已存在另一个连接。")

        self._started = True
        self.status = self._STARTED_
        self._stopped.clear()
        self._ws = create_connection(self._websocket_url, enable_multithread=True)
        self._recv_th.start()
        self._handle_event_th.start()
        return True

    def stop(self):
        """中断连接"""
        if self._stopped.is_set():
            return False
        if not self._started:
            return True

        self.status = self._STOPPED_
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
        :return: 回调方法
        """
        if not callback:
            return self.event_handlers.pop(event, None)
        if not callable(callback):
            raise RuntimeError("方法不能调用。")

        self.event_handlers[event] = callback
        return True

    def get_listener(self, event):
        """获取cdp event对应的回调方法
        :param event: cdp event
        :return: 回调方法
        """
        return self.event_handlers.get(event, None)

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
        if tab_id in BrowserDriver.BROWSERS:
            return
        super().__init__(tab_id, tab_type, address)
        BrowserDriver.BROWSERS[tab_id] = self

    def __repr__(self):
        return f"<BrowserDriver {self.id}>"
