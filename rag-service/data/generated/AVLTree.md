---
structure: AVLTree
operation: mixed
phase: api
difficulty: medium
---

# AVLTree 接口讲解（由引擎头文件自动抽取）

> 本文件由 `extract_docs.py` 从 `src/core/AVLTree.h` 自动生成，与可视化实现保持一致。

## bstInsert(value, frames)

- 操作类型: `other`
- Step 1: BST 插入（与 RB 的 bstInsert 同构）

## balanceInsert(z, frames)

- 操作类型: `balance`
- Step 2: 从 z 向上平衡（沿 parent 链上溯）

## compareValues(value, z->value)

- 操作类型: `other`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## deleteOneChild(succ, frames)

- 操作类型: `delete`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## deleteOneChild(z, frames)

- 操作类型: `delete`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## max(0, size_ - 1)

- 操作类型: `other`
- 说明: （头文件未提供注释，请结合源码实现阅读）

## compareValues(value, cur->value)

- 操作类型: `other`
- 说明: （头文件未提供注释，请结合源码实现阅读）

