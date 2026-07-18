# AVL 树「一旋转就崩溃」修复报告（第7轮）

## 问题
用户反馈：树一旦旋转（插入/删除触发平衡旋转）程序即崩溃。这是对第6轮 `rootPtr` 方案的直接否定。

## 两个根因

### 1. 第6轮 `rootPtr` 方案自身有 bug
第6轮用 `Node** rootPtr`，并在**每一次**旋转分支执行 `*rootPtr = newRoot.get()`。
- 内部（非顶层）旋转时，整棵树的根其实并没有变，但这句话把 `rootPtr` 指向了内部子树的新根。
- 后续帧采集 `makeFrame(*rootPtr, ...)` 只采到子树 → DSScene 把其余节点当成"已删除"而清除 → 结构错乱 → 下一次旋转/操作直接崩。

### 2. AVL 删除双子节点的后继摘除 bug
原代码手动 `std::move(node->right->left)` / `std::move(succParent->left)` 拼接摘除中序后继：
- 绕过了递归，导致祖先节点的 `height` 字段没有更新 → 留下**陈旧高度**。
- `balance()` 基于陈旧高度误判 → 触发**错误旋转** → 树结构损坏 → 下一次插入/删除/旋转崩溃。

## 修复（已落到 `src/core/AVLTree.h`）

**改动 1 — 帧采集根指针参数化**
```cpp
// 入口保存整树根
Node* realRoot = root_.get();
root_ = insertRec(std::move(root_), value, frames, added, realRoot, true);

// 递归签名
std::unique_ptr<Node> insertRec(std::unique_ptr<Node> node, const std::string& value,
                                FrameList& frames, bool& added, Node*& realRoot, bool isTop);
```
- 帧采集一律用 `realRoot`（递归全程指向整树根）。
- **仅 `if (isTop)` 顶层旋转**才 `realRoot = newRoot.get()` 更新整树根；内部旋转不动整树根。

**改动 2 — 删除双子节点改为递归摘除后继**
```cpp
Node* succ = node->right.get();
while (succ->left) succ = succ->left.get();
std::string succVal = succ->value;
node->value = succVal;
// 递归从右子树删除后继，高度沿递归路径正确回传
node->right = removeRec(std::move(node->right), succVal, frames, removed, realRoot, false);
```

## 验证方式（本机无 C++ 编译器，用 Python 移植等价验证）
- `avl_test.py`：Python dict 模拟 AVL，`validate()` 校验 BST 性质 + 高度平衡。
  - 旧方案（rootPtr + 手动摘除后继）：纯插入 0 失败，但「插入+删除混合」出现 **361 处 height viol**。
  - 修正后继摘除后：混合 + 纯插入 **全部 0 失败**。
- `rb_test.py`：红黑树移植，插入逻辑 0 失败（含全部 RB 不变量），确认红黑树无同类 bug。
- 结论：崩溃根因在 **AVL 删除逻辑**，与渲染层 / DSScene 无关。

## 你需要做的
本机 Qt Creator 中：**构建 → Clean Project → 重新构建**，然后验证：
1. AVL 大量插入、删除、连续旋转不再崩溃。
2. 红黑树回归（插入 + 第4轮新增的删除提示帧）。

## 文件清单
- 修改：`src/core/AVLTree.h`
- 新增（验证用，可删除）：`avl_test.py`、`rb_test.py`
