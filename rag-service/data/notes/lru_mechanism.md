---
structure: LRUCache
kind: theory
operation: mixed
phase: algorithm
difficulty: medium
---

# LRU 缓存淘汰机制详解

## 核心原理

LRU（Least Recently Used）是一种缓存淘汰策略，当缓存满时，淘汰最久未使用的数据。

## LRU的设计目标

1. **快速访问**：O(1)时间复杂度查找数据
2. **快速更新**：O(1)时间复杂度更新访问时间
3. **快速淘汰**：O(1)时间复杂度删除最久未使用的数据

## 常用实现方式

### 方式1：哈希表 + 双向链表

**结构**：
- 哈希表：存储key到节点的映射，O(1)查找
- 双向链表：维护访问顺序，最近访问的在表头，最久未访问的在表尾

**节点结构**：
```
struct Node {
    key: int
    value: int
    prev: Node*
    next: Node*
}
```

### 方式2：哈希表 + 有序字典

在Python中可以使用`collections.OrderedDict`，在Java中可以使用`LinkedHashMap`。

## 核心操作

### Get操作

1. 在哈希表中查找key
2. 如果找到：
   - 将节点移到链表头部
   - 返回value
3. 如果未找到：返回-1

### Put操作

1. 在哈希表中查找key
2. 如果找到：
   - 更新value
   - 将节点移到链表头部
3. 如果未找到：
   - 创建新节点
   - 添加到链表头部和哈希表
   - 如果缓存已满：
     - 删除链表尾部节点
     - 从哈希表中删除对应的key

## 示例

```
LRU缓存容量=3

操作序列：
1. put(1, "A") → 链表：[1:A]
2. put(2, "B") → 链表：[2:B, 1:A]
3. put(3, "C") → 链表：[3:C, 2:B, 1:A]
4. get(1)      → 链表：[1:A, 3:C, 2:B] → 返回"A"
5. put(4, "D") → 缓存满，淘汰2:B
                 链表：[4:D, 1:A, 3:C]
6. get(2)      → 未找到，返回-1
```

## 伪代码

```python
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_node(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node):
        prev = node.prev
        next_node = node.next
        prev.next = next_node
        next_node.prev = prev
    
    def _move_to_head(self, node):
        self._remove_node(node)
        self._add_node(node)
    
    def _pop_tail(self):
        node = self.tail.prev
        self._remove_node(node)
        return node
    
    def get(self, key):
        node = self.cache.get(key)
        if not node:
            return -1
        self._move_to_head(node)
        return node.value
    
    def put(self, key, value):
        node = self.cache.get(key)
        if not node:
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_node(new_node)
            if len(self.cache) > self.capacity:
                tail = self._pop_tail()
                del self.cache[tail.key]
        else:
            node.value = value
            self._move_to_head(node)
```

## 时间复杂度

| 操作 | 时间复杂度 |
|------|-----------|
| Get | O(1) |
| Put | O(1) |
| Delete | O(1) |

## LRU与LFU的对比

| 特性 | LRU | LFU |
|------|-----|-----|
| 淘汰策略 | 最久未使用 | 使用次数最少 |
| 优点 | 实现简单，响应最近访问 | 适合访问模式稳定的场景 |
| 缺点 | 可能淘汰长期使用但暂时不访问的数据 | 实现复杂，对突发访问不友好 |

## 实际应用

### 操作系统
- 页面置换算法
- 缓存管理

### 数据库
- MySQL查询缓存
- Redis缓存

### Web开发
- HTTP缓存策略
- CDN缓存

## 关键要点

- 双向链表维护访问顺序
- 哈希表实现O(1)查找
- 最近访问的在链表头部
- 最久未访问的在链表尾部