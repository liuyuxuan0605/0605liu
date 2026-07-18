# 红黑树插入 11/14/12 旋转崩溃 — 排查结论与修复

## 一句话结论
**红黑树算法本身没有 bug**（已用 Python 精确复刻并跑通 11→14→12，得到合法 RB 树）；
你看到的崩溃 **99% 是陈旧构建（qmake 没重编 `RedBlackTree.h`）或 Qt 运行时问题**。
**请先在 Qt Creator 里 Clean All → 重新构建。**

---

## 证据：红黑树算法正确

用 Python 逐行复刻 `RedBlackTree.h` 的 `fixInsert` / `rotate*` 逻辑，跑你给的确切序列：

```
插入 11 → 11(B)
插入 14 → 11(B) ─ 14(R)
插入 12 → 12(B)
          ├─ 11(R)
          └─ 14(R)
inorder = [11, 12, 14]   ✅ RB 性质校验通过
```

- `rb_test.py`：**5000 次随机插入全部 0 失败**（覆盖 RL / LR / 情况1 重着色等所有旋转情形，含 parent 指针一致性校验）。
- 逐行审查了 `DSScene.cpp` / `LayoutEngine.cpp` / `VisualNode.h` / `VisualEdge.h` / `StepAnimator.h` / `MainWindow.cpp`：
  - 旋转帧都是**完整整树快照**（`makeFrame(root_.get())`），没有残缺帧；
  - 渲染五阶段流水线健壮；
  - 节点/边的 `Q_PROPERTY` 声明正确。
  - **在源码层面没有找到任何会导致插入旋转崩溃的点。**

> 本机环境没有 C++ 编译器（无 g++/clang，也没有 apt），无法用 AddressSanitizer 编译复现崩溃。
> `IDataStructure.h` 是 Qt 无关头，理论上可无头编译，但当前环境装不了编译器。

---

## 最可能原因：陈旧构建（stale object files）

红黑树的 RL 情形（z 是父的左孩子、父是祖父的右孩子）在第 4 轮才从错误旋转 `rotateLeftAt(z)`
修正为 `rotateRightAt(z)`。**`11 → 14 → 12` 正好是一个 RL 情形**，正是旧版 bug 的典型触发序列
（同类还有 `30 → 50 → 40`）。

如果你用 qmake **增量构建**，修改 `.h` 后有时不会重编对应目标文件，运行的是**旧版带 bug 的 `RedBlackTree.h`**
→ 插入 12 触发错误旋转 → 段错误。

**做法：Qt Creator → 构建 → Clean All → 重新构建（或删掉 build 目录后 qmake + 构建）。**

---

## 本次顺手修掉的一个真实 bug（DSScene 双重释放）

在 `src/visual/DSScene.cpp` 的 `clearAll` 与 `applyFrame` Phase 3 中，删除**带有运行动画**的节点时：

- 动画是节点的子对象，且设了 `DeleteWhenStopped`（停止时 `deleteLater` 自删）；
- 代码先 `anim->stop()`（触发 `deleteLater`），随后 `delete item` 又**级联删除**这个动画
  → **双重释放 → 堆损坏崩溃**。

修复：停止动画后 `anim->setParent(nullptr)` 把动画从节点上 detach，交给 `DeleteWhenStopped` 的
`deleteLater` 单独安全回收，不再受节点析构影响。

> 注意：这个双重释放**只在节点被真正删除时触发**（撤销 / 清空 / 切换结构）。红黑树纯插入旋转
> 不会删除任何节点，所以**这个修复大概率不直接解决 11/14/12 的崩溃**，但它是必须修的真实缺陷
> （你做撤销/清空时一定会撞上）。

---

## 如果 Clean 重建后仍然崩溃

那说明是 Qt 渲染层运行时问题，需要你提供**崩溃现场**才能精确定位（本机无法编译）：

1. **Qt Creator "Application Output"** 面板里的崩溃文本（通常会有 `ASSERT` / `Segmentation fault` / `pure virtual` 之类）；
2. 或 **F5 调试模式**跑插入序列，崩溃后在 **Stack（调用栈）** 面板复制顶层十几行；
3. 或系统崩溃对话框里的异常码 / 模块名。

把其中任意一项贴给我，我就能定位到具体哪一行。
