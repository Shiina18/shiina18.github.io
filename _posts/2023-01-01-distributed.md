---
title: "Notes on Distributed Data"
categories: Tech
updated: 
comments: true
mathjax: false
---

- Kleppmann, M. (2017). *Designing data-intensive applications: The big ideas behind reliable, scalable, and maintainable systems*. " O'Reilly Media, Inc.".

There are various reasons why you might want to distribute a database across multiple machines:

- Scalability
- Fault tolerance/high availability
- Latency

## Replication

**Replication** means keeping a copy of the same data on multiple machines that are connected via a network. All of the difficulty in replication lies in handling **changes** to replicated data.

- 使数据和用户地理邻近 (减少延迟)
- 系统部分故障也能继续工作 (提高可用性)
- 横向扩展处理读取请求 (提高读取吞吐量)

> In this chapter we will assume that your dataset is so small that each machine can hold a copy of the entire dataset.

<!-- more -->

### Leaders and Followers

Each node that stores a copy of the database is called a **replica** (副本). Every write to the database needs to be processed by every replica. The most common solution for this is called **leader-based replication** (also known as **active/passive** or **master–slave** replication).

先看单主复制

1. 一个副本为主库, 写入请求只由主库处理.
2. 其他副本为从库, 主库把数据变更发送给所有从库. 每个从库从主库拉取日志, 按照相同顺序写入数据.
3. 客户可以从任意副本读取数据.

![](https://shiina18.github.io/assets/posts/images/517803212239698.png)

<details><summary><b>Implementation of Replication Logs</b><font color="deepskyblue"> (Show more &raquo;)</font></summary>
<p><strong>Statement-based replication</strong></p>
<p>In the simplest case, the leader logs every write request (statement) that it executes and sends that statement log to its followers. For a relational database, this means that every INSERT, UPDATE, or DELETE statement is forwarded to followers, and each follower parses and executes that SQL statement as if it had been received from a client.</p>
<ul>
<li>非确定函数在不同副本上值可能不同.</li>
<li>如果语句中用了自增列, 或者依赖于数据库中的现有数据 (例如 UPDATE ... WHERE ...), 则必须在每个副本上按相同顺序执行语句.</li>
<li>有副作用的语句 (例如, 触发器, 存储过程, 用户定义的函数) 可能在不同副本产生不同副作用.</li>
</ul>
<p><strong>Write-ahead log (WAL) shipping</strong></p>
<p>The log is an append-only sequence of bytes containing all writes to the database. We can use the exact same log to build a replica on another node.</p>
<p>缺点是日志记录的数据非常底层, 导致复制与存储引擎紧密耦合, 主从库上不能运行不同版本的数据库软件.</p>
<p>升级系统时, 希望从库先用更新版本的软件, 升级为主库, 这样系统就不用停机. 但是 WAL 经常要停机升级.</p>
<p><strong>Logical (row-based) log replication</strong></p>
<p>复制日志和存储引擎解耦.</p>
<p><strong>Trigger-based replication</strong></p>
<p>更灵活, 但是更大开销, 更易出错.</p></details>

#### Synchronous Versus Asynchronous Replication

![Follower 1 同步复制, Follower 2 异步复制](https://shiina18.github.io/assets/posts/images/210223912227565.png "Follower 1 同步复制, Follower 2 异步复制")

同步复制保证主从数据一致, 但任何一个节点中断都会导致系统停滞. 实际中的同步复制通常指半同步 (semi-synchronous): **一个** 从库同步, 其他都是异步. 如果同步从库不可用或缓慢, 则使一个异步从库变为同步.

通常主从复制都配置为完全异步, 意味着写入可能丢失.

#### Handling Node Outages

**Follower failure: Catch-up recovery**

On its local disk, each follower keeps a log of the data changes it has received from the leader. 根据日志拉取新的变动即可.

**Leader failure: Failover**

Failover (故障切换): One of the followers needs to be promoted to be the new leader, clients need to be reconfigured to send their writes to the new leader, and the other followers need to start consuming data changes from the new leader. 

1. 确认主库失效. 没有万无一失的方法, 大多只用超时判断.
2. 选择新主库. 选举 (副本多数决), 或者由控制器节点 (controller node) 指定. 最佳候选通常是数据最新的副本.
3. 重新配置系统以启用新主库.

问题

- 如果用异步复制, 新主库可能没有收到老主库宕机前最后的写入. 如果老主库重新加入集群, 新主库可能收到冲突的写入. 
- 在某些情况下, 可能出现两个节点都以为自己是主库的情况, 称为脑裂 (split brain). 如果没有写入冲突解决机制, 可能造成数据丢失.
- 主库宣告死亡的超时时间如何配置? 

这些问题没有简单的解决方案, 所以不少运维团队还是愿意手动执行故障切换.

### Problems with Replication Lag

异步复制下, 主从数据会有一段时间不一致. 但如果停止写入并等待一段 (不确定的) 时间, 主从最终会一致, 称为 **最终一致性** (eventual consistency).

**Reading Your Own Writes**

![读取的副本尚未写入](https://shiina18.github.io/assets/posts/images/549360614247731.png "读取的副本尚未写入")

一些解决方案

- When reading something that the user may have modified, read it from the leader; otherwise, read it from a follower. 比如从主库读取用户自己的档案 (因为只有用户自己能编辑), 在从库读取其他用户的档案.
- 其他标准例如在上次更新后的一分钟内从主库读.
- 客户端记住最后写入的时间戳, 保证从库更新到这个时间戳.

一种复杂情况是: 同一用户从多个设备请求服务. 略.

**Monotonic Reads**

![第一次读取的副本已写入, 第二次读取的副本尚未写入, 时光倒流](https://shiina18.github.io/assets/posts/images/55491214240400.png "第一次读取的副本已写入, 第二次读取的副本尚未写入, 时光倒流")

例如, 可以基于用户 ID 的 hash 选择副本, 确保每个用户从同一个副本读取.

**Consistent Prefix Reads**

![写入 AB, 读出 BA, 违反因果律](https://shiina18.github.io/assets/posts/images/88101614236955.png "写入 AB, 读出 BA, 违反因果律")

This is a particular problem in partitioned (sharded) databases. In many distributed databases, different partitions operate independently, so there is **no global ordering of writes**.

One solution is to make sure that any writes that are causally related to each other are written to the same partition—but in some applications that cannot be done efficiently.

### Multi-Leader Replication

We call this a **multi-leader** configuration (also known as **master–master** or **active/active** replication). In this setup, each leader simultaneously acts as a follower to the other leaders.

**Use Cases for Multi-Leader Replication**

- Multi-datacenter operation
- Clients with offline operation. 比如离线笔记, 在线同步, 每个设备都是一个 "数据中心".
- Collaborative editing.

**Handling Write Conflicts**

- **Conflict avoidance.** The simplest strategy for dealing with conflicts is to avoid them: if the application can ensure that all writes for a particular record go through the same leader, then conflicts cannot occur.
- **Converging toward a consistent state.** In a multi-leader configuration, there is no defined ordering of writes, so it's not clear what the final value should be. 办法略.

### Leaderless Replication

允许任何副本接受客户端的写入请求. 客户端发送每个写入请求到若干节点, 并从多个节点并行读取, 以检测和纠正具有陈旧数据的节点.

> The idea was mostly forgotten during the era of dominance of relational databases. It once again became a fashionable architecture for databases after Amazon used it for its in-house *Dynamo* system.

略.

## Partitioning

For very large datasets, or very high query throughput, replication is not sufficient: we need to break the data up into **partitions**, also known as **sharding**. The main reason for wanting to partition data is scalability.

Normally, partitions are defined in such a way that each piece of data (each record, row, or document) belongs to exactly one partition. 

### Partitioning and Replication

Partitioning is usually combined with replication so that copies of each partition are stored on multiple nodes. A node may store more than one partition. 

![](https://shiina18.github.io/assets/posts/images/449024715232709.png)

> The choice of partitioning scheme is mostly independent of the choice of replication scheme, so we will keep things simple and ignore replication in this chapter.

### Partitioning of Key-Value Data

Our goal with partitioning is to spread the data and the query load evenly across nodes. 不均匀则称为偏斜 (skew), 极端不均匀导致的高负载分区称为热点 (hot spot).

**Partitioning by Key Range**

![](https://shiina18.github.io/assets/posts/images/14285115250589.png)

The downside of key range partitioning is that certain access patterns can lead to hot spots. If the key is a timestamp, then the partitions correspond to ranges of time—e.g., one partition per day. Unfortunately, because we write data from the sensors to the database as the measurements happen, all the writes end up going to the same partition (the one for today), so that partition can be overloaded with writes while others sit idle. 可以给时间戳 key 加上 sensor name 的前缀.

**Partitioning by Hash of Key**

By using the hash of the key for partitioning we lose a nice property of key-range partitioning: the ability to do efficient range queries. 

**Skewed Workloads and Relieving Hot Spots**

Hash 分区可以帮助减少热点. 但极端情况下, 所有读写针对同一个 key, 所有请求都路由到同一个分区. 比如百万粉丝的名人做一个操作.

大多数系统无法自动处理这种高度偏斜的负载, 需要依靠应用程序. 比如在主键开头或末尾添加随机数.

次级索引分区: 略.

### Rebalancing Partitions

- 查询吞吐量增加, 添加 CPU 处理负载.
- 数据集增大, 添加磁盘和 RAM 存储.
- 机器故障, 其他机器接管故障机器的任务.

将负载从集群中的一个节点向另一个节点移动的过程称为 **再平衡** (rebalancing). 

最低要求

- 再平衡后各节点负载均衡.
- 再平衡时, 数据库可以继续接受读写请求.
- 只移动必要的数据, 以便快速再平衡, 减少网络和磁盘 IO 负载.

#### Strategies for Rebalancing

**How not to do it: hash mod N**

The problem with the mod N approach is that if the number of nodes N changes, most of the keys will need to be moved from one node to another. 

**Fixed number of partitions**

![](https://shiina18.github.io/assets/posts/images/292071816248193.png)

A fairly simple solution: create many more partitions than there are nodes, and assign several partitions to each node.

Only entire partitions are moved between nodes. The number of partitions does not change, nor does the assignment of keys to partitions. The only thing that changes is the assignment of partitions to nodes. 

**Dynamic partitioning**

For databases that use key range partitioning, a fixed number of partitions with fixed boundaries would be very inconvenient: if you got the boundaries wrong, you could end up with all of the data in one partition. (hash 分区也可以动态分区)

For that reason, key range–partitioned databases such as HBase and RethinkDB create partitions dynamically. 过大就分裂, 过小就合并.

**Partitioning proportionally to nodes**

Have a fixed number of partitions per node.

### Request Routing

This is an instance of a more general problem called **service discovery**, which isn't limited to just databases.

![](https://shiina18.github.io/assets/posts/images/528915516245695.png)

On a high level, there are a few different approaches to this problem:

1. 允许客户端访问任意节点 (比如轮询), 有节点负责查询数据.
2. 把所有客户端请求发送到路由层, 由路由层决定请求发给哪个节点.
3. 客户端知道应该去哪个节点读数据.

In all cases, the key problem is: how does the component making the routing decision learn about changes in the assignment of partitions to nodes?

Many distributed data systems rely on a separate coordination service such as ZooKeeper to keep track of this cluster metadata.

![](https://shiina18.github.io/assets/posts/images/421123817226936.png)

## Transactions

A transaction is a way for an application to group several reads and writes together into a logical unit. Conceptually, all the reads and writes in a transaction are executed as one operation: either the entire transaction succeeds (commit) or it fails (abort, rollback). 

### The Meaning of ACID

In practice, one database's implementation of ACID does not equal another's implementation. ACID has unfortunately become mostly a marketing term.

- **Atomicity.** The ability to abort a transaction on error and have all writes from that transaction discarded is the defining feature of ACID atomicity. Perhaps abortability would have been a better term than atomicity.
- **Consistency.** The idea of ACID consistency is that you have certain statements about your data (invariants) that must always be true. However, this idea of consistency depends on the application's notion of invariants, and it's the application's responsibility to define its transactions correctly so that they preserve consistency.
- **Isolation.** Isolation in the sense of ACID means that concurrently executing transactions are isolated from each other: they cannot step on each other's toes. 
- **Durability.** Durability is the promise that once a transaction has committed successfully, any data it has written will not be forgotten, even if there is a hardware fault or the database crashes.

ACID 的原子性和隔离性假设用户想同时修改多个对象 (行, 文档, 记录), 需要 **多对象事务** 保持多块数据保持同步. 

### Weak Isolation Levels

**Serializable** isolation means that the database guarantees that transactions have the same effect as if they ran serially (i.e., one at a time, without any concurrency). 可串行的隔离有损性能, 因此很多数据库选择更弱的隔离级别.

#### Read Committed

两个保证

1. 只能读到已提交的数据 (没有脏读 (dirty read))
2. 只会覆盖已写入的数据 (没有脏写 (dirty write))

**Implementing read committed**
  
Most commonly, databases prevent dirty writes by using row-level locks.

How do we prevent dirty reads? The approach of requiring read locks does not work well in practice, because one long-running write transaction can force many read-only transactions to wait until the long-running transaction has completed. 所以大多数数据库都会记住旧值和由当前持有写入锁的事务设置的新值, 在事务提前只能读到旧值.

#### Snapshot Isolation and Repeatable Read

![](https://shiina18.github.io/assets/posts/images/528263611234928.png)

在读已提交的隔离条件下, 可能出现不可重复读 (nonrepeatable read) 或者称为读取偏差 (read skew).

**Snapshot isolation** is the most common solution to this problem. The idea is that each transaction reads from a **consistent snapshot** of the database—that is, the transaction sees all the data that was committed in the database at the start of the transaction.

**Implementing snapshot isolation**

同样地, 用写锁防止脏写. 但是读取不需要锁. 从性能来看, 快照隔离的关键原则是: 读不阻塞写, 写不阻塞读.

数据库需要同时维护单个对象的多个版本, 这种技术称为多版本并发控制 (MVCC, multi-version concurrency control).

> Snapshot isolation is a useful isolation level, especially for read-only transactions. However, many databases that implement it call it by different names. In Oracle it is called serializable, and in PostgreSQL and MySQL it is called repeatable read.
>
> The reason for this naming confusion is that the SQL standard doesn't have the concept of snapshot isolation at that time. To make matters worse, the SQL standard's definition of isolation levels is flawed—it is ambiguous, imprecise. Even though several databases implement repeatable read, there are big differences in the guarantees they actually provide.

#### Preventing Lost Updates

Example: two concurrent counter increments

- **Atomic write operations**
- **Explicit locking.** 如果没有对应的原子操作, 就先锁定要更新的对象, 然后执行读取-修改-写入.
- **Automatically detecting lost updates.** An advantage of this approach is that databases can perform this check efficiently in conjunction with snapshot isolation. 
- **Compare-and-set.** In databases that don't provide transactions, you sometimes find an atomic compare-and-set operation. It allows an update to happen only if the value has not changed since you last read it.
- **Conflict resolution and replication.** Locks and compare-and-set operations assume that there is a single up-to-date copy of the data. However, databases with multi-leader or leaderless replication usually allow several writes to happen concurrently and replicate them asynchronously, so they cannot guarantee that there is a single up-to-date copy of the data.

接最后一点. A common approach in such replicated databases is to allow concurrent writes to create several conflicting versions of a value, and to use application code or special data structures to resolve and merge these versions after the fact.

Atomic operations can work well in a replicated context. On the other hand, the **last write wins** (LWW) conflict resolution method is prone to lost updates. Unfortunately, LWW is the default in many replicated databases.

#### Write Skew and Phantoms

例子: 两个人值班, 只要有一个人在岗另一个人就能请假. 当两个人同时决定请假时 (两个并发事务), 从快照读到两个人都在岗, 因此批准了两人请假, 结果没人值班了. 另外比如预定会议室的场景. 快照隔离级别不能防止这种问题.

This anomaly is called **write skew**. The anomalous behavior was only possible because the transactions ran concurrently. Write skew can occur if two transactions read the same objects, and then update some of those objects (different transactions may update different objects).

**Phantoms causing write skew**

All of these examples follow a similar pattern:

1. A SELECT query checks whether some requirement is satisfied by searching for rows that match some search condition.
2. Depending on the result of the first query, the application code decides how to continue.
3. If the application decides to go ahead, it makes a write to the database and commits the transaction. The effect of this write changes the precondition of the decision of step 2.

This effect, where a write in one transaction changes the result of a search query in another transaction, is called a **phantom** (幻读). Snapshot isolation avoids phantoms in read-only queries.

### Serializability

Serializable isolation is usually regarded as the strongest isolation level. It guarantees that even though transactions may execute in parallel, the end result is the same as if they had executed one at a time, serially, without any concurrency. 

Most databases that provide serializability today use one of three techniques as disscussed below.

#### Actual Serial Execution

完全去掉并发, 单线程顺序执行. Serial execution of transactions has become a viable way of achieving serializable isolation within certain constraints:

- 每个事务都小而快.
- It is limited to use cases where the active dataset can fit in memory. 
- 写入吞吐量必须低到能在单个 CPU 核上处理.
- Cross-partition transactions are possible, but there is a hard limit to the extent to which they can be used.

#### Two-Phase Locking (2PL)

比普通的写锁要求更严格. Several transactions are allowed to concurrently read the same object as long as nobody is writing to it. But as soon as anyone wants to write (modify or delete) an object, exclusive access is required:

- If transaction A has read an object and transaction B wants to write to that object, B must wait until A commits or aborts before it can continue. 
- If transaction A has written an object and transaction B wants to read that object, B must wait until A commits or aborts before it can continue. 

最大问题是性能差: 写入会阻塞其他读写, 读取也会阻塞写入. 这和快照隔离的要求截然相反.

两阶段意思是, 第一阶段 (事务执行时) 获取锁, 第二阶段 (事务结束时) 释放锁.

#### Serializable Snapshot Isolation (SSI)

略

## The Trouble with Distributed Systems

> We will now turn our pessimism to the maximum and assume that anything that can go wrong will go wrong.

### Faults and Partial Failures

In a distributed system, there may well be some parts of the system that are broken in some unpredictable way, even though other parts of the system are working fine. This is known as a **partial failure**. The difficulty is that partial failures are **nondeterministic**: if you try to do anything involving multiple nodes and the network, it may sometimes work and sometimes unpredictably fail. As we shall see, you may not even *know* whether something succeeded or not, as the time it takes for a message to travel across a network is also nondeterministic!

We need to build a reliable system from unreliable components. 比如互联网协议 (IP) 不可靠, 但是 TCP 在 IP 之上提供了更可靠的传输层.

### Unreliable Networks

The distributed systems we focus on in this book are shared-nothing systems: i.e., a bunch of machines connected by a network. The network is the only way those machines can communicate.

The internet and most internal networks in datacenters (often Ethernet) are **asynchronous packet networks**. In this kind of network, one node can send a message (a packet) to another node, but the network gives **no guarantees as to when it will arrive, or whether it will arrive at all**.

The usual way of handling this issue is a **timeout**: after some time you give up waiting and assume that the response is not going to arrive.

### Unreliable Clocks

Each machine on the network has its own clock, which is an actual hardware device: usually a quartz crystal oscillator. It is possible to synchronize clocks to some degree: the most commonly used mechanism is the Network Time Protocol (NTP), which allows the computer clock to be adjusted according to the time reported by a group of servers. The servers in turn get their time from a more accurate time source, such as a GPS receiver.

**Monotonic Versus Time-of-Day Clocks**

A time-of-day clock does what you intuitively expect of a clock: it returns the current date and time according to some calendar (also known as **wall-clock time**). 

Time-of-day clocks are usually synchronized with NTP. If the local clock is too far ahead of the NTP server, it may be forcibly reset and appear to **jump back to a previous point in time**. These jumps, as well as the fact that they often ignore leap seconds (闰秒), make time-of-day clocks **unsuitable for measuring elapsed time**.

A monotonic clock is **suitable for measuring a duration** (time interval), such as a timeout or a service's response time. The name comes from the fact that they are guaranteed to always move forward. However, the absolute value of the clock is meaningless. 比 NTP 时间快或慢时, 会微调单调时钟的速度.

时钟读数不是准确值, 存在置信区间.

![不能依赖时间戳排序](https://shiina18.github.io/assets/posts/images/371013921249376.png "不能依赖时间戳排序")

### Knowledge, Truth, and Lies

#### The Truth Is Defined by the Majority

Many distributed algorithms rely on a **quorum**, that is, voting among the nodes: decisions require some minimum number of votes from several nodes in order to reduce the dependence on any one particular node.

**The leader and the lock**

Frequently, a system requires there to be only one of some thing.

- Only one node is allowed to be the leader for a database partition, to avoid split brain.
- Only one transaction or client is allowed to hold the lock for a particular resource or object, to prevent concurrently writing to it and corrupting it.
- Only one user is allowed to register a particular username, because a username must uniquely identify a user.

![](https://shiina18.github.io/assets/posts/images/225535521244512.png)

上图中 Client 1 由于 stop-the-world garbage collector (有时候 GC 需要停止所有运行的线程) 停止了一段时间, 回来后依然以为自己持有锁 (需要等下次检测才知道锁没了), 结果执行了不安全的写入.

**Fencing tokens**

![](https://shiina18.github.io/assets/posts/images/458580322238058.png)

<details><summary><b>Byzantine Faults</b><font color="deepskyblue"> (Show more &raquo;)</font></summary>
<p>If the node deliberately wanted to subvert the system's guarantees, it could easily do so by sending messages with a fake fencing token.</p>
<p>Distributed systems problems become much harder if there is a risk that nodes may "lie" (send arbitrary faulty or corrupted responses). Such behavior is known as a <strong>Byzantine fault</strong>, and the problem of reaching consensus in this untrusting environment is known as the <strong>Byzantine Generals Problem</strong>.</p>
<p>This concern is relevant in certain specific circumstances.</p>
<ul>
<li>In aerospace environments, the data in a computer's memory or CPU register could become corrupted by radiation, and a system failure would be very expensive.</li>
<li>In a system with multiple participating organizations, some participants may attempt to cheat or defraud others.</li>
</ul>
<p>However, in the kinds of systems we discuss in this book, we can usually safely assume that there are no Byzantine faults.</p></details>

## Consistency and Consensus

One of the most important abstractions for distributed systems is **consensus**: that is, getting all of the nodes to agree on something. 

### Consistency Guarantees

最终一致性一个更好的名字可能是收敛 (convergence). 这是很弱的保证, 没有说什么时候收敛.

### Linearizability

The basic idea is to make a system appear as if there were only one copy of the data, and all operations on it are atomic.

This is the idea behind **linearizability** (线性一致性) (also known as atomic consistency, **strong consistency** (强一致性), immediate consistency, or external consistency).

![](https://shiina18.github.io/assets/posts/images/270862922231192.png)

矩形左边是请求发送时刻, 右边是客户端收到响应的时刻.

![](https://shiina18.github.io/assets/posts/images/560202922221722.png)

![](https://shiina18.github.io/assets/posts/images/381573322224226.png)

#### Relying on Linearizability

**Locking and leader election**

单主复制的系统要保证主库只有一个. 一种选举主库的方式是用锁: 每个节点启动时尝试获取锁, 成功者称为主库. 锁必须强一致: 所有节点必须就哪个节点拥有锁达成一致.

**Constraints and uniqueness guarantees**

唯一性约束在数据库很常见: 比如用户名或电子邮件地址. 如果要在写入数据时执行此约束, 则需要强一致性.

**Cross-channel timing dependencies**

![](https://shiina18.github.io/assets/posts/images/527574122233173.png)

用户传图看缩略图. 如果文件存储服务不是强一直的, 缩小图片的指令 (上图 3 和 4) 可能比图片存储快 (上图 2), image resizer 可能看到 (上图 5) 图片的旧版, 生成旧版缩略图.

#### Implementing Linearizable Systems

- 单主复制 (可能强一致)
- 共识算法 (强一致), 比如 ZooKeeper
- 多主复制 (非强一致)
- 无主复制 (不一定)

#### The Cost of Linearizability

**The CAP theorem**  

Thus, applications that don't require linearizability can be more tolerant of network problems. This insight is popularly known as the CAP theorem. CAP was originally proposed as a rule of thumb, without precise definitions, with the goal of starting a discussion about trade-offs in databases.

> CAP is sometimes presented as **Consistency, Availability, Partition tolerance: pick 2 out of 3.** Unfortunately, putting it this way is misleading because network partitions (where nodes that are alive but disconnected from each other) are a kind of fault, so they aren't something about which you have a choice: they will happen whether you like it or not.
> 
> At times when the network is working correctly, a system can provide both consistency (linearizability) and total availability. When a network fault occurs, you have to choose between either linearizability or total availability. Thus, a better way of phrasing CAP would be **either Consistent or Available when Partitioned**.
>
> In discussions of CAP there are several contradictory definitions of the term availability. **All in all, there is a lot of misunderstanding and confusion around CAP, and it does not help us understand systems better, so CAP is best avoided**.

> There are many more interesting impossibility results in distributed systems, and CAP has now been superseded by more precise results, so it is of mostly historical interest today.

**Linearizability and network delays**

Although linearizability is a useful guarantee, surprisingly few systems are actually linearizable in practice. For example, even RAM on a modern multi-core CPU is not linearizable.

The same is true of many distributed databases that choose not to provide linearizable guarantees: they do so primarily to increase performance, not so much for fault tolerance.

### Ordering Guarantees

**The causal order is not a total order.** 因果顺序不是全序.

- 强一致性 (线性一致性): 操作是全序的
- 因果性: 没有因果顺序的操作是并发的

**Linearizability is stronger than causal consistency**

许多情况下, 看上去需要线性一致性的系统实际只需要因果一致性.

#### Sequence Number Ordering

Although causality is an important theoretical concept, actually keeping track of all causal dependencies can become impractical. There is a better way: we can use **sequence numbers** or **timestamps** to order events. A timestamp can come from a **logical clock**, which is an algorithm to generate a sequence of numbers to identify operations, typically using counters that are incremented for every operation.

**Lamport timestamps**

There is actually a simple method for generating sequence numbers that is consistent with causality.

Each node has a unique identifier, and each node keeps a counter of the number of operations it has processed. The Lamport timestamp is then simply a pair of (counter, node ID).

![](https://shiina18.github.io/assets/posts/images/37771013235537.png)

A Lamport timestamp bears no relationship to a physical time-of-day clock, but it provides total ordering: if you have two timestamps, the one with a greater counter value is the greater timestamp; if the counter values are the same, the one with the greater node ID is the greater timestamp.

The key idea about Lamport timestamps, which makes them consistent with causality, is the following: every node and every client keeps track of the maximum counter value it has seen so far, and includes that maximum on every request. When a node receives a request or response with a maximum counter value greater than its own counter value, it immediately increases its own counter to that maximum.

**Timestamp ordering is not sufficient**

The problem is that the total order of operations only emerges after you have collected all of the operations. If another node has generated some operations, but you don't yet know what they are, you cannot construct the final ordering of operations. 比如一个操作需要马上响应 (两个人同时注册相同用户名), 但是我们无法马上知道它在全序操作中到底排在哪里 (到底谁先注册). It's not sufficient to have a total ordering of operations—you also need to know when that order is finalized. 

#### Total Order Broadcast

Single-leader replication determines a total order of operations by choosing one node as the leader and sequencing all operations on a single CPU core on the leader. The challenge then is how to scale the system if the throughput is greater than a single leader can handle, and also how to handle failover if the leader fails. In the distributed systems literature, this problem is known as **total order broadcast** or **atomic broadcast**.

Informally, it requires that two safety properties always be satisfied:

- Reliable delivery. No messages are lost: if a message is delivered to one node, it is delivered to all nodes.
- Totally ordered delivery. Messages are delivered to every node in the same order.

### Distributed Transactions and Consensus

**Atomic commit:** In a database that supports transactions spanning several nodes or partitions, we have the problem that a transaction may fail on some nodes but succeed on others. If we want to maintain transaction atomicity, we have to get all nodes to agree on the outcome of the transaction: either they all abort/roll back or they all commit.

In particular, we will discuss the two-phase commit (2PC) algorithm, which is the most common way of solving atomic commit and which is implemented in various databases, messaging systems, and application servers. It turns out that 2PC is a kind of consensus algorithm—but not a very good one. By learning from 2PC we will then work our way toward better consensus algorithms, such as those used in ZooKeeper.

#### Atomic Commit and Two-Phase Commit (2PC)

![](https://shiina18.github.io/assets/posts/images/232480015262492.png)

2PC uses a new component that does not normally appear in single-node transactions: a **coordinator** (also known as **transaction manager**). 

We call these database nodes **participants** in the transaction. When the application is ready to commit, the coordinator begins phase 1: it sends a **prepare** request to each of the nodes, asking them whether they are able to
commit. The coordinator then tracks the responses from the participants:

- If all participants reply "yes," indicating they are ready to commit, then the coordinator sends out a **commit** request in phase 2, and the commit actually takes place.
- If any of the participants replies "no," the coordinator sends an **abort** request to all nodes in phase 2.

**A system of promises**

From this short description it might not be clear why two-phase commit ensures atomicity, while one-phase commit across several nodes does not.

1. When the application wants to begin a distributed transaction, it requests a transaction ID from the coordinator. **This transaction ID is globally unique.**
2. The application begins a single-node transaction on each of the participants, and attaches the globally unique transaction ID to the single-node transaction. All reads and writes are done in one of these single-node transactions.
3. When the application is ready to commit, the coordinator sends a prepare request to all participants, tagged with the global transaction ID.
4. When a participant receives the prepare request, **it makes sure that it can definitely commit the transaction under all circumstances**.
5. When the coordinator has received responses to all prepare requests, it makes a definitive decision on whether to commit or abort the transaction.  The coordinator must write that decision to its transaction log on disk so that it knows which way it decided in case it subsequently crashes. This is called the **commit point**.
6. Once the coordinator's decision has been written to disk, the commit or abort request is sent to all participants. If this request fails or times out, **the coordinator must retry forever until it succeeds**. 

**Three-phase commit**

Two-phase commit is called a **blocking** atomic commit protocol due to the fact that 2PC can become stuck waiting for the coordinator to recover. 

As an alternative to 2PC, an algorithm called three-phase commit (3PC) has been proposed. However, 3PC assumes a network with bounded delay and nodes with bounded response times. 不实际

### Distributed Transactions in Practice

Distributed transactions in MySQL are reported to be over 10 times slower than single-node transactions, so it is not surprising when people advise against using them. Much of the performance cost inherent in two-phase commit is due to the additional disk forcing (fsync) that is required for crash recovery, and the additional network round-trips.

Two quite different types of distributed transactions are often conflated:

- Database-internal distributed transactions. 所有参与事务的节点都运行相同的数据库软件.
- Heterogeneous distributed transactions. 参与者运行不同数据库软件, 甚至是非数据库系统 (如消息代理).

### Fault-Tolerant Consensus

Informally, consensus means getting several nodes to agree on something. The consensus problem is normally formalized as follows: one or more nodes may *propose* values, and the consensus algorithm *decides* on one of those values.

要求

- Uniform agreement. No two nodes decide differently.
- Integrity. No node decides twice.
- Validity. If a node decides value v, then v was proposed by some node.
- Termination. Every node that does not crash eventually decides some value. 

The uniform agreement and integrity properties define the core idea of consensus: everyone decides on the same outcome, and once you have decided, you cannot change your mind. 

其他略.