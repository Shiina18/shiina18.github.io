---
title: "Intro to Facebook Prophet"
categories: 
- Machine Learning
updated:
comments: true
mathjax: true
---

主要介绍 Facebook 的 [Prophet: Forecasting at Scale](https://facebook.github.io/prophet/). 包含了翻译, 转述, 和我自己的理解. 

<!-- more -->

## Introduction

> The analysts responsible for data science tasks throughout an organization typically have deep domain expertise about the specific products or services that they support, but often do not have training in time series forecasting.

Prophet 的 motivation 就是让具有领域知识但缺乏时间序列训练的人能更方便地进行预测. 使用传统方法, 如 ARIMA 等, 需要分析员理解模型假设的时间序列性质, 再有针对性地调整参数. 而 Prophet 的设计目标是, 使用者可以不知道模型的细节, 但依然能直观地调参.

标题中的 at scale 是指

> Simple, adjustable models and scalable performance monitoring in combination allow a large number of analysts to forecast a large number and a variety of time series.

主要用于商业领域的时间序列分析.

## The Prophet Forecasting Model

把时间序列 $y(t)$ 分解为三部分,

$$
y(t) = g(t) + s(t) + h(t) + \varepsilon_t,
$$

其中 $g(t)$, $s(t)$, $h(t)$ 分别表示 trend, seasonality, and holidays; 而 $\varepsilon_t$ 代表模型没有捕捉到的独特特征, 下面假设它服从正态分布.

> We are, in effect, framing the forecasting problem as a curve-fitting exercise, which is inherently different from time series models that explicitly account for the temporal dependence structure in the data. 

Prophet 放弃了 ARIMA 这类生成式模型的良好 inference 性质, 换来的是以下优势

- 灵活性: 可以轻易地建模多个周期的 seasonality, 并且对 trends 做出不同的假设.
- Unlike with ARIMA models, the measurements do not need to be regularly spaced, and we do not need to interpolate missing values e.g. from removing outliers. (暂时不知道为什么可以这样.)
- 拟合速度快.
- 参数含义直观.

总得来说是一个广义线性模型, 然后用 Bayes 方法得到最大后验估计.

### The Trend Model

两个模型: a saturating growth model, and a piecewise linear model.

#### Nonlinear, Saturating Growth

大家都知道人口/种群增长曲线通常被假设为 Logistic 曲线 (S 型曲线, sigmoid 曲线). 逻辑是, 环境资源有限, 不能让生物无限制地繁殖, capacity 是种群数量上限. 当种群数量接近环境 capacity 时, 它的增长速率会减缓, 称为达到饱和.

以 Facebook 为例, 某地区脸书用户的 capacity 就是当地通网的群众. 模仿 logistic 函数, trend 项写成下式

$$
g(t) = \frac{C(t)}{1+\exp(-k(t-m))},
$$

其中 $C(t)$ 表示随时间变化的 capacity, 而 $k$ 是增长率, $m$ 是一个偏移参数. 

Note: 论文这个写法有点歧义, 上式的 $k$ 是一个常数, 而不是函数, $k(t-m)$ 是一个常数乘 $(t-m)$.

这里 $C(t)$ 是一个重要的参数, 分析员可以通过业务理解自行设置.

增长率是可能改变的, 比如出了新产品. 处理方式是在模型中加入 changpoints, 在这些点上增长率可能改变. 假设有 $S$ 个变点分别在时间点 $t_1$, $\dots$, $t_S$ 上. 在每个变点, 增长率的变化为 $\delta_j$. 记初始增长率为 $k$, 于是在时间 $t$ 时的增长率为 $k+\sum_{j\colon t>s_j} \delta_j$. 而为了让曲线连续, 偏移 $m$ 要做对应的调整使得曲线在变点上不会断开.

#### Linear Trend

如果没有 capacity, 那么可以假设为分段线性模型

$$
g(t) = kt + m,
$$

其中 $k$ 和 $m$ 都可以加入变点调整.

吐槽: 如果没有 capacity, 种群增长一般应当是指数增长. 

#### Automatic Changepoint Selection

变点可以手动设置也可以全自动. 自动设置是对增长率变化 $\delta$ 假设了稀疏先验 Laplace 分布.

脸书通常会设置大量变点, 然后假设 $\delta_j \sim \text{Laplace}(0, \tau)$, 参数 $\tau$ 控制了增长率变化的频繁程度, $\tau$ 越大, 越容易过拟合, 得到的置信区间越大.

#### Trend Forecast Uncertainty

主要是通过生成式模型来做的. 根据历史估计出变点大小, 采样出变点, 如此 simulate 多个 trends, 最后得到 "置信" 区间. 很 Bayes 的方法.

假设历史数据有 $T$ 个点, 包含 $S$ 个变点. 变点大小的估计可以通过纯 Bayes 的框架, 但这里用的是 MLE $\lambda = (1/S) \sum_j \vert\delta_j \vert$.

Future changepoints are randomly sampled in such a way that the average frequency of changepoints matches that in the history: 对于任意 $j > T$,

$$
\begin{cases}
\delta_{t_j} \sim \text{Laplace}(0, \lambda), & \text{w.p. $S/T$} ,\\
\delta_{t_j} = 0, & \text{otherwise}.
\end{cases}
$$

Note: 这里原文写的是 $\delta_j$, 符号和之前的重复, 比较迷惑. 按照意思, 应该是第 $j$ 个时间点, 有 $S/T$ 的概率成为变点, 其大小服从 Laplace 分布.

Side Note: 具体实现要看源码中的 `forecaster.py` 的 `sample_predictive_trend` 函数. 源码中变点位置是通过 Poisson 过程采样得到的, 最终结果依然是未来变点出现的频率和历史相似.

```python
# New changepoints from a Poisson process with rate S on [1, T]
if T > 1:
    S = len(self.changepoints_t)
    n_changes = np.random.poisson(S * (T - 1))
else:
    n_changes = 0
if n_changes > 0:
    changepoint_ts_new = 1 + np.random.rand(n_changes) * (T - 1)
    changepoint_ts_new.sort()
else:
    changepoint_ts_new = []

# Get the empirical scale of the deltas, plus epsilon to avoid NaNs.
lambda_ = np.mean(np.abs(deltas)) + 1e-8

# Sample deltas
deltas_new = np.random.laplace(0, lambda_, n_changes)
```

we use this generative model to simulate possible future trends and use the simulated trends to compute uncertainty intervals.

> The assumption that the trend will continue to change with the same frequency and magnitude as it has in the history is fairly strong, so we do not expect the uncertainty intervals to have exact coverage.

### Seasonality

商业时间序列通常有多种周期的 seasonality (比如周, 月, 年). 主要通过 Fouries 级数建模, 假设周期为 $P$, 则

$$
s(t) = \sum_{n=1}^N \left( a_n\cos\left(\frac{2\pi nt}{P}\right) + b_n\sin\left(\frac{2\pi nt}{P}\right) \right).
$$

需要 $2N$ 个参数 $a_1$, $b_1$, $\dots$, $a_n$, $b_n$, 并且假设它们服从联合正态分布先验 $\text{N}(0, \sigma^2)$, 其中 $\sigma$ 是可调参数.

增加 $N$ 会让 seasonality 变化更频繁, 增大过拟合风险. 对于年周期 (365.25) 和周周期 (7), 脸书发现 $N$ 分别为 10 和 3 时可以应对大部分问题. 参数选择可以通过 AIC 等准则判断.

### Holidays and Events

Incorporating this list of holidays into the model is made straightforward by assuming that the effects of holidays are independent.

$$
h(t) = \sum_i\kappa_i 1_{\{\text{$t$ 在节日 $i$ 的时段}\}}.
$$

其中 $\kappa$ 也是服从联合正态先验 $\text{N}(0, \nu^2)$, 其中 $\nu$ 是可调参数.

## Automating Evaluation of Forecasts

### Modeling Forecast Accuracy

Forecasts are made over a certain *horizon*, which we denote $H$. The horizon is the number of days in the future we care about forecasting - this is typically 30, 90, 180, or 365 days in our applications. 这里 horizon 指要预测未来多少天.

选定了 loss function (原文用的是度量函数, 但明显可以不用局限于此) 之后, 我们通过模拟或者直接计算得到 loss 的期望. 记 loss function 为 $d$, 记 $h\in (0, H]$, 令 $\hat y(t \vert T)$ 表示根据时间 $T$ 及以前的观测值得到的 $t$ 时刻的预测值, 再引入一个记号

$$
\phi(T, h) = d(\hat y(T+h \vert T), y(T+h)).
$$

> Unfortunately these approaches only give correct estimates of error conditional on having specified the correct model for the process - a condition that is unlikely to hold in practice.

脸书倾向的方案是在不同的 $h$ 下得到期望误差,

$$
\xi(h) = \mathbb E(\phi(T,h)).
$$

我们可以加一些简单的假设.

- 函数应该在 $h$ 处局部光滑, 因为我们期望在邻近天数内的预测误差应该差不多.
- 函数关于 $h$ 应该是缓慢上升的. 这个假设并不普适.

### Simulated Historical Forecasts

简单地说是在历史数据中取 $K$ 个截点, 在这些截点处, 用以前的数据进行预测, 最后把误差求和.

- 如果截点取得过多, 那么误差估计会 highly correlated. 极端情况下对每个时间点, 都用直到这个时间点之前的数据进行预测. 那么由于训练集只多了一个样本点, 最终的预测可能不会相差太多, 导致误差和以前一天之前为历史做预测的误差几乎相等, highly correlated. 截点取太多还会拖慢运行速度, 但是截点取太少的话也不行, 一个经验法则是每隔 $H/2$ 时间就取截点做一次预测.
- 另一个问题是使用的数据多并不保证能得到更好的结果. 如果模型假设错误, 并且过拟合, 那么预测结果可能会更差.

When the SHF error for a method increases sharply from one cutoff to the next, it could indicate that the data generating process has changed. Adding changepoints or modeling different phases separately may address the issue.

论文基本讲完了, 后续实例待写.