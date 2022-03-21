import collections
import re

from config import joinurl, SITE_HOSTNAME, POST_DST_DIR
from sitemap_base import Post, CAT_DESC_HTML, EXTERNAL_POSTS
from utils import Tag


def get_meta(path) -> dict[str, str]:
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


def get_sitemap():
    posts_groupby_cat = collections.defaultdict(list)
    for path in POST_DST_DIR.glob('*.md'):
        filename = path.stem  # yyyy-mm-dd-slug
        datefmt = 'yyyy-mm-dd'
        post = Post.from_kwargs(
            slug=filename[len(datefmt) + 1:],
            created=filename[:len(datefmt)],
            **get_meta(path)
        )
        posts_groupby_cat[post.categories].append(post)

    for cat, posts in EXTERNAL_POSTS.items():
        posts_groupby_cat[cat].extend(posts)

    sitemap_lines = [
        f'---\ntitle: Sitemap\nlayout: page\nmathjax: true\n---\n',
        f"\n## Categories {Tag.grey(f'({len(posts_groupby_cat)})')}\n\n"
    ]
    total_num_posts = 0
    sorted_cats = sorted(posts_groupby_cat.keys())
    for cat in sorted_cats:
        url = joinurl(
            SITE_HOSTNAME, 'sitemap', f'#{cat.replace(" ", "-").lower()}'
        )
        num_posts = len(posts_groupby_cat[cat])
        total_num_posts += num_posts
        sitemap_lines.append(f'- [{cat}]({url}) {Tag.grey(f"({num_posts})")}\n')
    sitemap_lines.append(CAT_DESC_HTML)

    sitemap_lines.append(f'\n## Posts {Tag.grey(f"({total_num_posts})")}\n')
    for cat in sorted_cats:
        sitemap_lines.append(f'\n### {cat}\n\n')
        for post in sorted(
                posts_groupby_cat[cat], key=lambda x: x.created, reverse=True
        ):
            tag_part = f' `{post.tags}`' if post.tags else ''
            updated_part = f' {Tag.grey(f"({post.updated} updated)")}' if post.updated else ''
            sitemap_lines.append(
                f'- {post.created}{tag_part} [{post.title}]({post.url}){updated_part}\n'
            )
    return ''.join(sitemap_lines)


if __name__ == '__main__':
    print(get_sitemap())
