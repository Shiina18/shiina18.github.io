---
title: "Notes on the art of readable code"
categories: Tech
updated: 
comments: true
mathjax: false
---

最初是看到姚泽源分享的 [编写可读代码的艺术](https://zhuanlan.zhihu.com/p/62184786), 然后读了 The Art of Readable Code. 一本很薄的小书, 姚基本上把大致要点都整理出来了. 现在再整理一遍, 覆盖面有所不同, 很基础的就略过了.

> Code should be written to minimize the time it would take for someone else to understand it.

<!-- more -->

## Packing Information into Names

### Choose Specific Words

```python
def GetPage(url):
    ...
```

The word "get" doesn't really say much. Does this method get a page from a local cache, from a database, or from the Internet? If it's from the Internet, a more specific name might be `FetchPage()` or `DownloadPage()`.

**Matching Expectations of Users**

Many programmers are used to the convention that methods starting with get are "lightweight accessors" that simply return an internal member. Going against this convention is likely to mislead those users. 需要一定计算或者读取时间的操作命名为 get 就可能让人意外, 比如求很多数据的平均值 `getMean()` 可以写为 `computeMean()` 体现它调用耗时.

---

```java
class BinaryTree {
    int Size();
    ...
};
```

What would you expect the `Size()` method to return? The height of the tree, the number of nodes, or the memory footprint of the tree?

The problem is that `Size()` doesn't convey much information. A more specific name would be `Height()`, `NumNodes()`, or `MemoryBytes()`.

### Attaching Extra Information to a Name

For example, here is some JavaScript code that measures the load time of a web page:

```javascript
var start = (new Date()).getTime(); // top of the page
...
var elapsed = (new Date()).getTime() - start; // bottom of the page
document.writeln("Load time was: " + elapsed + " seconds");
```

There is nothing obviously wrong with this code, but it doesn't work, because `getTime()` returns milliseconds, not seconds.

By appending `_ms` to our variables, we can make everything more explicit:

```javascript
var start_ms = (new Date()).getTime(); // top of the page
...
var elapsed_ms = (new Date()).getTime() - start_ms; // bottom of the page
document.writeln("Load time was: " + elapsed_ms / 1000 + " seconds");
```

比如 Python [Kafka](https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html) 的参数命名, 就有 `request_timeout_ms` 等.


|      Function parameter       | Renaming parameter to encode units |
| ----------------------------- | ---------------------------------- |
| Start(int delay)              | delay → delay\_secs                |
| CreateCache(int size)         | size → size\_mb                    |
| ThrottleDownload(float limit) | limit → max\_kbps                  |
| Rotate(float angle)           | angle → degrees\_cw                |


## Names That Can't Be Misconstrued

```java
results = Database.all_objects.filter("year <= 2011")
```

What does `results` now contain?
- Objects whose year is <= 2011?
- Objects whose year is not <= 2011?

If you want "to pick out," a better name is `select()`. If you want "to get rid of," a better name is `exclude()`.

---

**Naming Booleans**

```java
bool read_password = true;
```

There are two very different interpretations:
- We *need* to read the password
- The password has already *been* read

Name it `need_password` or `user_is_authenticated` instead. 或者按照通用惯例, 可以加上前缀 `should_`, `has_`.

Finally, it's best to avoid *negated* terms in a name. For example, instead of:

```java
bool disable_ssl = false;
```

it would be easier to read (and more compact) to say:

```java
bool use_ssl = true;
```

---

- Prefer min and max for (Inclusive) Limits
- Prefer first and last for Inclusive Ranges
- Prefer begin and end for Inclusive/Exclusive Ranges

## Aesthetics

### Organize Declarations into Blocks

分段

```cpp
class FrontendServer {
    public:
        FrontendServer();
        void ViewProfile(HttpRequest* request);
        void OpenDatabase(string location, string user);
        void SaveProfile(HttpRequest* request);
        string ExtractQueryParam(HttpRequest* request, string param);
        void ReplyOK(HttpRequest* request, string html);
        void FindFriends(HttpRequest* request);
        void ReplyNotFound(HttpRequest* request, string error);
        void CloseDatabase(string location);
        ~FrontendServer();
};
```

This code isn't horrible, but the layout certainly doesn't help the reader digest all those methods. Instead of listing all the methods in one giant block, they should be logically organized into groups, like this:

```cpp
class FrontendServer {
    public:
        FrontendServer();
        ~FrontendServer();
        
        // Handlers
        void ViewProfile(HttpRequest* request);
        void SaveProfile(HttpRequest* request);
        void FindFriends(HttpRequest* request);
        
        // Request/Reply Utilities
        string ExtractQueryParam(HttpRequest* request, string param);
        void ReplyOK(HttpRequest* request, string html);
        void ReplyNotFound(HttpRequest* request, string error);
        
        // Database Helpers
        void OpenDatabase(string location, string user);
        void CloseDatabase(string location);
};
```

### Break Code into "Paragraphs"

还是分段

```python
# Import the user's email contacts, and match them to users in our system.
# Then display a list of those users that he/she isn't already friends with.
def suggest_new_friends(user, email_password):
    friends = user.friends()
    friend_emails = set(f.email for f in friends)
    contacts = import_contacts(user.email, email_password)
    contact_emails = set(c.email for c in contacts)
    non_friend_emails = contact_emails - friend_emails
    suggested_friends = User.objects.select(email__in=non_friend_emails)
    display['user'] = user
    display['friends'] = friends
    display['suggested_friends'] = suggested_friends
    return render("suggested_friends.html", display)
```

It may not be obvious, but this function goes through a number of distinct steps. So it would be especially useful to break up those lines of code into paragraphs:

```python
def suggest_new_friends(user, email_password):
    # Get the user's friends' email addresses.
    friends = user.friends()
    friend_emails = set(f.email for f in friends)
    
    # Import all email addresses from this user's email account.
    contacts = import_contacts(user.email, email_password)
    contact_emails = set(c.email for c in contacts)
    
    # Find matching users that they aren't already friends with.
    non_friend_emails = contact_emails - friend_emails
    suggested_friends = User.objects.select(email__in=non_friend_emails)
    
    # Display these lists on the page.
    display['user'] = user
    display['friends'] = friends
    display['suggested_friends'] = suggested_friends
    
    return render("suggested_friends.html", display)
```

## Comments

good code > bad code + good comments

### Don't Comment Bad Names—Fix the Names Instead

```java
// Enforce limits on the Reply as stated in the Request,
// such as the number of items returned, or total byte size, etc.
void CleanReply(Request request, Reply reply);
```

Most of the comment is simply explaining what "clean" means. Instead, the phrase "enforce limits" should be moved into the function name:

```java
// Make sure 'reply' meets the count/byte/etc. limits from the 'request'
void EnforceLimitsFromRequest(Request request, Reply reply);
```

### Avoid Ambiguous Pronouns. 


> Insert the data into the cache, but check if **it**'s too big first.

> Insert the data into the cache, but check if **the data** is too big first.

附注: data 是复数, 所以本句应该用 are.

> If the data is small enough, insert it into the cache.

### Use Input/Output Examples That Illustrate Corner Cases

For example, here's a common function that removes parts of a string:

```java
// Remove the suffix/prefix of 'chars' from the input 'src'.
String Strip(String src, String chars) { ... }
```

This comment isn't very precise because it can't answer questions such as:

- Is `chars` a whole substring that is to be removed, or effectively just an unordered set of letters?
- What if there are multiples of chars on the end of src?

Instead, a well-chosen example can answer these questions:

```java
// ...
// Example: Strip("abba/a/ba", "ab") returns "/a/"
String Strip(String src, String chars) { ... }
```

The example "shows off" the full functionality of `Strip()`. Note that a simpler example wouldn't be as useful, if it doesn't answer those questions:

```java
// Example: Strip("ab", "a") returns "b"
```

---

Here's another example of a function that could use an illustration:

```java
// Rearrange 'v' so that elements < pivot come before those >= pivot;
// Then return the largest 'i' for which v[i] < pivot (or -1 if none are < pivot)
int Partition(vector<int>* v, int pivot);
```

This comment is actually very precise, but a little bit hard to visualize. Here's an example you could include to illustrate things further:

```java
// ...
// Example: Partition([8 5 9 8 2], 8) might result in [5 2 | 8 9 8] and return 1
int Partition(vector<int>* v, int pivot);
```

There are a number of points to mention about the specific example input/output we chose:
- The `pivot` is equal to elements in the vector to illustrate that edge case.
- We put duplicates in the vector (8) to illustrate that this is an acceptable input.
- The resulting vector is not sorted—if it were, the reader might get the wrong idea.
- Because the return value was 1, we made sure 1 wasn't also a value in the vector—that would be confusing.

## Simplifying Loops and Logic

减少嵌套: 在函数里可以 return early, 在循环里可以写 continue.

### The Order of Arguments in Conditionals

Which of these two pieces of code is more readable:

```
if (length >= 10)
```

or

```
if (10 <= length)
```

To most programmers, the first is much more readable. But what about the next two:

```
while (bytes_received < bytes_expected)
```

or

```
while (bytes_expected > bytes_received)
```

Again, the first version is more readable. 

|                           Left-hand side                           |                            Right-hand side                            |
| ------------------------------------------------------------------ | --------------------------------------------------------------------- |
| The expression “being interrogated,” whose value is more in  flux. | The expression being compared against, whose value is  more constant. |


### The Order of if/else Blocks

- Prefer dealing with the *positive* case first instead of the negative—e.g., `if (debug)` instead of `if (!debug)`.
- Prefer dealing with the *simpler* case first to get it out of the way. This approach might also allow both the if and the else to be visible on the screen at the same time, which is nice.
- Prefer dealing with the more *interesting* or conspicuous case first.


For example, suppose you have a web server that's building a response based on whether the URL contains the query parameter `expand_all`:

```java
if (!url.HasQueryParameter("expand_all")) {
    response.Render(items);
    ...
} else {
    for (int i = 0; i < items.size(); i++) {
        items[i].Expand();
    }
    ...
}
```

When the reader glances at the first line, her brain immediately thinks about the `expand_all` case. It's like when someone says, "Don't think of a pink elephant." You can't help but think about it—the "don't" is drowned out by the more unusual "pink elephant."

## Breaking Down Giant Expressions

引入中间变量.

```python
if line.split(':')[0].strip() == "root":
...
```

Here is the same code, now with an explaining variable:

```python
username = line.split(':')[0].strip()
if username == "root":
...
```

## Variables and Readability

精简, 减少变量名中不必要的词汇, 减少不必要的 (不能帮助理解代码的) 中间变量.

- Moving Definitions Down. 把变量定义延迟到后面最接近它出现的地方, 减少心智负担.
- Prefer Write-Once Variables. [Immutables] tend to more often be trouble
free. The more places a variable is manipulated, the harder it is to reason about its
current value.

### Shrink the Scope of Your Variables

> Make your variable visible by as few lines of code as possible.

**No Nested Scope in Python and JavaScript**

In Python and JavaScript, variables defined in a block "spill out" to the whole function.
For example, notice the use of `example_value` in this perfectly valid Python code:

```python
# No use of example_value up to this point.
if request:
    for value in request.values:
        if value > 0:
            example_value = value
            break

for logger in debug.loggers:
    logger.log("Example:", example_value)
```

This scoping rule is surprising to many programmers, and code like this is harder to read. 

The previous example is also buggy: if `example_value` is not set in the first part of the code, the second part will raise an exception: "NameError: 'example_value' is not defined" (PyCharm 会标黄显示变量可能没定义). We can fix this, and make the code more readable, by defining `example_value` at the "closest common ancestor" (in terms of nesting) to where it's used:

```python
example_value = None

if request:
    for value in request.values:
        if value > 0:
            example_value = value
            break
            
if example_value:
    for logger in debug.loggers:
        logger.log("Example:", example_value)
```

However, this is a case where `example_value` can be eliminated altogether. `example_value` is just holding an intermediate result, and variables like these can often be eliminated by "completing the task as soon as possible." In this case, that means logging the example value as soon as we find it.

Here’s what the new code looks like:

```python
def LogExample(value):
    for logger in debug.loggers:
        logger.log("Example:", value)
        
if request:
    for value in request.values:
        if value > 0:
            LogExample(value) # deal with 'value' immediately
            break
```

## My preferences

这一段纯粹是个人喜好.

每行长度控制在 80 字符以内 (便于双窗口并排), 偶尔长一点但不超过 100 字符. 一般 IDE 我会开三条辅助线: 80, 100, 120. Pandas 和 [Django](https://code.djangoproject.com/ticket/23395) 用的是 80, 而 huggingface 用的是 120. 另外 pandas (以及我见过的大多优秀开源项目) 用的括号严格按照

```python
x = f(
    a=...,
    b=...,
    ...
)
```

这也是分割长句的基本操作. 而非

```python
x = f(a=...,
      b=...,
      ...)
```

上例要依赖 IDE 自动对齐. 或者

```python
x = f(
    a=...,
    b=...,
    ...)
```

上面三种都有人用, 但我参照的范本是 pandas.