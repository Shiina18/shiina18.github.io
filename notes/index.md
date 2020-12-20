---
title: "Notes"
layout: page
comments: true
mathjax: false
---

Last Updated on 2020-12-19

虽说标题写着 notes, 但其实内容基本没有正儿八经的 notes, 只是一些杂乱物品的堆放. 只有作者自己公开的材料会被列在这里. (2019/9/29)

## Notes

- 2020/6/4 [Solutions to Selected Problems in Time Series
Analysis](https://shiina18.github.io/assets/docs/Solutions%20to%20Selected%20Problems%20in%20Time%20Series%20Analysis.pdf)

This document contains solutions to selected problems in Brockwell, P. J., Davis, R. A., and Fienberg, S. E. (1991). *Time series: theory and methods*. Springer Science & Business Media.

- [Reading lists on probability](https://www.zhihu.com/question/60288185/answer/1634006267)

~~虽然我也什么都还没入门就跑路了~~. (2020/12/19)

- [CS224n: Natural Language Processing with Deep Learning @Stanford](http://web.stanford.edu/class/cs224n/)

很著名的课了. 大概是 19 年的时候看的, 回顾一下发现还是这里的 notes 写得好. 尤其是开头几个 notes (w2v 等), 其他网上的 notes 要么跳过细节, 要么语焉不详. (2020/8/16)

- [Author and Reviewer Tutorials](https://www.springer.com/cn/authors-editors/authorandreviewertutorials)

Springer 上的作者和审稿人教程, 非常棒. 有中文版. ~~施普林格, 永远的神.~~ (2020/6/11)

- [User guide: contents — scikit-learn 0.23.1 documentation](https://scikit-learn.org/stable/user_guide.html)

Sklearn 的用户指南, 有些 topic 其实写得特别好, 比如 [GBDT](https://scikit-learn.org/stable/modules/ensemble.html#gradient-tree-boosting). (2020/6/10)

- [2DI70 - Statistical Learning Theory Lecture Notes](https://www.win.tue.nl/~rmcastro/2DI70/files/2DI70_Lecture_Notes.pdf)

Fengnan Gao 老师在 2017 Fall Statistical Learning 用过这个讲义, 主要讲 PAC learning, VC dimension 等理论, 不太涉及具体模型. 原以为是不公开的讲义, 结果轻易搜到了 [出处](https://www.win.tue.nl/~rmcastro/2DI70/). 本来 Gao 的 syllabus 非常 ambitious, 用的材料也不是这个, 但后来考虑到只是本科课程, 就换了这个简单的讲义, 不过有点太简单了. 

- [随机分析引论](http://homepage.fudan.edu.cn/jgying/files/2011/06/%E9%9A%8F%E6%9C%BA%E5%88%86%E6%9E%90%E5%BC%95%E8%AE%BA2015-6.pdf)

精简易读, 以很少的前置知识介绍了随机分析最主干的内容, 路线比较自然, typo 不少 (不过一般都容易自己看出来). GTM274: *Brownian Motion, Martingales, and Stochastic Calculus* by Le Gall (他是 19 年的 Wolf 数学奖得主) 的主体框架也和这个讲义相似, 非常友好, 比 GTM113: *Brownian Motion and Stochastic Calculus* by Shreve 友好多了.

## Snippets

- [Pearson's chi-square test](http://personal.psu.edu/drh20/asymp/fall2006/lectures/ANGELchpt07.pdf)

A test of goodness of fit for multinomial distribution 证明速查. "This course is required for all second-year PhD students in statistics." 有空的时候想把整个讲义看一看. (2020/6/10)

- [The exponential family: Basics](https://people.eecs.berkeley.edu/~jordan/courses/260-spring10/other-readings/chapter8.pdf)

写得比较清楚的 quick reference, 不过 typo 挺多的 (而且 TeX 只编译了一遍导致 ref 没有编译出来). (2020/1/14)

- [Limiting distribution for a Markov chain](http://www.columbia.edu/~ks20/stochastic-I/stochastic-I-MCII.pdf)

Every irreducible Markov chain with a finite state space is positive recurrent and thus has a stationary distribution. 随便找的一个内容很少的 quick reference, see also[「为什么有限状态马氏链不存在零常返状态？」](https://www.zhihu.com/question/361982166/answer/943474143). (2019/12/20)

- [Differentiation Under the Integral Sign](https://planetmath.org/differentiationundertheintegralsign)

积分与求导交换的几种条件简单小结. (2019/12/10)

## Books

- [神经网络与深度学习](https://nndl.github.io/)

邱锡鹏老师的书. 数学推导写得清楚, 这点好评. 

- [Probability: Theory and Examples](https://services.math.duke.edu/~rtd/)

非常有名的 Durrett 的 PTE, 展示了很多有趣的例子, 鞅只讲了离散鞅, 有时候我要翻倒向鞅的结论时会翻这本. 另外 Durrett 的主页给我印象最深的是, 专门有个 "my smiling face" 的链接. 世图引进的白色封面的第 3 版比较常见, 习题答案也可以找到.

- [The Elements of Statistical Learning](https://web.stanford.edu/~hastie/ElemStatLearn/)

The well-known ESL. 确实不太容易读.

## Recreation

- [Trailing the dovetail shuffle to its lair](https://projecteuclid.org/download/pdf_1/euclid.aoap/1177005705)

17 年的时候看到的一篇讲洗牌的文章, 另外还有一篇解读 [HOW MANY TIMES SHOULD YOU SHUFFLE A DECK OF CARDS?](https://www.dartmouth.edu/~chance/teaching_aids/Mann.pdf). (2020/2/12)

以及 Diaconis 的后续文章 [The cutoff phenomenon in finite Markov chains](https://www.pnas.org/content/pnas/93/4/1659.full.pdf). (2020/2/28)

- [平均需要多少个人才有相同的生日的渐近问题推广](https://www.zhihu.com/question/367513670)

渐近分析. (2020/1/23)

- [N Points On Sphere all in One Hemisphere](https://mathpages.com/home/kmath327/kmath327.htm)

起因是看到 "圆内 4 个鸭子在同一个半圆的概率" 那个问题, 然后在想推广到任意有限维空间, 看到 Wendel 做过这个. 该链接是在问题 [Probability that n points on a circle are in one semicircle](https://math.stackexchange.com/questions/325141/probability-that-n-points-on-a-circle-are-in-one-semicircle) 的评论区中找到的. (2020/1/9)

- [圆周上均匀分布的 n 个点互相连线可将圆分为多少块?](https://www.zhihu.com/question/67970620/answer/259170402)

记得以前作业有道题好像就是这个, 十分凶残, 考试也考了这个. 不过参考答案只是给了个简单的 bound 而已.

- [How to Share a Secret](https://cs.jhu.edu/~sdoshi/crypto/papers/shamirturing.pdf) by Adi Shamir

作者是 RSA 算法的 S.

- [耶鲁大学公开课: 博弈论](http://open.163.com/special/gametheory/)

由于是公选课, 所以涉及的数学很浅. 以前有一段时间需要坐长地铁, 于是就拿这个当消遣品, 只看了前几节课, 内容还算有趣. [原始课程主页](https://oyc.yale.edu/economics/econ-159).

## Non-Mathematical

- [二十四条逻辑谬误](https://zhuanlan.zhihu.com/p/19837940)

便携. (2020/2/1)

- [暨南大学公开课: 民法与生活](https://open.163.com/newview/movie/free?pid=MEFDHUS6H&mid=MEFDJIAH0)

一点通识知识. 每个视频都很短, 带有案例讲解, 很方便观看. 不过中间缺了几个视频, 有些遗憾. (2019/12/25)