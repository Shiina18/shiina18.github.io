---
title: "词权重求和背后的假设"
categories: 
- Machine Learning
updated: 
comments: true
mathjax: true
---

来自 BM25 专著

- Robertson, S., & Zaragoza, H. (2009). *[The probabilistic relevance framework: BM25 and beyond](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)*. Now Publishers Inc.

其中的第一部分介绍词 (term) 权重求和的背后假设. 这里的 "词" 可以指各种粒度.

<!-- more -->

首先假设 query 和某个 doc (文档, document) 之间的相关性只和那个 doc 有关系, 并且是 01 变量. 给定 query 求出其与各个 doc 相关的概率并进行排序. 下面说明在一定假设下, $p(r \mid d, q)$ 的概率排序与

$$
\sum_{q, f_i > 0} w_i
$$ 

词权重求和得到的相同, 其中 $d$ 表示 doc, $q$ 表示 query, $r$ 为表示是否相关的 01 变量, 中间是左边的简记, 右边的记号之后介绍. 记号 $p(x \mid y)$ 理解为 $\mathbb P(X = x \mid Y = y)$, 涉及的随机变量都可以从上下文推断出.

**保持概率排序**

因为只看概率排序, 所以可以对概率作一个保持排序不变的变换 (单调递增函数), 因此只要考虑

$$
\begin{align}
\frac{p(r \mid d, q)}{p(\bar r \mid d, q)} = \frac{p(d \mid r, q) p (r \mid q)}{p(d \mid \bar r, q) p(\bar r \mid q)},
\end{align}
$$

其中 $\bar r = 1 - r$. 由于右边式子上下第二项和 doc 无关, 所以可以再做个单调变换, 只要考虑

$$
\begin{align}
\frac{p(d \mid r, q)}{p(d \mid \bar r, q)}.
\end{align}
$$

**假设词之间的条件独立性**

记一个 doc 为

$$
d = (f_1, \dots, f_{\vert V\vert}),
$$

其中 $V$ 代表全体词的集合 (词典, vocabulary), $\vert V\vert$ 表示集合元素个数, $f_i$ 表示第 $i$ 个词在该 doc 中的词频 (可以 01 也可以是出现次数等). 于是得到

$$
\begin{align}
\prod_{i\in V}\frac{p(f_i \mid r, q)}{p(f_i \mid \bar r, q)}.
\end{align}
$$

虽然这个假设不太现实, 但是 Naive Bayes 也是这么做的, 而且效果不错. 文章 argue 这是一个不太差的假设.

**假设没有出现在 query 中的词没有贡献**

记

$$
q = (q_1, \dots, q_{|V|}),
$$

出现在 query 中的词的索引记为 $\mathcal Q = \\{ i \mid q_i > 0 \\}$. 因此得到

$$
\begin{align}
\prod_{i\in \mathcal Q}\frac{p(f_i \mid r, q)}{p(f_i \mid \bar r, q)}.
\end{align}
$$

做个保排序的变换

$$
\begin{align}
\sum_{i\in \mathcal Q}\log\frac{p(f_i \mid r, q)}{p(f_i \mid \bar r, q)}.
\end{align}
$$

**词权重求和**

记 

$$
U_i(f_i) = \log\frac{p(f_i \mid r, q)}{p(f_i \mid \bar r, q)},
$$

再简记 $\sum_{\mathcal Q} U_i := \sum_{i\in\mathcal Q} U_i$, 可得

$$
\begin{align}
&\sum_{\mathcal Q} U_i(f_i) \nonumber \\
= & \sum_{\mathcal Q, f_i > 0} U_i(f_i) + \sum_{\mathcal Q, f_i = 0} U_i(0) \nonumber \\
& + \sum_{\mathcal Q, f_i > 0} U_i(0) - \sum_{\mathcal Q, f_i > 0} U_i(0) \nonumber \\
= & \sum_{\mathcal Q, f_i > 0} (U_i(f_i) - U_i(0)) + \sum_{\mathcal Q} U_i (0),
\end{align}
$$

由于第二项和 doc 无关, 所以去掉也不影响概率排序. 最后记词权重

$$
\begin{align}
w_i(f_i) &= U_i(f_i) - U_i(0) \\
&= \log\frac{p(f_i\mid r) p(0\mid \bar r)}{p(f_i\mid \bar r) p(0\mid \bar r)}. \nonumber
\end{align}
$$

这里重点在于所有东西都可以事先算好存起来.

**BM25**

TFIDF 以及 BM25 和各种变体都是赋予不同的词权重加权平均. 其中 BM25 的最简介介绍可以看 [wiki](https://en.wikipedia.org/wiki/Okapi_BM25); gensim 实现的 BM25 代码参考 3.8.3 版本 (4.0 开始就没了) 的 [这个](https://github.com/RaRe-Technologies/gensim/blob/release-3.8.3/gensim/summarization/bm25.py), 一个文件内实现的简单清晰的逻辑, 使用注意事项也在代码注释里.