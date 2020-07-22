---
title: "快速幂"
categories: Algorithms
updated: 
comments: true
mathjax: true
---

要求 $a^n$, 其中 $a\in\mathbb R$, $n\in\mathbb Z$. 先不妨假设 $n\ge 0$, 基本想法是

$$
a^n = \begin{cases}
a^{n/2}a^{n/2}, & \text{if $n$ is even,}\\
a^{(n-1)/2}a^{(n-1)/2}a, & \text{if $n$ is odd.}
\end{cases}
$$

很容易写出时间复杂度 $O(\log n)$ 的递归算法, 而要写迭代算法需要再想一想.

<!-- more -->

## 迭代

用二进制表示指数 $n = \sum_{j=0}^m b_j 2^j$, 其中 $b_j\in\\{0, 1\\}$, 则 $a^n = \prod_{j=0}^m a^{b_j 2^j}$. 

以 10 为例, 把它转化成二进制数.

$$
\begin{align*}
10 = b_3 2^3 + b_2 2^2 + b_1 2^1 + b_0 2^0,
\end{align*}
$$

由于 10 是偶数, 所以 $b_0 = 0$.

$$
\begin{align*}
10 = 2(b_3 2^2 + b_2 2^1 + b_1 2^0),
\end{align*}
$$

由于 10/2 是奇数, 所以 $b_1 = 1$.

$$
\begin{align*}
5 = 2(b_3 2^1 + b_2 2^0) + 1,
\end{align*}
$$

由于 (5-1)/2 是偶数, 所以 $b_2 = 0$.

$$
\begin{align*}
2 = 2(b_3 2^0),
\end{align*}
$$

由于 2/2 是奇数, 所以 $b_3=1$.

由此

```python
class Solution:
    def myPow(self, a: float, n: int) -> float:
        if n>= 0:
            res = 1
            while n:
                if n % 2:
                    res *= a
                n //= 2
                a *= a
            return res
        else:
            return 1/self.myPow(a, -n)
```

另外, Python 对小整数乘法有优化 (见 [这里](https://stackoverflow.com/questions/37053379/times-two-faster-than-bit-shift-for-python-3-x-integers)). 就 3.7 版本来说, 下面前两句时间一样, 后两句时间一样, 所以没有必要强行把代码写成位运算.

```python
for _ in range(int(1e8)):
    7777777 >> 1
    
for _ in range(int(1e8)):
    7777777 // 2

for _ in range(int(1e8)):
    7777777 & 1
    
for _ in range(int(1e8)):
    7777777 % 1
```

## 取模

若

$$
\begin{align*}
a &\equiv r_1 \pmod{p},\\
b &\equiv r_2 \pmod{p},
\end{align*}
$$

考虑 $a = k_1 p + r_1$, $b = k_2 p + r_2$, 其中 $k_1, k_2 \in \mathbb N$ 立即可以看出.

$$
\begin{align*}
ab &\equiv r_1r_2 \pmod{p}.
\end{align*}
$$

由此易知 $a^n$ 对 $p$ 取模的算法.