---
title: "编程题杂录"
categories: Algorithms
updated: 2020-07-19
comments: true
mathjax: true
---

<!-- more -->

## LeetCode 847. Shortest Path Visiting All Nodes

2020/7/19

广度优先搜索. 

一个 trick 是可以用二进制数表示访问过的节点, 1 表示访问过, 0 表示未访问过. 比如一共 5 个节点 (0-indexed), 则可以用 11001 表示访问过节点 0, 3, 4. 位运算 `1<<n` 比 `2**n` 快得多.

```python
from collections import deque

class Solution:
    def shortestPathLength(self, graph: List[List[int]]) -> int:
        '''
        binary representation
        e.g. 11001 for nodes 034 visited and 12 unvisited
        '''
        goal = (1<<len(graph)) - 1
        # (curr_node, visited_nodes, steps)
        queue = deque((node, 1<<node, 0) for node in range(len(graph)))
        seen = set()
        while queue:
            curr_node, visited_nodes, steps = queue.popleft()
            if visited_nodes == goal:
                return steps
            for adj_node in graph[curr_node]:
                state = (adj_node, visited_nodes | 1<<adj_node, steps+1)
                if state not in seen:
                    seen.add(state)
                    queue.append(state) 
        return -1
```

## 外卖小哥的保温箱

没看到这道题的题解, 自己写一遍. 

众所周知, 美团外卖的口号是: "美团外卖,送啥都快". 身着黄色工作服的骑手作为外卖业务中商家和客户的重要纽带, 在工作中, 以快速送餐突出业务能力; 工作之余, 他们会通过玩智力游戏消遣闲暇时光, 以反应速度彰显智慧, 每位骑手拿出装有货物的保温箱, 参赛选手需在最短的时间内用最少的保温箱将货物装好.

我们把问题简单描述一下:

1. 每个货物占用空间都一模一样;
2. 外卖小哥保温箱的最大容量是不一样的, 每个保温箱由两个值描述: 保温箱的最大容量 $b_i$, 当前已有货物个数 $a_i$, 其中 $a_i \le b_i$;
3. 货物转移的时候, 不必一次性全部转移, 每转移一件货物需要花费 1 秒的时间.

输入描述:

1. 第一行包含 $n$ 个正整数 ($1\le n \le 100$) 表示保温箱的数量;
2. 第二行有 $n$ 个正整数 $a_1, a_2,\dots, a_n$,  其中 $a_i$ 表示第 $i$ 个保温箱的已有货物个数, $1\le a_i \le 100$;
3. 第三行有 $n$ 个正整数 $b_1, b_2, \dots, b_n$,  其中 $b_i$ 表示第 $i$ 个保温箱的最大容量, $1\le b_i \le 100$.

输出描述:

输出为两个整数 $k$ 和 $t$, 其中 $k$ 表示能容纳所有货物的保温箱的最少个数, $t$ 表示将所有货物转移到这 $k$ 个保温箱所花费的最少时间, 单位为秒.

输入例子 1:

```
4 
3 3 4 3
4 7 6 5
```

输出例子 1: 2 6

例子说明 1:

我们可以把第一个保温箱中的货物全部挪到第二个保温箱中, 花费时间为 3 秒, 此时第二个保温箱剩余容量为 1, 然后把第四个保温箱中的货物转移一份到第二个保温箱中, 转移最后两份到第三个保温箱中. 总花费时间也是 3 秒, 所以最少保温箱个数是 2, 最少花费时间为 6 秒.

输入例子 2:

```
2 
1 1
100 100
```

输出例子 2: 1 1

输入例子3:

```
5 
10 30 5 6 24
10 41 7 8 24
```

输出例子 3: 3 11

### 题解

题目稍微有些模糊, 意思是首先确保保温箱数目最少, 然后在这个前提下用时最少. 

由于总物品数是一定的, 用时最少等价于选用的保温箱中已有物品数最多. 很明显是 01 背包问题的变形.

记 $f(i, j) = (k_{i,j}, t_{i,j})$ 为在前 $i$ 个保温箱中选出若干个使得总容量为 $j$ 时, 所用的最少保温箱数, 和在最少箱数前提下的最大物品数.

- 若 $k_{i,j} > k_{i-1, j-b_i}+1$, 则说明选用第 $i$ 个保温箱后所需箱数更少, 于是 $t_{i,j} = t_{i-1, j-b_i} + a_i$.
- 若 $k_{i,j} = k_{i-1, j-b_i}+1$, 则所用保温箱数相同, 比较已有物品数, 取  $t_{i,j} = \max\{t_{t-1, j}, t_{i-1, j-b_i} + a_i\}$.
- 否则选用第 $i$ 个保温箱后所需箱数更多, 不考虑.

空间可以优化为 $O(\sum_{i=1}^n b_i)$, 对每个 $i$ 对 $j$ 进行遍历时, 为了避免覆盖 $i-1$ 时的值, $j$ 需要倒过来遍历.

时间为 $O(n\sum_{i=1}^n b_i)$.


```python
import sys
n = int(input().strip())
lines = sys.stdin.readlines()
# since there is something wrong with the input
if len(lines) == 1:
    temp = list(map(int, lines[0].strip().split()))
    a = temp[:n]
    b = temp[n:]
else:
    a = list(map(int, lines[0].strip().split()))
    b = list(map(int, lines[1].strip().split()))

n_items = sum(a)
total_cap = sum(b)
f = [[float('inf'), 0] for _ in range(total_cap+1)]
f[0] = [0, 0]
for i in range(n):
    for j in range(total_cap, b[i]-1, -1):
        if f[j][0] > f[j-b[i]][0] + 1:
            f[j] = [f[j-b[i]][0] + 1, f[j-b[i]][1] + a[i]]
        elif f[j][0] == f[j-b[i]][0] + 1:
            f[j][1] = max(f[j][1], f[j-b[i]][1] + a[i])
res = [float('inf'), 0]
for j in range(n_items, total_cap+1):
    if f[j][0] < res[0]:
        res = f[j]
    elif f[j][0] == res[0]:
        res[1] = max(res[1], f[j][1])
print(res[0], n_items-res[1])
```

## 取数

来源: [2020-3-29 百度编程题](https://blog.csdn.net/Calotte_Lin/article/details/105188172)

首先给出 $n$ 个数字 $a_1, a_2,\dots, a_n$, 然后给你 $m$ 个回合, 每回合你可以 (笔者注: 如果是 "必须" 的话更简单些) 从中选择一个数取走它, 剩下来的每个数字 $a_i$ 都要减去一个值 $b_i$. 如此重复 $m$ 个回合, 所有你拿走的数字之和就是你所得到的分数. 

现在给定你 $a$ 序列和 $b$ 序列, 请你求出最多可以得到多少分. 

输入描述:

1. 输入第一行, 仅包含一个整数 $n$, 表示数字的个数. 
2. 第二行, 一个整数 $m$, 表示回合数. 
3. 接下来一行有 $n$ 个正整数, 分别为 $a_1, a_2,\dots, a_n$. 
4. 最后一行有 $n$ 个正整数, 分别为 $b_1, b_2,\dots, b_n$. 

输出描述:

输出一个仅包含一个正整数, 即最多可以得到的分数.


输入例子: 

```
5
5
10 10 30 40 50
4 5 6 7 8
```

输出：100

(笔者注: 从输出来看, 输入应该是 10 20 30 40 50, 并且之前的笔者注应该是 "必须")

### 题解

题目不是官方来源, 所以可能有误, 按照上面的笔者注来做.

在决定好最后取哪些数之后, 显然 $b_i$ 值大的数要先取. 于是这还是一个背包问题, 关键是先对 $b_i$ 从大到小排序.

记 $f(i,j)$ 为在前 $i$ 个数中取 $j$ 个, 得分的最大值.

递推关系为 $f(i,j) = \max\{f(i-1, j), f(i-1, j-1) + a_i -(j-1)b_i \}$.

```python
def score(a, b, m):
    a = list(zip(a, b))
    a.sort(key=lambda x: -x[1])
    f = [0 for _ in range(m+1)]
    for i in range(len(a)):
        for j in range(min(m, i+1), 0, -1):
            f[j] = max(f[j], f[j-1] + a[i][0] - (j-1)*a[i][1])
        print(i, f)
    return f[-1]

a = [10, 20, 30, 40, 50]
b = [4, 5, 6, 7, 8]
m = 5
print(score(a, b, m))
'''
0 [0, 50, 0, 0, 0, 0]
1 [0, 50, 83, 0, 0, 0]
2 [0, 50, 83, 101, 0, 0]
3 [0, 50, 83, 101, 106, 0]
4 [0, 50, 83, 101, 106, 100]
100
'''
```

时间 $O(nm)$, 空间 $O(m)$.

若题目由 "必须" 取数改为 "可以" 取数, 最后改为 `return max(f)` 即可.



## LeetCode 547. Friend Circles

最直接的想法, 朴素地迭代求并集效率太低了, [并查集](https://zhuanlan.zhihu.com/p/93647900) 是一个更高效的实现. 想法是用代表元表示一个朋友圈, 用树结构表示朋友圈, 根节点为代表元. 对于每个人, 查找根节点就可以得知其所在的朋友圈. 为了降低树的高度需要对父节点做一些优化.

```python
class Solution:
    def find(self, x):
        if self.a[x] == x:
            return x
        else:
            self.a[x] = self.find(self.a[x])
            return self.a[x]
    
    def findCircleNum(self, M):
        self.a = [i for i in range(len(M))]
        for i, ui in enumerate(M):
            for j, rij in enumerate(ui[i+1:], i+1):
                if rij:
                    self.a[self.find(j)] = self.find(i)
        return len(set(self.find(i) for i in self.a))
```

另一种办法是深度优先搜索.

```python
class Solution:
    def findCircleNum(self, M):
        res = 0
        seen = set()
        
        def dfs(i):
            for j, rij in enumerate(M[i]):
                if rij and j not in seen:
                    seen.add(j)
                    dfs(j)
        
        for i in range(len(M)):
            if i not in seen:
                dfs(i)
                res += 1
        return res
```