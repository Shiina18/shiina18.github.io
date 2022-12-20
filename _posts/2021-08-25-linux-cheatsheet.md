---
title: "Linux cheatsheet (自用)"
categories: Tech
updated: 2022-11-09
comments: true
mathjax: false
---

入门时参考了

- Shotts, W. (2019). [The Linux command line](https://linuxcommand.org/tlcl.php).

可在官网免费下载, 从 09 年开始, 目前已经到了第五版.

<!-- more -->

## 常用命令

看一下 `awk` 和 `rsync`; `top`, `nvidia-smi`.

- 叉烧. (2019). [算法工程师 Linux 必知必会​](https://mp.weixin.qq.com/s/y97ivwbksKNpqiSNFhWJeQ)
- CHRIS HOFFMAN. (2016). [The Linux Directory Structure, Explained](https://www.howtogeek.com/117435/htg-explains-the-linux-directory-structure-explained/)

### kill

> Generally, you should use `kill` before `kill -9` to give the target process a chance to clean up after itself. If you don't give the process a chance to finish what it's doing and clean up, it may leave corrupted files (or other state) around that it won't be able to understand once restarted.

参考 [linux - When should I not kill -9 a process? - Unix & Linux Stack Exchange](https://unix.stackexchange.com/questions/8916/when-should-i-not-kill-9-a-process)

## 训练模型

> The `nohup` command executes another program specified as its argument and ignores all `SIGHUP` (hangup) signals. `SIGHUP` is a signal that is sent to a process when its controlling terminal is closed.
> 
> Usually, when you run a program over SSH, if your connection drops or you log out, the session is terminated, and all the processes executed from the terminal will stop. This is where the `nohup` command comes in handy. It ignores all hangup signals, and the process will continue to run.

```shell
nohup COMMAND [ARGS]
```

通常来说

```shell
nohup python xxx.py -blahblah &
nohup sh xxx.sh -blahblah &
```

默认把输出保存在当前目录的 `nohup.out` 文件中. 最后加上 `&` 使命令立刻在后台运行 (书 Putting a Process in the Background 一节), 会返回一个 pid, 如果忘了也能用 `ps` 查看.

然后可以用

```shell
tail -f nohup.out 
```

查看输出. 默认打印最后 10 行, 加上 `-f` (`--follow`) 表示 output appended data as the file grows.

**参考**

- [Linux Nohup Command \| Linuxize](https://linuxize.com/post/linux-nohup-command/)
- [tail(1) - Linux manual page](https://man7.org/linux/man-pages/man1/tail.1.html)

## 监控显存

```shell
watch -n 1 -d nvidia-smi
```

其中 `-n` (`--interval`) 表示更新间隔, 单位为秒, 默认 2 秒; `-d` (`--difference`) 会高亮变化. 另外, smi 是 system management interface 的缩写.

参考 [Linux Watch Command \| Linuxize](https://linuxize.com/post/linux-watch-command/)

## 运行脚本

在运行脚本前修改权限 (书 Executable Permissions 一节).

```shell
chmod 755 script_filename
```

权限分三组, owner, group, world, 每组三个权限 rwx (read 4, write 2, execute 1), 用二进制表示再写为十进制, 则 7 (111) 就是 rwx, 5 (101) 是 r-x.

然后 for the script to run, we must precede the script name with an explicit path, 原因见书 Script File Location 一节.

```shell
./script_filename
```

## 输出到文件

参考书 Redirecting Standard Output and Standard Error to One File 一节

```shell
blahblah > output_filename.log 2>&1
```

We redirect file descriptor 2 (standard error) to file descriptor 1 (standard output) using the notation `2>&1`. The redirection of standard error must always occur *after* redirecting standard output or it doesn't work, 即 `2>&1 > output_filename.log` 无效.

Recent versions of bash provide a second, more streamlined method for performing this combined redirection shown here

```shell
blahblah &> output_filename.log
blahblah &>> output_filename.log
```

第二行是 append.

## 传输文件

```shell
scp [OPTION] [user@]SRC_HOST:]file1 [user@]DEST_HOST:]file2
```

用 `-r` recursively 传输文件夹.

参考 [How to Use SCP Command to Securely Transfer Files \| Linuxize](https://linuxize.com/post/how-to-use-scp-command-to-securely-transfer-files/)

## 简单 Docker 部署

参见 [Docker 部署简要](https://shiina18.github.io/tech/2022/08/19/docker/).

Docker 简介可参考 [这篇](https://zhuanlan.zhihu.com/p/187505981), 以及 [Docker 底层原理浅析](https://mp.weixin.qq.com/s/0jFHlWAeH5avIO2NLpTmGA).

Docker 教程: [天池](https://tianchi.aliyun.com/competition/entrance/231759/information)

先创建镜像 (image) 文件, 再基于镜像创建进程 (称为容器).

另外参考 [What’s the difference between `up`, `run`, and `start`?](https://docs.docker.com/compose/faq/#whats-the-difference-between-up-run-and-start)

## 杂项

**找到并 kill 相关进程**

```shell
ps aux | grep "$service" | grep -v grep | awk '{print $2}' | xargs kill
```

参考 [SC2009: Consider using `pgrep` instead of grepping `ps` output.](https://github.com/koalaman/shellcheck/wiki/SC2009), 一个更简洁安全的写法是 (另外参考 pkill)

```shell
# When `-f` option is used, the command matches against full argument lists. 
pgrep -f "$service" | xargs kill
```

**查看系统版本**

```shell
cat /etc/os-release
```

**conda**

```shell
conda create --name myenv
conda create -n myenv python=3.8

conda remove --name myenv --all
conda env remove --name myenv
```

## less

相比于 vim, less loads the document a page at a time. 

```shell
# 显示行号
less -N /etc/init/mysql.conf
```

| Shortcuts |                  Action                  |
| --------- | ---------------------------------------- |
| g         | jump to the **beginning** of the file.   |
| G         | end                                      |
| /[string] | search forward for the specified string. |
| n         | **next** match during a search.          |
| N         | previous                                 |


## vim

搜索同 less, `gg` 跳到文件首行, `G` 尾行.

| Shortcuts  |              Action               |
| ---------- | --------------------------------- |
| u          | undo                              |
| Ctrl + r   | redo                              |
| dd         | delete (cut) a line               |
| 2dd 或 d2d | delete (cut) 2 lines              |
| 0          | jump to the **start** of the line |
| $          | jump to the **end** of the line   |

**删除选中的多行**

先 `Shift + v` 进入 visual line 模式, 移动光标选中多行, 再按 `d` 删除选中的多行.

**多行注释**

1. 先 `Ctrl + v` 进入 visual block 模式, 移动光标 (之后会多行同时编辑)
2. `Shift + i` (大写 I) 进入 insert 模式, 输入例如 `#`, 再按 `Esc` 退回普通模式看到效果

**取消多行注释**

同上 step 1 之后, 按 `d` 或 `x` 删除选中行的首字符 (多个字符需要重复多次).

**删除所有**

`gg` + `dG`

**若粘贴的文本被自动注释**

`:set paste` 进入粘贴模式, 再进入 insert 模式

参考 [vimrc - VIM commenting out what I paste - Unix & Linux Stack Exchange](https://unix.stackexchange.com/questions/84639/vim-commenting-out-what-i-paste)