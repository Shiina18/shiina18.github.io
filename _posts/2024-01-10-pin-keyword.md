---
title: "读文章: Understanding Pins through keyword extraction"
categories: 
- Machine Learning
updated: 
comments: true
mathjax: false
---

挺久之前读的, 补个笔记. 传统机器学习. 从帖子的多个文本来源抽取候选标签, 然后用分类模型判断标签是否与帖子相关. 没有用到图片信息 (除了从图中抽取文字).

- 2019-08 [Understanding Pins through keyword extraction](https://medium.com/pinterest-engineering/understanding-pins-through-keyword-extraction-40cf94214c18)

<!-- more -->

Pinterest 主要通过 annotations 理解文本. Annotations 是 1~6 个词的关键词或者短语, 描述 Pin 的主题. Annotations 除了文本, 还有置信度分数和语言标签 (共 28 门语言), 例如:

```
- (EN, sloth sanctuary, 0.99)
- (EN, sloths, 0.95)
- (EN, costa rica, 0.90)
- (EN, carribean, 0.85)
- (EN, animals, 0.80)
- (EN, travel, 0.80)
```

## 用例

Annotations 用作他们很多产品的机器学习模型特征, 得到了很好的效果.

**搜索.** 用 annotations 召回.

**相关 Pins (推荐).** 用 annotation 向量求 cosine 相似度.

**安全内容过滤 (分类).**

## 生成方法

**Annotations dictionary**

Annotations are limited to a finite vocabulary known internally as the Dictionary. The advantage of using such a dictionary over allowing annotations to be arbitrary ngrams is that it guarantees the annotations will be valid and useful phrases instead of misspellings (e.g., “recipies”), stopwords (e.g., “the”), fragments (e.g., “of liberty”) and generic phrases (e.g., “ideas”, “things”).

The dictionary initially started with popular topics that were manually entered by users, but it has grown to include additional sources of terms such as search queries, hashtags, etc. A significant amount of human curation has gone into building the dictionary to ensure its quality is maintained, and we periodically use heuristics to trim out bad terms and use a spell checker to remove misspellings. We have around 100,000 terms in the dictionary for each language.

**Candidate extraction**

先从不同文本源抽取候选 annotations. 文本源包括:

*   Pin title, description, url
*   Board name and description
*   Page title and description of the link
*   Search queries that frequently lead to clicks on the Pin
*   Names of objects detected in the image using a visual classifier

抽取候选:

1.  检测文本语言.
2.  分词.
3.  滑窗获得所有 1-6 词的 ngrams.
4.  标准化 ngrams.
5.  Ngrams are matched against the annotations dictionary.
6.  The extracted annotations are canonicalized to reduce duplication (e.g., “sloth” is canonicalized to “sloths” since it is not useful to have both of these annotations on a Pin). Canonical mappings are stored in the dictionary.

**Features**

Features are extracted for each annotation candidate to be later used for scoring.

Pin — Annotation features:

*   TF-IDF
*   Embedding similarity — cosine similarity between Pin embedding and annotation embedding
*   Source — some text sources tend to yield higher quality annotations than others, and annotations that were extracted from multiple sources (e.g., both Pin title and board title) tend to be better than annotations that were only present in a single source (e.g., just board title)

Annotation features:

*   IDF
*   Category Entropy — annotations that are popular across multiple categories tend to be more generic and less useful
*   Search frequency

We found our model performed better when we normalized our features such that the value distribution was similar across language and Pin popularity (i.e., number of repins).

**Model**

从候选中判断是否真的和 Pin (当前帖子) 相关. XGBoost.

Training labels are obtained through crowdsourcing where judges are asked to label for a given (Pin, annotation) pair whether the annotation is relevant to the Pin. Around 150,000 labels per language are used.
