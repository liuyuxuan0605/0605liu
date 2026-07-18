# 第8轮修复报告 — AVL / 红黑树"一旋转就崩溃"真正根因

## 你的调用栈截图 = 铁证

```
#2  std::unique_ptr<...>           unique_ptr.h:374
#3  std::unique_ptr<...>           unique_ptr.h:283
#4  dsv::RedBlackTree::rotateRight  RedBlackTree.h:109   ← y->left = std::move(T2);
#5  dsv::RedBlackTree::rotateRightAt RedBlackTree.h:132
#6  dsv::RedBlackTree::fixInsert    RedBlackTree.h:204
#7  dsv::RedBlackTree::insert       RedBlackTree.h:50
#8  dsv::MainWindow::runOperation    MainWindow.cpp:123
```

局部变量：`_a` = `<无法访问>`（野指针）、`_b` = `0`（空指针）

---

## 真正的 Bug：`std::move(unique_ptr)` 后还解引用它

旋转函数里是这样的：

```cpp
std::unique_ptr<Node> rotateRight(std::unique_ptr<Node> y) {
    std::unique_ptr<Node> x  = std::move(y->left);
    std::unique_ptr<Node> T2 = std::move(x->right);
    x->right = std::move(y);   // ★ y 的所有权被移走，y 内部指针变成 null
    y->left  = std::move(T2);  // 💀 解引用已经为 null 的 y → SIGSEGV !!!
    upd(y.get());              // 💀 又一次解引用空 y
    return x;
}
```

`std::move(y)` 把 `y` 所持有的节点所有权转移到 `x->right` 后，**`y` 变成空 `unique_ptr`（内部指针 = nullptr）**。紧接着 `y->left` 和 `y.get()` 都在解引用空指针 → 段错误。

`rotateLeft` 有完全相同的错误（先 `y->left = std::move(x)` 再 `x->right = ...`）。

**为什么之前 7 轮都没发现、Python 测试也全绿？**
因为 Python 没有 move 语义——`y` 被"移走"后它依然能访问。这是**纯 C++ `unique_ptr` 所有权转移**才会触发的崩溃，我的 Python 移植模拟器抓不到。

---

## 修复方式（两棵树都改了）

在 `std::move` **之前**用裸指针把节点抓住，后续一律走裸指针：

```cpp
std::unique_ptr<Node> rotateRight(std::unique_ptr<Node> y) {
    std::unique_ptr<Node> x  = std::move(y->left);
    std::unique_ptr<Node> T2 = std::move(x->right);
    Node* y_raw = y.get();   // ★ move 前保存裸指针
    Node* x_raw = x.get();   // ★ move 前保存裸指针
    x->right = std::move(y);       // y 现在为空，但我们有 y_raw
    y_raw->left = std::move(T2);   // 用 y_raw 代替已空的 y
    upd(y_raw); upd(x_raw);        // 用裸指针更新高度
    return x;
}
```

`rotateLeft` 同理（用 `x_raw` / `y_raw`）。

| 文件 | 改动 |
|------|------|
| `src/core/RedBlackTree.h` | `rotateLeft` / `rotateRight` 两处（含 `fixInsert` 依赖的父子指针维护） |
| `src/core/AVLTree.h` | `rotateLeft` / `rotateRight` 两处（含 `upd()` 高度更新），同样踩了 `upd(y.get())` 的坑 |

---

## 你接下来做的

1. Qt Creator：**构建 → Clean All Projects**
2. 右键项目 → **Run qmake**（重新生成 Makefile）
3. **Build → Rebuild All Projects**（强制全部重编，确保新 `.h` 生效）
4. 运行，依次输入 **11 → 14 → 12**（之前必崩的序列，现在应正常得到 `12(B)/11(R)/14(R)`）
5. 顺便回归测一下 **AVL**：大量插入/删除/连续旋转

预期：不再 SIGSEGV。如果还有任何崩溃，把新的调用栈截图发我，我直接定位。

---

## 经验教训（已记入项目记忆）

> **C++ `unique_ptr` 黄金法则**：`std::move(ptr)` 之后，`ptr` 立即变为空/失效，**绝对不能再通过 `ptr->xxx` 或 `ptr.get()` 访问成员**。任何"先 move 再访问"的写法都是段错误。需要访问原节点时，必须在 move **之前**用 `Node* raw = ptr.get()` 保存裸指针。
