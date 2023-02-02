本节介绍与浏览器元素的交互。浏览器元素对象为`ChromiumElement`。

# ✔️ 点击元素

## 📍 `click()`

此方法用于点击元素。可选择模拟点击或 js 点击。并支持点击重试功能。

| 参数名称           | 类型                         | 默认值     | 说明                                                                                                                      |
|:--------------:|:--------------------------:|:-------:| ----------------------------------------------------------------------------------------------------------------------- |
| `by_js`        | `bool`                     | `None`  | 是否用 js 方式点击<br>为`True`时直接用 js 点击，不重试；<br>为`False`时只用模拟点击，且根据`retry`设置重试；<br>为`None`时先用模拟点击并根据`retyr`设置重试，如全部失败，改用 js 点击 |
| `retry`        | `bool`                     | `False` | 遇到其它元素遮挡时，是否重试                                                                                                          |
| `timeout`      | `int`<br>`float`           | `0.2`   | 点击失败重试超时时间，为`None`时使用父页面`timeout`设置，`retry`为`True`时才生效                                                                  |
| `wait_loading` | `int`<br>`float`<br>`True` | `0`     | 指定等待页面进入加载状态的超时时间，为`True`时等待 2 秒，默认 0 秒                                                                                 |

| 返回类型   | 说明     |
|:------:| ------ |
| `bool` | 是否点击成功 |

点击重试的设计，可以用于检测页面上的遮罩层是否消失。遮罩层经常出现在 js 方式翻页的时候，它的覆盖会阻碍模拟点击，所以可以通过对其下面的元素不断重试点击，来判断遮罩层是否存在。  
而如果直接使用 js 进行点击，则可无视任何遮挡，只要元素在 DOM 内，就能点击得到，这样可以根据须要灵活地对元素进行操作。

通常，点击链接后立刻获取新页面的元素，程序可自动等待元素加载，但若跳转前的页面拥有和跳转后页面相同定位符的元素，会导致过早获取元素，跳转后失效的问题。可以对`wait_loading`参数设置一个超时时间，点击后程序会等待页面进入
loading 状态，才会继续往下执行，从而避免上述问题。

**示例：**

```python
# 对ele元素进行点击
ele.click()

# 用js方式点击ele元素
ele.click(by_js=True)

# 假设遮罩层出现，ele是遮罩层下方的元素
ele.click(by_js=False, retry=True, timeout = 10)  # 不断重试点击，直到遮罩层消失，或到达 10 秒
ele.click(by_js=True)  # 无视遮罩层，直接用 js 点击下方元素
```

---

## 📍 `click_at()`

此方法用于带偏移量点击元素，偏移量相对于元素左上角坐标。不传入`offset_x`和`offset_y`时点击元素中上部位置。   
点击的目标不一定在元素上，可以传入负值，或大于元素大小的值，点击元素附近的区域。向右和向下为正值，向左和向上为负值。

| 参数名称       | 类型    | 默认值      | 说明                                    |
|:----------:|:-----:|:--------:| ------------------------------------- |
| `offset_x` | `int` | `None`   | 相对元素左上角坐标的 x 轴偏移量，向下向右为正              |
| `offset_y` | `int` | `None`   | 相对元素左上角坐标的 y 轴偏移量，向下向右为正              |
| `button`   | `str` | `'left'` | 要点击的键，传入`'left'`、`'right'`或`'middle'` |

**返回：**`None`

**示例：**

```python
# 点击元素右上方 50*50 的位置
ele.click_at(50, -50)

# 点击元素上中部，x 相对左上角向右偏移50，y 保持在元素中点
ele.click_at(offset_x=50)

# 和 click() 相似，但没有重试功能
ele.click_at()
```

---

## 📍 `r_click()`

此方法实现右键单击元素。

**参数：** 无

**返回：**`None`

**示例：**

```python
ele.r_click()
```

---

## 📍 `r_click_at()`

此方法用于带偏移量右键点击元素，用法和`click_at()`相似。

| 参数名称       | 类型    | 默认值    | 说明                       |
|:----------:|:-----:|:------:| ------------------------ |
| `offset_x` | `int` | `None` | 相对元素左上角坐标的 x 轴偏移量，向下向右为正 |
| `offset_y` | `int` | `None` | 相对元素左上角坐标的 y 轴偏移量，向下向右为正 |

**返回：**`None`

**示例：**

```python
# 点击距离元素左上角 50*50 的位置（位于元素内部）
ele.r_click_at(50, 50)  
```

---

## 📍 `m_click()`

此方法实现中键单击元素。

**参数：** 无

**返回：**`None`

**示例：**

```python
ele.m_click()
```

---

# ✔️ 输入内容

## 📍 `clear()`

此方法用于清空元素文本，可选择模拟按键或 js 方式。

模拟按键方式会自动输入`ctrl-a-del`组合键来清除文本框，js 方式则直接把元素`value`属性设置为`''`。

| 参数名称    | 类型     | 默认值     | 说明          |
|:-------:|:------:|:-------:| ----------- |
| `by_js` | `bool` | `False` | 是否用 js 方式清空 |

**返回：**`None`

**示例：**

```python
ele.clear() 
```

---

## 📍 `input()`

此方法用于向元素输入文本或组合键，也可用于输入文件路径到上传控件。可选择输入前是否清空元素。

| 参数名称    | 类型     | 默认值     | 说明                                 |
|:-------:|:------:|:-------:| ---------------------------------- |
| `vals`  | `Any`  | `False` | 文本值或按键组合<br>对文件上传控件时输入路径字符串或其组成的列表 |
| `clear` | `bool` | `True`  | 输入前是否清空文本框                         |

**返回：**`None`

?>**Tips:** <br>- 有些文本框可以接收回车代替点击按钮，可以直接在文本末尾加上`'\n'`。<br>- 会自动把非`str`数据转换为`str`。

**示例：**

```python
# 输入文本
ele.input('Hello world!')

# 输入文本并回车
ele.input('Hello world!\n')
```

---

## 📍 输入组合键

使用组合键或要传入特殊按键前，先要导入按键类`Keys`。

```python
from DrissionPage import Keys
```

然后将组合键放在一个`tuple`中传入`input()`即可。

```python
ele.input((Keys.CTRL, 'a', Keys.DEL))  # ctrl+a+del
```

---

## 📍 上传文件

上传文件是用`input()`对`type`属性为`'file'`的`<input>`元素进行输入，把文件路径输入到元素即可，用法与输入文本一致。

稍有不同的是，无论`clear`参数是什么，都会清空原控件内容。

多文件上传控件，多个路径以`list`、`tuple`或以`\n`分隔的字符串传入。

```python
# 传入一个路径
ele.input('D:\\test1.txt')

# 传入多个路径，方式 1
paths = 'D:\\test1.txt\nD:\\test2.txt'
ele.input(paths)

# 传入多个路径，方式 2
paths = ['D:\\test1.txt', 'D:\\test2.txt']
ele.input(paths)
```

---

# ✔️ 拖拽和悬停

?>**Tips:** <br>除了以下方法，本库还提供更灵活的动作链`ActionChains`功能，详见后面章节。

## 📍 `drag()`

此方法用于拖拽元素到相对于当前的一个新位置，可以设置速度，可以选择是否随机抖动。

| 参数名称       | 类型     | 默认值    | 说明               |
|:----------:|:------:|:------:| ---------------- |
| `offset_x` | `int`  | `0`    | x 轴偏移量，向下向右为正    |
| `offset_y` | `int`  | `0`    | y 轴偏移量，向下向右为正    |
| `speed`    | `int`  | `40`   | 拖动的速度，传入 0 即瞬间到达 |
| `shake`    | `bool` | `True` | 是否随机抖动           |

**返回：**`None`

**示例：**

```python
# 拖动当前元素到距离 50*50 的位置，速度为 100，不随机抖动
ele.drag(50, 50, 100, False)
```

---

## 📍 `drag_to()`

此方法用于拖拽元素到另一个元素上或一个坐标上。

| 参数名称         | 类型                                     | 默认值    | 说明               |
|:------------:|:--------------------------------------:|:------:| ---------------- |
| `ele_or_loc` | `ChromiumElement`<br>`Tuple[int, int]` | 必填     | 另一个元素对象或坐标元组     |
| `speed`      | `int`                                  | `40`   | 拖动的速度，传入 0 即瞬间到达 |
| `shake`      | `bool`                                 | `True` | 是否随机抖动           |

**返回：**`None`

**示例：**

```python
# 把 ele1 拖拽到 ele2 上
ele1 = page.ele('#div1')
ele2 = page.ele('#div2')
ele1.drag_to(ele2)

# 把 ele1 拖拽到网页 50, 50 的位置
ele1.drag_to((50, 50))
```

---

## 📍 `hover()`

此方法用于模拟鼠标悬停在元素上，可接受偏移量，偏移量相对于元素左上角坐标。不传入`offset_x`和`offset_y`值时悬停在元素中点。

| 参数名称       | 类型    | 默认值    | 说明                       |
|:----------:|:-----:|:------:| ------------------------ |
| `offset_x` | `int` | `None` | 相对元素左上角坐标的 x 轴偏移量，向下向右为正 |
| `offset_y` | `int` | `None` | 相对元素左上角坐标的 y 轴偏移量，向下向右为正 |

**返回：**`None`

**示例：**

```python
# 悬停在元素右上方 50*50 的位置
ele.hover(50, -50)

# 悬停在元素上中部，x 相对左上角向右偏移50，y 保持在元素中点
ele.hover(offset_x=50)

# 悬停在元素中点
ele.hover()
```

---

# ✔️ 修改元素

## 📍 `set_innerHTML()`

此方法用于设置元素的 innerHTML 内容。

| 参数名称   | 类型    | 默认值 | 说明     |
|:------:|:-----:|:---:| ------ |
| `html` | `str` | 必填  | html文本 |

**返回：**`None`

---

## 📍 `set_prop()`

此方法用于设置元素`property`属性。

| 参数名称    | 类型    | 默认值 | 说明  |
|:-------:|:-----:|:---:| --- |
| `prop`  | `str` | 必填  | 属性名 |
| `value` | `str` | 必填  | 属性值 |

**返回：**`None`

**示例：**

```python
ele.set_prop('value', 'Hello world!')
```

---

## 📍 `set_attr()`

此方法用于设置元素`attribute`属性。

| 参数名称    | 类型    | 默认值 | 说明  |
|:-------:|:-----:|:---:| --- |
| `attr`  | `str` | 必填  | 属性名 |
| `value` | `str` | 必填  | 属性值 |

**返回：**`None`

**示例：**

```python
ele.set_attr('href', 'http://www.gitee.com')
```

---

## 📍 `remove_attr()`

此方法用于删除元素`attribute`属性。

| 参数名称   | 类型    | 默认值 | 说明  |
|:------:|:-----:|:---:| --- |
| `attr` | `str` | 必填  | 属性名 |

**返回：**`None`

**示例：**

```python
ele.remove_attr('href')
```

---

# ✔️ 执行 js 脚本

## 📍 `run_js()`

此方法用于对元素执行 js 代码，代码中用`this`表示元素自己。

| 参数名称      | 类型     | 默认值     | 说明                                              |
|:---------:|:------:|:-------:| ----------------------------------------------- |
| `script`  | `str`  | 必填      | js 脚本文本                                         |
| `as_expr` | `bool` | `False` | 是否作为表达式运行，为`True`时`args`参数无效                    |
| `*args`   | -      | 无       | 传入的参数，按顺序在js文本中对应`argument[0]`、`argument[1]`... |

| 返回类型  | 说明     |
|:-----:| ------ |
| `Any` | 脚本执行结果 |

!>**注意：**<br>要获取 js 结果记得写上`return`。

**示例：**

```python
# 用执行 js 的方式点击元素
ele.run_js('this.click();')

# 用 js 获取元素高度
height = ele.run_js('return this.offsetHeight;')
```

---

## 📍 `run_async_script()`

此方法用于以异步方式执行 js 代码，代码中用`this`表示元素自己。

| 参数名称      | 类型     | 默认值     | 说明                                              |
|:---------:|:------:|:-------:| ----------------------------------------------- |
| `script`  | `str`  | 必填      | js 脚本文本                                         |
| `as_expr` | `bool` | `False` | 是否作为表达式运行，为`True`时`args`参数无效                    |
| `*args`   | -      | 无       | 传入的参数，按顺序在js文本中对应`argument[0]`、`argument[1]`... |

**返回：**`None`

---

# ✔️ 元素滚动

## 📍 `scroll`

此属性用于以某种方式滚动元素中的滚动条。  
调用此属性返回一个`ChromiumScroll`对象，调用该对象的方法实现各种方式的滚动。

| 方法                  | 参数说明   | 功能               |
|:-------------------:|:------:|:----------------:|
| `to_top()`          | 无      | 滚动到顶端，水平位置不变     |
| `to_bottom()`       | 无      | 滚动到底端，水平位置不变     |
| `to_half()`         | 无      | 滚动到垂直中间位置，水平位置不变 |
| `to_rightmost()`    | 无      | 滚动到最右边，垂直位置不变    |
| `to_leftmost()`     | 无      | 滚动到最左边，垂直位置不变    |
| `to_location(x, y)` | 滚动条坐标值 | 滚动到指定位置          |
| `up(pixel)`         | 滚动的像素  | 向上滚动若干像素，水平位置不变  |
| `down(pixel)`       | 滚动的像素  | 向下滚动若干像素，水平位置不变  |
| `right(pixel)`      | 滚动的像素  | 向左滚动若干像素，垂直位置不变  |
| `left(pixel)`       | 滚动的像素  | 向右滚动若干像素，垂直位置不变  |

```python
# 滚动到底部
ele.scroll.to_bottom()

# 滚动到最右边
ele.scroll.to_rightmost()

# 向下滚动 200 像素
ele.scroll.down(200)

# 滚动到指定位置
ele.scroll.to_location(100, 300)
```

---

# ✔️ 列表选择

## 📍 `select`

此属性用于对`<select>`元素的操作。非`<select>`元素此属性为`None`。

调用此属性时返回一个`ChromiumSelect`对象，调用该对象的方法实现列表项的选中与取消。

假设有以下`<select>`元素，下面示例以此为基础：

```html
<select id='s' multiple>
    <option value='value1'>text1</option>
    <option value='value2'>text2</option>
    <option value='value3'>text3</option>
</select>
```

该对象实现了`__call__()`方法，可直接调用进行按文本选择项目。

```python
ele = page.ele('#s')

ele.select('text1')  # 选中文本为 'text1' 的项目
```

---

## 📍 对象方法

| 方法                                | 参数说明    | 功能             |
|:---------------------------------:|:-------:|:--------------:|
| `by_text(text, timeout)`          | 文本，超时时间 | 根据文本选择项        |
| `by_value(value, timeout)`        | 项值，超时时间 | 根据值选择项         |
| `by_index(index, timeout)`        | 序号，超时时间 | 根据序号选择项（0开始）   |
| `cancel_by_text(text, timeout)`   | 文本，超时时间 | 根据文本取消选择（多选列表） |
| `cancel_by_value(value, timeout)` | 项值，超时时间 | 根据项值取消选择（多选列表） |
| `cancel_by_index(index, timeout)` | 序号，超时时间 | 根据序号取消选择（多选列表） |
| `invert()`                        | 无       | 反选（多选列表）       |
| `clear()`                         | 无       | 清空列表（多选列表）     |

**示例：**

```python
ele.select.by_text('text1')  # 和 ele.select('text1') 一样
ele.select.by_value('value2')  # 选中 value 属性为 'value2' 的项
ele.select.by_index(2)  # 选中第 3 项

ele.select.cancel_by_text('text1')  # 取消选中文本为 'text1' 的项
ele.select.cancel_by_value('value2')  # 取消选中 value 属性为 'value2' 的项
ele.select.cancel_by_index(2)  # 取消选中第 3 项

ele.invert()  # 反选
ele.clear()  # 清空
```

---

## 📍 `ChromiumSelect`对象属性

| 属性                 | 类型                      | 说明                        |
|:------------------:|:-----------------------:| ------------------------- |
| `is_multi`         | `bool`                  | 返回是否多选表单                  |
| `options`          | `List[ChromiumElement]` | 返回所有选项元素组成的列表             |
| `selected_option`  | `ChromiumElement`       | 返回第一个被选中的`<option>`元素     |
| `selected_options` | `List[ChromiumElement]` | 返回所有被选中的`<option>`元素组成的列表 |

**示例：**

```python
print(ele.select.is_multi)
```

**输出：**

```console
True
```

---

## 📍 多选

上述各种选择/取消选择的方法均支持多选下拉列表。

要选择/取消选择多项，只要传入相应内容组成的`tuple`或`list`即可。

```python
# 选择多个文本项
ele.select(('text1', 'text2'))

# 选择多个值
ele.select.by_value(('value1', 'value2'))

# 取消选择多个序号
ele.select.cancel_by_index((0, 2))
```

---

## 📍 等待

很多网站下拉列表采用 js 加载，如果加载不及时会导致异常。

因此本库在此集成了一个贴心小功能，上面各种方法均设置了`timeout`参数，如果选择目标未找到，会在限时内等待该项出现，超时就返回`False`。

```python
# 目标选择 'abc'，设置超时时间为 3 秒
print(ele.select('abc', 3))
```

**输出：**

```console
False
```