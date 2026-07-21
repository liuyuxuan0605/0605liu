---
structure: MinHeap
operation: mixed
phase: api
difficulty: medium
---

# MinHeap 接口讲解（由引擎头文件自动抽取）

> 本文件由 `extract_docs.py` 从 `src/core/MinHeap.h` 自动生成，与可视化实现保持一致。

## push(value)

- 操作类型: `insert`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## push(value)

- 操作类型: `insert`
- MinHeap does not support positional insertion; ignore pos and push normally.

## findIter(value)

- 操作类型: `query`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## pop()

- 操作类型: `delete`
- Removing the root = standard pop

## updateAllIndices()

- 操作类型: `other`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## siftDownFrames(idx, frames)

- 操作类型: `other`
- Sift down from idx

## to_string(i)

- 操作类型: `other`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## makeFrame("未找到 '" + value + "'")

- 操作类型: `other`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## makeFrame("查找完成：找到 [" + value + "]")

- 操作类型: `other`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## idCounter()

- 操作类型: `other`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## swap(data_[idx], data_[parent])

- 操作类型: `other`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## updateAllIndices()

- 操作类型: `other`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## siftDownFrames(0, frames)

- 操作类型: `other`
- Sift down from root

## makeFrame("")

- 操作类型: `other`
- 说明: （头文件未提供注释，请结合源码实现阅读）

