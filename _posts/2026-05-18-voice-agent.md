---
title: "【机翻】语音智能体基础 101：能够与人对答的 AI 背后的架构"
categories: 
- LLM
tags: Agent
updated: 
comments: true
mathjax: false
---

- [Voice Agents 101: The Architecture Behind AI That Talks Back](https://manthanguptaa.in/posts/voice_agents_primer/)

<!-- more --> 

# Voice Agents 101: The Architecture Behind AI That Talks Back

语音智能体基础 101：能够与人对答的 AI 背后的架构

May 5, 2026 · Manthan Gupta

The first time I built a voice agent and got on a call with it, the thing felt like talking to someone over a satellite phone in 2003. Long pauses, unnatural cadence, occasional cuts where it would just keep talking over me. The text version of the same product was usable. The voice version was not. That was the moment I learned that text engineering and voice engineering are not the same craft.

第一次构建语音智能体并与它通话时，感觉就像是在2003年用卫星电话与人交谈。漫长的停顿、不自然的语流，偶尔还会卡顿，有时还会一直抢着跟我说话。同一个产品的文本版本是可用的，但语音版本却完全不行。就在那一刻，我意识到：文本工程和语音工程根本不是同一门手艺。

The moment you introduce audio, you are dealing with a fundamentally different latency profile, a different failure mode surface, and a different set of tradeoffs than anything you would encounter in a text-based system. Voice agents aren’t just LLMs with a speaker attached. They are pipelines, and every stage of that pipeline fights against the same constraint: time.

引入音频的那一刻，你所面对的延迟剖面、故障暴露面以及需要权衡的因素，都与基于文本的系统中遇到的情况截然不同。语音智能体绝不仅仅是外接了一个扬声器的大语言模型（LLM）。它们是流水线（pipelines），而这条流水线的每一个阶段都在与同一个限制条件作斗争：时间。

This post covers how the voice agent pipeline actually works, the architectural choice between cascade and end-to-end speech models, the latency budget you are working within, what full-duplex means and why it is hard, and the design decisions that determine whether your voice agent feels natural or robotic.

本文将探讨语音智能体流水线在实际中是如何运作的，级联模型与端到端语音模型之间的架构选择，你需要遵守的延迟预算，全双工是什么以及为什么难，以及那些决定你的语音智能体感觉自然还是机械的设计决策。

## The Three-Stage Pipeline

三阶段流水线

At its core, the most common voice agent architecture is built on three sequential stages.

从核心来看，最常见的语音智能体架构是建立在三个连续的阶段之上的。

**Speech-to-Text (STT)** takes the raw audio from the microphone and converts it into text that the LLM can process. The dominant options here are OpenAI Whisper (open-source, extremely accurate, but has latency), Deepgram (low-latency streaming transcription, production-proven), AssemblyAI (good accuracy, streaming support), and a handful of others. The key metric is not just word error rate but *time to transcript* — how long it takes to produce a transcript. A 98% accurate transcription that takes 800ms to produce is often worse than a 95% accurate one that takes 150ms.

**语音转文本 (STT)** 接收来自麦克风的原始音频，并将其转换为 LLM 可以处理的文本。在此环节，主流选项包括 OpenAI Whisper（开源，极其准确，但存在延迟）、Deepgram（低延迟流式转录，经过生产环境验证）、AssemblyAI（准确度高，支持流式传输）等少数几个。这里的关键指标不仅是词错误率（word error rate），还有*生成转录耗时（time to transcript）*——即生成转录结果需要多长时间。一个准确率98%但需要800毫秒才能生成结果的转录，往往比一个准确率95%但只需150毫秒的转录更差。

**LLM** is the brain. It takes the transcript, applies context and memory, and generates a response. The same models you would use in text apply here, but the prompt structure changes: voice conversations are shorter-turn, more casual, and the model absolutely cannot produce markdown, numbered lists, or long walls of text. Every response needs to be spoken aloud naturally.

**LLM（大语言模型）** 是大脑。它接收转录文本，运用上下文和记忆，然后生成回复。你在文本中使用的模型同样适用于此，但提示词（prompt）结构需要改变：语音对话的单轮话轮更短、更随意，并且模型绝对不能生成 Markdown、编号列表或大段的长篇大论。每一个回复都需要能够被自然地大声朗读出来。

**Text-to-Speech (TTS)** converts the LLM’s text response to audio. The options range from older, robotic systems to modern neural TTS that sounds remarkably human: ElevenLabs, Cartesia (exceptionally low-latency), OpenAI TTS, PlayHT, and others. The metric that matters most in production is *time to first audio chunk* — how long before the user hears anything at all.

**文本转语音 (TTS)** 将 LLM 的文本回复转换为音频。可选方案从老式的、听起来很机械的系统，一直延伸到极其逼真的现代神经 TTS：ElevenLabs、Cartesia（延迟极低）、OpenAI TTS、PlayHT 等。在生产环境中最重要的指标是*首段音频生成耗时（time to first audio chunk）*——即在用户听到任何声音之前需要等待多长时间。

Stitching these three stages together is straightforward but making them feel seamless is not.

将这三个阶段拼接在一起并不复杂，但要让它们感觉无缝衔接却并不容易。

## Cascade vs. End-to-End Speech Models

级联模型 vs. 端到端语音模型

Before we get deeper into the cascade pipeline, you should know that there is now a second architectural family that didn’t really exist 18 months ago: end-to-end speech models.

在我们深入探讨级联流水线之前，你需要知道，现在出现了第二种架构体系，这在18个月前几乎是不存在的：端到端语音模型。

Cascade is what we just described. STT transcribes audio to text, an LLM produces text, TTS turns that text back into audio. You get full control of every stage, complete observability, and the ability to swap components independently. The price you pay is latency (each stage adds time and you can’t always overlap them perfectly), context loss (the LLM never hears tone of voice or hesitation, only the transcribed words), and a flatter emotional surface (the LLM doesn’t know the user is frustrated, and the TTS doesn’t naturally react to the content).

级联（Cascade）就是我们刚才描述的方式。STT 将音频转录为文本，LLM 生成文本，TTS 再将该文本转回音频。你可以完全控制每一个阶段，拥有完整的可观测性，并且能够独立替换各个组件。你为此付出的代价是延迟（每个阶段都会增加时间，而且你无法总是让各阶段完美并行衔接）、上下文丢失（LLM 永远听不到语调或犹豫，只能看到转录的文字），以及更为扁平化的情感表现（LLM 不知道用户很沮丧，TTS 也不会自然地根据内容做出反应）。

End-to-end speech models bypass the transcription step entirely. The model takes audio in and produces audio out. OpenAI’s Realtime API (built on GPT-4o), Kyutai’s Moshi, and Sesame’s CSM are the prominent examples. Because there’s no STT step and no separate TTS step, latency drops dramatically. Moshi reports response latency in the 200-300ms range which is closer to human conversation than any cascade system can reach. Prosody and emotion are also better because the model directly hears and produces audio without flattening it through text.

端到端语音模型完全绕过了转录步骤。模型直接输入音频并输出音频。OpenAI 的 Realtime API（基于 GPT-4o）、Kyutai 的 Moshi 以及 Sesame 的 CSM 都是典型范例。因为没有 STT 步骤，也没有独立的 TTS 步骤，延迟大幅下降。Moshi 报告其响应延迟在200-300毫秒范围内，这比任何级联系统所能达到的水平都更接近人类对话。由于模型直接倾听和生成音频，而不是通过文本进行扁平化处理，因此韵律和情感表现也更佳。

The tradeoff is that you give up most of the things that make cascade systems engineerable. You can’t easily inspect what the model “heard.” You can’t swap a better STT in next quarter. Tool calling and structured output are weaker because they have to be encoded into the audio modality rather than handled as text. And the cost per minute of conversation is currently much higher than running a small fast LLM in a cascade.

其权衡之处在于，你放弃了让级联系统可工程化的大部分特性。你很难检查模型“听到”了什么；你无法在下个季度轻松替换一个更好的 STT；工具调用和结构化输出能力较弱，因为它们必须编码到音频模态中，而不是作为文本处理。而且，目前每分钟对话的成本远高于在级联系统中运行一个快速的小型 LLM。

For most production voice agents in 2026 customer service, telephony, voice front-ends to existing systems cascade is still the right architecture. The control surface, observability, and maturity of the component ecosystem outweigh the latency advantage of end-to-end models. But for use cases where natural conversation matters more than precise tool use (companions, language tutors, hands-free assistants), end-to-end is becoming genuinely competitive. It’s worth knowing both architectures exist before you commit to one.

对于2026年大多数生产环境中的语音智能体——客户服务、电话系统、现有系统的语音前端——级联仍然是正确的架构。控制面、可观测性以及组件生态系统的成熟度，这些优势盖过了端到端模型的延迟优势。但对于那些自然对话比精确使用工具更重要的用例（如虚拟伴侣、语言导师、免提助手），端到端正在变得真正具有竞争力。在决定使用哪一种架构之前，了解这两种架构的存在是很有必要的。

The rest of this post focuses on cascade because that’s where the engineering surface is most interesting.

本文的其余部分将主要关注级联架构，因为这里的工程层面最有意思。

## The Latency Budget

延迟预算

For a voice conversation to feel natural, the total round-trip from the user finishing a sentence to hearing the first word of a response needs to be under roughly 500-800ms. Beyond that, users start perceiving a delay. Beyond 1.5 seconds, it feels broken. So, you are usually fighting against the clock to get your voice agent to feel natural.

要让语音对话感觉自然，从用户说完一句话到听到回复的第一个词，总的往返时间大约需要控制在500到800毫秒以内。超过这个时间，用户就会开始感知到延迟。超过1.5秒，对话就会感觉明显不自然。因此，你通常是在与时间赛跑，以努力让你的语音智能体感觉自然。

Let’s break down where the time goes in a naive sequential implementation of a voice agent:

让我们来分解一下，在一个朴素串行实现的语音智能体中，时间都花在了哪里：

| Stage | Typical latency |
| --- | --- |
| Audio capture + VAD end-detection | 100–300ms |
| STT transcription | 150–400ms |
| LLM Time to First Token (TTFT) | 300–800ms |
| TTS first audio chunk | 100–300ms |
| Network overhead | 50–150ms |
| **Total** | **700ms–1.95s** |

| 阶段 | 典型延迟 |
| --- | --- |
| 音频捕获 + VAD 结束检测 | 100–300ms |
| STT 转录 | 150–400ms |
| LLM 首个 Token 时间 (TTFT) | 300–800ms |
| TTS 首个音频块 | 100–300ms |
| 网络开销 | 50–150ms |
| **总计** | **700ms–1.95s** |

Even at the optimistic end, you are already at the edge of acceptable. At the pessimistic end, it feels like talking to someone with a bad phone connection. This is why voice agents are fundamentally a latency engineering problem, not just an AI problem. The best voice experiences are built by teams that treat milliseconds as a first-class engineering concern.

即使是在最乐观的情况下，你也已经处于可接受范围的边缘。而在悲观的情况下，感觉就像是与电话信号极差的人在交谈。这就是为什么语音智能体本质上是一个延迟工程问题，而不仅仅是一个 AI 问题。最好的语音体验是由那些将“毫秒”视为首要工程关注点的团队打造出来的。

The solution isn’t to make each stage faster in isolation (though that helps). The real unblock is **streaming** so that the stages can overlap rather than run sequentially.

解决方案并不是孤立地让每个阶段变得更快（尽管这也有帮助）。真正能破局的是**流式传输（streaming）**，这样各个阶段就可以重叠进行，而不是按顺序执行。

## Streaming: The Only Way to Win on Latency

流式传输：在延迟问题上获胜的唯一途径

In a naive pipeline, you wait for the user to finish speaking, wait for the full transcript, send it to the LLM, wait for the full response, then send it all to TTS. That’s fully sequential and the latency compounds.

在朴素流水线中，你需要等待用户讲完，等待完整的转录，将其发送给 LLM，等待完整的回复，然后再将所有内容发送给 TTS。这是完全顺序执行的，延迟会不断叠加。

In a streaming pipeline, you start TTS as soon as the LLM starts generating tokens and you don’t wait for the full response. The LLM streams token by token, and the TTS system consumes those tokens and begins synthesizing audio in real time, typically buffering 5-15 tokens before generating the first chunk of audio to avoid stopping and starting.

在流式流水线中，只要 LLM 开始生成 token，TTS 就会随之启动，你无需等待完整的回复。LLM 逐个 token 地进行流式传输，而 TTS 系统实时消耗这些 token 并开始合成音频，通常在生成第一块音频之前会缓冲 5-15 个 token，以避免播放时走走停停。

![The voice agent pipeline: from end of user turn to first audio chunk of response](https://shiina18.github.io/assets/posts/images/417131710287018.png "The voice agent pipeline: from end of user turn to first audio chunk of response")

语音智能体流水线：从用户回合结束到回复的首段音频

The result is that the user hears the first word of the response while the LLM is still generating the second sentence. This is how production voice systems at companies like ElevenLabs’ Conversational AI, Bland.ai, and Retell AI achieve sub-600ms end-to-end response latency despite using powerful LLMs under the hood.

最终的结果是，当 LLM 还在生成第二句话时，用户就已经听到了回复的第一个词。这正是 ElevenLabs 的 Conversational AI、Bland.ai、Retell AI 等公司的生产级语音系统，在底层仍使用强大 LLM 的情况下，仍能把端到端响应延迟压到 600 毫秒以下的做法。

## Half-Duplex vs Full-Duplex

半双工 vs 全双工

This is one of the most important architectural decisions in voice agent design, and it’s underappreciated.

这是语音智能体设计中最重要架构决策之一，但其重要性往往未被充分认识。

**Half-duplex** is the push-to-talk model: one party speaks, then the other speaks. The system listens while the user talks, then responds, then listens again. Simple to implement. Feels like leaving voicemails back and forth. For simple command-response interfaces (think: “set a timer for 5 minutes”), half-duplex is fine. For natural conversation, it’s frustrating.

**半双工（Half-duplex）** 是按键通话（push-to-talk）模式：一方说话，然后另一方再说话。系统在用户说话时倾听，然后回复，接着再倾听。这种模式实现起来很简单。感觉就像在互相留语音信箱。对于简单的命令-响应界面（比如：“设定一个5分钟的计时器”），半双工就够用。但对于自然对话来说，这种体验非常令人沮丧。

**Full-duplex** is how human conversations actually work: both parties can speak simultaneously, interrupt each other, say “uh-huh” mid-sentence, and react in real time. Building this is substantially harder. It requires the system to be listening and generating audio at the same time which means you need to solve the barge-in problem.

**全双工（Full-duplex）** 则是人类实际对话的方式：双方可以同时说话、互相打断、在句子中间附和（说“嗯哼”），并实时做出反应。构建这种系统的难度要大得多。它要求系统同时进行倾听和音频生成，这意味着你需要解决语音打断（barge-in）的问题。

**Barge-in** is what happens when the user starts speaking while the agent is still talking. In a well-designed full-duplex system, the agent detects that the user has started speaking (via VAD), immediately stops its own audio output, cancels any pending TTS chunks, and begins processing the new input. In a poorly designed system, the agent just keeps talking while the user is trying to interrupt, which is deeply annoying.

**语音打断（Barge-in）** 是指当智能体还在说话时，用户就开始说话的情况。在一个设计良好的全双工系统中，智能体会检测到用户已开始说话（通过 VAD），并立即停止自己的音频输出，取消任何挂起的 TTS 块，然后开始处理新的输入。而在一个设计糟糕的系统中，即使用户试图打断，智能体也会自顾自地继续说话，这极其恼人。

The technical challenge of barge-in is threefold. First, you need a Voice Activity Detection (VAD) model that can distinguish the user’s voice from the agent’s own audio playback through the speaker, otherwise the agent hears itself and thinks it’s being interrupted. Second, you need to handle the latency gracefully: the moment VAD fires, you need to cut audio within milliseconds, not 300ms later. Third, you need to decide what to do with the partial audio captured during the barge-in. The question is: is it a real input or accidental noise?

语音打断的技术挑战主要有三个方面。首先，你需要一个语音活动检测（VAD）模型，该模型能够区分用户的声音和智能体自己通过扬声器播放的音频，否则智能体会听到自己的声音并误以为自己被打断了。其次，你需要在延迟约束下平稳处理：在 VAD 触发的瞬间，你必须在几毫秒内切断音频，而不是在 300 毫秒之后。第三，你需要决定如何处理在打断期间捕获的部分音频。问题在于：这是真正的输入，还是意外的噪音？

The current state of the art uses [Silero VAD](https://github.com/snakers4/silero-vad), a lightweight neural VAD model that runs locally with very low latency (~10ms per 32ms audio chunk). Combined with echo cancellation (filtering out the agent’s own audio from the mic), it gives you a reasonable barge-in detection system.

当前主流做法使用 [Silero VAD](https://github.com/snakers4/silero-vad)，这是一个轻量级的神经 VAD 模型，可在本地运行且延迟极低（每 32 毫秒音频块的延迟约为 10 毫秒）。再结合回声消除（从麦克风输入中过滤掉智能体自身的音频），你就能得到一个够用的打断检测系统。

## Turn-Taking Management

话轮转换管理 (Turn-Taking)

Humans don’t just talk and listen in strict alternation. We use backchannels (“mm-hmm”, “yeah”), we start talking slightly before the other person has fully finished, and we use prosodic cues (pitch, rhythm, trailing off) to signal turn-yielding. Current voice agent systems handle this clumsily.

人类并非严格轮流地说话与倾听。我们会使用附和语（“嗯哼”、“嗯”），会在对方尚未完全说完时稍微提前开始说话，还会使用韵律线索（音高、节奏、尾音渐弱）来暗示让出话轮。目前的语音智能体系统在处理这些情况时往往显得很笨拙。

The naive approach is energy-based end-of-speech detection: wait for N milliseconds of silence before deciding the user has finished speaking. The problem is that 500ms of silence is natural in thoughtful speech it doesn’t mean the user is done. Wait too long and the agent feels unresponsive. Wait too short and it cuts off the user.

一种朴素做法是基于能量（音量）的语音结束检测：在认定用户讲完之前，等待 N 毫秒的静音。问题在于，在深思熟虑的讲话中，500 毫秒的停顿是很自然的，这并不意味着用户已经说完了。等待时间太长，会让人觉得智能体反应迟钝。等待时间太短，又会打断用户的话。

Better approaches combine silence detection with prosodic analysis (does the pitch fall in a pattern consistent with sentence completion?) and semantic analysis (does the transcript so far form a complete thought?). Some systems use a small, fast LLM to predict whether the user’s utterance is likely complete given the transcript so far, which works surprisingly well.

更好的方法是将静音检测与韵律分析（音高的下降模式是否符合句子完成的特征？）以及语义分析（到目前为止的转录文本是否构成了一个完整的想法？）结合起来。一些系统会使用一个快速的小型 LLM，根据目前为止的转录内容来预测用户的话语是否可能已经结束，这种方法的效果出奇地好。

This is an active research area and the [LiveKit Agents](https://github.com/livekit/agents) framework supports pluggable turn detection strategies including model-based approaches.

这是一个活跃的研究领域，而 [LiveKit Agents](https://github.com/livekit/agents) 框架支持可插拔的话轮检测策略，其中包括基于模型的方法。

## The Full Architecture

完整架构

A production voice agent pipeline typically looks like this:

一个生产环境中的语音智能体流水线通常是这样的：

![Real-time voice agent architecture: a streaming loop that listens, thinks, and speaks](https://shiina18.github.io/assets/posts/images/392851710266852.jpeg "Real-time voice agent architecture: a streaming loop that listens, thinks, and speaks")

实时语音智能体架构：一个倾听、思考和说话的流式循环

The conversation state (history, memory, context) lives in the LLM prompt, which gets reconstructed for each turn. The audio transport layer (how audio bytes travel between the user’s device and your server) is typically handled by WebRTC for browser-based agents or SIP/RTP for telephony-based ones.

对话状态（历史、记忆、上下文）保存在 LLM 提示词中；每一轮都会重新构建该提示词。音频传输层（音频字节在用户设备与你的服务器之间如何传输）对基于浏览器的智能体通常由 WebRTC 处理，电话场景下的则由 SIP/RTP 处理。

## A Minimum Viable Voice Agent

## 最小可行语音智能体

To make this concrete, here is roughly what wiring up a voice agent looks like in practice. This is a simplified Pipecat-style pipeline showing how the pieces snap together — production code adds error handling, observability, and a lot more configuration, but the architecture is the same.

为了更加具体，以下是在实践中搭建一个语音智能体大致的代码模样。这是一个简化的 Pipecat 风格流水线，展示了各个组件是如何拼接在一起的——生产环境的代码会增加错误处理、可观测性以及大量配置，但整体架构是相同的。

```python
from pipecat.frames.frames import LLMMessagesFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.openai import OpenAILLMService
from pipecat.services.cartesia import CartesiaTTSService
from pipecat.transports.services.daily import DailyTransport
from pipecat.vad.silero import SileroVADAnalyzer

async def main():
    # WebRTC transport with built-in VAD and echo cancellation
    # 内置 VAD 和回声消除的 WebRTC 传输层
    transport = DailyTransport(
        room_url, token, "Voice Bot",
        DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
            transcription_enabled=False,
        ),
    )

    # Three pipeline stages
    # 流水线的三个阶段
    stt = DeepgramSTTService(api_key=DEEPGRAM_KEY)
    llm = OpenAILLMService(api_key=OPENAI_KEY, model="gpt-4o-mini")
    tts = CartesiaTTSService(api_key=CARTESIA_KEY, voice_id=VOICE_ID)

    # Voice-specific system prompt (more on this below)
    # 针对语音的系统提示词（下文会有更多说明）
    messages = [{
        "role": "system",
        "content": "You are a voice assistant. Keep replies short and natural."
    }]

    # Wire the pipeline: audio in → STT → LLM → TTS → audio out
    # 组装流水线: 音频输入 → STT → LLM → TTS → 音频输出
    pipeline = Pipeline([
        transport.input(),
        stt,
        LLMMessagesFrame(messages),
        llm,
        tts,
        transport.output(),
    ])

    task = PipelineTask(pipeline)
    await PipelineRunner().run(task)
```

That’s it. Forty lines and you have a streaming voice agent that handles VAD, echo cancellation, barge-in, and full-duplex audio over WebRTC. The complexity hidden inside `DailyTransport`, `SileroVADAnalyzer`, and the streaming services is enormous, but the application code stays small. Frameworks like Pipecat and LiveKit Agents have done the heavy lifting on the orchestration so you can focus on the parts that are actually unique to your product.

就是这样。只需四十行代码，你就能获得一个支持流式传输的语音智能体，它能够处理 VAD、回声消除、语音打断，并通过 WebRTC 实现全双工音频。隐藏在 `DailyTransport`、`SileroVADAnalyzer` 以及流式服务内部的复杂性是巨大的，但应用层的代码却依然简洁。像 Pipecat 和 LiveKit Agents 这样的框架已经完成了繁重的编排工作，以便你可以专注于那些对你的产品而言真正独特的部分。

## Choosing Your Components

组件选择

The right component choices depend heavily on your use case:

正确的组件选择在很大程度上取决于你的应用场景：

**For lowest latency:** Deepgram Nova-2 (STT), a distilled 7-8B model (LLM), Cartesia Sonic or ElevenLabs Flash (TTS). This stack can hit sub-500ms consistently.

**追求最低延迟：** Deepgram Nova-2 (STT)，经过蒸馏的 7-8B 模型 (LLM)，Cartesia Sonic 或 ElevenLabs Flash (TTS)。这个技术栈可以稳定地达到 500 毫秒以下的延迟。

**For highest accuracy:** Whisper large-v3 or AssemblyAI (STT), GPT-4o or Claude Sonnet (LLM), ElevenLabs Turbo (TTS). Accuracy is better but latency is 800ms+.

**追求最高准确率：** Whisper large-v3 或 AssemblyAI (STT)，GPT-4o 或 Claude Sonnet (LLM)，ElevenLabs Turbo (TTS)。准确率更高，但延迟在 800 毫秒以上。

**For telephony deployment:** Twilio handles audio transport, Deepgram for STT, small LLM, ElevenLabs or AWS Polly for TTS. The PSTN (phone network) introduces its own latency — typically 150-200ms of jitter buffer alone — so your target response time needs to account for it.

**针对电话部署：** Twilio 处理音频传输，Deepgram 负责 STT，搭配小型 LLM，ElevenLabs 或 AWS Polly 用于 TTS。PSTN（公共交换电话网络）会引入其自身的延迟——通常单是抖动缓冲就有 150-200 毫秒——因此你的目标响应时间需要考虑到这一点。

**For fully self-hosted, privacy-first:** Whisper.cpp (local STT), Llama-3 via Ollama (local LLM), Coqui/VITS or Piper (local TTS). Excellent for private deployments; latency depends on your hardware.

**针对完全自托管、隐私优先：** Whisper.cpp (本地 STT)，基于 Ollama 的 Llama-3 (本地 LLM)，Coqui/VITS 或 Piper (本地 TTS)。非常适合私有部署；延迟取决于你的硬件。

## What the LLM Prompt Looks Like

LLM 提示词 (Prompt) 应该怎么写

Voice-specific prompt engineering deserves a mention. Responses need to be designed for speech, not text. That means:

专门针对语音的提示词工程值得一提。回复必须是为了“被说出来”而设计的，而不是为了阅读。这意味着：

*   No markdown formatting, bullet points, or headers. These appear verbatim in TTS and sound bizarre
*   Short sentences and natural cadence. Long complex sentences with many sub-clauses are hard to follow when spoken
*   Avoid lists and use “first… then… finally…” constructions instead
*   Contractions and casual register feel more natural in speech
*   Build in filler words sparingly (“let me check that for you”) when computation will take a moment

*   不要使用 Markdown 格式、项目符号或标题。这些内容在 TTS 中会被一字不差地读出来，听起来非常怪异。
*   使用简短的句子和自然的语流。冗长复杂、包含众多从句的句子在口语中很难让人跟上。
*   避免使用列表，而是改用“首先……然后……最后……”的句式结构。
*   在口语中，缩读（如 I'm, you're）和随意的语域（register）会显得更自然。
*   当计算需要稍作等待时，适度加入一些填补词（“请稍等，让我为您查看一下”）。

```python
SYSTEM_PROMPT = """You are a voice assistant. Your responses will be spoken aloud.
Follow these rules strictly:
- Respond in natural conversational language, as you would speak it
- Never use bullet points, numbered lists, headers, or markdown
- Keep responses concise — 2-4 sentences for most answers
- Use natural speech patterns with contractions (you're, it's, I'll)
- If you need more time to think, say 'let me think about that for a moment'
"""
```

## The Hard Problems That Remain

尚未解决的难题

The basic pipeline I have described is well-understood at this point. The hard problems are what separate mediocre voice agents from good ones.

我刚刚描述的基本流水线目前已经为人熟知。那些悬而未决的难题，才是区分平庸语音智能体与优秀语音智能体的关键所在。

**Noisy environments** are the underrated killer of voice agents. A user calling from a coffee shop, or with background TV noise, or with kids in the same room sees STT accuracy drop substantially. The model still produces a transcript, but it’s wrong, and the LLM responds confidently to a query the user never asked. Tools like Krisp and RNNoise help significantly with stationary noise (HVAC, fans, traffic), but non-stationary noise (other voices, music with vocals, sudden loud sounds) is much harder. You can paper over this with voice-specific prompting that asks the user to repeat themselves when confidence is low, but it’s a workaround, not a solution.

**嘈杂的环境**是语音智能体被低估的杀手。用户在咖啡馆、有电视背景音、或者与孩子同处一室的情况下打电话，会导致 STT 的准确率大幅下降。模型仍然会生成转录，但却是错误的，随后 LLM 就会对一个用户从未提出的问题给出自信的回答。像 Krisp 和 RNNoise 这样的工具对平稳噪声（暖通空调、风扇、交通噪音）有显著帮助，但对于非平稳噪声（其他人的声音、带有人声的音乐、突然的巨响）则很难处理。你可以通过语音专用的提示词，在置信度低时要求用户重复他们的话来临时糊弄过去，但这只是一种变通之计，并非根本解决方案。

**Multi-speaker scenarios** are the situation almost no production voice agent handles correctly. Imagine a family customer service call: spouse and kid in the same room, both occasionally chiming in. The agent’s STT will produce a Frankenstein transcript blending all three voices, and the LLM will respond to a query that nobody actually asked. Speaker diarization (figuring out *who* said *what*) is the answer. Pyannote-audio is the dominant open-source option, but adding it costs 200-400ms of latency on every turn and the accuracy on short utterances is still poor. Most teams just don’t solve this.

**多说话人场景**是几乎没有已上线语音智能体能正确处理的情况。想象一通家庭客服电话：配偶和孩子在同一个房间里，偶尔都会插话。智能体的 STT 会生成一个混合了三人声音的“科学怪人”式转录，而 LLM 也会回应一个实际上没有任何人提出的问题。说话人分离（识别*谁*说了*什么*）是解决之道。Pyannote-audio 是占主导地位的开源选项，但加入它会在每一轮对话中增加 200-400 毫秒的延迟，而且在短句上的准确率仍然很差。大多数团队干脆选择不去解决这个问题。

**Long conversations** hit context-window limits faster than text agents because every utterance needs to be transcribed, stored, and fed back as context for every subsequent turn. A 30-minute support call is easily 6,000-10,000 tokens of conversation history alone, before any system prompt or RAG context. You need a memory architecture that summarizes older turns, extracts persistent facts, and reloads relevant context on demand and crucially, all of that has to fit inside the same 500ms latency budget. This is one of the harder engineering problems in the space.

**超长对话**达到上下文窗口限制的速度比文本智能体更快，因为每一次发言都需要被转录、存储，并作为每一轮后续对话的上下文反馈回去。一个 30 分钟的支持电话，单是对话历史就轻松达到 6000-10000 个 tokens，这还不包括任何系统提示词或 RAG 上下文。你需要一种记忆架构来总结旧的轮次、提取持久的事实，并按需重新加载相关的上下文，而且至关重要的是，所有这些操作都必须在同一个 500 毫秒的延迟预算内完成。这是该领域较难的工程问题之一。

**Accents and speaking styles** vary STT accuracy dramatically. A model that scores 5% WER on a benchmark of American English speakers might score 15% on Indian English, 20% on Nigerian English, and 30% on heavily accented non-native speakers. Deepgram and AssemblyAI have improved substantially here, but if your product is global, you need to test specifically on the accents your users actually have, not the benchmarks the vendors quote.

**口音和说话风格**会极大影响 STT 的准确率。一个在美式英语基准测试中得分只有 5% WER（词错误率）的模型，在面对印度英语时可能会达到 15%，尼日利亚英语可能达到 20%，而在面对口音浓重的非母语者时甚至会高达 30%。Deepgram 和 AssemblyAI 在这方面已经取得了实质性的进步，但如果你的产品是面向全球的，你就需要针对你的用户实际拥有的口音进行专门的测试，而不要只看供应商引用的基准测试数据。

## The Road Ahead

未来的路

This primer covers the architecture. The interesting engineering is in the details. In future posts I’ll go deep on the latency stack and where every millisecond actually goes, the barge-in problem and how production systems solve full-duplex correctly, building memory layers that survive within the latency budget, evaluating voice agents (which standard LLM evals completely miss), telephony infrastructure including WebRTC versus SIP and the codec choices that matter, and how modern TTS expresses emotion and prosody.

这篇入门指南涵盖了架构。有意思的工程都在细节里。在未来的文章中，我将深入探讨延迟栈以及每一毫秒到底花在了哪里，探讨语音打断问题以及生产系统如何正确实现全双工，探讨如何在延迟预算内构建仍可用的记忆层，探讨如何评估语音智能体（标准的 LLM 评估完全无法覆盖这一点），探讨电话基础设施（包括 WebRTC 与 SIP 的对比以及关键的编解码器选择），还会探讨现代 TTS 是如何表达情感和韵律的。

The voice agent space is moving fast and frameworks like LiveKit, Daily, and Pipecat have made the infrastructure significantly more accessible than it was even 18 months ago. The architectural patterns are converging. The challenge now is in the details: making the latency actually feel like presence, making the memory actually feel like continuity, and making the turn-taking actually feel like a conversation.

语音智能体领域发展迅速，像 LiveKit、Daily 和 Pipecat 这样的框架使得基础设施比 18 个月前变得容易获取得多。架构模式正在趋同。现在的挑战在于细节：如何让延迟带来真人在场的临场感，如何让记忆感觉连贯，以及如何让话轮转换真正像一场流畅的对话。

If you’re building anything in this space, I’d love to hear about it.

如果你正在这个领域做任何事，我非常希望能听到你的分享。

***

*If you found this interesting, I’d love to hear your thoughts. Share it on [Twitter](https://twitter.com/manthanguptaa), [LinkedIn](https://www.linkedin.com/in/manthanguptaa/), or reach out at guptaamanthan01\[at\]gmail\[dot\]com.*

*如果你觉得这篇文章很有趣，我非常期待听到你的想法。欢迎在 [Twitter](https://twitter.com/manthanguptaa)、[LinkedIn](https://www.linkedin.com/in/manthanguptaa/) 上分享，或者通过 guptaamanthan01\[at\]gmail\[dot\]com 与我联系。*

## References

参考资料

*   [Silero VAD](https://github.com/snakers4/silero-vad) — Lightweight neural voice activity detection
*   [LiveKit Agents](https://github.com/livekit/agents) — Open-source voice agent framework
*   [Pipecat](https://github.com/pipecat-ai/pipecat) — Open-source framework for voice and multimodal AI applications
*   [Deepgram Nova-2](https://deepgram.com/) — Low-latency streaming STT
*   [Cartesia Sonic](https://cartesia.ai/) — Ultra-low-latency neural TTS
*   [Kyutai Moshi](https://kyutai.org/Moshi.pdf) — Open end-to-end speech model with sub-300ms latency
*   [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime) — End-to-end speech via GPT-4o
*   Latency benchmarks from ElevenLabs, Bland.ai, and Retell.ai public documentation

*   [Silero VAD](https://github.com/snakers4/silero-vad) — 轻量级神经语音活动检测 (VAD)
*   [LiveKit Agents](https://github.com/livekit/agents) — 开源语音智能体框架
*   [Pipecat](https://github.com/pipecat-ai/pipecat) — 用于语音和多模态 AI 应用的开源框架
*   [Deepgram Nova-2](https://deepgram.com/) — 低延迟流式 STT (语音转文本)
*   [Cartesia Sonic](https://cartesia.ai/) — 超低延迟神经 TTS (文本转语音)
*   [Kyutai Moshi](https://kyutai.org/Moshi.pdf) — 延迟低于 300 毫秒的开源端到端语音模型
*   [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime) — 基于 GPT-4o 的端到端语音
*   来自 ElevenLabs、Bland.ai 和 Retell.ai 公开文档的延迟基准测试