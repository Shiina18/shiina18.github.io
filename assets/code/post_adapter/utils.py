# import asyncio
import logging
import pathlib
# import re

# import httpx

logger = logging.getLogger(__name__)


class Tag:
    @staticmethod
    def tag(tag, content, **attrs):
        attr_line = ''.join(f' {attr}="{v}"' for attr, v in attrs.items())
        return f'<{tag}{attr_line}>{content}</{tag}>'

    @staticmethod
    def font(content, color):
        return Tag.tag('font', content, color=color)

    @staticmethod
    def grey(content):
        return Tag.font(content, 'lightgrey')


def should_update(src_path: pathlib.Path, dst_path: pathlib.Path):
    if dst_path.exists() and src_path.stat().st_mtime <= dst_path.stat().st_mtime:
        return False
    return True


################################################################################
# TODO: WIP, doesn't work now
# https://www.twilio.com/blog/asynchronous-http-requests-in-python-with-httpx-and-asyncio

# def gather_urls(path) -> list[str]:
#     urls = []
#     with open(path, encoding='utf8') as reader:
#         for line in reader:
#             for match in re.finditer(r'\[.*?\]\((.*?)\)', line):
#                 # TODO: make it safe since there can be `()` in the url
#                 url_desc = match.group(1)
#                 if not url_desc.startswith('http'):
#                     logger.warning(
#                         f"{url_desc} doesn't start with http: {line} {path.name}")
#                     continue
#                 urls.append(re.sub(r' ".*?"', '', url_desc))
#     return urls
#
#
# # TODO: still full of errors
# # white_list = [
# #         'wikipedia.org',
# #         'https://github.com',
# #         'https://www.youtube.com',
# #         'https://shiina18.github.io'
# #     ]
#
#
# async def is_url_alive(client, url, posts):
#     log = f' : {url} {posts}'
#     # TODO: VPN can not be used now
#     # for s in white_list:
#     #     if s in url:
#     #         return
#     try:
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
#         }
#         await client.head(url, headers=headers)
#         # TODO: check status code
#         logger.debug('ok' + log)
#     except httpx.ConnectTimeout as exc:
#         logger.error(type(exc).__name__ + log)
#     except (httpx.RemoteProtocolError, httpx.ReadTimeout) as exc:
#         logger.debug(type(exc).__name__ + log)
#     except httpx.HTTPError as exc:
#         logger.error(type(exc).__name__ + log)
#
#
# async def check_urls(url_posts_dict: dict[str, list[str]]):
#     # https://www.python-httpx.org/advanced/#pool-limit-configuration
#     limits = httpx.Limits(max_connections=None)
#     async with httpx.AsyncClient(limits=limits) as client:
#         tasks = [
#             asyncio.ensure_future(is_url_alive(client, url, posts))
#             for url, posts in url_posts_dict.items()
#         ]
#         await asyncio.gather(*tasks)
################################################################################
