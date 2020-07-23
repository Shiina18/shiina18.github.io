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

写了一个简陋的 Python 脚本自动处理线下线上的 gap. 另外, 主题自带的 categories 页面不好看, 也一并集成在脚本中了. 功能并不完善, 是按照个人 md 写作习惯写的.

<!-- more -->

```python
import os
import re
import shutil
import time
s = time.time()

def solve_escape(string, mode='link'):
    # https://stackoverflow.com/questions/6116978/how-to-replace-multiple-substrings-of-a-string
    
    if mode == 'link':
        pattern = '(\[.*?\|.*?\])(\(.*?\))'
        rep = {'|': '\|'}
        
    if mode == 'math':
        pattern = '\$(.*)\$'
        rep = {'\{': r'\\{', '\}': r'\\}'}
        
    new_string = []
    index = 0
    rep = dict((re.escape(k), v) for k, v in rep.items()) 
    sub_pattern = re.compile("|".join(rep.keys()))
    for match in re.finditer(pattern, string):
        new_string.append(string[index:match.start(1)])
        new_string.append(sub_pattern.sub(lambda m: rep[re.escape(m.group(0))], string[match.start(1):match.end(1)]))
        index = match.end(1)
    new_string.append(string[index:])
    return ''.join(new_string)

def solve_display_math(string):
    global flag
    if '$$' in string or string.startswith('```'):
        flag = -flag
        return string
    if string.startswith(r'\begin{align') and flag>0:
        return '$$\n' + string
    if string.startswith(r'\end{align') and flag>0:
        return string + '$$\n'
    return string

def solve_img(string, path='https://shiina18.github.io/assets/posts/'):
    pattern = '!\[(.*?)\]\((.*?)\)'
    new_string = []
    index = 0
    for match in re.finditer(pattern, string):
        new_string.append(string[index:match.start(2)])
        tmp = string[match.start(1):match.end(1)]
        tmp = f' "{tmp}"' if tmp else ''
        new_string.extend([path,
                           string[match.start(2):match.end(2)],
                           tmp])
        index = match.end(2)
    new_string.append(string[index:])
    return ''.join(new_string)

# posts   
                        
source = r'F:\vnote_notebooks\vnotebook\Blogger\Posts'
target = r'F:\GitHub\shiina18.github.io\_posts'

for file in os.listdir(source):
    if file.endswith('.md'):
        with open(os.path.join(source, file), encoding='utf-8') as f:
            with open(os.path.join(target, file), encoding='utf-8', mode='w') as g:
                # solve_display_math
                flag = 1
                for line in f:
                    line = solve_escape(line, 'link')
                    line = solve_escape(line, 'math')
                    line = solve_display_math(line)
                    line = solve_img(line)
                    g.write(line)
                        
# pages

source = r'F:\vnote_notebooks\vnotebook\Blogger'
target = r'F:\GitHub\shiina18.github.io'

for file in os.listdir(source):
    if '.' not in file and file not in {'Posts', '_v_attachments', 'images'}:
        with open(os.path.join(source, file, 'index.md'), encoding='utf-8') as f:
            with open(os.path.join(target, file, 'index.md'), encoding='utf-8', mode='w') as g:
                for line in f:
                    line = solve_escape(line, 'link')
                    line = solve_escape(line, 'math')
                    line = solve_display_math(line)
                    line = solve_img(line)
                    g.write(line)

# images

source = r'F:\vnote_notebooks\vnotebook\Blogger\Posts\images'
target = r'F:\GitHub\shiina18.github.io\assets\posts\images'
for file in os.listdir(source):
    if file.endswith('.jpg') or file.endswith('.png'):
        shutil.copyfile(os.path.join(source, file), os.path.join(target, file))

# sitemap

from collections import defaultdict

class Post():
    def __init__(self, date=None, title=None, cat=None, updated=None, link=None):
        self.date = date
        self.title = title
        self.cat = cat
        self.updated = updated
        self.link = link

source = r'F:\GitHub\shiina18.github.io\_posts'
cated = defaultdict(list)

for post in os.listdir(source):
    date = post[:10]
    link = post[11:-3]
    cur_post = Post(date=date, link=link)
    with open(os.path.join(source, post), encoding='utf-8') as p:
        flag = 0
        for line in p:
            if line.startswith('---'):
                flag += 1
            if flag == 2:
                break
            if flag:
                if line.startswith('title'):
                    cur_post.title = line[6:].strip().strip('"')
                if line.startswith('categories'):
                    cur_post.cat = line[11:].strip().strip('"')
                if line.startswith('updated'):
                    cur_post.updated = line[8:].strip().strip('"')
        cated[cur_post.cat].append((cur_post.date, cur_post.title, cur_post.updated, cur_post.link))

site = 'https://shiina18.github.io'           
target = r'F:\GitHub\shiina18.github.io\sitemap'
with open(os.path.join(target, 'index.md'), encoding='utf-8', mode='w') as g:
    g.write('---\n')
    g.write('title: Sitemap\n')
    g.write('layout: page\n')
    g.write('mathjax: true\n')
    g.write('---\n\n')
    
    g.write(f'\n## Categories\n\n')
    for cat in sorted(cated.keys()):
        url = '/'.join([site, 'category', '#', cat])
        g.write(f'- [{cat}]({url}) <font color="lightgrey">({len(cated[cat])})</font>\n')

    g.write(f'\n## Posts\n\n')   
    for cat in sorted(cated.keys()):
        g.write(f'\n### {cat}\n\n')
        for post in sorted(cated[cat], key=lambda x: x[0], reverse=True):
            date, title, updated, link = post
            y, m, d = date[:4], date[5:7], date[-2:]
            url = '/'.join([site, cat.lower(), y, m, d, link])
            if updated:
                g.write(f'- {date} [{title}]({url}) <font color="lightgrey">({updated} updated)</font>\n')
            else:
                g.write(f'- {date} [{title}]({url})\n')

print(time.time() - s)
time.sleep(2)
```

## 过去博客

Wordpress.com -> Github Page -> Blogger -> Github Page

### 考虑过/使用过的平台

- 简书
    - TeX 太丑了
    - 链接要额外跳转一次
- 博客园
    - 我不写技术博客, 和宗旨不符合
    - TeX 好看, 代码块不好看
- CSDN
    - 看起来就远不如博客园
- Wordpress.com
    - 免费版有广告, 体验太差
- Blogger
    - 搬迁到这里之前使用的, 遗址见 [这里](https://randomwalk034.blogspot.com/)
    - 最主要问题是被墙了
- Github Page
    - 最初使用过极简的 [Renge](https://github.com/billyfish152/Renge) 主题, 为了修改 pick up 了一点点 HTML 语法知识. 但是很多地方不合心意就放弃了.

### 用过的编辑器

- 作业部落
    - TeX 支持很好
    - 文件管理系统不太喜欢
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