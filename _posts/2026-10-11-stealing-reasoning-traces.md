---
title: "读论文: 偷走大模型的思考链"
categories:
- LLM
tags: Security
updated:
comments: true
mathjax: false
---

读 Panfilov et al. (2026) 的笔记.

- Panfilov, A., Schmotz, D., Shumailov, I., Beurer-Kellner, L., Schaeffer, J., Prabhu, A., Geiping, J., & Andriushchenko, M. (2026). [Stealing reasoning traces from proprietary LLM APIs](https://arxiv.org/abs/2608.09867). *arXiv preprint arXiv:2608.09867*.

<!-- more -->

## 原理

推理模型的思维链比最终答案敏感得多 — 既能拿去蒸馏, 又常夹带用户隐私和有害内容. 所以各家 API 已不再明文返回: 思维链包成加密块交客户端保存, 后续请求原样传回, 服务端不存 (无状态设计).

漏洞出在无状态上 — 加密块必须可移植, 否则没法跨请求传递. 实际上各家都是同一把全局 key, 加密块在同一家供应商的 session / 用户 / 模型之间随意互换 (并非无条件: Fable 5 的块哪都放不进, GPT-5.6 系列的块只有同系模型接得住); 而防护不对称: 强模型有反蒸馏的 refusal 训练, 弱模型 (Haiku / Luna 这类) 没有. 于是解码只要两步: 向强模型要一个加密思维链, 塞进弱模型上下文骗它逐字转写成明文. 全程没碰强模型的对齐, 弱模型只是个解密 oracle.

![跨模型重放攻击总览, 来自论文 Figure 1](https://shiina18.github.io/assets/posts/images/steal-cot-teaser.png "跨模型重放攻击总览, 来自论文 Figure 1")

## 能干什么

- 蒸馏: 白嫖真思维链当训练数据, 监督信号比只抄最终答案密得多; 解码 1 万条约 $720. 更省事的是连强模型都不用调, 公开数据集里现成的加密块直接解
- 泄密: 模型思考时会原样复述用户的 API key 和密码, 而加密块对用户不可读, 公开日志时只洗得掉明文. 作者扫了公开 agent 日志里 31.5 万个块, 找回 62 个真实 API key, 33 个密码; 另有 64 条敏感信息只存在于密文里
- 越狱: 模型被训练成 "只在最终输出里拒绝", 思考过程照样推演有害内容. 让强模型想一个有害问题 (最终答案安全地拒绝), 解码思维链即可拿到
- 隐形 prompt injection: 恶意指令可以整个藏进加密块随 trace 发布, 别人续跑这条 trace 时模型把注入当成 "自己之前的思考" 照做, 用户和外部 monitor 都看不到明文

## 修法

要么服务端存思维链 (客户端只拿一个 ID), 要么把 session / 用户 id 绑进加密信封 (AEAD, authenticated encryption with associated data), 跨上下文重放直接验签失败. 对用户的建议只有一条: 公开 agent trace 前把 reasoning block 整个删掉 — 反正你也读不了它.
