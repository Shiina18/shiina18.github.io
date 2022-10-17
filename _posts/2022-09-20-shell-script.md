---
title: "Shell 脚本简要"
categories: Language
updated: 2022-10-13
comments: true
mathjax: false
---

主要参考

- Shotts, W. (2019). [The Linux command line](https://linuxcommand.org/tlcl.php)

学习目标: 能写简单脚本, 能看懂长一些的脚本. Shell 脚本不是开发语言, 难以 debug, 不适合写太长.

> If you are writing a script that is more than 100 lines long, or that uses non-straightforward control flow logic, you should rewrite it in a more structured language *now*. Bear in mind that scripts grow. Rewrite your script early to avoid a more time-consuming rewrite at a later date. (Google Shell Style Guide)

<!-- more -->

## Hello world

### 1. 编写脚本

新建 `hello_world` 文件.

```shell
#!/bin/bash

echo 'Hello world!'  # this is a comment
```

**注释** 的语法和 Python 单行注释相同, 当前行 `#` 后面的内容视为注释.

以 `#!` 开头的第一行称为 **shebang**, 告诉系统用什么解释器执行该脚本. 

<details><summary><b>shebang 可以不写</b><font color="deepskyblue"> (Show more &raquo;)</font></summary>
<p>以 <code>./hello_world</code> 执行时, usually the parent shell guesses that the script is written for the same shell (minimal Bourne-like shells run the script with <code>/bin/sh</code>, bash runs it as a bash subprocess). <font color="lightgrey">(The fact that a program can launch other programs is expressed in the process scheme as a <em>parent process</em> producing a <em>child process</em>.)</font></p>
<p>另外也可以指定解释器执行, 比如 <code>bash hello_world</code>, <code>python main.py</code>.</p>
<ul>
<li><a href="https://stackoverflow.com/questions/12296308/shell-script-working-fine-without-shebang-line-why">linux - Shell script working fine without shebang line? Why? - Stack Overflow</a></li>
</ul></details>

<details><summary><b>sh, bash and dash</b><font color="deepskyblue"> (Show more &raquo;)</font></summary>
<p>The name "bash" is an acronym for "Bourne Again SHell", a reference to the fact <code>bash</code> is an enhanced replacement for <code>sh</code>, the original Unix shell program written by Steve Bourne.</p>
<p>注意现在一般 <code>/bin/sh</code> 软链接到 dash 而不是 bash (以前是). 但默认的 login shell 还是 bash.</p>
<ul>
<li><a href="https://askubuntu.com/questions/141928/what-is-the-difference-between-bin-sh-and-bin-bash">scripts - What is the difference between #!/bin/sh and #!/bin/bash? - Ask Ubuntu</a></li>
</ul></details>

### 2. 使文件可执行

```shell
$ chmod 755 hello_world
```

默认自己只有读写权限 (`rw-`).  注意可读权限是程序可执行的必要条件, 所以让别人可执行要给 5 (`r-x`).

### 3. 将文件放在 shell 可以找到的路径下

```shell
$ ./hello_world
```

如果写成 

```shell
$ hello_world
```

会报错. 因为如果不显式指定路径, shell 只在环境变量 `PATH` 所包含的路径下搜索可执行文件. PATH 默认包括了 `/bin`, 和 `/home/me/bin` (创建 `~/bin` 目录后重启 shell, 系统一般会自动添加该路径到 PATH) 等.

<details><summary><b>Good Locations for Scripts</b><font color="deepskyblue"> (Show more &raquo;)</font></summary>
<p>The <code>~/bin</code> directory is a good place to put scripts intended for personal use. If we write  a script that everyone on a system is allowed to use, the traditional location is <code>/usr/local/bin</code>. Scripts intended for use by the system administrator are often located in <code>/usr/local/sbin</code>. In most cases, locally supplied software, whether scripts or compiled programs, should be placed in the <code>/usr/local</code> hierarchy and not in <code>/bin</code> or <code>/usr/bin</code>. These directories are specified by the Linux Filesystem Hierarchy Standard to contain only files supplied and maintained by the Linux distributor.</p>
<ul>
<li>usr = User System Resources</li>
<li>sbin: binaries with superuser (root) privileges required</li>
<li><a href="https://askubuntu.com/questions/308045/differences-between-bin-sbin-usr-bin-usr-sbin-usr-local-bin-usr-local">command line - Differences between /bin, /sbin, /usr/bin, /usr/sbin, /usr/local/bin, /usr/local/sbin - Ask Ubuntu</a></li>
</ul></details>

## 变量

```shell
a=233 TITLE="System Information Report For $HOSTNAME"
b=
d="$(ls -l foo.txt)"  # results of a command
# 可以写成 d=`ls -l foo.txt` 但不推荐
e=$((5 * 7))  # arithmetic expansion
f="\t\ta string\n"  # escape

echo "<html>
    <head><title>${TITLE}</title></head>
    <body><h1>${TITLE}</h1></body>
</html>"
```

- 变量名规则同 Python. 习惯用大写字母表示常量, 小写字表示变量.
- 赋值 `=` 两侧不能有空格. 一行可以多次赋值.
- shell 不区分变量类型, 都视为字符串.
- 单引号不做 string interpolation, 双引号做, 参考 [这里](https://stackoverflow.com/questions/6697753/difference-between-single-and-double-quotes-in-bash).
- `${}` 称为 parameter substitution/expansion (双引号内生效), 类似 Python 的 f-string, 把字符串里面的占位符替换成对应值. 其中 `{}` 可写可不写, 最好写上避免歧义. `$()` 称为 command substitution, 见 [这里](https://superuser.com/questions/935374/difference-between-and-in-a-shell-script). 单纯的圆括号 `()` 表示 subshell.
- 用 `"` 可以写多行字符串. 另外同 Python, 在行末尾写 `\` 为 line continuation.
- [Double quote to prevent globbing and word splitting.](https://github.com/koalaman/shellcheck/wiki/SC2086)

<details><summary><b>很少用的 declare</b><font color="deepskyblue"> (Show more &raquo;)</font></summary>
<ul>
<li>声明常量 <code>declare -r TITLE="Page Title"</code></li>
<li>声明整数变量 <code>`declare -i</code></li>
</ul></details>

如果使用未赋值的变量

```shell
$ foo=foo.txt
$ echo $foo1  # 什么都不会打印
$ echo ${foo}1
```

其中 `$foo1` 为空 (类似 None/null), 而不是空字符串. 写成 `"$foo1"` 保证是字符串.

### Here documents

少见?

A here document is an additional form of I/O redirection in which we embed a body of text into our script and feed it into the standard input of a command. 

```
command << token
    text
token
```

where `command` is the name of command that accepts standard input and `token` is a string used to indicate the end of the embedded text. Note that the token must appear alone and that there must not be trailing spaces on the line. By default, **single and double quotes within here documents lose their special meaning to the shell.**

```shell
# 例子: cat > ~/foo << _EOF_
# 写成 cat <<- _EOF_ 则忽略 text 中开头的 tab (不忽略空格)
cat << _EOF_
<html>
    <head><title>${TITLE}</title></head>
    <body><h1>${TITLE}</h1></body>
</html>
_EOF_
```

## 函数

两种写法. Deprecated, 见 [这里](https://stackoverflow.com/questions/4654700/what-are-the-parentheses-used-for-in-a-bash-shell-script-function-definition-lik)

```
function name {
    commands
    return
}
```

推荐

```
name () {
    commands
    return
}
```

调用方法, 直接写 `name`, 不要加括号.

**局部变量**

```shell
foo=0

func () {
    local foo
    foo=1
    echo ${foo}
}
```

- 不声明局部变量则用的是全局变量.
- `return` 可以不写, 默认结尾 return. 如果 return 没写参数 (正整数), 默认 return 最近执行命令的 exit status (`exit` 命令也是如此, 它写在脚本末尾). 见 [这里](https://unix.stackexchange.com/questions/446420/implicit-return-in-bash-functions).
- shell 函数只能返回 exit status, 见 [这里](https://stackoverflow.com/questions/8742783/returning-value-from-called-function-in-a-shell-script).
- 不能写参数.

## 条件语句

两种写法, 见 [这里](https://stackoverflow.com/questions/50117346/why-do-some-people-put-a-semicolon-after-an-if-condition-in-shell-scripts). 

```shell
x=5
y=~/foo.txt

if [ "$x" -eq 5 -a ! \( -e "$y" \) ]; then
    echo "equal"
elif [ "$x" -lt 5 ]; then
    echo "less than"
else
    echo "greater than"
fi

# 或者不写分号, 但是把 then 写在下一行
# 因为分号只是分隔命令用
# if [ ... ]
# then
```

**Using the quotes around the parameter ensures that the operator is always followed by a string, even if the string is empty.**

### Exit status

Commands (including the scripts and shell functions we write) issue a value to the system when they terminate, called an **exit status**. This value, which is an integer in the range of 0 to 255 (没有负数, 一般 0 表示成功), indicates the success or failure of the command's execution. 

执行命令后, 执行 `$?` 可得上一条命令的 exit status. shell 有两个 bulitin 命令 (不是变量), `true` 的 exit status 为 0, `false` 为 1.

### `test`

The command used most frequently with `if` is `test`. 两种写法

```
test expression
```

第二种更流行

```
[ expression ]
```

当 expression 为真时返回 exit status 0, 否则 1. 注意 `test` 和 `[` 都是命令 (后者参数以 `]` 结尾, 也因此 `[` 后与 `]` 前需要空格).

下面详细的要查表, 随便列几个.

**File expressions**

- `-e file`: `file` exists
- `-d file`: `file` exists and is a directory, `-f` regular file
- `-x file`: 存在且有执行权限, 类似地, `-r`, `-w`

**String expressions**

- `string`: `string` is not null.
- `-n string`: the length of `string` is greater than zero, `-z` 表示长度为 0
- `string1 == string2`: 相等. 在 `bash` 推荐双等号, 但是 POSIX 只能用单等号. 不相等用 `!=`

**Integer expressions**

- `int1 -eq int2`: 相等, `-ne` 不相等. 可以直接用双等号?
- `int1 -le int2`: 小于等于, `-lt` 为小于. 字符串比较用 `"<"`, 记得双引号, 否则会视为 redirection operators. 注意字符串比较大小与整数比较大小方法不同.

### Modern `test`

现代 bash 提供了下述语法 (推荐使用)

```
[[ expression ]]
```

比单个方括号增加的功能是正则匹配.

```
string =~ regex
```

例如

```shell
if [[ "$INT" =~ ^-?[0-9]+$ ]]
```

其他可参考 [这里](https://stackoverflow.com/questions/3427872/whats-the-difference-between-and-in-bash/3427931#3427931).

Since all expressions and operators used by `test` are treated as command arguments by the shell (unlike `[[]]` and `(( ))`), characters that have special meaning to `bash`, such as `<`, `>`, `(`, and `)`, must be quoted or escaped.

**逻辑运算符**

|     | test | `[[]]` and `(())` |
| --- | ---- | ----------------- |
| AND | -a   | `&&`              |
| OR  | -o   | `||`              |
| NOT | !    | `!`               |


此外 shell 本身可以用 `&&` 或者 `||` 拼接命令, 短路执行. 可以作为 if 的 one liner.

```shell
$ mkdir temp && cd temp
$ [[ -d temp ]] || mkdir temp  # 不存在才创建
```

**`(())` for integers**

bash 的语法, 少见?

```shell
if ((1))  # true
if ((0))  # false
if ((INT == 0))
if ((INT < 0))
if (( ((INT % 2)) == 0 ))
```

## 读取键盘输入

The `read` builtin command is used to read a single line of standard input. This command  can be used to read keyboard input or, when redirection is employed, a line of data from a file.

```
read [-options] [variable...]
```

If no variable name is supplied, the shell variable `REPLY` contains the line of data.

少见? 鸽了, 直接看书.

## 循环

### while

```shell
foo=1
while [ "$foo" -lt 5 ]; do
    echo "$foo"
    foo=$((foo+1))
done
```

同 if 可以用双方括号. 此外还有 break 和 continue.

### for

```shell
for foo in 1 2 3 4; do
    echo "$foo"
done
```

brace expansion

```shell
for foo in {1..4}
```

此外还有 C 语言形式的 for 循环, 略.

## Debug

书上列了一些典型错误, 直接看.

直接 print 大法 (指 echo) 或者 bash 提供了 tracing

```shell
#!/bin/bash -x
```

或者

```shell
#!/bin/bash

# blahblah

set -x # Turn on tracing
# blahblah
set +x # Turn off tracing
```

## 位置参数

Executing

```bash
./script.sh Hello World
```

Will make

```bash
$0 = ./script.sh
$1 = Hello
$2 = World
```

当参数很多时, The `shift` command causes all the parameters to "move down one" each time it is executed.

```shell
#!/bin/bash

# posit-param2: script to display all arguments

count=1
# $# 参数数量, 不算 $0
while [[ $# -gt 0 ]]; do
    echo "Argument $count = $1"
    count=$((count + 1))
    shift
done
```

可以在函数里使用这些位置参数.

可以结合 `case` 写位置参数, 略.

## 数组

只支持一维数组. 使用场景可以参考 [SC2086#exceptions](https://github.com/koalaman/shellcheck/wiki/SC2086#exceptions).

```bash
# index 从 0 开始, 但是赋值时中间可以不赋值
a[1]=foo
echo ${a[1]}

days=(Sun Mon Tue Wed Thu Fri Sat)
days=([0]=Sun [1]=Mon [2]=Tue [3]=Wed [4]=Thu
[5]=Fri [6]=Sat)

for i in "${days[@]}"; do echo $i; done
```

## Tips

[shellcheck](https://github.com/koalaman/shellcheck/wiki/Checks) 插件提供了 [很多建议](https://github.com/koalaman/shellcheck#gallery-of-bad-code)

- Use `cd ... || exit` in case `cd` fails. See [SC2164](https://github.com/koalaman/shellcheck/wiki/SC2164). 因为默认情况下 shell 脚本遇到错误会继续执行下一句, 而不是退出.
- Check exit code directly with e.g. `if mycmd;`, not indirectly with `$?`. See [SC2181](https://github.com/koalaman/shellcheck/wiki/SC2181).

Google 也有 [style guide](https://google.github.io/styleguide/shellguide.html).
