---
title: "Super Egg Drop"
categories: Mathematics
updated: 
comments: true
mathjax: true
---

> You are given $k$ eggs, and you have access to a building with $N$ floors from $1$ to $N$.
> 
> Each egg is identical in function, and if an egg breaks, you cannot drop it again.
> 
> You know that there exists a floor $F$ with $0 \le F \le N$ such that any egg dropped at a floor higher than $F$ will break, and any egg dropped at or below floor $F$ will not break.
> 
> Each move, you may take an egg (if you have an unbroken one) and drop it from any floor $X$ (with $1 \le X \le N$). 
> 
> Your goal is to know with certainty what the value of $F$ is.
> 
> What is the minimum number of moves that you need to know with certainty what $F$ is, regardless of the initial value of $F$?

<!-- more -->

一道陈题. (事后查出来是 LeetCode 887)

## 100 层楼 2 个玻璃球

起因是窥室友手机屏, 看到他群里有人问一个经典问题.

> 两个一模一样的玻璃球, 两个玻璃球如果从一定高度掉落到地上会被摔碎, 如果在这个高度以下往下扔怎么都不会碎, 现在已知这个恰巧摔碎的高度范围在 1 层楼到 100 层楼之间, 如何用最少的试验次数, 用这两个玻璃球测试出玻璃球恰好摔碎的楼高呢?

题目的意思是只要玻璃球不碎, 那么它是不会受到损伤的, 即临界层数 (最低摔碎楼层) 不变. 给定一个策略 $S\colon \mathbb N \to \mathbb N$, $S(n)$ 表示临界层数为 $n$ 时, 该策略需要测试的次数, 则最少测试次数是指 $\displaystyle \min_S\max_n S(n)$.

当只剩 1 个球时, 只能一层一层往上测试. 第 1 个球的任务是减少第 2 个球所需测试的次数. 直观上讲, 第 1 个球测试点的间隔要越来越小, 这样第 2 个球所需测试次数少, 才能保证总次数一定.

记最少测试次数为 $m$, 即最优策略的最坏测试次数为 $m$. 若第 1 个球第 $j$ 次测试 (之前都没碎) 在 $n_j$ 层下落

- 没碎, 则 $j+1$ 次测试时, 问题归结为求 $100 - n_j$ 层楼的最少试验次数.
- 摔碎, 则第 2 个球要在 $m-j$ 次内在 $n_j - n_{j-1} - 1$ 层楼中完成测试. 而第 2 个球 $m-j$ 次最多只能在 $m-j$ 层楼中定位临界层数.

因此 2 个球 $m$ 次测试最多可以在 $m + (m-1) + \dots + 1 = m(m+1)/2$ 层楼中定位临界层数. 最小测试次数即 $\min\\{ m\in\mathbb N \mid m(m+1)/2 \ge 100 \\} = 14$. 策略并不唯一, 例如令 $n_j = m + (m-1) + \dots + (m-j+1)$, 其中 $j\le 11$.

## $N$ 层楼 $k$ 个玻璃球

一个很自然的问题是, 若有 $k$ 个玻璃球, 求在 $N$ 层楼中定位临界层数需要的最少测试次数. 类似上题, 考虑 $k$ 个球 $m$ 次测试最多能在 $f(k, m)$ 层楼中定位临界层数. 若第 1 个球第 1 次测试在 $n_1$ 层下落

- 没碎, 则剩下 $k$ 个球, $m-1$ 次机会, 至多还可以在上面的 $f(k, m-1)$ 层楼中定位临界层数.
- 摔碎, 则剩下 $k-1$ 个球, $m-1$ 次机会, 至多还可以在下面的 $f(k-1, m-1)$ 层楼中定位临界层数.

因此 

$$
f(k, m) = f(k, m-1) + 1 + f(k-1, m-1), $$

边界条件 $f(0, m) = f(k, 0) = 0$, 或者说 $f(1,m) = m$, $f(k,1) = 1$.

这个形式让人很自然地想起了 (广义) 组合数的递推式

$$
\frac{m(m-1)\cdots (m-n+1)}{n!}=\begin{pmatrix}m\\n\end{pmatrix} = \begin{pmatrix}m-1\\n\end{pmatrix} + \begin{pmatrix}m-1\\n-1\end{pmatrix}.
$$

所以要想办法把递推式中的 1 去掉. First attempt 是记 $g(k,m) = f(k, m) + 1$, 但是这样边界条件不对. 尝试 $g(k,m) = f(k,m) - f(k,m-1)$ 边界条件也不对. 记 $g(k,m) = f(k,m) - f(k-1,m)$, 则

$$
g(k,m) = g(k, m-1) + g(k-1, m-1),
$$

这次边界条件对了, $g(1,m) = m$,  $g(1,1) = 1$,  $g(k,1) = 0$ for $k>1$. 易知

$$
f(k,m) = \sum_{x=1}^k g(x,m) + f(0,m) = \sum_{x=1}^k\begin{pmatrix}m\\x\end{pmatrix}.
$$

于是 $k$ 个球 $N$ 层楼, 最少测试次数是 $\min\\{m \mid f(k,m) \ge N\\}$.

```python
class Solution:
    def superEggDrop(self, k: int, N: int) -> int:
        
        def f_k(m):  
        # if f(k, m) >= N, return True; else False
            result = 0
            c = 1
            for x in range(1, k+1):
                c = c * (m-x+1) / x  # combinatorial number C_m^x
                result += c  # f(x, m)
                if result >= N:
                    return True
            return False
        
        # binary search
        left, right = 1, N
        while left < right:
            mid = (left + right) // 2
            if f_k(mid):
                right = mid
            else:
                left = mid + 1
        return left
```

算法时间复杂度 $O(k\log N)$, 空间复杂度 $O(1)$.
