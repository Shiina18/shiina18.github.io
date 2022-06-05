---
title: "Transformer 复习"
categories: 
- Machine Learning
tags: 
updated: 
comments: true
mathjax: true
---

复习

- Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention is all you need. *Advances in Neural Information Processing Systems*, 5998–6008.

<!-- more -->

## Positional encoding

Since our model contains no recurrence and no convolution, in order for the model to make use of the order of the sequence, we must inject some information about the relative or absolute position of the tokens in the sequence.

注意 BERT 用了可学习的绝对位置编码.

- [什么是 Transformer 位置编码?](https://mp.weixin.qq.com/s/IZr1WJvV8YrdNZZICBElhQ)
- 苏剑林. (2021, Mar 8). [Transformer 升级之路: 1. Sinusoidal 位置编码追根溯源](https://kexue.fm/archives/8231).
- 码农场. (2021, Nov 27). [相对位置并不优于绝对位置](https://www.hankcs.com/ml/a-simple-and-effective-positional-encoding-for-transformers.html).

## Attention

The two most commonly used attention functions are additive attention, and dot-product (multiplicative) attention. While the two are similar in theoretical complexity, dot-product attention is much faster and more space-efficient in practice, since it can be implemented using highly optimized matrix multiplication code.

We found it beneficial to linearly project the queries, keys and values $h$ times with different, learned linear projections to $d_k$, $d_k$ and $d_v$ dimensions, respectively.

- [为什么 Q 和 K 用不同矩阵?](https://www.zhihu.com/question/319339652/answer/1617078433)

### Scaling

We suspect that for large values of $d_k$ (the dimension of input queries and keys), the dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients. To illustrate why the dot products get large, assume that the components of q and k are independent random variables with mean 0 and variance 1. Then their dot product, $q \cdot k = \sum_{i=1}^{d_k} q_i k_i$ has mean 0 and variance $d_k$.

- [为什么较大的输入会让梯度很小?](https://www.zhihu.com/question/339723385/answer/782509914)
- [为什么分类任务的 softmax 前不用 scale?](https://www.zhihu.com/question/339723385/answer/811341890)

### Multihead

Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions. With a single attention head, averaging inhibits this.

- [为什么 Transformer 需要进行 Multi-head Attention?](https://www.zhihu.com/question/341222779)

很难讲.

## Residual block

- He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition. *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition*, 770–778.

With the network depth increasing, accuracy gets saturated (which might be unsurprising) and then degrades rapidly. Unexpectedly, such degradation is **not caused by overfitting**, and adding more layers to a suitably deep model leads to higher training error. If the added layers can be constructed as identity mappings, a deeper model should have training error no greater than its shallower counterpart. The degradation problem suggests that the solvers might **have difficulties in approximating identity mappings by multiple nonlinear layers** (Zhang, et al., 2016).

也就是, 在网络后面加几层, 如果这几层能拟合出恒等映射, 那么最终结果至少应该持平. 观察到结果变差, 而且不是过拟合, 说明最后几层难以拟合恒等映射. 办法是加个 skip connection, 让神经网络拟合残差; 对于恒等映射而言, 拟合残差意味着把所有东西都映射为常数零, 这就容易得多. 最终使得构造更深的网络成为可能.

## Layer norm

- Batch size 小的时候不适用 batch normalization.
- Layer norm 对每个词向量放缩, 比 batch norm 更 make sense.

<!-- 看过 https://kexue.fm/archives/4765 -->