本节介绍获取页面对象各种信息的属性和方法。

# ✔️ 两种模式共有属性

## 📍 `url`

此属性返回当前访问的 url。

## 📍 `mode`

此属性返回当前页面对象的模式，`'s'`或`'d'`。

## 📍 `drission`

此属性返回当前页面对象使用的`Drission`对象。

## 📍 `driver`

此属性返回当前页面对象使用的`WebDriver`对象。访问时会自动切换到 d 模式。

## 📍 `session`

此属性返回当前页面对象使用的`Session`对象。访问时不会切换模式。

## 📍 `cookies`

此属性以`dict`方式返回当前页面所使用的 cookies。  
d 模式只返回当前标签页的 cookies，s 模式则只返回当前访问的 url 的`cookies`。

## 📍 `get_cookies()`

此方法获取 cookies 并以 cookie 组成的`list`形式返回。

**参数：**

- `as_dict`：是否以字典方式返回，为`False`返回`cookie`组成的`list`
- `all_domains`：是否返回所有域的`cookies`，只有 s 模式下生效

**返回：**`cookies`信息

```python
from DrissionPage import MixPage

p = MixPage('s')
p.get('http://www.baidu.com')
p.get('http://gitee.com')

for i in p.get_cookies(as_dict=False, all_domains=True):
    print(i)
```

**输出：**

```
{'domain': '.baidu.com', 'domain_specified': True, ......}
......
{'domain': 'gitee.com', 'domain_specified': False, ......}
......
```

## 📍 `html`

此属性返回当前页面 html 文本。

## 📍 `title`

此属性返回当前页面`title`文本。

## 📍 `timeout`

s 模式下，此属性代表网络请求超时时间。  
d 模式下，此属性为元素查找、点击、处理提示框等操作的超时时间。  
默认为 10，可对其赋值。

```python
# 创建 MixPage 对象时指定
page = MixPage(timeout=5)

# 修改 timeout
page.timeout = 20
```

## 📍 `retry_times`

此参数为网络连接失败时的重试次数。默认为 3，可对其赋值。

```python
# 修改重试次数
page.retry_times = 5
```

## 📍 `retry_interval`

此参数为网络连接失败时的重试等待间隔秒数。默认为 2，可对其赋值。

```python
# 修改重试等待间隔时间
page.retry_interval = 1.5
```

## 📍 `url_available`

此属性以布尔值返回当前链接是否可用。  
s 模式下根据`Response`对象的`status_code`判断。  
d 模式根据`check_page()`方法返回值判断。

# ✔️ s 模式独有属性

## 📍 `response`

此属性为 s 模式请求网站后生成的`Response`对象，本库没实现的功能可直接获取此属性调用 requests 库的原生功能。

```python
# 打印连接状态
r = page.response
print(r.status_code)
```

## 📍 `json`

此属性把请求内容解析成 json。  
比如请求接口时，返回内容是 json 格式，那就可以用这个属性获取。  
事实上，用 html 属性获取也是可以的，不过 html 属性没有对文本进行解析。

# ✔️ d 模式独有属性

## 📍 `timeouts`

此属性以字典方式返回三种超时时间，selenium 4 以上版本可用。  
`'implicit'`用于元素查找、点击重试、输入文本重试、处理弹出框重试等；  
`'pageLoad'`用于等待页面加载；  
`'script'`用于等待脚本执行。

```python
print(page.timeouts)
```

**输出：**

```
{'implicit': 10, 'pageLoad': 30.0, 'script': 30.0}
```

## 📍 `tabs_count`

此属性返回当前浏览器标签页数量。

## 📍 `tab_handles`

此属性以列表形式返回当前浏览器所有标签页的 handle。

!> **注意：**  
以下情况会导致获取到的顺序与视觉效果不一致：1、自动化过程中手动点击标签页；2、浏览器被接管时已打开一个以上标签页。

## 📍 `current_tab_index`

此属性返回当前标签页的序号。

!> **注意：** <br>以下情况会导致获取到的排序号与视觉效果不一致：1、自动化过程中手动点击标签页；2、浏览器被接管时已打开一个以上标签页。

## 📍 `current_tab_handle`

此属性返回当前标签页的 handle。

## 📍 `active_ele`

此属性返回当前页面上焦点所在元素。类型为`DriverElement`。

## 📍 `wait_obj`

此属性返回当前页面对象用于等待的对象。

## 📍 `chrome_downloading()`

此方法返回浏览器下载中的文件列表。

**参数：**

- `path:` 下载文件夹路径，默认从配置信息读取

**返回：** 下载中的文件列表
