浏览器的启动配置非常繁杂，本库使用`ChromiumOptions`类管理启动配置，并且内置了常用配置的设置接口。

!> **注意：** <br>该对象只能用于浏览器的启动，浏览器启动后，再修改该配置没有任何效果。接管已打开的浏览器时，启动配置也是无效的。

# ✔️ 创建对象

## 📍 导入

```python
from DrissionPage import ChromiumOptions
```

---

## 📍 `ChromiumOptions`

`ChromiumOptions`对象用于管理浏览器初始化配置。可从配置文件中读取配置来进行初始化。

| 初始化参数       | 类型              | 默认值    | 说明                                 |
|:-----------:|:---------------:|:------:| ---------------------------------- |
| `read_file` | `bool`          | `True` | 是否从 ini 文件中读取配置信息，为`False`则用默认配置创建 |
| `ini_path`  | `Path`<br>`str` | `None` | 指定 ini 文件路径，为`None`则读取内置 ini 文件    |

创建配置对象：

```python
from DrissionPage import ChromiumOptions

co = ChromiumOptions()
```

默认情况下，`ChromiumOptions`对象会从 ini 文件中读取配置信息，当指定`read_file`参数为`False`时，则以默认配置创建。

---

# ✔️ 使用方法

创建配置对象后，可调整配置内容，然后在页面对象创建时以参数形式把配置对象传递进去，页面对象会根据配置对象的内容对浏览器进行初始化。

```python
from DrissionPage import WebPage, ChromiumOptions

# 创建配置对象（默认从 ini 文件中读取配置）
co = ChromiumOptions()
# 设置不加载图片、静音
co.set_no_imgs(True).set_mute(True)

# 以该配置创建页面对象
page = WebPage(driver_or_options=co)
```

---

# ✔️ 启动参数配置

Chromium 内核浏览器有一系列的启动配置，以`--`开头，可在浏览器创建时传入。如`--headless`无界面模式，`--disable-images`禁用图像等。有些参数只有参数名，有些会带有值。

启动参数非常多，详见：[List of Chromium Command Line Switches « Peter Beverloo](https://peter.sh/experiments/chromium-command-line-switches/)

`set_argument()`和`remove_argument()`方法用于设置浏览器启动命令行参数。

## 📍 `set_argument()`

此方法用于设置启动参数，带值和不带值的参数项都可以。

| 参数名称    | 类型                         | 默认值    | 说明                                                |
|:-------:|:--------------------------:|:------:| ------------------------------------------------- |
| `arg`   | `str`                      | 必填     | 启动参数名称                                            |
| `value` | `str`<br>`None`<br>`False` | `None` | 参数的值。带值的参数传入属性值，没有的传入`None`。<br>如传入`False`，删除该参数。 |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

**示例：** 无值和有值的参数设置

```python
# 设置用无头模式启动浏览器
co.set_argument('--headless')
# 设置浏览器默认 user agent
co.set_argument('--user-agent', 'Mozilla/5.0 (Macintos.....')
```

---

## 📍 `remove_argument()`

此方法用于在启动配置中删除一个启动参数，只要传入参数名称即可，不需要传入值。

| 参数名称  | 类型    | 默认值 | 说明                  |
|:-----:|:-----:|:---:| ------------------- |
| `arg` | `str` | 必填  | 参数名称，有值的设置项传入设置名称即可 |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象自身 |

**示例：** 删除无值和有值的参数设置

```python
# 删除--headless参数
co.remove_argument('--headless')
# 删除--user-agent参数
co.remove_argument('--user-agent')
```

---

# ✔️ 插件配置

`add_extension()`和`remove_extensions()`用于设置浏览器启动时要加载的插件。可以指定数量不限的插件。

## 📍 `add_extension()`

此方法用于添加一个插件到浏览器。

| 参数名称   | 类型              | 默认值 | 说明   |
|:------:|:---------------:|:---:| ---- |
| `path` | `str`<br>`Path` | 必填  | 插件路径 |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

?>**Tips：**<br>根据作者的经验，把插件文件解压到一个独立文件夹，然后把插件路径指向这个文件夹，会比较稳定。

**示例：**

```python
co.add_extension(r'D:\SwitchyOmega')
```

---

## 📍 `remove_extensions()`

此方法用于移除配置对象中保存的所有插件路径。如须移除部分插件，请移除全部后再重新添加需要的插件。

**参数：** 无

**返回：** 配置对象自身

```python
co.remove_extensions()
```

---

# ✔️ 用户文件配置

除了启动参数，还有大量配置信息保存在 preferences 文件，以下方法用于对用户文件进行设置。

## 📍 `set_user()`

Chromium 浏览器支持多用户配置，我们可以选择使用哪一个。默认为`'Default'`。

| 参数名称   | 类型    | 默认值         | 说明        |
|:------:|:-----:|:-----------:| --------- |
| `user` | `str` | `'Default'` | 用户配置文件夹名称 |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

**示例：**

```python
co.set_user(user='Profile 1')
```

---

## 📍 `set_pref()`

此方法用于设置用户配置文件里的一个配置项。

在哪里可以查到所有的配置项？作者也没找到，知道的请告知。谢谢。

| 参数名称    | 类型    | 默认值 | 说明    |
|:-------:|:-----:|:---:| ----- |
| `arg`   | `str` | 必填  | 设置项名称 |
| `value` | `str` | 必填  | 设置项值  |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

**示例：**

```python
co.set_pref(arg='profile.default_content_settings.popups', value='0')
```

---

## 📍 `remove_pref()`

此方法用于在当前配置对象中删除一个`pref`配置项。

| 参数名称  | 类型    | 默认值 | 说明    |
|:-----:|:-----:|:---:| ----- |
| `arg` | `str` | 必填  | 设置项名称 |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

**示例：**

```python
co.remove_pref(arg='profile.default_content_settings.popups')
```

---

## 📍 `remove_pref_from_file()`

此方法用于在用户配置文件删除一个配置项。注意与上一个方法不一样，如果用户配置文件中已经存在某个项，用`remove_pref()`是不能删除的，只能用`remove_pref_from_file()`删除。

| 参数名称  | 类型    | 默认值 | 说明    |
|:-----:|:-----:|:---:| ----- |
| `arg` | `str` | 必填  | 设置项名称 |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

**示例：**

```python
co.remove_pref_from_file(arg='profile.default_content_settings.popups')
```

---

# ✔️ 运行参数配置

页面对象运行时需要用到的参数，也可以在`ChromiumOptions`中设置。

## 📍 `set_paths()`

此方法用于设置各种路径信息。对有传入值的路径进行设置，为`None`的则无视。

| 参数名称               | 类型              | 默认值    | 说明                                                          |
|:------------------:|:---------------:|:------:| ----------------------------------------------------------- |
| `browser_path`     | `str`<br>`Path` | `None` | 浏览器可执行文件路径                                                  |
| `local_port`       | `str`<br>`int`  | `None` | 浏览器要使用的本地端口号                                                |
| `debugger_address` | `str`           | `None` | 浏览器地址，例：127.0.0.1:9222，如与`local_port`一起设置，会覆盖`local_port`的值 |
| `download_path`    | `str`<br>`Path` | `None` | 下载文件默认保存路径                                                  |
| `user_data_path`   | `str`<br>`Path` | `None` | 用户数据文件夹路径                                                   |
| `cache_path`       | `str`<br>`Path` | `None` | 缓存路径                                                        |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

**示例：**

```python
co.set_paths(local_port=9333, user_data_path=r'D:\tmp')
```

---

## 📍 `auto_port()`

此方法用于设置是否使用自动分配的端口。

如果设置为`True`，程序会自动寻找一个可用端口，并在系统临时文件夹创建一个文件夹，用于储存浏览器数据。由于端口和用户文件夹都是唯一的，所以用这种方式启动的浏览器不会产生冲突，但也无法多次启动程序时重复接管同一个浏览器。

`set_paths()`方法中`local_port`和`user_data_path`参数，会和`auto_port()`互相覆盖，即以后调用的为准。

| 参数名称     | 类型     | 默认值    | 说明               |
|:--------:|:------:|:------:| ---------------- |
| `on_off` | `bool` | `True` | 是否开启自动分配端口和用户文件夹 |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

**示例：**

```python
co.auto_port(True)
```

!>**注意：**<br>启用此功能后即会获取端口和新建临时用户数据文件夹，若此时用`save()`方法保存配置到 ini 文件，ini 文件中的设置会被该端口和文件夹路径覆盖。这个覆盖对使用并没有很大影响。

---

## 📍 `set_timeouts()`

此方法用于设置几种超时时间，以秒为单位。超时用法详见使用方法章节。

| 参数名称       | 类型               | 默认值    | 说明                                                            |
|:----------:|:----------------:|:------:| ------------------------------------------------------------- |
| `implicit` | `int`<br>`float` | `None` | 默认超时时间，用于元素等待、alert 等待、`WebPage`的 s 模式连接等等，除以下两个参数的场景，都使用这个设置 |
| `pageLoad` | `int`<br>`float` | `None` | 页面加载超时时间                                                      |
| `script`   | `int`<br>`float` | `None` | JavaScript 运行超时时间                                             |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

**示例：**

```python
co.set_timeouts(implicit=10)
```

---

## 📍 `set_page_load_strategy()`

此方法用于设置网页加载策略。

加载策略是指强制页面停止加载的时机，如加载完 DOM 即停止，不加载图片资源等，以提高自动化效率。

无论设置哪种策略，加载时间都不会超过`set_timeouts()`中`pageLoad`参数设置的时间。

加载策略：

- `'normal'`：阻塞进程，等待所有资源下载完成（默认）

- `'eager'`：DOM 就绪即停止加载

- `'none'`：网页连接成功即停止加载

| 参数名称    | 类型    | 默认值 | 说明                               |
|:-------:|:-----:|:---:| -------------------------------- |
| `value` | `str` | 必填  | 可接收`'normal'`、`'eager'`、`'none'` |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

**示例：**

```python
co.set_page_load_strategy('eager')
```

---

## 📍 `set_proxy()`

该方法用于设置浏览器代理。

| 参数名称    | 类型    | 默认值 | 说明                                      |
|:-------:|:-----:|:---:| --------------------------------------- |
| `proxy` | `str` | 必填  | 格式：协议://ip:port<br>当不指定协议时，默认使用 http 代理 |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

**示例：**

```python
co.set_proxy('http://localhost:1080')
```

---

# ✔️ 其它配置

作者将一些常用的配置封装成方法，可以直接调用。

## 📍 `set_headless()`

该方法用于设置是否已无界面模式启动浏览器。

| 参数名称     | 类型     | 默认值    | 说明                  |
|:--------:|:------:|:------:| ------------------- |
| `on_off` | `bool` | `True` | `True`和`False`表示开或关 |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

**示例：**

```python
co.set_headless(True)
```

!>**注意：**<br>经实测，Chrome 使用无界面模式时，由 js 生成的元素可能不能加载。

---

## 📍 `set_no_imgs()`

该方法用于设置是否禁止加载图片。

| 参数名称     | 类型     | 默认值    | 说明                  |
|:--------:|:------:|:------:| ------------------- |
| `on_off` | `bool` | `True` | `True`和`False`表示开或关 |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

**示例：**

```python
co.set_no_imgs(True)
```

---

## 📍 `set_no_js()`

该方法用于设置是否禁用 JavaScript。

| 参数名称     | 类型     | 默认值    | 说明                  |
|:--------:|:------:|:------:| ------------------- |
| `on_off` | `bool` | `True` | `True`和`False`表示开或关 |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

**示例：**

```python
co.set_no_js(True)
```

---

## 📍 `set_mute()`

该方法用于设置是否静音。

| 参数名称     | 类型     | 默认值    | 说明                  |
|:--------:|:------:|:------:| ------------------- |
| `on_off` | `bool` | `True` | `True`和`False`表示开或关 |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

**示例：**

```python
co.set_mute(True)
```

---

## 📍 `set_user_agent()`

该方法用于设置 user agent。

| 参数名称         | 类型    | 默认值 | 说明           |
|:------------:|:-----:|:---:| ------------ |
| `user_agent` | `str` | 必填  | user agent文本 |

| 返回类型              | 说明     |
| ----------------- | ------ |
| `ChromiumOptions` | 配置对象本身 |

**示例：**

```python
co.set_user_agent(user_agent='Mozilla/5.0 (Macintos.....')
```

---

# ✔️ 保存设置到文件

您可以把不同的配置保存到各自的 ini 文件，以便适应不同的场景。

## 📍 `save()`

此方法用于保存配置项到一个 ini 文件。

| 参数名称   | 类型              | 默认值    | 说明                              |
|:------:|:---------------:|:------:| ------------------------------- |
| `path` | `str`<br>`Path` | `None` | ini 文件的路径， 传入`None`保存到当前读取的配置文件 |

| 返回类型  | 说明             |
| ----- | -------------- |
| `str` | 保存的 ini 文件绝对路径 |

**示例：**

```python
# 保存当前读取的ini文件
co.save()

# 把当前配置保存到指定的路径
co.save(path=r'D:\tmp\settings.ini')
```

---

## 📍 `save_to_default()`

此方法用于保存配置项到固定的默认 ini 文件。默认 ini 文件是指随 DrissionPage 内置的那个。

**参数：** 无

| 返回类型  | 说明             |
| ----- | -------------- |
| `str` | 保存的 ini 文件绝对路径 |

**示例：**

```python
co.save_to_default()
```

---

# ✔️ `ChromiumOptions`属性

## 📍 `debugger_address`

该属性为要控制的浏览器地址，格式为 ip:port，默认为`'127.0.0.0:9222'`。可对其赋值进行设置。也可以用后文介绍的`set_paths()`方法设置。

**类型：**`str`

```python
co.debugger_address = 'localhost:9333'
```

---

## 📍 `browser_path`

该属性返回浏览器可执行文件的路径。

**类型：**`str`

---

## 📍 `user_data_path`

该属性返回用户数据文件夹路径。

**类型：**`str`

---

## 📍 `download_path`

该属性返回默认下载路径文件路径。

**类型：**`str`

---

## 📍 `user`

该属性返回用户配置文件夹名称。

**类型：**`str`

---

## 📍 `page_load_strategy`

该属性返回页面加载策略。有`'normal'`、`'eager'`、`'none'`三种

**类型：**`str`

---

## 📍 `timeouts`

该属性返回超时设置。包括三种：`'implicit'`、`'pageLoad'`、`'script'`。

**类型：**`dict`

```python
print(co.timeouts)
```

**输出：**

```console
{
    'implicit': 10,
    'pageLoad': 30,
    'script': 30
}
```

---

## 📍 `proxy`

该属性返回代理设置。

**类型：**`str`

---

## 📍 `arguments`

该属性以`list`形式返回浏览器启动参数。

**类型：**`list`

---

## 📍 `extensions`

该属性以`list`形式返回要加载的插件路径。

**类型：**`list`

---

## 📍 `preferences`

该属性返回用户首选项配置。

**类型：**`dict`