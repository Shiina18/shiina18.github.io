---
title: "Lights-Out"
categories: Mathematics
updated: 
comments: true
mathjax: true
---

> Each employee of MegaCorp has a separate office in the MegaCorp office building. Each office is equipped with one overhead light and one toggle switch to turn the light on and off.
>
> Every day, the employees turn on all lights when they come to work. Each evening they turn off all lights when they go home.
>
> One day, the employees arrive to discover that someone has played a rather elaborate hoax on them. Though all looks fine when they come in (all lights are off), every time an employee flicks the switch in her office, this not only toggles the light in her office, but also the lights in the offices of all of her friends. (Friendship is a symmetric relationship.)
> 
> The question: does there necessarily exist an arrangement of the switches that will turn all lights simultaneously on (so that work can begin)? Prove your answer.

<!-- more -->

这个问题是半年前在知乎的 "有哪些有趣的线性代数习题?" 问题下的 [一个回答](https://www.zhihu.com/question/54835038/answer/141326311) 中看到的. 搜到了原题出处, [Using your Head is Permitted](https://www.brand.site.co.il/riddles/201103q.html), 一个十分有趣的网站, 可惜多年前就停更了.

把开记为 1, 关记为 0, 下面在 2 元域 $\mathbb F_2=\\{0,1\\}$ 下考虑. 如果你不知道 2 元域, 那么只要考虑 1 + 1 = 0, 其余加法和乘法运算的形式和实数域上相同 (事实上, XOR 就是 2 元域上的加法).

设有 $n$ 位员工, 第 $k$ 号员工的开关对应列向量 $\alpha_k=(a_{1k},\dots,a_{nk})'$, 其中 $a_{jk}=1$ 意为他的开关与第 $j$ 号员工的灯泡相连, $a_{kk}=1$. 所以我们要找 $x = (x_1,\dots,x_n)'\in\mathbb F_2^n$, 其中 $x_k=1$ 表示第 $k$ 号员工按下开关, 使得 $\sum_{k=1}^n x_k \alpha_k=(1,\dots,1)'$. 记 $A=(\alpha_1,\dots,\alpha_n)$, 我们要求 $Ax = (1,\dots,1)'$. 

事实上, 可以证明更一般的结论, 在 $\mathbb F_2$ 下, 对任意对称阵 $A=(a_{ij})$, 记 $b=(a_{11},\dots,a_{nn})'$, 则存在 $x$, 使得 $Ax=b$.

**证明**. 要证 $b\in \operatorname{Ran} A = \operatorname{Ran} A' = (\operatorname{Ker} A)^\bot$. 即对任意 $x\in\operatorname{Ker} A$, 成立 $x'b = \sum_i x_i a_{ii}=0$.

事实上,

$$
\begin{align*}
x'Ax &= \sum_{i,j} x_i a_{ij} x_j\\\\
&=\sum_i x_i^2 a_{ii} + \sum_{i<j} (x_i a_{ij} x_j + x_j a_{ji} x_i)\\\\
&=\sum_i x_i a_{ii}.
\end{align*}
$$

即得. $\square$

注:

- 2 元域条件不能去掉. 考虑 

$$
A = \begin{pmatrix}1 & c \\ c & c^2\end{pmatrix}.
$$

- 矩阵对称条件不能去掉. 考虑 

$$
A = \begin{pmatrix}0 & 1 \\ 0 & 1\end{pmatrix}.
$$

- $b$ 不能是任意向量. 考虑

$$
A = \begin{pmatrix}1 & 1 \\ 1 & 1\end{pmatrix}, b = \begin{pmatrix}0 \\ 1\end{pmatrix}.
$$

P.S. 写完后查了查, 才发现 Matrix67 也写过这道题, [链接](http://www.matrix67.com/blog/archives/4263).