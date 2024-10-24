# Deprecated
# TODO
# - 重构代码: 现在代码冗余太多

import os
import re
import shutil
import time

import markdown

s = time.time()

# source_dir = r'F:\vnote_notebooks\vnotebook'
# target_dir = r'F:\GitHub'
source_dir = r'D:\GitHub\vnote_notebooks\vnotebook'
target_dir = r'D:\GitHub'


def solve_escape(string, mode='link'):
    # https://stackoverflow.com/questions/6116978/how-to-replace-multiple-substrings-of-a-string

    if mode == 'link':
        pattern = '(\[.*?\|.*?\])(\(.*?\))'
        rep = {'|': '\|'}

    elif mode == 'math':
        pattern = '\$(.*?)\$'
        rep = {'\{': r'\\{', '\}': r'\\}', '^*': r'^\ast', '\#': r'\\#'}

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
    if string.startswith(r'\begin{align') and flag > 0:
        return '$$\n' + string
    if string.startswith(r'\end{align') and flag > 0:
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


def solve_img2html(string, path='https://shiina18.github.io/assets/posts/'):
    pattern = '!\[(.*?)\]\((.*?)\)'
    new_string = []
    index = 0
    for match in re.finditer(pattern, string):
        new_string.append(string[index:match.start(2)])
        tmp = string[match.start(1):match.end(1)]
        tmp = f' "{tmp}"' if tmp else ''
        new_string.extend([path,
                           string[match.start(2):match.end(2)]])
        index = match.end(2)
    new_string.append(string[index:])
    return ''.join(new_string)


# posts

source = os.path.join(source_dir, r'Blogger\Posts')
target = os.path.join(target_dir, r'shiina18.github.io\_posts')

for file in os.listdir(source):
    if file.endswith('.md'):
        source_path = os.path.join(source, file)
        target_path = os.path.join(target, file)
        if os.path.exists(target_path) and (
                os.path.getmtime(source_path) <= os.path.getmtime(target_path)):
            continue
        with open(source_path, encoding='utf-8') as f:    
            with open(target_path, encoding='utf-8', mode='w') as g:
                # solve_display_math
                flag = 1
                is_details_tag = False
                details_tag_lines = []
                for line in f:
                    details_ht = line.startswith('<details>') or line.startswith('</details>')
                    if details_ht:
                        # TODO: syntax highlighting requires js which is not urgent
                        # https://blog.paoloamoroso.com/2021/10/how-to-add-code-syntax-highlighting-to.html
                        # mathjax is not tested and not urgent
                        is_details_tag = not is_details_tag
                    if line.startswith('<details>'):
                        match = re.match('<details><summary>(.*)</summary>', line)
                        line = f'<details><summary>{line[match.start(1):match.end(1)]} <font color="deepskyblue">(Show more &raquo;)</font></summary>'
                    if is_details_tag and not details_ht:
                        line = solve_img2html(line)
                        details_tag_lines.append(line)
                        continue
                    if line.startswith('</details>'):
                        details_md = ''.join(details_tag_lines)
                        details_tag_lines = []
                        details_html = markdown.markdown(details_md, extensions=['fenced_code'])
                        g.write(details_html)
                    line = solve_escape(line, 'link')
                    line = solve_escape(line, 'math')
                    line = solve_display_math(line)
                    line = solve_img(line)
                    if '^*' in line:
                        print(os.path.join(source, file))
                        print(line)
                    g.write(line)

# pages

source = os.path.join(source_dir, r'Blogger')
target = os.path.join(target_dir, r'shiina18.github.io')

for file in os.listdir(source):
    if '.' not in file and file not in {'Posts', '_v_attachments', 'images'}:
        source_path = os.path.join(source, file, 'index.md')
        target_path = os.path.join(target, file, 'index.md')
        if os.path.exists(target_path) and (
                os.path.getmtime(source_path) <= os.path.getmtime(target_path)):
            continue
        with open(source_path, encoding='utf-8') as f:
            with open(target_path, encoding='utf-8', mode='w') as g:
                for line in f:
                    line = solve_escape(line, 'link')
                    line = solve_escape(line, 'math')
                    line = solve_display_math(line)
                    line = solve_img(line)
                    if '^*' in line:
                        print(os.path.join(source, file))
                        print(line)
                    g.write(line)

# images

source = os.path.join(source_dir, r'Blogger\Posts\images')
target = os.path.join(target_dir, r'shiina18.github.io\assets\posts\images')

for file in os.listdir(source):
    if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.gif'):
        source_path = os.path.join(source, file)
        target_path = os.path.join(target, file)
        if os.path.exists(target_path) and (os.path.getmtime(source_path) <= os.path.getmtime(target_path)):
            continue
        shutil.copyfile(source_path, target_path)

# sitemap

from collections import defaultdict


class Post():
    def __init__(self, date=None, title=None, cat=None, updated=None, link=None, tag=None):
        self.date = date
        self.title = title
        self.cat = cat
        self.updated = updated
        self.link = link
        self.tag = tag


source = os.path.join(target_dir, r'shiina18.github.io\_posts')
cated = defaultdict(list)

for post in os.listdir(source):
    date = post[:10]
    link = post[11:-3]
    cur_post = Post(date=date, link=link)
    with open(os.path.join(source, post), encoding='utf-8') as p:
        flag = 0
        cat_flag = 0
        tag_flag = 0
        for line in p:
            if line.startswith('---'):
                flag += 1
            if flag == 2:
                break
            if flag:
                if line.startswith('title'):
                    cur_post.title = line[6:].strip().strip('"')
                elif line.startswith('categories'):
                    cur_post.cat = line[11:].strip().strip('"')
                    if not cur_post.cat:
                        cat_flag = 1
                elif line.startswith('tags'):
                    cur_post.tag = line[5:].strip().strip('"')
                    if not cur_post.tag:
                        tag_flag = 1
                elif line.startswith('updated'):
                    cur_post.updated = line[8:].strip().strip('"')
                elif cat_flag and line.startswith('-'):
                    cur_post.cat = line[2:].strip().strip('"')  # only single category is supported
                    cat_flag = 0
                elif tag_flag and line.startswith('-'):
                    cur_post.tag = line[2:].strip().strip('"')  # only single tag is supported
                    tag_flag = 0
        cated[cur_post.cat].append((cur_post.date, cur_post.title, cur_post.updated, cur_post.link, cur_post.tag))

posts_from_other_sites = {
    'Mathematics': [
        ('2018-04-11', '甄姬洛神后闪电判定是否更容易命中? (知乎)', '', 'https://www.zhihu.com/question/270563020/answer/363874639', None),
        ('2019-11-07', '条件方差公式的直观解释? (知乎)', '', 'https://www.zhihu.com/question/38726155/answer/885319771', None),
        ('2021-01-16', '为什么熵值最大的分布状态是正态分布而不是均匀分布? (知乎)', '', 'https://www.zhihu.com/question/357032828/answer/907586249', None),
        ('2018-09-05', '随笔｜名推理期望问题大结局 (公众号)', '', 'https://mp.weixin.qq.com/s/wsTlzJGfTzERfFmkOhtemA', None),
        ('2020-03-05', '洗牌的一点数学 (公众号)', '', 'https://mp.weixin.qq.com/s/wQLWX7x9NFpVCK3Dk9u7Xw', None),
        ('2021-01-13', '轮抽卡池怎么洗? (公众号)', '', 'https://mp.weixin.qq.com/s/8xsCp5IPisAD1qUPUr9IHA', None),
        ('2020-11-14', '为什么中位数最小化 MAE? (知乎)', '2022-01-09', 'https://www.zhihu.com/question/429407710/answer/1591908502', None)
    ],
    'Games': [
        ('2020-08-04', 'KTS 的瑞士轮算分机制 (增补) (公众号)', '', 'https://mp.weixin.qq.com/s/jwZVkYOZNIgwzCDhb-qkdg', None),
        ('2021-02-02', '复盘一把简单却曲折的五子棋对局 (公众号)', '', 'https://mp.weixin.qq.com/s/eu8Rvl4ca-T9UX129ND6wg', 'Renju'),
        ('2018-08-02', 'Tracker 与 KTS 的瑞士轮算分机制 (公众号)', '', 'https://mp.weixin.qq.com/s/cSdJ78-maUl1m0w1lJUbmQ', None),
        ('2020-02-09', 'Challonge 的瑞士轮算分与匹配机制 (公众号)', '', 'https://mp.weixin.qq.com/s/3b75Z2c3GC4bJWfmtWcS0g', None),
        ('2016-10-07', '上海决斗都市战报 (公众号)', '', 'https://mp.weixin.qq.com/s/6s2fHirOwLGPozwh1Xsa4g', None)
    ],
    'Food and Cooking': [
        ('2021-01-01', '黄焖是什么意思? (公众号)', '', 'https://mp.weixin.qq.com/s/LjsnO0a0Y-iZ4nFwPK20Lw', None),
    ],
    'Language': [
        ('2021-02-10', '「おかしいです」现代日语中一个 "奇怪" 的用法 (公众号)', '', 'https://mp.weixin.qq.com/s/8XRHmV6mt3deIWM1oRYZdg', None),
    ],
    'Miscellanea': [
        ('2021-06-24', '上海动物园游记 (公众号)', '', 'https://mp.weixin.qq.com/s/fJO61Rlpa48yWe1nb_l3Fw', None),
    ],
    'Machine Learning': [
        ('2020-08-12', '关于 Facebook Prophet 中 future changepoints 的一个脚注 (知乎)', '', 'https://zhuanlan.zhihu.com/p/181708348', 'Time Series')
    ],
    'Algorithms': [
        ('2019-11-26', '一类双指针贪心法的证明——以 LeetCode 11, 16 为例 (知乎)', '', 'https://zhuanlan.zhihu.com/p/93808593', None),
        ('2019-11-25', 'LeetCode 179. Largest Number (知乎)', '', 'https://zhuanlan.zhihu.com/p/93630049', None),
        ('2021-02-05', '最小化「集换社」税收 (公众号)', '', 'https://mp.weixin.qq.com/s/TKUS6IEiE-a1-kYuz1t1sw', None)
    ]
}
for cat in posts_from_other_sites.keys():
    cated[cat].extend(posts_from_other_sites[cat])

site = 'https://shiina18.github.io'
target = os.path.join(target_dir, r'shiina18.github.io\sitemap')

md_guide = '''
- 技术类
    - [#machine-learning](https://shiina18.github.io/sitemap/#machine-learning): 包含深度学习
    - [#tech](https://shiina18.github.io/sitemap/#tech): 更一般的计算机技术, 以及工程问题, 单纯关于编程语言的文章则归入 [#language](https://shiina18.github.io/sitemap/#language)
    - [#algorithms](https://shiina18.github.io/sitemap/#algorithms): 算法导论和编程题 (如 LeetCode) 相关
- 数学类: 简单但有趣的问题, 包含严格证明
    - [#mathematics](https://shiina18.github.io/sitemap/#mathematics): 包含概率论
    - [#statistics](https://shiina18.github.io/sitemap/#statistics)
- 其他分类都 self-explained
'''

str_userguide = f'''
<details><summary><b>分类说明</b></summary>
{markdown.markdown(md_guide, extensions=['fenced_code'])}
</details>
'''

with open(os.path.join(target, 'index.md'), encoding='utf-8', mode='w') as g:
    g.write('---\n')
    g.write('title: Sitemap\n')
    g.write('layout: page\n')
    g.write('mathjax: true\n')
    g.write('---\n\n')

    g.write(f'\n## Categories  <font color="lightgrey">({len(cated.keys())})</font>\n\n')
    for cat in sorted(cated.keys()):
        # url = '/'.join([site, 'category', '#', cat.replace(" ", "%20")])
        url = '/'.join([site, 'sitemap', f'#{cat.replace(" ", "-").lower()}'])
        g.write(f'- [{cat}]({url}) <font color="lightgrey">({len(cated[cat])})</font>\n')  
    g.write(str_userguide)

    g.write(f'\n## Posts <font color="lightgrey">({sum(len(cated[cat]) for cat in cated.keys())})</font>\n\n')
    for cat in sorted(cated.keys()):
        g.write(f'\n### {cat}\n\n')
        for post in sorted(cated[cat], key=lambda x: x[0], reverse=True):
            date, title, updated, link, tag = post
            y, m, d = date[:4], date[5:7], date[-2:]
            if link.startswith('https://') or link.startswith('http://'):
                url = link
            else:
                url = '/'.join([site, cat.lower().replace(" ", "%20"), y, m, d, link])
            if tag:
                line = f'- {date} `{tag}` [{title}]({url})'
            else:
                line = f'- {date} [{title}]({url})'
            if updated:
                line += f' <font color="lightgrey">({updated} updated)</font>'
            line += '\n'
            g.write(line)

print(time.time() - s)
input()
