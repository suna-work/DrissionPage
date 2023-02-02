操作页面前通常要先跳转到目标 url（接管现有浏览器除外），本库访问网页主要支持`get()`和`post()`两种方式，还支持自动重试。

# ✔️ `get()`

该方法在 d 模式和 s 模式下都可用，用于跳转到一个网址。  
当连接失败时，程序默认重试 3 次，每次间隔 2 秒，也可以通过参数设置重试次数和间隔。   
在 s 模式下，可传入连接参数，语法与 requests 的`get()`方法一致。  
方法返回是否连接成功的布尔值，s 模式下根据`Response`对象的`status_code`参数决定，d 模式下根据浏览器的状态，还可以通过重写`check_page()`方法实现自定义检查方式。

**参数：**

- `url`：目标 url
- `show_errmsg`：是否显示和抛出异常，默认不抛出，连接错误会返回`None`
- `retry`：重试次数，与页面对象的设置一致，默认 3 次
- `interval`：重试间隔（秒），与页面对象的设置一致，默认 2 秒
- `**kwargs`：连接参数，s 模式专用，与 requests 的使用方法一致

**返回：**`bool`类型，表示是否连接成功，d 模式下如返回`None`表示不确定

## 📍 d 模式

```python
from DrissionPage import MixPage

page = MixPage('d')
page.get('https://www.baidu.com')
```

## 📍 s 模式

s 模式的`**kwargs`参数与 requests 中该参数使用方法一致，但有一个特点，如果该参数中设置了某一项（如`headers`），该项中的每个项会覆盖从配置中读取的同名项，而不会整个覆盖。  
就是说，如果想继续使用配置中的`headers`信息，而只想修改其中一项，只需要传入该项的值即可。这样可以简化代码逻辑。

实用功能：

- 程序会根据要访问的网址自动在`headers`中加入`Host`和`Referer`项。
- 程序会自动从返回内容中确定编码，一般情况无须手动设置。
- s 模式下页面对象的`timeout`属性是指连接超时时间，不是查找元素超时时间。

```python
from DrissionPage import MixPage

page = MixPage('s')

headers = {'referer': 'gitee.com'}
cookies = {'name': 'value', }
proxies = {'http': '127.0.0.1:1080', 'https': '127.0.0.1:1080'}
page.get(url, headers=headers, cookies=cookies, proxies=proxies)
```

# ✔️ `post()`

此方法是用 post 方式请求页面。大致用法与`get()`一致，但增加一个`data`参数。  
此方法只有 s 模式拥有，调用时，页面对象会自动切换到 s 模式。

**参数：**

- `url`：目标 url
- `data`：提交的数据，可以是`dict`或`str`类型
- `show_errmsg`：是否显示和抛出异常，默认不抛出，连接错误会返回 None
- `retry`：重试次数，与页面对象的设置一致，默认 3 次
- `interval`：重试间隔（秒），与页面对象的设置一致，默认 2 秒
- `**kwargs`：连接参数，s 模式专用

?> **Tips:**  <br>虽然参数里没有`json`参数，但也和 requests 一样可以对`json`参数传值。

```python
from DrissionPage import MixPage

page = MixPage('s')
data = {'username': 'xxxxx', 'pwd': 'xxxxx'}

page.post('http://example.com', data=data)
# 或
page.post('http://example.com', json=data)
```

`data`参数和`json`参数都可接收`str`和`dict`格式数据，即有以下 4 种传递数据的方式：

```python
# 向 data 参数传入字符串
page.post(url, data='xxx')

# 向 data 参数传入字典
page.post(url, data={'xxx': 'xxx'})

# 向 json 参数传入字符串
page.post(url, json='xxx')

# 向 json 参数传入字典
page.post(url, json={'xxx': 'xxx'})
```

# ✔️ 其它请求方式

本库只针对常用的 get 和 post 方式作了优化，但也可以通过提取页面对象内的`Session`对象以原生 requests 代码方式执行其它请求方式。当然，它们工作在 s 模式。

```python
from DrissionPage import MixPage

page = MixPage('s')
# 获取内置的 Session 对象
session = page.session
# 以 head 方式发送请求
response = session.head('https://www.baidu.com')
print(response.headers)
```

**输出：**

```console
{'Accept-Ranges': 'bytes', 'Cache-Control': 'private, no-cache, no-store, proxy-revalidate, no-transform', 'Connection': 'keep-alive', 'Content-Length': '277', 'Content-Type': 'text/html', 'Date': 'Tue, 04 Jan 2022 06:49:18 GMT', 'Etag': '"575e1f72-115"', 'Last-Modified': 'Mon, 13 Jun 2016 02:50:26 GMT', 'Pragma': 'no-cache', 'Server': 'bfe/1.0.8.18'}
```
