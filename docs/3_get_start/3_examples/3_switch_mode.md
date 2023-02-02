这个示例演示`WebPage`如何切换控制浏览器和收发数据包两种模式。

通常，切换模式是用来应付登录检查很严格的网站，可以用浏览器处理登录，再转换模式用收发数据包的形式来采集数据。

但是这种场景须要有对应的账号，不便于演示。演示使用浏览器在百度搜索，然后转换到收发数据包的模式来读取数据。虽然现实使用意义不大，但可以了解其工作模式。

# ✔️ 页面分析

网址：[https://www.baidu.com](https://www.baidu.com)

打开网址，按`F12`，我们可以看到页面 html 如下：

![](https://gitee.com/g1879/DrissionPage/raw/master/docs/imgs/baidu_1.jpg)

（图片点击放大）

输入框`<input>`元素`id`属性为`'kw'`，“百度一下”按钮`<input>`元素`id`属性为`'su'`。

输入关键词搜索后，再查看页面 html：

![](https://gitee.com/g1879/DrissionPage/raw/master/docs/imgs/baidu_2.jpg)

（图片点击放大）

通过分析 html 代码，我们可以看出，每个结果的标题都存在于`<h3>`元素里。因此，我们可以获取页面中所有`<h3>`元素，再遍历获取其信息。

---

# ✔️ 示例代码

您可以直接运行以下代码：

```python
from DrissionPage import WebPage

# 创建页面对象
page = WebPage()
# 访问网址
page.get('https://www.baidu.com')
# 查找文本框元素并输入关键词
page('#kw').input('DrissionPage')
# 点击搜索按钮
page('#su').click(wait_loading=True)
# 切换到收发数据包模式
page.change_mode()
# 获取所有<h3>元素
links = page.eles('tag:h3')
# 遍历获取到的元素
for link in links:
    # 打印元素文本
    print(link.text)
```

**输出：**

```console
DrissionPage: 一个整合了selenium和requests_html的模块,...
python采集库DrissionPage- 腾讯云开发者社区-腾讯云
DrissionPage- Web应用开发 - 青少年人工智能资源与创新...
DrissionPage-demos: 使用DrissionPage爬取常见网站的示例。
DrissionPagev1.9.0 已经发布,WEB 自动化测试集成工具_程...
DrissionPage首页、文档和下载 - WEB 自动化测试集成工具 ...
DrissionPage- Gitee
DrissionPage—— Web 自动化测试集成工具 - OSCHINA - ...
DrissionPagev1.10.0 已经发布,WEB 自动化测试集成工具 |...
DrissionPagev2.2.1 发布,WEB 自动化测试集成工具
```

---

# ✔️ 示例详解

我们逐行解读代码：

```python
from DrissionPage import WebPage
```

↑ 首先，我们导入页面对象`WebPage`类。

```python
page = WebPage()
```

↑ 接下来，我们创建一个`WebPage`对象。

```python
page.get('https://www.baidu.com')
```

↑ 然后控制浏览器访问百度。

```python
page('#kw').input('DrissionPage')
page('#su').click(wait_loading=True)
```

↑ 再通过模拟输入的方式输入关键词，模拟点击搜索按钮。

这里查找元素的方法上两个示例已经讲过，不再细说。

`click()`方法里面的`wait_loading`参数用于等待页面进入加载状态，避免操作过快出现异常。

```python
page.change_mode()
```

↑ `change_mode()`方法用于切换工作模式，从当前控制浏览器的模式切换到收发数据包模式。

切换的时候程序会在新模式重新访问当前 url。

```python
links = page.eles('tag:h3')
```

↑ 切换后，我们可以用与控制浏览器一致的语法，获取页面元素，这里`eles()`方法是获取页面中所有`<h3>`元素，它返回这些元素对象组成的列表。`tag:`是查找条件，表示查找某种类型的元素。

```python
for link in links:
    print(link.text)
```

↑ 最后，我们遍历这些元素，并逐个打印它们包含的文本。