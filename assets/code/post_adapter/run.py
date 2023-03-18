import logging
import shutil
import time

from adapter import PostAdapter
from config import (
    SRC_ROOT, DST_ROOT, POST_SRC_DIR, POST_DST_DIR, IMG_SRC_DIR, IMG_DST_DIR
)
from sitemap import get_sitemap
from utils import should_update

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s | %(message)s')

start_time = time.time()
OVERWRITE_ALL = False


def adapt(path, target_path):
    if OVERWRITE_ALL or should_update(path, target_path):
        logger.info(path.relative_to(path.parents[1]))
        p = PostAdapter(path)
        adapted_p = p.adapt()
        target_path.write_text(''.join(adapted_p), encoding='utf8')


# posts
for path in POST_SRC_DIR.glob('*.md'):
    adapt(path, POST_DST_DIR / path.name)

# pages
for path in SRC_ROOT.iterdir():
    if path.is_dir() and path.name not in {POST_SRC_DIR.name, 'images'} and not path.name.startswith('_'):
        adapt(path / 'index.md', DST_ROOT / path.name / 'index.md')

# images
# no images for pages currently
for path in IMG_SRC_DIR.iterdir():
    if path.suffix in {'.png', '.jpg', '.gif'}:
        target_path = IMG_DST_DIR / path.name
        if OVERWRITE_ALL or should_update(path, target_path):
            logger.info(path.relative_to(path.parents[1]))
            shutil.copyfile(path, target_path)

# sitemap
(DST_ROOT / 'sitemap' / 'index.md').write_text(get_sitemap(), encoding='utf8')
logger.info(f'Elapsed time: {time.time() - start_time: .2f} s')
input()
