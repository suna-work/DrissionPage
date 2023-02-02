本库使用 ini 文件记录浏览器或`Session`对象的启动配置。便于配置复用，免于在代码中加入繁琐的配置信息。  
默认情况下，页面对象启动时自动加载文件中的配置信息。  
也可以在默认配置基础上用简单的方法再次修改，再保存到 ini 文件。  
也可以保存多个 ini 文件，按不同项目须要调用。

!> **注意：**  <br>- ini 文件仅用于管理启动配置，页面对象创建后再修改 ini 文件是没用的。  <br>- 如果是接管已打开的浏览器，这些设置也没有用。  <br>- 每次升级本库，ini
文件都会被重置，可另存到其它路径以免重置。

# ✔️ ini 文件内容

ini 文件初始内容如下。

```
[paths]
chromedriver_path = 
download_path = 

[chrome_options]
debugger_address = 127.0.0.1:9222
binary_location = chrome
arguments = ['--no-first-run', '--no-sandbox', '--disable-gpu', '--ignore-certificate-errors', '--disable-infobars', '--disable-popup-blocking']
extensions = []
experimental_options = {'prefs': {'profile.default_content_settings.popups': 0, 'profile.default_content_setting_values': {'notifications': 2}, 'plugins.plugins_list': [{'enabled': False, 'name': 'Chrome PDF Viewer'}]}, 'useAutomationExtension': False, 'excludeSwitches': ['enable-automation']}
page_load_strategy = normal
user = Default
auto_port = False

[session_options]
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'connection': 'keep-alive', 'accept-charset': 'GB2312,utf-8;q=0.7,*;q=0.7'}

[timeouts]
implicit = 10
page_load = 30
script = 30

[proxies]
http = 
https = 
```

---

# ✔️ 文件位置

默认配置文件存放在库文件夹下，文件名为 configs.ini。  
用户可另存其它配置文件，或从另存的文件读取配置，但默认文件的位置和名称不会改变。

---

# ✔️ 使用默认配置文件启动

## 📍 使用页面对象自动加载

这是默认启动方式。

```python
from DrissionPage import WebPage

page = WebPage()
```

---

## 📍 使用配置对象加载

这种方式一般用于加载配置后须要进一步修改。

```python
from DrissionPage import ChromiumOptions, SessionOptions, WebPage

do = ChromiumOptions(ini_path=r'D:\setting.ini')
so = SessionOptions(ini_path=r'D:\setting.ini')

page = WebPage(driver_or_options=do, session_or_options=so)
```

---

## 📍 使用 Drission 对象加载

这种方式一般用于加载非默认配置文件，或须在多个页面对象间传递`Drission`对象的情况。这是`MixPage`独有的加载方式。

```python
from DrissionPage import MixPage, Drission

ds = Drission(ini_path=r'D:\config1.ini')
page = MixPage(drission=ds)
```

---

# ✔️ 保存/另存 ini 文件

```python
from DrissionPage import ChromiumOptions

co = ChromiumOptions()

# 修改一些设置
co.set_no_imgs()

# 保存到当前打开的ini文件
co.save()
# 保存到指定位置的配置文件
co.save(r'D:\config1.ini')
# 保存到默认配置文件
co.save_to_default()
```