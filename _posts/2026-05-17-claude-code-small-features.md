---
title: "读 Claude Code 源码 - 若干小功能 (recap, suggestion, insights)"
categories: 
- LLM
tags: Agent
updated: 
comments: true
mathjax: false
---

小功能 `away recap`, `prompt suggestion`, `insights`.

<!-- more -->

## Away recap

终端失焦 5 分钟后触发的简短总结, 只用于展示给用户, 提醒用户之前在干什么, 下一步是什么. 默认用 Haiku.

### 触发

```ts
const BLUR_DELAY_MS = 5 * 60_000

/**
 * Appends a "while you were away" summary message after the terminal has been
 * blurred for 5 minutes. Fires only when (a) 5min since blur, (b) no turn in
 * progress, and (c) no existing away_summary since the last user message.
 */
```

```ts
function hasSummarySinceLastUserTurn(messages: readonly Message[]): boolean {
  for (let i = messages.length - 1; i >= 0; i--) {
    const m = messages[i]!
    if (m.type === 'user' && !m.isMeta && !m.isCompactSummary) return false
    if (m.type === 'system' && m.subtype === 'away_summary') return true
  }
  return false
}
```

### Prompt

只说两件事: 你在干什么, 下一步是什么.

```ts
// Recap only needs recent context — truncate to avoid "prompt too long" on
// large sessions. 30 messages ≈ ~15 exchanges, plenty for "where we left off."
const RECENT_MESSAGE_WINDOW = 30
```

```ts
function buildAwaySummaryPrompt(memory: string | null): string {
  const memoryBlock = memory
    ? `Session memory (broader context):\n${memory}\n\n`
    : ''
  return `${memoryBlock}The user stepped away and is coming back. Write exactly 1-3 short sentences. Start by stating the high-level task — what they are building or debugging, not implementation details. Next: the concrete next step. Skip status reports and commit recaps.`
}
```

## Prompt suggestion

输入框预测下一条 prompt 底纹词

### 触发

- 会话太早不给
- 上一轮报错不给
- 正在等 permission / elicitation 不给
- `plan mode` 不给
- non-interactive / teammate 也会禁用

```ts
const assistantTurnCount = count(messages, m => m.type === 'assistant')
if (assistantTurnCount < 2) {
  ...
  return null
}
```

```ts
export function getSuggestionSuppressReason(appState: AppState): string | null {
  if (!appState.promptSuggestionEnabled) return 'disabled'
  if (appState.pendingWorkerRequest || appState.pendingSandboxRequest)
    return 'pending_permission'
  if (appState.elicitation.queue.length > 0) return 'elicitation_active'
  if (appState.toolPermissionContext.mode === 'plan') return 'plan_mode'
  ...
}
```

### Prompt

```ts
const SUGGESTION_PROMPT = `[SUGGESTION MODE: Suggest what the user might naturally type next into Claude Code.]

FIRST: Look at the user's recent messages and original request.

Your job is to predict what THEY would type - not what you think they should do.

THE TEST: Would they think "I was just about to type that"?
...
Stay silent if the next step isn't obvious from what the user said.

Format: 2-12 words, match the user's style. Or nothing.

Reply with ONLY the suggestion, no quotes or explanation.`
```

### 接受以后不只是填字

Suggestion 生成完以后, 如果开着 `speculation`, Claude Code 会提前沿着这条 suggestion 跑一个 forked agent:

```ts
if (isSpeculationEnabled() && result.suggestion) {
  void startSpeculation(
    result.suggestion,
    context,
    context.toolUseContext.setAppState,
    false,
    cacheSafeParams,
  )
}
```

等用户真的接受 suggestion 时, 如果 speculative path 已经跑出一部分结果, 就直接注入:

```ts
if (speculation.status === 'active') {
  markAccepted()
  logOutcomeAtSubmission(suggestionText, { skipReset: true })
  void onSubmitProp(suggestionText, ..., {
    state: speculation,
    speculationSessionTimeSavedMs,
    setAppState
  })
  return
}
```

## Insights

`/insights` 不是把全部 transcript 一把喂给模型写总结.

更接近两条支线最后汇合:

1. 先扫全部 session, 生成或读取一层本地统计摘要
2. 从里面筛出“值得分析的 session”
3. 只对“还没有结构化分析缓存”的这部分 session 做单 session LLM 分析
4. 把这些结构化分析结果缓存下来
5. 再把聚合统计 + 结构化分析缓存拼成全局上下文, 并行跑各个 section
6. 最后单独写一个 `At a Glance`, 拼成 HTML report

### 先把 session 变成结构化数据

扫描所有 session.

第一步只是扫文件系统元数据:

```ts
/**
 * Scans all project directories using filesystem metadata only (no JSONL parsing).
 * Returns a list of session file info sorted by mtime descending.
 */
async function scanAllSessions(): Promise<LiteSessionInfo[]> {
  ...
}
```

接着才读一层本地缓存的 session 摘要. 对还没有这层摘要的 session, 最多补载一批:

```ts
const META_BATCH_SIZE = 50
const MAX_SESSIONS_TO_LOAD = 200
```

这里这层摘要对应源码里的 `SessionMeta`, 可以理解成“从原始 session 日志里直接统计出来的一页概要”, 不是 LLM 产物, 会缓存在 `usage-data/session-meta/<sessionId>.json`.

也就是:

- 扫描范围是全部 session 文件
- 但真正新解析 JSONL、重算这份本地统计摘要的 session, 默认最多 `200` 个
- 而且后面做 LLM 结构化分析的范围还会再缩一次

先从原始 log 里抽一些硬统计:

```ts
type SessionMeta = {
  session_id: string
  duration_minutes: number
  user_message_count: number
  assistant_message_count: number
  tool_counts: Record<string, number>
  languages: Record<string, number>
  git_commits: number
  git_pushes: number
  input_tokens: number
  output_tokens: number
  user_interruptions: number
  tool_errors: number
  uses_task_agent: boolean
  uses_mcp: boolean
  uses_web_search: boolean
  uses_web_fetch: boolean
}
```

统计口径还会扫 `tool_use` 和 `tool_result`:

```ts
if (toolName === AGENT_TOOL_NAME || toolName === LEGACY_AGENT_TOOL_NAME)
  usesTaskAgent = true
if (toolName.startsWith('mcp__')) usesMcp = true
if (toolName === 'WebSearch') usesWebSearch = true
if (toolName === 'WebFetch') usesWebFetch = true
```

以及各种 user-side / tool-side 摩擦:

```ts
if (isError) {
  toolErrors++
  ...
  if (lowerContent.includes('exit code')) {
    category = 'Command Failed'
  } else if (lowerContent.includes('string to replace not found')) {
    category = 'Edit Failed'
  } else if (lowerContent.includes('modified since read')) {
    category = 'File Changed'
  }
}
```

接着才进入单 session LLM 分析这条支线: 把 transcript 变成“结构化会话分析结果”. 这层结果会缓存到 `usage-data/facets/<sessionId>.json`, 后面各个 section 直接复用.

这一步的 prompt 把口径卡得很死:

```ts
const FACET_EXTRACTION_PROMPT = `Analyze this Claude Code session and extract structured facets.

CRITICAL GUIDELINES:

1. **goal_categories**: Count ONLY what the USER explicitly asked for.
   - DO NOT count Claude's autonomous codebase exploration
   - DO NOT count work Claude decided to do on its own

2. **user_satisfaction_counts**: Base ONLY on explicit user signals.

3. **friction_counts**: Be specific about what went wrong.
...
SESSION:
`
```

### 真正发给 LLM 的 session 数量

先会过滤掉明显太小的 session:

```ts
const isSubstantiveSession = (meta: SessionMeta): boolean => {
  if (meta.user_message_count < 2) return false
  if (meta.duration_minutes < 1) return false
  return true
}
```

这里源码里的 `substantive session`, 可以直接理解成“值得分析的 session”.

然后只对“还没有结构化分析缓存的、值得分析的 session”补抽, 并且有硬上限:

```ts
const MAX_FACET_EXTRACTIONS = 50
```

所以更准确地说:

- `/insights` 会扫全部 session
- 会尽量复用已有的本地统计摘要和结构化分析缓存
- 单 session 分析就发生在这里
- 一次最多只会对 `50` 个“还没做过结构化分析、而且值得分析”的 session 发 LLM

长 session 还会先切块总结, 再做这层结构化分析:

```ts
// If under 30k chars, use as-is
if (fullTranscript.length <= 30000) {
  return fullTranscript
}

const CHUNK_SIZE = 25000
const summaries = await Promise.all(chunks.map(summarizeTranscriptChunk))
```

### 再并行生成几个 section

拆 section 并行跑.

```ts
// ============================================================================
// Parallel Insights Generation (6 sections)
// ============================================================================
```

第一批 section 大概这些:

- `project_areas`
- `interaction_style`
- `what_works`
- `friction_analysis`
- `suggestions`
- `on_the_horizon`
- `fun_ending`

定义也很直白:

```ts
const INSIGHT_SECTIONS: InsightSection[] = [
  {
    name: 'interaction_style',
    prompt: `Analyze this Claude Code usage data and describe the user's interaction style.

RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "narrative": "2-3 paragraphs ... Use second person 'you'.",
  "key_pattern": "One sentence summary ..."
}`,
  },
  ...
]
```

### 最后再写一个总览

等各 section 都有了, 再写 `At a Glance`.

```ts
const atAGlancePrompt = `You're writing an "At a Glance" summary for a Claude Code usage insights report for Claude Code users.

Use this 4-part structure:

1. **What's working**
2. **What's hindering you**
3. **Quick wins to try**
4. **Ambitious workflows for better models**
...
RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "whats_working": "...",
  "whats_hindering": "...",
  "quick_wins": "...",
  "ambitious_workflows": "..."
}`
```

### 它甚至在统计你怎么用 Claude

还有几个很“使用分析”而不是“代码分析”的指标.

比如 multi-clauding:

```ts
/**
 * Detects multi-clauding (using multiple Claude sessions concurrently).
 * Uses a sliding window to find the pattern: session1 -> session2 -> session1
 * within a 30-minute window.
 */
const OVERLAP_WINDOW_MS = 30 * 60000
```

实现就是找 `s1 -> s2 -> s1` 这种交替模式, 看你是不是在并行开多个 Claude session 来回切.

### 最后落成 shareable report

生成 HTML:

```ts
const htmlReport = generateHtmlReport(aggregated, insights)
const htmlPath = join(getDataDir(), 'report.html')
await writeFile(htmlPath, htmlReport, {
  encoding: 'utf-8',
  mode: 0o600,
})
```

### 用哪个模型

`/insights` 和前两个不一样, 它明确指定了 Opus.

代码里直接分了两个 getter:

```ts
// Model for facet extraction and summarization (Opus - best quality)
function getAnalysisModel(): string {
  return getDefaultOpusModel()
}

// Model for narrative insights (Opus - best quality)
function getInsightsModel(): string {
  return getDefaultOpusModel()
}
```

## 附: `/insights` 用到的 prompts

### 1. 单 session 的结构化分析 prompt

先对单个 session 抽一层结构化分析:

```ts
const FACET_EXTRACTION_PROMPT = `Analyze this Claude Code session and extract structured facets.

CRITICAL GUIDELINES:

1. **goal_categories**: Count ONLY what the USER explicitly asked for.
   - DO NOT count Claude's autonomous codebase exploration
   - DO NOT count work Claude decided to do on its own
   - ONLY count when user says "can you...", "please...", "I need...", "let's..."

2. **user_satisfaction_counts**: Base ONLY on explicit user signals.
   - "Yay!", "great!", "perfect!" → happy
   - "thanks", "looks good", "that works" → satisfied
   - "ok, now let's..." → likely_satisfied
   - "that's not right", "try again" → dissatisfied
   - "this is broken", "I give up" → frustrated

3. **friction_counts**: Be specific about what went wrong.
...
SESSION:
`
```

这个 prompt 后面还会再拼上 schema, 要求模型只回 JSON:

```ts
{
  "underlying_goal": "...",
  "goal_categories": {"category_name": count, ...},
  "outcome": "fully_achieved|mostly_achieved|...",
  "user_satisfaction_counts": {"level": count, ...},
  "claude_helpfulness": "...",
  "session_type": "...",
  "friction_counts": {"friction_type": count, ...},
  "friction_detail": "...",
  "primary_success": "...",
  "brief_summary": "..."
}
```

### 2. `project_areas`

```ts
Analyze this Claude Code usage data and identify project areas.

RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "areas": [
    {"name": "Area name", "session_count": N, "description": "2-3 sentences ..."}
  ]
}

Include 4-5 areas. Skip internal CC operations.
```

### 3. `interaction_style`

```ts
Analyze this Claude Code usage data and describe the user's interaction style.

RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "narrative": "2-3 paragraphs ... Use second person 'you'.",
  "key_pattern": "One sentence summary ..."
}
```

### 4. `what_works`

```ts
Analyze this Claude Code usage data and identify what's working well for this user. Use second person ("you").

RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "intro": "1 sentence of context",
  "impressive_workflows": [
    {"title": "Short title", "description": "2-3 sentences ..."}
  ]
}

Include 3 impressive workflows.
```

### 5. `friction_analysis`

```ts
Analyze this Claude Code usage data and identify friction points for this user. Use second person ("you").

RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "intro": "1 sentence summarizing friction patterns",
  "categories": [
    {"category": "Concrete category name", "description": "1-2 sentences ...", "examples": ["...", "..."]}
  ]
}

Include 3 friction categories with 2 examples each.
```

### 6. `suggestions`

这个 prompt 最长, 因为前面先塞了一段 CC features reference, 明确允许它从这些功能里挑:

- `MCP Servers`
- `Custom Skills`
- `Hooks`
- `Headless Mode`
- `Task Agents`

然后再要求输出三类建议:

```ts
{
  "claude_md_additions": [
    {"addition": "...", "why": "...", "prompt_scaffold": "..."}
  ],
  "features_to_try": [
    {"feature": "...", "one_liner": "...", "why_for_you": "...", "example_code": "..."}
  ],
  "usage_patterns": [
    {"title": "...", "suggestion": "...", "detail": "...", "copyable_prompt": "..."}
  ]
}
```

里面还有一条很重要的约束:

```ts
IMPORTANT for claude_md_additions: PRIORITIZE instructions that appear MULTIPLE TIMES in the user data.
```

也就是优先找“用户重复说过的协作习惯”.

### 7. `on_the_horizon`

```ts
Analyze this Claude Code usage data and identify future opportunities.

RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "intro": "1 sentence about evolving AI-assisted development",
  "opportunities": [
    {"title": "Short title", "whats_possible": "2-3 ambitious sentences ...", "how_to_try": "...", "copyable_prompt": "..."}
  ]
}

Include 3 opportunities. Think BIG - autonomous workflows, parallel agents, iterating against tests.
```

### 8. `fun_ending`

```ts
Analyze this Claude Code usage data and find a memorable moment.

RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "headline": "A memorable QUALITATIVE moment from the transcripts - not a statistic.",
  "detail": "Brief context about when/where this happened"
}
```

### 9. `At a Glance`

等前面的 section 都跑完了, 再写一个总览:

```ts
You're writing an "At a Glance" summary for a Claude Code usage insights report for Claude Code users.

Use this 4-part structure:

1. **What's working**
2. **What's hindering you**
3. **Quick wins to try**
4. **Ambitious workflows for better models**
```

它不是直接看原始 transcript, 而是再消费前面各个 section 的输出:

```ts
## Project Areas
## Big Wins
## Friction Categories
## Features to Try
## Usage Patterns to Adopt
## On the Horizon
```

所以 `/insights` 的 prompt 链路其实挺清楚:

- 先扫全部 session, 生成或读取本地统计摘要
- 再筛出值得分析的 session, 只补跑缺失的结构化分析缓存
- 再把全局聚合数据切成几个 narrative section
- 最后再把这些 section 回收成一页总览

## 附: `/insights` 里的 data / session 是怎么拼进 prompt 的

这里其实是两条支线:

- 单 session 分析支线: 原始 log -> transcript 风格文本 -> 结构化会话分析结果
- 全局报告支线: 聚合统计 + 结构化分析结果 -> section prompts -> `At a Glance`

### 1. 单个 session: 转成 transcript 风格纯文本

做单 session 结构化分析时, 先把 log 转成这种文本:

```text
Session: abcd1234
Date: 2026-...
Project: /path/to/project
Duration: 18 min

[User]: ...
[Assistant]: ...
[Tool: Edit]
[Assistant]: ...
```

对应代码:

```ts
lines.push(`Session: ${meta.session_id.slice(0, 8)}`)
lines.push(`Date: ${meta.start_time}`)
lines.push(`Project: ${meta.project_path}`)
lines.push(`Duration: ${meta.duration_minutes} min`)

...
lines.push(`[User]: ${content.slice(0, 500)}`)
...
lines.push(`[Assistant]: ${(block.text as string).slice(0, 300)}`)
...
lines.push(`[Tool: ${block.name}]`)
```

也就是:

- 用户文本截到 `500` 字符
- assistant 文本截到 `300` 字符
- tool 只保留工具名, 不把整段 input/output 全塞进去

如果 transcript 太长, 不直接全塞. 会先切块总结:

```ts
// If under 30k chars, use as-is
if (fullTranscript.length <= 30000) {
  return fullTranscript
}

const CHUNK_SIZE = 25000
const summaries = await Promise.all(chunks.map(summarizeTranscriptChunk))
```

然后再拼成:

```text
Session: ...
Date: ...
Project: ...
Duration: ...
[Long session - N parts summarized]

<summary 1>

---

<summary 2>
```

最后才把它接到单 session 分析 prompt 后面.

### 2. 全局 usage data: 聚合统计 + 结构化分析缓存

到了并行生成 section 的阶段, 走的是另一条“全局报告”支线. 这时喂给模型的已经不是单条 session transcript, 而是一份由聚合统计和结构化分析缓存拼出来的全局上下文字符串.

先有一段聚合 JSON:

```ts
const dataContext = jsonStringify(
  {
    sessions: data.total_sessions,
    analyzed: data.sessions_with_facets,
    date_range: data.date_range,
    messages: data.total_messages,
    hours: Math.round(data.total_duration_hours),
    commits: data.git_commits,
    top_tools: ...,
    top_goals: ...,
    outcomes: data.outcomes,
    satisfaction: data.satisfaction,
    friction: data.friction,
    success: data.success,
    languages: data.languages,
  },
  null,
  2,
)
```

再补三段“更像自然语言”的摘要:

```ts
const facetSummaries = Array.from(facets.values())
  .slice(0, 50)
  .map(f => `- ${f.brief_summary} (${f.outcome}, ${f.claude_helpfulness})`)
  .join('\n')

const frictionDetails = Array.from(facets.values())
  .filter(f => f.friction_detail)
  .slice(0, 20)
  .map(f => `- ${f.friction_detail}`)
  .join('\n')

const userInstructions = Array.from(facets.values())
  .flatMap(f => f.user_instructions_to_claude || [])
  .slice(0, 15)
  .map(i => `- ${i}`)
  .join('\n')
```

最后拼成一个 `fullContext`:

```ts
const fullContext =
  dataContext +
  '\n\nSESSION SUMMARIES:\n' +
  facetSummaries +
  '\n\nFRICTION DETAILS:\n' +
  frictionDetails +
  '\n\nUSER INSTRUCTIONS TO CLAUDE:\n' +
  (userInstructions || 'None captured')
```

所以这里的 `Claude Code usage data` 实际是:

- 一段聚合后的 JSON
- 最多 `50` 条 session one-line summaries
- 最多 `20` 条 friction details
- 最多 `15` 条 user instructions

不是把所有 session 原样塞进去.

### 3. 每个 section 真正收到的 prompt 形式

section 调用时很简单:

```ts
userPrompt: section.prompt + '\n\nDATA:\n' + dataContext
```

但这里传进去的 `dataContext` 实际就是上面那个 `fullContext`, 因为外层调用是:

```ts
generateSectionInsight(section, fullContext)
```

也就是每个 section 看到的形式大概是:

```text
<section prompt>

DATA:
{
  "sessions": ...,
  "analyzed": ...,
  ...
}

SESSION SUMMARIES:
- ...
- ...

FRICTION DETAILS:
- ...

USER INSTRUCTIONS TO CLAUDE:
- ...
```

### 4. `At a Glance` 再做一次二次拼装

`At a Glance` 不只看 `fullContext`, 还把前面已经生成好的 section 结果再格式化一遍塞进去:

```ts
## Project Areas
## Big Wins
## Friction Categories
## Features to Try
## Usage Patterns to Adopt
## On the Horizon
```

每段本质上又是一些 `- title: description` 这样的 bullets.
