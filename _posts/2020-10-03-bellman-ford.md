---
title: "Bellman-Ford Algorithm"
categories: Algorithms
updated:
comments: true
mathjax: true
---

解决带负权重的单源最短路径问题.

给定一个带权有向图 $G = (V, E)$, 其中 $V$ 为顶点 (vertex) 集, $E$ 为边 (edge) 集, 从顶点 $u$ 到 $v$ 的边表示为 tuple $(u, v)$; 权重 (weight) 函数 $w\colon E \to \mathbb R$. 一个路径 $p=\langle v_0, v_1, \dots, v_k \rangle$ 的权重为

$$
w(p) = \sum_{i=1}^k w(v_{i-1}, v_i).
$$

<!-- more -->

从 $u$ 到 $v$ 的最短 (权重最小) 路径权重记为

$$
\delta(u, v) = 
\begin{cases}
\min\{ w(p) : u \xrightarrow{p} v\} & \text{若存在从 $u$ 到 $v$ 的路径,}\\
\infty & \text{otherwise.}
\end{cases}
$$

其中 $u \xrightarrow{p} v$ 表示从 $u$ 到 $v$ 的路径 $p$. 于是自然地, 从 $u$ 到 $v$ 的最短路径就是权重为 $\delta(u, v)$ 的任意路径. 很显然, 从最短路径中取两个顶点, 子路径依然是这两个顶点的最短路径. 如果存在一个环, 其路径权重为负, 显然我们可以无数次通过此环来减少权重, 所以可以经过这个环的最短路径权重都为 $-\infty$. 

## Relaxation

考虑单源的最短路径问题. 对每个顶点 $v$ 维护一个属性 $v.d$, 为从源 (source) $s$ 到 $v$ 的最短路径权重的上界估计; 用 $v.p$ 来记录估计的路径的前一个顶点. 所谓松弛, 就是让这个上界趋于上确界. 

```python
def initialize_single_source(G, s):
    for v in G.V:
        v.d = float('inf')
        v.p = None
    s.d = 0

def relax(u, v, w):
    if v.d > u.d + w(u, v):
        v.d = u.d + w(u, v)
        v.p = u
```

## Bellman-Ford algorithm

```python
def bellman_ford(G, w, s):
    initialize_single_source(G, s)
    # v.d becomes delta(s, v) 
    # after the following loop
    for _ in range(len(G.V)-1):
        for (u, v) in G.E:
            relax(u, v, w)
    # Return True if there is 
    # a negative-weight cycle
    for (u, v) in G.E:
        if v.d > u.d + w(u, v):
            return False
    return True
```

显然时间复杂度是 $\Theta(\vert V \vert \vert E \vert)$. 

### Path-relaxation property

考虑一条最短路径 $p=\langle v_0, v_1, \dots, v_k \rangle$, 如果在一系列松弛过程中 (中间可以穿插其他松弛过程), $(v_0, v_1)$, $\dots$, $(v_{k-1}, v_k)$ 依次被松弛, 则 $v_k.d = \delta(s, v_k)$.

用归纳法证明. 初始是 $s$ 没问题. 若 $v_i.d = \delta(s, v_i)$, 那么再对 $(v_i, v_{i+1})$ 松弛有 $v_{i+1}.d = \delta(s, v_{i+1})$ (回忆松弛的定义以及最短路径的子路径依然是最短路径).

### Correctness of the Bellman-Ford algorithm

假设没有负环, 最短路径不必包含环, 因此至多有 $\vert V\vert -1$ 条边. 于是, Bellman-Ford 算法跑完第一小段循环后, 由 path-relaxation property 所有顶点的最短路径估计都收敛到了真正的最短路径权重. 

假设有负环 $c = \langle v_0, v_1, \dots, v_k \rangle$, 其中 $v_0 = v_k$, 则

$$
\sum_{i=1}^k w(v_{i-1}, v_i) < 0.
$$

用反证法, 假设 $v_i.d \le v_{i-1}.d + w(v_{i-1}, v_i)$, 则

$$
\sum_{i=1}^k v_i.d \le \sum_{i=1}^k (v_{i-1}.d + w(v_{i-1}, v_i)),
$$

注意到 $v_0 = v_k$, 右边第一项求和等于左边, 于是环路权重非负, 矛盾.

有一个优化一些的算法, 略. 对于每个顶点对的最短路径问题, 可以循环跑 Bellman-Ford 算法, 当然也有更好的算法, 有待更新.

**Ref**

Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). *Introduction to algorithms*. MIT press. pp. 643-676.