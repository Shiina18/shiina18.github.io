---
title: "计算机网络简要"
categories: Tech
updated:
comments: true
mathjax: false
---

参考

- 谢希仁. (2017). 计算机网络 (第 7 版). 电子工业出版社.

只记录了大体框架.

<!-- more -->

## 概述

- 互联网 (Internet): 注意是 "联", 不是 "连". 互连网络 (internet) 是一个通用名词. 从数学上来说, 计算机网络可以看为一个图; 用这个学科的术语, 图的顶点称为结点 (node), 边为链路 (link). 结点可以是计算机, 集线器, 交换机, 路由器等, 注意不是 "节点".
- 主机 (host): 与网络相连的计算机.
- ISP (Internet Service Provider): 互联网服务提供商, 比如电信, 联通, 移动.

![](https://shiina18.github.io/assets/posts/images/20201230110851735_20495.png)

### 互联网的组成

从工作方式看, 可以分为边缘部分, 即连接在互联网上的主机, 是用户直接使用的部分, 主机称为端系统 (end system); 以及核心部分, 由大量网络和连接这些网络的路由器组成, 为边缘部分提供服务.

进行通信的是进程 (process). 端系统间的通信方式有 Client/Service, P2P (peer to peer).

路由器 (router) 是一种专用计算机, 是实现分组交换 (packet switching) 的关键构件, 任务是转发收到的分组.

分组交换采用存储转发技术. 要发送的整块数据称为一个报文 (message), 先把它分为更小的等长数据段, 每个数据段前加上首部 (header) 后就构成了一个分组 (packet), 也叫 "包". 首部包含了目的地址和源地址等控制信息. 路由器收到分组时, 先暂时存储一下, 检查首部, 查找转发表, 按照首部中的目的地址, 找到合适的接口转发到下一个路由器直至主机.

![分组交换的好处](https://shiina18.github.io/assets/posts/images/20201230104248594_9970.png "分组交换的好处")

### 协议

TCP/IP 是四层结构, 学习时以五层结构来讲. 协议只针对同层之间的通信, 是 "水平的". 服务是 "垂直的", 由下层向上层通过接口提供.

![](https://shiina18.github.io/assets/posts/images/20201230110142008_19379.png)

- 应用层 (application layer). 应用进程间通信和交互的规则. DNS, HTTP, SMTP 等. 应用层交互的数据单元称为报文.
- 运输层 (transport layer). 负责向两台主机中进程间的通信提供通用的数据传输服务.
    - TCP (transmission control protocol). 提供面向连接的, 可靠的数据传输服务, 单位是报文段 (segment).
    - UDP (user datagram protocol). 提供无连接的, 尽最大努力 (best-effort) 的数据传输服务 (不保证可靠性). 单位是用户数据报.
- 网络层 (network layer). 负责为分组交换网上的不同主机提供通信服务. 把运输层产生的报文段或用户数据报封装成分组. 由于使用 IP, 分组也叫 IP 数据报, 或简称数据报 (和用户数据报不同). 另一个任务是选择合适的路由.
- 数据链路层 (data link layer). 把分组组装成帧 (frame), 在结点间传送帧.
- 物理层 (physical layer). 单位是比特 (bit). 要考虑用多大的电压代表 1 或 0, 以及接收方如何识别. 电缆插头结构.

![](https://shiina18.github.io/assets/posts/images/20201230105926206_17763.png)

首部可以看成 "信封", 传输时一层层套信封, 最后一层层解开信封. 路由器只有底下三层, 没有运输层.

## 网络层

网络层向上只提供简单灵活的, 无连接的, 尽最大努力交付的数据报 (datagram) 服务. 数据报, IP 数据报, 分组是同义词. 在发送分组时不需要先建立连接, 每个分组独立发送 (不编号). **网络层不提供服务质量的承诺.** 分组可能出错, 丢失, 重复, 失序, 也不保证交付时限. 这使得路由器简单, 价格低廉. 可靠性由运输层负责, 就是端系统自己保证, 而不是靠网络保证.

### 网际协议 IP

Internet Protocol.

#### 虚拟互连网络

将网络连接起来的中间设备.

- 物理层: 转发器 (repeater).
- 数据链路层: 网桥, 桥接器 (bridge).
- 网络层: 路由器 (router), 由于历史原因, 也叫网关.
- 网络层以上: 网关 (gateway).

互连之后的网络看成虚拟互连网络 (internet), 称为 IP 网. 即逻辑互连, 利用 IP 使得物理上各异的网络在网络层上看起来好像是一个统一的网络. 如果在覆盖全球的 IP 网的上层使用 TCP, 那么就是现在的互联网.

#### IP 地址

IP 地址是给互联网上每一台主机或路由器的每一个接口分配一个在全世界范围内是唯一的 32 位的标识符. IP 地址的结构方便寻址. 为了提高可读性, 就有点分十进制标记法.

硬件地址又称为物理地址或 MAC (media access control) 地址, 是指局域网上的每一台计算机中固化在适配器的 ROM 中的地址. 物理地址是数据链路层和物理层使用的地址, 而 IP 地址是网络层及以上各层使用的地址, 是一种逻辑地址.

尽管互连在一起的网络硬件地址体系各不相同, 但 IP 层抽象的互联网却屏蔽了下层这些很复杂的细节. 只要我们在网络层上讨论问题, 就能使用统一的, 抽象的 IP 地址研究主机和主机或路由器之间的通信.

编址方法的三个历史阶段.

- 分类的 IP 地址.
- 子网的划分.
- 构成超网. 无分类.

无分类域间路由选择 CIDR (classless inter-domain routing). 消除了传统的分类地址以及划分子网的概念, 因而能更加有效地分配 IPv4 的地址空间. 把 32 位的 IP 地址划分为前后两个部分, 前面部分是 "网络前缀", 指名网络, 后面部分用来指名主机. 还使用 "斜线记法" (slash notation), 或者叫 CIDR 记法, 即在 IP 地址后面加上斜线 `/`, 然后写上网络前缀所占的位数.

为了更方便地进行路由选择, CIDR 使用 32 位的地址掩码 (address mask). 由一串 1 和一串 0 组成, 1 的个数就是网络前缀的长度. 虽然 CIDR 不适用子网了, 但由于目前还有一些网络使用子网划分和子网掩码, 地址掩码也可继续称为子网掩码. 例如 `/20` 地址块的掩码就是连续 20 个 1 再接 12 个 0. 

网际控制报文协议 ICMP (Internet Control Message Protocol). ICMP 报文作为 IP 层数据报的数据, 有两种, ICMP 差错报告报文和 ICMP 询问报文.

IPv6 每个地址占位 128 位, 点分十进制记法也不够方便了, 改用冒号十六进制记法.

#### 网络地址转换 NAT

Network Address Translation. 专用 (private).

![](https://shiina18.github.io/assets/posts/images/20201231115723494_18052.png)

![](https://shiina18.github.io/assets/posts/images/20201231115741988_7227.png)

为了更加有效地利用 NAT 路由器上的全球 IP 地址, 现在常用的转换表把运输层的端口号也利用上. 这样就可以使多个拥有本地地址的主机共用一个 NAT 路由器上的全球 IP 地址.

![](https://shiina18.github.io/assets/posts/images/20201231115903055_4129.png)

硬件茶谈. (2020, Aug 21). [【硬件科普】IP 地址是什么东西? IPv6 和IPv4 有什么区别? 公网 IP 和私有 IP 又是什么?](https://www.bilibili.com/video/BV1DD4y127r4). *bilibili*.

## 运输层

###  概述

运输层提供通信服务. IP 虽然能将分组送到目的主机, 但是这个分组还停留在网络层而没有交付应用进程.

![](https://shiina18.github.io/assets/posts/images/20201230120739897_2181.png)

逻辑通信: 数据实际按照虚线传送, 但是底下的细节在运输层看不到, 就好像两个运输层之间直接传送一样. 网络层为主机之间提供逻辑通信, 而运输层为应用进程之间提供逻辑通信.

运输层还要对报文进行差错检测. 网络层只检验首部, 不检查数据部分. 传送的数据单位是 TCP 报文段 (segment) 或 UDP 用户数据报.

单个计算机中的进程使用进程标识符 (一个不大的整数) 标志, 但这不适用与互联网. 解决方法是在运输层使用协议端口号 (protocol port number), 简称端口. 虽然通信的终点是应用进程, 但只要把报文交到目的主机的目的端口, 剩下的工作就由 TCP 或 UDP 来完成.

TCP/IP 的运输层用一个 16 位端口号标志一个端口. 端口号只具有本地意义, 标志本计算机应用层中的各个进程和运输层交互时的层间接口. 由此, 两个计算机中的进程需要通信, 不仅要知道对方的 IP 地址 (为了找到对方的计算机), 也需要知道对方的端口号 (为了找到对方计算机中的应用进程).

- 服务器端使用的端口号
    - 熟知端口号 (well-known port number) 或系统端口号, 数值为 0~1023. 例如 DNS 53, HTTP 80, HTTPS 443.
    - 登记端口号, 数值为 1024~49151.
- 客户端使用的端口号
    - 数值为 49152~65535. 仅在客户进程运行时才动态选择, 又叫短暂端口号. 

### 用户数据报协议 UDP

User Datagram Protocol. 只在 IP 的数据报服务上增加了很少的一点功能.

- 无连接. 发送数据前不需要建立连接.
- 尽最大努力交付. 不保证可靠交付.
- 面向报文. 发送方的 UDP 对应用进程交下来的报文, 添加首部后就交付 IP 层, 不合并也不拆分.
- 没有拥塞控制. 网络出现的拥塞不会使源主机的发送速率降低, 这对某些实时应用是很重要的 (视频会议).
- 支持多对多的交互通信.
- 首部开销小. 只有 8 个字节, 比 TCP 20 个字节短.

首部由 4 个字段组成, 每个字段 2 个字节. 源端口, 目的端口, 用户数据报的长度, 检验和.

如果接收方 UDP 发现报文中的目的端口号不正确, 就丢弃该报文, 并由 ICMP 发送 "端口不可达" 差错报文给发送方.

### 传输控制协议 TCP

Transmission Control Protocol. 

- 面向连接. 应用进程在使用 TCP 之前, 必须先建立连接, 传完后释放连接.
- 每一条 TCP 连接只能有两个端点. 一对一. 端点叫做套接字 (socket) 或插口. 端口号拼接到 IP 地址即构成了套接字, 例 (192.3.4.5: 80), 前面是点分十进制的 IP 地址, 中间冒号或逗号隔开, 再写上端口号. 一条 TCP 连接唯一地被两个套接字确定.
- 可靠交付. 无差错, 不丢失, 不重复, 按序到达.
- 全双工 (full duplex) 通信. 允许数据在两个方向上同时传输.
- 面向字节流. 流指的是流入或流出进程的字节序列. 面向字节流的意思是, 虽然应用进程和 TCP 的交互是一次一个数据块, 但 TCP 把应用程序交下来的数据仅仅看成是一连串的无结构的字节流.

![](https://shiina18.github.io/assets/posts/images/20201230150230590_3710.png)

### 可靠传输

出现差错时, 让发送方重传出现差错的数据; 同时在接收方来不及处理收到的数据时, 及时告知发送方适当降低发送数据的速度.

#### 停止等待协议

只讨论原理, 因此把传送的数据单位都称为分组, 不考虑是在哪个层次上传送的. "停止等待" 就是每发完一个分组就停止发送, 等待对方的确认, 在收到确认后再发送下一个分组.

发送方记为 A, 接收方记为 B.

![](https://shiina18.github.io/assets/posts/images/20201230152212702_8404.png)

出现差错就丢弃,其他什么也不做 (不通知 A). A 发送完一个分组后, 暂时保留副本以备重传, 直到收到确认再清除副本.

![](https://shiina18.github.io/assets/posts/images/20201230153439806_23983.png)

如果 B 收到了分组, 但是发送的确认丢失了. A 在设定的超时重传时间到后重传了分组, B 收到了重复的分组. 此时, B 要丢弃重复的分组, 并向 A 发送确认.

这种可靠传输协议称为自动重传请求 ARQ (automatic repeat request), 即重传的请求是自动进行的.

#### 连续 ARQ 协议

上面的协议显然信道利用率太低.

![](https://shiina18.github.io/assets/posts/images/20201230153821470_23930.png)

位于图中发送窗口内的 5 个分组都可连续发送出去, 而不需要等待对方的确认. 发送方每收到一个确认, 就把发送窗口向前滑动一个分组的位置.

接收方一般采用累积确认的方式. 即不必对收到的分组逐个发送确认, 而是收到几个分组后, 对按序到达的最后一个分组发送确认.

### TCP 报文段的首部

一个 TCP 报文段分为首部和数据两部分. 前 20 字节固定, 后面 4n 个字节按需增加.

![](https://shiina18.github.io/assets/posts/images/20201230154239291_17716.png)

- 序号 (seq). 字节流的每一个字节都按顺序编号. 首部中的序号指的是本报文段数据第一个字节的序号.
- 确认号 (ack). 期望收到对方下一个报文段的第一个数据字节的序号.
- 数据偏移. 首部长度.
- 6 个控制位
    - 紧急 URG (urgent). URG = 1 时, 告诉系统此报文段中有紧急数据, 应尽快传送, 而不要按排队顺序传送 (比如中断命令).
    - 确认 ACK (acknowledgement). 连接建立后所有传送的报文段 ACK = 1.
    - 推送 PSH (push). 一端的应用进程希望在键入一个命令后立即收到对方响应. 此时可令 PSH = 1, 接收方收到时就尽快交付. 很少用.
    - 复位 RST (reset). RST = 1 表明 TCP 连接中出现严重差错, 必须释放连接, 再重新建立连接.
    - 同步 SYN (synchronization). 在连接建立时用来同步序号. 当 SYN = 1, ACK = 0 时, 表明这是一个连接请求报文段. 若对方同意, 则响应报文段使用 SYN = 1, ACK = 1.
    - 终止 FIN (finis). 用来释放一个连接. FIN = 1 表明发送方的数据已发送完毕, 要求释放连接.
- 窗口. 指发送方的接收窗口 (而不是自己的发送窗口). 这是由于接收方的数据缓存空间是有限的. 指出现在允许对方发送的数据量, 动态变化.

### TCP 可靠传输

不妨假定数据传输只在一个方向进行, A 发送, B 确认. 滑动窗口以字节为单位. 假定 A 收到了 B 发来的确认报文段, 确认号为 31 (表明序号直到 30 的数据都收到了).

![](https://shiina18.github.io/assets/posts/images/20201230162658203_31272.png)

TCP 流量控制和拥塞控制略.

### TCP 运输连接管理

运输连接有三个阶段: 连接建立, 数据传送, 连接释放. 

连接建立过程解决三个问题

- 使每一方能确知对方的存在
- 要允许双方协商一些参数
- 能够对运输实体资源 (如缓存大小) 进行分配

主动发起连接的应用进程叫客户 (client), 被动等待连接建立的进程叫服务器 (server).

#### TCP 连接建立

TCP 连接建立的过程叫握手, 需要交换三个 TCP 报文段. 三报文段握手 (three way handshake) 实际是一次握手过程中交换了三个报文段, 而不是进行了三次握手 (handshake 是单数).

![](https://shiina18.github.io/assets/posts/images/20201230165903354_29331.png)

最初两端的 TCP 进程都处于 CLOSED (关闭) 状态. 主机下面的方框表示 TCP 进程所处的状态.

一开始 , B 的 TCP 服务器进程先创建传输控制块 TCB, 进入 LISTEN (收听) 状态, 等待客户的连接请求.

A 的 TCP 客户进程也是先创建传输控制块 TCB, 然后发出连接请求报文段, 首部同步位 SYN = 1, 初始序号 seq = x. SYN 报文段不能携带数据, 但要消耗掉一个序号. 进入 SYN-SENT (同步已发送) 状态.

B 收到连接请求报文段, 如同意连接, 则向 A 发送确认. 确认报文段 SYN = 1, ACK = 1, 确认号是 ack = x+1, 同时也为自己选择一个初始序号 seq = y. 这个报文段也不能携带数据, 但要消耗掉一个序号. 进入 SYN-RCVD (同步收到) 状态.

A 收到 B 的确认后, 还要向 B 给出确认, 报文段 ACK = 1, 确认号 ack = y + 1, 自己的序号 seq = x + 1. ACK 报文段可以携带数据, 但如果不携带数据则不消耗序号 (即下一个数据报文段依然 seq = x+1). 此时 TCP 连接已经建立, 进入 ESTABLISHED 状态.

B 收到 A 的确认后, 也进入 ESTABLISHED 状态.

为什么 A 最后还要发送一次确认? 主要是为了防止已失效的连接请求报文突然又传到了 B (比如之前长时间滞留在半路上), 因而产生错误. 如果 B 收到了已失效的连接请求报文, 直接建立了连接, 那么就会一直干等, 白白浪费了资源

#### TCP 连接释放

四报文握手.

现在 A 和 B 都处于 ESTABLISHED 状态. A 先发出连接释放报文段, 首部 FIN = 1, 序号 seq = u, 为前面传送过的数据的最后一个字节的序号 +1. A 进入 FIN-WAIT-1 状态. 即使 FIN 报文段不携带数据, 也消耗一个序号.

![](https://shiina18.github.io/assets/posts/images/20201230201105367_5830.png)

B 收到连接释放报文段后发出确认, 确认号 ack = u + 1, 自己的序号是 v, 为 B 已经传送过的数据的最后一个字节的序号 +1. B 进入 CLOSE-WAIT 状态. TCP 服务器进程此时通知应用进程, 因而 A 到 B 的连接就释放了, 这时 TCP 连接处于半关闭状态, 即 A 已经没有数据要发送了, 若 B 发送, A 仍要接受.

A 收到确认后, 进入 FIN-WAIT-2 状态.

B 发出连接释放报文段, FIN = 1, ack = u + 1, seq = w (B 可能又发送了一些数据). 进入 LAST-ACK (最后确认) 状态.

A 收到连接释放报文段后, 发出确认, ACK = 1, ack = w + 1, seq = u + 1. 进入 TIME-WAIT (时间等待) 状态. 经过时间等待计时器设置的时间后, A 进入 CLOSED 状态. 

为什么还要等一段时间?

- 保证 A 发送的最后一个 ACK 报文段能够到达 B.
- 防止 "已经失效的连接请求报文段" 出现在本连接中. 下一个新的连接中不会出现旧的连接请求报文段.

## 应用层

### 域名系统 DNS

Domain Name System. 方便把机器名字转换为 IP 地址. 

为什么分组要使用 IP 地址而不使用域名? 因为 IP 地址长度固定, 而域名长度不固定, 机器处理起来比较困难.

域名到 IP 地址的解析 (resolve) 是由分布在互联网上的许多域名服务器程序共同完成的. 当某一个进程需要解析主机名时, 调用解析程序, 称为 DNS 的一个客户, 把待解析的域名放在 DNS 的请求报文中, 以 UDP 用户数据报方式发给本地域名服务器 (用 UDP 目的是减少开销). 本地域名服务器查找域名后, 把对应的 IP 地址放在回答报文中返回. 若本地域名服务器不能回答, 则向其他域名服务器发出查询请求.

任何一个连接在互联网上的主机或路由器, 都有一个唯一的层次结构的名字, 即域名. "域" 是名字空间中一个可被管理的划分. 例如

```
mail.cctv.com
```

最后面的 `com` 是顶级域名, 然后 `cctv` 是二级域名, `mail` 是三级域名. 域名不区分大小写. 通用顶级域名: com (公司企业), net (网络服务机构), org (非营利性组织), edu (美国专用的教育机构, 比如中国的则是 edu.cn), gov (美国的政府部门) 等.

硬件茶谈. (2020, Sep 30).  [【硬件科普】能上 QQ 但是打不开网页? 详解 DNS 服务, DNS 解析, DNS 劫持和污染](https://www.bilibili.com/video/BV1Rp4y1a7xQ). *bilibili*.

### 万维网 WWW

World Wide Web. 万维网是一个分布式的超媒体 (hypermedia) 系统, 是超文本 (hypertext) 系统的扩充. 所谓超文本是指包含指向其他文档的链接的文本. 超媒体则可以包含其他表示形式的信息, 如图像, 声音, 视频等.

万维网以客户服务器方式工作. 需要解决几个问题

- 怎样标志分布在整个互联网上的万维网文档? 同一资源定位符 URL (uniform resource locator).
- 用什么协议实现各种链接? 超文本传送协议 HTTP (hypertext transfer protocol), 通过 TCP 连接进行可靠的传送.
- 怎样使不同风格的文档能在各种主机上显示出来, 同时使用户清楚地知道在什么地方有链接? 超文本标记语言 HTML (hypertext markup language).
- 怎样使用户能够很方便地找到所需的信息? 搜索引擎.

#### URL

URL 是与互联网相连的机器上的任何可访问对象的一个指针. 由四部分组成: 

```
<协议>://<主机>:<端口>/<路径>
```

常用协议 http, https. HTTP 默认端口号是 80, 通常可以省略. 若再省略路径, URL 就指向某个主页 (home page).

#### HTTP

HTTP 定义了浏览器 (即万维网客户进程) 如何向万维网服务器请求万维网文档, 以及服务器怎样把文档传送给浏览器.

- 无连接的. 虽然 HTTP 使用了 TCP 连接, 但通信双方在交换 HTTP 报文前, 不需要先建立 HTTP 连接.
- 无状态的. 同一个客户第二次访问同一个服务器上的页面时, 服务器的相应与第一次被访问时相同 (假设页面没有更新). 这简化了服务器的设计, 使得其支持大量并发请求.

何明科. (2016, Feb 15). [为什么 2015 年底各大网站都纷纷用起了 HTTPS?](https://www.zhihu.com/question/40371841/answer/86265596). *知乎*.

**代理服务器 (proxy server)** 

是一种网络实体, 又称为万维网高速缓存.

![](https://shiina18.github.io/assets/posts/images/20201231103524046_1363.png)

**在服务器上存放用户的信息**

虽然前面提到 HTTP 是无状态的, 但是实际一些网站希望能够识别用户, 这时可以使用 Cookie 来跟踪用户. 这里 Cookie 表示在 HTTP 服务器和客户之间传递的状态信息.

当用户 A 浏览某个使用 Cookie 的网站时, 该网站的服务器就位 A 产生一个唯一的标识码, 并以此作为索引在服务器的后端数据库中产生一个项目. 接着在 A 的 HTTP 响应报文中添加一个叫做 Set-cookie 的首部行. 例如 

```
Set-cookie: 31d4d96e407aad42
```

当 A 收到这个相应时, 浏览器就在它管理的特定 Cookie 文件中添加一行, 包括服务器的主机名和 Set-cookie 后面的识别码. 当 A 继续浏览这个网站时, 每发送一个 HTTP 请求报文, 其浏览器就会从其 Cookie 文件中取出这个网站的识别码, 并放到 HTTP 请求报文的 Cookie 首部行中.

```
Cookie: 31d4d96e407aad42
```

#### HTML

XML (extensible markup language) 是可扩展标记语言, 设计宗旨是传输数据, 而 HTML 则是显示数据. XML 标记由文档的作者定义, 而 HTML 标记是预定义的.

CSS (cascading style sheets) 是层叠样式表, 是一种样式表语言, 用于为 HTML 文档定义布局, 格式化结构化的内容.

上面讨论的都是静态文档. 就是在创作完毕后放在服务器中, 被浏览的过程中, 内容不会改变. 动态文档是动态创建的 (脚本). 脚本指的是一个程序, 它被另一个 (解释) 程序而不是计算机的处理机来解释或执行. 专门的脚本语言有 JavaScript 等, 也可用常见编程语言如 C/C++ 来写脚本.

动态文档一旦建立, 其所包含的信息内容也就固定下来而无法即使刷新屏幕. 有两种技术可用于浏览器屏幕显示的连续更新. 一个是服务器推送, 把所有工作交给服务器, 这显然不好. 另一种是活动文档 (active document), 把所有工作转移给浏览器端, 服务器返回一段活动文档程序副本使该副本在浏览器端运行 (如 Java 等). 

#### 搜索引擎

TecHour官方频道. (2020, Jul 13). [【分享】你真的会用搜索引擎吗? 转发! 99% 的人都不知道的高效搜索引擎使用技巧](https://www.bilibili.com/video/BV1w54y1q7uf). *bilibili*.