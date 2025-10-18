---
title: "读代码: Cherry Studio 联网搜"
categories: 
- Machine Learning
tags: LLM
updated: 
comments: true
mathjax: false
---

非常粗糙.

如果同时开启知识库和联网搜 (`searchOrchestrationPlugin.ts`), 则用 `SEARCH_SUMMARY_PROMPT`  做意图分析和 query 改写. 简单地把两种搜索的结果拼接起来 (不会混起来重排), index 加上偏移量避免重叠. 如果设置了召回 memory 也会拼在后面.

联网搜分为两种: 

- 一种是 local search (见 `LocalSearchProvider.ts`), 直接解析 SERP (比如 `https://www.google.com/search?q=%s`). 免费. 
- 另一种就是调搜索 API, 比如 Tavily.

访问搜索引擎以及 fetch url 内容都是通过 Electron 在后台打开不可见的浏览器窗口加载指定的 url.

```ts
window.api.searchService.openUrlInSearchWindow(uid, url)
```

类似白嫖搜索引擎的项目还有比如 [duckduckgo-mcp-server](https://github.com/nickclyde/duckduckgo-mcp-server) 以及 [open-webSearch](https://github.com/Aas-ee/open-webSearch/tree/741bbda6376e9d0aba0a46536bdc155f953a4687). 不清楚是否合规.

<!-- more -->

## Prompts

`prompts.ts` 

```ts
// https://github.com/ItzCrazyKns/Perplexica/blob/master/src/lib/prompts/webSearch.ts
export const SEARCH_SUMMARY_PROMPT = `
  You are an AI question rephraser. Your role is to rephrase follow-up queries from a conversation into standalone queries that can be used by another LLM to retrieve information, either through web search or from a knowledge base.
  **Use user's language to rephrase the question.**
  Follow these guidelines:
  1. If the question is a simple writing task, greeting (e.g., Hi, Hello, How are you), or does not require searching for information (unless the greeting contains a follow-up question), return 'not_needed' in the 'question' XML block. This indicates that no search is required.
  2. If the user asks a question related to a specific URL, PDF, or webpage, include the links in the 'links' XML block and the question in the 'question' XML block. If the request is to summarize content from a URL or PDF, return 'summarize' in the 'question' XML block and include the relevant links in the 'links' XML block.
  3. For websearch, You need extract keywords into 'question' XML block. For knowledge, You need rewrite user query into 'rewrite' XML block with one alternative version while preserving the original intent and meaning.
  4. Websearch: Always return the rephrased question inside the 'question' XML block. If there are no links in the follow-up question, do not insert a 'links' XML block in your response.
  5. Knowledge: Always return the rephrased question inside the 'question' XML block.
  6. Always wrap the rephrased question in the appropriate XML blocks to specify the tool(s) for retrieving information: use <websearch></websearch> for queries requiring real-time or external information, <knowledge></knowledge> for queries that can be answered from a pre-existing knowledge base, or both if the question could be applicable to either tool. Ensure that the rephrased question is always contained within a <question></question> block inside these wrappers.

  There are several examples attached for your reference inside the below 'examples' XML block.

  <examples>
  1. Follow up question: What is the capital of France
  Rephrased question:\`
  <websearch>
    <question>
      Capital of France
    </question>
  </websearch>
  <knowledge>
    <rewrite>
      What city serves as the capital of France?
    </rewrite>
    <question>
      What is the capital of France
    </question>
  </knowledge>
  \`

  2. Follow up question: Hi, how are you?
  Rephrased question:\`
  <websearch>
    <question>
      not_needed
    </question>
  </websearch>
  <knowledge>
    <question>
      not_needed
    </question>
  </knowledge>
  \`

  3. Follow up question: What is Docker?
  Rephrased question: \`
  <websearch>
    <question>
      What is Docker
    </question>
  </websearch>
  <knowledge>
    <rewrite>
      Can you explain what Docker is and its main purpose?
    </rewrite>
    <question>
      What is Docker
    </question>
  </knowledge>
  \`

  4. Follow up question: Can you tell me what is X from https://example.com
  Rephrased question: \`
  <websearch>
    <question>
      What is X
    </question>
    <links>
      https://example.com
    </links>
  </websearch>
  <knowledge>
    <question>
      not_needed
    </question>
  </knowledge>
  \`

  5. Follow up question: Summarize the content from https://example1.com and https://example2.com
  Rephrased question: \`
  <websearch>
    <question>
      summarize
    </question>
    <links>
      https://example1.com
    </links>
    <links>
      https://example2.com
    </links>
  </websearch>
  <knowledge>
    <question>
      not_needed
    </question>
  </knowledge>
  \`

  6. Follow up question: Based on websearch, Which company had higher revenue in 2022, "Apple" or "Microsoft"?
  Rephrased question: \`
  <websearch>
    <question>
      Apple's revenue in 2022
    </question>
    <question>
      Microsoft's revenue in 2022
    </question>
  </websearch>
  <knowledge>
    <question>
      not_needed
    </question>
  </knowledge>
  \`

  7. Follow up question: Based on knowledge, Formula of Scaled Dot-Product Attention and Multi-Head Attention?
  Rephrased question: \`
  <websearch>
    <question>
      not_needed
    </question>
  </websearch>
  <knowledge>
    <rewrite>
      What are the mathematical formulas for Scaled Dot-Product Attention and Multi-Head Attention
    </rewrite>
    <question>
      What is the formula for Scaled Dot-Product Attention?
    </question>
    <question>
      What is the formula for Multi-Head Attention?
    </question>
  </knowledge>
  \`
  </examples>

  Anything below is part of the actual conversation. Use the conversation history and the follow-up question to rephrase the follow-up question as a standalone question based on the guidelines shared above.

  <conversation>
  {chat_history}
  </conversation>

  **Use user's language to rephrase the question.**
  Follow up question: {question}
  Rephrased question:
`
```


`WebSearchTool.ts`, `KnowledgeSearchTool.ts` 也类似

```ts
  let summary = 'No search needed based on the query analysis.'
  if (results.query && results.results.length > 0) {
    summary = `Found ${results.results.length} relevant sources. Use [number] format to cite specific information.`
  }

  const citationData = results.results.map((result, index) => ({
    number: index + 1,
    title: result.title,
    content: result.content,
    url: result.url
  }))

  // 🔑 返回引用友好的格式，复用 REFERENCE_PROMPT 逻辑
  const referenceContent = `\`\`\`json\n${JSON.stringify(citationData, null, 2)}\n\`\`\``
  const fullInstructions = REFERENCE_PROMPT.replace(
    '{question}',
    "Based on the search results, please answer the user's question with proper citations."
  ).replace('{references}', referenceContent)
  return {
    type: 'content',
    value: [
      {
        type: 'text',
        text: 'This tool searches for relevant information and formats results for easy citation. The returned sources should be cited using [1], [2], etc. format in your response.'
      },
      {
        type: 'text',
        text: summary
      },
      {
        type: 'text',
        text: fullInstructions
      }
    ]
  }
```

```ts
export const REFERENCE_PROMPT = `Please answer the question based on the reference materials

## Citation Rules:
- Please cite the context at the end of sentences when appropriate.
- Please use the format of citation number [number] to reference the context in corresponding parts of your answer.
- If a sentence comes from multiple contexts, please list all relevant citation numbers, e.g., [1][2]. Remember not to group citations at the end but list them in the corresponding parts of your answer.
- If all reference content is not relevant to the user's question, please answer based on your knowledge.

## My question is:

{question}

## Reference Materials:

{references}

Please respond in the same language as the user's question.
`
```

`BaseApiClient.ts`

```ts
  public async getMessageContent(
    message: Message
  ): Promise<{ textContent: string; imageContents: { fileId: string; fileExt: string }[] }> {
    const content = getMainTextContent(message)

    if (isEmpty(content)) {
      return {
        textContent: '',
        imageContents: []
      }
    }

    const webSearchReferences = await this.getWebSearchReferencesFromCache(message)
    const knowledgeReferences = await this.getKnowledgeBaseReferencesFromCache(message)
    const memoryReferences = this.getMemoryReferencesFromCache(message)

    const knowledgeTextReferences = knowledgeReferences.filter((k) => k.metadata?.type !== 'image')
    const knowledgeImageReferences = knowledgeReferences.filter((k) => k.metadata?.type === 'image')

    // 添加偏移量以避免ID冲突
    const reindexedKnowledgeReferences = knowledgeTextReferences.map((ref) => ({
      ...ref,
      id: ref.id + webSearchReferences.length // 为知识库引用的ID添加网络搜索引用的数量作为偏移量
    }))

    const allReferences = [...webSearchReferences, ...reindexedKnowledgeReferences, ...memoryReferences]

    const referenceContent = `\`\`\`json\n${JSON.stringify(allReferences, null, 2)}\n\`\`\``
    const imageReferences = knowledgeImageReferences.map((r) => {
      return { fileId: r.metadata?.id, fileExt: r.metadata?.ext }
    })

    return {
      textContent: isEmpty(allReferences)
        ? content
        : REFERENCE_PROMPT.replace('{question}', content).replace('{references}', referenceContent),
      imageContents: isEmpty(knowledgeImageReferences) ? [] : imageReferences
    }
  }
```
