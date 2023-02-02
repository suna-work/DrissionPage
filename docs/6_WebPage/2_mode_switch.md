本节介绍`WebPage`的模式切换功能。

`WebPage`的 d 模式，行为与`ChromiumPage`一致，s 模式行为与`SessionPage`一致。

使用`change_mode()`方法进行切换。模式切换的时候会同步登录信息。

# ✔️ `mode`

**类型：**`str`

此属性返回`WebPage`当前模式。

**示例：**

```python
from DrissionPage import WebPage

page = WebPage()
print(page.mode)
```

**输出：**

```console
d
```

---

# ✔️ `change_mode()`

此方法用于切换`WebPage`运行模式。

| 参数名称           | 类型              | 默认值    | 说明                                               |
|:--------------:|:---------------:|:------:| ------------------------------------------------ |
| `mode`         | `str`<br>`None` | `None` | 接收 's' 或 'd'，以切换到指定模式<br>接收`None`则切换到与当前相对的另一个模式 |
| `go`           | `bool`          | `True` | 目标模式是否跳转到原模式的 url                                |
| `copy_cookies` | `bool`          | `True` | 切换时是否复制 cookies 到目标模式                            |

**返回：**`None`

---

# ✔️ 示例

## 📍 切换模式

```python
from DrissionPage import WebPage

page = WebPage()
page.get('https://www.baidu.com')
print(page.mode)
page.change_mode()
print(page.mode)
print(page.title)
```

**输出：**

```console
d
s
百度一下，你就知道
```

本示例中，执行操作如下：

- 初始d 模式访问百度

- 切换到 s 模式，此时会同步登录信息到 s 模式，且在 s 模式访问百度

- 打印 s 模式访问到的页面标题

---

## 📍 自动切换

在某个模式中使用另一个模式独有的方法，会自动切换模式。

!>**注意：**<br>这个功能还在调整中，后续版本表现可能和现在不一致，慎用。

```python
page = WebPage('s')
page.get('https://www.baidu.com')
print(page.mode)
print(page.size)
print(page.mode)
```

**输出：**

```python
s
(1250, 684)
d
```
