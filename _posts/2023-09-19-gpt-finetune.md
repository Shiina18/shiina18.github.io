---
title: "GPT 微调指南要点"
categories: 
- Machine Learning
tags: NLP
updated: 
comments: true
mathjax: false
---

[Fine-tuning - OpenAI API](https://platform.openai.com/docs/guides/fine-tuning)

这个指南大概也能当成其他 LLM 的微调指南.

<!-- more -->

## 什么时候微调

在决定微调前推荐先尝试其他操作: prompt engineering, prompt chaining (breaking complex tasks into multiple prompts), and [function calling](https://platform.openai.com/docs/guides/gpt/function-calling).

- 很多任务可以通过优化 prompt 得到更好的结果.
- 迭代 prompt 可以得到更快的反馈.
- 即使最终还是决定微调, 之前做的 prompt engineering 依然不会白费, 因为更好的 prompt 能微调出更好结果.

关于 prompt engineering 可以参考 [GPT best practices](https://platform.openai.com/docs/guides/gpt-best-practices).

除了优化结果之外, 另一种微调的使用场景是降低成本 (替换 GPT-4) 或者降低延迟 (每次调用只需要更短的 prompt). 

> If you can achieve good results with GPT-4, you can often reach similar quality with a fine-tuned `gpt-3.5-turbo` model by fine-tuning on the GPT-4 completions, possibly with a shortened instruction prompt.

## 准备训练数据

You should create a diverse set of demonstration conversations that are similar to the conversations you will ask the model to respond to at inference time in production.

### 样例格式

```json
{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "What's the capital of France?"}, {"role": "assistant", "content": "Paris, as if everyone doesn't know that already."}]}
{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "Who wrote 'Romeo and Juliet'?"}, {"role": "assistant", "content": "Oh, just some guy named William Shakespeare. Ever heard of him?"}]}
{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "How far is the Moon from Earth?"}, {"role": "assistant", "content": "Around 384,400 kilometers. Give or take a few, like that really matters."}]}
```

### Crafting prompts

We generally recommend taking the set of instructions and prompts that you found worked best for the model prior to fine-tuning, and including them in every training example.

If you would like to shorten the instructions or prompts that are repeated in every example to save costs, keep in mind that the model will likely behave as if those instructions were included, and it may be hard to get the model to ignore those "baked-in" instructions at inference time.

### 训练集大小

最小 10 个样本. 通常 50~100 个样本有明显提升.

建议先用 50 个精心构造的样本进行微调, 观察效果是否有提升. 如果没有提升, 说明应该重新考虑任务设置并重新构造数据, 等有提升了再考虑加数据量.

## 分析微调后的模型

API 提供了管理微调任务和调用微调后的模型等接口 (略).

**目前不支持在微调的模型上继续微调.** 计划之后支持.

### Metrics

We provide the following training metrics computed over the course of training: training loss, training token accuracy, test loss, and test token accuracy. These statistics are meant to provide a sanity check that training went smoothly (loss should decrease, token accuracy should increase).

```json
{
    "object": "fine_tuning.job.event",
    "id": "ftevent-abc-123",
    "created_at": 1693582679,
    "level": "info",
    "message": "Step 100/100: training loss=0.00",
    "data": {
        "step": 100,
        "train_loss": 1.805623287509661e-5,
        "train_mean_token_accuracy": 1.0
    },
    "type": "metrics"
}
```

评估模型效果除了看测试样本结果之外, 可以考虑 [OpenAI evals framework](https://github.com/openai/evals).

### 优化数据质量

如果效果不尽人意, 可以考虑以下几个方面:

- Collect examples to target remaining issues (扩充处理 badcase 的样本)
- Scrutinize existing examples for issues (修正错误样本)
- Consider the balance and diversity of data (多样化样本)
    - If 60% of the assistant responses in the data says "I cannot answer this", but at inference time only 5% of responses should say that, you will likely get an overabundance of refusals
- Make sure your training examples contain all of the information needed for the response (确保给模型足够信息)
    - If we want the model to compliment a user based on their personal traits and a training example includes assistant compliments for traits not found in the preceding conversation, the model may learn to hallucinate information
- Look at the agreement / consistency in the training examples (检查结果一致性)
- Make sure your all of your training examples are in the same format, as expected for inference (检查格式一致性)

### 调整数据量

We expect a similar amount of improvement every time you double the number of training examples. You can loosely estimate the expected quality gain from increasing the training data size by:

- Fine-tuning on your current dataset
- Fine-tuning on half of your current dataset
- Observing the quality gap between the two

In general, if you have to make a trade-off, a smaller amount of high-quality data is generally more effective than a larger amount of low-quality data. 少量优质 > 大量低质  

### 调整超参数

We recommend initially training without specifying the number of epochs, allowing us to pick a default for you based on dataset size, then adjusting if you observe the following:

- If the model does not follow the training data as much as expected increase the number by 1 or 2 epochs (比如分类, 实体识别等标准化任务, 可以直接求准确分数, 增加轮数避免欠拟合)
    - This is more common for tasks for which there is a single ideal completion (or a small set of ideal completions which are similar). Some examples include classification, entity extraction, or structured parsing. These are often tasks for which you can compute a final accuracy metric against a reference answer.
- If the model becomes less diverse than expected decrease the number by 1 or 2 epochs (生成式任务如果模型输出变得单调, 则减少轮数避免过拟合)
    - This is more common for tasks for which there are a wide range of possible good completions


## 其他

**可微调的模型**: `gpt-3.5-turbo-0613` (recommended), `babbage-002`, `davinci-002`. GPT-4 微调预计今年晚些时候开放.

**Token limits**: Each training example is limited to 4096 tokens. The maximum number of total tokens trained per job is 50 million tokens (`tokens_in_dataset * n_epochs`).

**Estimate costs**

[Pricing](https://openai.com/pricing), 1K tokens 价格

|            Model            | 	Training |  Input   | Output  |
| --------------------------- | ------------ | -------- | ------- |
| GPT-4 (8K context)          |              | $0.03    | 	$0.06 |
| GPT-3.5 Turbo (4K context)  |              | $0.0015  | $0.0020 |
| GPT-3.5 Turbo (fine-tuning) | $0.0080      | 	$0.0120 | $0.0160 |

训练之后调用价格是 8 倍.


```
base cost per 1k tokens * number of tokens in the input file * number of epochs trained
```

## 实际案例

### 正面案例

[原推](https://twitter.com/morgymcg/status/1694828375490039963)

> Finetuning ChatGPT-3.5 brought it up from 22% -> 47% on the Gorilla hugging face api evaluation dataset, cool! 
>
> Full details and code here: [Does Finetuning ChatGPT-3.5 on Gorilla improve api and tool performance?](https://wandb.ai/prompt-eng/gorilla-api/reports/Does-Finetuning-ChatGPT-3-5-on-Gorilla-improve-api-and-tool-performance---Vmlldzo1MjI3MTQw) (里面看图, 微调后在这个数据集上效果比 GPT-4 好)
> 
> Still not indicative that finetuning can make it as useful as GPT-4's \`funcs\` for tool use, but its promising!

### 负面案例

日本的 ML_Bear (Kaggle Master / ML Engineer) 试用了一下微调, 但是效果不好. 博文见 [ChatGPT の Fine-tuning を試したけど上手くいかなかった話](https://zenn.dev/ml_bear/articles/49ed93d33e69cc).

原 po 拿最新的 2023 FIFA 女足世界杯 wiki 文章, 让 chatgpt 根据文章生成 QA pair, 用以微调问答机器人.

共生成了 60 个样本. 原 po 在 GPT-4 上用日语 prompt (生成 QA pair 的 prompt) 效果不好, 所以最后训练数据都用了英语.

实际使用微调后的模型效果不好, 可以参考原文的图.

### 负面案例 2

- [GPT-3.5をFine-tuningして架空のスポーツを教え込んでみた①](https://qiita.com/sakue_103/items/c71e65808cb92356508c)
- [GPT-3.5をFine-tuningして架空のスポーツを教え込んでみた②](https://qiita.com/sakue_103/items/03d79d1d7c7c565830c6)

在第一篇文章中, 原 po 虚构了一种运动, 自己根据其虚构的定义生成日语 QA pair 用来训练. 最终模型效果不好. 

**个人想法.** 我觉得失败案例的问题在于数据构造. 正面案例用的数据集是训练 Gorilla LLM 时用的. 上面两个负面案例都差不多, 想通过 QA pairs 教会 GPT 未知的知识. 但是他们构造数据集的时候只有单纯的 QA pairs, 而没有原始来源 (第一个案例的原 wiki 文章, 第二个案例的架空运动的定义). 直接拿未知知识问 GPT 本来就不会带来好结果, 这样构造没有给模型足够信息, 也违反了微调指南所说的先 prompt engineering, 之后再用最好的 prompt 训练. 会不会在训练集中加入完整的来源文档会更好? 比如 Q: XX 运动规则是什么? A: 完整的虚构规则. Q: 先贴上规则, 再问 XX 运动如何如何.  

### 其他负面案例

- [Fine tuning very very poor results](https://community.openai.com/t/fine-tuning-very-very-poor-results/286284). 

> I have a JSONL file with 3974 records containing 3974 short stories from 212 different notorious English-speaking authors, anonymized (several records for each author):
> 
> ```json
> {"prompt": "Write a text in the style of author_207", "completion": "A complete short story by this author"}  
> ```
>
> I submitted it to the fine-tuning process at OpenAI. I used two models as a basis: first Curie and then Ada. Then, using the new models generated, I asked questions like: “Write a text in the style of author\_207”. With both the results were **terrible**.

任务设置不合适.
