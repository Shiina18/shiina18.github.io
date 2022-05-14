---
title: "深度学习吐槽杂录"
categories: 
- Machine Learning
updated:
comments: true
mathjax: false
---

都是老生常谈的问题. 吐槽外还包含哪些事情有意义. 主要内容看原文链接.

<!-- more -->

## 一般深度学习

神经网络黑箱的意思是我们知其然, 不知其所以然, 相关理论比较缺乏. 别看神经网络相关论文汗牛充栋, 但是大部分类似于 technical report, 告诉你我这么做效果不错, 具体原因不知道, 只能 "guess", 所以很容易被打脸.

- mileistone. (2018, Jun 30). [为什么都说神经网络是个黑箱?](https://www.zhihu.com/question/263672028/answer/430179912). *知乎*.
    - Ali Rahimi. (2018, Jan 25). [Lessons from Optics, The Other Deep Learning](http://www.argmin.net/2018/01/25/optics/). *argmin blog*.

---

一是算力飞涨, 大规模数据训练成为可能, 对于当下一些 AI 任务, 网络不区分任务特性, 只要给了合理的监督和学习目标函数, 网络就能自动学到高效的模型.

二是现在学术界的氛围已经很奇怪了. 杂糅乱七八糟的 trick, 争先恐后地在各种 task 上移植, 黑箱调参灌水成风.

- 付聪Ben. (2018, Mar 20). [为什么都说神经网络是个黑箱?](https://www.zhihu.com/question/263672028/answer/345883835). *知乎*.

---

> 但是许多研究生都发 DL 方向的 paper, 这是为什么?
>
> 因为 DL 确实能 work, 只要它能 work, 你管它能不能被 explain.
>
> 我不知道为什么加 dropout, 我不知道为什么加 BN, 但是我就是要搜一些博客上的解释, 然后生搬硬套到我的论文上.

- Cherrise. (2022, Feb 12). [我确实在DL上没有天赋](https://zhuanlan.zhihu.com/p/466568642). *知乎*.

---

很多工作在 gnn 之前有个更通俗易懂的名字, 叫网络连连看 (为了避免误伤需要说明一下, 这里主要指低级的, 没有多少道理的连连看, 毕竟广义上讲resNet 也是, 相信大家有鉴定两种连连看区别的水平), 实质是一回事.

- 孙天祥. (2021, Apr 10). [图神经网络如何在自然语言处理中应用?](https://www.zhihu.com/question/330103469/answer/1827458619). *知乎*.

## (深度) 强化学习

DRL 成功的关键离不开一个好的奖励函数 (reward function), 然而这种奖励函数往往很难设计.

不稳定性. 不同的超参和随机种子下的表现天壤之别, 可以完全不 work.

- Frankenstein. (2018, Feb 25). [这里有一篇深度强化学习劝退文](https://zhuanlan.zhihu.com/p/33936457). *知乎*.
    - Alex Irpan. (2018, Feb 14). [Deep Reinforcement Learning Doesn't Work Yet](https://www.alexirpan.com/2018/02/14/rl-hard.html). *Sorta Insightful*.

---

数据收集过程不可控, 玄之又玄, 可解释性较差. 本来 Q-learning 就是一个通过逐步学习来完善当前动作对未来收益影响作出估计的过程. 加入 DNN后, 还涉及到了神经网络近似 Q 的训练. 这就是 "不靠谱" 上又套了一层 "不靠谱".

攻城狮子. (2021, Mar 10). [为什么说强化学习在近年不会被广泛应用?](https://www.zhihu.com/question/404471029/answer/1755948468). *知乎*.

## 应用场景

研究型岗位还可以, 虽然被咔嚓的例子很多, 但至少有点盼头, 实在没卷过, 往业务型兼容也有机会; 太偏应用或者业务的就算了, 尤其是纯分类任务的场景 (比如审核), 容易被替.

- 知乎问题: [NLP 现在就业是否没有前途?](https://www.zhihu.com/question/363740740)

用 RL 做 NLP. 坑上加坑了属于是.

- 阿柴. (2019, Apr 11). [当前机器学习中有哪些研究方向特别的坑?](https://www.zhihu.com/question/299068775/answer/647698748). *知乎*.

推荐系统/计算广告. 现在就是工业界能看到一堆问题但是没人去做, 学术界找不到问题开始制造问题不管是否有实际应用意义.

- 周国睿. (2019, Apr 8). [当前机器学习中有哪些研究方向特别的坑?](https://www.zhihu.com/question/299068775/answer/644809803). *知乎*.

> cv难的地方主要包含创新算法，模型底层加速和部署。前者就是各种大佬，既能够提出好的idea，又能够解决实现idea的各种问题，刚开始idea不一定work需要不断调整，另外很多东西没有现成的轮子需要自己实现。因此理论能力和工程能力都要具备。后者一般来说c++要够熟练，工程能力尤其是解决bug的能力要强，有些时候还要自己从底层写op，需要熟悉不同平台的指令优化等，这个过程同样需要强的理论功底来加快运算速度。这两方面的大佬真正的核心竞争力就是理论功底加工程能力，只不过不大重叠，不可替代性强。

- 匿名用户. (2020, Dec 2). [为什么现在不看好 CV 方向了呢?](https://www.zhihu.com/question/383486199/answer/1606619221). *知乎*.

> 没有意义。我一直都认为nlp工程岗位没有前途，nlp只适合做research。学nlp的同学，如果毕业之后想去到工业界，建议要么做nlp的research，要么转去做推荐 or 广告。普通的nlp工程岗位是最烂的岗位，没有之一，毫无意义。

- Berkeley. (2021). [NLP 常规任务用 bert 类模型几行代码就能解决, 那 NLP 岗主要存在的价值是什么?](https://www.zhihu.com/question/462802557/answer/2036794468).

其他

- 纳米酱. (2020, Jul 8). [算法工程师当前选哪个方向好?](https://www.zhihu.com/question/398876586/answer/1325455486). *知乎*.