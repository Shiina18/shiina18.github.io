---
title: "【机翻】语音智能体中的记忆问题比你想象的更难"
categories: 
- LLM
tags: Agent
updated: 
comments: true
mathjax: false
---

- [Memory in Voice Agents Is a Harder Problem Than You Think](https://x.com/manthanguptaa/status/2054184627854877176)

<!-- more --> 

# Memory in Voice Agents Is a Harder Problem Than You Think

语音智能体中的记忆问题比你想象的更难

The first time I tried to plug a memory layer into a voice agent, it slowed by hundreds of milliseconds on the first turn and never recovered. The conversation went from natural to “is the line still there?” in a single round-trip, because I had ported a text-agent memory architecture wholesale: a synchronous vector lookup against a hosted store, a small re-ranking pass, then the LLM. On a chat surface, nobody would have noticed. On voice, every turn felt like the agent was buffering before it spoke.

第一次尝试在语音智能体中接入记忆层时，它在第一轮对话就慢了数百毫秒，并且再也没有恢复过来。仅仅一个回合，对话体验就从自然流畅变成了“线路还在吗？”，因为我完全照搬了文本智能体的记忆架构：针对托管存储进行同步向量检索，执行一个小的重排序，再进入 LLM。在聊天界面上，没人会注意到这个延迟。但在语音交互中，每一轮对话都让人感觉智能体在开口前卡顿缓冲。

In the [voice agents primer](https://manthanguptaa.in/posts/voice_agents_primer) I flagged memory as one of the harder engineering problems in space and promised to come back to it. This is that post. The short version: voice memory is not text memory with a tighter clock. The clock is so much tighter that the entire read/write path has to invert. Most of what you think of as “memory” cannot live in the response critical path at all. It has to be pre-loaded, pre-computed, or written after the fact.

在[语音智能体入门指南](https://manthanguptaa.in/posts/voice_agents_primer)中，我曾指出记忆是该领域较难的工程问题之一，并承诺会专门撰文探讨。这篇文章就是来兑现承诺的。简而言之：语音记忆并不是时间要求更紧迫的文本记忆。它的时间要求极高，以至于整个读写路径都必须反转。你所认为的绝大多数“记忆”根本不能存在于响应的关键路径（critical path）中。它必须被预加载、预计算，或者在事后写入。

I have spent a fair bit of time staring at memory across surfaces, reverse-engineering how [ChatGPT](https://manthanguptaa.in/posts/chatgpt_memory) and [Claude](https://manthanguptaa.in/posts/claude_memory) actually do it, building the layered memory hierarchy inside the [Water](https://github.com/manthanguptaa/water) framework, building BYOM as a portable user-owned memory layer, and then [arguing publicly](https://manthanguptaa.in/posts/memory_is_a_mistake) that most AI products shouldn’t ship memory at all. None of those experiences quite prepared me for what voice does to the design space. This post is about the constraints, the tradeoffs they force, the four families of architectures I keep seeing in production, and the things you only learn the hard way.

我花了不少时间琢磨不同交互界面上的记忆问题，逆向工程了 [ChatGPT](https://manthanguptaa.in/posts/chatgpt_memory) 和 [Claude](https://manthanguptaa.in/posts/claude_memory) 的实际做法，在 [Water](https://github.com/manthanguptaa/water) 框架中构建了分层记忆体系，开发了 BYOM 作为可移植的用户自有记忆层，并且[公开主张](https://manthanguptaa.in/posts/memory_is_a_mistake)大多数 AI 产品根本不该附带记忆功能。但这些经验都没能让我完全准备好应对语音如何改变这一设计空间。这篇文章将探讨其中的限制条件、这些限制迫使我们做出的权衡、我在生产环境中反复看到的四大类架构，以及那些只有踩过坑才会明白的事。

## Why Voice Memory Sits Differently from Text Memory

为何语音记忆与文本记忆位处不同

Text agents come with natural slack. The user types, sees a loading indicator, and tolerates 1-3 seconds before a response. That gap is where most memory work hides in the form of vector lookups, semantic search over past chats, even a quick summarization pass. Text trained users to wait, and you can spend that wait however you like.

文本智能体自带天然的时间余量。用户输入文字，看到加载提示，并能容忍回复前有 1-3 秒的延迟。大多数记忆处理工作（形式包括向量检索、对历史聊天的语义搜索，甚至是一次快速的总结）就隐藏在这个时间差里。文本场景培养了用户的等待习惯，而你可以随心所欲地利用这段等待时间。

Voice does not give you that gift. The expected end-to-end response is 500-800ms, and that budget includes everything: STT finalization, memory lookup, LLM time-to-first-token, TTS first-chunk synthesis, and audio delivery. If memory eats more than 50-100ms of that, the conversational rhythm breaks. A single round-trip to a hosted vector database is often 20-80ms just on the network. Add embedding computation, ANN (approximate nearest neighbor) search, and result formatting, and you have spent your entire memory budget before the LLM has seen a token.

语音并没有给你这样的馈赠。预期的端到端响应时间是 500-800 毫秒，这个时间预算包含了所有环节：语音转文本（STT）完成、记忆检索、大语言模型（LLM）的首字响应时间（TTFT）、文本转语音（TTS）的首块合成，以及音频传输。如果记忆层消耗了其中超过 50-100 毫秒的时间，对话的节奏就会被破坏。单次往返托管向量数据库的网络延迟通常就需要 20-80 毫秒。如果再加上嵌入计算、近似最近邻（ANN）搜索和结果格式化，在 LLM 看到任何 token 之前，你的记忆时间预算就已经耗尽了。

Input format is the second wedge. Text agents receive structured prose, but voice agents receive a streaming transcript of spontaneous speech, including disfluencies, restarts, false antecedents, and corrections. Any fact extraction pipeline that worked beautifully on chat will struggle here.

输入格式是第二个分岔因素。文本智能体接收的是结构化的书面语，而语音智能体接收的是自发性语音的流式转录文本，其中包含话语不流利现象、重新开头、错误的先行词与指代后改口。任何在聊天中表现优异的事实提取管道在这里都会举步维艰。

Turn density is the third. Voice conversations produce shorter, faster, less information-dense turns, typically 10-30 words. A 10-minute call lands at 40-60 turns and 1500-2000 tokens of transcript on average. That sounds manageable until you consider how audio inflates it on speech-native models. OpenAI’s own [Realtime API cookbook](https://developers.openai.com/cookbook/examples/context_summarization_with_realtime_api) is blunt: “in practice you’ll often see ≈ 10× more tokens for the same sentence in audio versus text”, and gpt-realtime caps at a 32k window. A modest support call is enough to put you on the wrong side of that line.

对话轮次密度是第三个分岔因素。语音对话产生的轮次更短、更快，信息密度更低，通常为 10-30 个词。一个 10 分钟的通话平均会产生 40-60 个轮次，以及 1500-2000 个 token 的转录文本。这听起来似乎可以处理，直到你考虑到音频在原生语音模型上是如何使 token 数量膨胀的。OpenAI 自己的 [Realtime API 官方指南](https://developers.openai.com/cookbook/examples/context_summarization_with_realtime_api)说得很直白：“在实践中，对于相同的句子，音频格式下的 token 数量通常是文本格式的 10 倍左右”，而且 gpt-realtime 的上下文窗口上限为 32k。一通普通的客服电话就足以让你超出这个限制。

The fourth wedge usually gets ignored: the cold-start problem. On a chat surface you almost always have an authenticated session. On telephony voice, you often start with nothing but a phone number and have to identify the caller in the first few hundred milliseconds. Memory architectures that assume “you know who the user is at turn one” are fragile. The good ones make the unknown caller case the base condition.

第四个分岔因素往往被忽视：冷启动问题。在聊天界面上，你几乎总是有一个经过身份验证的会话。而在电话语音中，你通常一开始除了一个电话号码什么都没有，并且必须在最初的几百毫秒内识别出呼叫者。那些假设“你在第一轮就知道用户是谁”的记忆架构是很脆弱的。优秀的架构会将未知呼叫者的情况作为基础条件来处理。

## The Memory Layers That Actually Matter

真正重要的记忆层

Three layers are worth caring about, and they line up with how the survey literature talks about agent memory more broadly. The recent [“From Storage to Experience” survey](https://arxiv.org/abs/2605.06716) frames the same evolution as Storage -> Reflection -> Experience. Letta’s product docs codify roughly the same split as Core -> Recall -> Archival. The labels change, but the layers don’t.

有三个记忆层值得关注，它们与综述文献中讨论智能体记忆的框架相对应。最近的[《从存储到体验》综述文章 (From Storage to Experience)](https://arxiv.org/abs/2605.06716) 将同样的演变概括为 存储 -> 反思 -> 体验 (Storage -> Reflection -> Experience)。Letta 的产品文档大致也将这种划分归纳为 核心 -> 召回 -> 归档 (Core -> Recall -> Archival)。标签虽然变了，但层次没变。

Conversation memory is the current call’s transcript and turn ordering, living in the LLM context window. A long call will overflow a practical 4-8k window before you notice, even though modern models nominally support 128k+ tokens. Stuffing the entire transcript into context slows generation and degrades the model’s effective attention on the parts that matter.

**对话记忆 (Conversation memory)** 是当前通话的转录文本和轮次顺序，存在于 LLM 的上下文窗口中。一次长通话会在你不经意间溢出实际可用的 4-8k 窗口，尽管现代模型名义上支持 128k+ 的 token。将整个转录文本塞进上下文会减慢生成速度，并削弱模型对关键信息的有效注意力。

Session facts is the working memory layer. Things established during the current call that have to be carried forward inside it. “The caller’s name is Priya. They are calling about account 4821. They sound frustrated.” This is what the agent must not re-ask for five turns later. Without it, voice agents come across as goldfish, and goldfish behavior is the single fastest way to destroy trust on a phone call.

**会话事实 (Session facts)** 是工作记忆层。指在当前通话中确立、并须在后续轮次中沿用的事实。“来电者的名字叫 Priya。她致电询问账户 4821。她听起来很沮丧。” 这是智能体在五轮对话后绝对不能再次询问的信息。如果没有这一层，语音智能体就会表现得像金鱼，而在电话中，这种“金鱼行为”是头号最快毁掉信任的方式。

User profile is the long-term layer. Persistent facts across conversations. Name, preferences, last-call summary, open issues, relationship context. This is what lets a returning caller feel recognized rather than restarting from zero.

**用户画像 (User profile)** 是长期记忆层。指跨对话持久存在的事实。包括姓名、偏好、上次通话总结、未解决的问题、关系背景等。这能让再次来电的用户感到被认出来，而不是从零开始。

The hard design question is the middle two layers: how do you capture and surface session facts within a call, and how do you persist and retrieve user profile information across calls, both under the latency constraints above?

最困难的设计问题在于中间这两层：如何在上述延迟限制下，在通话中捕获和呈现会话事实，以及如何在多次通话间持久化并检索用户画像信息？

## Where the Latency Actually Goes

延迟究竟花在了哪里

Let’s make the constraint concrete. A typical voice agent response cycle looks like this:

让我们把这个限制具体化。典型的语音智能体响应周期如下：

1.  User stops speaking -> VAD detects end of turn (~100ms)
2.  Final transcript arrives from streaming STT (~50ms after VAD)
3.  Memory retrieval runs (how long?)
4.  LLM receives augmented prompt -> TTFT (~300ms for a fast model)
4.  LLM 接收增强后的提示词 -> 首字响应时间 TTFT（对于速度快的模型约 300 毫秒）
5.  TTS first audio chunk (~100ms after first tokens)
6.  Total target: ~600ms from end of user speech to first audio

---

1.  用户停止说话 -> VAD 检测到话语结束（约 100 毫秒）
2.  流式 STT 返回最终转录文本（VAD 后约 50 毫秒）
3.  记忆检索运行（需要多长时间？）
4.  LLM 接收增强后的提示词 -> 首字响应时间 TTFT（对于速度快的模型约 300 毫秒）
5.  TTS 首块音频合成（收到首批 token 后约 100 毫秒）
6.  总目标：从用户说话结束到第一段音频输出，大约 600 毫秒。

Step 3 is where memory lives, and it has to fit in roughly 50-100ms to stay under that 600ms total.

第 3 步是记忆层发挥作用的地方，它的耗时必须被控制在大约 50-100 毫秒以内，以确保总时长低于 600 毫秒。

That immediately rules out most of the obvious approaches. A synchronous vector search at turn time runs 30-100ms for the query, plus another 50-100ms for embedding, ranking, and formatting. Mem0’s own [voice agent memory guide](https://mem0.ai/blog/ai-memory-for-voice-agents) puts semantic search at “50-200ms depending on your vector store and infrastructure”. Even Zep, engineered specifically for low-latency context retrieval, [advertises P95 of <200ms standalone and <250ms with LiveKit voice agents](https://blog.getzep.com/zep-livekit/). Those numbers are great for chat. For voice they live at the very edge of acceptable, and only on the median, never the tail. An LLM-based summarization pass at turn time is a non-starter, 300-800ms blows the entire budget before the main LLM has even started. The one option that genuinely works is a key-value fetch from a fast in-process cache or a local Redis: 1-5ms, predictable, invisible.

这立刻排除了大多数显而易见的方法。在对话轮次进行时的同步向量搜索，仅查询就需要 30-100 毫秒，加上嵌入、排序和格式化还需要 50-100 毫秒。Mem0 自己的[语音智能体记忆指南](https://mem0.ai/blog/ai-memory-for-voice-agents)指出，语义搜索“根据你的向量存储和基础设施，大约需要 50-200 毫秒”。甚至连专为低延迟上下文检索而设计的 Zep，其[宣传的独立 P95 延迟也仅为 <200 毫秒，与 LiveKit 语音智能体结合时 <250 毫秒](https://blog.getzep.com/zep-livekit/)。这些数据对聊天来说很棒。但对于语音来说，它们处于可接受的极度边缘，且这些数字只在中位数上成立，长尾则无法指望。在轮次进行时使用基于 LLM 的总结更是天方夜谭，300-800 毫秒的耗时在主 LLM 还没启动前就耗尽了所有预算。唯一真正可行的选项是从快速的进程内缓存或本地 Redis 中获取键值对（Key-Value）：1-5 毫秒，可预测，对总延迟几乎可忽略。

## The Four Questions Behind Every Voice Memory Architecture

每一种语音记忆架构背后的四个问题

Once you have internalized “memory work cannot live in the critical path”, the design space collapses to four decisions. You can find the same four questions implicit in every production memory system I have looked at, Letta, Zep, Mem0, A-MEM, MemoryBank, Generative Agents, even though each of them answers the questions differently. Pin them down and most of the architecture follows. (Mem0’s [voice memory guide](https://mem0.ai/blog/ai-memory-for-voice-agents) is a useful read on the same terrain if you want a vendor’s point of view.)

一旦你深刻认识到“记忆工作不能存在于关键路径中”，设计空间就会收缩为四个决定。无论是在 Letta、Zep、Mem0、A-MEM、MemoryBank 还是 Generative Agents 中，你都能发现这四个隐藏的问题，尽管它们各自给出的答案不尽相同。确定这四个问题的答案，大部分架构也就顺理成章了。（如果你想从供应商的角度了解这一领域，Mem0 的[语音记忆指南](https://mem0.ai/blog/ai-memory-for-voice-agents)是一份很有用的参考资料。）

When do you write? Per-turn (fact-extract after every exchange) or per-session (batch at end-of-call). Per-session is cheaper and produces cleaner extractions because the model sees the whole arc. Per-turn is more expensive and noisier, but durable: if the process crashes mid-call, the WebRTC session dies without a clean disconnect, or the end-of-call extraction itself fails, per-session loses everything for that call while per-turn keeps every fact written through the last successful turn. Almost every production voice deployment I have seen accepts the cost penalty and runs per-turn, because abnormal terminations are routine in telephony and “we lost the transcript” is not a failure mode you want to debug live. (A third option, sleep-time writes, gets its own section below.)

**何时写入？** 是按轮次（在每次交流后进行事实提取）还是按会话（在通话结束时批量处理）。按会话处理更便宜，且提取的内容更干净，因为模型看到了整个对话脉络。按轮次处理成本更高，噪音也更大，但更持久：如果进程在通话中途崩溃、WebRTC 会话非正常断开，或者通话结束时的提取任务本身失败，按会话处理将丢失本次通话的所有内容，而按轮次处理则能保留直到最后一次成功轮次的所有事实。我见过的几乎每一个生产级语音部署，都宁愿承担成本惩罚而选择按轮次处理，因为在电话系统中异常终止是家常便饭，而“我们丢失了转录文本”绝对不是你想要在生产环境中调试的故障模式。（第三种选项是闲时写入，下文将单独讨论。）

What do you write? The question I would ask of every candidate fact is: would this actually change how the agent responds in a future session? If not, it’s noise, and noisy memory hurts more than absent memory because it makes retrieval less precise on the things that do matter. In practice this means the more specialized your use case, the more aggressive your filtering should be. A general assistant can afford generic LLM driven extraction. A medical intake agent should be writing into a typed schema and rejecting anything that doesn’t fit.

**写入什么？** 我会对每一个候选事实提出的问题是：它是否真的会改变智能体在未来会话中的响应方式？如果不会，那就是噪音，而且噪音记忆比缺乏记忆危害更大，因为它会降低关键事物检索的精确度。在实践中，这意味着你的用例越专业，你的过滤就应该越激进。通用的助手可以负担得起由 LLM 驱动的通用提取。但一个医疗登记智能体应该将其写入严格限制在强类型模式（typed schema）中，并拒绝任何不符合规范的信息。

How do you retrieve? Four patterns dominate:

**如何检索？** 四种模式占据了主导地位：

```text
| Pattern | When it works | What it costs |
|---------|----------------|----------------|
| Dump everything | Users with <20-30 memories | Token bloat past the threshold; ["lost in the middle"](https://arxiv.org/abs/2307.03172) past long contexts |
| Pure semantic search | When relevance per-turn is the bottleneck | 50-200ms per turn - usually too much for voice |
| Pre-loaded context | When the user has stable, summarizable history | Stale within long sessions; cold-start has nothing to load |
| Hybrid (pre-load + on-demand) | Most production voice agents | Requires a topic-shift detector, but it's the right default |
```

```text
| 模式 | 适用场景 | 代价与成本 |
|---------|----------------|----------------|
| 全部加载 (Dump everything) | 用户历史记忆 <20-30 条 | 超过阈值后会导致 Token 膨胀；长上下文会导致[“迷失在中间”](https://arxiv.org/abs/2307.03172) |
| 纯语义搜索 (Pure semantic search) | 每轮的相关性成为瓶颈时 | 每轮 50-200 毫秒 - 对语音来说通常太慢了 |
| 预加载上下文 (Pre-loaded context) | 用户有稳定的、可总结的历史记录时 | 在长会话中容易过期；冷启动时无内容可加载 |
| 混合模式 (预加载 + 按需) | 大多数生产级语音智能体 | 需要一个话题转换检测器，但它是正确的默认选择 |
```

Where does the work happen? Inline, parallel (a memory agent alongside the voice pipeline), or post-processing. For voice, the answer is almost always parallel for writes and pre-loaded for reads, with inline retrieval reserved for the tightest cases.

**工作在哪里发生？** 内联（Inline，落在主响应路径上）、并行（Parallel，与语音管道并行的记忆智能体），还是后处理（Post-processing）。对于语音，答案几乎总是：写入操作并行，读取操作预加载，而内联检索仅保留给延迟预算最紧的情况。

These four answers, taken together, decide which architecture family you are in.

这四个答案结合起来，就决定了你所采用的架构体系。

## The Architecture Landscape

架构图景

I would group the voice memory architectures I have looked at into roughly four families. They aren’t mutually exclusive but most real systems blend at least two and they make for a useful map.

我将我研究过的语音记忆架构粗略地分为四大类。它们并不相互排斥，但大多数真实系统仍会至少融合其中两种；这四类划分本身构成一张有用的版图。

Family 1: Native framework state

**第一类：原生框架状态**

Every serious voice agent framework maintains conversation state inside the pipeline for the duration of a session, and the major end-to-end speech APIs do the same on their side, often with built-in context truncation. This family handles only the within session problem and nothing survives the call. Treat it as the floor of any architecture, not the architecture itself which is useful as the place to put session facts, useless for anything across calls.

所有成熟的语音智能体框架都会在会话期间将对话状态保留在管道内部，主要的端到端语音 API 也在其内部执行同样的操作，并且通常带有内置的上下文截断功能。这类架构只处理会话内的问题，没有任何信息在通话后留存。请把它当作任何架构的基础底座，而不是架构本身——它是放置会话事实的好地方，但对跨通话记忆毫无用处。

End-to-end speech models collapse the STT-LLM-TTS pipeline into a single stateful session and solve the latency of pipeline problem outright, but they don’t solve the memory problem. OpenAI’s Realtime API caps at a 32k token session, Google’s Gemini Live discards session state at the end of every call, and neither has any built-in concept of cross-session persistence beyond what you wire up around them. Whatever architecture you would have built around a cascade pipeline, you still have to build around an end-to-end one. One genuine upside is that multimodal models can process audio directly, so fact extraction can operate on raw audio rather than a text approximation, which matters for any domain where paralinguistic signal (hesitation, tone, affect) actually shapes the response.

端到端语音模型将 STT-LLM-TTS 管道折叠成一个单一的带状态会话，彻底解决了管道的延迟问题，但它们并未解决记忆问题。OpenAI 的 Realtime API 单次会话 token 上限为 32k，Google 的 Gemini Live 在每次通话结束时丢弃会话状态，除了你在它们外围配置的系统，两者都没有任何内置的跨会话持久化概念。无论你围绕级联管道构建什么样的架构，你仍然需要围绕端到端管道构建同样的架构。一个真正的优势是多模态模型可以直接处理音频，因此事实提取可以对原始音频（而不是近似的文本）进行操作，这对于副语言信号（犹豫、语气、情感）真正影响响应的任何领域都至关重要。

Family 2: Bolted-on memory services

**第二类：外挂记忆服务**

This is where most teams I have talked to start: drop a third-party memory service into the pipeline as a processor between the user aggregator and the LLM, configure a user/entity ID, and let it handle the read/write loop. [Mem0](https://docs.mem0.ai/integrations/pipecat), [Zep](https://blog.getzep.com/zep-livekit/), [Hindsight](https://hindsight.vectorize.io/blog/2026/04/28/pipecat-voice-ai-persistent-memory), and [Supermemory](https://github.com/supermemoryai/pipecat-memory) all ship plugins for the major voice frameworks. The shared shape across all of them is pipeline level integration, user/entity scoping, async writes, and either pre-loaded or on-demand retrieval. The differences are mostly storage substrate (vector vs graph vs SQL), how aggressive the extraction is, and per-call ergonomics.

这是我交流过的大多数团队的起点：将第三方记忆服务作为处理节点接入管道，置于用户聚合器和 LLM 之间，配置用户/实体 ID，让它处理读写循环。[Mem0](https://docs.mem0.ai/integrations/pipecat)、[Zep](https://blog.getzep.com/zep-livekit/)、[Hindsight](https://hindsight.vectorize.io/blog/2026/04/28/pipecat-voice-ai-persistent-memory) 和 [Supermemory](https://github.com/supermemoryai/pipecat-memory) 都为主要的语音框架提供了插件。所有这些工具的共同点是：管道级的集成、用户/实体作用域控制、异步写入，以及预加载或按需检索。它们的差异主要在于存储底层（向量、图或 SQL）、提取的激进程度，以及单次调用的集成易用性。

Family 3: Knowledge-graph memory

**第三类：知识图谱记忆**

This is the family I find most interesting because it actually changes what “memory” means, not just how fast you can fetch it. Instead of embedded text chunks retrieved by similarity, knowledge-graph systems store entities, relationships, and temporal validity, and retrieve by graph traversal augmented with semantic search. The model gets “John’s favorite song is ‘Viva La Vida’ by Coldplay (valid: 2024-01-15 to present)” instead of three loose chunks of past dialog. The production option I have seen show up most often is [Zep’s Graphiti](https://blog.getzep.com/zep-livekit/); the most interesting academic entry is [A-MEM (NeurIPS 2025)](http://arxiv.org/abs/2502.12110v7), which writes each memory as a Zettelkasten-style note that other memories can update over time, so the graph is actively reorganized rather than just appended to. The cost is complexity: graphs are harder to debug, harder to evict from, and more expensive to build than a flat vector index, but for any voice agent that will be on the phone with the same user for years, this family is where the long-term answer lives.

这一类架构最让我感兴趣，因为它真正改变了“记忆”的含义，而不仅仅是你获取它的速度。不同于通过相似度检索嵌入的文本块，知识图谱系统存储实体、关系和时间有效性，并通过辅以语义搜索的图遍历来进行检索。模型获得的是“John 最喜欢的歌是 Coldplay 的 'Viva La Vida'（有效期：2024-01-15 至今）”，而不是过去对话中三个松散的片段。我最常看到的生产环境选项是 [Zep 的 Graphiti](https://blog.getzep.com/zep-livekit/)；最有趣的学术界成果是 [A-MEM (NeurIPS 2025)](http://arxiv.org/abs/2502.12110v7)，它将每一个记忆写成像卢曼卡片盒（Zettelkasten）式的笔记，其他记忆可以随着时间推移对其进行更新，因此图谱是被主动重组的，而不仅仅是被追加的。代价是复杂性：图谱比扁平的向量索引更难调试、更难做记忆淘汰（evict），构建成本也更高，但对于任何需要与同一用户保持多年通话的语音智能体来说，这一类架构正是长期解决方案所在。

Family 4: Cognitive architectures

**第四类：认知架构**

The fourth family treats memory as a cognitive process and not as a database. The foundational reference is [Park et al.’s Generative Agents (UIST 2023)](https://arxiv.org/abs/2304.03442) a memory stream, a reflection step that periodically synthesizes higher-level insights, and a retrieval policy scoring candidates on recency, importance, and relevance. Reflection is the part everyone copies, because it’s what makes the agent feel like it understands you over time rather than parroting what you said. Variants add other tricks: [MemoryBank](https://arxiv.org/pdf/2305.10250) introduces an Ebbinghaus-style forgetting curve so old unused memories quietly drop out; [MemR3 (2025)](https://arxiv.org/abs/2512.20237) flips retrieval into a router that decides between retrieve, reflect, and answer on each turn. These rarely ship as turnkey products. They are patterns to steal, reflection schedules, importance weighted retrieval, time-decayed scoring, and graft onto a Family 1 + Family 2 base.

第四类架构将记忆视为一个认知过程，而不是一个数据库。基础参考是 [Park 等人的 Generative Agents (UIST 2023)](https://arxiv.org/abs/2304.03442)：一个记忆流，一个定期合成高层次洞察的反思步骤，以及一个根据近期性、重要性和相关性对候选记忆进行打分的检索策略。大家都喜欢照搬“反思”这部分，因为正是它让智能体感觉在随着时间推移逐渐理解你，而不是像鹦鹉学舌一样重复你说过的话。它的各种变体加入了一些其他技巧：[MemoryBank](https://arxiv.org/pdf/2305.10250) 引入了艾宾浩斯风格的遗忘曲线，使得旧的未使用记忆悄然退出；[MemR3 (2025)](https://arxiv.org/abs/2512.20237) 将检索转变为一个路由器，决定在每一轮是检索、反思还是回答。这些很少作为现成的产品提供，它们是你应该借鉴的模式（反思计划、重要性加权检索、时间衰减评分），并将它们嫁接到第一类 + 第二类的基础架构上。

## Inverting the Read/Write Path

反转读写路径

The pattern that actually works in production, regardless of which family you pick from above, is to split memory operations into two categories: things that happen before the response (retrieval) and things that happen after the response (writing). Keep only the absolutely essential retrieval in the critical path, and make even that as fast as possible through pre-loading.

在生产环境中真正奏效的模式，无论你选择上述哪一类，都是将记忆操作分为两类：在响应前发生的事情（检索）和在响应后发生的事情（写入）。只将绝对必要的检索保留在关键路径中，并通过预加载让这部分尽可能快。

Pre-load at conversation start. When a call begins, before the user says a word, you have a few hundred milliseconds of setup time, WebRTC connection, audio initialization, codec negotiation. Use that window to fetch the user’s profile, their last-call summary, and any open issues into a session-local cache. When the first turn arrives, your “memory retrieval” is a dictionary lookup, not a network call. Every millisecond you spend fetching profile data on turn one is a millisecond the user spends listening to silence.

**在对话开始时预加载。** 通话开始时，在用户开口前的几百毫秒里，你有建立 WebRTC 连接、初始化音频、协商编解码器的设置时间。利用这段窗口，将用户的画像、上次通话摘要以及任何未决问题拉取到会话本地缓存中。当第一轮对话到来时，你的“记忆检索”只是一个字典查找，而不是网络调用。你在第一轮为获取画像数据花费的每一毫秒，都是用户聆听死寂的每一毫秒。

The cold-start case is where this gets real. If the caller is anonymous, you can’t pre-load anything user-specific. You either authenticate them in the first turn or two (account number, CRM phone-number lookup during setup) or accept thinner context on the first call and design the prompt to be graceful about it. The mistake I see most often is teams treating authenticated as “the system” and anonymous as an edge case. In telephony, anonymous is a hot path.

冷启动情况才是真正考验架构的地方。如果来电者是匿名的，你无法预加载任何用户特定的信息。你要么在前一两个回合内对其进行身份验证（在设置期间通过账号或 CRM 电话号码查找），要么接受第一次通话上下文信息匮乏的现实，并设计得体的提示词来从容应对。我看到团队最常犯的错误是将已认证用户当作系统默认路径来设计，而把匿名用户当作边缘情况。在电话系统中，匿名是一条高频热点路径（hot path）。

The other half of the inversion is async writes. After each response, kick off a fire-and-forget background task that extracts new facts from the latest turn and persists them. By the time the call ends, the profile is largely up to date and none of that work has spent any of your inner-loop latency budget. To handle short calls that hang up before extraction finishes, block the call-end handler on a small timeout (2-3 seconds is usually fine) so in-flight tasks drain. The user has already gone, so there is no latency budget to defend. Then run a full summarization pass over the entire transcript and store it as the canonical record like what the call was about, whether it was resolved, key facts, follow-ups. That summary becomes the last_interaction you pre-load on the next call, and it is the single most underrated artifact in a voice memory system. Both [ChatGPT](https://manthanguptaa.in/posts/chatgpt_memory) and [Claude](https://manthanguptaa.in/posts/claude_memory) lean on the same idea in their text systems: a curated summary beats a raw transcript at retrieval time, every single time.

反转的另一半是**异步写入**。在每次响应之后，启动一个“触发即忘”（fire-and-forget）的后台任务，从最新的一轮对话中提取新事实并持久化保存。到通话结束时，用户画像已基本更新，且这些工作没有消耗任何内循环的延迟预算。为了处理提取完成前就挂断的短通话，可以在通话结束处理程序中设置一个小小的超时阻塞（2-3 秒通常足够），让运行中的任务排空。反正此时用户已经挂断了，不需要再去捍卫延迟预算。然后，对整个转录文本运行一次完整的总结过程，并将其存储为规范记录：例如电话的主题、问题是否解决、关键事实、后续跟进等。该摘要将成为你下次通话时预加载的 `last_interaction`（上次交互），它是语音记忆系统中最被低估的数据产物。在文本系统中，[ChatGPT](https://manthanguptaa.in/posts/chatgpt_memory) 和 [Claude](https://manthanguptaa.in/posts/claude_memory) 也依赖于同样的思想：在检索时，精心策划的摘要每次都完胜原始转录记录。

Two things bite you once you actually ship this. First, the pre-load can race the previous call’s writebacks. Imagine a caller asks to be called Alex on one call: the per-turn extraction captures “please call me Alex” and persists it. If the next call’s pre-load reads from a snapshot taken a few seconds before that writeback finished draining, the agent greets them by their old name which erodes trust faster than no memory at all. The fix is the obvious one (always serve the freshest writeback even if your snapshot is older), but the failure mode only shows up once you have real users. Second, per-turn extraction means an extra LLM call on every single turn. At a few cents per call multiplied by 40-60 turns, a 10-minute conversation can land at a couple of dollars in extraction alone which is fine for a high-value support call, ruinous for a free consumer assistant at scale. The honest move is to pick a cheaper model for extraction (a distilled 7-8B is usually plenty), run extraction on a longer rolling window, or bias toward post-call extraction for low-margin use cases.

一旦你真正在生产环境中部署，会有两件事让你吃苦头。第一，预加载可能与上一次通话的回写操作发生竞争。想象一下，来电者在一次通话中要求叫他 Alex：按轮次提取捕获到了“请叫我 Alex”并将其持久化。如果下一次通话的预加载读取的快照发生在此次回写完成前几秒钟，智能体就会用旧名字来称呼他，这比完全没有记忆还更伤信任。修复方法显而易见（始终提供最新的回写记录，即使快照较旧），但这种故障模式只有在你拥有真实用户时才会出现。第二，按轮次提取意味着每一轮都要额外调用一次 LLM。每次通话几美分，乘以 40-60 个轮次，一个 10 分钟的对话仅提取成本就可能高达几美元——对于高价值的客服电话来说可以接受，但对于规模化的免费消费者助手来说则是毁灭性的。务实的做法是：选择更便宜的模型进行提取（经过蒸馏的 7-8B 模型通常足够了），在较长的滚动窗口上运行提取，或者对于低利润用例倾向于在通话后提取。

## Compressing Conversation History Within a Call

在单次通话中压缩对话历史

Even within a single call you will hit the practical context limit faster than you expect. A 10-minute call at normal pace lands at 1500-2000 tokens of transcript alone, and on a speech-native session the 10× audio token inflation pushes you well past where any large context advertisement actually holds up.

即使在一次通话中，你也会比想象中更快触及实际的上下文限制。一个正常语速的 10 分钟通话单靠转录就会产生 1500-2000 个 token，而在原生语音会话中，10 倍的音频 token 膨胀会让你远超厂商对大上下文能力宣传中真正能撑住的范围。

The mitigation is a rolling window with summary: keep the last N turns in full, replace earlier turns with a compressed summary. When the transcript hits a threshold (say, 20 turns), kick off an async compression pass that replaces the first 10 with 3-4 sentences. Use a fast small model for this, a distilled 1-3B on a colocated GPU, or a fine-tuned summarizer on CPU. 50-150ms per compression is fine async but would be painful in the critical path.

缓解措施是带有摘要的滚动窗口：完整保留最近的 N 个轮次，用压缩摘要替换较早的轮次。当转录文本达到某个阈值（比如 20 个轮次），就启动一轮异步压缩处理，将前 10 轮替换为 3-4 句话。使用快速的小模型来做这件事，例如在同机部署的 GPU 上使用经过蒸馏的 1-3B 模型，或者在 CPU 上使用微调的摘要模型。每次压缩耗时 50-150 毫秒，只要是异步的就没问题，但如果放在关键路径中就会非常痛苦。

Selective retention is the other lever. Not all turns are equally valuable “okay”, “got it”, “mm-hmm” contribute close to nothing. Even a length and stopword heuristic, much less a tiny classifier, can drop low-signal turns without losing content. Treat the transcript as something to curate, not a log to preserve.

选择性保留是另一个杠杆。并非所有轮次都有同等价值——“好的”、“明白了”、“嗯嗯”等几乎不提供任何信息。甚至仅用长度与停用词启发式（更不用说小型分类器）即可在不丢失内容的情况下丢弃低信号的轮次。请将转录文本视为需要筛选提炼的素材，而不是需要全盘保留的日志。

## Long-Term Episodic Retrieval

长期情景检索

For structured profile data like name, preferences, known issues, a key-value store is the right answer. Fast, predictable, no embedding required. This is the boring part of memory and it should stay boring.

对于姓名、偏好、已知问题等结构化的画像数据，键值对存储是正确的答案。快速、可预测、无需向量嵌入。这是记忆中枯燥的部分，也应该保持枯燥。

For unstructured episodic memory that is specific past conversations, detailed historical interactions, you eventually need semantic retrieval. The question is when to do it, and the answer is: not during a turn.

对于非结构化的情景记忆，即过去具体的对话、详细的历史交互记录，你最终需要语义检索。问题在于什么时候做，答案是：不要在对话回合进行时做。

The pattern that works is background relevance preparation. You maintain a representation of the current conversation topic. In practice this is usually the last one or two user turns embedded as a single query vector, sometimes augmented with a small classifier-derived topic label. Periodically, every 3-5 turns, or whenever the topic vector shifts beyond a threshold, you fire an async retrieval query against past conversations. If the retrieval finds something relevant, the result gets staged for injection on the next turn, not the current one.

行之有效的模式是后台相关性准备。你维护当前对话话题的某种表征。在实践中，这通常是把用户最后的一两次发言嵌入为单个查询向量，有时会附加由小型分类器派生的话题标签。周期性地，例如每 3-5 轮，或者当话题向量偏移超过某个阈值时，你向过去的对话发起一次异步检索查询。如果检索发现了相关内容，结果会被暂存起来，在*下一轮*（而不是当前轮次）注入。

That introduces a one-turn lag on episodic context, and that tradeoff is almost always the right one. Users won’t notice that the agent referenced a past conversation a beat after the topic came up. They will absolutely notice if every turn has a 200ms hesitation.

这会在情景上下文中引入一轮的滞后，而这种权衡几乎总是正确的。用户不会注意到智能体在话题被提出后稍微晚了一拍才引用过去的对话。但如果每一轮都有 200 毫秒的停顿，他们绝对会注意到。

The honest counterpoint is rapid topic shift. If a user pivots topics every turn which happens more in casual support calls than you would expect your staged retrieval is constantly stale. The pragmatic fix is to detect the shift cheaply (cosine similarity drop between consecutive query vectors) and fall back to a “no episodic context” path rather than injecting yesterday’s topic into today’s question. Stale context is worse than absent context.

坦率地说，还有一个需要正视的反面：快速的话题转换。如果用户每一轮都在切换话题——这在日常客服电话中比你想象的要多——你暂存的检索结果就会不断过期。务实的修复方法是低成本地检测话题转换（连续查询向量之间的余弦相似度下降），并回退到“无情景上下文”的路径，而不是把昨天的话题硬塞进今天的问题里。过期的上下文比没有上下文更糟。

## Sleep-Time Memory Consolidation

闲时记忆巩固

Per-turn writes plus end-of-call summarization handle the basics. The next-level move is doing memory work between sessions, while the system is idle. The clearest articulation of this is Letta’s [sleep-time compute](https://letta.com/blog/sleep-time-compute), which spawns a separate agent that shares memory blocks with the user-facing agent and runs in the background, reorganizing and consolidating what’s there. The [paper that motivated it](https://arxiv.org/abs/2504.13171v1) reports a ~5× test-time compute reduction at equal accuracy and 13-18% accuracy lifts when queries are predictable. Those are the paper’s headline numbers on their chosen benchmarks; for voice, the more useful framing is that even modest consolidation work between calls pays back in retrieval quality on the next one.

按轮次的写入加上通话后的摘要处理了基础问题。更进阶的操作是在会话之间、系统空闲时进行记忆处理工作。对此最清晰的阐述是 Letta 的[闲时计算 (sleep-time compute)](https://letta.com/blog/sleep-time-compute)，它会生成一个独立的智能体，与面向用户的智能体共享记忆块并在后台运行，重新组织和巩固已有的信息。[促成这一做法的论文](https://arxiv.org/abs/2504.13171v1)报告称，在同等准确率下测试时的计算量减少了约 5 倍，且当查询可预测时，准确率提升了 13-18%。这是该论文在自选基准上报道的核心数字；对于语音领域，更具实用价值的观点是：即使在通话之间进行少量的巩固工作，也能在下一次通话的检索质量上得到回报。

The intuition for voice is straightforward. Per-turn writes give you a flat, time-ordered stream of facts. Over weeks and months, that stream accumulates contradictions (“user prefers email”… “user said please call them”) and stale context. A nightly sleep-time consolidation pass can merge duplicates, resolve contradictions in favor of the more recent signal, prune low-importance memories with a [forgetting-curve schedule](https://arxiv.org/pdf/2305.10250), and synthesize higher-level reflections in the spirit of Park’s Generative Agents — “this user tends to call when something is broken, not for general questions.”

就语音场景而言，道理很直白。按轮次的写入为你提供了一个扁平的、按时间排序的事实流。数周乃至数月积累下来，这个流就会产生矛盾（“用户更喜欢发邮件”……“用户说请给他们打电话”）和过期的上下文。夜间的闲时巩固过程可以合并重复项，以较新的信号为准解决矛盾，使用[遗忘曲线调度](https://arxiv.org/pdf/2305.10250)修剪低重要性的记忆，并本着 Park 的 Generative Agents 的精神合成更高层次的反思——“该用户倾向于在东西坏了的时候打电话，而不是为了询问一般性问题。”

The reason this matters specifically for voice is that you cannot afford to do any of this consolidation work in the critical path. Sleep-time is the only place in the architecture where you have unlimited latency budget. Anything you don’t do here, you’ll regret doing inline.

这之所以对语音特别重要，是因为你无法承受在关键路径中做任何此类巩固工作。闲时是架构中唯一拥有无限延迟预算的地方。任何你在这里没做的事，将来若改在内联路径上做，都会让你追悔莫及。

## Clean Signal: Transcripts and Multiple Speakers

干净的信号：转录文本与多说话人

All of this assumes the input to your memory pipeline is reasonably clean. In practice it isn’t, and there are two distinct problems hiding in there: noisy transcripts of the caller’s own speech, and the fact that there’s often more than one person in the room.

所有这一切都假设进入记忆管道的输入是相对干净的。但在实践中并非如此，里面隐藏着两个截然不同的问题：来电者自身讲话产生的质量较差的转录文本，以及房间里往往不止一个人这一事实。

On the first: voice transcripts are messy. Users say “um” and “uh”, they restart sentences, they use pronouns without antecedents (“tell me about that thing we talked about”). Raw transcripts make for noisy fact extraction. The mitigation is a lightweight transcript cleaning step, a fast pass that removes disfluencies and normalizes references before passing the text into any memory pipeline. This runs asynchronously and never touches the response cycle. The LLM itself sees the raw transcript (because cleaning it adds latency you cannot afford), but memory extraction works off the cleaned version.

首先：语音转录文本非常混乱。用户会说“嗯”和“呃”，他们会重新开始句子，会使用没有前情指代的代词（“告诉我关于我们讨论过的那件事”）。原始转录文本会使事实提取充满噪声、很不准确。缓解方法是加入一个轻量级的转录文本清理步骤——快速扫过以去除语塞并规范化指代，然后再将文本传入任何记忆管道。这一步异步运行，不进入响应链路。LLM 本身看的是原始转录文本（因为清理它会增加你无法承受的延迟），但记忆提取使用的是清理后的版本。

The second problem is the one almost no production voice agent solves cleanly. Family customer service calls have a spouse and a kid in the same room. Healthcare calls have a caretaker. Inbound support from a small business has someone shouting context from across the office. Speaker diarization, figuring out who said what is what makes memory accurate here. Without it, your fact extractor cheerfully writes “caller’s spouse hates the current plan” into the caller’s profile, which destroys trust on the next call.

第二个问题是几乎没有生产级语音智能体能干净解决的。家庭客服电话会有配偶和孩子在同一个房间。医疗保健电话有看护人在场。小型企业的呼入客服电话会有人在办公室另一端大声补充背景信息。说话人分离（Speaker diarization，即弄清楚谁说了什么）是使记忆在这里保持准确的关键。如果没有它，你的事实提取器会兴高采烈地将“来电者的配偶讨厌当前的套餐”写入来电者的个人资料中，从而在下一次通话时彻底毁掉信任。

[pyannote-audio](https://github.com/pyannote/pyannote-audio) is the dominant open-source option; newer LLM-grounded systems like [TagSpeech](https://arxiv.org/abs/2601.06896) and [DM-ASR](https://arxiv.org/abs/2604.22467) show meaningful gains on overlap-heavy audio. Though the latency cost is real with 200-400ms of additional latency per turn on the critical path which is why most production voice agents I have seen don’t ship live diarization aware memory. The workable compromise is to run diarization async on the post-call recording, attribute facts to the right speaker before persisting, and accept some attribution noise within the call itself. It’s the kind of thing that goes wrong rarely enough to be acceptable and wrong badly enough that you should at least have a story for it.

[pyannote-audio](https://github.com/pyannote/pyannote-audio) 是主导的开源选择；较新的以 LLM 为核心的系统，如 [TagSpeech](https://arxiv.org/abs/2601.06896) 和 [DM-ASR](https://arxiv.org/abs/2604.22467) 在大量重叠声音频上显示出显著提升。然而延迟成本是真真切切的：关键路径上每一轮额外需要 200-400 毫秒的延迟，这就是为什么我见过的绝大多数生产级语音智能体，并没有上线具备实时说话人分离能力的记忆系统。可行的折中方案是对通话后的录音异步运行说话人分离，在持久化保存前将事实归因给正确的说话人，并接受在通话过程中存在的少量归因不确定性。这类问题发生频率足够低，尚可接受，但一旦发生后果很严重，因此你至少应该对此有一套预案与说法。

## The Three-Tier Stack

三层技术栈

Putting it together, a production voice memory system has three tiers, defined by latency profile rather than what they store.

总而言之，一个生产级语音记忆系统分为三层，层级由延迟特性决定，而不是由存储内容决定。

Tier 1 - hot cache (1-5ms): pre-loaded at call start. User profile, last-call summary, open issues. Lives in process memory for the call’s duration. Serves every turn lookup essentially instantly.

**第一层 - 热缓存 (1-5毫秒)：** 在通话开始时预加载。包含用户画像、上次通话摘要、未决问题。在通话期间存在于进程内存中。为每轮查询提供近乎即时的服务。

Tier 2 - background retrieval (50-150ms, async): episodic search between turns, results staged for injection on the next turn. Never blocks.

**第二层 - 后台检索 (50-150毫秒，异步)：** 在对话回合之间进行的情景搜索，结果暂存准备在下一轮注入。绝不阻塞。

Tier 3 - async writes (latency irrelevant): fact extraction, profile updates, end-of-call summarization, sleep-time consolidation. Happens after each turn, after the call ends, and during system idle. Feeds Tier 1 for the next call.

**第三层 - 异步写入 (延迟无关紧要)：** 事实提取、画像更新、通话后总结、闲时巩固。发生在每轮之后、通话结束后以及系统空闲期间。为下一次通话的第一层提供数据。

![](https://shiina18.github.io/assets/posts/images/249933511271996.png)

Notice the asymmetry: the only thing on the blocking path is the cache lookup. Everything expensive embedding, retrieval, summarization, writeback, consolidation has been pushed to the cracks between turns, to after the call has ended, or to system idle.

请注意这种不对称性：在阻塞路径上的唯一操作就是缓存查找。所有昂贵的操作——嵌入、检索、总结、回写、巩固——都被推迟到了轮次之间的缝隙中，推迟到了通话结束后，或者推迟到了系统空闲时。

## Closing Thoughts

结语

Voice agent memory is still largely unsolved in the sense that genuinely human-like recall across many conversations remains elusive. The infrastructure has fast caches, async extraction, structured profiles, end-of-call summaries, knowledge graphs, sleep-time consolidation and is well-understood and implementable today, with mature frameworks (Pipecat, LiveKit Agents) and a healthy ecosystem of memory services (Mem0, Zep, Letta, Hindsight, Supermemory, Cognee) you can drop in without writing the read/write loop from scratch. The craft lives in the semantic part: deciding what to remember, when to surface it, and how to do it without sounding like the agent is reading from a file. That part rewards careful prompt design and aggressive curation of what gets persisted, not bigger vector databases.

语音智能体的记忆问题在很大程度上仍未完全解决，因为在众多对话中实现真正类人的回想依然难以企及。如今基础设施层面的快速缓存、异步提取、结构化画像、通话后总结、知识图谱、闲时巩固已经被充分理解并可付诸实施，而且拥有成熟的框架（Pipecat、LiveKit Agents）和健康的记忆服务生态系统（Mem0、Zep、Letta、Hindsight、Supermemory、Cognee），你可以直接引入而无需从头编写读写循环代码。技艺体现在语义层面：决定要记住什么、何时呈现，以及如何在呈现时听起来不像智能体在照本宣科。这一部分值得在提示词设计上花心思，并对持久化内容做严格筛选，而不是简单地堆砌更大的向量数据库。

If there’s a single line to take away: in a voice agent, the speed of memory is set by what you have already prepared, not by what you can fetch in the moment.

如果只能带走一句话，那就是：在语音智能体中，记忆的速度取决于你已经准备好了什么，而不是你当下能抓取什么。

Next in this series I will cover evaluating voice agents, the part that standard LLM evals (and even LongMemEval and LoCoMo) miss completely, and where most of the hard won lessons from production actually live.

在本系列的下一篇文章中，我将介绍如何评估语音智能体，这是标准的 LLM 评估（甚至包括 LongMemEval 和 LoCoMo）完全忽略的部分，而绝大多数来自生产环境、来之不易的经验都蕴含其中。

If you found this interesting, I’d love to hear your thoughts. Share it on [Twitter](https://twitter.com/manthanguptaa), [LinkedIn](https://www.linkedin.com/in/manthanguptaa/), or reach out at guptaamanthan01\[at\]gmail\[dot\]com.

如果你觉得这很有趣，我很想听听你的想法。欢迎在 [Twitter](https://twitter.com/manthanguptaa)、[LinkedIn](https://www.linkedin.com/in/manthanguptaa/) 上分享它，或者通过 guptaamanthan01\[at\]gmail\[dot\]com 与我联系。

## References

参考文献

*   Liu, Nelson F., et al. [“Lost in the Middle: How Language Models Use Long Contexts.”](https://arxiv.org/abs/2307.03172) arXiv:2307.03172, 2023.
*   Liu, Nelson F., 等. [《迷失在中间：语言模型如何使用长上下文》](https://arxiv.org/abs/2307.03172) arXiv:2307.03172, 2023.

*   Park, Joon Sung, et al. [“Generative Agents: Interactive Simulacra of Human Behavior.”](https://arxiv.org/abs/2304.03442) UIST 2023.
*   Park, Joon Sung, 等. [《生成式智能体：人类行为的交互式拟像》](https://arxiv.org/abs/2304.03442) UIST 2023.

*   Zhong, Wanjun, et al. [“MemoryBank: Enhancing Large Language Models with Long-Term Memory.”](https://arxiv.org/pdf/2305.10250) arXiv:2305.10250, 2023.
*   Zhong, Wanjun, 等. [《MemoryBank：为大型语言模型增强长期记忆》](https://arxiv.org/pdf/2305.10250) arXiv:2305.10250, 2023.

*   Chhikara, Prateek, et al. [“Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory.”](https://arxiv.org/pdf/2504.19413) arXiv:2504.19413, 2025.
*   Chhikara, Prateek, 等. [《Mem0：构建具备可扩展长期记忆的生产级 AI 智能体》](https://arxiv.org/pdf/2504.19413) arXiv:2504.19413, 2025.

*   Xu, Wujiang, et al. [“A-MEM: Agentic Memory for LLM Agents.”](http://arxiv.org/abs/2502.12110v7) NeurIPS 2025.
*   Xu, Wujiang, 等. [《A-MEM：面向 LLM 智能体的智能体记忆》](http://arxiv.org/abs/2502.12110v7) NeurIPS 2025.

*   Du, Xingbo, et al. [“MemR3: Memory Retrieval via Reflective Reasoning for LLM Agents.”](https://arxiv.org/abs/2512.20237) arXiv:2512.20237, 2025.
*   Du, Xingbo, 等. [《MemR3：通过反思推理实现 LLM 智能体的记忆检索》](https://arxiv.org/abs/2512.20237) arXiv:2512.20237, 2025.

*   [“Sleep-time Compute: Beyond Inference Scaling at Test-time.”](https://arxiv.org/abs/2504.13171v1) arXiv:2504.13171, 2025.
*   [《闲时计算：超越测试时推理缩放》](https://arxiv.org/abs/2504.13171v1) arXiv:2504.13171, 2025.

*   Luo, Jinghao, et al. [“From Storage to Experience: A Survey on the Evolution of LLM Agent Memory Mechanisms.”](https://arxiv.org/abs/2605.06716) arXiv:2605.06716, 2026.
*   Luo, Jinghao, 等. [《从存储到体验：LLM 智能体记忆机制演进综述》](https://arxiv.org/abs/2605.06716) arXiv:2605.06716, 2026.