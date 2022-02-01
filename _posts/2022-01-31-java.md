---
title: "Java 初体验: 线性回归系数的检验"
categories: Language
updated: 
comments: true
mathjax: true
---

与 Python 比较

- `new` 相当于在 Python 中显式地调用 `__init__` 方法.
- `import` 好像没有 Python 灵活, 比如 `a.b.c`, 只能导入 fully qualified name (一个具体的类) 或者一个库下所有的类, 而不能像 Python 一样 `from a import b` 然后再用 `b.c`.
- 没有默认参数 (可以用函数重载实现), 没有位置参数 (传参感觉不方便读 raw text?).
- 方法命名习惯用动词开头, camelCase.
- "only public methods are allowed to be called on class instance." [Why subclass in another package cannot access a protected method?](https://stackoverflow.com/questions/19949327/why-subclass-in-another-package-cannot-access-a-protected-method)

<!-- more -->

## 线性回归系数检验

Apache Commons Math 库的线性回归类没有直接实现各种假设检验. 考虑线性回归 (满足一般假设)

$$
y = X\beta + \varepsilon, \quad \varepsilon \sim N(0, \sigma^2 I).
$$

其中 $X$ 是 $n\times p$ 设计矩阵 (第一列全为 1), $\beta$ 是 $p\times 1$ 参数向量. 检验估计参数 $\hat \beta$ 的每一项,

$$
H_0\colon \beta_1 = \cdots = \beta_{p-1} = 0,
$$

其中 $\beta_0$ 为截距. 由于

$$
\hat \beta \sim N_p(\beta, \sigma^2 (X'X)^{-1}),
$$

如果 $\beta_i = 0$ 成立, 则 t-统计量

$$
\tau_i = \frac{\hat \beta_i}{\sqrt{c_{i, i}} \sqrt{u'u / (n-p)}} \sim t_{n-p},
$$

其中 $c_{i, i}$ 表示 $(X'X)^{-1}$ 的第 $i$ 行第 $i$ 列, 残差 $u = y- X\hat\beta$ (右下角这一坨是 $\hat \sigma$), 符号 $t_{n-p}$ 表示自由度为 $n-p$ 的 t 分布. 最后 $2\mathbb P(Z > \vert\tau_i\vert)$ 则为第 $i$ 项对应的 p-value, 其中随机变量 $Z \sim t_{n-p}$.

实现见 [这里](https://gist.github.com/Shiina18/844dcd880e5a377adc9880536f0d0563), 其中 Javadoc 的写法参考了官方文档风格, 用函数重载实现了类似默认参数的效果.


## 其他

Python 可以用 [JPype](https://jpype.readthedocs.io/en/latest/) 调 jar 包, 但是一个 [已知缺陷](https://jpype.readthedocs.io/en/latest/install.html#known-bugs-limitations) 是

> Because of lack of JVM support, you cannot shutdown the JVM and then restart it. Nor can you start more than one copy of the JVM.