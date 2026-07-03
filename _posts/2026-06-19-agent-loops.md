---
title: "读 Agent 新趋势 - goal, loop 和 loop engineering"
categories:
- LLM
tags: Agent
updated:
comments: true
mathjax: false
---

Written by Codex with GPT-5.5 high

最近 AI coding 圈又出了一个新词: `loop engineering`.

如果只看 high level, 我现在会把它理解成一句话:

> prompt engineering 是你怎么提示 agent; harness engineering 是你怎么给 agent 搭工作环境; loop engineering 是你怎么让一个系统代替你去提示 agent、检查结果、记录状态、决定下一步.

这不是说 prompt 没用了. 恰恰相反, loop 里面仍然到处都是 prompt, 只是你的工作重心从“一条一条写 prompt”挪到了“设计一个会不断产生 prompt 的系统”.

这篇主要想讲清楚四件事: `goal` 和 `loop` 到底差在哪, Codex / Claude Code / Cursor 各自怎么实现, 为什么最近大家说的 loop engineering 已经不只是一个 `/loop` 命令, 以及真正有用的 loop 应该留下些什么东西.

<!-- more -->

## 先看主线

过去用 coding agent, 很像人在旁边手动打拍子: “改这里”, “跑测试”, “失败了再修”, “再跑一遍”, “开 PR”. Agent 能做很多事, 但每一步通常都等你推一下.

Loop engineering 的想法是把这个节奏外置出来. 你设计一套机制, 它会在合适的时候唤醒 agent, 告诉 agent 该处理什么, 让 agent 执行、验证、记录结果, 然后根据结果决定下一步. 换句话说, 你不再总是那个亲手提示 agent 的人, 而是在设计一个会提示 agent 的系统.

我觉得最有用的拆法, 是把 harness 分成两层: 里面一层是 `agent loop`, 也就是 Claude Code / Codex / Cursor 这类 agent runtime 如何完成一个给定任务; 外面一层是 `outer loop`, 负责决定什么值得做、什么时候触发、状态放哪、多个 loop 怎么共享信息、结果怎么反哺下一次. Addy Osmani 在 [Loop Engineering](https://addyosmani.com/blog/loop-engineering/) 里说它 sits one floor above the harness, 这个说法很准: harness 让一个 agent run 能工作, loop 让一组 agent run 能自己找活、验收、记录、继续.

所以现在我会这样分:

```text
agent loop  = 给定一个任务, agent 如何完成它
outer loop  = 系统如何决定下一个任务、触发 agent、保存结果、继续学习
```

`/goal`、`/loop`、Codex automations、Cursor 里可以用 skill 或 shell watcher 拼出来的 loop, 都只是 outer loop 的具体触发手段. 真正的 loop engineering 是把触发、状态、工具、验证、记忆、升级路径组合起来.

## 1) goal 和 loop 的区别

`goal` 和 `loop` 经常被混在一起讲, 因为它们都会让 agent “自己继续”. 但它们问的是两个不同问题.

`goal` 问的是: 目标完成了吗? 如果没完成, 再跑一轮; 如果完成, 停. 所以它是条件驱动. 典型例子是“修到所有测试通过”“迁移完整个模块并验证”“调研到能给出明确结论”.

`loop` 问的是: 什么时候再跑? 到时间了、事件来了、watcher 看到变化了, 就唤醒 agent. 所以它是时间或事件驱动. 典型例子是“每 5 分钟检查部署状态”“CI 结束后继续处理”“commit 前跑测试”.

可以把它们压成两行:

```text
goal: continue until condition is true
loop: wake up when schedule/event says so
```

这两者经常组合. 比如一个 CI 修复系统可以是: 每 5 分钟或 CI webhook 触发一次, 读最新失败, 目标是 PR checks 全绿, 每轮用 `gh pr checks` 验证. 时间/event 是 loop, checks 全绿是 goal.

## 2) Claude Code: `/goal` 是条件, `/loop` 是调度

Claude Code 现在的两个概念正好对应上面这组区别.

`/goal` 是 session-scoped 的目标机制. 你写一个可验证条件, agent 每轮执行后, 会有一个独立的小模型判断目标是否已经达成. 没达成就继续, 达成就清掉 goal. 这里最关键的是 maker/checker 分离: 写代码的 agent 不直接给自己的完成状态盖章, 另一个模型来判断“算不算 done”.

`/loop` 则更像 scheduled task. 你可以写 `/loop 5m check deploy`, 让它按固定间隔唤醒; 也可以不写间隔, 让 agent 自己判断下一次多久后再查. 它解决的是 cadence, 不是 completion.

所以这两个命令的心智模型完全不同. `/goal fix auth tests until green` 是让 agent 追一个结束条件; `/loop 5m check auth deploy` 是让 agent 周期性观察一个外部状态. 前者适合一次性但多轮的任务, 后者适合持续监控.

## 3) Codex: goal 是持久 thread state

Codex 的 goal 和 Claude Code `/goal` 看起来像, 但实现重心不一样. Claude Code 更像 session 里的 Stop hook/evaluator wrapper; Codex 更像 thread 上的一份持久状态.

源码里的核心状态是:

```rs
pub enum ThreadGoalStatus {
    Active,
    Paused,
    Blocked,
    UsageLimited,
    BudgetLimited,
    Complete,
}
```

这几个状态说明它不是简单 while loop. 它要处理用户暂停、真实阻塞、用量限制、token budget、完成状态. app-server 也有明确 API:

```text
thread/goal/set
thread/goal/get
thread/goal/clear
thread/goal/updated
thread/goal/cleared
```

模型侧暴露的是 `get_goal`、`create_goal`、`update_goal`. 其中 `create_goal` 要求必须由用户或系统显式请求, 不能从普通任务里自动脑补一个 goal; `update_goal` 也只能标 `complete` 或 `blocked`, 不能让模型自己暂停、resume、标 budget-limited 或 usage-limited. 这些状态由用户或系统控制.

真正让 Codex goal 像 loop 的地方在 runtime. 当 thread idle 且当前 goal 仍是 `Active`, runtime 会注入一条 continuation steering item, 再尝试启动下一轮. high level 是:

```text
read current goal from state db
if status is Active:
  inject "continue working toward the active thread goal"
  start another turn if thread is idle
else:
  clear active accounting
```

所以 Codex goal 我会记成: `持久 thread goal + idle continuation + token/time accounting`. 它不是 cron, 也不是 shell loop; 它是一个挂在 thread 上的状态机.

## 4) Cursor: 可以用 shell sentinel 做 wakeup

Cursor 官方公开文档里我没找到等价的内建 `/goal` 或 `/loop`, 但可以用 Cursor skill 的方式拼出类似机制. 这种实现很朴素, 也很实用: 固定间隔时, 启动一个后台 shell:

```bash
while true; do
  sleep <seconds>
  echo 'AGENT_LOOP_TICK_<purpose> {"prompt":"<prompt>"}'
done
```

重点不是 `while true`, 而是 stdout 里的 sentinel. Agent 监控后台终端输出, 看到 `AGENT_LOOP_TICK_*` 后读取 JSON 里的 prompt, 再执行下一轮.

动态模式也类似, 只是每轮结束后 arm 一个 one-shot sleeper:

```bash
sleep <seconds>
echo 'AGENT_LOOP_WAKE_<purpose> {"prompt":"<prompt>"}'
```

如果下一轮更适合由事件触发, 它还会让 agent arm watcher, 比如 git ref 前进、文件变化、CI 完成、日志出现某个匹配. 这个实现比 Claude `/loop` 更“手工”: Claude 是产品内置 scheduling primitive, Cursor 这类方案是 agent 用 shell 和 monitored output 搭出来的小调度器.

## 5) Codex automations: 更接近 outer loop

如果只看 Codex TUI, 容易把 loop engineering 和 `/goal` 绑死. 但从 Codex Desktop 的 automations 看, 它已经更接近 outer loop: 你定义一个定时任务, 绑定 workspace、prompt、model、reasoning effort, 到点后启动一个独立运行. Thread heartbeat 则更像“让当前线程稍后醒来继续”.

这里可以把 automation 理解成 outer loop 的 heartbeat: 它负责 discovery / triage, 找到东西后落到 inbox、thread、PR 或 artifact. `/goal` 是让一个线程追一个条件, automation 是让系统定期产生或推进工作. 前者是“这个任务何时 done”, 后者是“什么时候再扫一遍世界”.

所以在 Codex 里我会这样分:

```text
/goal or thread goal      单个 materialized thread 的长期目标
heartbeat automation      当前 thread 的稍后继续
cron/worktree automation  独立周期任务, 可产出新工作
```

这三者都可以参与 loop engineering, 但层级不同.

## 6) loop engineering 的五件套

如果从实现角度看, 一个 loop 的最小形态是三件事: 明确目标和停止条件、反馈闭环、状态记忆. 再往上做, 就会自然长出 automations、worktrees、skills、plugins/connectors、sub-agents、外部 memory 这些东西. Addy 的拆法也差不多: automations 是 heartbeat, worktrees 负责并行隔离, skills 沉淀项目知识, plugins/connectors 接真实工具, sub-agents 做 maker/checker 分离, 最后再加一份 conversation 外的 memory. 这套分类有一个好处: 它把“loop”从神秘概念拉回了工程部件.

我会把这些合并成一个更工程化的公式:

```text
Loop = Trigger + State + Harness + Skill + Verifier + Memory
```

`Trigger` 负责唤醒, 可以是 cron、webhook、hook、watcher、另一个 agent. `State` 负责让下一轮知道上一轮做了什么, 可以是 `PROGRESS.md`、Linear board、domain README、artifact timeline. `Harness` 负责让 agent 真能跑起来, 包括可执行环境、测试、沙箱、worktree. `Skill` 负责沉淀项目知识, 避免每轮重学. `Verifier` 负责判断结果是否可信, 最好和 maker 分离. `Memory` 负责跨 loop 复利, 让一个 loop 的发现能被另一个 loop 读到.

这个公式里, 最容易被低估的是 `State` 和 `Memory`. 没有它们, loop 只是定时重复 prompt; 有了它们, loop 才能跨 session 继续, 多个 loop 才能互相学习.

LangChain 的 [The Art of Loop Engineering](https://www.langchain.com/blog/the-art-of-loop-engineering) 给了另一个很有用的分层: 第一层是 agent loop, 模型拿上下文、调工具、直到任务完成; 第二层是 verification loop, 用 rubric、测试或 grader 检查输出, 失败就把反馈送回 agent; 第三层是 event-driven loop, 用 cron、webhook、Slack channel 这类外部事件触发 agent; 第四层是 hill-climbing loop, 从生产 trace 里分析失败模式, 反过来改 prompt、tool、grader 甚至 memory. 这个分层和上面的公式不冲突, 只是视角不同: 我的公式在拆一个 loop 需要哪些部件, LangChain 在拆这些 loop 如何一层层叠起来.

其中最值得补的一点是第四层. 很多讨论会停在“让 agent 自动做事”, 但生产系统真正有复利的是“让 agent run 的痕迹反过来改善 agent harness”. 如果 20 次 docs agent run 都在同一种链接检查上失败, 下一个动作不应该只是第 21 次重跑, 而是开一个任务去改 prompt、工具或 grader. 这就是 hill climbing: outer loop 的回箭头不只是回到任务队列, 而是伸进内层 loop, 让下一轮 agent 本身变强.

## 7) 一个 loop 到底怎么写

如果只写一个 prompt-only loop, 最小模板其实很固定:

```text
Start the "<loop name>" loop.

Goal: <最终要达成的状态>
Max iterations: <最多跑几轮>
Between iterations run: <每轮之后必须执行的检查命令>
Exit when: <可验证的停止条件>

Step 1: <第一轮具体做什么>

Self-pace this loop. After each iteration, run the check command,
read the output, and only continue if the exit condition is not met.
Stop when the exit condition passes or max iterations is reached.
Give a short status update each pass.

Guardrails:
- Do not modify the check command or exit criteria to force success.
- Do not skip, disable, or bypass checks to pass the exit condition.
- If stuck after several iterations, stop and report blockers.
```

这段模板里最重要的不是措辞, 而是字段. `Goal` 写业务结果, 不是写动作; `Between iterations run` 写机器可执行的反馈门; `Exit when` 写可验证的停止条件; `Max iterations` 是熔断器; `Step 1` 是启动动作, 防止 agent 一上来空转; `Guardrails` 是防作弊和防 overbaking.

一个好 loop 的 `Goal` 应该像“PR is open with all CI checks passing”, 而不是“把 PR 做好”. `Exit when` 应该像“all PR checks are success”, 而不是“看起来差不多了”. `Between iterations run` 应该是 `gh pr checks`、`npm test`、`npm audit --audit-level=high && npm test` 这种命令, 而不是“检查一下”.

举几个很像样的 kickoff:

```text
Start the "Ship PR Until Green" loop.
Goal: PR is open with all CI checks passing
Max iterations: 10
Between iterations run: gh pr checks
Exit when: all PR checks are success
Step 1: Implement the change, test locally, push, open PR, and fix CI until green.
Self-pace this loop. After each iteration, run the check command, read the output,
and only continue if the exit condition is not met. Stop when the exit condition
passes or max iterations is reached. Give a short status update each pass.
```

```text
Start the "npm Audit Fix Loop" loop.
Goal: no high or critical npm audit vulnerabilities
Max iterations: 10
Between iterations run: npm audit --audit-level=high && npm test
Exit when: npm audit reports no high/critical issues
Step 1: Pick one high/critical advisory, apply the safest fix, run tests, and repeat.
```

```text
Start the "Flaky Test Triage" loop.
Goal: classify failing tests as flaky vs real and fix only real regressions
Max iterations: 5
Between iterations run: npm test -- --testPathPattern=<failing-suite>
Exit when: every failure is classified and real regressions are fixed or explicitly deferred
Step 1: Run the failing suite multiple times. Classify each failure, fix real ones,
and document flaky behavior.
```

注意这些例子都有一个共同点: 每轮结束后都必须回到一个外部事实, 而不是回到模型自己的感觉. CI 状态、测试结果、audit 输出、diff、工单状态, 都比“我认为完成了”可靠.

## 8) manual loop 和 event loop 不一样

写 loop 时还要先分清它是 manual 还是 event.

Manual loop 是现在就启动, 然后一轮一轮自我推进. 例如修 CI、处理 npm audit、同步 docs、跑 a11y audit. 这种 loop 的 kickoff 一般要有 `Max iterations`, 因为它可能当场跑很多轮. 它的触发点是你粘贴 prompt 或创建 goal.

Event loop 是某个事件发生时触发. 例如 file edit 后跑 related tests, git commit 前跑 full tests, merge/rebase 后跑 smoke tests. 这种 loop 除了 kickoff prompt, 往往还需要 hook 文件或外部 watcher. kickoff 只告诉 agent 触发后做什么; hook / watcher 负责什么时候触发.

Event loop 的写法更像:

```text
Install and run the "Post-Edit Test Guard" loop.
Goal: after each batch of file edits, related tests must pass before continuing.
Between iterations run: npm test -- --findRelatedTests <edited files>
Exit when: related tests exit 0.
Step 1: After edits, run related tests. If they fail, fix before making more changes.
```

这里 `Between iterations run` 里的 `<edited files>` 不是装饰, 它要求 agent 或 hook 把事件上下文带进来. 没有这个上下文, “related tests” 就会退化成瞎猜. 所以 event loop 的关键不只是 prompt, 还包括事件 payload: 哪些文件变了、哪个 commit intent 触发了、哪个 CI run 完成了、哪条日志匹配了.

这也是为什么一个成熟 loop 不应该只有一句 `/loop 5m ...`. 它至少要说清楚: 事件长什么样, 事件 payload 放哪里, agent 第一轮读哪里, 每轮输出写哪里, 什么情况下停止或升级.

## 9) shared artifacts: loop 复利的地方

这里最有价值的部分不是“怎么让 agent 每小时跑”, 而是 shared artifact system.

假设 support、SEO、product growth、ads 多个 loop 同时跑. Support loop 发现很多用户问 export, 不只是回消息, 而是写一个结构化 signal: `export-too-hidden.md`. SEO loop 发现某个页面有流量但转化差, 写另一个 signal. Product growth loop 后面读这两个 signal, 发现 export 可能是比 analytics 单独显示更大的转化摩擦. Ads loop 发现某个 keyword 点击率好但没有 organic content, 又可以反哺 SEO loop.

这时 loop 不再是孤立 automation. 它们开始围绕一套共同的知识库工作.

`loop-engineer-template` 里这个模型更具体. README 说 loop 是被 cron、webhook、incident 或另一个 agent 唤醒, 做调查和工作, 然后把发现写进 shared file-based memory, 下一次再读这个 memory 继续. ARCHITECTURE.md 把知识库压得很克制: artifacts 按 kind 放, domain 是字段不是目录; domain folder 代表 loop, 只放 README 和 machinery, 链接 artifacts, 不吞 artifacts.

这个设计有两个关键细节. 第一, artifact 是 global 的, `signal` 就放 `signals/`, `doc` 就放 `docs/`, 不因为它来自 support loop 就塞进 `domains/support/`. 跨领域靠 frontmatter、tags、links. 第二, 每个 artifact 有正文和 append-only `## Timeline`; 正文表示“现在相信什么”, timeline 记录“发生过什么”. 这样 agent 可以更新当前判断, 也保留证据轨迹.

换句话说, loop engineering 的成熟形态不是“很多 agent 在跑”, 而是:

```text
many loops, one shared brain
```

这个 shared brain 可以很土, 就是 markdown + frontmatter + git. 但它必须可 diff、可 review、agent 可写、人也能看.

## 10) loop contract: 每个 loop 都要有契约

如果 shared artifacts 是系统记忆, 那每个 loop 的 README 就是它的契约.

`loop-engineer-template` 的 `new-loop` skill 会为一个新 loop scaffold `domains/<loop>/README.md`, 里面至少有 goal、cadence、current focus、backlog、timeline. 更重要的是, 它要求新 loop 不是只建文件夹, 而是必须做一次真实 test run, 然后把结果写进该 loop 的 timeline 和全局 `LOG.md`.

这个要求很关键. 很多“自动化系统”死在第一天: spec 写得很漂亮, 但从来没跑过真实输入. `new-loop` 反过来要求先小规模跑一次, 看看工具、数据、权限、输出格式是不是真的通.

一个 loop contract 至少应该说明: 它负责什么、不负责什么, 何时触发, 每轮读什么, 产出什么 artifact, 怎么去重, 怎么升级给人, timeline 写在哪里. 如果这些都没有, 你只有一个 prompt, 还没有一个 loop.

## 11) Loop market: 样例比定义更有用

[loops!](https://loops.elorm.xyz/) 可以理解成一个 loop market: 它收集的不是“提示词灵感”, 而是一组可以复制的 closed-loop workflow. 它首页那句定位很准确: 每个 loop 都应该包含 trigger、feedback gate 和 exit condition, 让 agent 能 self-pace 到工作完成. 这比抽象定义更容易看出 loop 该怎么写.

`Pre-Commit Guard` 是其中一个小而完整的例子. 它的目标是: commit 前测试必须是绿的. 触发点是 git commit intent, 检查命令是 `npm test`, 退出条件是 tests exit 0 before each commit.

它的 loop 大概是:

```text
detect commit intent
run npm test
if red, fix failures and rerun
if green, allow commit
```

这里有两点值得学. 第一, 它是 event-driven, 不是 schedule-driven. 不是每 5 分钟跑一次测试, 而是在危险动作 commit 之前触发. 第二, 它的 guardrails 明确禁止 agent 为了过关而篡改规则: 不能改 check command, 不能 skip/disable tests, 不能删断言或改成 always-pass, 优先修 production code, 多轮失败后要报告 blocker.

这就是 feedback gate 的最小形态: 不只是“检查 npm test”, 还规定了检查失败后允许怎么做、不允许怎么做. 没有后半部分, agent 很容易 Goodhart: 你量什么, 它就优化什么, 哪怕优化方式不是你想要的.

这个 market 的价值不在于每个 loop 都能原封不动拿来用, 而在于它把 loop 的结构暴露得很直白: manual、event、interval 是不同触发类型; `Between iterations run` 是反馈门; `Exit when` 是停止条件; hardened loop 会额外写 anti-gaming guardrails. 如果你不知道自己的 loop 怎么写, 可以先从这些样例反推: 我的触发点是什么, 每轮必须读哪个外部事实, 哪个条件算真的完成, agent 为了过关时绝对不能改什么.

## 12) maker/checker 分离, 但别迷信

很多 loop 设计都会引入 sub-agent 或独立 verifier. 这个方向是对的: 写代码的 agent 很容易给自己的作业放水. Claude `/goal` 用小模型判断 done, Codex goal 要求 `update_goal complete` 只能在目标真正达成时调用, template 里的 `/pr` skill 也要求 fresh verifier sub-agent 驱动真实 app 验证功能, 然后主 agent 再跑 type-check、lint、unit、e2e.

但这里不能迷信: 两个 LLM 不是两个真正独立的审计员. 它们可能有相同盲区、相同过度自信、相同训练偏差. Verifier 能抓到很多低级错, 但不能替代工程判断. 尤其是架构方向、权限边界、支付鉴权、数据一致性这类问题, 不能因为“另一个 agent 也说可以”就放心合并.

所以我会把 verifier 看成 back-pressure, 不是 proof. 它提高“done claim”的质量, 但最终你仍然要决定哪些代码能进主线.

## 13) 最容易踩的坑

Loop 最大的坑不是它跑不起来, 而是它跑得太顺.

第一是 token 和时间成本. 每一轮都是一次完整 agent run, 还可能读上下文、跑工具、spawn verifier. 对模型公司内部人员来说, token 便宜; 对普通团队来说, 高频 loop 很容易变成自动烧钱机. 一个 loop 要值得跑, 通常要满足几个条件: 任务重复、验证能自动化、工具权限齐、失败有清晰升级路径.

第二是调试成本. 一个 prompt 跑偏, 你看一轮就知道. 一个 loop 跑了 47 轮才坏, 你要翻状态、日志、artifact timeline、PR diff、工具输出, 才能知道第几轮开始偏. 所以一开始要小: 小目标、短 cadence、硬停止条件、每轮写短日志.

第三是 overbaking. 约束太松、跑太久, agent 会开始加戏: 重构不该重构的模块、添加没人要的功能、把测试改松、把错误吞掉. Ralph Wiggum loop 那类实践已经反复暴露这个问题. 解决办法不是“相信更强模型”, 而是写清楚 non-goals、max iterations、anti-gaming rules, 并让人 review.

第四是理解债. Loop 发 PR 的速度可能超过你读 PR 的速度. 这时瓶颈不是写代码, 而是 review 和理解. 如果你用 loop 逃避理解, 它会把你带进一堆你不懂但已经合并的代码里.

## 14) 我会怎么设计第一个 loop

如果是给一个普通工程团队落地, 我不会从“多 agent 公司操作系统”开始. 我会选一个重复、低风险、可验证、能省人工盯梢的点, 比如 CI failure triage 或 post-edit related tests.

第一版只需要一个 domain README、一个状态文件、一个检查命令和一个升级规则. 例如 CI triage loop 的 contract 可以写成: 每天早上读昨晚失败的 CI 和最近 commits, 把失败分成 env、flake、bug、dependency、infra; flake 重试一次, env/infra 升级给人, bug/dependency 才起草修复; 每次运行更新 `domains/ci-triage/README.md` timeline, 真实 bug 写成 `signals/` 或 backlog line.

在把它设成真正的循环之前, 我会先手动跑一次 test run. 这一步不是仪式, 而是在检查代码库是否 loop-ready: agent 能不能快速读懂入口和边界, 能不能一条命令启动本地环境, 多个 worktree 并行时会不会抢端口或共享状态, 失败后有没有测试、lint、Playwright、日志或只读 verifier 之类的外部证据. 如果这些条件不满足, 先补 harness, 不要急着加调度.

等这个 loop 跑稳, 再加 worktree、PR workflow、verifier sub-agent、Slack/GitHub connector. 不要一上来搭 8 个 artifact kind、5 个 domain、3 个 sub-agent. `loop-engineer-template` 的 ARCHITECTURE.md 也强调: 先从 `signal` 和 `doc` 开始, 新 kind 要“挣出来”, 不要预建.

这点很像好的代码架构: loop 也要从真实压力里长出来, 不是从 PPT 分类法里长出来.

## 15) 一句话总结

如果只保留一句中文解释, 我会写成:

> Loop engineering 不是让 agent 无限跑, 而是设计一个 outer loop: 它知道何时唤醒 agent、交给它什么任务、用什么 harness 执行、怎样验证结果、把状态写到哪里、失败时如何升级, 并让这些记录变成下一轮和其他 loop 的输入.

所以它确实是继 harness engineering 之后的一个新热词, 但不是替代 harness. Harness 让单个 agent 能可靠执行; loop engineering 让一组 agent run 能持续发现工作、完成工作、记录学习, 最后形成复利.

真正的难点也在这里: 写 prompt 是一句话的事, 设计 loop 是在设计一个小型操作系统. 它奖励已经想清楚的人, 也会放大没想清楚的混乱.
