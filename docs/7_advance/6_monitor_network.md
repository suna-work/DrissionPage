许多网页的数据来自接口，在网站使用过程中动态加载，如使用 JS 加载内容的翻页列表。

这些数据通常以 json 形式发送，浏览器接收后，对其进行解析，再加载到 DOM 相应位置。

做数据采集的时候，我们往往从 DOM 中去获取解析后数据的，可能存在 数据不全、加载响应不及时、难以判断加载完成等问题。

因此开发了一个监听器，专门用于抓取 Chromium 内核浏览器数据包。

由于该工具不依赖 DrissionPage，现已独立发布为一个库，但仍然可以在 DrissionPage 中导入。

!> 为了便于维护，该工具用法请移步 [FlowViewer](https://gitee.com/g1879/FlowViewer) 查看。

# ✔️ 简单示例

```python
from DrissionPage.tools import Listener

listener =Listener(9222)  # 创建监听器，监听9222端口的浏览器
listener.set_targets('JobSearchResult.aspx')  # 设置需要监听的url

listener.listen(count=10)  # 开始监听，接收到10条目标url的请求后停止

for i in listener.steps():
    print(i.body)  # 打印实时打印监听到的内容

listener.stop()  #停止监听
```