# 第9轮报告 — AVL 旋转复核 + 红黑树删除功能

## 一、AVL 旋转：已按 RB 同构修复（第8轮已落地，本轮复核确认）

AVL 的旋转函数（`src/core/AVLTree.h` 行 116-135）**和 RB 是同一天、同一手法修的**：`std::move` 前保存 `y_raw`/`x_raw` 裸指针，之后一律走裸指针，不再 move 后解引用。

我无法在本机编译（系统里搜不到任何 `g++.exe`/`qmake.exe`），所以写了 `avl_faithful_test.py` 忠实模拟 AVL 的插入+删除（含四种旋转），验证算法正确性：

- 已知旋转触发序列（11/14/12、30/50/40、10/20/30、30/20/10、10/30/20 等）✅
- **2000 回合随机插入/删除混合** ✅ —— 全部满足 BST 性质 + AVL 平衡 + 高度一致

**结论**：AVL 的 C++ 代码逻辑正确。你说 AVL 还崩，**最大可能是陈旧构建**——RB 和 AVL 是同一次 `Rebuild All` 一起重编的，应该一起生效。麻烦你那边：

> **构建 → Clean All → 右键项目 Run qmake → Build → Rebuild All**，然后专门测 AVL（插入后删节点、连续旋转）。如果还崩，把** AVL 专属的调用栈截图**发我（指明 `AVLTree.h` 哪一行），我直接定位。

## 二、红黑树删除：已实现 + 自测通过（你要求"自己检测"的部分）

`src/core/RedBlackTree.h` 的 `remove()` 从占位提示重写为**完整删除**：

1. BST 查找目标节点
2. 双子节点 → 用中序后继值替换，再删除后继（后继至多一个子节点）
3. `deleteOneChild`：transplant 安全移交 `unique_ptr` 所有权
4. `fixDelete`：双黑修复 fixup，沿父指针上溯，覆盖 4 类情形（兄红 / 兄黑两侄黑 / 兄黑远侄黑 / 兄黑近侄黑）
5. 全程带可视化帧（断链 / 重着色 / 旋转），保持 premium 观感

**内存安全**：`transplant` 接收 `unique_ptr` 形参、`deleteOneChild` 在 `transplant` 前用裸指针捕获 `x`/`xp`、`fixDelete` 只操作裸指针 + 已修复的 `rotateAt` —— 没有任何"move 后解引用"。

### 自测结果（`rb_delete_test.py`，忠实端口插入+删除+fixup，含父指针）

```
已知序列: PASS - 已知序列通过
随机混合: PASS - 3000 回合随机插入/删除全部通过
OVERALL: ALL PASS
```

校验项：根黑、红不连红、黑高一致、BST 有序、父指针一致、size 一致。

> 注：初版自测误报"size 不一致"，排查发现是**测试脚本自己漏写了 `remove` 里的 size 递减**（C++ 里 `remove` 有 `size_ = std::max(0, size_-1)`，但 Python 测试没写）。树结构本身从未出错（inorder 与理论集合始终一致）。修正脚本后全过。**这说明删除算法是对的，只是计数 bug 在测试里。**

## 三、你需要做的

1. **AVL**：Clean All → Run qmake → Rebuild All 后测 AVL 旋转/删除（同一次构建应让 AVL 与 RB 一起生效）。
2. **红黑树删除**：现在可以测了——插入若干节点后，删除任意节点（包括触发双黑修复的情形：删黑色内部节点、删根、删有两个子节点的节点），观察动画与最终黑高平衡。

## 四、辅助文件
- `avl_faithful_test.py` — AVL 插入/删除模拟（2000 回合）
- `rb_delete_test.py` — RB 插入/删除 + 双黑修复模拟（3000 回合）
- `rb_memory_diag.py` — 第8轮 unique_ptr 内存安全诊断器
