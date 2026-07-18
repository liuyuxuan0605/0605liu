# 第 5 轮修复 — AVL/RB 崩溃根治 + Undo/Redo 重设计

> **触发原因**：AVL 第 3 次插入崩溃、RB 第 8 次插入崩溃、撤销功能需改为 undo/redo 双栈。

---

## 一、崩溃修复（3 处）

### 1. 红黑树 fixInsert gp 空指针 → `RedBlackTree.h:165`
**根因**：`fixInsert` 的 while 循环中，Case 1（recolor）将 z 推上到"父节点是红色根节点"时，`gp = z->parent->parent` = **nullptr**（根无父节点），下一行直接解引用 `gp->left.get()` → **段错误**。典型场景：连续多次插入触发 recolor 传播，z 最终停留在红色根节点的子节点位置。
**修复**：在 `Node* gp = z->parent->parent;` 之后加 `if (!gp) break;`。循环结束后 `root_->color = BLACK` 会修复根节点颜色。

### 2. AVL removeRec 部分帧仍用 `node.get()` → `AVLTree.h:192,203`
**根因**：前轮修复了旋转/删除高亮/后继高亮共 6 处（insertRec + removeRec），但 **removeRec 的 BreakLink 帧（行 192）和 Swap 帧（行 203）遗漏**——仍用 `makeFrame(node.get(), ...)` 只采局部子树。虽然用户报的是插入崩溃不是删除崩溃，但为一致性全部修正。
**修复**：两处均改为 `makeFrame(root_.get(), ...)` 展示完整树。

### 3. DSScene::applyFrame 处理顺序导致竞态崩溃 → `DSScene.cpp` 全重写
**根因**：原顺序为"处理节点增删 → 处理边增删"。当旋转等结构变化发生时：
- 先创建/更新节点（带位置动画）
- 再删除旧节点（带 deleteLater 动画 + 从 map erase）
- 最后处理边时，可能引用已从 m_nodes erase 但 deleteLater 尚未执行的图元
- 同时边删除的 deleteLater 动画可能与新边创建冲突

**修复**：重写为 **5 阶段安全流水线**：
| 阶段 | 操作 | 安全保证 |
|------|------|----------|
| Phase 1 | 计算 present 集合 | 无副作用 |
| Phase 2 | **先删旧边**（立即 delete，无边子对象） | 边不持有子对象，安全即时删除 |
| Phase 3 | **再删旧节点**（动画→deleteLater 或立即 delete） | 此时边已清理完毕 |
| Phase 4 | 创建/更新节点 | 引用的所有节点都是"活着的" |
| Phase 5 | 创建/更新边 | **Phase 4 保证所有端点 node 都存在于 m_nodes** |

关键改动：旧边改为**立即删除**（不用动画），因为边的消失不如节点显眼且消除了最大的竞态面；节点保留淡出动画（视觉体验）。

---

## 二、Undo/Redo 重设计（用户需求调整）

### 用户要求
1. 保持 `|◀` 符号（不改文字）
2. `|◀` = 撤销上一步操作
3. 撤销后能通过 `▶|` 快进恢复（= redo）
4. 新操作清空 redo 栈

### 实现方案

#### 数据结构
```
m_values        : vector<string>     // 当前值集合
m_history       : vector<vector<string>>  // undo 栈
m_redo          : vector<vector<string>>  // redo 栈
```

#### 信号连接
```
LogViewer::undo ──→ MainWindow::undo()      // |◀ 按钮
LogViewer::redo ──→ MainWindow::redo()      // ▶| 按钮（原 toEnd 改为 redo）
```

#### 操作语义

| 操作 | undo 栈 | redo 栈 | 说明 |
|------|--------|---------|------|
| 插入/删除/清空 | push 快照 | **clear** | 新操作清空 redo |
| 点击 `\|◀` | pop 恢复 | push 当前 | 撤销，当前状态可 redo |
| 点击 `▶\|` | push 当前 | pop 恢复 | 重做；redo 空时退化为跳末帧 |
| 切换结构 | clear | clear | 全清 |

#### 共用提取：`rebuildAndShow()`
undo 和 redo 共用同一套重建逻辑：
1. `m_ds->clear()` 清空引擎
2. 按 m_values 顺序 `insert` 重放（恢复树形）
3. 用 `currentFrame()` 生成单帧展示
4. 差异动画呈现"回退/重做"视觉效果

### 文件变更清单

| 文件 | 变更 |
|------|------|
| `src/core/RedBlackTree.h` | +`if (!gp) break;` 防御空指针 |
| `src/core/AVLTree.h` | removeRec 2处 `node.get()` → `root_.get()` |
| `src/visual/DSScene.cpp` | applyFrame 重写为 5 阶段安全流水线 |
| `src/ui/LogViewer.h` | +`redo()` 信号 |
| `src/ui/LogViewer.cpp` | 按钮改回 `\|◀`；`▶\|` 连接 `emit redo()` |
| `src/ui/MainWindow.h` | +`redo()` 槽 + `m_redo` 栈 + `rebuildAndShow()` |
| `src/ui/MainWindow.cpp` | undo/redo/rebuildAndShow 完整实现；runOperation/runPreset 清 redo |

---

## 验证步骤

1. Qt Creator **构建 → Clean Project → 重新构建**
2. **AVL 测试**：
   - 手动依次插入 50、30、20（第 3 次触发 LL 旋转）→ 应该不崩溃
   - 运行演示序列 → 跑完 8 步（含旋转+删除）不崩溃
3. **红黑树测试**：
   - 手动依次插入 50、30、70、20、40、60、80、10（第 8 次）→ 不崩溃
   - 运行演示序列（9 个值）→ 不崩溃
4. **Undo/Redo 测试**：
   - 插入几个值 → 点 `\|◀` → 回退到上一步状态
   - 点 `▶\|` → 恢复到 undo 前的状态
   - 再插一个新值 → redo 栈被清空，`\|◀` 仍然可用
   - 多次 undo 后多次 redo → 逐步恢复
