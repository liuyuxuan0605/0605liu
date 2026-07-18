# AVL 旋转崩溃 — 第9轮后续诊断

## 已完成的排查（代码层面已排除 AVL 树逻辑 bug）

| 排查项 | 结果 |
|--------|------|
| `AVLTree.h` 是否唯一 | ✅ 全局仅 `src/core/AVLTree.h`，被 `Factory.h`/`tests` include，无重复文件 |
| 帧结构是否一致 | ✅ `Common.h` 的 `FrameNode`(5字段)/`FrameEdge`(3字段) 与 AVL、RB 的 `collectVisual` 完全兼容 |
| 旋转函数 unique_ptr 语义 | ✅ 与 RB 同构（move 前保存 `y_raw`/`x_raw` 裸指针） |
| C++ move 语义严格模拟 | ✅ `avl_memory_sim.py` v4：已知旋转序列 + **3000 回合随机插入/删除混合 ALL PASS（无 move 后解引用）** |

**结论**：AVL 的旋转 + `insertRec`/`removeRec` 在 C++ `unique_ptr` 语义下无 RB 第8轮那种崩溃。代码逻辑层面 AVL 正确。

## 本轮新增的防御性修复
- `AVLTree.h` 的 `rotateRight`/`rotateLeft` 加了 `if (!y->left) return y;` / `if (!x->right) return x;`，与 RB 旋转函数完全一致（逻辑上 AVL 平衡因子已保证有对应孩子，此检查为防御性，无害）。

## 为什么还需要你提供信息
本机（我的环境）**没有 C++ 编译器**，无法编译复现你的 SIGSEGV。代码静态 + 模拟验证都通过，所以崩溃点不在我肉眼可见的树逻辑里，需要你本机的编译器/调试器给出**精确位置**。

## 请你用下面任一方式定位（按推荐顺序）

### 方式 A：Qt Creator 调试（最简单，崩溃自动停行）
1. Qt Creator 打开项目 → 菜单 **Debug → Start Debugging (F5)**
2. 依次输入触发崩溃的 AVL 操作（如插入 `10`、`20`、`30` 后继续…用你之前崩的那个序列）
3. 崩溃时 Qt Creator **会自动打开 `AVLTree.h` 并高亮出错的那一行**（不是反汇编）
4. 把**那一行代码 + 行号**告诉我

### 方式 B：AddressSanitizer 测试程序（最精确）
项目里已放好 `avl_san_test.cpp`（Qt 无关纯 C++，只依赖 `src/core/*.h`）：
```
# 在 MinGW 终端（项目根目录）
g++.exe -std=c++17 -O0 -g -fsanitize=address -I. avl_san_test.cpp -o avl_san.exe
./avl_san.exe
```
崩溃时 ASan 会打印：出错文件名 + 行号 + 错误类型（heap-use-after-free / null deref 等）。把输出贴给我。

### 方式 C：直接告诉我触发崩溃的操作序列
比如"依次插入 10、20、30、40、50 后崩"或"插入 11、14、12 后删 14 崩"——我能在模拟器里精确复现并定位。

## 同时请确认构建是最新的
在 Qt Creator 里严格执行：**Build → Clean All Projects → 右键项目 Run qmake → Build → Rebuild All Projects**，再测 AVL。
（你确认过 RB 删除没问题，说明构建系统工作正常；但请再次确认 AVL 这次用的是最新 `AVLTree.h`。）
