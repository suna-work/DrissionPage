# v3.1.3

- `ChromiumPage`添加`latest_tab`属性

- `WebPage`初始化删除`tab_id`参数

- 修复页面未加载完可能获取到空元素的问题

- 修复新标签页重定向时获取文档不正确问题

- 增强稳定性

# v3.1.1

- 增强下载功能

    - `ChromiumPage`也可以使用内置下载器下载文件

    - 可拦截并接管浏览器下载任务

    - 新增`download_set`属性对下载参数进行设置

    - 增加`wait_download_begin()`方法

- 改进浏览器启动设置

    - 优化 ini 文件结构

    - 新增`ChromiumOptions`取代`DriverOptions`，完全摆脱对 selenium 的依赖

    - 新增自动分配端口功能

    - 优化`SessionOptions`设计，增加一系列设置参数的方法

    - 改进对用户配置文件的设置

- 对部分代码进行重构

    - 优化页面对象启动逻辑

    - 优化配置类逻辑

    - 优化项目结构

- 细节

    - 上传文件时支持传入相对路径

- bug 修复

    - 修复`get_tab()`出错问题

    - 修复新浏览器第一次新建标签页时不正确切换的问题

    - 修复关闭当前标签页出错问题

    - 修复改变浏览器窗口大小出错问题

# v3.0.34

- `WebPage`删除`check_page()`方法

- `DriverOptions`和`easy_set`的`set_paths()`增加`browser_path`参数

- `DriverOptions`增加`browser_path`属性

- `ChromiumFrame`现在支持页面滚动

- 改进滚动到元素功能

- 修改`SessionElement`相对定位参数顺序

- `SessionPage`也可以从 ini 文件读取 timeout 设置

- ini 文件中`session_options`增加`timeout`项

- `SessionOptions`增加`timeout`属性、`set_timeout()`方法

- 优化和修复一些问题

# v3.0.31

- `run_script()`、`run_async_script()`更名为`run_js`和`run_async_js()`
- 返回的坐标数据全部转为`int`类型组成的`tuple`
- 修改注释

# v3.0.30

- 元素增加`m_click()`方法
- 动作链增加`type()`、`m_click()`、`r_hold()`、`r_release()`、`m_hold()`、`m_release()`方法
- 动作链的`on_ele`参数可接收文本定位符
- `WebPage`、`SessionPage`、`ChromiumPage`增加`set_headers()`方法

# v3.0.28

- 各种大小、位置信息从`dict`改为用`tuple`返回
- 改进`ChromiumFrame`
- 修复小窗时定位不准问题，修复 iframe 内元素无法获取 s_ele() 问题
- 增加`wait_loading`方法和参数
- 其它优化和问题修复

# v3.0.22

- `change_mode()`增加`copy_cookies`参数
- 调整`WebPage`生成的元素对象的`prev()`、`next()`、`before()`、`after()`参数顺序
- 修复读取页面时小概率失效问题
- 用存根文件取代类型注解

# v3.0.20

重大更新。推出`WebPage`，重新开发底层逻辑，摆脱对 selenium 的依赖，增强了功能，提升了运行效率。支持 chromium 内核的浏览器（如 chrome 和 edge）。比`MixPage`有以下优点：

- 无 webdriver 特征，不会被网站识别
- 无需为不同版本的浏览器下载不同的驱动
- 运行速度更快
- 可以跨 iframe 查找元素，无需切入切出
- 把 iframe 看作普通元素，获取后可直接在其中查找元素，逻辑更清晰
- 可以同时操作浏览器中的多个标签页，即使标签页为非激活状态
- 可以直接读取浏览器缓存来保持图片，无需用 GUI 点击保存
- 可以对整个网页截图，包括视口外的部分（90以上版本浏览器支持）

其它更新：

- 增加`ChromiumTab`和`ChromiumFrame`类用于处理 tab 和 frame 元素
- 新增与`WebPage`配合的动作链接`ActionChains`
- ini 文件和`DriverOption`删除`set_window_rect`属性
- 浏览器启动配置实现对插件的支持
- 浏览器启动配置实现对`experimental_options`的`prefs`属性支持

# v2.7.3

- 页面对象和元素对象的`screenshot_as_bytes()`方法合并到`screenshot()`
- `input()`方法接收非文本参数时自动转成文本输入

# v2.7.2

- d 模式页面和元素对象增加`screenshot_as_bytes()`方法

# v2.7.1

- DriverPage
    - 增加`get_session_storage()`、`get_local_storage()`、`set_session_storage()`、`set_local_storage()`、`clean_cache()`方法
    - `run_cdp()`的`cmd_args`参数改为`**cmd_args`
- 关闭 driver 时会主动关闭 chromedriver.exe 的进程
- 优化关闭浏览器进程逻辑

# v2.6.2

- d 模式增加`stop_loading()`方法
- 优化完善监听器功能

# v2.6.0

- 新增`Listener`类
    - 可监听浏览器数据包
    - 可异步监听
    - 可实现每监听到若干数据包执行操作
- 放弃对selenium4.1以下的支持
- 解决使用新版浏览器时出现的一些问题

# v2.5.9

- 优化 s 模式创建连接的逻辑

# v2.5.7

- 列表元素`select()`、`deselect()`等方法添加`timeout`参数，可等待列表元素加载
- 优化了对消息提示框的处理
- `drag()`和`drag_to()`不再检测是否拖拽成功，改成返回`None`
- `DriverOptions`对象从父类继承的方法也支持链式操作
- 其它优化和问题修复

# v2.5.5

- `DriverPage`添加`run_cdp()`方法
- `get()`和`post()`方法删除`go_anyway`参数
- 连接重试默认不打印提示

# v2.5.0

- 用 DownloadKit 库替代原来的`download()`方法，支持多线程并发
- `DriverPage`增加`set_ua_to_tab()`方法
- 删除`scroll_to()`方法
- 其它优化和问题修复

# v2.4.3

- `wait_ele()`、`to_frame()`、`scroll_to()`改用类的方式，避免使用字符串方式选择功能
- `scroll_to()`方法改为`scroll`属性
- 滚动页面或元素增加`to_location()`方式
- 优化`Select`类用法

# v2.3.3

- `DriverPage`添加`forward()`方法
- `DriverPage`的`close_current_tab()`改为`close_tabs()`，可一次过关闭多个标签页
- `DriverPage`添加`run_async_script()`
- `DriverPage`添加`timeouts`属性
- `DriverPage`添加`set_timeouts()`方法
- `DriverElement`添加`scroll_to()`方法，可在元素内滑动滚动条
- `DriverOptions`添加`set_page_load_strategy()`方法
- ini 文件增加`page_load_strategy`、`set_window_rect`、`timeouts`三个属性
- 其它优化和问题修复

# v2.2.1

- 新增基于页面布局的相对定位方法`left()`，`right()`，`below()`，`above()`，`near()`，`lefts()`，`rights()`，`belows()`，`aboves()`，`nears()`
- 修改基于 DOM 的相对定位方法：删除`parents()`方法，`parent`属性改为 `parent()`方法，`next`属性 改为`next()`方法，`prev`属性改为`prev()`方法，`nexts()`和`prevs()`
  方法改为返回多个对象
- 增加`after()`，`before()`，`afters()`，`before()`等基于 DOM 的相对定位方法
- 定位语法增加`@@`和`@@-`语法，用于同时匹配多个条件和排除条件
- 改进`ShadowRootElement`功能，现在在 shadow-root 下查找元素可用完全版的定位语法。
- `DriverElement`的`after`和`before`属性改为`pseudo_after`和`pseudo_before`
- `DriverElement`的`input()`增加`timeout`参数
- `DriverElement`的`clear()`增加`insure_clear`参数
- 优化`DriverElement`的`submit()`方法
- `DriverPage`增加`active_ele`属性，获取焦点所在元素
- `DriverPage`的`get_style_property()`改名为`style()`
- `DriverPage`的`hover()`增加偏移量参数
- `DriverPage`的`current_tab_num`改名为`current_tab_index`
- `DriverPage`的`to_frame()`方法返回页面对象自己，便于链式操作
- 优化自动下载 driver 逻辑
- `set_paths()`增加`local_port`参数
- 默认使用`9222`端口启动浏览器
- 其它优化和问题修复

# v2.0.0

- 支持从`DriverElement`或 html 文本生成`SessionElement`，可把 d 模式的页面信息爬取速度提高几个数量级（使用新增的`s_ele()`和`s_eles()`方法）
- 支持随时隐藏和显示浏览器进程窗口（只支持 Windows 系统）
- s 模式和 d 模式使用相同的提取文本逻辑，d 模式提取文本效率大增
- `input()`能自动检测以确保输入成功
- `click()`支持失败后不断重试，可用于确保点击成功及等待页面遮罩层消失
- 对 linux 和 mac 系统路径问题做了修复
- `download()`能更准确地获取文件名
- 其它稳定性和效率上的优化

# v1.11.7

- `SessionOptions`增加`set_headers()`方法
- 调整`MixPage`初始化参数
- `click()`增加`timeout`参数，修改逻辑为在超时时间内不断重试点击。可用于监视遮罩层是否消失
- 处理`process_alert()`增加`timeout`参数
- 其他优化和问题修复

# v1.11.0

- `set_property()`方法改名为`set_prop`
- 增加`prop()`
- `clear()`改用 selenium 原生
- 增加`r_click()`和`r_click_at()`
- `input()`返回`None`
- 增加`input_txt()`

# v1.10.0

- 优化启动浏览器的逻辑
- 用 debug 模式启动时可读取启动参数
- 完善`select`标签处理功能
- `MixPage`类的`to_iframe()`改名为`to_frame()`
- `MixPage`类的`scroll_to()`增加`'half'`方式，滚动半页
- Drission 类增加`kill_browser()`方法

# v1.9.0

- 元素增加`click_at()`方法，支持点击偏移量
- `download()`支持重试
- 元素`input()`允许接收组合键，如`ctrl+a`
- 其它优化

# v1.8.0

- 添加`retry_times`和`retry_interval`属性，可统一指定重连次数
- 元素对象增加`raw_text`属性
- 元素查找字符串支持极简模式，用`x`表示`xpath`、`c`表示`css`、`t`表示`tag`、`tx`表示`text`
- s 模式元素`text`尽量与 d 模式保持一致
- 其它完善和问题修复

# v1.7.7

- 创建`WebDriver`时可自动下载 chromedriver.exe
- 修复获取不到`content-type`时会出现的问题

# v1.7.1

- d 模式如指定了调试端口，可自动启动浏览器进程并接入
- 去除对 cssselect 库依赖
- 提高查找元素效率
- 调整获取元素 xpath 和 css_path 逻辑

# v1.7.0

- 优化`cookies`相关逻辑
- `MixPage`增加`get_cookies()`和`set_cookies()`方法
- 增加`SessionOptions`类
- 浏览文件`DriverElement`增加`remove_attr()`方法
- 修复`MixPage`初始化时`Session`导入`cookies`时的问题
- `MixPage`的`close_other_tabs()`方法现在可以接收列表或元组以保留多个 tab
- 其它优化

# v1.6.1

- 增加`.`和`#`方式用于查找元素，相当于`@Class`和`@id`
- easy_set 增加识别 chrome 版本并自动下载匹配的 chromedriver.exe 功能
- 改进配置功能
- 修复 shadow-root 方面的问题

# v1.5.4

- 优化获取编码的逻辑
- 修复下载不能显示进度的问题

# v1.5.2

- 修复获取 html 时会把元素后面的文本节点带上的问题
- 修复获取编码可能出现的错误
- 优化`download()`和获取编码代码

# v1.5.1

- 修复获取编码可能出现的 bug

# v1.5.0

- s 模式使用 lxml 库代替 requests_html 库
- 可直接调用页面对象和元素对象获取下级元素，`element('@id=ele_id')`等价于`element.ele('@id=ele_id')`
- `nexts()`、`prevs()`方法可获取文本节点
- 可获取伪元素属性及文本
- 元素对象增加`link`和`inner_html`属性
- 各种优化

# v1.4.0

- d 模式使用 js 通过`evaluate()`方法处理 xpath，放弃使用 selenium 原生的方法，以支持用 xpath 直接获取文本节点、元素属性
- d 模式增加支持用 xpath 获取元素文本、属性
- 优化和修复小问题

# v1.3.0

- 可与 selenium 代码无缝对接
- 下载功能支持 post 方式
- 元素添加`texts`属性，返回元素内每个文本节点内容
- s 模式增加支持用 xpath 获取元素文本、属性

# v1.2.1

- 优化修复网页编码逻辑
- `download()`函数优化获取文件名逻辑
- 优化`download()`获取文件大小逻辑
- 优化`MixPage`对象关闭 session 逻辑

# v1.2.0

- 增加对 shadow-root 的支持
- 增加自动重试连接功能
- `MixPage`可直接接收配置
- 修复一些 bug

# v1.1.3

- 连接有关函数增加是否抛出异常参数
- s 模式判断编码优化
- d 模式`check_page()`优化
- 修复`run_script()`遗漏`args`参数的问题

# v1.1.1

- 删除`get_tabs_sum()`和`get_tab_num()`函数，以属性`tabs_count`和`current_tab_num`代替
- 增加`current_tab_handle`、`tab_handles`属性
- `to_tab()`和`close_other_tabs()`函数可接收`handle`值
- `create_tab()`可接收一个 url 在新标签页打开
- 其它优化和 bug 修复

# v1.1.0

- 元素对象增加 xpath 和 css path 路径属性
- 修复 driver 模式下元素对象用 css 方式不能获取直接子元素的问题（selenium 的锅）
- s 模式下现在能通过 xpath 定位上级元素
- 优化 d 模式兄弟元素、父级元素的获取效率
- 优化标签页处理功能
- 其它小优化和修复

# V1.0.5

- 修复切换模式时 url 出错的 bug

# V1.0.3

- `DriverOptions`支持链式操作
- `download()`函数增加参数处理遇到已存在同名文件的情况，可选跳过、覆盖、自动重命名
- `download()`函数重命名调整为只需输入文件名，不带后缀名，输入带后缀名也可自动识别

# V1.0.1

- 增强拖拽功能和 chrome 设置功能

# V0.14.0

- `Drission`类增加代理设置和修改

# V0.12.4

- `click()`的`by_js`可接收`False`
- 修复一些 bug

# V0.12.0

- 增加`tag:tagName@arg=val`查找元素方式
- `MixPage`增加简易方式创建对象方式

# V0.11.0

- 完善`easy_set`的函数
- 元素增加多级定位函数

# v0.10.2

- 完善`attr`及`attrs`功能

# v0.10.1

- 增加`set_headless()`以及`to_iframe()`兼容全部原生参数

# v0.9.4

- 修复 bug

# v0.9.0

- 增加了元素拖拽和处理提示框功能

# v0.8.4

- 基本完成