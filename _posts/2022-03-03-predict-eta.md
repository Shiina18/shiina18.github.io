---
title: "到达时间预测两则: Uber 和美团"
categories: 
- Machine Learning
tags:
updated: 
comments: true
mathjax: true
---

## Uber: DeepETA (Transformer)

参考

- Xinyu Hu, Olcay Cirit, Tanmay Binaykiya, and Ramit Hora. (2022, Feb 10). [DeepETA: How Uber Predicts Arrival Times Using Deep Learning](https://eng.uber.com/deepeta-how-uber-predicts-arrival-times/). *Uber Engineering*.

预测到达时间 (ETA, estimated time of arrival) 显然对 Uber 很重要 (最高 QPS 的服务). 传统方法把道路网分割为小路段, 每个路段表示为图中的带权边, 找出图中最短路径即得 ETA. 为考虑别的因素, 用机器学习预测 "真实到达时间和传统方法得到的 ETA" 的差值 (residual). 

之前用 XGB ensemble. Eventually, we reached a point where increasing the dataset and model size using XGBoost became untenable. (为啥不行?) We decided to explore deep learning because of the relative ease of scaling to large datasets using data-parallel SGD. (树模型应该也有并行算法?)

目标有三个

- 时延: 毫秒级
- 准确度: MAE 要胜过 XGB
- 通用性: 用于 Uber 所有业务线

<!-- more -->

### 模型

在表格数据上用 Transformer, 其中 attention 可以学到特征之间的交互. Uber 实践中将连续变量按照分位数分桶效果更好.

其中地理位置有很多粒度, embedding 用下述第三种方式处理

- Exact indexing, which maps each grid cell to a dedicated embedding. This takes up the most space.
- Feature hashing, which maps each grid cell into a compact range of bins using a hash function. The number of bins is much smaller than with exact indexing.  
- Multiple feature hashing, which extends feature hashing by mapping each grid cell to multiple compact ranges of bins using independent hash functions. See Figure 5:

![](https://shiina18.github.io/assets/posts/images/384194819246802.png)

### 加速

用了 linear transformer. 对于 $K$ 个 $d$ 维输入, 原始 transformer 时间复杂度为 $O(K^2d)$, 而 linear transformer 为 $O(Kd^2)$, 只要 $K > d$ 就能加速 (不严谨, 要看它们差的数量级和 big o 前面的常数).

模型层数少, 参数主要在 embedding 层. 把连续输入离散化也便于直接找 embedding 从而加速.

### 通用化

模型的总体架构如下

![](https://shiina18.github.io/assets/posts/images/256004119226636.png)

The decoder is a fully connected neural network with a segment bias adjustment layer. This approach performs better than simply adding segment features to the model. The reason we implemented a bias adjustment layer instead of a multi-task decoder is due to latency constraints.

### Further reading

- [tabtransformer](https://zhuanlan.zhihu.com/p/414462640) 不如树模型
- [表格数据还得看树模型](https://zhuanlan.zhihu.com/p/381323980)

## 美团: GBDT 到 DeepFM

参考

-  超逸. (2017, Nov 23). [即时配送的 ETA 问题之亿级样本特征构造实践](https://mp.weixin.qq.com/s/c-flgHKAlCfdZCIrMXAzxg).
- 基泽, 周越, 显杰. (2019, Feb 21). [深度学习在美团配送 ETA 预估中的探索与实践](https://mp.weixin.qq.com/s/98X2agJlZcCH6IdZqf9m0A). 包括 "长尾规则补时", 和部署方案.

外卖场景比打车更复杂. 

- 外卖场景 ETA 对用户和骑手都很重要; 而打车场景用户更关心能否打到车, 司机也不会特别 care 这个.
- 外卖场景环节更多: 骑手 (接-到-取-送), 商户 (出餐), 用户 (交付), 还要经历室内室外的场景转换 (上下楼).

![](https://shiina18.github.io/assets/posts/images/194852521226637.png)

17 年的时候美团还是 GBDT 构造特征 + 线性回归. 迭代路径类似 CTR, 转向用 DeepFM 以及自定义的网络.

推荐阅读业务全景描述, 非常 informative

- 何仁清. (2018, Dec 13). [机器学习在美团配送系统的实践: 用技术还原真实世界](https://tech.meituan.com/2018/12/13/machine-learning-in-distribution-practice.html).

### 特征

- 离线特征
    - 商户画像: 商户平均送达时长, 到店时长, 取餐时长, 出餐状况, 单量, 种类偏好, 客单价, 平均配送距离
    - 配送区域画像: 区域运力平均水平, 骑手规模, 单量规模, 平均配送距离
- 在线特征
    - 商家实时特征: 商家订单挤压状况, 过去 N 分钟出单量, 过去 N 分钟进单量
    - 区域实时特征: 在岗骑手实时规模, 区域挤压 (未取餐) 单量, 运力负载状况
    - 订单特征: 配送距离, 价格, 种类, 时段
    - 天气数据: 温度, 气压, 降水量
    
> 在实际配送中, 我们都会要求骑手在完成交付后进行签到, 这样就会积累大量的上报数据, 对于后续进行精细化挖掘非常有帮助.
