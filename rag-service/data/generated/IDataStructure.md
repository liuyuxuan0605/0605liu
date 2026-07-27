---
structure: IDataStructure
operation: mixed
phase: api
difficulty: medium
---

# IDataStructure 接口讲解（由引擎头文件自动抽取）

> 本文件由 `extract_docs.py` 从 `src/core/IDataStructure.h` 自动生成，与可视化实现保持一致。

## kind()

- 操作类型: `other`
- --- metadata ---

## name()

- 操作类型: `other`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## description()

- 操作类型: `other`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## insert(const std::string& value)

- 操作类型: `insert`
- --- core operations: mutate + return step frames ---

## insertAt(int pos, const std::string& value)

- 操作类型: `insert`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## remove(const std::string& value)

- 操作类型: `delete`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## removeAt(int pos)

- 操作类型: `delete`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## find(const std::string& value)

- 操作类型: `query`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## clear()

- 操作类型: `other`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## currentFrame()

- 操作类型: `other`
- A single frame of the current state (for static rendering).

## size()

- 操作类型: `other`
- --- state queries ---

## empty()

- 操作类型: `other`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## snapshotValues()

- 操作类型: `other`
- Snapshot of all values, in insertion/iteration order, for undo support.

