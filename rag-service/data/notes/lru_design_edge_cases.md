---
structure: LRUCache
kind: theory
operation: mixed
phase: concept
difficulty: medium
---

# LRU 缓存设计要点与边界情况

## 基本结构

LRU（Least Recently Used）缓存 = 哈希表 + 双向链表：
- 哈希表：key → 链表节点指针，O(1) 定位
- 双向链表：维护访问顺序，头部 = 最近使用，尾部 = 最久未使用

操作：
- get(key)：哈希表找到节点 → 移到链表头部 → 返回值。O(1)
- put(key, value)：
  - key 已存在：更新值 → 移到头部。O(1)
  - key 不存在且未满：新建节点 → 插入头部 → 哈希表记录。O(1)
  - key 不存在且已满：删除尾部节点（最久未用）→ 从哈希表删除 → 新建节点插入头部。O(1)

## 为什么用双向链表不用单向链表

删除尾部节点时需要知道它的前驱（才能把前驱的 next 置空）。单向链表找前驱要 O(n) 遍历；双向链表直接 prev 指针 O(1)。

也可以用"哨兵节点"（dummy head + dummy tail）简化边界判断，避免空指针特判。

## 为什么不用哈希表 + 数组

数组删除中间元素需要 O(n) 搬移。双向链表删除/插入任意位置都是 O(1)（已知节点指针时）。

## 边界情况：容量为 1

capacity = 1 时：
- 每次 put 新 key 都会淘汰当前唯一的元素
- get 不存在的 key 返回 -1（或默认值）
- 链表始终只有一个节点（或为空）
- 实现上不需要特殊处理——通用的"删尾 + 插头"逻辑天然兼容

## 面试手写 LRU 的关键点

1. 双向链表节点存 key + value（存 key 是为了淘汰时能从哈希表里也删掉）
2. 哈希表的 value 是节点指针（不是 value 本身），这样才能 O(1) 定位到链表节点做移动
3. 用哨兵节点（dummy head/tail）避免 null 判断
4. 淘汰时：tail.prev 就是最久未用的节点，删除它，同时用它的 key 从哈希表删除
5. 所有操作都是 O(1)：哈希表定位 + 链表指针操作

## 变体与扩展

- LFU（Least Frequently Used）：按访问频率淘汰，需要频率桶 + 双向链表
- ARC（Adaptive Replacement Cache）：结合 LRU 和 LFU，ZFS 文件系统用
- 2Q / LIRS：更复杂的缓存替换策略，数据库缓冲池常用
- Redis 的近似 LRU：不维护精确链表，随机采样 k 个 key 淘汰最旧的（省内存）

## 面试高频问题

- LRU 和 LFU 的区别：LRU 看"最后一次访问时间"，LFU 看"总访问次数"
- 为什么 Redis 用近似 LRU 而不是精确 LRU：精确 LRU 需要维护全局双向链表，每次访问都要移动节点（写放大）；近似 LRU 只需采样，省内存省 CPU
- 线程安全的 LRU：加读写锁（get 读锁、put 写锁）或用 ConcurrentHashMap + 分段链表
- LRU 的缺陷：一次性大量冷数据扫描会污染缓存（如全表扫描），把热数据挤出去
