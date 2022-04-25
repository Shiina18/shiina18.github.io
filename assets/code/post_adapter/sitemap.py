import collections
import datetime
import re
from typing import *

import markdown

from config import joinurl, SITE_HOSTNAME, POST_DST_DIR
from sitemap_base import Post, CAT_DESC_HTML, EXTERNAL_POSTS
from utils import Tag


def get_meta(path) -> Dict[str, str]:
    with open(path, encoding='utf8') as reader:
        separator_count = 0
        # only single value for each key is supported
        # many corner cases are not covered since they can be avoided by hand
        meta_dict = dict()
        k_buffer = None
        for line in reader:
            if line.startswith('---'):
                separator_count += 1
            if separator_count == 2:
                break
            if separator_count > 0:
                match = re.match(r'(.*?):(.*)', line)
                if match:
                    k, v = match.group(1), match.group(2).strip().strip('"')
                    if v:
                        meta_dict[k] = v
                        k_buffer = None
                    else:
                        k_buffer = k
                elif k_buffer is not None:
                    match = re.match(r'- (.*)', line)
                    if match:
                        meta_dict[k_buffer] = match.group(1).strip()
                    k_buffer = None
    return meta_dict


def get_cat2posts():
    cat2posts = collections.defaultdict(list)
    for path in POST_DST_DIR.glob('*.md'):
        filename = path.stem  # yyyy-mm-dd-slug
        datefmt = 'yyyy-mm-dd'
        post = Post.from_kwargs(
            slug=filename[len(datefmt) + 1:],
            created=filename[:len(datefmt)],
            **get_meta(path)
        )
        cat2posts[post.categories].append(post)
    for cat, posts in EXTERNAL_POSTS.items():
        cat2posts[cat].extend(posts)
    return cat2posts


def get_cat_lines(cat2posts):
    lines = []
    total_num_posts = 0
    for cat in sorted(cat2posts.keys()):
        url = joinurl(
            SITE_HOSTNAME, 'sitemap', f'#{cat.replace(" ", "-").lower()}'
        )
        num_posts = len(cat2posts[cat])
        total_num_posts += num_posts
        lines.append(f'- [{cat}]({url}) {Tag.grey(f"({num_posts})")}\n')

    lines.append(CAT_DESC_HTML)
    lines.append(get_recent_update_lines(cat2posts))
    lines.append(f'\n## Posts {Tag.grey(f"({total_num_posts})")}\n')
    return lines


def get_post_item(post):
    tag_part = f' `{post.tags}`' if post.tags else ''
    updated_part = f' {Tag.grey(f"({post.updated} updated)")}' if post.updated else ''
    return f'- {post.created}{tag_part} [{post.title}]({post.url}){updated_part}\n'


def get_post_lines(cat2posts):
    lines = []
    for cat in sorted(cat2posts.keys()):
        lines.append(f'\n### {cat}\n\n')
        # newest to oldest
        lines += [
            get_post_item(post) for post in sorted(
                cat2posts[cat], key=lambda x: x.created, reverse=True
            )
        ]
    return lines


def get_recent_update_lines(cat2posts):
    recent_updates = []
    since_date_str = (
        datetime.datetime.today() - datetime.timedelta(days=90)
    ).strftime('%Y-%m-%d')
    for _, posts in cat2posts.items():
        for post in posts:
            if post.updated is not None and post.updated > since_date_str:
                recent_updates.append(post)
    recent_updates.sort(key=lambda post: post.updated, reverse=True)
    recent_updates = ''.join(get_post_item(post) for post in recent_updates)
    RECENT_UPDATES_HTML = '\n'.join([
        '',
        '<details><summary><b>Recent updates</b></summary>',
        f"{markdown.markdown(recent_updates, extensions=['fenced_code'])}",
        '</details>',
        '',
    ])
    return RECENT_UPDATES_HTML


def get_sitemap():
    cat2posts = get_cat2posts()
    sitemap_lines = [
        f'---\ntitle: Sitemap\nlayout: page\nmathjax: true\n---\n',
        f"\n## Categories {Tag.grey(f'({len(cat2posts)})')}\n\n"
    ]
    sitemap_lines += get_cat_lines(cat2posts)
    sitemap_lines += get_post_lines(cat2posts)
    return ''.join(sitemap_lines)


if __name__ == '__main__':
    print(get_sitemap())
