---
structure: BlockingQueue
kind: theory
operation: mixed
phase: concept
difficulty: medium
---

# 阻塞队列（Blocking Queue）

## 基本原理

阻塞队列是一种线程安全的特殊队列，在普通队列基础上增加了两个阻塞语义：
- 队列已满时，尝试插入的线程（生产者）被阻塞，直到有空间
- 队列为空时，尝试取出的线程（消费者）被阻塞，直到有元素

核心价值：自动协调生产者和消费者的速度差异，无需手动实现复杂的线程同步逻辑。

## 等待/唤醒机制：锁 + 条件变量

阻塞队列的实现原理是互斥锁（Mutex）+ 两个条件变量（Condition Variable）：

- notEmpty：队列为空时消费者在此等待，生产者放入元素后唤醒
- notFull：队列已满时生产者在此等待，消费者取出元素后唤醒

为什么需要两个条件变量：如果只用一个等待队列，生产者和消费者混在一起唤醒，会出现"消费者唤醒消费者""生产者唤醒生产者"的无效唤醒（惊群效应）。两个条件变量让唤醒精确到对方角色。

## put 操作流程（生产者）

```
lock.lock()
while (队列已满):
    notFull.wait(lock)    // 释放锁 + 阻塞
将元素入队
notEmpty.signal()         // 唤醒一个消费者
lock.unlock()
```

## take 操作流程（消费者）

```
lock.lock()
while (队列为空):
    notEmpty.wait(lock)   // 释放锁 + 阻塞
取出队首元素
notFull.signal()          // 唤醒一个生产者
lock.unlock()
return 元素
```

## 为什么必须用 while 而不是 if 检查条件

线程被唤醒不代表条件一定满足：
- 虚假唤醒（spurious wakeup）：操作系统可能无故唤醒等待线程
- 多线程竞争：多个消费者同时被唤醒，第一个取走元素后队列又空了
- 所以被唤醒后必须重新检查条件，while 循环保证条件不满足时继续等待

## C++ 实现要点

```cpp
std::mutex mtx;
std::condition_variable notEmpty, notFull;

void put(T value) {
    std::unique_lock<std::mutex> lock(mtx);
    notFull.wait(lock, [&]{ return size < capacity; });
    queue.push(value);
    notEmpty.notify_one();
}

T take() {
    std::unique_lock<std::mutex> lock(mtx);
    notEmpty.wait(lock, [&]{ return !queue.empty(); });
    T val = queue.front(); queue.pop();
    notFull.notify_one();
    return val;
}
```

关键：`wait(lock, predicate)` 内部就是 while 循环 + 释放锁 + 阻塞 + 重新获锁 + 检查谓词。

## 与环形缓冲区的关系

- RingBuffer 是底层数据结构（固定容量、指针回绕）
- BlockingQueue 是接口语义（满则阻塞、空则阻塞）
- 两者可以组合：用 RingBuffer 做存储 + 条件变量做阻塞 = 固定容量阻塞队列
- 区别：RingBuffer 满了可以覆盖（不阻塞），BlockingQueue 满了必须等待（不丢数据）

## 面试要点

- 生产者-消费者模型的标准解法就是阻塞队列，解耦双方、平衡速度差
- Java 常见实现：ArrayBlockingQueue（数组有界）、LinkedBlockingQueue（链表可选有界）、SynchronousQueue（不存储，直接交接）
- condition_variable 的 wait 必须先持有 unique_lock，否则未定义行为
- notify_one vs notify_all：单生产者单消费者用 notify_one 即可；多消费者用 notify_one 也能正确工作（while 保证竞争失败的继续等待）
