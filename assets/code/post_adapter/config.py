import pathlib


def joinurl(*args):
    scheme = 'https://'
    part_a = scheme if not args[0].startswith(scheme) else ''
    part_b = '/'.join(arg.strip('/') for arg in args)
    return part_a + part_b


SITE_HOSTNAME = 'shiina18.github.io'
SRC_ROOT = pathlib.Path('D:/GitHub/vnote_notebooks/vnotebook/Blogger')
DST_ROOT = pathlib.Path('D:/GitHub') / SITE_HOSTNAME
POST_SRC_DIR = SRC_ROOT / 'Posts'
POST_DST_DIR = DST_ROOT / '_posts'
IMG_URL_ROOT = joinurl(SITE_HOSTNAME, 'assets/posts')
IMG_SRC_DIR = POST_SRC_DIR / 'images'
IMG_DST_DIR = DST_ROOT / 'assets/posts' / 'images'
