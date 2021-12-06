# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   common.py
"""
from html import unescape
from pathlib import Path
from re import split, search, sub, findall
from shutil import rmtree
from typing import Union
from zipfile import ZipFile


def get_ele_txt(e) -> str:
    """获取元素内所有文本
    :param e: 元素对象
    :return: 元素内所有文本
    """
    # 前面无须换行的元素
    nowrap_list = ('br', 'sub', 'em', 'strong', 'a', 'font', 'b', 'span', 's', 'i', 'del', 'ins', 'img', 'td', 'th',
                   'abbr', 'bdi', 'bdo', 'cite', 'code', 'data', 'dfn', 'kbd', 'mark', 'q', 'rp', 'rt', 'ruby',
                   'samp', 'small', 'sub', 'time', 'u', 'var', 'wbr', 'button', 'slot', 'content')
    # 后面添加换行的元素
    wrap_after_list = ('p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'li', 'blockquote', 'header',
                       'footer', 'address' 'article', 'aside', 'main', 'nav', 'section', 'figcaption', 'summary')
    # 不获取文本的元素
    noText_list = ('script', 'style', 'video', 'audio', 'iframe', 'embed', 'noscript', 'canvas', 'template')
    # 用/t分隔的元素
    tab_list = ('td', 'th')

    if e.tag in noText_list:
        return e.raw_text

    def get_node_txt(ele, pre: bool = False):
        tag = ele.tag
        if tag == 'br':
            return [True]
        if not pre and tag == 'pre':
            pre = True

        str_list = []
        if tag in noText_list and not pre:  # 标签内的文本不返回
            return str_list

        nodes = ele.eles('xpath:./text() | *')
        prev_ele = ''
        for el in nodes:
            if isinstance(el, str):  # 字符节点
                if pre:
                    str_list.append(el)

                else:
                    if sub('[ \n\t]', '', el) != '':  # 字符除了回车和空格还有其它内容
                        txt = el
                        if not pre:
                            txt = txt.replace('\n', ' ').strip(' ')
                            txt = sub(r' {2,}', ' ', txt)
                        str_list.append(txt)

            else:  # 元素节点
                if el.tag not in nowrap_list and str_list and str_list[-1] != '\n':  # 元素间换行的情况
                    str_list.append('\n')
                if el.tag in tab_list and prev_ele in tab_list:  # 表格的行
                    str_list.append('\t')

                str_list.extend(get_node_txt(el, pre))
                prev_ele = el.tag

        if tag in wrap_after_list and str_list and str_list[-1] not in ('\n', True):  # 有些元素后面要添加回车
            str_list.append('\n')

        return str_list

    re_str = get_node_txt(e)
    if re_str and re_str[-1] == '\n':
        re_str.pop()
    re_str = ''.join([i if i is not True else '\n' for i in re_str])
    return format_html(re_str)


def str_to_loc(loc: str) -> tuple:
    """处理元素查找语句                                                                    \n
    查找方式：属性、tag name及属性、文本、xpath、css selector、id、class                      \n
    @表示属性，.表示class，#表示id，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串    \n
    """
    loc_by = 'xpath'

    # .和#替换为class和id查找
    if loc.startswith('.'):
        if loc.startswith(('.=', '.:',)):
            loc = loc.replace('.', '@class', 1)
        else:
            loc = loc.replace('.', '@class=', 1)

    elif loc.startswith('#'):
        if loc.startswith(('#=', '#:',)):
            loc = loc.replace('#', '@id', 1)
        else:
            loc = loc.replace('#', '@id=', 1)

    elif loc.startswith(('t:', 't=')):
        loc = f'tag:{loc[2:]}'

    elif loc.startswith(('tx:', 'tx=')):
        loc = f'text{loc[2:]}'

    # 根据属性查找
    if loc.startswith('@'):
        loc_str = _make_xpath_str('*', loc)
        # r = split(r'([:=])', loc[1:], maxsplit=1)
        # if len(r) == 3:
        #     mode = 'exact' if r[1] == '=' else 'fuzzy'
        #     loc_str = _make_xpath_str('*', f'@{r[0]}', r[2], mode)
        # else:
        #     loc_str = f'//*[@{loc[1:]}]'

    # 根据tag name查找
    elif loc.startswith(('tag:', 'tag=')):
        at_ind = loc.find('@')
        if at_ind == -1:
            loc_str = f'//*[name()="{loc[4:]}"]'
        else:
            loc_str = _make_xpath_str(loc[4:at_ind], loc[at_ind:])
        # if '@' not in loc[4:]:
        #     loc_str = f'//*[name()="{loc[4:]}"]'
        # else:
        #     at_lst = loc[4:].split('@', maxsplit=1)
        #     r = split(r'([:=])', at_lst[1], maxsplit=1)
        #     if len(r) == 3:
        #         mode = 'exact' if r[1] == '=' else 'fuzzy'
        #         arg_str = 'text()' if r[0] in ('text()', 'tx()') else f'@{r[0]}'
        #         loc_str = _make_xpath_str(at_lst[0], arg_str, r[2], mode)
        #     else:
        #         loc_str = f'//*[name()="{at_lst[0]}" and @{r[0]}]'

    # 根据文本查找
    elif loc.startswith(('text:', 'text=')):
        if len(loc) > 5:
            loc_str = _make_xpath_str('*', f'@text(){loc[4:]}')
        else:
            loc_str = '//*[not(text())]'

    # 用xpath查找
    elif loc.startswith(('xpath:', 'xpath=')):
        loc_str = loc[6:]
    elif loc.startswith(('x:', 'x=')):
        loc_str = loc[2:]

    # 用css selector查找
    elif loc.startswith(('css:', 'css=')):
        loc_by = 'css selector'
        loc_str = loc[4:]

    elif loc.startswith(('c:', 'c=')):
        loc_by = 'css selector'
        loc_str = loc[2:]

    # 根据文本模糊查找
    else:
        if loc:
            loc_str = _make_xpath_str('*', f'@text():{loc}')
        else:
            loc_str = '//*[not(text())]'

    return loc_by, loc_str


def _make_xpath_str(tag: str, text: str) -> str:
    tag_name = '' if tag == '*' else f'name()="{tag}" and '
    r = findall(r'@([^@]*)', text)
    res_list = []
    for i in r:
        r = split(r'([:=])', i, maxsplit=1)
        if len(r) == 3:
            arg_str = 'text()' if r[0] in ('text()', 'tx()') else f'@{r[0]}'
            if r[1] == '=':
                loc_str = f'{arg_str}={_make_search_str(r[2])}'
            else:
                loc_str = f'contains({arg_str}, {_make_search_str(r[2])})'
        else:
            loc_str = f'@{i}'
        res_list.append(loc_str)

    s = ' and '.join(res_list)
    return f"//*[{tag_name}{s}]"


# def _make_xpath_str(tag: str, arg: str, val: str, mode: str = 'fuzzy') -> str:
#     """生成xpath语句                                          \n
#     :param tag: 标签名
#     :param arg: 属性名
#     :param val: 属性值
#     :param mode: 'exact' 或 'fuzzy'，对应精确或模糊查找
#     :return: xpath字符串
#     """
#     tag_name = '' if tag == '*' else f'name()="{tag}" and '
#
#     if mode == 'exact':
#         return f'//*[{tag_name}{arg}={_make_search_str(val)}]'
#
#     elif mode == 'fuzzy':
#         if arg == 'text()':
#             tag_name = '' if tag == '*' else f'{tag}/'
#             return f'//{tag_name}text()[contains(., {_make_search_str(val)})]/..'
#         else:
#             return f"//*[{tag_name}contains({arg},{_make_search_str(val)})]"
#
#     else:
#         raise ValueError("mode参数只能是'exact'或'fuzzy'。")


def translate_loc(loc: tuple) -> tuple:
    """把By类型的loc元组转换为css selector或xpath类型的  \n
    :param loc: By类型的loc元组
    :return: css selector或xpath类型的loc元组
    """
    if len(loc) != 2:
        raise ValueError('定位符长度必须为2。')

    loc_by = 'xpath'

    if loc[0] == 'xpath':
        loc_str = loc[1]

    elif loc[0] == 'css selector':
        loc_by = 'css selector'
        loc_str = loc[1]

    elif loc[0] == 'id':
        loc_str = f'//*[@id="{loc[1]}"]'

    elif loc[0] == 'class name':
        loc_str = f'//*[@class="{loc[1]}"]'

    elif loc[0] == 'link text':
        loc_str = f'//a[text()="{loc[1]}"]'

    elif loc[0] == 'name':
        loc_str = f'//*[@name="{loc[1]}"]'

    elif loc[0] == 'tag name':
        loc_str = f'//{loc[1]}'

    elif loc[0] == 'partial link text':
        loc_str = f'//a[contains(text(),"{loc[1]}")]'

    else:
        raise ValueError('无法识别的定位符。')

    return loc_by, loc_str


def _make_search_str(search_str: str) -> str:
    """将"转义，不知何故不能直接用 \ 来转义 \n
    :param search_str: 查询字符串
    :return: 把"转义后的字符串
    """
    parts = search_str.split('"')
    parts_num = len(parts)
    search_str = 'concat('

    for key, i in enumerate(parts):
        search_str += f'"{i}"'
        search_str += ',' + '\'"\',' if key < parts_num - 1 else ''

    search_str += ',"")'
    return search_str


def format_html(text: str) -> str:
    """处理html编码字符             \n
    :param text: html文本
    :return: 格式化后的html文本
    """
    return unescape(text).replace('\xa0', ' ') if text else text


def clean_folder(folder_path: str, ignore: list = None) -> None:
    """清空一个文件夹，除了ignore里的文件和文件夹  \n
    :param folder_path: 要清空的文件夹路径
    :param ignore: 忽略列表
    :return: None
    """
    ignore = [] if not ignore else ignore
    p = Path(folder_path)

    for f in p.iterdir():
        if f.name not in ignore:
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                rmtree(f, True)


def unzip(zip_path: str, to_path: str) -> Union[list, None]:
    """解压下载的chromedriver.zip文件"""
    if not zip_path:
        return

    with ZipFile(zip_path, 'r') as f:
        return [f.extract(f.namelist()[0], path=to_path)]


def get_exe_path_from_port(port: Union[str, int]) -> Union[str, None]:
    """获取端口号第一条进程的可执行文件路径      \n
    :param port: 端口号
    :return: 可执行文件的绝对路径
    """
    from os import popen
    from time import perf_counter
    process = popen(f'netstat -ano |findstr {port}').read().split('\n')[0]
    t = perf_counter()

    while not process and perf_counter() - t < 10:
        process = popen(f'netstat -ano |findstr {port}').read().split('\n')[0]

    processid = process.split(' ')[-1]

    if not processid:
        return
    else:
        file_lst = popen(f'wmic process where processid={processid} get executablepath').read().split('\n')
        return file_lst[2].strip() if len(file_lst) > 2 else None


def get_usable_path(path: Union[str, Path]) -> Path:
    """检查文件或文件夹是否有重名，并返回可以使用的路径           \n
    :param path: 文件或文件夹路径
    :return: 可用的路径，Path对象
    """
    path = Path(path)
    parent = path.parent
    path = parent / make_valid_name(path.name)
    name = path.stem if path.is_file() else path.name
    ext = path.suffix if path.is_file() else ''

    first_time = True

    while path.exists():
        r = search(r'(.*)_(\d+)$', name)

        if not r or (r and first_time):
            src_name, num = name, '1'
        else:
            src_name, num = r.group(1), int(r.group(2)) + 1

        name = f'{src_name}_{num}'
        path = parent / f'{name}{ext}'
        first_time = None

    return path


def make_valid_name(full_name: str) -> str:
    """获取有效的文件名                  \n
    :param full_name: 文件名
    :return: 可用的文件名
    """
    # ----------------去除前后空格----------------
    full_name = full_name.strip()

    # ----------------使总长度不大于255个字符（一个汉字是2个字符）----------------
    r = search(r'(.*)(\.[^.]+$)', full_name)  # 拆分文件名和后缀名
    if r:
        name, ext = r.group(1), r.group(2)
        ext_long = len(ext)
    else:
        name, ext = full_name, ''
        ext_long = 0

    while get_long(name) > 255 - ext_long:
        name = name[:-1]

    full_name = f'{name}{ext}'

    # ----------------去除不允许存在的字符----------------
    return sub(r'[<>/\\|:*?\n]', '', full_name)


def get_long(txt) -> int:
    """返回字符串中字符个数（一个汉字是2个字符）          \n
    :param txt: 字符串
    :return: 字符个数
    """
    txt_len = len(txt)
    return int((len(txt.encode('utf-8')) - txt_len) / 2 + txt_len)
