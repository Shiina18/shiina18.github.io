---
title: "Langchain 团队如何评估与优化 agent harness"
categories: 
- LLM
tags: Agent
updated: 
comments: true
mathjax: false
---

<!-- more -->

## How we build evals for Deep Agents

- LangChain. 2026-03. [How we build evals for Deep Agents](https://www.langchain.com/blog/how-we-build-evals-for-deep-agents).

直接开源了 eval

> Our eval architecture and implementation is open sourced in the [Deep Agents repository](https://github.com/langchain-ai/deepagents/tree/main/libs/evals?ref=blog.langchain.com).

For each eval, add a docstring that explains *how* it measures an agent capability. This ensures **each eval is self-documenting.** We also tag each eval with categories like `tool_use` to enable grouped runs. 用文字描述评估, 打标签分组 (依据测试内容而非来源)

一些标签分组

|     Category      |                                                       What It Tests                                                        |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `file_operations` | File tools (read, write, edit, ls, grep, glob), parallel invocation, pagination                                            |
| `retrieval`       | Finding information across files, search strategies, multi-hop document synthesis                                          |
| `tool_use`        | Selecting the right tool, chaining multi-step calls, tracking state across turns                                           |
| `memory`          | Recalling seeded context, extracting implicit preferences, persisting durable info                                         |
| `conversation`    | Asking clarifying questions for vague requests, sustaining multi-turn dialogue with correct actions                        |
| `summarization`   | Handling context overflow, triggering summarization, recovering info after compaction                                      |
| `unit_tests`      | SDK plumbing - do our system prompt passthrough, interrupt config, subagent routing, skill path resolution, etc. all work? |

### How we curate data

1. Dogfooding
2. Pulling selected evals from external benchmarks (like [Terminal Bench 2.0](https://www.tbench.ai/?ref=blog.langchain.com) or [BFCL](https://gorilla.cs.berkeley.edu/leaderboard.html?ref=blog.langchain.com)) and often adapting them for a particular agent. 从现成 benchmark 里取相关的评估并改造
    - For coding tasks, we integrate with [Harbor](https://github.com/laude-institute/terminal-bench?ref=blog.langchain.com) to run selected tasks from datasets like [Terminal Bench 2.0](https://www.tbench.ai/leaderboard/terminal-bench/2.0?ref=blog.langchain.com) tasks in sandboxed environments.
3. Writing our own (artisanal) evals and unit tests by hand for behaviors we think are important.
    - Many evals are written from scratch and act as focused tests to observe isolated behavior, like testing a `read_file` tool.
    
### How we define metrics

除了常规的规则匹配, LLM judge 等, 还评估效率.  The metrics we measure for each evaluator run are:

|     Metric      |                                             Definition                                              |
| --------------- | --------------------------------------------------------------------------------------------------- |
| Correctness     | Whether the model completed the task correctly                                                      |
| Step ratio      | Observed agent steps / ideal agent steps                                                            |
| Tool call ratio | Observed tool calls / ideal tool calls                                                              |
| Latency ratio   | Observed latency / ideal latency                                                                    |
| Solve rate      | Number of expected steps / observed latency, with a score of 0 if the task was not solved correctly |

其中 ideal trace 是最小步数 (包括 parallel tool call) 做完的 trace.

### How we run evals

We use pytest with GitHub Actions to run evals in CI so changes run in a clean, reproducible environment. 可复现.

We can also run a subset of eval using tags save costs and measure targeted experiments. For example, if building an agent that requires a lot of local file processing and synthesis, we may focus on the `file_operations` and `tool_use` tagged subsets. 节约成本只跑相关标签分组的 eval

## Improving Deep Agents with Harness Engineering

- LangChain. 2026-03. [Improving Deep Agents with Harness Engineering](https://x.com/Vtrivedy10/status/2023805578561060992)

提升  Terminal Bench 2.0 排名.

![](https://shiina18.github.io/assets/posts/images/415973014260551.png)

![用 skill 分析 trace](https://shiina18.github.io/assets/posts/images/197863114278977.png "用 skill 分析 trace")

### Build & Self-Verify

Self-verification allows agents to self-improve via feedback within a run. However, they don’t have a natural tendency to enter this build-verify loop.

We added guidance to the system prompt on how to approach problem solving. 

- Planning & Discovery
- Build
- Verify
- Fix

做了个类似 ralph loop 的 hook 让 agent 退出循环前先验证通过.

### Giving Agents Context about their Environment

看起来是对 terminal bench 特化调提示词.

### Encouraging Agents to Step Back & Reconsider Plans

通过 hook 检测如果编辑同个文件多次, 则注入提示词提醒 agent 换种方法.

### Choosing How Much Compute to Spend on Reasoning

因为 terminal bench 有时间限制, 不能无脑开 xhigh thinking.

## 代码

### 设计原则

1. **每个 eval 只测一个行为**。不是"这个 Agent 好不好"，而是"Agent 能不能并行读取两个文件"。
2. **两层断言**：正确性（必须通过）和效率（记录但不阻塞）。Agent 做对了就过，做得快慢是优化指标。
3. **所有评测结果追踪到 LangSmith**，团队任何人都能看 trace、分析失败原因。

### 两级测试策略

每个 eval 被标记为 **baseline**（基础）或 **hillclimb**（爬坡）：

- **baseline**：回归门槛——当前模型必须通过。失败意味着功能退步，需要立即修复。
- **hillclimb**：进度跟踪——当前模型可能过不了。用来追踪改进趋势，不阻塞 CI。

可以通过 `--eval-tier baseline` 只跑基础测试，`--eval-tier hillclimb` 只看爬坡进度。

---

### 1. 文件操作（file_operations） — 全部 baseline

**测什么**：Agent 能否正确使用文件工具——读、写、编辑、列目录、搜索内容，并且在合适的时候并行调用多个工具。

给 Agent 一些预先放好的文件，然后让它执行各种文件任务：

- 读一个文件，告诉我第 2 行第 3 个词是什么
- 把"bar"同时写到两个文件里（应该一步并行完成，而不是串行写两遍）
- 先写两个文件，再同时读回来验证（先并行写，再并行读）
- 把文件里所有的"cat"替换成"dog"
- 读一个 300 行的文件并告诉我最后一行内容（需要翻页才能看到尾部）
- 读一个空文件，应该说"EMPTY"而不是编造内容
- 问"2+2 等于几"——不需要用任何工具，直接回答就行（测 Agent 不会乱调用工具）
- 用 grep 找哪些文件包含"needle"这个词
- 用 glob 列出所有 .md 文件
- 在深层嵌套目录里找一个特定标记（应该用 grep 一步定位，而不是逐层翻目录）
- 在 5 个引用文件中找出哪个是 Grace Hopper 说的（应该先 ls，再并行读所有文件）
- 同上但不告诉 Agent "要高效"——看它是否自发地并行读取

**效率预期**：每个任务都定义了"理想轨迹"——几步完成、调用几次工具、每步调什么。Agent 如果多绕弯子，效率指标就会变差。

### 2. 检索（retrieval）

**测什么**：Agent 能否跨越多个文件找到信息，并组合出答案。

- 从外部 benchmark FRAMES 精选了 5 个困难案例：需要多跳检索（先找 A 文件拿到一个线索，再用线索去 B 文件找答案），有的还涉及算术或时间推理
- 从 Nexus 精选了 5 个困难案例：需要 4-6 层嵌套的函数组合推理

这些案例的数据预先放入 Agent 的工作空间作为文件。Agent 必须用文件工具找到答案。评分方式：检查最终回答是否包含标准答案的关键片段。

### 3. 工具选择（tool_selection）

**测什么**：给 Agent 8 个模拟工具（Slack 发消息、发频道消息、GitHub 创建 issue/PR、Linear 创建 issue、Gmail 发邮件、网页搜索、日历创建事件），看它能不能选对工具。

分三种难度（3 个 baseline，5 个 hillclimb）：

- **直接请求**（hillclimb）："用 Slack 给 U12345 发一条消息"、"创建一个 PR"
- **多工具同时调用**（baseline）："在 Linear 和 GitHub 上都建个 issue"
- **间接请求**：日历（baseline）、Slack 频道通知（hillclimb）、Gmail 发邮件（hillclimb）
- **多步链式**：搜索再发邮件（baseline）、创建 issue 再通知 Slack（hillclimb）

同时测 Agent 能不能一次调用多个工具（比如用户说"在 Linear 和 GitHub 上都建个 issue"）。

### 4. 工具使用——关系数据（tool_usage_relational） — 全部 baseline

**测什么**：Agent 能否通过 ID 关联的多步查询获取信息。

模拟了一个小数据库：6 个用户、5 个城市、7 种食物，通过 ID 互相关联。每个工具只能查一个属性（比如"查用户所在城市"返回的是城市 ID，不是城市名）。

从简单到复杂的测试：
- **1 步**：列出所有用户 ID
- **2 步**：查用户 21 的邮箱（先拿到用户信息再提取邮箱）
- **3 步**：当前用户住在哪个城市？（获取当前用户 ID → 获取位置 ID → 获取城市名）
- **4-5 步**：当前用户最喜欢的食物分别叫什么？（拿到食物 ID 列表后，应该并行查所有食物名称）
- **最复杂**：找到 Eve 的邮箱、所在城市、以及每种最爱食物的名字、热量和过敏原——总共需要 14 次工具调用，理想轨迹是大量并行

这个 suite 同时测量正确性和并行化效率。

### 5. 工具使用——事件管理（tool_usage_incident_graph） — 全部 baseline

**测什么**：在更复杂的业务域中做同样的链式查询和聚合推理。

模拟了一个运维事件管理系统：工程师、团队、服务、仓库、手册、环境、事件、告警、部署、指标——10 种实体通过 ID 互相关联，约 35 个工具。

测试覆盖：
- **简单查询**：列出所有事件 ID
- **链式查找**：当前事件影响了哪个服务？→ 这个服务属于哪个团队？→ 谁在值班？
- **并行查询**：事件 41043 的标题、严重程度和状态是什么？（三个独立查询应该一步并行发出）
- **聚合推理**：每个团队有多少个活跃事件？哪个最多？（需要遍历所有事件、过滤活跃的、查服务归属、查团队名称）
- **跨域推理**：哪个活跃事件的服务依赖了 identity-api？那个服务的值班工程师是谁？（事件 → 服务 → 依赖列表 → 筛选 → 团队 → 工程师）

### 6. 工具使用——状态追踪（todos） — 全部 baseline

**测什么**：Agent 能否通过同一个工具反复修改同一份数据，每次都基于上一次的结果。

让 Agent 创建一个 5 项的待办清单（比如"煮咖啡、喝水、查日历、写计划、开始第一个任务"），然后逐步标记每一项为完成。每次只改一项，5 次更新。这测的是 Agent 的状态追踪能力——它需要记住上一步的结果，而不是从零开始。

### 7. 记忆（memory） — 全部 baseline

分三组测试：

#### 7a. 记忆加载（test_memory，10 个测试）

给 Agent 预先写入的"记忆文件"，看它能不能：
- 读到项目名并回答"项目叫什么？"
- 遵循记忆中的命名规范：记忆里说"所有配置文件必须用 config_ 前缀"，用户让创建 `/api.txt`，Agent 应该自动创建 `/config_api.txt`
- 遵循记忆中的代码风格：记忆里说"每个函数都要写 # Purpose: 注释"，Agent 写代码时应该照做
- 从多个记忆文件组合信息（"你用什么语言？" + "项目用什么框架？"）
- 记忆文件不存在时不崩溃、不编造
- 已经在记忆里有的信息，不应该再读一遍文件
- 临时信息（"我在咖啡店"）不应该被持久化到记忆文件
- 用户说"以后用 bullet points"，应该写入记忆文件作为持久偏好

#### 7b. 多轮记忆（test_memory_multiturn，9 个测试）

模拟多轮对话，看 Agent 能不能从对话中提取偏好并持久化：

- **隐式提取**：用户说"我不懂 JavaScript，只看 Python 的 PR"——Agent 应该自己意识到"哦，这个人只做 Python"并写入记忆
- **显式指令**："记住，以后别用 emoji"——直接写入
- **不该记住的**：用户说"今天好累"然后让改个变量名——Agent 不应该把"累了"写入记忆

记忆写入的质量用 LLM judge 来评估（而不是简单子串匹配），确保写入的是简洁的偏好而不是一大段对话原文。

#### 7c. MemoryAgentBench（ICLR 2026 论文 benchmark）

从 HuggingFace 加载数据。测试两种策略：
- **长上下文策略**：把材料分块喂给 Agent，然后提问
- **文件检索策略**：把材料放到文件里，Agent 自己搜索

两种维度：
- **冲突解决**：前面说"小明在北京"，后面说"小明搬到了上海"，问"小明在哪"——应该回答上海
- **测试时学习**：给一些分类规则和示例，然后问新样本的分类

### 8. 上下文溢出与摘要（summarization）

**测什么**：当对话太长超出上下文窗口时，Agent 能不能正确处理。

5 个测试，每个都很不同：

1. **摘要触发后继续工作** — baseline：故意把上下文窗口设小（15k），让 Agent 读一个大文件。验证摘要确实被触发了，而且 Agent 在摘要后还能继续读文件（而不是丢失进度）
2. **历史卸载到文件** — baseline：摘要后对话历史应该被保存为 markdown 文件。然后做一个"大海捞针"测试——追问摘要前读过的内容细节（"文件里第一个标准库 import 是什么？"），Agent 应该从历史文件中找到答案
3. **切换任务时压缩** — baseline：给一个长对话，然后突然切换到完全不相关的任务——Agent 应该主动调用"压缩对话"工具
4. **不该压缩时别压缩** — hillclimb：长对话后追问一个相关问题——Agent 不应该压缩（因为上下文还有用）
5. **又要读大文件** — hillclimb：长对话后让 Agent 读另一个大文件——上下文快满了，应该压缩

### 9. 对话质量（conversation）

#### 9a. 追问质量 — 全部 hillclimb

给 Agent 模糊的用户请求，看它会不会问出恰当的追问：

- "分析我的数据"——应该问：什么数据？哪种分析？不应该假设数据格式
- "每周给我的团队发报告"——应该问：报告包含什么？怎么发？不应该问"每周"（用户已经说了）
- "监控生产系统出问题了提醒我"——应该问：什么指标算"出问题"？怎么通知你？不应该自己假设阈值
- "每天总结我的邮件"——应该问：总结多详细？不应该问"哪些邮件"（用户说了"我的邮件"就是全部）
- "帮客户更快地回复"——应该问：客户问题从哪来？什么领域？不应该问"要不要自动化"（不明确时才问）
- "每天早上 5 点看日历发简报"——只需问一个：发到哪里？不应该问时间和范围（用户已经给了）

用 LLM judge 评估追问是否恰当。

#### 9b. τ²-bench 航空客服 — 全部 hillclimb

来自 Sierra Research 的 τ-bench 系列。模拟一个航空客服场景：

- 完整的航空业务域：航班、机票、座位、行李、会员等级、改签政策等
- 用另一个 LLM 扮演用户，和 Agent 进行最多 30 轮真实对话
- 每个任务有具体的场景（比如"用户要改签航班，但只有银卡会员才能免费改签"）
- 评估两件事：①数据库状态是否正确（票改对了没）②Agent 是否向用户传达了关键信息（比如"改签需要额外收费"）

这是最难的一组测试，因为需要 Agent 同时做到：理解业务规则、在多轮对话中保持一致、正确操作数据库、和用户沟通清楚。

### 10. 外部基准（external_benchmarks） — baseline 与 hillclimb 混合

从三个公开 benchmark 各精选了 5 个困难案例。每个案例的运行方式不同，但核心思路一样：给 Agent 一组工作空间文件或工具，让它完成一个有标准答案的任务，然后对比结果。

#### 10a. FRAMES — 多跳检索 + 推理

**来源**：FRAMES benchmark（Google DeepMind）
**测什么**：Agent 需要在多个文件之间跳转查找信息，然后做推理或计算才能得到答案。

**怎么运行**：每个案例预先往工作空间放入 3-6 个文本文件，每个文件包含一条线索。Agent 的系统提示告诉它"只看这些文件来回答问题"。评分方式：检查最终回答是否包含标准答案片段。

**5 个精选案例：**

1. **frames_10 — baseline**（5 个文件 + 1 个干扰项）：问题是"1997 年 12 月 6 日 SNL 主持人拿过几个托尼奖，乘以 Greta Gerwig 2023 年电影的奥斯卡提名数，再除以 1979 年专辑 Tusk 那个乐队拿过的格莱美奖数"。Agent 需要找到一个文件知道主持人是 Nathan Lane，另一个文件知道他拿了 3 个托尼奖，又一个文件知道 Barbie 拿了 8 个奥斯卡提名，还有一个文件知道 Fleetwood Mac 拿了 2 个格莱美。最后计算 3 × 8 ÷ 2 = **12**。还有一个干扰文件提到 Little Women，也是 Gerwig 导演的但不是 2023 年的——Agent 需要区分。

2. **frames_11 — baseline**（5 个文件）：把轧棉机、真空泵、商业卫生纸发明人的 2010 年年龄加起来，减去安全别针和缝纫机发明人的年龄。每个文件单独给出一个发明人的"2010 年年龄"，Agent 需要全部找到并计算 (245 + 363 + 183) - (84 + 85) = **622**。

3. **frames_12 — hillclimb**（3 个文件）：三个人分别在黑斯廷斯战役、火药阴谋处决日、伦敦 2012 开幕式时过了 10/12/14 岁生日。谁在某个比较日期最老？Agent 需要从"事件日期"文件算出生年，再用"比较日期"文件算各人年龄并比较。答案取决于比较日期（亨利一世去世 1135 年、纳西比战役 1645 年、特拉斯辞职 2022 年），需要一步步算出 Edmund 在所有比较日期都是最老的。

4. **frames_16 — baseline**（6 个文件 + 1 个干扰项）：一条知识链——Joan Didion 的第二本小说 → 电影改编导演 Frank Perry → 他是 Katy Perry 的叔叔 → Katy Perry 的哪首歌在第 54 届格莱美被提名"最佳流行独唱表演"和"年度唱片"→ 那首歌受哪本书启发？答案是 **Firework** 和 **On the Road**。有一个干扰文件提到 Roar 也是 Katy Perry 的歌，但不是这道题的答案。

5. **frames_18 — baseline**（5 个文件 + 1 个干扰项）：找出同一年在同一个国家举办过冬季和夏季奥运会的年份，然后看哪一年的女性参赛者总和最多。文件给出了 1924/1932/1936 三年的数据，需要分别加总后比较：1924 = 148、1932 = 143、1936 = 411，答案是 **1936**。干扰文件提到 1984 年，但那年的冬奥和夏奥不在同一个国家。

#### 10b. Nexus — 深层函数组合

**来源**：Nexus benchmark
**测什么**：Agent 需要阅读 API 文档文件，然后写出正确的嵌套函数调用表达式。不是实际调用 API，而是组合出正确的调用链。

**怎么运行**：每个案例给 2 个文件（API 文档 + 具体参数说明），Agent 写出表达式，评分检查表达式是否包含标准答案的关键片段。

**5 个精选案例：**

1. **nexus_nvd_nested_13 — baseline**（NVD 漏洞数据库 API）：需要先用 `searchCVE` 搜索 Microsoft Exchange Server 2013 的 CPE 记录，再用 `filterDeprecatedCPEs` 过滤掉已弃用的，取第一个结果的 CPE 名称，最后用这个名称再搜索相关漏洞。组合出来是嵌套的：`searchCVE(cpeName=getCPEName(get_first_object_from_list(filterDeprecatedCPEs(searchCVE(...)))))`。

2. **nexus_nvd_nested_14 — baseline**（同上）：用精确关键词搜索"Windows"，过滤弃用，取第一个的 CPE 名称，再搜漏洞。同样的 API 但不同的搜索路径。

3. **nexus_placesapi_15 — hillclimb**（地点推荐 API）：两个并行请求——"在我当前位置附近找好吃的"和"在 Reno 附近找好吃的"。每个都需要先获取经纬度，再获取推荐，再按距离排序。Agent 需要写出两条独立的嵌套调用。

4. **nexus_multiversemath_17 — baseline**（数学函数 API）：用文档中提供的 `sin`、`cos`、`add`、`negate`、`pi`、`power` 等函数组合出四个数学表达式的值。比如 `sin(π) - sin(-cos(8 + π))` 需要翻译成 `subtract(a=sin(radians=pi()), b=sin(radians=negate(a=cos(radians=add(a=8.0, b=pi())))))`。

5. **nexus_multiversemath_18 — hillclimb**（同上）：类似但表达式不同，包括 `π^(-(cos(5) + sin(0)))` 这样的嵌套。

#### 10c. BFCL v3 — 多轮有状态工具调用

**来源**：BFCL (Berkeley Function Calling Leaderboard) v3
**测什么**：Agent 需要在多轮对话中调用有内部状态的 API（有持久化的数据），执行一系列操作。对话结束后，对比 Agent 操作后的 API 内部状态和标准答案的状态是否完全一致。

**怎么运行**：为每个案例实例化真实的 API 对象（不是 mock），所有方法调用会修改内部状态（比如余额、票队列、消息列表）。Agent 通过多轮对话逐个完成任务。评分：把 Agent 执行后的每个 API 属性值和标准答案逐个对比，任何不一致就判失败。

**5 个精选案例：**

1. **multi_turn_composite_97 — hillclimb**（消息 API + 车辆控制 API，8 轮）：
   - 第 1-2 轮：用户问两个城市之间的距离（Agent 需要用地图 API 查询）
   - 第 3-4 轮：担心油不够，要求加满油箱（调车辆 API 的加油方法）
   - 第 5-6 轮：启动汽车
   - 第 7 轮：给朋友发消息（调消息 API）
   - 第 8 轮：查看收件箱

2. **multi_turn_composite_116 — baseline**（交易机器人 API，8 轮）：
   - 查看股票观察列表
   - 从列表中移除 Zeta Corp
   - 查看 Omega Industries 的股票详情
   - 列出科技板块的所有股票
   - 充值 $10,000 到账户
   - 以 $150/股买入 50 股 AAPL
   - 最终验证：账户余额、持仓、观察列表都应该正确更新

3. **multi_turn_composite_199 — hillclimb**（消息 API + 旅行 API，7 轮）：
   - 用欧元订一张洛杉矶到纽约的商务舱机票
   - 查看发票
   - 联系客服反映订票问题
   - 把情况告诉同事 Kevin
   - 汇总所有回复

4. **multi_turn_miss_func_55 — hillclimb**（工单 API + 车辆控制 API，6 轮）：
   - 如果油量低于 10 就加两倍，然后启动引擎
   - 检查胎压
   - 开一个"胎压问题"的紧急工单
   - 查看这个工单的状态
   - 标记工单为已解决

5. **multi_turn_miss_param_55 — baseline**（工单 API + 车辆控制 API，6 轮）：
   - 和上一个案例几乎相同，但第 1 轮用户故意漏说了"低于多少"这个参数，第 2 轮才补上"低于 10"
   - 这测试的是 Agent 在信息不完整时能不能正确处理——不应该在第一轮就调用加油工具

**为什么选这些**：这 15 个案例（5×3）是各 benchmark 中最困难、模型表现最差的子集。能在这上面拿高分，意味着 Agent 在真实场景中也不会差。

### 11. SDK 集成测试（unit_test） — 全部 baseline

这些不测模型能力，而是测框架本身有没有正确工作：

- **系统提示穿透**：设置了系统提示"你叫 Foo Bar"，问 Agent 名字，应该回答 Foo Bar
- **子 Agent 委托**：通过 task 工具把任务分给命名的子 Agent
- **人工审核中断**：配置了"某些工具需要人工批准"，验证 Agent 会在正确的时候暂停等待
- **Skill 发现与使用**：Agent 能找到 skill 文件、按名字选择正确的 skill、并行读多个 skill、编辑 skill 文件