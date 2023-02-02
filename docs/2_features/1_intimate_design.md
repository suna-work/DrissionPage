这里介绍一些本库内置了人性化设计。

# ✔️ 无处不在的等待

网络环境不稳定，很多时候程序须要稍微等待一下才能继续运行。等待太少，会导致程序出错，等待太多，又会浪费时间。为了解决这些问题，本库在大量须要等待的部分内置了超时功能，并且可以随时灵活设置，大幅降低程序复杂性。

- 查找元素内置等待。可以为每次查找元素单独设定等待时间。有些页面会不定期出现提示信息，如果一律等待会太浪费时间，可以独立设置一个很短的超时时间，避免浪费。

- 等待下拉列表选项。很多下拉列表使用 js 加载，本库选择下拉列表时，会自动等待列表项出现。

- 等待弹窗。有时预期的 alert 未必立刻出现，本库处理 弹窗消息时也可以设置等待。

- 等待元素状态改变。使用`wait_ele()`方法可等待元素出现、消失、删除等状态。

- 点击功能也内置等待，如遇元素被遮挡可不断重试点击。

- 设置页面加载时限及加载策略。有时不需要完整加载页面资源，可根据实际须要设置加载策略。

--- 

# ✔️ 自动重试连接

在访问网站时，由于网络不稳定可能导致连接异常。本库设置了连接自动重试功能，当网页连接异常，会默认重试 3 次。当然也可以手动设置次数和间隔。

```python
page.get('xxxxxx', retry=5, interval=3)  # 出错是重试 5 次，每次间隔 3 秒
```

---

# ✔️ 极简的定位语法

本库制定了一套简洁高效的查找元素语法，支持链式操作，支持相对定位。与 selenium 繁琐的语法相比简直不要太方便。

而且每次查找内置等待，可以独立设置每次查找超时时间。

同是设置了超时等待的查找，对比一下：

```python
# 使用 selenium：
element = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, '//*[contains(text(), "some text")]')))

# 使用 DrissionPage：
element = page('some text', timeout=10)
```

---

# ✔️ 无需切入切出，逻辑清晰

使用过 selenium 的人都知道，selenium 同一时间只能操作一个标签页或`<iframe>`元素，要操作其它标签页，或`<iframe>`元素，须要用`switch_to()`
方法切换，操作后还要切换回来。如果是多级`<iframe>`，还要逐级切入，相当麻烦。

DrissionPage 则无需这些麻烦的操作，它把每个标签页和`<iframe>`都看作独立的对象，可以同时并发操作，而且可以直接跨多层`<iframe>`获取里面的元素，然后直接处理，非常方便。

对比一下，获取 2 层`<iframe>`内一个 id 为`'div1'`的元素：

```python
# 使用 selenium
driver.switch_to.frame(0)
driver.switch_to.frame(0)
ele = driver.find_element(By.ID, 'div1')
driver.switch_to.default_content()

# 使用 DrissionPage
ele = page('#div1')
```

多标签页同时操作，selenium 无此功能：

```python
tab1 = page.get_tab(page.tabs[0])
tab2 = page.get_tab(page.tabs[1])

tab1.get('https://www.baidu.com')
tab2.get('https://www.163.com')
```

---

# ✔️ 高度集成的便利功能

很多操作方法集成了常用功能，如`chick()`中内置`by_js`参数，可以直接改用 js 方式点击，而无需写独立的 js 语句。

---

# ✔️ 强大的下载功能

DrissionPage 内置一个下载工具，可实现大文件分块多线程下载文件。并且可以直接读取缓存数据保存图片，而无需控制页面作另存操作。

```python
img = page('tag:img')
img.save('img.png')  # 直接保存图片到文件夹
```

---

# ✔️ 更多便捷的功能

- 可对整个网页截图，包括视口外的部分

- 每次运行程序可以反复使用已经打开的浏览器，无需每次从头运行

- s 模式访问网页时会自动纠正编码，无须手动设置

- s 模式在连接时会自动根据当前域名自动填写`Host`和`Referer`属性

- 下载工具支持多种方式处理文件名冲突、自动创建目标路径、断链重试等

- `MixPage`可自动下载合适版本的 chromedriver，免去麻烦的配置

- 支持直接获取`after`和`before`伪元素的内容