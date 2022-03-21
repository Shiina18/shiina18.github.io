import dataclasses
import datetime
import inspect

import markdown

from config import joinurl, SITE_HOSTNAME


@dataclasses.dataclass()
class Post:
    created: str
    title: str
    slug: str  # full url for external posts
    updated: str = None
    tags: str = None  # only single tag for now
    categories: str = None  # only single category for now

    @classmethod
    def from_kwargs(cls, **kwargs):
        # https://stackoverflow.com/questions/55099243/python3-dataclass-with-kwargsasterisk
        cls_fields = {field for field in inspect.signature(cls).parameters}
        native_args = {k: v for k, v in kwargs.items() if k in cls_fields}
        return cls(**native_args)

    def __post_init__(self):
        if self.slug.startswith('https://') or self.slug.startswith('http://'):
            self.url = self.slug
        else:
            self.url = joinurl(
                SITE_HOSTNAME,
                self.categories.lower().replace(" ", "%20"),
                datetime.datetime.strptime(self.created, '%Y-%m-%d').strftime('%Y/%m/%d'),
                self.slug
            )


EXTERNAL_POSTS = {
    'Mathematics': [
        Post('2018-04-11', '甄姬洛神后闪电判定是否更容易命中? (知乎)', 'https://www.zhihu.com/question/270563020/answer/363874639'),
        Post('2019-11-07', '条件方差公式的直观解释? (知乎)', 'https://www.zhihu.com/question/38726155/answer/885319771'),
        Post('2021-01-16', '为什么熵值最大的分布状态是正态分布而不是均匀分布? (知乎)',
             'https://www.zhihu.com/question/357032828/answer/907586249'),
        Post('2018-09-05', '随笔｜名推理期望问题大结局 (公众号)', 'https://mp.weixin.qq.com/s/wsTlzJGfTzERfFmkOhtemA'),
        Post('2020-03-05', '洗牌的一点数学 (公众号)', 'https://mp.weixin.qq.com/s/wQLWX7x9NFpVCK3Dk9u7Xw'),
        Post('2021-01-13', '轮抽卡池怎么洗? (公众号)', 'https://mp.weixin.qq.com/s/8xsCp5IPisAD1qUPUr9IHA'),
        Post('2020-11-14', '为什么中位数最小化 MAE? (知乎)', 'https://www.zhihu.com/question/429407710/answer/1591908502',
             updated='2022-01-09')
    ],
    'Games': [
        Post('2022-03-20', '【中村名局】第三十八局, 明星, 对长谷川一人 (知乎)', 'https://zhuanlan.zhihu.com/p/484040607', tags='Renju'),
        Post('2022-03-09', '游戏王 Master Duel 比赛试办: 公开卡组双盘制 (公众号)', 'https://mp.weixin.qq.com/s/tWCjb1TBSYF__EKyfutZhQ'),
        Post('2020-08-04', 'KTS 的瑞士轮算分机制 (增补) (公众号)', 'https://mp.weixin.qq.com/s/jwZVkYOZNIgwzCDhb-qkdg'),
        Post('2021-02-02', '复盘一把简单却曲折的五子棋对局 (公众号)', 'https://mp.weixin.qq.com/s/eu8Rvl4ca-T9UX129ND6wg', tags='Renju'),
        Post('2018-08-02', 'Tracker 与 KTS 的瑞士轮算分机制 (公众号)', 'https://mp.weixin.qq.com/s/cSdJ78-maUl1m0w1lJUbmQ'),
        Post('2020-02-09', 'Challonge 的瑞士轮算分与匹配机制 (公众号)', 'https://mp.weixin.qq.com/s/3b75Z2c3GC4bJWfmtWcS0g'),
        Post('2016-10-07', '上海决斗都市战报 (公众号)', 'https://mp.weixin.qq.com/s/6s2fHirOwLGPozwh1Xsa4g')
    ],
    'Food and Cooking': [
        Post('2021-01-01', '黄焖是什么意思? (公众号)', 'https://mp.weixin.qq.com/s/LjsnO0a0Y-iZ4nFwPK20Lw'),
    ],
    'Language': [
        Post('2021-02-10', '「おかしいです」现代日语中一个 "奇怪" 的用法 (公众号)', 'https://mp.weixin.qq.com/s/8XRHmV6mt3deIWM1oRYZdg'),
    ],
    'Miscellanea': [
        Post('2021-06-24', '上海动物园游记 (公众号)', 'https://mp.weixin.qq.com/s/fJO61Rlpa48yWe1nb_l3Fw'),
    ],
    'Machine Learning': [
        Post('2020-08-12', '关于 Facebook Prophet 中 future changepoints 的一个脚注 (知乎)',
             'https://zhuanlan.zhihu.com/p/181708348', tags='Time Series')
    ],
    'Algorithms': [
        Post('2019-11-26', '一类双指针贪心法的证明——以 LeetCode 11, 16 为例 (知乎)', 'https://zhuanlan.zhihu.com/p/93808593'),
        Post('2019-11-25', 'LeetCode 179. Largest Number (知乎)', 'https://zhuanlan.zhihu.com/p/93630049'),
        Post('2021-02-05', '最小化「集换社」税收 (公众号)', 'https://mp.weixin.qq.com/s/TKUS6IEiE-a1-kYuz1t1sw')
    ]
}

CAT_DESC = '''- 技术类
    - [#machine-learning](https://shiina18.github.io/sitemap/#machine-learning): 包含深度学习
    - [#tech](https://shiina18.github.io/sitemap/#tech): 更一般的计算机技术, 以及工程问题, 单纯关于编程语言的文章则归入 [#language](https://shiina18.github.io/sitemap/#language)
    - [#algorithms](https://shiina18.github.io/sitemap/#algorithms): 算法导论和编程题 (如 LeetCode) 相关
- 数学类: 简单但有趣的问题, 包含严格证明
    - [#mathematics](https://shiina18.github.io/sitemap/#mathematics): 包含概率论
    - [#statistics](https://shiina18.github.io/sitemap/#statistics)
- 其他分类都 self-explained'''

CAT_DESC_HTML = f'''
<details><summary><b>分类说明</b></summary>
{markdown.markdown(CAT_DESC, extensions=['fenced_code'])}
</details>
'''