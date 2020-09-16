---
title: "多重共线性"
categories: Statistics
updated:
comments: true
mathjax: true
---

## 简介

考虑线性回归

$$
y = X\beta + \varepsilon,
$$

其中 $X$ 为 $n\times p$ 矩阵, 可以理解为 $n$ 个样本, $p$ 个特征 (因变量). 当 $X$ 的列向量线性相关时, $X'X$ 不存在逆, 参数估计会有问题. 我们把 $X$ 的列向量线性相关或者近似线性相关的情形称为存在多重共线性. 因为普通线性回归参数估计要用到 $X'X$ 的逆, 多重共线性会导致参数估计非常不稳定, 比如会出现特别大的估计值.

<!-- more -->

## 来源

- 数据收集: 举个极端例子, 比如特征为身高, 一列是以厘米为单位的身高, 一列以米为单位, 那么这两列就线性相关了. 现实一些的例子, 比如特征包含家庭收入和房屋面积, 这两者是正相关的, 也会导致多重共线性.
- 模型选择: 比如加入交叉特征. 假设有两个特征 $x_1$ 和 $x_2$, 如果 $x_1$ 数据非常集中, 那么把 $x_1 x_2$ 加入模型会导致多重共线性.
- Overdetermined model: 特征数量比样本多.

## 诊断

一个诊断方法是观察 $X$ 的奇异值. 记其 SVD 为 $X = U\Sigma V'$, 详见 [用 SVD 进行图像压缩](https://shiina18.github.io/mathematics/2019/03/07/svd/), 主成分 $Z = XV$ 的列互相正交, 且 $Z'Z = \Sigma^2$. 

由于

$$
Z_i = \sigma_{k=1}^p v_{ik}X_k.
$$

若 $\sigma_i$ 小, 意味着 $Z_i$ 接近零, 那么 $X_k$ 近似线性相关. (事实上, 这导致 $X'X$ 的逆 ill-conditioned.)

不过, 更常见的方法应该是利用 VIF (variance inflation factor) 等, 但我不是很关心.

## 对策

- (笑) Make sure you have not fallen into the dummy variable trap; including a dummy variable for every category (e.g., summer, autumn, winter, and spring) and including a constant term in the regression together guarantee perfect multicollinearity.
- 最佳方法是收集额外数据.
- 模型重设, 特征选择
- 正则化
- 主成分回归. 即按照上一节所说的主成分中去掉 $\sigma_i$ 较小的成分再进行回归.
- Leave the model as is, despite multicollinearity. The presence of multicollinearity doesn't affect the efficiency of extrapolating the fitted model to new data provided that the predictor variables follow the same pattern of multicollinearity in the new data as in the data on which the regression model is based.

## Final Note

> Finally, consider the actual *impact* of multicollinearity. It doesn't change the predictive power of the model (at least, on the training data) but it does screw with our coefficient estimates. In most ML applications, we don't care about coefficients *themselves*, just the loss of our model predictions, so in that sense, checking VIF doesn't actually answer a consequential question. (But if a slight change in the data causes a huge fluctuation in coefficients \[a classic symptom of multicollinearity\], it may also change predictions, in which case we do care -- but all of this \[we hope!\] is characterized when we perform cross-validation, which is a part of the modeling process anyway.) A regression is more easily interpreted, but interpretation might not be the most important goal for some tasks.

See [Why is multicollinearity not checked in modern statistics/machine learning - Cross Validated](https://stats.stackexchange.com/questions/168622/why-is-multicollinearity-not-checked-in-modern-statistics-machine-learning)

## 其他模型中的多重共线性

> Permutation feature importance is a model inspection technique that can be used for any fitted estimator when the data is tabular. This is especially useful for non-linear or opaque estimators. The permutation feature importance is defined to be the decrease in a model score when a single feature value is randomly shuffled 1. This procedure breaks the relationship between the feature and the target, thus the drop in the model score is indicative of how much the model depends on the feature. This technique benefits from being model agnostic and can be calculated many times with different permutations of the feature.

> Tree-based models provide an alternative measure of [feature importances based on the mean decrease in impurity](https://scikit-learn.org/stable/modules/ensemble.html#random-forest-feature-importance) (MDI). Impurity is quantified by the splitting criterion of the decision trees (Gini, Entropy or Mean Squared Error). However, this method can give high importance to features that may not be predictive on unseen data when the model is overfitting. Permutation-based feature importance, on the other hand, avoids this issue, since it can be computed on unseen data.
>
> Furthermore, impurity-based feature importance for trees are **strongly biased** and **favor high cardinality features** (typically numerical features) over low cardinality features such as binary features or categorical variables with a small number of possible categories.
>
> Permutation-based feature importances do not exhibit such a bias. Additionally, the permutation feature importance may be computed performance metric on the model predictions predictions and can be used to analyze any model class (not just tree-based models).

> When two features are correlated and one of the features is permuted, the model will still have access to the feature through its correlated feature. This will result in a lower importance value for both features, where they might *actually* be important.

See [4.2. Permutation feature importance — scikit-learn 0.23.2 documentation](https://scikit-learn.org/stable/modules/permutation_importance.html#permutation-importance)

**参考**

- Montgomery, D. C., Peck, E. A., & Vining, G. G. (2016). 线性回归分析导论 (第 5 版) (王辰勇, 译). 北京: 机械工业出版社. pp. 203-231.
- [Multicollinearity - Wikipedia](https://en.wikipedia.org/wiki/Multicollinearity)