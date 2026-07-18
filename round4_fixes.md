# 第4轮修复说明 — AVL/红黑树崩溃 + 快退改撤销

> 项目：`D:\ai_canshow\2026-07-07-17-09-05`
> 构建：Qt Creator 打开 `DSVisualizer.pro` → 构建 → Clean Project → 重新构建

## 一、崩溃根因与修复

### 1. 红黑树 RL 情形空指针段错误（确定根因）
- **文件**：`src/core/RedBlackTree.h`
- **根因**：`fixInsert` 的 RL 情形（z 是父的左孩子、父是祖父的右孩子）误调用 `rotateLeftAt(z)`。当被旋转的父节点没有右孩子时，`rotateLeft` 内部 `std::move(y->left)` 解引用空指针 `y` → **段错误**。典型触发序列：插入 `30 → 50 → 40`（40 是 50 的左孩子，构成 RL）。
- **修复**：
  - RL 情形改为 `rotateRightAt(z)`（先右旋父节点把 RL 转成 RR，再左旋祖父）。
  - `rotateLeft` / `rotateRight` 增加防御性空指针保护：`if (!x->right) return x;` / `if (!y->left) return y;`。

### 2. AVL 旋转/删除帧只采局部子树（潜在崩溃 + 闪烁）
- **文件**：`src/core/AVLTree.h`（6 处）
- **根因**：旋转帧/删除帧用 `makeFrame(node.get(), ...)` 或 `makeFrame(succ, ...)` 只采集局部子树，导致祖先节点被渲染层误判为"消失"而删除并重建，触发 Qt 动画对已销毁图元的悬空引用。
- **修复**：全部改为 `makeFrame(root_.get(), ...)`，每帧展示完整树。

### 3. DSScene 动画悬空指针崩溃（通用根因）
- **文件**：`src/visual/DSScene.cpp`
- **根因**：`applyFrame` 中 `QPropertyAnimation` 以无父对象创建并直接指向图元；图元被删除（删除/重画路径）时，动画成为悬空指针 → 崩溃。这是 AVL/红黑树在旋转导致节点增删时崩溃的通用诱因。
- **修复**：把 `QPropertyAnimation` 设为目标图元的子对象（`new QPropertyAnimation(obj, prop, obj)`），图元销毁时动画自动随子对象销毁；移除重复的 `connect(a, finished, a, deleteLater)`，仅保留 `finished → deleteLater(item)`。

## 二、快退按钮改为"撤销上一步操作"（undo）

- `src/ui/LogViewer.h`：新增 `undo()` 信号；`|◀` 按钮标签改为 `↶ 撤销`，点击 `emit undo()`。
- `src/ui/MainWindow.h / .cpp`：
  - 新增 `m_values`（当前有序值集合，作为结构重建依据）+ `m_history`（撤销快照栈）。
  - `runOperation`：插入/删除/清空**前**先快照 `m_values`；仅当结构真正变更（去重后真正新增 / 真正删除 / 清空）才压栈并同步 `m_values`；`find` 不记录快照；重复插入/删除不存在等无实际变更不记录。
  - `runPreset`：整个演示序列作为**一次**可撤销单元。
  - `undo()`：弹栈恢复 `m_values` → `clear()` + 按插入顺序重放 `insert` 重建结构 → 用 `currentFrame()` 单帧展示并做差异动画呈现"回退"。
  - `switchKind` 切换结构时清空 `m_history` / `m_values`。
- 保留：`|▶` = 跳到当前操作末帧（toEnd）；`◀` / `▶` = 帧内步进。

## 三、验证清单（请在本机构建后确认）
- [ ] 红黑树：依次插入 `30、50、40`（RL 结构）不崩溃，能看到旋转动画。
- [ ] AVL：依次插入 `10、20、30`（LL）及更多节点不崩溃，旋转时整棵树稳定无闪烁。
- [ ] 红黑树演示序列（`运行演示序列`）完整跑完不崩溃。
- [ ] 插入若干数据后点 `↶ 撤销`：结构回退到上一步；`运行演示序列` 后点一次 `↶ 撤销` 回退到演示前状态。
- [ ] `◀` / `▶` 帧内步进正常，`|▶` 跳到操作末帧正常。

## 待办
- 红黑树 `remove`（删除）尚未实现，仅返回提示帧；撤销目前不含红黑树删除步骤。需要可补充。
