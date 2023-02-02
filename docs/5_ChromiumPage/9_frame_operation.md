`<iframe>`元素是一种特殊的元素，它既是元素，也是页面，因此独立一个章节对其进行介绍。

与 selenium 不同，DrissionPage 无需切入切出即可处理`<iframe>`元素。因此可实现跨级元素查找、元素内部单独跳转、同时操作`<iframe>`内外元素、多线程控制多个`<iframe>`等操作，功能更灵活，逻辑更清晰。

我们使用菜鸟教程在线编辑器来演示：

[菜鸟教程在线编辑器 (runoob.com)](https://www.runoob.com/try/try.php?filename=tryhtml_iframe)

源代码框内容要作一点调整，然后按“点击运行”：

```html
<!DOCTYPE html>
<html>        
    <head> 
        <meta charset="utf-8"> 
        <title>菜鸟教程(runoob.com)</title> 
    </head> 

    <body>
        <iframe id="sss" src="https://www.runoob.com">
            <p>您的浏览器不支持  iframe 标签。</p>
        </iframe>
    </body>
</html>
```

按`F12`，可以看到网页右侧是一个两层`<iframe>`，一个 id 是`'iframeResult'`的`<iframe>`里面有一个 id 是`'sss'`的`<iframe>`。最里层的`<iframe>`
页面指向 https://www.runoob.com。

---

# ✔ 获取`<iframe>`对象

现在我们获取最里层`<iframe>`对象。方法和直接获取元素一样：

```python
iframe = page('#sss')
print(iframe.html)
```

**输出：**

```console
<iframe id="sss" src="https://www.runoob.com"><html><head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>菜鸟教程 - 学的不仅是技术，更是梦想！</title>

  <meta name="robots" content="max-image-preview:large">

下面省略。。。
```

这个`ChromiumFrame`对象既是页面也是元素，下面演示其功能。

---

# ✔ 查找`<iframe>`内元素

从刚才获取元素对象看出，我们并不须要先切入 id 为`'iframeResult'`的`<iframe>`，就可以获取到里面的元素。所以我们获取元素也并不一定要先获取到`ChromiumFrame`对象。

## 📍 在`<iframe>`内查找

使用我们刚才获取到的元素，可以在里面查找元素：

```python
ele = iframe('首页')
print(ele)
```

**输出：**

```console
<ChromiumElement a href='https://www.runoob.com/' data-id='index' title='菜鸟教程' class='current'>
```

---

## 📍 页面跨`<iframe>`查找

如果`<iframe>`元素的网址和主页面是同域的，我们可以直接用页面对象查找`<iframe>`内部元素，而无需先获取`ChromiumFrame`对象：

```python
ele = page('首页')
print(ele)
```

**输出：**

```console
<ChromiumElement a href='https://www.runoob.com/' data-id='index' title='菜鸟教程' class='current'>
```

只要是同域名的，无论跨多少曾`<iframe>`都能用页面对象直接获取。

---

## 📍 与 selenium 对比

`WebPage`：

```python
from DrissionPage import WebPage

page = WebPage()
ele = page('首页')
```

`MixPage`（基于 selenium）：

```python
from DrissionPage import MixPage

page = MixPage()
page.to_frame('#iframeResult')
page.to_frame('#sss')
ele = page('首页')
page.to_frame.main()
```

可见，原来的逻辑要切入切出，比较繁琐。

---

## 📍 重要事项

如果`<iframe>`跟当前标签页是不同域名的，不能使用页面对象直接查找其中元素，只能先获取其`ChromiumFrame`元素对象，再在这个对象中查找。

---

# ✔ `ChromiumFrame`的元素特征

正如上面所说，`ChromiumFrame`既是元素也是页面，这里说一下其元素方面的用法。

## 📍 `tab_id`

**类型：**`str`

此属性返回`<iframe>`元素所在标签页的 id。

---

## 📍 `tag`

**类型：**`str`

此属性返回元素名称。

---

## 📍 `html`

**类型：**`str`

此属性返回整个`<iframe>`元素的 outerHTML 文本。

---

## 📍 `inner_html`

**类型：**`str`

此属性返回 innerHTML 文本。

---

## 📍 `attrs`

**类型：**`dict`

此属性以`dict`形式返回元素所有 attribute 属性。

---

## 📍 `size`

**类型：**`Tuple[int, int]`

此属性以`tuple`形式返回元素大小。

---

## 📍 `location`

**类型：**`Tuple[int, int]`

此属性以`tuple`形式返回元素在主页面中的位置，左上角为 (0, 0)。

---

## 📍 `is_displayed`

**类型：**`bool`

此属性返回元素是否可见。

---

## 📍 `xpath`

**类型：**`str`

此属性返回元素在其页面上的 xpath 路径。

---

## 📍 `css_path`

**类型：**`str`

此属性返回元素在其页面上的 css selector 路径。

---

## 📍 `attr()`

此方法用于一个获取元素 attribute 属性。

| 参数名称   | 类型    | 默认值 | 说明  |
|:------:|:-----:|:---:| --- |
| `attr` | `str` | 必填  | 属性名 |

| 返回类型   | 说明            |
|:------:| ------------- |
| `str`  | 属性值文本         |
| `None` | 没有该属性返回`None` |

---

## 📍 `set_attr()`

此方法用于设置元素的 attribute 属性。

| 参数名称    | 类型    | 默认值 | 说明  |
|:-------:|:-----:|:---:| --- |
| `attr`  | `str` | 必填  | 属性名 |
| `value` | `str` | 必填  | 属性值 |

**返回：**`None`

---

## 📍 `remove_attr()`

此方法用于删除元素的 attribute 属性。

| 参数名称   | 类型    | 默认值 | 说明  |
|:------:|:-----:|:---:| --- |
| `attr` | `str` | 必填  | 属性名 |

**返回：**`None`

---

## 📍 相对定位

相对定位方法与普通元素一致，详见获取元素章节。

- `parent()`：返回上面某一级父元素。

- `prev()`：返回前面的一个兄弟元素。

- `next()`：返回后面的一个兄弟元素。

- `before()`：返回当前元素前面的一个元素。

- `after()`：返回当前元素后面的一个元素。

- `prevs()`：返回前面全部兄弟元素或节点组成的列表。

- `nexts()`：返回后面全部兄弟元素或节点组成的列表。

- `befores()`：返回当前元素后面符合条件的全部兄弟元素或节点组成的列表。

---

# ✔ `ChromiumFrame`的页面特征

## 📍 `url`

**类型：**`str`

此属性返回页面当前 url。

---

## 📍 `title`

**类型：**`str`

此属性返回页面当前 title 文本。

---

## 📍 `cookies`

**类型：**`dict`

此属性返回页面当前 cookies 内容。

---

## 📍 `get()`

此方法用于实现`<iframe>`页面跳转，使用方法与`ChromiumPage`一致。

```python
iframe.get('https://www.runoob.com/css3/css3-tutorial.html')
```

---

## 📍 `refresh()`

此方法用于刷新页面。

**参数**： 无

**返回：**`None`

```python
iframe.refresh()
```

---

## 📍 `ready_state`

**类型：**`str`

此属性为页面加载状态，包括`'loading'`、`'interactive'`、`'complete'`3 种。

---

## 📍 `is_loading`

**类型：**`bool`

此属性返回页面是否正在加载。

---

## 📍 `active_ele`

**类型：**`ChromiumElement`

此属性返回页面中焦点所在元素。

---

## 📍 `frame_size`

**类型：**`Tuple[int, int]`

此属性以`tuple`形式返回页面大小。

---

## 📍 `run_js()`

此方法用于在`<iframe>`内执行 js 脚本。

| 参数名称      | 类型     | 默认值     | 说明                                              |
|:---------:|:------:|:-------:| ----------------------------------------------- |
| `script`  | `str`  | 必填      | js 脚本文本                                         |
| `as_expr` | `bool` | `False` | 是否作为表达式运行，为`True`时`args`参数无效                    |
| `*args`   | -      | 无       | 传入的参数，按顺序在js文本中对应`argument[0]`、`argument[1]`... |

| 返回类型  | 说明     |
|:-----:| ------ |
| `Any` | 脚本执行结果 |

---

## 📍 `scroll`

`ChromiumFrame`的滚动方法与页面或元素是一致的。

**示例：** 使`<iframe>`元素向下滚动 300 像素

```python
iframe.scroll.down(300)
```