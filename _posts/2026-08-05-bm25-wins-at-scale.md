---
title: "读论文 - BM25 Wins at Scale"
categories:
- LLM
tags: RAG
updated:
comments: true
mathjax: false
---

做企业 RAG 时，最容易被默认接受的一套叙事是：语料大了要上 embedding，复杂问题要上 agent，结构复杂再上 graph RAG。

这篇论文把它们放到同一条、跨度约 450 倍的语料规模曲线上，结论很不客气：小语料时文件系统 Agent 略好；语料约过 1,000 万 token 后，BM25 反超并持续领先。

论文：
- [BM25 Wins at Scale: A Scaling Study of Retrieval-Augmented Generation Paradigms](https://arxiv.org/html/2607.26497v2)

<!-- more -->

## 1. 这篇论文真正比较的是什么

不是在某个固定 benchmark 上比一个排行榜，而是问：当同一批问题不变、同一批相关证据和干扰项不变，只往语料库持续塞入背景文档时，检索范式会怎样退化。

它比较了七条 native pipeline：

- BM25
- DenseRAG
- File-System Agent
- HippoRAG 2
- LinearRAG
- MS-GraphRAG
- LightRAG

所有方法共用 `Qwen3.6-27B` 作为 reader，temperature 为 0；主实验的 embedding 统一使用 `Qwen3-Embedding-0.6B`。凡是有固定 retrieval depth 的方法都取 top-5 chunk。这样至少排除了“BM25 用一个 reader、dense 用另一个 reader”这种常见混杂因素。

## 2. Setup：为什么这组扩展实验可信

数据来自 EnterpriseRAG-Bench：511,959 篇企业文档、600.8M token、500 个问题，覆盖 wiki、Slack、邮件、工单、会议纪要、CRM 和代码审查等九类来源。

作者从一个 1,144 文档的 bedrock 开始，构造了 28 个严格嵌套的 corpus tier；每层约按 1.25 倍增长，最终到完整语料。最小层已经固定包含：

- 500 个问题相关的 722 份 gold document；
- 326 份“主题相关但事实错误”的 trap；
- 99 份针对 `info_not_found` 的 lure；
- 两份组织级 scaffold 文档。

也就是说，规模变大时，题目本身没有变简单或变难，相关证据和对抗性干扰也没有逐步加进去；新增的是按来源与噪声分层抽样的背景文档。论文测的是“同一个检索任务被更大的搜索空间稀释”这件事。

评分也不是只看答案文字。official combined score 先判断答案是否与 gold answer 对齐，再以原子事实的覆盖率作为 completeness；错误答案即使写得很全也会被归零。作者还用独立 judge 和更简单的二元协议复核，九个共享规模上的大类排序保持不变。

### 2.1 问题不是多轮对话，但并非全是单跳查找

这 500 题都是单轮问题：系统对每题只提交一次答案。File-System Agent 的多步来自其内部工具循环，不是用户连续追问或跨轮状态记忆。因此，这篇论文没有测 agent 在多轮会话里的长期规划能力。

但题目并不等价于一组 keyword lookup。它覆盖十类问题，包括跨段的 `intra-document reasoning`、跨文档的 `project-related`、要求找全必要证据的 `completeness`、要求分辨新旧版本的 `conflicting-information`，以及 `high-level` 和 `info-not-found`。其中 470 题是 source-grounded，10 题是组织级 high-level，20 题不可回答；问题按类型从源文档或由探索语料的 Agent 构造。

这一区分也解释了为什么小规模时文件 Agent 能略胜：它在 42,587 文档这一层的 intra-document、project-related、completeness 和 conflicting-information 类上均高于 BM25；仅 completeness 一类就是 56 对 27。论文测的是“一个问题内的多证据发现与综合”，不是多轮聊天。

## 3. BM25、Dense 和 Agent 到底怎么检索

这里必须把 native pipeline 和 `Agent+BM25` 机制对照分开，否则很容易把“Agent 能改写查询”的结论错误归到 BM25 身上。

### 3.1 Native BM25：一次性全局词法召回

主实验中的 BM25 是标准的一次性检索器：以问题为 query，对全库 shared chunk 建的倒排索引做 BM25 排序，直接取 top-5 chunk 给 reader 回答。

- 不是 Agent 的搜索工具；
- 没有工具循环；
- 论文没有报告 query rewrite、query expansion 或 LLM query planning；
- 论文也没有报告 BM25 之后还有 reranker。

因此更准确的描述是“原问题直接做 BM25 top-5 召回”，而不是“Agent 先拿 BM25 搜一遍”。BM25 的在线成本约为 5.8K token/问，基本由共同的 reader context 主导；它没有 LLM 建库成本。

### 3.2 Native DenseRAG：一次性向量召回

DenseRAG 同样不是把 embedding 暴露给 Agent 调用。论文将 shared chunk 编码为向量，问题直接做 query embedding，在 chunk embedding 索引中进行一次 dense retrieval，取 top-5 交给同一个 reader。

- 没有 Agent loop；
- 没有报告 query rewrite 或多轮检索；
- 没有报告 dense retrieval 后还有 cross-encoder / LLM rerank；
- 完整语料的 embedding 建库处理了 659.4M embedding token，在线成本约 4.9K token/问。

有一个很容易看错的细节：作者在**构造 benchmark 的 trap**时，用 BM25 top-200 作为候选池，再让 dense retrieval rerank 这个池子来挖掘误导文档。这是数据集构造，不是 DenseRAG 主实验的运行路径。主实验所描述的是对 chunk embedding 的直接 dense retrieval；论文还单独做了 full-corpus direct DenseRAG top-10 audit，检查结果是否被这套 trap 候选池偏置。

### 3.3 File-System Agent：局部、串行的发现过程

File-System Agent 没有检索索引。它面对原始语料树，只能调用：

- `list_dir`：列目录；
- `grep`：固定字符串搜索，最多返回 30 个路径；
- `read_doc`：读取一个文档的前 8,000 字符。

它最多有 80 次 LLM 调用/题。因此它并不是一次全局排序，而是根据上一轮结果决定下一次要看哪个路径、grep 哪些关键词、读哪份文件。小库里，这种反复核对会带来收益；大库里，局部探索更容易从一开始就走进错误区域。

论文所说的 harness 是作者自实现的 tool-calling loop，并未命名为某个通用 Agent 框架，也不是直接调用 Claude Code 或 Codex。它的 policy model 同样是 `Qwen3.6-27B`；系统 prompt 要求先通过目录定位，再 grep，再读文档，只能基于文档作答并引用相对路径。`list_dir` 最多返回 200 个子项，`grep` 是固定字符串搜索、最多返回 30 个路径，`read_doc` 返回前 8,000 个字符。

这不是一个可以忽略的实现细节。作者在 bedrock 上做了 harness control，固定 policy model、原始文件、题集和 judge，只替换 agent loop：

| Harness / retrieval | 分数 |
|---|---:|
| 作者的 File-System harness | 86.3 |
| Pi-Agent | 82.3 |
| Codex harness | 43.9 |
| Native BM25 | 82.1 |

作者的 harness 在三种文件 Agent 中最高。因此论文避免了用一个显然较弱的 Agent 实现衬托 BM25；但跨规模的结论仍应理解为“作者这个最强观察到的文件探索 harness 会随规模失效”，而不是所有可能的 Agent harness 都必然如此。

### 3.4 Agent+BM25：唯一允许改写 query 的地方

论文额外做了一个很好的机制实验。`Agent+BM25` 保持 Agent 的模型、预算、问题集、judge 和回答约束不变，只把原始文件树工具换成 `bm25_search` 和文档读取。

它的**第一轮** `bm25_search` 被程序强制使用原始问题，确保返回的有序 top-5 与 Native BM25 完全一致。之后，Agent 才可以根据结果改写查询、继续检索，或打开已返回来源的更多上下文。

所以结论不是“native BM25 会自动改写 query”，而是：**先用一次可靠的全局 BM25 发现候选，再让 Agent 做有限的二次搜索与证据综合，效果很好。**

### 3.5 论文没有做 Agent+Dense

这是解释结果时必须保留的缺口。主实验有 Native DenseRAG，机制实验有 Agent+BM25，但没有一个严格对应的 `Agent+Dense`：即保持同一模型、同一 prompt、同一 80-call 预算，让第一轮强制返回 Native DenseRAG 的原问题 top-5，再允许 Agent 改写 query 和继续搜索。

因此论文能够证明“Agent 接到 BM25 候选发现后很有效”，不能证明“BM25 天然比 embedding 更适合作为 Agent 的搜索工具”。这个强结论需要 `Agent+Dense`，最好再加一个 Agent+hybrid 检索的匹配对照。

## 4. 主结果：交叉点在约 1,000 万 token

| 文档数 | BM25 | File-System Agent | DenseRAG |
|---:|---:|---:|---:|
| 1,144 | 74.7 | **77.4** | 58.1 |
| 21,614 | **64.9** | 62.6 | 44.2 |
| 42,587 | **61.2** | 58.9 | 40.7 |
| 131,876 | **55.2** | 50.9 | 36.0 |
| 511,959 | **50.5** | 30.7 | 29.9 |

在 bedrock，Agent 和 BM25 的 95% 置信区间重叠，Agent 的点估计略高。大约到 1,000 万 corpus token，曲线交叉；之后 BM25 在每个更大的共享 tier 都领先。

DenseRAG 不是因为延迟或 token 成本输掉：它在线成本甚至略低于 BM25。但它从最小 tier 的 58.1 一路降到完整语料的 29.9，始终没有给出“语料越大，dense 越能体现优势”的证据。

不过也不能把这读成“BM25 的语义能力胜过 embedding”。作者针对词法重合做了 paraphrase control：在 1,144 文档和 2,254 文档两个 tier 上，改写问题后 BM25 分别为 63.9 和 60.1，DenseRAG 为 51.8 和 49.9，BM25 仍领先 dense 与图方法。这说明结果不只是 exact keyword matching。

这个控制的边界同样要写清：它只覆盖两个小 tier，不能完全排除在更大规模上，企业专有名词、synthetic 文风和词法重合仍放大了 BM25 的优势。更准确的结论是：BM25 在这个 benchmark 的扩展设置中更强，而不是已经证明它对任何低词法重合的真实企业提问都更强。

File-System Agent 的问题更明显。它在 bedrock 已经使用 226K token/问，是 BM25 的约 39 倍；随着探索加深，21,614 文档时升到 343K token/问，约为 BM25 的 60 倍。满规模时，31% 的问题耗尽 80-call 预算；但即便只看未耗尽预算的问题，准确率仍在下降，所以不是简单地把 budget 加大就能解释。

## 5. Agent 输的不是阅读，而是 candidate discovery

作者用同一批 150 个分层抽样问题，在 bedrock 和完整语料上做了对照：

| 方法 | 1,144 文档 | 511,959 文档 | 满规模 DocR | 满规模 token/问 |
|---|---:|---:|---:|---:|
| Native BM25 | 81.3 | 54.8 | 65.6 | 5.8K |
| File-System Agent | 87.1 | 36.9 | 36.8 | 895K |
| Agent+BM25 | **90.1** | **69.4** | **72.4** | 101K |

文件 Agent 在“已经找到了至少一个 gold document”的条件下，答案质量高于 BM25：85.9 对 73.8。问题是满规模时，它的 any-gold hit rate 只有 39.0%，BM25 是 71.6%。它并非不会读证据，而是很难在巨大的原始文件树里首先找到证据。

只换掉候选发现原语，满规模 `Agent+BM25` 比文件 Agent 高 32.52 分，也比 Native BM25 高 14.56 分，且 token 成本约为文件 Agent 的九分之一。

这给出了最有用的工程结论：

> Agent 的适合位置是 ranked discovery 之后的改写、核验、补证与综合；它不适合替代全局候选排序。

## 6. Graph RAG：在这组实验中基本败在建库与规模

论文还比较了 HippoRAG 2、LinearRAG、MS-GraphRAG 和 LightRAG。它们并非都在小规模完全不能用，但在这条扩展曲线上没有形成可部署的竞争方案。

- HippoRAG 2 只完成到 131,876 文档；在约 154.7M corpus token 处，花了 724M 生成 token 建图，得分为 41.0，低于 BM25 的 55.2。按拟合推到完整语料，需约 2.9B 生成 token、约 3 个单实例日。
- MS-GraphRAG 只完成到 8,750 文档；完整语料估计约需 7.9B 生成 token、约 50 个单实例日。
- LightRAG 在 2,826 文档时已无法在资源预算内完成；其建图增长拟合为超线性，完整语料估计约 102B token、约 4 个单实例年。
- LinearRAG 不依赖生成式 LLM 建图，只需 NER 与 embedding，因此成本可控；但其准确率从 46.2 下降到约 29.8，也明显低于 BM25。

所以“graph RAG 失败”在这里应理解为：要么建库扩不动，要么扩得动但分数低于 BM25，没能同时满足准确率和部署成本两项要求。

## 7. 对实际 RAG 的启发

这篇论文并不证明 BM25 在所有任务上优于 dense retrieval 或 agent。它证明的是，在这个带有内部术语、过期近重复、错放文档和对抗性干扰的企业语料中，随着候选空间增长，**一次性、全局、词法排序的候选发现**比局部串行探索更稳。

我会把默认架构顺序定成：

1. 先做可测、可靠的 BM25 baseline；
2. 再评估 dense retrieval 是否真的增加召回，而不是因为“语义”标签默认加入；
3. 有复杂证据综合需求时，让 Agent 在 BM25 或 hybrid 的候选集合上工作；
4. 图索引只在关系结构确实能提高目标任务、且离线构建成本可接受时引入。

最短的总结是：**BM25 负责先把世界缩小，Agent 负责在缩小后的世界里思考。**

## 8. 分数到底在衡量什么

论文的 headline score 是 official combined score。对每一个问题，它的逻辑可以写成：

```text
如果答案与 gold answer 不对齐：combined = 0
如果答案对齐：combined = 被覆盖且一致的 atomic facts 比例
```

最后对问题取平均。除了 combined score，作者还分别记录：

- `alignment`：LLM judge 判断候选答案是否与 gold answer 对齐；允许措辞不同和额外相关上下文，但拒绝事实冲突、错误数值和遗漏核心内容；
- `completeness`：逐条检查 gold 的 atomic facts 是否被答案表达且保持一致；
- `document recall`：返回的文档 ID 与 gold 文档 ID 的精确集合重叠。

这个组合比只做答案相似度合理：回答了正确方向但漏掉必要条件，拿不到满分；罗列了许多事实但主结论错误，会直接归零；document recall 又能帮助区分“没找到证据”和“找到了却没有正确综合”。

它并非没有主观性。gold answer 和 atomic facts 出自 synthetic benchmark，alignment 与事实判定仍依赖 LLM-as-judge。作者做的缓解是：用独立 judge 复评，pooled alignment 一致率为 96.2%；再以简单 binary protocol 重算，九个共享规模上的大类排序不变。因此它足以支持 BM25、DenseRAG、文件 Agent 和图方法之间的宏观分层，但不适合把相差一两分的细微排序当成定论。
