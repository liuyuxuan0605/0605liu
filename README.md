# DSVisualizer

基于 **C++17 + Qt 5.12** 的数据结构可视化教学工具。将链表、栈、队列、平衡树（AVL / 红黑树）、B / B+ 树、堆、哈希表、图等 **16 种常用数据结构** 的插入 / 删除 / 查找等核心操作，拆成「微步骤」用动画逐步演出来，辅助算法理解与面试复习。

> 开发动机：为面试准备而做，重点展示算法分步思维与树旋转 / B 树分裂 / 图遍历等过程。

## 功能特性

- **16 种数据结构**：单/双链表、栈、队列、双端队列、阻塞队列、环形缓冲、BST、AVL、红黑树、B 树、B+ 树、最小堆、哈希表、无向/有向图
- **分步动画**：每个操作拆成 `Frame` 帧快照，渲染层做差分动画，节点位置 / 颜色 / 缩放平滑过渡（目标 60fps）
- **交互外壳**：分类下拉选结构、动态操作面板、值输入、播放/暂停/逐帧、撤销重做、切换即清空画布
- **遍历展示**：Graph + BST 上实现 BFS / DFS 去重顺序高亮（对标 VisuAlgo）

## 技术栈

| 维度 | 选型 |
|------|------|
| 语言 / 框架 | C++17 + Qt 5.12.11 (MinGW 7.3) |
| 构建 | qmake（`.pro` 工程） |
| 架构 | 三层：引擎层（纯 C++17，零 Qt）/ 渲染层（Qt Graphics View）/ 交互层（Qt Widgets） |
| 核心机制 | `Frame` 帧快照 + 差分动画；`unique_ptr` 持有节点 + 裸 `parent` 导航 |

## 架构亮点

- **引擎—渲染—交互三层解耦**：数据层为纯 C++17、零 Qt 依赖，可独立单元测试；两层通过 Qt 无关的 `Frame` 帧快照契约融合。
- **Graphics View 自绘**：自定义 `QGraphicsObject` 图元重写 `paint()` 绘制节点与连线。
- **属性动画**：`QPropertyAnimation` 对 `nodePos` / `nodeScale` / `fillColor` 做补间，实现平滑过渡。
- **内存安全**：树节点用 `unique_ptr` 持有子节点 + 裸 `parent` 指针导航；旋转严格遵循「move 前存裸指针」纪律，修复了旋转时 `unique_ptr` move 后悬空解引用导致的 SIGSEGV。

## 构建与运行

```bash
# 用 Qt 5.12 + MinGW 套件打开 DSVisualizer.pro
# 或命令行：
qmake DSVisualizer.pro
mingw32-make
./DSVisualizer.exe
```

单元测试（无 Qt 依赖，可独立编译）：

```bash
qmake tests/DSVisualizerTests.pro
mingw32-make
./tests/DSVisualizerTests
```

## 目录结构

```
src/core/     纯 C++17 数据结构引擎（零 Qt 依赖）
src/visual/   Graphics View 渲染层（DSScene / VisualNode / LayoutEngine）
src/ui/       Qt Widgets 交互层（MainWindow / OperationPanel）
src/app/      程序入口
tests/        无 Qt 单元测试
docs/         开发文档（DESIGN.md）
```

## 说明

- BFS / DFS 遍历顺序高亮目前实现于 **Graph 与 BST**；其他树结构的遍历按钮尚未接入。
- 深色 / 浅色主题切换当前未实现。
