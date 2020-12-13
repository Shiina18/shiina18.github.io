---
title: "从零开始的五子棋学习"
categories: Games
tags: Renju
updated: 2020-12-12
comments: true
mathjax: false
---

一个习惯的叫法是, 无禁手的称为 "五目" (gomoku), 有禁手的称为 "连珠" (renju). 比如一手交换, swap 2 这种都属于 gomoku.

<!-- more -->

## 预想路线

1. 三手胜, 花浦定式
2. 其他开局定式
3. 平衡开局和其他现代规则

作为业余随便玩玩的, 能完成第一步我就满足了. 花浦定式其实还是挺不容易的.

五子棋总体来说是一个小众且入门门槛不低的棋类, 相比其他棋类用时短, 攻防激烈.

## 书

- 曾杨锋. (2013). [五子棋零基础自学一本通 (第三版)](https://shiina18.github.io/assets/docs/五子棋零基础自学一本通.pdf). *百度五子棋贴吧*.
- 坂田吾朗. (2000). 三手胜五子棋题解. 人民体育出版社.

三手胜的题目构造真的很巧妙.

### 准备阅读

- 真野芳久五段. (2015, Jun). [連珠の基礎](http://tokai-renjukai.pya.jp/siryo/RenjuKiso/RenjuKiso-1-2.pdf). *東海連珠会*. 另附 [超链接版](http://tokai-renjukai.pya.jp/siryo/RenjuSiryo.html). (2020/12/12)

### 资料留存

- Nosovsky, A. & Sokolsky, A. (1999). [Renju for beginners (new revised edition)](https://renju.se/rif/nosovsky/renjuforbeginners.pdf).
- [連珠の本の案内](http://www15.plala.or.jp/ssiio/renjubook.htm)

## 软件

- 线上博弈平台. 五林大会: 自带人机模式, 专业, 主创团队为高段选手.
- 打谱. 通用操作: delete 键删除当前分枝. Ctrl+鼠标左键在棋盘上标注文字.
    - [renlib](https://www.renju.se/renlib/): 国外软件, 很容易找, 解题引擎用的就是 renju solver.
    - 乐赛五子棋打谱软件: 国人温向东开发, UI 漂亮, 功能强大. 收费软件. 作者是 Temple 大学的数学 PhD, 以前的爱五子棋打谱软件, 以及连珠终结者 (Renju Solver) 都是他写的. 作者本人其实只是初学者水平.
    - [蜗牛连珠](https://www.wind23.com/gomokuai.html): 手机 app. 主要好处是支持无禁手 AI 计算. 作者郝天一, 五子棋四段, 清华姚班, CS PhD. (2020/11/23)
    - [弈心](https://www.aiexp.info/pages/yixin.html): 作者孙锴, 上交 CS 本, Cornell CS PhD. 在 katago 和 embryo 出现前是无敌的 AI, 支持各种规则. (2020/12/7)

## 网上资源

### 特别推荐

- B 站 up 主:
    - [卖丶菜](https://space.bilibili.com/28742590). 几个最强开局的定式讲解.
- 河村典彦九段. [河村九段の連珠講座](http://www.kyogo.org/contents/kouza.html). *京都連珠会*. 初心者向.
- [励精连珠教室](http://www.ljrenju.com/index.htm). 国内很多网站都十分老旧, 这是难得的更新勤快的网站, 有用的资料也很多. 目前我都是在这里查定式的, 虽然可能资料有点老. (2020/11/9)
- [587 连珠](http://587.renju.org.tw/). 一个很好的台湾教学网站, 有交互式棋盘, 以及实用的资源整合. 有一定难度. 后来才知道作者是台湾顶尖棋手林書玄. (2020/12/7)

### 其他资源

- B 站 up 主:
    - [连珠之魂](https://space.bilibili.com/135341585/). 兰志仁, 专业六段.
    - [乐赛丶](https://space.bilibili.com/291338278/). 专业三段, 年轻的比赛讲解员.
- 五子剑. (2009, Jun 29). [五子剑系列讲座](http://www.wuzi8.com/xiti/HTML/1752.html). *中国五子棋网*.
- 温顺的瓜皮猫. (2020, Jun 3). [五子棋中, 先手下棋到底有多大的优势?](https://www.zhihu.com/question/267273167/answer/323472412). *知乎*. 主要是提到了一些弈心的资料.
- 叉色-xsir. (2019, Mar 11). [一个非常硬核的五子棋资料站](https://zhuanlan.zhihu.com/p/51846364). *知乎*.  Ando 的连珠教室的一些资料.
- 松浦浩七段. [連珠苦楽部](http://matsurenju.game.coocan.jp/). 包括用习题的方式讲解定式.
- 那智暴虐のれんじゅいし. (2018, Aug 10). [【連珠】入門、初心者の方が最初に覚える形について自分なりに考察した【五目並べ】](https://www.youtube.com/watch?v=J1kmzW9A95U). *YouTube*.
    - 容易取胜的形状: 不推荐初学者花浦, 推荐溪峡. 形状互通, 黑八卦不容易输.
    - 想记住手筋: 云雨. 互通, 手筋型的进攻多, 但是很难, 有背诵价值.
    - 想打持久战: 疏流.
    - 各种规则都适用 (?): 丘斜.
- [无禁必胜网页版](https://www.bytedance.ai/gomoku.html). (2020/11/9)
- [日本連珠社](https://www.renjusha.net/). 有许多河村九段的研究资料. (2020/11/14)
- [中国连珠网](http://www.rifchina.com/). 有比赛棋谱. (2020/11/14)
- [RenjuNews](http://renjunews.com/). 有一些棋评. (2020/12/7)
- [★魚丸湯の闇黑五子棋學院★](https://blog.xuite.net/jang20529659/twblog1). 台湾棋手楊裕雄三段的博客, 有很多教学文章. (2020/12/12)

## 术语对应表

未完待续

- 开局 - 珠型 (しゅけい)
- 活二 - 連
- 跳三 - トビ三
- 眠三 - 剣先
- 活四 - 達四 (たつし) - open four
- fork: 组合棋型, 包括四四 (double four / 4x4 Fork), 三三, 四三等
- 长连 - overline
- 禁手 - forbidden/disallowed moves
- 平局 - 満局 (まんきょく)
- 定式 - 定石 (じょうせき)
- 做杀 - ミセ手 (て)
- 连续冲四 - 四追い
- 做 V (下一手 VCF) - フクミ手. 最後の黒の防ぎ手が禁手になる白のフクミ手を、特に **ネライ手** と呼ぶことがあります。連珠では黒に禁手を打たざるを得ない状況にする (**ハメル** と言います) のも白の立派な作戦です。
- 进攻 (活三及以上级别的攻击) - 追い手: 三を作る (**ヒク**) 手・四を作る (**ノビル**) 手・ミセ手・フクミ手の総称。
- 连攻取胜 / 追胜 - 追詰 (おいづめ) / 追勝ち (おいがち)
- 牵制手 - ノリ手: 追い手となる防ぎ手、または相手の四追い中に四ができる防ぎ手。可以反先的防守, 以及面对 VCF 可以反四的防点.
- 做棋 (大概意思是做连接, 拓展棋型的着) - 呼手 (こしゅ): 追い手でない攻めの手。
- [Game dictionary](http://www.vcpr.cz/en/help-and-rules/game-dictionary/). *VCPR*.
- 需要注意的是 VCF 包括四三杀; VCT 的 T 代表 threats, 进攻手段, 即活三, 冲四, 做 V.
- [VC2](http://587.renju.org.tw/teach/teach023.htm). (2020/12/7)

## 杂项

- 传奇人物: [中村茂](https://www.zhihu.com/question/26880463/answer/34450158). 当时是无意间查了日本名人战的记录, 结果被他的成绩震惊了, 中学生名人, 霸榜了过半的名人战. 2020 年名人战卫冕成功.
- 开局名称来源 
    - [珠型名の由来](http://renju.jp/db/dictionary/syukei/). *東京連珠会*.
    - 第40期名人・山口釉水. (2007, Sep 27). [珠型名の由来・平成版](http://table28.renju.info/PageVisitor/Essay/NicknameOfOpenings.php).
    - [七桂, 七间, 七连](http://www.ljrenju.com/croom/history/7g7j7l.htm). *励精连珠教室*. 倒是可以帮助记忆, 只有七间是星, 其他都是月. (2020/11/23)

## 参考文献

- [連珠とは](http://tokai-renjukai.pya.jp/info/Renju.html). *東海連珠会*.
- [連珠基本ルール](http://matsurenju.game.coocan.jp/kihon_rule.htm). *連珠苦楽部*.
- [What is Renju?](https://www.renju.net/study/rules.php). *RenjuNet*.
- ハイサレス. (2015, Oct 29). [連珠における形勢判断～連と剣先～](http://haisaresu.blog.fc2.com/blog-entry-97.html)[Blog post].