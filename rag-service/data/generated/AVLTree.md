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
- 详细步骤：
  1. 从根节点开始比较
  2. 新值 < 当前节点值 → 递归插入左子树
  3. 新值 > 当前节点值 → 递归插入右子树
  4. 找到空位置后创建新节点，颜色默认为红色
  5. 记录路径上的比较操作到 frames

## balanceInsert(z, frames)

- 操作类型: `balance`
- Step 2: 从 z 向上平衡（沿 parent 链上溯）
- 详细步骤：
  1. 从插入节点 z 开始，沿 parent 链向上遍历
  2. 更新每个节点的 height 和 balance factor
  3. 检查 balance factor 是否为 ±2（失衡条件）
  4. 根据失衡类型执行旋转：
     - LL（bf=+2, left.bf=+1）→ rotateRight
     - LR（bf=+2, left.bf=-1）→ rotateLeft(left), rotateRight
     - RR（bf=-2, right.bf=-1）→ rotateLeft
     - RL（bf=-2, right.bf=+1）→ rotateRight(right), rotateLeft
  5. 插入操作最多一次旋转即可恢复平衡

## compareValues(value, z->value)

- 操作类型: `other`
- 说明: 比较新值与当前节点值，决定插入方向
- 返回值: -1（小于）、0（等于）、1（大于）

## deleteOneChild(succ, frames)

- 操作类型: `delete`
- 说明: 删除只有一个子节点的节点
- 详细步骤：
  1. 将子节点替换被删除节点的位置
  2. 更新父节点的指针
  3. 更新相关节点的 height 和 balance factor
  4. 触发向上平衡检查

## deleteOneChild(z, frames)

- 操作类型: `delete`
- 说明: 删除叶子节点或只有一个子节点的节点
- 详细步骤：
  1. 如果是叶子节点，直接删除
  2. 如果只有一个子节点，用子节点替换
  3. 更新父节点指针和树结构
  4. 触发向上平衡检查

## max(0, size_ - 1)

- 操作类型: `other`
- 说明: 获取最大节点索引，用于生成唯一节点 ID

## compareValues(value, cur->value)

- 操作类型: `other`
- 说明: 查找操作中的值比较
- 详细步骤：
  1. 比较目标值与当前节点值
  2. 如果相等，找到目标节点
  3. 如果小于，递归查找左子树
  4. 如果大于，递归查找右子树

## AVL 旋转操作

### rotateLeft(node, frames)

- 操作类型: `rotate`
- 说明: 左旋操作，用于修复 RR 和 RL 失衡
- 步骤：
  1. 将右子节点提升为新根
  2. 原根变为右子节点的左子树
  3. 右子节点原左子树变为原根的右子树
  4. 更新所有受影响节点的 height

### rotateRight(node, frames)

- 操作类型: `rotate`
- 说明: 右旋操作，用于修复 LL 和 LR 失衡
- 步骤：
  1. 将左子节点提升为新根
  2. 原根变为左子节点的右子树
  3. 左子节点原右子树变为原根的左子树
  4. 更新所有受影响节点的 height

## 平衡因子计算

- balance factor = left.height - right.height
- AVL 树要求所有节点 bf ∈ {-1, 0, 1}
- |bf| > 1 时触发旋转