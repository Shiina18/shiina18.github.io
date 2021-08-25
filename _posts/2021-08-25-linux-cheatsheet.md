---
title: "Linux cheatsheet (自用)"
categories: Tech
updated: 
comments: true
mathjax: false
---

入门时参考了

- Shotts, W. (2019). [The Linux command line](https://linuxcommand.org/tlcl.php).

可在官网免费下载, 从 09 年开始, 目前已经到了第五版.

<!-- more -->


## 训练模型

> The `nohup` command executes another program specified as its argument and ignores all `SIGHUP` (hangup) signals. `SIGHUP` is a signal that is sent to a process when its controlling terminal is closed.
> 
> Usually, when you run a program over SSH, if your connection drops or you log out, the session is terminated, and all the processes executed from the terminal will stop. This is where the `nohup` command comes in handy. It ignores all hangup signals, and the process will continue to run.

```
nohup COMMAND [ARGS]
```

通常来说

```
nohup python xxx.py -blahblah &
```

默认把输出保存在当前目录的 `nohup.out` 文件中. 最后加上 `&` 使命令立刻在后台运行 (书 Putting a Process in the Background 一节), 会返回一个 pid, 如果忘了也能用 `ps` 查看.

然后可以用

```
tail -f nohup.out 
```

查看输出. 默认打印最后 10 行, 加上 `-f` (`--follow`) 表示 output appended data as the file grows.

**参考**

- [Linux Nohup Command \| Linuxize](https://linuxize.com/post/linux-nohup-command/)
- [tail(1) - Linux manual page](https://man7.org/linux/man-pages/man1/tail.1.html)

## 运行脚本

在运行脚本前修改权限 (书 Executable Permissions 一节).

```
chmod 755 script_filename
```

权限分三组, owner, group, world, 每组三个权限 rwx (read 4, write 2, execute 1), 用二进制表示则 7 就是 rwx, 5 是 r-x.

然后 for the script to run, we must precede the script name with an explicit path, 原因见书 Script File Location 一节.

```
./script_filename
```

## 监控显存

```
watch -n 1 -d nvidia-smi
```

其中 `-n` (`--interval`) 表示更新间隔, 单位为秒, 默认 2 秒; `-d` (`--difference`) 会高亮变化. 另外, smi 是 system management interface 的缩写.

参考 [Linux Watch Command \| Linuxize](https://linuxize.com/post/linux-watch-command/)

## 传输文件

```
scp [OPTION] [user@]SRC_HOST:]file1 [user@]DEST_HOST:]file2
```

参考 [How to Use SCP Command to Securely Transfer Files \| Linuxize](https://linuxize.com/post/how-to-use-scp-command-to-securely-transfer-files/)

## 简单 Docker 部署

Docker 简介可参考 [这篇](https://zhuanlan.zhihu.com/p/187505981), 以及 [Docker 底层原理浅析](https://mp.weixin.qq.com/s/0jFHlWAeH5avIO2NLpTmGA).

先创建镜像 (image) 文件, 再基于镜像创建进程 (称为容器).

查看进程 (容器)

```
docker ps
```

Cheatsheet

```
docker-compose build
docker-compose stop
docker-compose up -d
```

其中 `-d` (`--detach`) Detached mode: Run containers in the background, print new container names.

另外参考 [What’s the difference between `up`, `run`, and `start`?](https://docs.docker.com/compose/faq/#whats-the-difference-between-up-run-and-start)