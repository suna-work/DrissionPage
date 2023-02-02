本节介绍打包程序须要注意的事项。

因为程序用到 ini 文件，而打包时不会自动带上，因此直接打包是会导致运行出错。

解决办法：

- 手动带上 ini 文件，并在程序中指定路径

- 把配置信息写在程序中，不带 ini 文件

# ✔️ 手动带上 ini

在程序中用相对路径方式指定 ini 文件，并且打包后手动把 ini 文件复制到程序文件夹。

`WebPage`：

```python
from DrissionPage import WebPage, ChromiumOptions, SessionOptions

do = ChromiumOptions(ini_path=r'.\configs.ini')
so = SessionOptions(ini_path=r'.\configs.ini')
page = WebPage(driver_or_options=do, session_or_options=so)
```

`MixPage`：

```python
from DrissionPage import Drission, MixPage

drission = Drission(ini_path=r'.\configs.ini')  # ini文件放在程序相同路径下
page = MixPage(drission=drission)
```

---

# ✔️ 不使用 ini

这种方法须把所有配置信息写到代码里。

`WebPage`：

```python
from DrissionPage import WebPage, ChromiumOptions, SessionOptions

do = ChromiumOptions(read_file=False)  # 不读取文件方式新建配置对象
so = SessionOptions(read_file=False)
do.set_paths(chrome_path=r'.\chrome.exe')  # 输入配置信息

page = WebPage(driver_or_options=do, session_or_options=so)
```

`MixPage`：

```python
from DrissionPage import MixPage, DriverOptions, SessionOptions

do = DriverOptions(read_file=False)
so = SessionOptions(read_file=False)
page = MixPage(driver_options=do, session_options=so)
```

!> **注意** <br>这个时候 driver 和 session 两个参数都要输入内容，如果其中一个不需要设置可以输入`False`。

如：

```python
page = WebPage(driver_or_options=do, session_or_options=False)
```

---

# ✔️ 实用示例

通常，我会把一个绿色浏览器和打包后的 exe 文件放在一起，程序中用相对路径指向该浏览器，这样拿到别的电脑也可以正常实用。

```python
from DrissionPage import WebPage, ChromiumOptions

do = ChromiumOptions(read_file=False).set_paths(local_port='9888',
                                                browser_path=r'.\Chrome\chrome.exe',
                                                user_data_path=r'.\Chrome\userData')
page = WebPage(driver_or_options=do, session_or_options=False)
# 注意：session_or_options=False

page.get('https://www.baidu.com')
```

注意以下两点，程序就会跳过读取 ini 文件：

- `ChromiumOptions()`里要设置`read_file=False`
- 如果不传入某个模式的配置（示例中为 s 模式），要在页面对象初始化时设置对应参数为`False`