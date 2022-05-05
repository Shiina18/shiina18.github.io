---
title: "从零开始的五子棋学习"
categories: Games
tags: Renju
updated: 2022-04-29
comments: true
mathjax: false
---

习惯叫法是, 无禁手的称为 "五目" (gomoku), 有禁手的称为 "连珠" (renju). 比如一手交换, swap 2 都属于 gomoku.

<!-- more -->

## 预想路线

五子棋总体来说是小众且入门门槛不低的棋类, 相比其他棋类用时短, 攻防激烈.

1. 三手胜, 花浦定式
2. 瑞星, 疏星的初步知识
3. 其他开局定式

作为业余随便玩玩的, 能完成第一步我就满足了. 花浦定式其实还挺不容易的.

## 书

- 曾杨锋. (2013). [五子棋零基础自学一本通 (第三版)](https://shiina18.github.io/assets/docs/五子棋零基础自学一本通.pdf). *百度五子棋贴吧*.
- 坂田吾朗. (2000). 三手胜五子棋题解. 人民体育出版社.
- 新井华石九段. (1997). 五子连珠必胜法 (译, 张书). 人民体育出版社.
- 真野芳久五段. (2015, Jun). [連珠の基礎](http://tokai-renjukai.pya.jp/siryo/RenjuKiso/RenjuKiso-1-2.pdf). *東海連珠会*. 另附 [超链接版](http://tokai-renjukai.pya.jp/siryo/RenjuSiryo.html). (2020/12/12)
- 李洪斌. (2010). 五子棋实战必读——基础定式. 成都时代出版社.

自学一本通是很好的零基础读物, 三手胜是必读经典.

李洪斌的书第一章讲如何学棋, 可以参考, 阅读定式需要一定基础.

戴晓涵有本《方寸之间》, 在 "零基础学五子棋" 公众号可以白嫖前三章, 对我来说第二章 "虎头虎尾" 有一些帮助.

随着技术发展, 一些非必胜的判断可能被推翻, 阅读这类书籍要非常小心.

### 资料留存

- [連珠の本の案内](http://www15.plala.or.jp/ssiio/renjubook.htm)
- 彭建国 & 包明慧. (2005). 五子棋争先妙手. 北京体育出版社

《五子棋争先妙手》是一本专门讲瑞星的书, 平铺直叙, 只能拿来看几个实战谱.

## 软件

- 线上博弈平台. 五林大会: 专业, 自带人机模式, 主创刘超四段, 霍九旭六段为夫妇. 2021 年 5 月后客户端关服, 改用 [网页平台](https://renjuworld.net/).
- 打谱. 通用操作: Delete 键删除当前分枝. Ctrl+鼠标左键在棋盘上标注文字.
    - [renlib](https://www.renju.se/renlib/): 国外软件, 很容易找, 解题引擎用的就是 renju solver. 
        - 一个重大问题是 renlib 打开棋谱占用的内存很大, 乐赛就没有这个问题.
    - 乐赛五子棋打谱软件: Temple 大学的数学 PhD 温向东开发, UI 漂亮, 功能强大. 收费软件. 以前的爱五子棋打谱软件, 以及连珠终结者 (Renju Solver) 都是他写的. 作者本人其实只是初学者水平.
    - [摆谱小工具](https://lfz084.gitee.io/renju/renju.html): 网页打谱, 可以设置 "下一手为 1", 以及各种方便的标记, 可以用来找点.
- AI
    - [蜗牛连珠](https://www.wind23.com/gomokuai.html): 手机 app. 主要好处是支持无禁手 AI 计算. 作者郝天一, 五子棋专业四段, 清华姚班, CS PhD. 实际用下来, 选点比弈心菜了不少, 但思路仍然值得初学者学习.
    - [弈心](https://www.aiexp.info/pages/yixin.html): 作者孙锴, 上交 CS 本, Cornell CS PhD. 在 katago 和 embryo 出现前是无敌的 AI.
    - [Embryo](https://github.com/Hexik/Embryo_engine). 如果设备跑不动 katago 的话就只能选择这个了. 另外还有基于 embryo 的制谱器, 可以在 QQ 群获取.
    - [Katago](https://github.com/hzyhhzy/KataGo). 乱杀奕心, 现在普通配置的电脑也跑得动. (2021/8/29)
        - 现在还有智子五子棋.

## 网上资源

### 特别推荐

- 五子棋 QQ 群: 可以免费获得大量资料, 以及比赛信息.
    - B 站五子棋 up 主粉丝交流群: 906038065
    - 五子棋道馆: 861589961
    - 华夏大讲堂五子棋初⑳: 737972308
- B 站 up 主:
    - [摆棋老李](https://space.bilibili.com/400842144). 李洪斌, 专业六段. 基础定式讲解, 名局讲解. 特效做得好.
    - [乐赛丶](https://space.bilibili.com/291338278/). 金洪利, 专业三段, 比赛官方解说员. 在虎牙直播. 比赛讲解.
    - [华韬五子棋](https://space.bilibili.com/587696044). 讲解很清楚.
- 河村典彦九段. [河村九段の連珠講座](http://www.kyogo.org/contents/kouza.html). *京都連珠会*. 初心者向.
- [励精连珠教室](http://www.ljrenju.com/index.htm). 国内很多网站都十分老旧, 这是难得更新勤快的网站, 有用的资料也很多. 定式资料有点老, 不过棋谱很全, 很好用.
    - 虽然推荐, 励精还是有做得不好的地方, 比如 [连珠兵法战术](http://www.ljrenju.com/croom/kjjj/r4.htm) 一文大量直接翻译自 [河村九段初级讲座第二回「连攻」](https://shiina18.github.io/games/2020/10/25/renju-kouza-beginner/), 却没有给出任何 credit (只提到了一句 "河村典彦先生首推山形为进攻做二的最佳结构"). 类似地, 定式大概也是翻译自日语 (有些甚至还留着原文), 但是没有给出任何 references; 定式的年代也不清楚, 因为定式会翻新, 不知道是老定式还是新定式不利于初学者获得正确的知识. 最讽刺的是, 他在页脚写道 "励精付出精力, 请勿转载翻版", 自己却一点也没有这样的意识, 这种行为对信息传播非常不利.
- [587 连珠](http://587.renju.org.tw/). 很好的台湾教学网站, 有交互式棋盘, 以及实用的资源整合. 有一定难度. 作者是台湾顶尖棋手林書玄. 
- [★魚丸湯の闇黑五子棋學院★](https://blog.xuite.net/jang20529659/twblog1). 台湾棋手楊裕雄三段的博客, 有很多教学文章.
- [The Renju International Federation Portal - RenjuNet](https://www.renju.net/). 官网. 去年看还是上个世纪的页面水平, 现在更新了很多东西, 文章里可以翻出很多老古董. (2022/3/31)

### 其他资源

- B 站 up
    - [卖丶菜](https://space.bilibili.com/28742590). 几个最强开局的定式讲解. 
    - [连珠之魂](https://space.bilibili.com/135341585/). 兰志仁, 专业六段. 定式介绍, 比赛讲解.
- 温顺的瓜皮猫. (2020, Jun 3). [五子棋中, 先手下棋到底有多大的优势?](https://www.zhihu.com/question/267273167/answer/323472412). *知乎*.
- 五子剑. (2009, Jun 29). [五子剑系列讲座](http://www.wuzi8.com/xiti/HTML/1752.html). *中国五子棋网*.
- 叉色-xsir. (2019, Mar 11). [一个非常硬核的五子棋资料站](https://zhuanlan.zhihu.com/p/51846364). *知乎*.  Ando 的连珠教室的一些资料. 还翻译了《连珠名局集-第七世名人 中村茂》 (2022/3/18)
- [xsir31 分享的若干资源](https://github.com/xsir317/ku10/tree/master/resources). 包括一些日语和英语的资源. 
- 松浦浩七段. [連珠苦楽部](http://matsurenju.game.coocan.jp/). 包括用习题的方式讲解定式.
- 那智暴虐のれんじゅいし. (2018, Aug 10). [【連珠】入門、初心者の方が最初に覚える形について自分なりに考察した【五目並べ】](https://www.youtube.com/watch?v=J1kmzW9A95U). *YouTube*.
    - 这是中山智晴, 日本 top 棋手, 有博客 [那智暴虐の連珠石](https://note.com/nachiblack) (但没啥好看的, 冈部宽也有博客, 也没啥好看的就没写). 
    - 容易取胜的形状: 不推荐初学者花浦, 推荐溪峡. 形状互通, 黑八卦不容易输.
    - 想记住手筋: 云雨. 互通, 手筋型的进攻多, 但是很难, 有背诵价值.
    - 想打持久战: 疏流.
    - 各种规则都适用 (?): 丘斜.
- [日本連珠社](https://www.renjusha.net/). 有许多河村九段的研究资料. 
- [中国连珠网](http://www.rifchina.com/). 有比赛棋谱. 
- [VCF 习题 24 道](https://kdocs.cn/l/cqe9vsPGEdUs). 李洪斌分享的习题. 
- [連珠あれこれ](http://haisaresu.blog.fc2.com). 除了题目外还有少量文章
- [連 珠 コ ー ナ ー](http://www15.plala.or.jp/ssiio/renju.htm). 定石、次の一手問題集还不错.
- [連珠雑記](https://renjuvarious.hatenablog.jp/). 日本棋手博客, 有不少实用习题讲解等. (2021/9/3)
- Gomoku quest. 上面有分类的 VCF 习题几千题, 尤其是白抓禁手的题, 还不错.
- [瑞星和棋大定式](https://www.bilibili.com/video/BV1n7411r7vJ), [金星和棋大定式](https://www.bilibili.com/video/BV1ua4y1Y7fr)
- 公众号 "微笑棋社" 山口规则定式讲解.
- 公众号 "广东五子棋" 上有自战棋评看.

## 术语对应表

- 开局 - 珠型 (しゅけい)
- 活二 - 連
- 跳三 - トビ三
- 眠三 - 剣先. 我还看到过有把两个冲四点叫做剣先的.
- 活四 - 達四 (たつし) - open four
- fork: 组合棋型, 包括四四 (double four / 4x4 Fork), 三三, 四三等
- 长连 - overline
- 禁手 - forbidden/disallowed moves
- 平局 - 満局 (まんきょく)
- 定式 - 定石 (じょうせき)
- 做杀 - ミセ手 (て)
- 连续冲四 - 四追い
- 做 V (下一手 VCF) - フクミ手. 最後の黒の防ぎ手が禁手になる白のフクミ手を、特に **ネライ手** と呼ぶことがあります。連珠では黒に禁手を打たざるを得ない状況にする (**ハメル** と言います) のも白の立派な作戦です。需要注意的是 VCF 包括四三杀.
- 进攻 (活三及以上级别的攻击) - 追い手: 三を作る (**ヒク**) 手・四を作る (**ノビル**) 手・ミセ手・フクミ手の総称。VCT 的 T 代表 threats, 进攻手段, 即活三, 冲四, 做 V.
- 连攻取胜 / 追胜 - 追詰 (おいづめ) / 追勝ち (おいがち)
- 牵制手 - ノリ手: 追い手となる防ぎ手、または相手の四追い中に四ができる防ぎ手。可以反先的防守, 以及面对 VCF 可以反四的防点.
- 做棋 (大概意思是做连接, 拓展棋型的着) - 呼手 (こしゅ): 追い手でない攻めの手。
- [Game dictionary](http://www.vcpr.cz/en/help-and-rules/game-dictionary/). *VCPR*.
- [VC2](http://587.renju.org.tw/teach/teach023.htm).

## 杂项

- 传奇人物: [中村茂](https://www.zhihu.com/question/26880463/answer/34450158). 当时无意间查了日本名人战的记录, 结果被他的成绩震惊了, 中学生名人, 霸榜了过半的名人战. 2020 年名人战卫冕成功.
- 无禁无交换规则下 11 路棋盘的必胜 1 不在天元, 见 [人类对棋牌类游戏的拆解到了什么地步?](https://www.zhihu.com/question/36972545/answer/69816408), 棋谱演示见 [这里](https://www.bilibili.com/video/BV1xJ41187Mh).
- 开局名称来源 
    - [珠型名の由来](http://renju.jp/db/dictionary/syukei/). *東京連珠会*.
    - 第40期名人・山口釉水. (2007, Sep 27). [珠型名の由来・平成版](http://table28.renju.info/PageVisitor/Essay/NicknameOfOpenings.php).
    - [七桂, 七间, 七连](http://www.ljrenju.com/croom/history/7g7j7l.htm). *励精连珠教室*. 倒是可以帮助记忆, 只有七间是星, 其他都是月. (2020/11/23)
    
## 游戏现状

除非成年前 (或者本科) 赢过大比赛 (有段者, 意味着很多精力投入而且达到了一定水平), 否则对成人而言就是 **纯粹的图一乐游戏**. 因为学习成本很高, 而又不能对工作/经济带来回报, 还没有什么社交价值 (没人玩, 英美那边更是没人, 所以英语资料稀缺).

小朋友比赛最多, 大学生还有一点点, 毕业后普通成人爱好者一年能参加的线下赛大约只有两个: 当地等级赛和智运会, 并且一些地方的等级赛不欢迎成人 (而且成人参加也没有意义). 价格更是不菲, 上海等级赛 130, 浙江宁波 200. 据称 200 是正常价格, 上海因为人多才能摊到 130.

学棋的主力是小朋友, 尤其是幼儿园和小学生. 小学才开始学的话一开始输给幼儿园还会带来心理压力. 在主力是小朋友, 成人没有动机 (除了有段者) 玩的现状下, 群众基础其实很糟糕.

## 参考文献

- [連珠とは](http://tokai-renjukai.pya.jp/info/Renju.html). *東海連珠会*.
- [連珠基本ルール](http://matsurenju.game.coocan.jp/kihon_rule.htm). *連珠苦楽部*.
- [What is Renju?](https://www.renju.net/study/rules.php). *RenjuNet*.
- ハイサレス. (2015, Oct 29). [連珠における形勢判断～連と剣先～](http://haisaresu.blog.fc2.com/blog-entry-97.html)[Blog post].