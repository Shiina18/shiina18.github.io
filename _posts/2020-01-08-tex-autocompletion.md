---
title: "在 TeXworks 中自定义代码补全"
categories: Language
updated: 
comments: true
mathjax: false
---

因为 TeXworks 用了太多年, 不太想换 IDE, 还是继续用了.

参考 [官方文档](https://github.com/TeXworks/texworks/wiki/CodeCompletion).

文件地址: TeXworks 菜单栏的 "帮助" -> "TeXworks 配置与资源" -> "资源" -> "completion" 文件夹 -> "tw-latex.txt" 文件.

## 语法

```
<alias>:=<text>
```

The `<alias>:=` part can be omitted to turn the code text into its own alias. `<text>` must fit in a single line. Empty lines and lines starting with a % are ignored.

第一句话的意思是, 单纯写 `blahblah` 相当于 `blahblah:=blahblah`.

`<text>` 中连续的空格是有效的.

- `#RET#` 表示 return, 换行.
- `#INS#` 表示 insert, 光标会被放置在此处.
- `•` bullet 是 placeholder, 使用 `<Ctrl>+<Tab>` 让光标移动到下一个占位符处.

<!-- more -->

## 使用

在 "tw-latex.txt" 文件中输入

```tex
bali:=\begin{align}#RET##INS##RET#\end{align}#RET#•
```

在 TeXworks 编辑器中输入 bali 后按 `<Tab>`, 那么 TeXworks 会从 completion 文件夹的所有文本中匹配以 bali 开头的所有 alias (有 bali, balis, baliat 等), 然后把 alias 替换为对应的 text. 

连续按 `<Tab>` 可以在所有的匹配中跳转. 如果仅输入 b 就按 `<Tab>` 的话, 以 b 开头的所有 alias 都会被匹配到, 要找到想要的命令会很困难.

把 bali 换成对应的 text 就成了下面的样子.

```tex
\begin{align}

\end{align}
•
```

## 例子

TW 自带的匹配项我觉得都挺别扭的,  比如

```tex
\begin{align}

\end{align}•
```

我觉得占位符和 end 放在同一行不好, 就加了个 `#RET#`. 

我写的部分代码如下.

```tex
(:=\left( #INS# \right) •

bfig:=\begin{figure}#RET#    \centering#RET#    \includegraphics[width=16cm]{#INS#}#RET#    \caption{•}#RET#\end{figure}#RET#•

sum:=\sum_{#INS#}^{•}
sum:=\sum_{i=1}^{n}#INS#
sum:=\sum_{j=1}^{n}#INS#
\sum:=\sum_{#INS#}^{•}
\sum:=\sum_{i=1}^{n}#INS#
\sum:=\sum_{j=1}^{n}#INS#

^:=^{-1}#INS#
^:=^{1/2}#INS#
^:=^{#INS#}
_:=_{\{ #INS# \}}•
_:=_{#INS#}
,:=, \dots, #INS#

\xrightarrow{#INS#}
```

Alias 是可以重复的. Alias 尾部的空格并没有用, 比如写为 `a :=text` 后输入 `a ` 按 `<Tab>` 是没有用的.