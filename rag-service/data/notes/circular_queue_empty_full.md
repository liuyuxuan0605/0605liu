---
structure: CircularQueue
kind: theory
operation: mixed
phase: concept
difficulty: easy
---

# 循环队列的空满判断

## 为什么需要循环队列

普通顺序队列（数组实现）的问题：元素出队后 front 前移，前面的空间浪费了，即使队列没满也无法继续入队（"假溢出"）。循环队列把数组首尾逻辑相连，指针到末尾后回绕到开头，充分利用空间。

## 基本结构

- 固定大小数组 data[0..capacity-1]
- front：指向队首元素（下一个出队的位置）
- rear：指向队尾元素的下一个位置（下一个入队的位置）
- 指针移动：`front = (front + 1) % capacity`，`rear = (rear + 1) % capacity`

## 空满判断的三种方案

### 方案一：空一格法（最常用）

故意浪费一个数组单元来区分空和满：
- 队空：front == rear
- 队满：(rear + 1) % capacity == front

实际可用容量 = capacity - 1。牺牲一个位置换取判断简洁。

### 方案二：计数器法

额外维护一个 size 变量：
- 入队时 size++
- 出队时 size--
- 队空：size == 0
- 队满：size == capacity

不浪费空间，但多一个变量的维护成本。多线程环境下 size 的读写需要原子操作。

### 方案三：标志位法

额外维护一个 bool full 标志：
- 入队后若 rear == front，置 full = true
- 出队后若 rear == front，置 full = false
- 队空：front == rear && !full
- 队满：front == rear && full

也不浪费空间，但逻辑稍复杂。

## 与 RingBuffer 的关系

循环队列和环形缓冲区（RingBuffer）底层结构完全相同（固定数组 + 取模回绕），区别在于满了之后的语义：
- 循环队列：满了就拒绝入队（返回 false / 抛异常），不丢数据
- RingBuffer（覆盖模式）：满了继续写，覆盖最旧的元素，丢旧数据
- BlockingQueue（阻塞模式）：满了生产者阻塞等待，不丢数据也不拒绝

## 面试高频问题

- 为什么空一格法要浪费一个位置：不浪费的话 front == rear 既是空也是满，无法区分
- 取模运算的性能：现代 CPU 取模较慢，若 capacity 是 2 的幂可以用位运算 `& (capacity - 1)` 替代
- 循环队列的线程安全版本：加锁（mutex）或用 CAS 做无锁队列（单生产者单消费者场景）
- Java 中 ArrayDeque 就是循环数组实现的双端队列，内部用 head/tail 指针 + 空一格法
