---
title: "读论文 - EnterpriseRAG-Bench"
categories:
- LLM
tags: Agent
updated:
comments: true
mathjax: false
---

之前遇到过类似场景, 看看人家怎么做的. 下面是 codex GPT-5.4 high 写的.

仓库：
- [onyx-dot-app/EnterpriseRAG-Bench](https://github.com/onyx-dot-app/EnterpriseRAG-Bench)

论文：
- [EnterpriseRAG-Bench: A RAG Benchmark for Company Internal Knowledge](https://arxiv.org/abs/2605.05253)

<!-- more -->

## 1. 这个 benchmark 在解决什么问题

作者的基本判断很准确：现有很多 RAG benchmark，数据来源要么是公开网页，要么是社区问答，要么是结构比较规整的知识库。这和企业内部知识的检索环境差别很大。

企业内网的难点通常不是“文档太少”，而是下面这些：

- 信息分散在很多源里，而且格式很杂。
- 同一件事会在 PR、设计票、Slack 讨论、runbook 里各说一部分。
- 文档会过期，会互相矛盾，会被放错地方。
- 问题里会充满内部项目代号、缩写和组织黑话。
- 真正困难的问题，往往不是找一个答案段落，而是判断哪些文档必须看、哪些只是相关但非必要、哪些根本是噪音。

EnterpriseRAG-Bench 的设计几乎就是围绕这些点展开的。

## 2. 数据集长什么样

根据仓库 README，这个 benchmark 的公开版本包含 50 万出头的文档和 500 道核心问题，模拟的是一家叫做 Redwood Inference 的 AI 推理服务公司。[README](https://github.com/onyx-dot-app/EnterpriseRAG-Bench/blob/main/README.md)

文档源分布大致是：

- Slack：27.5 万
- Gmail：12 万
- Linear：3.5 万
- Google Drive：2.5 万
- Hubspot：1.5 万
- Fireflies：1 万
- GitHub：8000
- Jira：6000
- Confluence：5000

这个分布本身就很像企业知识库的真实情况：聊天记录远多于规范文档，噪声远多于精炼知识。

问题集分成 10 类，核心分布以实际 `questions.jsonl` 为准：

- `basic`: 175
- `semantic`: 125
- `intra_document_reasoning`: 40
- `project_related`: 40
- `constrained`: 30
- `conflicting_info`: 20
- `completeness`: 20
- `miscellaneous`: 20
- `high_level`: 10
- `info_not_found`: 20

这里有一个值得注意的小坑：`README.md` 和实际 `questions.jsonl` 是一致的，但 `quickstart.md` 里的分类计数还是旧版本，和当前数据不完全一致。做复现时建议以 `questions.jsonl` 或 README 为准，而不是 quickstart 表格。

## 3. 它是怎么把这个 benchmark 造出来的

这是这套工作里最值得看的部分。仓库里不仅给了数据，还给了“怎么生成这样一家公司、这样一堆文档、这样一套题”的方法学。[methodology.md](https://github.com/onyx-dot-app/EnterpriseRAG-Bench/blob/main/methodology.md)

### 3.1 Stage 1：先搭出一家公司

第一阶段不是直接吐文档，而是先做人类参与的 scaffolding：

- 公司 overview
- initiatives
- employee directory
- source structure
- 各目录下的 `agents.md`

这一步的作用很关键。它不是让模型凭空随机写 50 万份文档，而是先定义一家公司是什么、有哪些部门、有哪些项目、各系统里应该长什么样。

尤其是 `agents.md` 这一招很实用。比如 GitHub 目录下的文档被约束成 PR + 评论，而不是让模型自由发挥成 issue、design doc、RFC 的混合体。这样能显著减少 source-format drift。

### 3.2 Stage 1 的核心：高保真文档 + 低成本海量文档

作者把文档生成分成两层：

1. 高保真项目文档
2. 高体量主题文档

前者对应 methodology 里的 Step 6 到 Step 8。

- Step 6 先生成项目 scaffolding。
- Step 7 再生成项目文档，每份文档都知道公司背景、项目描述、同项目其它文件、自己的路径和角色。
- Step 8 额外生成一小簇“完整性题”专用文档组，让后面可以稳定生成那种必须召回多个文档才答得全的问题。

后者对应 Step 9，也就是 bulk generation。

作者观察到，如果只给一个公司背景然后让模型批量写文档，模型会非常快地收敛到几个自己熟悉的话题，产生大量“换壳近重复”。所以他们先按 source type 估算文档量，再按 topic / subtopic 分层，把每个叶子主题控制在最多 500 篇文档，然后在局部主题内生成。

这本质上是在用 topic scaffolding 去压制 LLM 的 mode collapse。

### 3.3 Stage 2：故意加噪声

这是整个 benchmark 最像真实企业环境的地方。

他们没有把数据集做成一个理想化知识库，而是有意识地加了四种噪声：

- random shuffle：把一部分文档随机错放到同 source 的别的目录
- LLM-based shuffle：让 LLM 按“看起来合理但其实放错”的方式错放文档
- miscellaneous files：增加边缘目录和非主流文件
- near duplicates：制造近重复文档，并更新其中部分关键事实

这意味着 benchmark 不是只问“你能不能找到相关文档”，而是在问：

- 你会不会被错放文档误导？
- 你能不能处理“新文档推翻旧文档”？
- 你是否只会盯着主干目录，忽略边角资料？

### 3.4 Stage 3：问题不是一锅炖，而是按 10 类分别造

这部分设计得也很讲究。作者没有让模型直接“看文档出题”，而是把 10 类问题拆开，各自用不同 prompt 和流程生成。

比较值得注意的几类：

- `basic`
  不是单纯关键词题。prompt 明确要求避免过长 exact phrase，避免把检索做成字符串匹配。

- `semantic`
  和 basic 很像，但刻意减少 keyword overlap，让问题更像真实员工提问，而不是“把答案句子改写一下”。

- `intra_document_reasoning`
  测单文档内部长距离依赖。问题必须依赖同一长文档的不同段落，不能被某个连续 chunk 单独回答。

- `project_related`
  允许模型读一个项目下的多份文档，然后再反推“最小必要文档集”作为 gold docs。

- `constrained`
  这类题很像企业检索里的真坑：很多文档表面都相关，但只有满足所有限定条件的那一份或那几份才是对的。

- `conflicting_info`
  专门测“新旧版本冲突”与文档可信度排序。

- `completeness`
  不是找一个最相关文档，而是要求把必须文档全部召回；漏一个就答不完整。

- `high_level`
  刻意设计成没有单一 gold doc。问题能从公司整体上下文中回答，但不能被任何单个文档直接回答。

- `info_not_found`
  测系统会不会老老实实承认“文档里没有”，而不是看见相似词就编。

换句话说，这 10 类题并不是难度递增列表，而是在覆盖 10 种不同失败模式。

## 4. 它怎么评估

评估是另一半亮点。这个 benchmark 的评估思路，不是传统 IR 那种固定 qrels + nDCG / Recall@k，而是一个更 RAG-native 的流程。

### 4.1 输入格式

你的系统需要交一个 JSONL，每行形如：

```json
{"question_id": "qst_0001", "answer": "Your answer text...", "document_ids": ["dsid_abc", "dsid_def"]}
```

也就是说，评测同时看：

- 你生成了什么答案
- 你声称自己用到了哪些文档

这里要特别澄清一个很容易混淆的点：

- `eval` 脚本本身不负责召回。
- 召回发生在“你的 RAG 系统”或者“仓库提供的 answer-generation baseline”那一层。
- `metrics_based_eval.py` / `comparative_eval.py` 做的是“拿你提交的 `answer` 和 `document_ids` 来打分”，而不是自己先去库里搜一遍再替你答题。

换句话说，benchmark 的流程是：

1. 你自己先跑 retrieval + generation。
2. 你把答案和召回到的 `document_ids` 交给评测器。
3. 评测器根据 gold docs / gold answer / answer_facts 给你打分。
4. 如果你交上来的 docs 看起来比原 gold 更合理，评测器再触发 correction flow。

## 4.1.1 官方 baseline 是怎么召回的

仓库里确实提供了 3 套“官方参考召回/答题方式”，但它们属于 `answer_generation`，不是 `answer_evaluation`。

### Vector Search

- 用 `text-embedding-3-large`
- 每篇文档把 `title + content` 拼起来做 embedding
- 存到 Qdrant
- query 也做 embedding
- 单次 cosine similarity，取 top 10
- 不做 re-ranking、不做 query expansion、不做 metadata filtering

这是一条非常朴素的 dense baseline。

### BM25

- 把 `title + content` 拼成一个 `text` 字段
- 建到 OpenSearch
- query 直接做 BM25 `match`
- 取 top 10
- 再把 top 10 文档喂给 LLM 生成答案

这条线本质上是 lexical baseline。

### Agent-Based Retrieval

- 不是预建索引后 top-k 检索
- 而是让 LLM agent 直接在语料目录里搜索
- 工具包括 `grep`、`find`、`jq`、`sed`、`awk`、`ls`、`tree` 等
- agent 可以不断搜索、读文档、选择 `dsid`
- 单题默认 wall-clock 预算 10 分钟

这条线更像“研究员式搜库”，慢很多，但在多跳题、路径信息重要的题、需要动态探索的题上更有优势。

所以如果你问“这个 benchmark eval 时怎么召回”，准确答案应该是：

- 严格说，`eval` 不召回。
- 官方 repo 提供了 3 套可选的 retrieval baseline 用来先生成答案和 `document_ids`，然后再把结果送进 eval。
- leaderboard 上别人提交的系统，也应该是各自先完成召回，再提交 answer file。

### 4.2 四个核心指标

metrics-based eval 的四个核心指标是：

- `Correctness`
  整体答案是否和 gold answer 对齐。这个判断由 LLM 做 holistic comparison，不要求措辞一致，但核心事实不能冲突，尤其数字必须匹配。

- `Completeness`
  gold answer 会被拆成 `answer_facts`。评测器逐条检查 candidate answer 是否支持这些原子事实，最后算覆盖率。

- `Document Recall`
  你返回的 `document_ids` 里，覆盖了多少 gold docs。

- `Invalid Extra Documents`
  你多返回的文档里，有多少既不是 gold，也没有被评估器判成 “valid but not required”。

这四项拼在一起，比只看 answer accuracy 更有诊断力。

比如：

- correctness 高、completeness 低：说明你答对大方向了，但漏信息。
- recall 低、correctness 高：说明题可能比较容易，或者你的 answer model 在补偿 retrieval。
- invalid extra docs 高：说明 retriever 很“贪”，给了太多噪音。

## 4.2.1 `Completeness` 到底怎么打分

这项分数不是“judge 主观觉得答案挺全”，而是很机械地走 `answer_facts`。

以 `qst_0431` 这道题为例：

问题：

> What is the procedure for an emergency rollback of a Serving Runtime release (Hosted and Dedicated)?

它的 `answer_facts` 里一共有 12 条，典型几条是：

- 先暂停或冻结正在进行的 progressive rollout
- 把 serving runtime re-pin 到已知稳定的旧 release tag
- 触发 redeploy
- 用 5xx、p95 TTFT、GPU OOM 等指标验证回滚后健康状态
- Hosted 要按 region rollout 顺序回滚
- Hosted 回滚后要 lock tag 防止自动前滚
- Dedicated 要识别受影响 tenant cluster
- Dedicated 要按 cluster pin + redeploy
- Hosted 至少观察约 30 分钟，Dedicated 至少观察约 60 分钟
- 要保留 CI/CD job links、受影响 region/cluster、tag、timing、verification evidence

评测时，脚本会做两件并行的事：

1. 用一个 holistic judge 判你的答案整体是否和 gold answer 对齐。
2. 用多个独立 fact judge，逐条检查你的答案是否支持这 12 条事实。

如果你的答案只写了：

> Pause the rollout, pin to the previous runtime tag, redeploy, and verify metrics.

那么它很可能：

- `Correctness` 仍然是对的
- 但 `Completeness` 只会拿到一部分，因为你漏了 Hosted/Dedicated 的差异、稳定性观察窗口、证据留存等细节

这就是这个指标有用的地方：它把“答对了”和“答全了”拆开了。

### 4.3 这个 benchmark 最特别的点：gold 不是绝对真理

作者非常明确地承认了一件很多 benchmark 不愿承认的事实：大规模数据集里的 gold docs 并不一定是“绝对最优文档集”。

所以他们在评估里做了 correction flow：

1. 如果你的 `document_ids` 和原始 gold docs 完全一样，直接跳过 correction。
2. 如果不一样，就把 gold docs 和你新带来的 candidate docs 一起交给 3 个 LLM judge。
3. 每个 judge 会把每个文档分成三类：
   - `required`
   - `valid`
   - `invalid`
4. 多数票决定最终分类。
5. 如果 gold set 被推翻，就更新 `expected_doc_ids`。
6. 如果 gold docs 变了，还会基于新文档集重生成 `gold_answer` 和 `answer_facts`，再继续打分。

这个逻辑在 `metrics_based_eval.py` 里写得很清楚，而且还做了几件工程上很重要的保护：

- 对新增 candidate docs 做上限裁剪，最多只拿 20 个进 correction。
- gold doc 在 tie-break 上有保护，不会被轻易踢掉。
- `valid` 文档不会进入 gold set，但在 `invalid_extra_docs` 统计时不算脏文档。

这套设计让 benchmark 更像“可持续迭代的数据资产”，而不是一个完全静态的考试卷。

### 4.4 还有 comparative eval

除了单系统打分，仓库还支持两套系统 head-to-head 比较。

它会：

- 先合并两边检索到的文档，跑同样的 correction
- 再把两边答案交给 judge 做 pairwise preference
- 同时保留每个系统自己的 completeness / recall / invalid extra docs

这对于比较两个 RAG pipeline 的实际 trade-off 很有用。你不只是知道 A 的平均分比 B 高，还能知道 A 是因为更完整、还是因为更少 hallucination、还是因为 retrieval 更干净。

## 5. 三个具体例子

下面这部分最能说明这个 benchmark 的味道。

### 例子 1：一个看似简单、但确实来自企业 PR 文档的 basic 题

问题：

> What are the default size limits for file uploads and total request size for the new multipart upload support on the OpenAI-compatible API endpoints?

gold answer：

> The default limits are 10 MiB per file (max_file_size) and 50 MiB total per request (max_total_request_size) for multipart uploads on the OpenAI-compatible endpoints.

对应 gold doc：

- `dsid_ae068ee4aa9640159427cd941bef0238`
- 路径：`github/pr-18421-multipart-file-validation-limits.json`
- 标题：`add multipart/form-data handling, strict content-type validation, and payload limit enforcement for API tool/file inputs`

文档里的关键信息非常直接：

- 增加 multipart/form-data 解析
- 对每个 part 做 Content-Type 校验
- 默认限制：
  - `max_file_size = 10MiB`
  - `max_total_request_size = 50MiB`
  - `max_parts_count = 20`

这个例子说明两件事：

1. benchmark 里的“简单题”依然是企业内部风格，不是百科题。
2. gold doc 不是 polished FAQ，而可能就是一份 GitHub PR 描述和 review thread。

### 例子 2：同样是 basic 题，但答案藏在 review comment 里

问题：

> What is the name of the new metric added so SRE can track when server-side streaming sessions get finalized due to hitting the time limit?

gold answer：

> The new metric is `stream.timebox_finalized` (with labels for route and model).

对应 gold doc：

- `dsid_9550250a59e74f1bbd5612480b2e7100`
- 路径：`github/pr-129874-timebox-abort-idempotency-resume-openai-compat.json`
- 标题：`introduce-server-timebox-and-idempotent-cancel-fallbacks-for-streaming-compat`

这份文档的主体是一个 PR 描述，讲的是：

- 给 streaming session 加 server-side timebox
- client cancel 做 idempotent handling
- resume token 里保留 tool-call idempotency metadata

但真正回答问题的关键点，出现在 review comments：

- reviewer 提出“加一个 metric 给 SRE 看 timebox finalization”
- 作者回复“added metric `stream.timebox_finalized` with labels route/model”

这很像真实企业检索：你不能只看 PR title 或正文，有些答案就埋在评论线程里。

### 例子 3：一题必须召回两份 runbook 的 completeness 题

问题：

> What is the procedure for an emergency rollback of a Serving Runtime release (Hosted and Dedicated)?

gold answer 很长，核心意思是：

- 先暂停正在进行的 progressive rollout
- 把 runtime re-pin 到已知稳定 tag
- 触发 redeploy
- 验证健康指标
- Hosted 和 Dedicated 的执行对象、节奏和稳定性观察窗口不同

对应的 gold docs 有两份：

- `dsid_f6e3b7ad413142019dbb5a5fed07f548`
  - `confluence/eng-serving-runtime/runbooks/emergency-rollback-serving-runtime-hosted-dedicated.json`
  - 标题：`Emergency rollback: Serving Runtime (Hosted + Dedicated)`
- `dsid_840703a1cc37438a84e9beb68029d80b`
  - `confluence/eng-infra/ci-cd-and-build/runtime-release-pipeline-rollback-procedure.json`
  - 标题：`Runtime release pipeline: rollback procedure`

第一份 runbook 更偏“什么时候该 rollback、谁负责、Hosted/Dedicated 分别怎么控风险”。

第二份 runbook 更偏“流水线具体怎么回滚”，包括：

- pause rollout controller
- pin runtime release tag
- trigger redeploy
- verify metrics
- lock tag 防止自动前滚

这题非常典型。只召回第一份，你知道 rollback 原则，但缺少流程动作。只召回第二份，你知道命令步骤，但不知道 Hosted / Dedicated 的 operational context 和验证窗口。只有两份都到位，答案才完整。

这正是 `completeness` 题型要测的东西：不是 top-1 对不对，而是你有没有把“必须文档”全部拿到。

如果把这题再拆细一点，可以更直观看出为什么它是 `completeness`：

- 文档 A 提供“何时回滚、谁负责、Hosted / Dedicated 各自的 operational procedure”
- 文档 B 提供“pause rollout、set tag、deploy、verify、lock tag”的流水线动作

而 `answer_facts` 则把这两份文档里的信息重新拆成 12 个原子点。你的答案每漏一类信息，`completeness` 就往下掉。

所以 `completeness` 不是在测“有没有找到一个最相关文档”，而是在测：

- 你的召回是否把所有必要证据都拿到了
- 你的 answer synthesis 是否把这些证据真正合并进最终回答里

## 6. 它真正测到的是什么

我觉得这个 benchmark 真正测的，不是某一种 retrieval 算法，而是下面四层能力的组合：

### 6.1 术语层

企业数据里充满内部术语、项目代号、缩写和路径线索。

如果你的系统只会做通用语义匹配，不会利用 source type、目录结构、项目聚类、文档标题模式，效果会吃亏。

### 6.2 证据层

很多题不是“找到相关文档”就够了，而是要区分：

- required evidence
- merely relevant evidence
- misleading evidence

这和真实企业问答几乎一模一样。

### 6.3 聚合层

`project_related`、`completeness`、`high_level` 这些题，本质上是在测多文档聚合，而不是单文档查找。

### 6.4 边界层

`conflicting_info` 和 `info_not_found` 这两类题，测的是系统是否知道“什么时候不能乱答”。很多系统在这两类题上会暴露出过度自信。

## 7. 我觉得它的强项和局限

### 强项

第一，企业味很浓。

不是那种“把公开文档换个壳叫 enterprise”的做法，而是真的把 GitHub PR、Slack、Confluence、Linear、邮件这些内部系统放进来了。

第二，失败模式覆盖得好。

它不是只会造 semantic search 题，而是系统性覆盖了多文档、冲突、约束、完整性、不可回答等多种模式。

第三，evaluation 比很多 benchmark 更成熟。

特别是 correction flow，很适合企业语料这种天然存在 annotation incompleteness 的场景。

第四，仓库不只是放数据，还把生成流程也开源出来了。

这意味着你不只是能测，还能照着它的方法论给自己的行业做一套 benchmark。

### 局限

第一，它依然是 synthetic company。

哪怕设计得再认真，Redwood Inference 还是模拟公司，不是真实企业数据。它在 style、noise、冲突分布上肯定比真实世界更“可控”。

第二，它非常依赖 LLM-as-judge。

correctness、fact validation、document correction 都有 LLM judge 参与。这让评估更灵活，但也引入 judge variance 和 provider dependency。

第三，它不是一个纯 retrieval benchmark。

如果你只想比较 retriever，本 benchmark 会把 generation 能力和 retrieval 能力缠在一起。虽然有 `document_recall` 和 `invalid_extra_docs`，但整体设计更偏端到端 RAG。

第四，high-level / info-not-found 题没有 gold docs。

这让这两类题很有现实意义，但也意味着 retrieval 指标在这两类上天然是 `N/A`。

第五，仓库文档有少量漂移。

这次调研里我就碰到了 quickstart 题型计数和当前数据文件不一致的问题。对 benchmark 使用者来说，这不致命，但说明仓库内容在继续演化，复现时要以数据文件本身为准。

## 8. 如果你要拿它来测自己的 RAG，我的建议是什么

如果你的目标是“让这个 benchmark 分数更高”，我会优先改这几件事：

1. 不要只优化 embedding。
   企业题里 source metadata、目录结构、文档类型、项目聚类都很重要。

2. 把 retrieval 做成分层流程。
   先粗召回，再用 source-aware rerank，最后做 answer-time evidence filtering。

3. 单独优化 `info_not_found` 和 `conflicting_info`。
   这两类题往往最能暴露 hallucination。

4. 让系统显式区分 required vs supporting evidence。
   不然很容易出现 answer 还行，但 invalid extra docs 很高。

5. 对 multi-doc 题型单独做上下文打包策略。
   `completeness` 题如果只按 top-k 拼接，常常会漏关键文档。

## 9. 结论

我对 EnterpriseRAG-Bench 的判断是：

它不是“最终版企业 benchmark”，但它很可能是到目前为止最像企业内部知识检索场景的公开 benchmark 之一。

它真正有价值的地方不只是 50 万文档和 500 道题，而是它把企业 RAG 的几个本质难点都明牌写出来了：

- 文档源异构
- 内部术语
- 噪声和错放
- 近重复与冲突
- 多文档聚合
- 不可回答问题
- gold 本身也需要被持续修正

如果你做的是面向企业内网的 RAG，这套 benchmark 很值得测。更重要的是，仓库里的生成方法学和评估流程，本身就可以当成你设计内部 benchmark 的参考蓝图。

## 附录 A：10 个题型各举 1 个例子

下面按“题目 + gold docs”快速列一遍。这样你看每个类型时，不会停留在抽象定义。

### 1. `basic`

- `question_id`: `qst_0001`
- question:
  What are the default size limits for file uploads and total request size for the new multipart upload support on the OpenAI-compatible API endpoints?
- gold docs:
  - `github/pr-18421-multipart-file-validation-limits.json`

### 2. `semantic`

- `question_id`: `qst_0176`
- question:
  When does booking open for the new top end 80GB accelerator on dedicated clusters in the EU Central and India South locations?
- gold docs:
  - `slack/1763876000-dedicated-h200-eu-ap-launch.json`

这个例子像真实 Slack 提问，不直接复述文档标题里的术语。

### 3. `intra_document_reasoning`

- `question_id`: `qst_0301`
- question:
  During the 2025-02-10 capacity incident, what two thresholds should trigger noisy-tenant detection in the runbook update, and how long were SLA targets breached?
- gold docs:
  - `linear/engineering/ENG-847213-reservation-governor-rationalization-and-noisy-tenant-surge-remedy.json`

这类题的关键不是多文档，而是同一长文档内部跨段落取证。

### 4. `project_related`

- `question_id`: `qst_0341`
- question:
  For the Proxima Bank 429 spike after priority routing rollout, what caused the throttling and what temporary policy exception did we apply, and how do we verify it is not burning the enterprise route SLOs?
- gold docs:
  - `jira/ops-requests/SUP-18421-enterprise-429-spike-after-priority-routing-rollout.json`
  - `confluence/eng-sre/slo-and-error-budgets/hosted-api-slos-enterprise-route-tiers.json`

这是典型的“工单 + SLO 文档”联合回答。

### 5. `constrained`

- `question_id`: `qst_0381`
- question:
  In the planned controlled failover game day on 2026-01-15 (Hosted API us-east -> eu-west), what caused the routing automation to oscillate (flip/rollback), and what follow-up ticket and target ship date were created to fix the streaming disconnect/reconnect behavior clients saw during cross-region redirects?
- gold docs:
  - `confluence/eng-sre/incident-review/postmortem-controlled-failover-test-regression.json`
  - `confluence/oncall-and-incident-response/game-days/controlled-failover-test-results-2026-01-15.json`

这类题难点在限定条件多，一堆看起来相关的 failover 文档里，只有少数同时满足所有约束。

### 6. `conflicting_info`

- `question_id`: `qst_0411`
- question:
  On Streamly AI's dedicated pool dp-132-usw, what % of interactive burst credits should be reserved exclusively for priority=high routes?
- gold docs:
  - `jira/ops-requests/SUP-864999-sliced-ingest-priority-class-throttle-config.json`
  - `google_drive/shared_drives/engineering/site-reliability-engineering/sliced-ingest-429s-dedicated-pool-priority-class-debug-notes.json`

gold answer 指明最终值是 30%，同时说明更早建议过 20%。这就是“新旧冲突、要以更新信息为准”的典型场景。

### 7. `completeness`

- `question_id`: `qst_0431`
- question:
  What is the procedure for an emergency rollback of a Serving Runtime release (Hosted and Dedicated)?
- gold docs:
  - `confluence/eng-serving-runtime/runbooks/emergency-rollback-serving-runtime-hosted-dedicated.json`
  - `confluence/eng-infra/ci-cd-and-build/runtime-release-pipeline-rollback-procedure.json`

这题前面已经展开讲过，是“多文档必须全到”的标准例子。

### 8. `miscellaneous`

- `question_id`: `qst_0451`
- question:
  In the team chat about posting jokes when an AI makes things up in production, what tagging requirement did someone propose for the memes?
- gold docs:
  - `slack/memes/1711245600-model-hallucination-memes.json`

这类题故意来自边角目录，不在主干知识结构上。

### 9. `high_level`

- `question_id`: `qst_0471`
- question:
  What is Redwood Inference's mission statement?
- gold docs:
  - 无

这类题的意思不是“没有答案”，而是“没有单一 gold doc”；答案来自公司整体上下文。

### 10. `info_not_found`

- `question_id`: `qst_0481`
- question:
  For the hot-route capacity protection rollout in us-east, which specific enterprise accounts were on the initial allowlist, and what were the exact per-route-group budget values (RPS, estimated TPS, and concurrency) configured for each of those accounts?
- gold docs:
  - 无

这类题测试的是系统是否会明确承认：文档里没有足够信息回答这个问题。
