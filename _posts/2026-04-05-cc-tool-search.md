---
title: "读 Claude Code 源码 - ToolSearch 与 Skill Discovery"
categories: 
- LLM
tags: Agent
updated:
comments: true
mathjax: false
---

延迟 tool 加载

<!-- more -->

## deferred tool 

对内置 tools 以及 MCP tools 都可以延迟加载. MCP 默认延迟加载. 延迟加载内置工具 `WebSearch`, `WebFetch`, `NotebookEdit`, `TodoWrite`, `Task*`, `Team*`, `LSPTool` 等.

```ts
/**
 * When true, this tool is deferred (sent with defer_loading: true) and requires
 * ToolSearch to be used before it can be called.
 */
readonly shouldDefer?: boolean
/**
 * When true, this tool is never deferred — its full schema appears in the
 * initial prompt even when ToolSearch is enabled. For MCP tools, set via
 * `_meta['anthropic/alwaysLoad']`. Use for tools the model must see on
 * turn 1 without a ToolSearch round-trip.
 */
readonly alwaysLoad?: boolean
```

```ts
/**
 * Check if a tool should be deferred (requires ToolSearch to load).
 * A tool is deferred if:
 * - It's an MCP tool (always deferred - workflow-specific)
 * - It has shouldDefer: true
 *
 * A tool is NEVER deferred if it has alwaysLoad: true (MCP tools set this via
 * _meta['anthropic/alwaysLoad']). This check runs first, before any other rule.
 */
```

## 什么时候开启 ToolSearch

分了三种模式

```ts
/**
 * Tool search mode. Determines how deferrable tools (MCP + shouldDefer) are
 * surfaced:
 *   - 'tst': Tool Search Tool — deferred tools discovered via ToolSearchTool (always enabled)
 *   - 'tst-auto': auto — tools deferred only when they exceed threshold
 *   - 'standard': tool search disabled — all tools exposed inline
 */
```

环境变量 `ENABLE_TOOL_SEARCH` 决定具体模式

```ts
/**
 * Determines the tool search mode from ENABLE_TOOL_SEARCH.
 *
 *   ENABLE_TOOL_SEARCH    Mode
 *   auto / auto:1-99      tst-auto
 *   true / auto:0         tst
 *   false / auto:100      standard
 *   (unset)               tst (default: always defer MCP and shouldDefer tools)
 */
```

`auto` 模式会看 deferred tools 的总大小是不是超过上下文窗口的一定比例. 默认是 10%.

不是所有模型都支持 `tool_reference`.

```ts
/**
 * Check if a model supports tool_reference blocks (required for tool search).
 *
 * This uses a negative test: models are assumed to support tool_reference
 * UNLESS they match a pattern in the unsupported list.
 *
 * Currently, Haiku models do NOT support tool_reference.
 */
```

## ToolSearchTool 本身做了什么

未加载的 deferred tool, 模型先只知道名字

```ts
const PROMPT_HEAD = `Fetches full schema definitions for deferred tools so they can be called.
`
```

```ts
Until fetched, only the name is known — there is no parameter schema, so the tool cannot be invoked. This tool takes a query, matches it against the deferred tool list, and returns the matched tools' complete JSONSchema definitions inside a <functions> block. Once a tool's schema appears in that result, it is callable exactly like any tool defined at the top of this prompt.
```

支持三种 query 形式:

```ts
Query forms:
- "select:Read,Edit,Grep" — fetch these exact tools by name
- "notebook jupyter" — keyword search, up to max_results best matches
- "+slack send" — require "slack" in the name, rank by remaining terms
```

## 模型怎么知道有哪些 deferred tools 可以搜

```ts
function getToolLocationHint(): string {
  ...
  return deltaEnabled
    ? 'Deferred tools appear by name in <system-reminder> messages.'
    : 'Deferred tools appear by name in <available-deferred-tools> messages.'
}
```

```ts
// When the delta attachment is enabled, deferred tools are announced
// via persisted deferred_tools_delta attachments instead of this
// ephemeral prepend (which busts cache whenever the pool changes).
```

这句话其实已经把设计动机说出来了:  
**工具名变化是常态, 不该让它频繁破坏 prompt cache.**

## defer 之后, tool schema 到底怎么进 prompt

这个问题我一开始也容易想成“是不是 tool schema 完全不发给 API 了”.  

更准确一点说:

- **未 discover 的 deferred tool**, 不会像普通工具那样直接进入模型首轮可见的那部分工具上下文
- 但一旦它被 discover, 后续请求里它还是会作为 `defer_loading: true` 的工具 schema 发给 API

对应代码:

```ts
const toolSchemas = await Promise.all(
  filteredTools.map(tool =>
    toolToAPISchema(tool, {
      ...
      deferLoading: willDefer(tool),
    }),
  ),
)
```

底层就是给 tool schema 加一个字段:

```ts
// Per-request overlay: defer_loading and cache_control vary by call
if (options.deferLoading) {
  schema.defer_loading = true
}
```

所以不是“schema 完全没了”, 而是:

- 工具 schema 仍然在 API 的 `tools` 参数里
- 但被标成了 `defer_loading`
- 服务端不会把它当成普通 top-level tool schema 直接展开进 prompt 前缀

源码里还有一句更直白的注释:

```ts
// They get defer_loading: true and don't count against context - the API filters them out
// of system_prompt_tools before token counting
```

也就是说, deferred tools 就算跟着请求一起发上去, 也不是按普通工具那样占用 prompt context.

## ToolSearch 返回的不是普通文本, 而是 tool_reference

这一步特别关键.

`ToolSearchTool` 命中结果之后, 不是返回一段“我找到了这些工具”的说明文字, 而是返回结构化的 `tool_reference`:

```ts
/**
 * Returns a tool_result with tool_reference blocks.
 */
...
content: content.matches.map(name => ({
  type: 'tool_reference' as const,
  tool_name: name,
}))
```

后面消息规范化里还有一句很关键的注释:

```ts
// Server renders tool_reference expansion as <functions>...</functions>
```

也就是:

- 模型先调 `ToolSearch`
- `ToolSearch` 返回 `tool_reference`
- 服务端在后续处理中把它展开成对应工具定义

所以它并不是靠模型自己读文字、脑补 schema, 而是靠专门的结构化 block 把“这个工具已被发现”这件事传下去.

## 后续怎么记住“已经 discover 过哪些工具”

Claude Code 会从历史消息里扫描 `tool_reference`, 把已经 discover 过的工具名提取出来:

```ts
/**
 * Extract tool names from tool_reference blocks in message history.
 *
 * This approach:
 * - Eliminates the need to predeclare all MCP tools upfront
 * - Removes limits on total quantity of MCP tools
 */
export function extractDiscoveredToolNames(messages: Message[]): Set<string>
```

这就形成了一个闭环:

1. 模型先看到 deferred tools 的名字
2. 用 `ToolSearch` 搜索
3. `ToolSearch` 返回 `tool_reference`
4. 后续请求从历史里提取 discovered tool names
5. 这些已 discover 的工具继续保留在后续请求中

## Prompt Cache 怎么保持

这其实是整套机制最值钱的地方.

源码里有一句几乎把答案说完了:

```ts
// Exclude defer_loading tools from the hash -- the API strips them from the
// prompt, so they never affect the actual cache key. Including them creates
// false-positive "tool schemas changed" breaks when tools are discovered or
// MCP servers reconnect.
```

也就是说:

- `defer_loading` tools 不会进入实际 prompt 前缀
- 所以它们本来就不该参与 prompt cache key
- 如果把它们算进 hash, 那么每次 discover 新工具、MCP reconnect、工具池变化, 都会制造假的 cache miss

Claude Code 自己在 prompt cache break detection 里, 也特地把这些 defer_loading tools 排除了.

另外它还做了两层稳 cache 的处理:

第一层, deferred tool 名单尽量走 attachment / delta, 而不是直接改 prompt 文本:

```ts
// deferred tools are announced
// via persisted deferred_tools_delta attachments instead of this
// ephemeral prepend (which busts cache whenever the pool changes).
```

第二层, 有些 beta header 会做 sticky latch, 避免中途开关功能导致 cache key 变化. 这虽然不只是 ToolSearch 独有, 但思路一致:  
**能稳定的前缀尽量稳定, 动态部分尽量后移或旁路化.**

## 搜索怎么匹配

`ToolSearch` 的搜索逻辑不复杂, 但做得挺实用.

先把工具名拆成可搜索片段:

```ts
/**
 * Parse tool name into searchable parts.
 * Handles both MCP tools (mcp__server__action) and regular tools (CamelCase).
 */
```

然后支持:

- 精确名匹配
- MCP 前缀匹配
- 普通关键词搜索
- `+term` 强制命中

源码里对模型常见查询方式的总结:

```ts
/**
 * The model typically queries with:
 * - Server names when it knows the integration (e.g., "slack", "github")
 * - Action words when looking for functionality (e.g., "read", "list", "create")
 * - Tool-specific terms (e.g., "notebook", "shell", "kill")
 */
```

打分大概就是:

- 名字精确片段命中权重最高
- `searchHint` 次之
- 描述文本命中再次之

```ts
if (parsed.parts.includes(term)) {
  score += parsed.isMcp ? 12 : 10
} else if (parsed.parts.some(part => part.includes(term))) {
  score += parsed.isMcp ? 6 : 5
}

if (hintNormalized && pattern.test(hintNormalized)) {
  score += 4
}

if (pattern.test(descNormalized)) {
  score += 2
}
```

## 没 discover 就直接调用会怎样

Claude Code 这里还专门做了一个防呆.

如果模型直接调用一个尚未 discover 的 deferred tool, 它不会“试试看”, 而是直接提示先去调 `ToolSearch`:

```ts
This tool's schema was not sent to the API — it was not in the discovered-tool set derived from message history.
Without the schema in your prompt, typed parameters (arrays, numbers, booleans) get emitted as strings and the client-side parser rejects them.
Load the tool first: call ToolSearch with query "select:${tool.name}", then retry this call.
```

这段解释也挺到位:  
没有 schema 时, 模型很容易把数组、数字、布尔值都生成成字符串, 参数校验就会炸.

## compact 之后, discovered set 怎么不丢

如果 discovered tool names 只靠消息历史扫描, compact 之后就可能丢状态.

Claude Code 专门把它快照到 compact boundary 上:

```ts
// Carry loaded-tool state — the summary doesn't preserve tool_reference
// blocks, so the post-compact schema filter needs this to keep sending
// already-loaded deferred tool schemas to the API.
const preCompactDiscovered = extractDiscoveredToolNames(messages)
if (preCompactDiscovered.size > 0) {
  boundaryMarker.compactMetadata.preCompactDiscoveredTools = [
    ...preCompactDiscovered,
  ].sort()
}
```

之后 `extractDiscoveredToolNames` 再把这份快照读回来.

所以 compact 之后不会突然“失忆”, 又要求重新 search 一遍所有工具.

## skills 多的时候, 有没有类似的 search tool

有类似的东西, 但不是 `ToolSearch` 这种协议级机制.

对于 skills, Claude Code 更像是做了一套 **skill discovery**:

- 每轮自动注入 `skill_discovery`
- 还有一个 `DiscoverSkills` tool
- 然后真正执行 skill 还是统一走 `SkillTool`

系统提示里直接写了:

```ts
Relevant skills are automatically surfaced each turn as "Skills relevant to your task:" reminders. If you're about to do something those don't cover ... call DiscoverSkills ...
```

attachment 的类型定义也能看到:

```ts
type: 'skill_discovery'
skills: { name: string; description: string; shortId?: string }[]
```

而且 `query.ts` 里是预取注入的:

```ts
// Skill discovery prefetch ...
const pendingSkillPrefetch = skillPrefetch?.startSkillDiscoveryPrefetch(...)
```

所以 skills 这边的思路是:

- 不把所有 skill 细节硬塞给模型
- 而是每轮根据当前任务信号推一些相关 skill
- 不够时再显式调 `DiscoverSkills`

这和 ToolSearch 的目标很像, 但实现层不一样:

- `ToolSearch` 是 API / tool schema 层的按需加载
- `DiscoverSkills` / `skill_discovery` 是应用层的推荐 / 发现

`SkillTool` 里甚至专门记录了“这个 skill 是不是 discover 出来的”:

```ts
was_discovered:
  context.discoveredSkillNames?.has(commandName) ?? false
```

对于 remote skill, 还会强制要求先 discover:

```ts
Remote skill ${slug} was not discovered in this session. Use DiscoverSkills to find remote skills first.
```

所以如果 tools 很多, Claude Code 用的是 `ToolSearch`;  
如果 skills 很多, Claude Code 用的是 `skill_discovery + DiscoverSkills`.

## 小结

整个 ToolSearch 机制, 可以简单理解成一句话:

先只暴露 deferred tool 的名字, 真要用时通过 `ToolSearch` 发现, 再靠 `tool_reference` 和历史状态把这些工具带进后续上下文, 同时尽量不破坏 prompt cache.

这套设计解决的核心问题其实不是“搜索工具”, 而是:

- 工具太多时怎么不把 prompt 撑爆
- MCP 工具动态变化时怎么不频繁打碎 prompt cache
- compact 之后怎么保留已 discover 的工具状态

而 skills 这边, Claude Code 也做了类似的发现机制, 只是实现不是 `defer_loading + tool_reference`, 而是 `skill_discovery + DiscoverSkills + SkillTool`.

