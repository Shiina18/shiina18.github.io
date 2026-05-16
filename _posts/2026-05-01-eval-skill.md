---
title: "如何评估 skill"
categories: 
- LLM
tags: Agent
updated: 
comments: true
mathjax: false
---

<!-- more -->

## Anthropic

Anthropic 的 [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) 里已经提供了评估思路. 一个具体例子可以参考 [notion skill](https://github.com/makenotion/claude-code-notion-plugin).

测试用例

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Within the workspace, organize results by iteration (`iteration-1/`, `iteration-2/`, etc.) and within that, each test case gets a directory (`eval-0/`, `eval-1/`, etc.). 用序号记录版本. 对有无 skill 以及不同版本 skill 做本地 AB 对比.

Write an `eval_metadata.json` for each test case

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

跑完记录信息 (因为 cc 没有自动持久化这些东西, 所以要显示记下来)

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

最后打分, 聚合, 用 html 呈现给人看, 人给反馈. Empty feedback means the user thought it was fine. Focus your improvements on the test cases where the user had specific complaints.

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."},
    {"run_id": "eval-2-with_skill", "feedback": "perfect, love this", "timestamp": "..."}
  ],
  "status": "complete"
}
```

---

优化方向

- Generalize from the feedback
- Keep the prompt lean
- Explain the why. Try hard to explain the why behind everything you're asking the model to do. Today's LLMs are smart. They have good theory of mind and when given a good harness can go beyond rote instructions and really make things happen.
- Look for repeated work across test cases. 重复工作写成脚本.

---

Desc 优化

- Generate trigger eval queries. 正负例都要有, 负例要难. 而且 query 要更 "真实且复杂", 像口头语一样.

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

For the **should-not-trigger** queries (8-10), the most valuable ones are the near-misses — queries that share keywords or concepts with the skill but actually need something different. Think adjacent domains, ambiguous phrasing where a naive keyword match would trigger but shouldn't, and cases where the query touches on something the skill does but in a context where another tool is more appropriate.

## Perplexity

- Perplexity. 2026-05. [Designing, Refining, and Maintaining Agent Skills at Perplexity](https://research.perplexity.ai/articles/designing-refining-and-maintaining-agent-skills-at-perplexity)

> In fact, early research has [shown](https://arxiv.org/abs/2602.12670) that if you're using LLMs to write Skills, the LLM will probably not benefit from it: “Self-generated Skills provide no benefit on average, showing that models cannot reliably author the procedural knowledge they benefit from consuming.”

---

Desc:  good description says when the agent should load the Skill. Do not summarize the workflow.

---

Body: Don't write out a series of commands.

For example, you don’t need to write, “`git log # find the commit; git checkout main; git checkout -b <clean-branch>; git cherry-pick <commit>;`”

Instead, write, “Cherry-pick the commit onto a clean branch. Resolve conflicts preserving intent. If it can't land cleanly, explain why.”

---

At Perplexity, we run many eval suites to check for different things. There are Skill loading and Skill file reads, which checks the precision, recall, and forbidden checks of the Skill loading itself. Will the agent route your Skill when it's supposed to? These ensure new Skills don’t break existing boundaries. 

There are also evals that can check for proper progressive loading. The agent might load the Skill, but does it read the accessory file or files? For example, if you have a finance Skill for finance queries, does it read the special `FORMATTING.md` file?

There are also evals for Skills that test for end-to-end task completion within domains. We run the full agent loop and use an LLM judge to grade the results based on a rubric of well-defined criteria.

Finally, it’s important to run these evals against different models.

## LangChain

- LangChain. 2026-03. [Evaluating Skills](https://www.langchain.com/blog/evaluating-skills)

也开源了

To see all the tests we ended up writing, see our [benchmarking repo here](https://github.com/langchain-ai/skills-benchmarks/tree/main?ref=blog.langchain.com).
