---
title: "Bootstrap 失效的一个例子"
categories: Statistics
updated: 
comments: true
mathjax: true
---

假设 $Y_1, \dots, Y_n$ 独立同分布, 服从 $[0,\theta]$ 上的均匀分布. 则其似然函数为

$$
L(\theta|Y_1, \dots, Y_n) = \frac{1}{\theta^n} \prod_{k=1}^n 1_{\{ 0\le Y_k\le \theta \}}.
$$

<!-- more -->

由于 $L$ 关于 $\theta$ 单调递减, 故 $\theta$ 的极大似然估计为 $T := \hat\theta = \max\\{Y_1, \dots, Y_n\\} = Y_{(n)}$. 对一次观测 $\omega$, 观测值为 $y_k = Y_k(\omega)$, 这 $n$ 个观测值决定的经验分布函数记为 $\hat F_n$. 考虑非参数重采样, 即随机变量 $Y_1^\ast, \dots, Y_n^\ast$ 独立同分布, 服从经验分布 $\hat F_n$. 我们想要估计 $Q = n(\theta - T)/\theta$, 其分布为

\begin{align*}
\mathbb{P}(Q\le x) 
&= \mathbb{P}\left( T\ge \theta \left( 1-\frac{x}{n} \right) \right) \\
&= 1 - 0 \vee \left( 1-\frac{x}{n} \right)^n \wedge 1 \\
&\to 1 - e^{-x} \wedge 1,
\end{align*}

故其极限分布为标准指数分布. 按照一般的非参数重采样方法, 我们取 $Q^\ast = n(t - T^\ast)/t$, 其中 $t = T(\omega)$ 即在这组样本下的估计值, $T^\ast = Y^\ast_{(n)}$ 是 $n$ 个自助法样本的最大值. 然而

\begin{align*}
\mathbb{P}_{\hat F_n}(Q^\star = 0) 
&= \mathbb{P}_{\hat F_n}(T^\star = t) \\
&= 1 - \left(1-\frac1n \right)^n \\
&\to 1 - e^{-1}.
\end{align*}

因此 $Q^\ast$ 的极限分布不可能是标准指数分布, 从而自助法不适用.

这个例子来自 Davison, A. C., & Hinkley, D. V. (1997). *Bootstrap methods and their application* (Vol. 1). Cambridge university press. p. 39. 保证自助法有效的条件比较 technical, 可参考该书 pp. 38-39, 或者其他相关书籍.