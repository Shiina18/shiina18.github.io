---
title: "建站记录"
categories: Miscellanea
updated:
comments: true
mathjax: false
---

## 当前状况

在 Jekyll 版本的 [NexT](https://github.com/simpleyyt/jekyll-theme-next) 主题上做了若干修改. 目前初步搬运完成, 还需要进一步 debug.

线下使用 [VNote](https://vnote.readthedocs.io/zh_CN/latest/) 写作, 目前发现的和线上 md 的区别:

- 链接 `[discription](url)` 描述中如果有 `|` 的话线上会编译成 table, 需要转义.
- 线上公式中的 `\{` 需要转义写为 `\\{`.
- 当前线上的 mathjax display math 必须要用 `$$` 包住, 而不能直接 `\begin`.
- 线上图片 `[caption](url)` 部分如果需要 caption 的话, `url` 部分需要写为 `url "caption"`, caption 部分不能为空.
- 图片地址需要替换为可用的链接.
- 线上不支持 `[TOC]`, 不过有侧边栏倒是无所谓.

写了一个 [简陋的 Python 脚本](https://github.com/Shiina18/shiina18.github.io/blob/master/assets/codes/github_blog_transformer.py) 自动处理线下线上的 gap. 另外, 主题自带的 categories 页面不好看, 也一并集成在脚本中了. 功能并不完善, 是按照个人 md 写作习惯写的.

<!-- more -->

另外在修改样式的时候, [Agent Ransack](https://www.mythicsoft.com/agentransack/) 的全文搜索功能非常有帮助.

### 其他已经发现的 bug

- 长 code block 在手机端会被截断, 只能显示前 66 行.

### 其他想修正的点

- Modified date 为空时, 去掉对应的图标.
- 去掉侧边栏的展开动画.
- layout 为 page 时的 ol, ul, li 的 left margin 缩小.
- 段落间距修正.
- header 的上下间距修正.
- 点开 post 之后标题和正文之间的间距修正.
- 点击 read more 之后自动跳转到 read more 位置.

## 过往博客

[Wordpress.com](https://shiina1418.wordpress.com/) -> Github Page -> [Blogger](https://randomwalk034.blogspot.com/) -> Github Page

WP 和 blogger 倒是都找到了好看的主题. 

一点小发现是很多网站比如豆瓣 ([豆瓣收藏秀](https://www.douban.com/service/badgemaker)), goodreads ([new widget for your blog](https://www.goodreads.com/blog/show/42-new-widget-for-your-blog)) 等会提供一个 JavaScript widget 作为博客插件, 相关讨论帖大多是十多年前的, 非常有年代感, 也间接反映了博客的没落...

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