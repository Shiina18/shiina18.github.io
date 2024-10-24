---
title: "建站记录"
categories: Miscellanea
updated: 2022-01-13
comments: true
mathjax: false
---

## 当前状况

在 Jekyll 版本的 [NexT](https://github.com/simpleyyt/jekyll-theme-next) 主题上做了若干修改. 目前初步搬运完成, 还需要进一步 debug.

线下使用 [VNote](https://vnote.readthedocs.io/zh_CN/latest/) 写作, 目前发现的和线上 md 的区别:

- 链接 `[discription](url)` 描述中如果有 `|` 的话线上会编译成 table, 需要转义.
<!-- more -->
- 线上公式中的 `\{` 需要转义写为 `\\{`.
- 当前线上的 mathjax display math 必须要用 `$$` 包住, 而不能直接 `\begin`.
- 线上图片 `[caption](url)` 部分如果需要 caption 的话, `url` 部分需要写为 `url "caption"`, caption 部分不能为空.
- 图片地址需要替换为可用的链接.
- 线上不支持 `[TOC]`, 不过有侧边栏倒是无所谓.
- 数学模式中的一对 `|`会被编译成表格, 得写成 `\vert`. (2020/8/9)
- 数学模式中, 如果两个 `_` 之间没有空格, 则会被编译为斜体, 只要手动在 `_` 前加上空格即可. (2021/11/29)
- 关于暴露 client_secret 的问题, 参考这个 [issue](https://github.com/gitalk/gitalk/issues/150), 没有问题. (2020/12/19)
- 关于网站 size limit, 参考 [这里](https://docs.github.com/en/free-pro-team@latest/github/working-with-github-pages/about-github-pages). 限制是 1GB, 带宽每月 100GB. 目前看来几年之内还不需要太节约空间, 另外如果把现在用的图片压缩一遍 (比如有每日限额的 [这里](https://compressor.io/) 和每日无限的 [这里](https://kraken.io/web-interface)), 大概可以扩容一倍; 另外另开一个 repo 专门存图也可以. (2020/12/24)
    - 另外, 缩小图片尺寸可以显著减小图片 (比如用 [这个工具](https://www.iloveimg.com/resize-image)). (2021/2/21)
    - 发现了解决图片压缩和 resize 的免费软件 [RIOT](https://riot-optimizer.com/). (2021/8/22)
- [gitalk 403 问题](https://cuiqingcai.com/30010.html), 解决办法是在 `gitalk.html` 里新建一个属性 proxy, 再在 `_config.yml` 中填入可用的 proxy. (2021/2/18)
- gitalk 时不时会无法登录而跳转到主页, 也不是网上其他人的情况. 解决办法是换浏览器或者点击不同文章下面的登录按钮.

写了一个 [简陋的 Python 脚本](https://github.com/Shiina18/shiina18.github.io/blob/master/assets/code/post_adapter) 自动处理线下线上的 gap. 另外, 主题自带的 categories 页面不好看, 也一并集成在脚本中了. 功能并不完善, 是按照个人 md 写作习惯写的. 2022 年重构了代码.

另外在修改样式的时候, [Agent Ransack](https://www.mythicsoft.com/agentransack/) 的全文搜索功能非常有帮助.

### 一些 HTML 用法

2020/8/17

- 嵌入视频. B 站嵌入视频上下有约 120 px 的填充物, 宽高比大约 1.8, 宽度似乎要接近 500px 才会有进度条, 宽 500 高 400 刚好. 我不知道怎么让嵌入视频自动适应移动端大小, 只能暂时献祭移动端了. (现在放弃了, 线下编辑加载太慢了)
- 嵌入音乐. 网易云有提供外链生成 iframe 插件. 
- 嵌入其他网页. 推特, ins 都有提供插件. 
- 在 TeX 用 `align` 和 `label`, 再通过 id 属性页内跳转到编号公式.
- 下拉栏, 参考 [这里](https://github.com/snorkel-team/snorkel/blob/master/README.md) (2022/1/13)

<details><summary><b>Details on installing with <tt>conda</tt></b><font color="deepskyblue"> (Show more &raquo;)</font></summary>
<p>The following example commands give some more color on installing with <code>conda</code>. These commands assume that your <code>conda</code> installation is Python 3.6, and that you want to use a virtual environment called <code>snorkel-env</code>.</p>
<pre><code class="language-shell"># [OPTIONAL] Activate a virtual environment called &quot;snorkel&quot;
conda create --yes -n snorkel-env python=3.6
conda activate snorkel-env

# We specify PyTorch here to ensure compatibility, but it may not be necessary.
conda install pytorch==1.1.0 -c pytorch
conda install snorkel==0.9.0 -c conda-forge
</code></pre>
<pre><code class="language-python">print('test')
</code></pre></details>

<a name="模型简介"></a>

- <mark>Marked text</mark>
- <span style="background-color: #FFFF00">Marked text</span>
- <mark style="background-color: lightblue">Marked text</mark>
- 不确定
    - <kbd>keyboard</kbd>
    - This is a [hover text](## "your hover text") example.
    - <abbr title="Open Neural Network EXchange">ONNX</abbr>

手动加 anchor, [跳转](#模型简介)

```diff
+ import numpy as np
- import pandas as pd
```

### 其他已经发现的 bug

- 长 code block 在手机端会被截断, 只能显示前 66 行, 和 [这个](https://www.sidmartinbio.org/how-many-lines-is-a-standard-sheet-of-paper/) 巧合?
- 一行中有多个 inline math, 里面有 `_` 的场合, 依然会被编译成斜体, 在 `_` 两边加空格可以解决. (2020/9/23)

### 其他想修正的点

- Modified date 为空时, 去掉对应的图标.
- 去掉侧边栏的展开动画.
- layout 为 page 时的 ol, ul, li 的 left margin 缩小.
- 段落间距修正.
- header 的上下间距修正.
- 点开 post 之后标题和正文之间的间距修正.
- 点击 read more 之后自动跳转到 read more 位置. (不起作用的原因是 page 里没有相应的 id)

## 过往博客

[Wordpress.com](https://shiina1418.wordpress.com/) -> Github Page -> [Blogger](https://randomwalk034.blogspot.com/) -> Github Page

<details><summary><b>WP 和 blogger 倒是都找到了好看的主题.</b><font color="deepskyblue"> (Show more &raquo;)</font></summary>
<p><img alt="WordPress" src="https://shiina18.github.io/assets/posts/images/20200817232911683_26586.png" /></p>
<p><img alt="Blogger" src="https://shiina18.github.io/assets/posts/images/20200817232813332_31551.png" /></p>
<p>一点小发现是很多网站比如豆瓣 (<a href="https://www.douban.com/service/badgemaker">豆瓣收藏秀</a>), goodreads (<a href="https://www.goodreads.com/blog/show/42-new-widget-for-your-blog">new widget for your blog</a>) 等会提供一个 JavaScript widget 作为博客插件, 相关讨论帖大多是十多年前的, 非常有年代感, 也间接反映了博客的没落...</p></details>

### 考虑过/使用过的平台

- 简书
    - TeX 太丑了
    - 链接要额外跳转一次
    - SEO 还行
- 博客园
    - 我不写技术博客, 和博客园宗旨不符合
    - TeX 好看, 代码块不好看
    - SEO 很好
- CSDN
    - 看起来就远不如博客园
- Wordpress.com
    - 免费版有广告, 体验太差
- Blogger
    - 最主要问题是被墙了
- Github Page
    - 最初使用过极简的 [Renge](https://github.com/billyfish152/Renge) 主题, 为了修改 pick up 了一点点 HTML 语法知识. 但是很多地方不合心意又修改不来就放弃了.
    - 最大的好处是只要 commit push 就行了, 其他网站需要手动复制粘贴, 修改起来麻烦.

### 使用过的编辑器

- 作业部落
    - TeX 支持很好
    - 文件管理系统不太喜欢
    - 感到 VNote 预览不方便的时候会用它
- StackEdit
    - md, TeX 的语法高亮漂亮
    - 不支持 align 环境 (改名为 aligned 环境)
- VNote
    - 不能左边编辑右边看渲染有点不方便
    - 自带全局搜索很棒
    - 其他都很完美
- Typora
    - 编辑模式反 md 宗旨, 很别扭
    - 没有文件管理系统
    - 默认样式好看, 一般写好后导出时用它
- Notion
    - 花里胡哨的富文本, 可多人协作编辑, 可以用来做上述 markdown 不能做到的事情
    - 可定制性差
    - 编辑不方便
    - 用了我很讨厌的 block 机制