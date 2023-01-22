# -*- coding:utf-8 -*-
from json import load, dump
from pathlib import Path
from platform import system
from subprocess import Popen
from time import perf_counter, sleep

from requests import get as requests_get

from DrissionPage.configs.driver_options import DriverOptions
from .tools import port_is_using, get_exe_from_port


def connect_browser(option):
    """连接或启动浏览器                           \n
    :param option: DriverOptions对象
    :return: chrome 路径和进程对象组成的元组
    """
    system_type = system().lower()
    debugger_address = option.debugger_address
    chrome_path = option.browser_path

    debugger_address = debugger_address[7:] if debugger_address.startswith('http://') else debugger_address
    ip, port = debugger_address.split(':')
    if ip not in ('127.0.0.1', 'localhost'):
        return None, None

    if port_is_using(ip, port):
        chrome_path = get_exe_from_port(port) if chrome_path == 'chrome' and system_type == 'windows' else chrome_path
        return chrome_path, None

    args = get_launch_args(option)
    set_prefs(option)

    # ----------创建浏览器进程----------
    try:
        debugger = _run_browser(port, chrome_path, args)
        if chrome_path == 'chrome' and system_type == 'windows':
            chrome_path = get_exe_from_port(port)

    # 传入的路径找不到，主动在ini文件、注册表、系统变量中找
    except FileNotFoundError:
        from DrissionPage.easy_set import get_chrome_path
        chrome_path = get_chrome_path(show_msg=False)

        if not chrome_path:
            raise FileNotFoundError('无法找到chrome路径，请手动配置。')

        debugger = _run_browser(port, chrome_path, args)

    return chrome_path, debugger


def get_launch_args(opt):
    """从DriverOptions获取命令行启动参数
    :param opt: DriverOptions或ChromiumOptions
    :return: 启动参数列表
    """
    # ----------处理arguments-----------
    result = set(i for i in opt.arguments if not i.startswith(('--load-extension=', '--remote-debugging-port=')))
    result = list(result)

    # ----------处理插件extensions-------------
    ext = opt._extension_files if isinstance(opt, DriverOptions) else opt.extensions
    if ext:
        ext = ','.join(set(ext))
        ext = f'--load-extension={ext}'
        result.append(ext)

    return result


def set_prefs(opt):
    """处理启动配置中的prefs项，目前只能对已存在文件夹配置
    :param opt: DriverOptions或ChromiumOptions
    :return: None
    """
    if isinstance(opt, DriverOptions):
        prefs = opt.experimental_options.get('prefs', None)
        del_list = []
    else:
        prefs = opt.preferences
        del_list = opt._prefs_to_del

    if not opt.user_data_path:
        return

    args = opt.arguments
    user = 'Default'
    for arg in args:
        if arg.startswith('--profile-directory'):
            user = arg.split('=')[-1].strip()
            break

    prefs_file = Path(opt.user_data_path) / user / 'Preferences'

    if not prefs_file.exists():
        prefs_file.parent.mkdir(parents=True, exist_ok=True)
        with open(prefs_file, 'w') as f:
            f.write('{}')

    with open(prefs_file, "r", encoding='utf-8') as f:
        prefs_dict = load(f)

        for pref in prefs:
            value = prefs[pref]
            pref = pref.split('.')
            _make_leave_in_dict(prefs_dict, pref, 0, len(pref))
            _set_value_to_dict(prefs_dict, pref, value)

        for pref in del_list:
            _remove_arg_from_dict(prefs_dict, pref)

    with open(prefs_file, 'w', encoding='utf-8') as f:
        dump(prefs_dict, f)


def _run_browser(port, path: str, args) -> Popen:
    """创建chrome进程          \n
    :param port: 端口号
    :param path: 浏览器地址
    :param args: 启动参数
    :return: 进程对象
    """
    arguments = [path, f'--remote-debugging-port={port}']
    arguments.extend(args)
    debugger = Popen(arguments, shell=False)

    end_time = perf_counter() + 10
    while perf_counter() < end_time:
        try:
            tabs = requests_get(f'http://127.0.0.1:{port}/json').json()
            for tab in tabs:
                if tab['type'] == 'page':
                    return debugger
        except Exception:
            sleep(.2)

    raise ConnectionError('无法连接浏览器。')


def _make_leave_in_dict(target_dict: dict, src: list, num: int, end: int) -> None:
    """把prefs中a.b.c形式的属性转为a['b']['c']形式
    :param target_dict: 要处理的字典
    :param src: 属性层级列表[a, b, c]
    :param num: 当前处理第几个
    :param end: src长度
    :return: None
    """
    if num == end:
        return
    if src[num] not in target_dict:
        target_dict[src[num]] = {}
    num += 1
    _make_leave_in_dict(target_dict[src[num - 1]], src, num, end)


def _set_value_to_dict(target_dict: dict, src: list, value) -> None:
    """把a.b.c形式的属性的值赋值到a['b']['c']形式的字典中
    :param target_dict: 要处理的字典
    :param src: 属性层级列表[a, b, c]
    :param value: 属性值
    :return: None
    """
    src = "']['".join(src)
    src = f"target_dict['{src}']=value"
    exec(src)


def _remove_arg_from_dict(target_dict: dict, arg: str) -> None:
    """把a.b.c形式的属性从字典中删除
    :param target_dict: 要处理的字典
    :param arg: 层级属性，形式'a.b.c'
    :return: None
    """
    args = arg.split('.')
    args = [f"['{i}']" for i in args]
    src = ''.join(args)
    src = f"target_dict{src}"
    try:
        exec(src)
        src = ''.join(args[:-1])
        src = f"target_dict{src}.pop({args[-1][1:-1]})"
        exec(src)
    except:
        pass