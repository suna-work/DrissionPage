此示例演示如何使用多个线程同时控制一个浏览器的多个标签页进行采集。

# ✔️ 页面分析

目标网址：

- https://gitee.com/explore/ai

- https://gitee.com/explore/machine-learning

按`F12`，可以看到每个标题元素的`class`属性均为`title project-namespace-path`，可批量获取。

---

# ✔️ 编码思路

虽然 gitee 开源项目列表可以用 s 模式采集，但现在为了演示多标签页操作，还是使用浏览器进行操作。

使用`ChromiumPage`的`get_loc()`方法，分别获取两个标签页的对象，传入不同线程进行操作。

---

# ✔️ 示例代码

以下代码可直接运行。

须要注意的是，这里用到记录器对象，详见[DataRecorder](http://g1879.gitee.io/datarecorder)。

```python
from threading import Thread

from DrissionPage import ChromiumPage
from DataRecorder import Recorder


def collect(tab, recorder, title):
    """用于采集的方法
    :param tab: ChromiumTab 对象
    :param recorder: Recorder 记录器对象
    :param title: 类别标题
    :return: None
    """
    num = 1  # 当前采集页数
    while True:
        # 遍历所有标题元素
        for i in tab.eles('.title project-namespace-path'):
            # 获取某页所有库名称，记录到记录器
            recorder.add_data((title, i.text, num))

        # 如果有下一页，点击翻页
        if btn := tab('@rel=next', timeout=2):
            btn.click(wait_loading=True)
            num += 1

        # 否则，采集完毕
        else:
            break


def main():
    # 新建页面对象
    page = ChromiumPage()
    # 第一个标签页访问网址
    page.get('https://gitee.com/explore/ai')
    # 获取第一个标签页对象
    tab1 = page.get_tab()
    # 新建一个标签页并访问另一个网址
    page.new_tab('https://gitee.com/explore/machine-learning')
    # 获取第二个标签页对象
    tab2 = page.get_tab()

    # 新建记录器对象
    recorder = Recorder('data.csv')

    # 多线程同时处理多个页面
    Thread(target=collect, args=(tab1, recorder, 'ai')).start()
    Thread(target=collect, args=(tab2, recorder, '机器学习')).start()


if __name__ == '__main__':
    main()
```

---

# ✔️ 结果

程序生成一个结果文件 data.csv，内容如下：

```csv
机器学习,MindSpore/mindspore,1
机器学习,PaddlePaddle/Paddle,1
机器学习,MindSpore/docs,1
机器学习,scruel/Notes-ML-AndrewNg,1
机器学习,MindSpore/graphengine,1
机器学习,inspur-inna/inna1.0,1
ai,drinkjava2/人工生命,1
机器学习,MindSpore/course,1

后面省略。。。
```