---
structure: RingBuffer
kind: theory
---

# 环形缓冲区（RingBuffer）满了之后新数据会怎样

环形缓冲区（Circular / Ring Buffer）是用**固定大小数组 + 头尾指针取模环绕**实现的 FIFO 缓冲，
常用于生产者-消费者、音视频流、串口收发等场景。核心问题是：**写满之后再写怎么办？**

## 基本结构
- `buffer[cap]` 固定数组
- `head`：下一个可读位置；`tail`：下一个可写位置
- 写：`buffer[tail] = x; tail = (tail+1)%cap`
- 读：`x = buffer[head]; head = (head+1)%cap`

## 满了之后的两种策略

### 策略 A：覆盖（Overwrite / 环形覆盖）
当 `tail` 追上 `head`（缓冲区已满）时，**新数据覆盖最旧的数据**：
先 `head = (head+1)%cap`（丢弃最旧），再写入。
优点：永不阻塞、适合实时流（丢旧保新）；缺点：会丢失未读数据。

### 策略 B：阻塞 / 拒绝（Blocking / Drop）
写线程在满时**阻塞等待**（配合条件变量 / 信号量），直到读线程消费腾出空间；
或直接丢弃本次写入（drop newest）。优点：不丢数据；缺点：写线程可能卡住。

## 满 / 空判定
- 常用 `(tail+1)%cap == head` 表示"满"（牺牲一个槽，避免与空态 `head==tail` 冲突）
- 也可用独立 `count` 计数器：`count == cap` 为满，`count == 0` 为空

## 为什么用环形而不是普通队列
普通数组队列反复 `pop_front` 会导致整体前移（O(n)）或产生空洞；
环形缓冲通过取模让下标首尾相连，**读写都是 O(1) 且内存零拷贝、缓存友好**。
