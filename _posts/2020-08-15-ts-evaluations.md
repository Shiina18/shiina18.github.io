---
title: "Some Evaluations for Time Series Forecasting"
categories: 
- Machine Learning
updated:
comments: true
mathjax: true
---

主要以两篇文章为主线, 串讲多个话题. 场景以零售销量预测为例.

<!-- more -->

## Metrics for Point Estimations

先来讲 [Hyndman and Koehler (2006)](https://d1wqtxts1xzle7.cloudfront.net/41379081/mase.pdf?1453428839=&response-content-disposition=inline%3B+filename%3DAnother_look_at_measures_of_forecast_acc.pdf&Expires=1597157569&Signature=VC56UUZ~g1N23-9yYISmvHWaarMNWA4AQBwkvR7DYXb8qakN8s6QygVHw4yg6AN8m9M21oHOX0SYs7tthAFegz1u7UGN9V8h4IIbZkHYv0RVsBEtuLWtBJGmuFJzohp8CsQDCkUZmGxV3awu3REXqIDCYoOyg3~GeW6h-fqCJXJSjAiPZTuZj4VTbis20p-T6YF1gPPEQHP-Og~JDkeq63id~PvIsX-PNMz3v2DmjX03fqXUDtPEONUI6QNmoRmI8I2l8q8SXLQGgHRs13~miE3ezMj9yjE6eRV5illWTtvmwoW2O59NG9eOwZ2deMf-hP5isFoPHAeULzupXXk-hg__&Key-Pair-Id=APKAJLOHF5GGSLRBV4ZA) Another look at measures of forecast accuracy, 引用数非常高. 这是在沃尔玛于 Kaggle 上组织的比赛 [M5 Forecasting: Estimate the unit sales and the uncertainty distribution of Walmart retail goods](https://www.kaggle.com/c/m5-forecasting-accuracy) 上看到的. 比赛分为两个 track, 分别需要预测零售数据的销量和置信区间. 官方给出的 [M5 Participants Guide](https://mofc.unic.ac.cy/m5-competition/) 包含了挺有意思的信息.

### Popular Metrics

记时间序列为 $Y_t$, 点估计为 $\hat Y_t$, 误差为 $e_t = Y_t - \hat Y_t$. 历史有 $n$ 个时间点 $Y_1, \dots, Y_n$.

- MSE (mean squared error) and MAE (mean absolute error) are scale-dependent.
- 基于百分误差, 即 $e_t / Y_t$, 的指标. 比如 Mean Absolute Percentage Error (MAPE) = $\text{mean}(\vert e_t / Y_t\vert)$.
    - 当 $Y_t$ 为零或者接近零时会出问题. 这导致当时间序列经常出现零时, 不适合用这类指标. 也就不适合零售数据.
    - MAPE 对正误差的惩罚比对负误差小. Hyndman and Koehler 这一句说得有很迷惑并且方向反了, Makridakis (1993) 原文的意思其实是这样: 在 $t$ 时刻若真实值为 $a$, 预测值为 $b$, 误差 $e=a-b>0$; 而若真实值为 $b$, 预测值为 $a$, 则误差的绝对值相同, 但是 $e/a < e/b$, 前者的 MAPE 更小. 解决办法就是改造为 $e_t / (Y_t + \hat Y_t)$, 不过当 $Y_t$ 接近零时, 点估计往往也接近零, 两个接近零的数相除依然会有问题. 
- 误差和 benchmark 的误差 $e_t^\ast$ 相除, 即基于相对误差 $e_t / e_t^\ast$ 的指标. 但是依然会有问题, 比如当分子分母都是正态分布 (且独立) 时, 得到的是 Cauchy 分布, 不存在二阶矩.
- 相对指标, 比如 $\text{MAE}/\text{MAE}_b$, 带角标 $b$ 表示 baseline 模型的 MAE. 缺陷是我们需要若干个模型预测, 然后才能用这个比较.

比如 Facebook Prophet 的内置评估用的就是这些.

### Scaled Errors

Hyndman and Koehler 推荐的做法是采用 scaled errors. 分母部分相当于相对指标 baseline 取为 random walk, $\hat Y_t = Y_{t-1}$. 只有当 $Y_t$ 全部相等时, 分母才为零, 而这种情况可以很自然地排除.

以 M5 比赛为例, 记 forecasting horizon 为 $h$, 比如 28 (天), 也就是需要预测未来 28 天的数据. 选用的点估计的 loss 是 Root Mean Squared Scaled Error (RMSSE),

$$
\text{RMSSE} = \sqrt{
\frac{ \frac{1}{h} \sum_{t=n+1}^{n+h} (Y_t - \hat Y_t)^2}
{ \frac{1}{n-1} \sum_{t=2}^n (Y_t - Y_{t-1})^2}
}.
$$

冠军成绩为 0.52043 (RMSSE 的加权平均), 铜牌线 0.69934, 供参考.

类似地可以定义出其他的 scaled errors.

好处是这是 scale-independent, 即 $Y_t$ 和 $\hat Y_t$ 乘上同一个常数后指标不变, 因此适用于对多个不同 scale 的序列预测的场景.

## Evaluating Predictive Count Data Distributions

沃尔玛 M5 比赛的零售数据就是 counts 组成的, 恰好之前我看过不少关于 time series of counts 的文章. 一般而言, 计数时间序列处理的是非负整数 (counts) 且数值较小的时间序列, 若数值很大那么直接近似为连续值即可. 下面讲讲 Kolassa (2016) Evaluating predictive count data distributions in retail sales forecasting.

机器学习界通常更关注点估计, 所谓的 "预测能力", 但是这可能对计数时间序列并不合适. 预测分布可能是更需要的, 统计学界一般更关心这个, 所谓 "推断能力".

> For example, quantile forecasts are obviously necessary in supply chain forecasting for setting safety amounts, but also for scenario analyses in promotional or other forecasts.

事实上 M5 就有一个专门的预测分位数的 track, 不过参与度就少很多了.

> Count data pose specific challenges for error measures. In particular, minimizing common error measures does not necessarily lead to the "best" forecasting method for count data, especially for intermittent demand series. 

### Issues on MSE and MAE

众所周知, 期望可以最小化 MSE, 而中位数则可以最小化 MAE. 当数据分布对称时, 用这两个指标还行; 但是对于取值小的计数数列就不一样了. 

假设真实分布为 Poisson 分布, intensity rate 为 $\lambda < \log 2 \approx 0.693$, 则中位数为 0, 期望为 $\lambda$. 不论 $\lambda$ 是 0.01 还是 0.5, 0 都令 MAE 最小化. 事实上由于 Poisson 分布的中位数总是整数, 最小化 MAE 会天然地给出整数预测值, 而这通常 biased downward.

> Kolassa and Martin (2011) provide a very simple pedagogical illustration of a strictly positive discrete symmetric distribution with an explicit biased E(M)APE-optimal forecast.

- Kolassa, S., & Martin, R. (2011). Percentage Errors Can Ruin Your Day (and Rolling the Dice Shows How). *Foresight: The International Journal of Applied Forecasting*, (23). (没找到文献, 可以参考 [这里](https://blogs.sas.com/content/forecasting/2011/11/11/tumbling-dice/).)

> Boy-lan and Syntetos (2006) note that "the mean squared error is not suitable for intermittent-demand items because it is sensitive to the occurrence of very high forecast errors".

- Boylan, J. E., & Syntetos, A. A. (2006). Accuracy and accuracy-implication metrics for intermittent demand. *Foresight: The International Journal of Applied Forecasting*, *4*, 39-42. (还没读)

### Predict Quantiles

> In store replenishment, retailers need to consider logistical constraints (pack sizes, best by dates, delivery schedules, minimum or maximum truck loads), balancing a lower service level for one product against a higher service level for another. They need to optimize over complex cost functions (time-varying purchasing and sales prices, rebate brackets that kick in once a certain total order amount has been reached), which in turn require flexibility with regard to lead times: we may want to pull orders forward in time, a so-called "forward buy".

上述理由意味着用点估计并不合适. 一个简单的改进是预测各个分位数, 分位数回归用的是 [pinball loss](https://www.lokad.com/pinball-loss-function-definition). 容易证明, 对应的分位数恰好能使期望 loss 最小 (求导即可, 证明可见 [这里](http://www.econ.uiuc.edu/~roger/courses/LSE/lectures/L1.pdf) pp. 9-12).

M5 用的是其改版 scaled pinball loss. 给定一个 quantile $u$, 分子是 forecasting horizon 中 pinball loss 的均值, 分母是历史数据 random walk 的 MAE (为了保证 SPL scale-independent). 记 $Q_t(u)$ 为时间 $t$ 时 $u$ 分位数的估计.

$$
\text{SPL}(u) = 
\frac{
\frac1h \sum_{t=n+1}^{n+h}
\left[
u(Y_t - Q_t(u)) 1_{\{Q_t(u)\le Y_t\}} 
+ (1-u)(Q_t(u) - Y_t) 1_{\{Q_t(u) >  Y_t\}}
\right]
}
{\frac{1}{n-1} \sum_{t=2}^n|Y_t - Y_{t-1}|}.
$$

冠军成绩是 0.15420 (对各个分位数平均之后 SPL 的加权平均), 铜牌线为 0.18910, 供参考.

> Since M5 does not focus on a particular decision-making problem, neither defines the exact parameters of such a problem (which could also vary for different aggregation levels and series), it becomes evident that all quantiles could be potentially useful. Moreover, since the objective of the M5 is to estimate the uncertainty distribution of the realized values of the examined series as precisely as possible, both sides and both ends of the distribution are considered relevant. In this regard, no special weights are assigned to the examined quantiles, which are therefore equally weighted.

### Probabilistic Forecasting

分布估计的评估指标推荐阅读 Czado, C., Gneiting, T., & Held, L. (2009). Predictive model assessment for count data. *Biometrics*, *65*(4), 1254-1261.

提供量化供应链管理服务的 [Lokad](https://www.lokad.com/supply-chain-management-(scm)-knowledge-base) 网站上有很多有意思的话题, 见其 learn 菜单下, knowledge base 栏的 Forecasting, 以及 technology 栏他们自己模型的 [发展历史](https://www.lokad.com/forecasting-technology): 从点估计, 到分布估计, 再到深度学习. 传达出的信息大概是: 传统的, 教科书上的方法实际效果差, 深度学习大法好.

> Overdispersion in retail sales can result from shoppers independently buying more than one unit of a given product (Ehrenberg, 1959), while zero inflation could well result from items being out-of-stock.

- Ehrenberg, A. S. (1959). The pattern of consumer purchases. *Journal of the Royal Statistical Society: Series C (Applied Statistics)*, *8*(1), 26-41. (还没读)


## References

- The M5 competition, competitors' guide. (2020). https://mofc.unic.ac.cy/m5-competition/
- Hyndman, R. J., & Koehler, A. B. (2006). Another look at measures of forecast accuracy. *International journal of forecasting*, *22*(4), 679-688.
- Makridakis, S. (1993). Accuracy measures: theoretical and practical concerns. *International journal of forecasting*, *9*(4), 527-529.
- Kolassa, S. (2016). Evaluating predictive count data distributions in retail sales forecasting. *International Journal of Forecasting*, *32*(3), 788-803.