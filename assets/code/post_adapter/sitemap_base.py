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
             updated='2022-01-09'),
        Post(
            '2020-02-28', '关于那篇日本洗牌文的吐槽 (微博)',
            'https://card.weibo.com/article/m/show/id/2309404477060755095579?ua=Mozilla%2F5.0%20%28Linux%3B%20Android%2012%3B%20M2102J2SC%20Build%2FSKQ1.211006.001%3B%20wv%29%20AppleWebKit%2F537.36%20%28KHTML,%20like%20Gecko%29%20Version%2F4.0%20Chrome%2F100.0.4896.79%20Mobile%20Safari%2F537.36Mi%2010S_12_WeiboIntlAndroid_5980',
        ),
    ],
    'Games': [
#		Post('2024-08-14', '译文 MTG 标准 日本公开赛四强 阿布赞 Ramp 卡组解说 (公众号)', 'https://mp.weixin.qq.com/s/Vru30dBxGsMVwAYcKRGTcQ', tags='MTG'),
#		Post('2024-08-09', '译文 MTG 标准 苍红杯冠军 ryuumei 纯红中速卡组解说 (公众号)', 'https://mp.weixin.qq.com/s/6thISaZM-GeiTPrAr7iojg', tags='MTG'),
#		Post('2024-07-30', '杀戮尖塔的蛇眼到底有多强? (公众号)', 'https://mp.weixin.qq.com/s/pKaCjo9HHkxTk9-pmg0HZQ'),
#		Post('2024-07-25', '近期杀戮尖塔简要心得 (战士 A20 NOSL) (公众号)', 'https://mp.weixin.qq.com/s/C7b0ZPKGlx1xEo0IqeIvpA'),
#		Post('2024-06-04', '翻译 TCG 大赛选手被认为不当决定比赛结果而最终遭 DQ 的故事 (公众号)', 'https://mp.weixin.qq.com/s/qFzFidQNowjUOVEeO7Zt8w'),
#		Post('2024-05-22', '游戏王 YDK2DECKLIST 上线卡组打印功能 (公众号)', 'https://mp.weixin.qq.com/s/5GiinEC4tCr1sqgB7hIQ1A', tags='YGO'),
		Post('2024-05-13', '大模型在小众垂直领域的机器翻译尝试: 以游戏王、万智牌和五子棋为例 (公众号)', 'https://mp.weixin.qq.com/s/Rqwe6l3DNs5zeRY9wHufxQ'),
#		Post('2024-05-09', '译文 MTG 标准 PT 冠军 井川良彦 Domain Ramp 卡组解说 (公众号)', 'https://mp.weixin.qq.com/s/ambcBvYsUskBDlqM4BmqfA', tags='MTG'),
		Post('2024-01-12', '办小型 TCG 比赛时瑞士轮定几轮? (瑞士轮几胜出线 威力加强版) (公众号)', 'https://mp.weixin.qq.com/s/CfnlMWtBAUEOnrWC5oG72Q'),
		Post('2023-09-11', '回到 2011 年玩游戏王 (公众号)', 'https://mp.weixin.qq.com/s/4KqI0rGumkadEAgvO8karQ', tags='YGO'),
		Post('2023-06-29', '游戏王 cube 轮抽交流 (公众号)', 'https://mp.weixin.qq.com/s/jBs3DKJyPeUwP76NK1RCTg', tags='YGO'),
		Post('2023-04-29', '五子棋完全入门指南 (公众号)', 'https://mp.weixin.qq.com/s/BVt_cFO_IltuTt4ORDJYZQ', tags='Renju'),
		Post('2023-04-15', '用棋谱数据库生成的五子棋习题 (公众号)', 'https://mp.weixin.qq.com/s/YaY7-iwbdDyVxwMLsNGovw', tags='Renju'),
		Post('2023-02-19', '国际象棋入门札记 (公众号)', 'https://mp.weixin.qq.com/s/KO9Vjhr2Iz0CqGsaBvoawQ'),
        Post('2023-01-20', 'YDK 到 PDF 卡表转换器 1.0 (公众号)', 'https://mp.weixin.qq.com/s/VCS4aBVqPKbDwCcGf9RpXQ', tags='YGO'),
        Post('2023-01-18', 'YGOPRO YDK 文件直接生成 PDF 卡表 (公众号)', 'https://mp.weixin.qq.com/s/L7FaZdx4mZd5EpTubUlvMw', tags='YGO'),
        Post('2022-12-30', '译文: サイヤCS夺冠的忍者卡组解说 (公众号)', 'https://mp.weixin.qq.com/s/b9_Png1joIM10-5xamfSNA', tags='YGO'),
        Post('2022-06-12', '组织线上赛的经验 (公众号)', 'https://mp.weixin.qq.com/s/MABW63qZN0vkjPCpI7L6Yw', tags='YGO'),
        Post('2022-03-30', '【中村名局】第 41 局, 瑞星, 对西川厚 (知乎)', 'https://zhuanlan.zhihu.com/p/487873516', tags='Renju'),
        Post('2022-03-22', '【中村名局】第 40 局, 斜月, 对 Aldis Reims (知乎)', 'https://zhuanlan.zhihu.com/p/485666026', tags='Renju'),
        Post('2022-03-21', '【中村名局】第 39 局, 岚月, 对 Ingvar Sundling (知乎)', 'https://zhuanlan.zhihu.com/p/484993455', tags='Renju'),
        Post('2022-03-20', '【中村名局】第 38 局, 明星, 对长谷川一人 (知乎)', 'https://zhuanlan.zhihu.com/p/484040607', tags='Renju'),
        Post('2022-03-09', '游戏王 Master Duel 比赛试办: 公开卡组双盘制 (公众号)', 'https://mp.weixin.qq.com/s/tWCjb1TBSYF__EKyfutZhQ', tags='YGO'),
        Post('2020-08-04', 'KTS 的瑞士轮算分机制 (增补) (公众号)', 'https://mp.weixin.qq.com/s/jwZVkYOZNIgwzCDhb-qkdg', tags='YGO'),
        Post('2021-02-02', '复盘一把简单却曲折的五子棋对局 (公众号)', 'https://mp.weixin.qq.com/s/eu8Rvl4ca-T9UX129ND6wg', tags='Renju'),
        Post('2018-08-02', 'Tracker 与 KTS 的瑞士轮算分机制 (公众号)', 'https://mp.weixin.qq.com/s/cSdJ78-maUl1m0w1lJUbmQ', tags='YGO'),
        Post('2020-02-09', 'Challonge 的瑞士轮算分与匹配机制 (公众号)', 'https://mp.weixin.qq.com/s/3b75Z2c3GC4bJWfmtWcS0g', tags='YGO'),
        Post('2016-10-07', '上海决斗都市战报 (公众号)', 'https://mp.weixin.qq.com/s/6s2fHirOwLGPozwh1Xsa4g', tags='YGO')
    ],
    'Food and Cooking': [
        Post('2021-01-01', '黄焖是什么意思? (公众号)', 'https://mp.weixin.qq.com/s/LjsnO0a0Y-iZ4nFwPK20Lw'),
    ],
    'Language': [
        Post('2021-02-10', '「おかしいです」现代日语中一个 "奇怪" 的用法 (公众号)', 'https://mp.weixin.qq.com/s/8XRHmV6mt3deIWM1oRYZdg'),
    ],
    'Miscellanea': [
		Post('2024-08-10', 'TFCC 损伤 保守治疗篇 (公众号)', 'https://mp.weixin.qq.com/s/CAWkmJDvOr_InQf83CAtpg'),
        Post('2021-06-24', '上海动物园游记 (公众号)', 'https://mp.weixin.qq.com/s/fJO61Rlpa48yWe1nb_l3Fw'),
    ],
    'Machine Learning': [
		Post('2023-07-19', '基于神经网络的棋类 AI 简介: 以 AlphaGo Zero 和 Stockfish NNUE 为例 (公众号)', 'https://mp.weixin.qq.com/s/beI13muMO9uzUyhNs1ooig'),
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

CAT_DESC_HTML = '\n'.join([
    '',
    '<details><summary><b>分类说明</b></summary>',
    f"{markdown.markdown(CAT_DESC, extensions=['fenced_code'])}",
    '</details>',
    '',
])
