Chrome 浏览器的配置繁琐且难以记忆，本库提供一些常用功能的快速设置方法，调用即可修改 ini 文件中该部分内容。对于简单的设置，使用可以使代码更整洁。这些方法统称 easy_set 方法。

!>**注意：**<br>- easy_set 方法仅用于设置 ini 文件，浏览器或 Session 创建后再调用没有效果的。  <br>- 如果是接管已打开的浏览器，这些设置也没有用。<br>- 虽然能简化代码，但会修改 ini
文件，只适合在单页面对象时使用。

# ✔️ 导入

easy_set 方法存放在`DrissionPage.easy_set`路径中，可用以下方法按需导入：

```python
from DrissionPage.easy_set import set_headless, set_paths
```

---

# ✔️ 简单示例

由于 easy_set 方法会直接修改 ini 文件内容，而`ChromiumPage`创建时会默认读取 ini 文件，所以代码看上去比较简洁。

但如果要创建多个页面对象，就要避免用这种方法，否则会造成冲突。

```python
from DrissionPage.easy_set import set_headless
from DrissionPage import ChromiumPage

# 设置无头模式
set_headless(True)

# 启动浏览器
page = ChromiumPage()
```

---

# ✔️ 方法介绍

## 📍 `set_paths()`

此方法用于设置各类路径信息。

| 参数名称               | 类型              | 默认值     | 说明                                                             |
|:------------------:|:---------------:|:-------:| -------------------------------------------------------------- |
| `driver_path`      | `str`<br>`Path` | `None`  | chromdriver 的路径，只`MixPage`和`DriverPage`需要使用                    |
| `chrome_path`      | `str`<br>`Path` | `None`  | 浏览器可执行文件路径，为向后兼容保留，建议用`browser_path`代替                         |
| `browser_path`     | `str`<br>`Path` | `None`  | 浏览器可执行文件路径，与`chrome_path`同时设置时会覆盖`chrome_path`                 |
| `local_port`       | `str`<br>`int`  | `None`  | 浏览器使用的本地端口号                                                    |
| `debugger_address` | `str`           | `None`  | 调试浏览器地址，格式 ip: port，例：`'127.0.0.1:9222'`                       |
| `download_path`    | `str`<br>`Path` | `None`  | 下载文件默认保存路径                                                     |
| `user_data_path`   | `str`<br>`Path` | `None`  | 用户数据文件夹路径                                                      |
| `cache_path`       | `str`<br>`Path` | `None`  | 缓存路径                                                           |
| `ini_path`         | `str`<br>`Path` | `None`  | 要修改的ini文件路径，为`None`表示默认配置文件                                    |
| `check_version`    | `bool`          | `False` | 是否检查设置的 chromedriver 和 Chrome 是否匹配，只`MixPage`和`DriverPage`需要使用 |

**返回：**`None`

---

## 📍 `use_auto_port()`

此方法用于设置是否使用自动分配的端口和临时文件夹。

设置为`True`时，浏览器每次会用可用的端口和临时文件夹保存用户数据，而无视已经保存的端口和路径。

| 参数名称       | 类型              | 默认值    | 说明                          |
|:----------:|:---------------:|:------:| --------------------------- |
| `on_off`   | `bool`          | `True` | `bool`表示开或关                 |
| `ini_path` | `str`<br>`Path` | `None` | 要修改的ini文件路径，为`None`表示默认配置文件 |

**返回：**`None`

---

## 📍 `set_argument()`

此方法用于设置浏览器启动参数。

| 参数名称       | 类型              | 默认值    | 说明                          |
|:----------:|:---------------:|:------:| --------------------------- |
| `arg`      | `str`           | `True` | 属性名                         |
| `value`    | `str`           | `True` | 属性值，有值的属性传入值，没有的传入`None`    |
| `ini_path` | `str`<br>`Path` | `None` | 要修改的ini文件路径，为`None`表示默认配置文件 |

**返回：**`None`

---

## 📍 `set_user_agent()`

此方法用于设置 user agent。

| 参数名称         | 类型              | 默认值    | 说明                          |
|:------------:|:---------------:|:------:| --------------------------- |
| `user_agent` | `str`           | 必填     | user agent文本                |
| `ini_path`   | `str`<br>`Path` | `None` | 要修改的ini文件路径，为`None`表示默认配置文件 |

**返回：**`None`

---

## 📍 `set_proxy()`

此方法用于设置浏览器代理。注意此方法只能设置浏览器代理，不能设置`Session`对象代理。

| 参数名称       | 类型              | 默认值    | 说明                                  |
|:----------:|:---------------:|:------:| ----------------------------------- |
| `proxy`    | `str`           | 必填     | 代理网址和端口，例：`'http://localhost:1080'` |
| `ini_path` | `str`<br>`Path` | `None` | 要修改的ini文件路径，为`None`表示默认配置文件         |

**返回：**`None`

---

## 📍 `set_headless()`

此方法用于设置浏览器是否使用无界面模式。

| 参数名称       | 类型              | 默认值    | 说明                          |
|:----------:|:---------------:|:------:| --------------------------- |
| `on_off`   | `bool`          | `True` | `bool`表示开或关                 |
| `ini_path` | `str`<br>`Path` | `None` | 要修改的ini文件路径，为`None`表示默认配置文件 |

**返回：**`None`

---

## 📍 `set_no_imgs()`

此方法用于设置浏览器是否禁止加载图像。

| 参数名称       | 类型              | 默认值    | 说明                          |
|:----------:|:---------------:|:------:| --------------------------- |
| `on_off`   | `bool`          | `True` | `bool`表示开或关                 |
| `ini_path` | `str`<br>`Path` | `None` | 要修改的ini文件路径，为`None`表示默认配置文件 |

**返回：**`None`

---

## 📍 `set_no_js()`

此方法用于设置浏览器是否禁用 JavaScript。

| 参数名称       | 类型              | 默认值    | 说明                          |
|:----------:|:---------------:|:------:| --------------------------- |
| `on_off`   | `bool`          | `True` | `bool`表示开或关                 |
| `ini_path` | `str`<br>`Path` | `None` | 要修改的ini文件路径，为`None`表示默认配置文件 |

**返回：**`None`

---

## 📍 `set_mute()`

此方法用于设置浏览器是否静音。

| 参数名称       | 类型              | 默认值    | 说明                          |
|:----------:|:---------------:|:------:| --------------------------- |
| `on_off`   | `bool`          | `True` | `bool`表示开或关                 |
| `ini_path` | `str`<br>`Path` | `None` | 要修改的ini文件路径，为`None`表示默认配置文件 |

**返回：**`None`

---

## 📍 `show_settings()`

此方法用于打印 ini 文件内容。

| 参数名称       | 类型              | 默认值    | 说明                          |
|:----------:|:---------------:|:------:| --------------------------- |
| `ini_path` | `str`<br>`Path` | `None` | 要修改的ini文件路径，为`None`表示默认配置文件 |

**返回：**`None` 
