---
structure: Deque
kind: theory
---

# 双端队列（Deque）两端都能进出是怎么实现的

双端队列（Double-Ended QUEue）允许在**队头（front）和队尾（rear）两端**都进行插入与删除，
因此既能当栈用（只动一端），也能当队列用（一端进一端出），还能两端同时操作。

## 底层实现方式

### 1. 双向链表实现
每个节点持有 `prev` 和 `next` 指针，维护 `head` 与 `tail` 两个指针：
- `pushFront(x)`：在 head 之前插入，`x->next = head; x->prev = null; head->prev = x; head = x`
- `pushBack(x)`：在 tail 之后插入，`x->prev = tail; x->next = null; tail->next = x; tail = x`
- `popFront()`：取 head，移动 head 到 `head->next` 并断开前驱
- `popBack()`：取 tail，移动 tail 到 `tail->prev` 并断开后继
两端操作都是 O(1)，且天然支持在任意一端进出。

### 2. 循环数组实现
用连续数组 + `front`、`rear`、`size`（或 `(rear+1)%cap == front` 判满）：
- `pushFront`：`front = (front-1+cap)%cap; arr[front] = x`
- `pushBack`：`arr[rear] = x; rear = (rear+1)%cap`
- `popFront`：`x = arr[front]; front = (front+1)%cap`
- `popBack`：`rear = (rear-1+cap)%cap; x = arr[rear]`
下标用取模实现"环绕"，逻辑上首尾相连成环。

## 满 / 空判定
- 链表：空当 `head == null`；几乎不会满（受内存限制）
- 循环数组：常用"牺牲一个槽"法——`(rear+1)%cap == front` 即满；`front == rear` 即空

## 与栈、队列的关系
双端队列是栈和队列的超集：只在一端进出就是栈，固定一端进另一端出就是普通队列。
很多标准库（C++ `std::deque`、Java `ArrayDeque`）底层用分段数组或循环数组实现。
