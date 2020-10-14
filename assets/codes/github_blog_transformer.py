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
        
    elif mode == 'math':
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
    if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.gif'):
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
        cat_flag = 0
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
                elif line.startswith('updated'):
                    cur_post.updated = line[8:].strip().strip('"')
                elif cat_flag and line.startswith('-'):
                    cur_post.cat = line[2:].strip().strip('"')  # only single category is supported
                    cat_flag = 0
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
        url = '/'.join([site, 'category', '#', cat.replace(" ", "%20")])
        g.write(f'- [{cat}]({url}) <font color="lightgrey">({len(cated[cat])})</font>\n')

    g.write(f'\n## Posts\n\n')   
    for cat in sorted(cated.keys()):
        g.write(f'\n### {cat}\n\n')
        for post in sorted(cated[cat], key=lambda x: x[0], reverse=True):
            date, title, updated, link = post
            y, m, d = date[:4], date[5:7], date[-2:]
            url = '/'.join([site, cat.lower().replace(" ", "%20"), y, m, d, link])
            if updated:
                g.write(f'- {date} [{title}]({url}) <font color="lightgrey">({updated} updated)</font>\n')
            else:
                g.write(f'- {date} [{title}]({url})\n')

print(time.time() - s)
time.sleep(2)
