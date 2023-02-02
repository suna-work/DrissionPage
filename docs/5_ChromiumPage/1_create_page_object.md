`ChromiumPage`对象和`WebPage`对象的 d 模式都能收发数据包，本节只介绍`ChromiumPage`的创建，在`WebPage`的章节再对其进行介绍。

# ✔️ `ChromiumPage`初始化参数

| 初始化参数              | 类型                                                  | 默认值    | 说明                                                                                                                           |
|:------------------:|:---------------------------------------------------:|:------:| ---------------------------------------------------------------------------------------------------------------------------- |
| `addr_driver_opts` | `str`<br>`ChrromiumDriver`<br>`ChromiumOptions`<br> | `None` | 浏览器启动配置或接管信息。<br>传入`ChromiumDriver`对象时接管浏览器；<br>传入 ' ip: port' 字符串或`ChromiumOptions`对象时按配置启动或接管浏览器；<br>为`None`时使用配置文件配置启动浏览器 |
| `tab_id`           | `str`                                               | `None` | 要控制的标签页 id，为`None`则控制激活的标签页                                                                                                  |
| `timeout`          | `float`                                             | `None` | 整体超时时间，为`None`则从配置文件中读取，默认 10                                                                                                |

---

# ✔️ 直接创建

这种方式代码最简洁，程序会从默认 ini 文件中读取配置，自动生成页面对象。

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
```

创建`ChromiumPage`对象时会在指定端口启动浏览器，或接管该端口已有浏览器。

默认情况下，程序使用 9222 端口，浏览器可执行文件路径为`'chrome'`。如路径中没找到浏览器可执行文件，Windows 系统下程序会在注册表中查找路径。

如果都没找到，则要用下一种方式手动配置。

!>**注意：**<br>这种方式的程序不能直接打包，因为使用到 ini 文件。可参考“打包程序”一节的方法。

?>**Tips：**<br>您可以修改配置文件中的配置，实现所有程序都按您的须要进行启动，详见”启动配置“章节。

---

# ✔️ 通过配置信息创建

如果须要已指定方式启动浏览器，可使用`ChromiumOptions`。它是专门用于设置浏览器初始状态的类，内置了常用的配置。详细使用方法见“浏览器启动配置”一节。

## 📍 使用方法

`ChromiumOptions`用于管理创建浏览器时的配置，内置了常用的配置，并能实现链式操作。详细使用方法见“启动配置”一节。

| 初始化参数       | 类型     | 默认值    | 说明                                   |
| ----------- | ------ | ------ | ------------------------------------ |
| `read_file` | `bool` | `True` | 是否从 ini 文件中读取配置信息，如果为`False`则用默认配置创建 |
| `ini_path`  | `str`  | `None` | 文件路径，为`None`则读取默认 ini 文件             |

!>**注意：**<br>- 配置对象只有在启动浏览器时生效。<br>- 浏览器创建后再修改这个配置是没有效果的。<br>- 接管已打开的浏览器配置也不会生效。

```python
# 导入 ChromiumOptions
from DrissionPage import ChromiumPage, ChromiumOptions

# 创建浏览器配置对象，指定浏览器路径
do = ChromiumOptions().set_paths(browser_path=r'D:\chrome.exe')
# 用该配置创建页面对象
page = WebPage(addr_driver_opts=do)
```

---

## 📍 直接指定地址创建

`ChromiumPage`可以直接接收浏览器地址来创建，格式为 'ip:port'。

使用这种方式时，如果浏览器已存在，程序会直接接管；如不存在，程序会读取默认配置文件配置，在指定端口启动浏览器。

```python
page = ChromiumPage(addr_driver_opts='127.0.0.1:9333')
```

---

## 📍 使用指定 ini 文件创建

以上方法是使用默认 ini 文件中保存的配置信息创建对象，你可以保存一个 ini 文件到别的地方，并在创建对象时指定使用它。

```python
from DrissionPage import ChromiumPage, ChromiumOptinos

# 创建配置对象时指定要读取的ini文件路径
co = ChromiumOptinos(ini_path=r'./config1.ini')
# 使用该配置对象创建页面
page = ChromiumPage(addr_driver_opts=co)
```

---

# ✔️ 传递控制权

当须要使用多个页面对象共同操作一个页面时，可在对象间传递驱动器。

这可以实现多个页面对象共同控制一个浏览器。

```python
# 创建一个页面
page1 = ChormiumPage()
# 获取页面对象的浏览器控制器
driver = page1.driver
# 把控制器对象在第二个页面对象初始化时传递进去
page2 = ChormiumPage(driver_or_options=driver)
```

---

# ✔️ 接管已打开的浏览器

页面对象创建时，只要指定的地址（ip: port）已有浏览器在运行，就会直接接管。无论浏览器是下面哪种方式启动的。

## 📍 用程序启动的浏览器

默认情况下，创建浏览器页面对象时会自动启动一个浏览器。只要这个浏览器不关闭，下次运行程序时会接管同一个浏览器继续操作（配置的 ip: port 信息不变）。

这种方式极大地方便了程序的调试，使程序不必每次重新开始，可以单独调试某个功能。

```python
from DrissionPage import ChromiumPage

# 创建对象同时启动浏览器，如果浏览器已经存在，则接管它
page = ChromiumPage()  
```

---

## 📍 手动打开的浏览器

如果须要手动打开浏览器再接管，可以这样做：

- 右键点击浏览器图标，选择属性

- 在“目标”路径后面加上` --remote-debugging-port=端口号`（注意最前面有个空格）

- 点击确定

- 在程序中的浏览器配置中指定接管该端口浏览器

文件快捷方式的目标路径设置：

```
D:\chrome.exe --remote-debugging-port=9222
```

程序代码：

```python
from DrissionPage import ChromiumPage, ChromiumOptions

co = ChromiumOptions().set_paths(local_port=9222)
page = ChromiumPage(addr_driver_opts=co)
```

!> **注意：**<br>接管浏览器时只有`local_port`、`debugger_address`参数是有效的。

---

## 📍 bat 文件启动的浏览器

可以把上一种方式的目标路径设置写进 bat 文件（Windows系统），运行 bat 文件来启动浏览器，再用程序接管。

新建一个文本文件，在里面输入以下内容（路径改为自己电脑的）：

```console
"D:\chrome.exe" --remote-debugging-port=9222
```

保存后把后缀改成 bat，然后双击运行就能在 9222 端口启动一个浏览器。程序代码则和上一个方法一致。

---

# ✔️ 多浏览器共存

如果想要同时操作多个浏览器，或者自己在使用其中一个上网，同时控制另外几个跑自动化，就须要给这些被程序控制的浏览器设置单独的**端口**和**用户文件夹**，否则会造成冲突。

## 📍 指定独立端口和数据文件夹

每个要启动的浏览器使用一个独立的`ChromiumOptions`对象进行设置：

```python
from DrissionPage import ChromiumPage, ChromiumOptions

# 创建多个配置对象，每个指定不同的端口号和用户文件夹路径
do1 = ChromiumOptions().set_paths(local_port=9111, user_data_path=r'D:\data1')
do2 = ChromiumOptions().set_paths(local_port=9222, user_data_path=r'D:\data2')

# 创建多个页面对象
page1 = ChromiumPage(addr_driver_opts=do1)
page2 = ChromiumPage(addr_driver_opts=do2)

# 每个页面对象控制一个浏览器
page1.get('https://www.baidu.com')
page2.get('http://www.163.com')
```

?>**Tips：**<br>每个浏览器都要设置独立的端口号和用户文件夹，二者缺一不可。

---

## 📍 `auto_port()`方法

`ChromiumOptions`对象的`auto_port()`方法，可以指定程序每次使用空闲的端口和临时用户文件夹创建浏览器。也是每个浏览器要使用独立的`ChromiumOptions`对象。

但这种方法创建的浏览器不能重复使用。

```python
from DrissionPage import ChromiumPage, ChromiumOptions

co1 = ChromiumOptions().auto_port()
co2 = ChromiumOptions().auto_port()

page1 = ChromiumPage(addr_driver_opts=co1)
page2 = ChromiumPage(addr_driver_opts=co2)

page1.get('https://www.baidu.com')
page2.get('http://www.163.com')
```

---

## 📍 在 ini 文件设置使用自动分配

可以把自动分配的配置记录到 ini 文件，这样无须创建`ChromiumOptions`，每次启动的浏览器都是独立的，不会冲突。但和`auto_port()`一样，这些浏览器也不能复用。

```python
from DrissionPage.easy_set import use_auto_port

use_auto_port(True)
```

这段代码把记录该配置到 ini 文件，只需运行一次，要关闭的话把参数换成`False`再执行一次即可。

```python
from DrissionPage import ChromiumPage

page1 = ChromiumPage()
page2 = ChromiumPage()

page1.get('https://www.baidu.com')
page2.get('http://www.163.com')
```
