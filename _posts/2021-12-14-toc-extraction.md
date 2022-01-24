---
title: "文档目录抽取"
categories: 
- Machine Learning
updated: 
comments: true
mathjax: false
---

文档结构化是很暧昧的词, 它可能的意思很多, 不过本文只考虑目录抽取.

结构化文档由各级章节标题和段落等逻辑结构组成, 比如对 HTML 来说, 逻辑结构包括 `<body>` `<h1>` `<p>` 等标签. 文档结构化任务基本等价于目录抽取, 因为识别出标题后剩下的就是段落. 这个领域可供搜索的关键词包括 document structure recognition, document layout analysis (版面分析) 等. 意义: 便于抽取信息, 高度定制化的展示等.

<!-- more -->

```html
<body>

<h1>Structured document</h1>
<p>A <strong class="selflink">structured document</strong> 
is an <a href="/wiki/Electronic_document" title="Electronic document">electronic document</a> 
where some method of 
<a href="/wiki/Markup_language" title="Markup language">markup</a> 
is used to identify the whole and parts of the document 
as having various meanings beyond their formatting.</p>

</body>
```

## PDF 解析

Java 的 [Apache PDFBox](https://pdfbox.apache.org/) 可以得到 pdf 底层信息, 然后进行推断重建文档结构. 可以得到的信息包括

- 每个字的盒子 (bounding box): 左上角 (不确定, 总之是某个角) 横纵坐标, 盒子高度和宽度, 颜色, 字体, 方向 (页面是否旋转) 等. 
- 线条信息, 从而可以连接组合成有线表.

纯 PDF 解析版面分析算法的例子可以参考 [这里](https://pdfminersix.readthedocs.io/en/latest/topic/converting_pdf_to_text.html), 连字成行, 连行成段.

开源工具 [pdf2htmlEX](https://pdf2htmlex.github.io/pdf2htmlEX/) 可以高质量地还原 pdf 排版, 但是很慢而且几乎无法从其生成的 html 中读出结构信息, 可定制性低, 难以后续处理, 文件大.

- 北京庖丁科技. (2020, Mar 24). [为什么说从 PDF 中提取文本是一件困难的事?](https://mp.weixin.qq.com/s/99LlGzr1K1LrigW1w6uCgg).
- 北京庖丁科技. (2020, Dec 7). [电子文档全景结构识别漫谈](https://mp.weixin.qq.com/s/aH2kEqtUElAtub3El1l_kg).

### Python 包

- [Pdfminer.six](https://github.com/pdfminer/pdfminer.six) 不太能用.
- [pdfplumber](https://github.com/jsvine/pdfplumber): Plumb a PDF for detailed information about each text character, rectangle, and line. Plus: Table extraction and visual debugging. Works best on machine-generated, rather than scanned, PDFs. 他实现表格抽取的逻辑可以参考 [冰焰虫子的博客](https://iceflameworm.github.io/).

<!--
### 其他

- 根据字体可以判别粗体/斜体与否, 比如 [这里](https://github.com/jsvine/pdfplumber/issues/299) 粗体直接有 bold, [这里](https://github.com/jsvine/pdfplumber/issues/368) 说斜体可以从 fontname 判断, 但实际好像不行. [下划线的判别方法](https://github.com/jsvine/pdfplumber/issues/368).
- Poor man's bold 会以重复相同的字两次 (平移微小的量) 实现.
-->

## 难点

- 缺乏标注数据.
- 排版依赖于 PDF 解析, 后者本身就是众所周知的难题.

## 相关比赛

- [CCKS2021 面向保险领域的低资源文档信息抽取](https://tianchi.aliyun.com/competition/entrance/531903/introduction)
    - 数据: 解析后的 pdf 信息, 包括 word, x0, y0, x1, y1, fontsize, fontname. 少量标注数据, 大量无标注数据.
    - 任务: 文档标题层级抽取, 文档开放信息抽取 (属性-属性值对). 
    - 方法: 目前没有找到公开讨论.
    - 评论: 第一个任务和我们的目标完全吻合, 但给出的案例标题前都有数字, 看起来比较简单 (我们要处理的标题前没有数字); 第二个任务看实例也很简单.
- 虽然不是比赛, 但任务同 CCKS2021. 北邮同学的方法: 改造 Adaboost
    - 文章截图给出的例子是带数字开头标题的保险协议. 一共 1w+ 个 data samples.
    - Yue, T., Li, Y., & Hu, Z. (2021). DWSA: An Intelligent Document Structural Analysis Model for Information Extraction and Data Mining. *Electronics*, *10*(19), 2443.
- FINTOC 系列比赛
    - 目前 19-21 年一共三届, 每次只有五个左右队伍参加.
        - Juge, R., Bentabet, I., & Ferradans, S. (2019). The fintoc-2019 shared task: Financial document structure extraction. *Proceedings of the Second Financial Narrative Processing Workshop (FNP 2019)*, 51–57.
        - Bentabet, N.-I., Juge, R., El Maarouf, I., Mouilleron, V., Valsamou-Stanislawski, D., & El-Haj, M. (2020). The financial document structure extraction shared task (FinToc 2020). *Proceedings of the 1st Joint Workshop on Financial Narrative Processing and MultiLing Financial Summarisation*, 13–22.
        - El Maarouf, I., Kang, J., Azzi, A. A., Bellato, S., Gan, M., & El-Haj, M. (2021). The Financial Document Structure Extraction Shared Task (FinTOC2021). *Proceedings of the 3rd Financial Narrative Processing Workshop*, 111–119.
    - 数据: 英语和法语的股票招股说明书
    - 任务: 标题识别, 和标题层级 (目录) 抽取
    - 方法: 一般分为两步, 先识别标题, 再生成层次 (可以看成推荐系统中的召回精排两步). 方法几乎清一色的传统机器学习 (XGB 等), 一般不用到文本, 而是字体大小, 斜体与否, 标点数字, 上下文特征等特征; 基于规则生成也很多.
    - 评论: 任务吻合, 可以参考特征.


## 工业界实践

好像没有直接的识别标题层次.

- BMES 序列标注@达观数据: 只是段落识别, 并没有提到怎么识别标题以及标题层次
    - 把段落解析任务类比为分词任务, 把每一行看成 "字", 每个段落看成 "词". 
    - 分词要结合每个字符上下文的语义信息做概率判断, 但是在分段的时候, 每一行的语义信息太过丰富, 在实践上不好用. 不过分段有自己的特征, 比如缩进, 结尾标点, 独立成行的标题可能会有数字开头, 这些都可以作为特征输入到模型里去. 
    - 参考 [达观数据高级技术专家分享: 如何在金融行业应用文档结构化?](https://zhuanlan.zhihu.com/p/260440588) (让听众思考怎么解决 badcase, 但是没有说他们的方案)

![](https://shiina18.github.io/assets/posts/images/20211213152655088_17000.png)

- CV 版面分析@百度文库: 百度文库为了多平台展示, 要把 pdf 的版式排版解析为流式排版. 
    - 最开始用的也是通用方法, 连字成行再成段; 对于复杂排版 (多栏, 图文排绕等) 需要 CV 分析版面, 把页面切分成多个区域, 每个区域再用通用方案. 
    - 百度文库里 word 文档很多, 专门方案: 先把 doc (二进制) 格式转化为 docx (ooxml) 格式, 再对后者解析. 
    - 参考 [文档内容结构化在百度文库的技术探索](https://mp.weixin.qq.com/s/QIp8K6U-FCj2H9cq_SgkPA)
- 预训练模型 LayoutLM@Amazon
    - Although traditional text models (like RNNs, LSTMs, or even n-gram based methods) account for the order of words in the input, many are quite rigid in their approach of treating text as a linear sequence of words. In practice, documents aren't simple strings of words, but rich canvases with features like headings, paragraphs, columns, and tables. Because the input position encoding of models like BERT can incorporate this position information, we can boost performance by training models that learn not just from the content of the text, but the size and placement too. 
    - 用到了微软亚研出品的 LayoutLM, 简单地说就是把 BERT 的 positional encoding 替换为了基于每个字 bounding box 四个坐标的编码, 除此之外还有 image embedding. 
    - 参考 [Bring structure to diverse documents with Amazon Textract and transformer-based models on Amazon SageMaker](https://aws.amazon.com/cn/blogs/machine-learning/bring-structure-to-diverse-documents-with-amazon-textract-and-transformer-based-models-on-amazon-sagemaker/)
    - LayoutLM 已经发展了很多代版本
        - [微软亚洲研究院提出多语言通用文档理解预训练模型 LayoutXLM](https://www.msra.cn/zh-cn/news/features/layoutxlm) (包括中文)
        - [Github](https://github.com/microsoft/unilm/tree/master/layoutxlm). 模型巨大 (1.5G), 目前没有看到国内实践经验.
- 阿里达摩院的 [展示](https://vision.aliyun.com/experience/detail?spm=a2c4g.11186623.0.0.6cc469768Y2hb7&&tagName=ocr&children=TrimDocument). 给的实例都太简单了, 案例五效果明显有问题.
- 同花顺 iFinD 的 [展示](https://www.sohu.com/a/238369466_100132876), 对于数字开头的标题, 截图中肉眼可见的有错漏.

## 其他

- [文档结构化任务数据集介绍](https://zhuanlan.zhihu.com/p/437042065)  
- [微信图片翻译技术优化之路](https://mp.weixin.qq.com/s/GVLZ3IRanjJebp87we_R5A)
- Déjean, H., & Meunier, J.-L. (2010). Reflections on the inex structure extraction competition. *Proceedings of the 9th IAPR International Workshop on Document Analysis Systems*, 301–308.
- [PaddleOCR新发版v2.2：开源版面分析与轻量化表格识别](https://mp.weixin.qq.com/s/Au6PGio56IJ1bdY3GkaIgg)
- [CCKS测评任务5 基于 OpenCV 和 Faster R-CNN 的金融财报抽取](https://conference.bj.bcebos.com/ccks2019/eval/webpage/pdfs/eval_paper_5_6.pdf)
- 比如 Google 的 [Document AI](https://cloud.google.com/document-ai) 重点还是解析表单, 证件等.