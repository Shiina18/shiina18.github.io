---
title: "Notes on statistics done wrong"
categories: Statistics
updated:
comments: true
mathjax: true
---

- Reinhart, A. (2015). *Statistics done wrong: The woefully complete guide*. No starch press.

这本书是在 akuna capital 的 [招聘页面](https://akunacapital.com/careers#quantitative) FAQs section 下的 QUANT tab 上看到的.

> What can I read to prepare for the job/industry?
> 
> Many of our Quants have read and strongly recommend "Clean Code: A Handbook of Agile Software Craftsmanship" by Robert C. Martin, "Statistics Done Wrong: The Woefully Complete Guide" by Alex Reinhart, and "Python for Data Analysis: Data Wrangling with Pandas, NumPy, and Ipython" by Wes McKinney.

## Ch. 1 statistical significance

- $p$-value is a measure of surprise. It's not a measure of the size of the effect. It's not the false positive rate.
- Statistical significance does not mean your result has any *practical* significance.
- Two experiments with different designs can produce identical data but different $p$ values because the unobserved data is different. 本身样本空间就不一样.
- If you run 100 identical experiments, about 95 of the 95% confidence intervals will include the true value you're trying to measure. 在频率派观点下, 真实参数为固定值.
    - 假设参数真实值为 $\theta$, 随机样本为 $X$, 观测值为 $X(\omega)$, 则置信水平为 $\mathbb P(L(X) < \theta < U(X))$, 其中 $L(X)$ 和 $U(X)$ 都是统计量.
- 尽量用置信区间 (Gardner and Altman, 1986). In the process, you get the added bonus of learning how precise your estimate is. 
- 置信区间不流行的原因.
    - 置信区间太宽了, 不好意思写出来 (Cohen, 1994).
    - Another is that the peer pressure of peer-reviewed science is too strong—it's best to do statistics the same way everyone else does, or else the reviewers might reject your paper. 照葫芦画瓢.
    - Or the overemphasis on hypothesis testing in statistics courses means most scientists don't know how to calculate and use confidence intervals.

## Ch. 2 statistical power

- Few scientists ever perform this calculation. 得到统计显著的结果, 但是可能实验本身 underpowered. **Truth inflation** arises because small, underpowered studies have widely varying results. 
    - 参考 Cohen's classic *Statistical Power Analysis for the Behavioral Sciences*.
- Why are power calculations often forgotten?
    - 一个原因是可能根本没意识到样本量不够 (Tsang, et al., 2009).
    - Math is another possible explanation for why power calculations are so uncommon: **analytically calculating power can be difficult or downright impossible. Techniques for calculating power are not frequently taught in intro statistics courses.** And some commercially available statistical software does not come with power calculation functions.
- [ ] Sample size selection methods based on **assurance** have been developed for many common statistical tests, though not for all; it is a new field, and statisticians have yet to fully explore it. When you need to measure an effect with precision, rather than simply testing for significance, use assurance instead of power. 这个还真没听说过. 
- 小样本的 variation 更大, 从而会得到更大的置信区间, 极端值更可能出现在小样本中. 书中举的例子是大学校和小学校的成绩, 成绩最好的和成绩最差的一批可能都是小学校, 因为他们人少. Mather King 的 [姓氏越稀有, 越有可能成为精英姓氏?](https://zhuanlan.zhihu.com/p/30073359) 说的也是同样的事情.
    - A popular strategy to fight this problem is called *shrinkage*. For counties with few residents, you can "shrink" the cancer rate estimates toward the national average by taking a weighted average of the county cancer rate with the national average rate. 做法上有点像后验估计.
    - 另一种做法是让 sample sizes 都相同, 但这显然并不总能做到. 比如线上购物网站评分, 还有 reddit 评论的赞同反对. Reddit 可以用得赞率置信区间的下界来排序评论.

## Ch. 4 base rate fallacy

第三章略.

一个例子, 测试 100 种药, 其中只有 10 种真正有效. 取置信水平为 0.05, power 为 0.8, 则 10 种有效药中大概有 8 种是统计显著的, 另外无效药中有 5 种 (应该是 4.5) 统计显著. 于是 false discovery rate 为 5/13=0.38, 这么高的原因是 base rate 10/100 太低了. 因此如果有一次实验统计显著, 那么它大概有 38% 得到的是无效药. 这便是 base rate fallacy. 换一个角度, 这就是套 Bayes 公式最简单的习题.

另一个话题是 multiple tests, 当多个检验同时进行的时候, 需要关注整体的 false positive rate. 

- 一个方法是 Bonferroni correction. This reduces statistical power, since you're demanding much stronger correlations before you conclude they're statistically significant. In some fields, power has decreased systematically in recent decades because of increased awareness of the multiple comparisons problem.
- 另外就是 1995 年的 Benjamini–Hochberg 方法, 见 pp. 52-53. The procedure usually provides better statistical power than the Bonferroni correction, and the false discovery rate is easier to interpret than the false positive rate.

## Ch. 5 bad judges of significance

> We compared treatments A and B with a placebo. Treatment A showed a significant benefit over placebo, while treatment B had no statistically significant benefit. Therefore, treatment A is better than treatment B.

这段有几个问题

- 是否统计显著取决于显著性水平的选取. 比如取 $\alpha = 0.05$, 得到 $p = 0.04$ 和 $p=0.06$, 我们不能因此宣称这两种 treatments 显著地不同.
- $p$ values are not measures of effect size, so similar $p$ values do not always mean similar effects.
- If they have identical effects but we have only 50% power, then there's a good chance we'll say treatment A has significant benefits and treatment B does not.
    - 假设两个 treatments 相对于安慰剂有等同的有效性, statistical power 为 $c$, 则得出其中一个有效另一个无效的概率是 $2c(1-c)$.
- Instead of independently comparing each drug to the placebo, we should compare them against each other. This doesn't improve our statistical power, but it does prevent the false conclusion that the drugs are different.
- 为什么非要这么做? Why can't I just look at the
two confidence intervals and judge whether they overlap?
    - The standard deviation measures the *spread* of the individual data points. Confidence intervals and standard errors estimate how far the *average* for this sample might be from the true average. Hence, it is important to know whether an error bar represents a standard deviation, confidence interval, or standard error, though papers often do not say.
    - [ ] There might be a statistically significant difference between them, even though the confidence intervals overlap (Schenker and Gentleman, 2001).
    - [ ] For standard errors, we have the opposite problem we had with confidence interval bars: two observations might have standard errors that don't overlap, but the difference between the two is not statistically significant. 
    - There is exactly one situation when visually checking confidence intervals works, and it is when comparing the confidence interval against a fixed value, rather than another confidence interval.

## Ch. 6 double-dipping

- Double-dipping. 差不多就是 [A Wrong Way to Do Cross-Validation](https://shiina18.github.io/machine%20learning/2019/12/12/wrong-cv/). 
- [ ] Regression to the mean. It's just the observation that luck doesn't last forever. On average, everyone's luck is average.
- Stopping rules. Medical trials are expensive, so many
pharmaceutical companies develop stopping rules, which allow investigators to end a study early if it's clear the experimental drug has a substantial effect. **If we wait long enough and test after every data point, we will eventually cross any arbitrary line of statistical significance.  Poorly implemented stopping rules still increase false positive rates significantly** (Simmons, et al., 2011).
    - Choosing a more stringent $p$ value threshold that accounts for the multiple testing or by using different statistical tests.
    - Modern clinical trials are often required to register their statistical protocols in advance and generally preselect only a few evaluation points at which to test their evidence, rather than after every observation. Such **registered studies** suffer only a small increase in the false positive rate, which can be accounted for by carefully choosing the required significance levels and other sequential analysis techniques.

## Ch. 7-8 regression

- 把一个连续变量按照一个阈值分为两组会丢失很多信息 (Maxwell and Delaney, 1993).
    - If you do need to split continuous variables into groups for some reason, don't choose the groups to maximize your statistical significance. Define the split in advance, use the same split as in previous similar research, or use outside standards (such as a medical definition of obesity or high blood pressure) instead. 又回到了 double-dipping 的问题.
- **Stepwise** regression (forward selection, backward
elimination) is common in many scientific fields, but it's usually a bad idea (Whittingham, et al., 2006). 问题是 overfitting 和 truth inflation. 
    - 作者推荐 lasso.
- 训练集测试集分割, 相关性和因果性, Simpson 悖论

## Ch. 9-12 

略了. 开源大法好, 需要有机制鼓励开源, 比如规范引用数据集.

- Ioannidis, J. P. (2005). Why most published research findings are false. *PLoS medicine*, *2*(8), e124. (9144 citations till 2020/11/19)
- Schoenfeld, J. D., & Ioannidis, J. P. (2013). Is everything we eat associated with cancer? A systematic cookbook review. *The American journal of clinical nutrition*, *97*(1), 127-134. (165 citations till 2020/11/19)

## References

- Gardner, M. J., & Altman, D. G. (1986). Confidence intervals rather than P values: estimation rather than hypothesis testing. *Br Med J (Clin Res Ed)*, *292*(6522), 746-750. (2011 citations till 2020/11/19)
- Cohen, J. (1994). The earth is round (p<. 05). *American psychologist*, *49*(12), 997. (5170 citations till 2020/11/19)
- Tsang, R., Colley, L., & Lynd, L. D. (2009). Inadequate statistical power to detect clinically significant differences in adverse event rates in randomized controlled trials. *Journal of clinical epidemiology*, *62*(6), 609-616. DOI: *10.1016/j.jclinepi.2008.08.005*. (83 citations till 2020/11/19)
- Schenker, N., & Gentleman, J. F. (2001). On judging the significance of differences by examining the overlap between confidence intervals. *The American Statistician*, *55*(3), 182-186. (952 citations till 2020/11/19)
- Simmons, J. P., Nelson, L. D., & Simonsohn, U. (2011). False-positive psychology: Undisclosed flexibility in data collection and analysis allows presenting anything as significant. *Psychological science*, *22*(11), 1359-1366. DOI: *10.1177/0956797611417632*. (5083 citations till 2020/11/19)
- Maxwell, S. E., & Delaney, H. D. (1993). Bivariate median splits and spurious statistical significance. *Psychological bulletin*, *113*(1), 181. (772 citations till 2020/11/19)
- Whittingham, M. J., Stephens, P. A., Bradbury, R. B., & Freckleton, R. P. (2006). Why do we still use stepwise modelling in ecology and behaviour?. *Journal of animal ecology*, *75*(5), 1182-1189. (1311 citations till 2020/11/19)