---
title: "读 Claude Code 源码 - Web Search & Web Fetch"
categories: 
- LLM
tags: Agent
updated: 
comments: true
mathjax: false
---

`WebSearch` 调用服务端的搜索工具, `WebFetch` 本地抓 URL、HTML 转 markdown、再交给一个小模型按 prompt 提炼.

<!-- more -->

## WebSearch

### Schema

```ts
const inputSchema = lazySchema(() =>
  z.strictObject({
    query: z.string().min(2).describe('The search query to use'),
    allowed_domains: z
      .array(z.string())
      .optional()
      .describe('Only include search results from these domains'),
    blocked_domains: z
      .array(z.string())
      .optional()
      .describe('Never include search results from these domains'),
  }),
)
```

禁止同时传 `allowed_domains` 和 `blocked_domains`.

```ts
'Error: Cannot specify both allowed_domains and blocked_domains in the same request'
```

The `max_uses` parameter limits the number of searches performed. If Claude attempts more searches than allowed, the `web_search_tool_result` is an error with the `max_uses_exceeded` error code.

```ts
function makeToolSchema(input: Input): BetaWebSearchTool20250305 {
  return {
    type: 'web_search_20250305',
    name: 'web_search',
    allowed_domains: input.allowed_domains,
    blocked_domains: input.blocked_domains,
    max_uses: 8, // Hardcoded to 8 searches maximum
  }
}
```

从结果解析那段注释来看, 设计上就是允许同一次 `WebSearch` 里出现多轮 search, 限制 `max_uses` 轮次.

```ts
  // The result is a sequence of these blocks:
  // - text to start -- always?
  // [
  //    - server_tool_use
  //    - web_search_tool_result
  //    - text and citation blocks intermingled
  //  ]+  (this block repeated for each search)
```

### Prompt

```ts
- Allows Claude to search the web and use the results to inform responses
- Provides up-to-date information for current events and recent data
- Returns search result information formatted as search result blocks, including links as markdown hyperlinks
- Use this tool for accessing information beyond Claude's knowledge cutoff
- Searches are performed automatically within a single API call
```

回答之后的引用格式.

```ts
CRITICAL REQUIREMENT - You MUST follow this:
  - After answering the user's question, you MUST include a "Sources:" section at the end of your response
  - In the Sources section, list all relevant URLs from the search results as markdown hyperlinks: [Title](URL)
  - This is MANDATORY - never skip including sources in your response
  - Example format:

    [Your answer here]

    Sources:
    - [Source Title 1](https://example.com/1)
    - [Source Title 2](https://example.com/2)
```

```ts
Usage notes:
  - Domain filtering is supported to include or block specific websites
  - Web search is only available in the US
```

时间约束不是通过类似 time filter / recency 这样的参数, 而是 prompt 引导在搜索 query 中加上年份 (比如 "XXX 文档 2026"). 

```ts
IMPORTANT - Use the correct year in search queries:
  - The current month is ${currentMonthYear}. You MUST use this year when searching for recent information, documentation, or current events.
  - Example: If the user asks for "latest React docs", search for "React documentation" with the current year, NOT last year
```

拿到链接拼回 tool result 后再次提醒.

```ts
'\nREMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.'
```

## WebFetch

```ts
const inputSchema = lazySchema(() =>
  z.strictObject({
    url: z.string().url().describe('The URL to fetch content from'),
    prompt: z.string().describe('The prompt to run on the fetched content'),
  }),
)
```

```ts
const outputSchema = lazySchema(() =>
  z.object({
    bytes: z.number().describe('Size of the fetched content in bytes'),
    code: z.number().describe('HTTP response code'),
    codeText: z.string().describe('HTTP response code text'),
    result: z
      .string()
      .describe('Processed result from applying the prompt to the content'),
    durationMs: z
      .number()
      .describe('Time taken to fetch and process the content'),
    url: z.string().describe('The URL that was fetched'),
  }),
)
```

抓网页, 转 markdown, 传 prompt 指导小模型提取信息.

优先用 MCP (比如智谱 coding plan 就是提供的自家的 web fetch MCP), 对 Github 优先用 gh CLI.

```ts
IMPORTANT: WebFetch WILL FAIL for authenticated or private URLs. Before using this tool, check if the URL points to an authenticated service (e.g. Google Docs, Confluence, Jira, GitHub). If so, look for a specialized MCP tool that provides authenticated access.

- Fetches content from a specified URL and processes it using an AI model
- Takes a URL and a prompt as input
- Fetches the URL content, converts HTML to markdown
- Processes the content with the prompt using a small, fast model
- Returns the model's response about the content
- Use this tool when you need to retrieve and analyze web content

Usage notes:
  - IMPORTANT: If an MCP-provided web fetch tool is available, prefer using that tool instead of this one, as it may have fewer restrictions.
  - The URL must be a fully-formed valid URL
  - HTTP URLs will be automatically upgraded to HTTPS
  - The prompt should describe what information you want to extract from the page
  - This tool is read-only and does not modify any files
  - Results may be summarized if the content is very large
  - Includes a self-cleaning 15-minute cache for faster responses when repeatedly accessing the same URL
  - When a URL redirects to a different host, the tool will inform you and provide the redirect URL in a special format. You should then make a new WebFetch request with the redirect URL to fetch the content.
  - For GitHub URLs, prefer using the gh CLI via Bash instead (e.g., gh pr view, gh issue view, gh api).
```

### 权限和安全策略

有一层“预批准域名”`src\tools\WebFetchTool\preapproved.ts:5` 是源码里内置的一份 host 白名单, 命中之后会直接 allow.

```ts
// For legal and security concerns, we typically only allow Web Fetch to access
// domains that the user has provided in some form. However, we make an
// exception for a list of preapproved domains that are code-related.
//
// SECURITY WARNING: These preapproved domains are ONLY for WebFetch (GET requests only).
// The sandbox system deliberately does NOT inherit this list for network restrictions,
// as arbitrary network access (POST, uploads, etc.) to these domains could enable
// data exfiltration. Some domains like huggingface.co, kaggle.com, and nuget.org
// allow file uploads and would be dangerous for unrestricted network access.
//
// See test/utils/sandbox/webfetch-preapproved-separation.test.ts for verification
// that sandbox network restrictions require explicit user permission rules.

export const PREAPPROVED_HOSTS = new Set([
  // Anthropic
  'platform.claude.com',
  'code.claude.com',
  'modelcontextprotocol.io',
  'github.com/anthropics',
  'agentskills.io',

  // Top Programming Languages
  'docs.python.org', // Python
  'en.cppreference.com', // C/C++ reference
  
  ...
  
  // Other Essential Tools
  'git-scm.com', // Git
  'nginx.org', // Nginx
  'httpd.apache.org', // Apache HTTP Server
])
```

### 拉取链路

缓存

```ts
// Cache with 15-minute TTL and 50MB size limit
// LRUCache handles automatic expiration and eviction
```

域名预检缓存

```ts
// Separate cache for preflight domain checks. URL_CACHE is URL-keyed, so
// fetching two paths on the same domain triggers two identical preflight
// HTTP round-trips to api.anthropic.com. This hostname-keyed cache avoids
// that. Only 'allowed' is cached — blocked/failed re-check on next attempt.
```

- 页面内容缓存按 URL
- 安全预检缓存按 hostname
- 而且只缓存 `allowed`, 不缓存失败态, 因为 blocked / failed 可能是暂时性的, 下次重试未必还是一样.

资源限制:

```ts
// "Implement resource consumption controls because setting limits on CPU,
// memory, and network usage for the Web Fetch tool can prevent a single
// request or user from overwhelming the system."
const MAX_HTTP_CONTENT_LENGTH = 10 * 1024 * 1024

const FETCH_TIMEOUT_MS = 60_000
const DOMAIN_CHECK_TIMEOUT_MS = 10_000
const MAX_REDIRECTS = 10
export const MAX_MARKDOWN_LENGTH = 100_000
```

自己接管 redirect.

```ts
 * "Do not automatically follow redirects because following redirects could
 * allow for an attacker to exploit an open redirect vulnerability in a
 * trusted domain to force a user to make a request to a malicious domain
 * unknowingly"
```

只允许很有限的跳转:

- 同 origin 改 path / query
- `www.` 的增减
- 其他跨 host redirect 不自动跟

如果真跳到别的 host, `WebFetchTool` 不会偷偷跟过去, 而是返回一个特殊结果, 明确告诉模型“请用新 URL 和 prompt 再调一次”. 

```ts
    // Check if we got a redirect to a different host
    if ('type' in response && response.type === 'redirect') {
      const statusText =
        response.statusCode === 301
          ? 'Moved Permanently'
          : response.statusCode === 308
            ? 'Permanent Redirect'
            : response.statusCode === 307
              ? 'Temporary Redirect'
              : 'Found'

      const message = `REDIRECT DETECTED: The URL redirects to a different host.

Original URL: ${response.originalUrl}
Redirect URL: ${response.redirectUrl}
Status: ${response.statusCode} ${statusText}

To complete your request, I need to fetch content from the redirected URL. Please use WebFetch again with these parameters:
- url: "${response.redirectUrl}"
- prompt: "${prompt}"`
```

### 内容处理

抓到内容后, 区分 HTML 和非 HTML. 用现成的 [turndown](https://www.npmjs.com/package/turndown) 库把 HTML 转成 markdown

```ts
// Lazy singleton — defers the turndown → @mixmark-io/domino import (~1.4MB
// retained heap) until the first HTML fetch, and reuses one instance across
// calls
```

```ts
if (contentType.includes('text/html')) {
  markdownContent = (await getTurndownService()).turndown(htmlContent)
}
```

二进制内容也没简单丢掉

```ts
// Binary content: save raw bytes to disk with a proper extension so Claude
// can inspect the file later. We still fall through to the utf-8 decode +
// Haiku path below — for PDFs in particular the decoded string has enough
// ASCII structure (/Title, text streams) that Haiku can summarize it
```

### 加速

`WebFetch` 加速点主要有五个.

第一层是 URL 缓存和域名预检缓存, 上面已经说了.

第二层是“可信内容直出”:

- 如果 URL 属于 preapproved domain
- 且 `content-type` 是 `text/markdown`
- 且长度小于 `MAX_MARKDOWN_LENGTH`

那么它直接把 markdown 原文返回, 不再过二级模型. 也就是说, 对官方文档站这类最常见场景, 它直接省掉一次 Haiku 调用.

第三层是内容截断:

```ts
// Truncate content to avoid "Prompt is too long" errors from the secondary model
```

这虽然看起来只是防报错, 但本质上也是 latency 控制:  不让二级模型吃超长网页.

第四层是二级模型本身就选了快模型 (haiku). 

```ts
- Processes the content with the prompt using a small, fast model
```

第五层是 prompt 也按站点信任级别分流. 对预批准文档站, 指令比较宽松, 对普通网站则更保守. 这里的 `prompt` 参数是调 web fetch 工具时传的 prompt 参数.

```ts  
export function makeSecondaryModelPrompt(
  markdownContent: string,
  prompt: string,
  isPreapprovedDomain: boolean,
): string {
  const guidelines = isPreapprovedDomain
    ? `Provide a concise response based on the content above. Include relevant details, code examples, and documentation excerpts as needed.`
    : `Provide a concise response based only on the content above. In your response:
 - Enforce a strict 125-character maximum for quotes from any source document. Open Source Software is ok as long as we respect the license.
 - Use quotation marks for exact language from articles; any language outside of the quotation should never be word-for-word the same.
 - You are not a lawyer and never comment on the legality of your own prompts and responses.
 - Never produce or reproduce exact song lyrics.`

  return `
Web page content:
---
${markdownContent}
---

${prompt}

${guidelines}
`
}
```
