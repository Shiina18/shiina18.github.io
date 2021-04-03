---
title: "宝可梦对战入门资料集"
categories: Games
updated: 2021-03-21
comments: true
mathjax: true
---

仅仅是一些材料的堆砌, 包括 Pokémon Showdown 上的 66 单打 (gen7) 以及更习见的 VGC 64 双打. 

- Gen 8 变动
    - [Opinion: 10 Mechanics Changes for Pokémon Sword and Shield](https://www.trainertower.com/opinion-10-mechanics-changes-for-pokemon-sword-and-shield/)
    - [Pokémon Sword and Shield – New Competitive Features and Mechanic Changes](https://www.trainertower.com/pokemon-sword-and-shield-new-competitive-features-and-mechanic-changes/)
- 百科
    - [神奇宝贝百科](https://wiki.52poke.com/wiki/%E4%B8%BB%E9%A1%B5)
    - [口袋百科](http://www.pokemon.name/wiki/%E9%A6%96%E9%A1%B5)
<!-- more -->
- 66 单打
    - [66 对战基础教程](https://yiqixie.com/d/home/fcABLqhwPAERgUsMg00zSXVNz)
    - [66 单打进阶](https://zhuanlan.zhihu.com/p/34888897) (需要一定基础)
    - [66 单打教学 replay 分析](https://www.bilibili.com/video/av20160557) (需要一定基础, 这个系列一共 3 个视频), [G8 一则 replay 分析](https://www.bilibili.com/video/av80472994) (2019/12/24)
    - 构筑范例: 超爆破队 ([译文](https://tieba.baidu.com/p/5492625848?red_tag=3467346667)/[原文](https://www.smogon.com/forums/threads/usum-psyspam-offense-peaked-1-by-btb-ayevon-2100-elo.3623157/))
- 64 双打
    - [【翻译】【入门必读】VGC 综合介绍](https://tieba.baidu.com/p/6025225272)
    - [バルドルのなみのり日記](http://barudoru.hatenablog.com/) twitter@barudoru, 其中有一篇双打入门 [ポケモンダブルバトル入門](https://barudoru.hatenablog.com/entry/2017/02/25/170142) ([译文](https://tieba.baidu.com/p/4989084112?red_tag=0546073896))
    - [Double Battle Primer](https://www.smogon.com/dp/articles/double_battles)
    - [カ・エールのぶろぐ](http://hiromoti.hatenablog.com/) twitter@hirosipoke
- Pokémon Showdown
    - [Pokémon Showdown](https://pokemonshowdown.com/)
    - [宝可梦分析](https://www.smogon.com/dex/ss/pokemon/) (这是我看得最多的板块了)
    - 官方论坛 [Smogon](https://www.smogon.com/forums/). 资源丰富, 例如 Metagames 板块的 [资源](https://www.smogon.com/forums/forums/overused.387/?prefix_id=181) 等
- 贴吧
    - [smogon 吧](https://tieba.baidu.com/f?kw=smogon&ie=utf-8&tp=0)
    - [pokemonshowdown 吧](https://tieba.baidu.com/f?kw=pokemonshowdown)
    - [开朗斗笠菇吧](https://tieba.baidu.com/f?kw=%E5%BC%80%E6%9C%97%E6%96%97%E7%AC%A0%E8%8F%87&ie=utf-8&tab=main)
- APP
    - 口袋对战宝典
    - 口袋图鉴
-  其他
    - [为什么口袋妖怪世界锦标赛没有单打](https://www.zhihu.com/question/24985569/answer/81853292?tdsourcetag=s_pcqq_aiomsg)
    - [关于 66 单打](https://www.zhihu.com/question/49561076/answer/117070939) (看 14-1)
    - 宝可梦对战史: 知乎专栏 [大小姐的游戏随笔](https://zhuanlan.zhihu.com/c_29687970). 了解恶系, 钢系, 妖系引入的历史因素可以更好地记忆属性相克表...吧. 专栏里还有几次 wcs 的解说, 非常有意思.
    - B 站上的 [PM 发展史](https://www.bilibili.com/video/av23225621) 系列. 虽然不是讲对战的, 但也很有意思.
    - B 站上艾尔十六的 [宝可梦特别篇漫画解说](https://www.bilibili.com/video/BV1tK4y1C7Sd). 虽然也和对战无关, 但是特别篇漫画真的好看, 现在已经做到了宝石篇. (2020/3/25)
- 杂项
    - 关于国内的一些术语. 「先读」来自日语「先読み」, 意为预测. 「确1」也是来自日本那边的表达「確定1」, 意思同英语 OHKO. Smogon 有提供 [词汇表](https://www.smogon.com/dp/articles/pokemon_dictionary).
    - 另外, 好像是来自日本的习惯, 把 HP 简写为 H, 物攻物防特攻特防依次为 ABCD, 速度为 S.
    - 对英文名有疑惑的话, 可以看看百科底下给的词源.
    - 为什么宝可梦只能带 6 个: [Finding Comfortable Settings of Video Games: using Game Refinement Measure in Pokemon Battle AI](https://www.researchgate.net/publication/309476022_Finding_Comfortable_Settings_of_Video_Games_using_Game_Refinement_Measure_in_Pokemon_Battle_AI)
    - 伤害计算: 主要是用 [Pokémon Damage Calculator](https://pokemonshowdown.com/damagecalc/), 下面是从百科化简而来的计算公式.

100 级, 满个体, 种族值记为 $b$, 努力值记为 $e$. 其中 $[x]$ 为不大于 $x$ 的最大整数 (即向下取整). $[e/4]$ 最大为 63.

$$
\begin{align*}
\text{HP} &= 2b + 141 + [e/4]\\
\text{最大 HP} &= 2b + 204\\
\text{其他能力值} &= \left[(2b + 36 + [e/4])\times\text{性格修正}\right]\\
\text{最大其他能力值} &= \left[(2b + 99)\times 1.1\right]\\
\text{伤害} &= \left[\left[\frac{21}{25}\frac{\text{攻击}}{\text{防御}}\times\text{技能威力} + 2\right]\times\text{加成}\right]
\end{align*}
$$

加成左边那一坨称为基础伤害.  
加成 = 属性一致 × 属性相克 × 击中要害 × 其他 × 随机数.  
随机数取自 $\\{0.85, 0.86,\dots, 1\\}$ 的 16 个数, 均匀分布.

例. 极速满特攻的 Mega 胡地内战.  
HP, 特攻, 特防, 速度种族值分别为 55, 175, 105, 150.  
则实际值为 251, 449, 246, 438.  
用 shadow ball 对攻的基础伤害为 124, 算上加成为 210-248, 不能 OHKO.

- Pachirisu 名场面
    - 三千院凪. (2019, Mar 15). [宝可梦对战史番外篇-复盘白色恶魔的奇迹](https://zhuanlan.zhihu.com/p/59312357). *知乎*.
    - 没吃药的Alan. (2017, Oct 18). [Pokemon WCS2014 白色恶魔封神战](https://www.bilibili.com/video/BV1Mx411M7pT). *bilibili*.
    
![source: https://www.pixiv.net/artworks/45464932](https://shiina18.github.io/assets/posts/images/20201219193935474_14482.png "source: https://www.pixiv.net/artworks/45464932")