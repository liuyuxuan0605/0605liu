# DSVisualizer 开发文档

> 数据结构可视化演示工具。本文件为当前（2026-07-08）的权威开发文档，取代早期
> "8 种结构 + CMake" 的旧版本。如与代码冲突，以代码为准。

---

## 1. 项目简介

DSVisualizer 是一个用 C++17 + Qt 手写的数据结构可视化工具，最初为**面试准备**而做——
目标是把高频考点（树旋转、哈希冲突、堆调整、图遍历等）以"单步调试式"动画演示出来。

核心特色：**步骤分解机制**。每个操作（插入/删除/查找/遍历…）既真正修改数据结构，又返回
一串 `Frame`（微步快照）；可视化层对相邻帧做差分，用 `QPropertyAnimation` 平滑过渡，
效果类似 IDE 调试器的 step-by-step。

当前规模：**16 种数据结构**，全部自实现（不依赖第三方库）。

---

## 2. 技术栈与运行环境

| 项 | 说明 |
|----|------|
| 语言 | C++17 |
| GUI | Qt 5.12.11 + MinGW 7.3（本机环境，**无 Qt 6**） |
| 构建 | **qmake**（`.pro`）；仓库根有 `CMakeLists.txt` 但 Qt 5.12.11 套件未配置 CMake，故以 qmake 为准 |
| 核心引擎 | 纯 C++17，**零 Qt 依赖**，可独立编译与单元测试 |
| 单元测试 | `tests/DSVisualizerTests.pro`，不链接 Qt，仅用 MinGW 编译核心引擎 |

> ⚠️ 开发沙箱内**没有 C++ 编译器**，所有改动目前只做代码审查 + 一致性检查；
> 真正的编译/运行验证需在本地 Qt Creator（Qt 5.12.11 + MinGW 7.3）完成。

---

## 3. 目录结构

```
DSVisualizer/
├── DSVisualizer.pro            # 主程序 qmake 工程（GUI）
├── CMakeLists.txt              # 备选构建（本机未配置到 Qt5.12.11 套件）
├── docs/DESIGN.md              # 本文档
├── resources/                  # 图标等资源（如有）
├── tests/
│   ├── DSVisualizerTests.pro   # 无 Qt 的核心引擎单测
│   └── test_core.cpp
└── src/
    ├── app/main.cpp             # 程序入口
    ├── core/                    # 数据结构引擎（纯 C++，无 Qt）
    │   ├── Common.h             # Frame / FrameNode / FrameEdge / StepType / DSKind / 工具函数
    │   ├── IDataStructure.h     # 所有结构的统一抽象接口
    │   ├── Factory.h            # 按 DSKind 创建实例 + kindToString
    │   ├── SinglyLinkedList.h   DoublyLinkedList.h
    │   ├── Stack.h  Queue.h  Deque.h
    │   ├── BlockingQueue.h  RingBuffer.h
    │   ├── BinarySearchTree.h  AVLTree.h  RedBlackTree.h
    │   ├── BTree.h  BPlusTree.h  MinHeap.h
    │   ├── HashMap.h  LRUCache.h
    │   └── Graph.h
    ├── visual/                  # 可视化渲染层（Qt）
    │   ├── VisualNode.h  VisualEdge.h     # QGraphicsObject，自带可动画属性
    │   ├── LayoutEngine.h/.cpp           # 按类型自动布局
    │   ├── DSScene.h/.cpp               # FrameList 差分 → 节点/边增删 + 平滑动画
    │   └── StepAnimator.h               # QTimer 驱动逐帧播放（播放/暂停/单步/调速）
    └── ui/                       # 交互层（Qt Widgets）
        ├── MainWindow.h/.cpp     # 整合场景/动画器/左右面板，处理操作与切换
        ├── OperationPanel.h/.cpp # 结构选择（分类下拉）/输入/操作按钮/调速/演示序列
        └── LogViewer.h/.cpp      # 当前步骤说明/进度/播放控制/撤销重做/步骤日志
```

> 注：`src/core/CircularQueue.h` 是**已废弃的残留文件**（见 §10），不参与编译。

---

## 4. 架构（三层 + 数据流）

```
┌──────────────────────────────────────────────────────────────┐
│  UI 层 (src/ui)   OperationPanel · MainWindow · LogViewer       │
│   - 选择结构 / 输入值 / 点按钮 → 调用 MainWindow 的 doOperation  │
└───────────────┬──────────────────────────────────────────────┘
                │  operationRequested("insert","42")
                ▼
┌──────────────────────────────────────────────────────────────┐
│  Core 引擎 (src/core)   纯 C++，无 Qt                           │
│   IDataStructure::insert/remove/find/bfs/dfs …                 │
│      ↓ 既修改结构，又返回 FrameList（一串微步快照）              │
└───────────────┬──────────────────────────────────────────────┘
                │  FrameList
                ▼
┌──────────────────────────────────────────────────────────────┐
│  Visual 层 (src/visual)   DSScene + StepAnimator                │
│   DSScene::applyFrame 对相邻帧差分 → QPropertyAnimation 过渡    │
│   StepAnimator 用 QTimer 按 BASE_MS/speed 逐帧推进              │
└──────────────────────────────────────────────────────────────┘
```

**关键不变量**：引擎层只产数据（`FrameList`），不碰任何 Qt 绘图；Visual 层只消费数据做动画。
两层之间仅靠 `Common.h` 里的 `Frame` 数据结构耦合，因此引擎可被独立单测。

---

## 5. 核心机制：步骤分解（FrameList）

### 5.1 Frame 数据模型（Common.h）

```cpp
struct Frame {
    StepType type;                 // Start/CreateNode/Traverse/Compare/Rotate/.../Done
    std::string description;       // 当前微步的说明文字（显示在"当前步骤"面板 + 步骤日志）
    std::vector<FrameNode> nodes;  // 本帧全部节点的完整快照
    std::vector<FrameEdge> edges;  // 本帧全部连线的完整快照
    std::vector<int> highlightIds; // 本帧要高亮的节点 id
    std::string highlightColor;    // 高亮色（绿=新增/橙=断开/紫=旋转/琥珀=比较）
    int focusId = -1;              // 当前焦点节点（可选强调）
};
using FrameList = std::vector<Frame>;
```

每个节点有**稳定 id**（`FrameNode.id`），跨帧不变，动画器据此追踪节点"移动"而非"删除重建"。

### 5.2 差分动画（DSScene::applyFrame）

`applyFrame` 必须按固定顺序处理，避免悬空图元：

```
删旧边 → 删旧节点（同步 delete，不淡出）→ 建新节点 → 建新边
```

- 新节点：从 `scale 0` 弹出到 `1`
- 节点移动：`nodePos` 属性补间
- 连线重连：`p1/p2` 跟随端点补间，`edgeOpacity` 渐隐渐显
- 高亮：`fillColor` 变色

### 5.3 逐帧播放（StepAnimator）

`StepAnimator` 用 `QTimer` 按 `BASE_MS / speed` 间隔推进帧。支持播放/暂停/单步前进/后退/
跳到首/尾，速度可调（约 0.25x–4x）。

### 5.4 去重遍历顺序展示

图/树的 BFS、DFS 完成帧会在 `description` 末尾用 `\n` 换行追加遍历顺序，例如：

```
BFS(层序) 完成
遍历顺序（去重）：50 → 30 → 80 → 20 → 40 → 60 → 80
```

去重天然成立：遍历时只在**首次访问**（`visited` 集合标记）时记录顺序，配合 `visited` 不会出现重复顶点。
该格式仿照 VisuAlgo 等工具在完成帧列出访问顺序的惯例。`description` 经开启 `wordWrap` 的
`QLabel` 渲染，`\n` 正常换行。

---

## 6. 统一接口 IDataStructure

```cpp
class IDataStructure {
public:
    virtual DSKind kind() const = 0;
    virtual std::string name() const = 0;
    virtual std::string description() const = 0;

    // 核心操作：既修改结构，又返回 FrameList
    virtual FrameList insert(const std::string& value) = 0;
    virtual FrameList insertAt(int pos, const std::string& value) = 0;
    virtual FrameList remove(const std::string& value) = 0;
    virtual FrameList removeAt(int pos) = 0;
    virtual FrameList find(const std::string& value) = 0;
    virtual FrameList clear() = 0;

    // 双端队列扩展点（默认空实现，其余结构编译不受影响）
    virtual FrameList pushFront(const std::string&);
    virtual FrameList pushBack(const std::string&);
    virtual FrameList popFront();
    virtual FrameList popBack();

    // 图扩展点（默认空实现）
    virtual FrameList addVertex(const std::string&);
    virtual FrameList addEdge(const std::string&);
    virtual FrameList bfs(const std::string& start);   // 默认空
    virtual FrameList dfs(const std::string& start);   // 默认空
    virtual FrameList dijkstra(const std::string& start);

    virtual Frame currentFrame() const = 0;            // 静态渲染当前状态
    virtual int size() const = 0;
    virtual bool empty() const = 0;
    virtual std::vector<std::string> snapshotValues() const = 0;  // 供撤销快照
};
```

**新增一种数据结构的步骤**：
1. 在 `Common.h` 的 `DSKind` 枚举加一项；
2. 新建 `src/core/Xxx.h`，继承 `IDataStructure`，实现所需操作并返回 `FrameList`；
3. 在 `Factory.h` 的 `createDataStructure` 与 `kindToString` 加分支；
4. 在 `OperationPanel::buildKindCombo()` 的分类表中加入对应条目（决定它出现在哪个分组）；
5. 把头文件加入 `DSVisualizer.pro` 的 `HEADERS`（若含 `Q_OBJECT` 才会被 moc 处理，纯引擎头不需要）。

> 设计约定：`bfs/dfs/dijkstra`、双端队列方法用**默认空实现**作为扩展点，
> 因此新增结构不必一次性实现全部操作也能编译通过。

---

## 7. 已实现数据结构（16 种）

| 分类 | 结构 | 可视化重点 | BFS/DFS |
|------|------|-----------|:------:|
| **链表类** | 单链表 SinglyLinkedList | 指针断开/重连 | — |
| | 双链表 DoublyLinkedList | 双向指针同步 | — |
| **栈与队列** | 栈 Stack | 栈顶入出（竖向） | — |
| | 队列 Queue | 队首/队尾移动（横排） | — |
| | 双端队列 Deque | 头尾均可插入/删除 | — |
| | 阻塞队列 BlockingQueue | 固定容量+牺牲1单元判满；满时拒绝入队（提示帧模拟阻塞） | — |
| | 环形缓冲区 RingBuffer | 满时**覆盖**最旧（与 BlockingQueue 语义对照） | — |
| **树结构** | 二叉搜索树 BST | 比较路径、删除后继替换 | ✅ BFS+DFS |
| | AVL 平衡树 | 平衡因子变化 + 四种旋转（最出彩） | — |
| | 红黑树 RedBlackTree | 颜色 + 旋转 + 双黑修复 | — |
| | B 树 B-Tree | 多路分裂/合并 | — |
| | B+ 树 B+Tree | 叶子链表、内部/叶子节点区分 | — |
| | 最小堆 MinHeap | 数组布局 + 上浮/下沉交换 | — |
| **哈希与缓存** | 哈希表 HashMap | 链式冲突：`hash(key)%8` 定位桶 → 桶内链追加 | — |
| | LRU 缓存 LRUCache | get 命中移到队首、容量满淘汰队尾 | — |
| **图** | 图 Graph | 邻接遍历、边权 | ✅ BFS+DFS+Dijkstra |

> BFS/DFS 目前仅 **Graph** 与 **BST** 真正实现（其他树的 `bfs/dfs` 是接口默认空实现）。
> 因此 OperationPanel 的"树遍历"按钮组**仅在 BST 选中时显示**，避免出现"点了没反应"的死按钮。

---

## 8. 可视化与交互

### 8.1 左侧 OperationPanel
- **分类下拉**：用 `QStandardItemModel` 实现，分组标题为不可选加粗项，数据项携带 `DSKind`。
  分组：链表类 / 栈与队列 / 树结构 / 哈希与缓存 / 图。
- **输入与操作按钮**：按结构类型动态改文案（如栈=压入/弹出，队列=入队/出队，哈希=key:value）。
- **调速**：速度滑块（信号 `speedChanged`）。
- **演示序列**：「运行演示序列」自动跑一组预设操作，连续演示旋转/重平衡/遍历等复杂场景。

### 8.2 中间 DSScene
`QGraphicsView` 场景，按 `LayoutEngine` 自动布局（链表横排 / 树中序+深度 / 堆数组索引 /
哈希桶链 / 图力导或环排），节点与边带平滑动画。

### 8.3 右侧 LogViewer
- 当前步骤说明（`Frame.description`）、进度（第 n/总 帧）。
- 播放控制：播放/暂停、单步前进/后退、跳首/尾、速度调节。
- **撤销/重做**：`|◀`（undo）与 `▶|`（redo）。`MainWindow` 用 `m_values` + `m_history`（undo 栈）
  + `m_redo`（redo 栈）实现；变更操作前对当前值集合做快照，新操作清空 redo 栈；
  只读遍历（bfs/dfs）不记快照。

### 8.4 切换数据结构时彻底清屏
`MainWindow::switchKind` 在切换时执行：

```cpp
m_animator->stop();          // 先停动画（避免删图元时旧动画仍持有指针）
m_animator->setFrames({});   // 清空帧序列
m_scene->clearAll();         // 清空场景图元
m_view->resetTransform();    // 复位视图缩放
```

> 早期版本顺序为「先 clearAll 再 stop」，存在动画持有时删图元的悬空风险，现已修正。
> 下拉框的 `setKindIndex` 用 `QSignalBlocker` 防止程序化 `setCurrentIndex` 触发
> `currentIndexChanged` 导致 `switchKind` 被重复调用。

---

## 9. 构建与运行

### 方式 A：Qt Creator（推荐）
1. `File → Open File or Project` 选择 `DSVisualizer.pro`；
2. 套件选 **Desktop Qt 5.12.11 MinGW 64-bit**；
3. 配置 → 构建（锤子）→ 运行。

### 方式 B：命令行
```bash
qmake DSVisualizer.pro
mingw32-make
# 生成 DSVisualizer.exe，直接运行
```

### 核心引擎单测（无需 Qt）
```bash
cd tests
qmake DSVisualizerTests.pro
mingw32-make
debug\DSVisualizerTests.exe
```

> 建议流程：**Clean All → Run qmake → Rebuild All**，确保旧目标文件不会残留导致链接错误。

---

## 10. 已知问题与待清理

1. **`src/core/CircularQueue.h` 是废弃残留文件**
   它是 `BlockingQueue.h` 的早期副本，第 41 行 `return DSKind::CircularQueue;` 引用了
   **已在第 15 轮删除的枚举值**。它未被列入 `DSVisualizer.pro` 的 `HEADERS`，因此不参与编译；
   但一旦被任何翻译单元 `#include` 就会触发编译错误。**应直接删除该文件**。

2. **主题切换未实现**
   早期文档称"菜单 视图 → 切换深色/浅色主题"，经代码核查**并未实现**。如需此功能需另行开发。

3. **遍历仅 Graph 与 BST 实现**
   AVL / 红黑树 / B 树 / B+ 树 / 最小堆 均未重写 `bfs/dfs`（默认空实现）。
   "树遍历"按钮组因此只在 BST 显示。若要"所有树都有遍历"，需按 BST 的
   "记录首次访问顺序"思路逐个补上。

4. **MinHeap 归入"树结构"分类**
   语义上堆是特殊的完全二叉树，放"树结构"分组可接受；如想更精确可单列"堆"分组。

---

## 11. 开发历程精华（踩坑与解法）

以下为本项目多轮迭代中已确认的根因与定式，供后续维护参考：

- **`std::unique_ptr` 旋转后解引用（SIGSEGV）**：`rotateLeft/rotateRight` 中
  `x->right = std::move(y)` 之后 `y` 已被移走，紧接着 `y->left = ...` 解引用空 unique_ptr。
  **解法**：move 前用 `Node* y_raw = y.get()` 保存裸指针，后续全走裸指针。Python 移植测试
  因无 move 语义无法复现此 bug，必须以 C++ 实测为准。

- **MinGW 7.3 严格类型检查**：`unique_ptr ↔ raw pointer` 不允许隐式转换。赋值/比较 raw 指针
  必须 `.get()`；只有 unique_ptr 间传所有权才用 `std::move()`。MSVC 更宽松，但 MinGW 按标准来。

- **AVL 整树根 `root_` 被 move 后帧采集成空**：`insertRec(std::move(root_), ...)` 把所有权
  转移给递归参数，导致递归期间 `root_.get()==nullptr` → 帧数据空 → 误删全部节点。
  **解法**：用 `Node*& realRoot + bool isTop`，仅顶层旋转才回写整树根；帧采集一律用 `realRoot`。

- **AVL 删除双子节点后继摘除 bug**：原手写拼接摘除后继，绕过递归致祖先 height 不更新 →
  陈旧高度 → 错误旋转。解法是改为递归 `removeRec` 删除后继，高度沿递归正确回传。

- **DSScene 动画生命周期**：节点删除必须**同步立即 `delete`**（不用 `deleteLater` 淡出），
  因 750ms 间隔内 340ms 动画窗口会造成新旧图元冲突。用 `QPropertyAnimation::start(
  DeleteWhenStopped)` 替代 `connect(finished, deleteLater)`；新动画创建前先 `stopPropertyAnimations()`。

- **Qt5 `.h` 必须显式 include 用到的 widget 类型**：`.h` 中声明 `QGroupBox*` 成员必须在 `.h`
  中 `#include <QGroupBox>`，不能依赖 `.cpp` 间接提供，否则 MinGW 报"未声明"。

- **重复定义**：新增结构实现到独立 `.h` 后，必须清理其他文件中的旧 stub（曾出现 `HashMap.h`
  末尾残留旧 `MinHeap` 定义，与 `MinHeap.h` 冲突导致 redefinition）。

---

## 12. 后续可扩展点

- [ ] 给 AVL / 红黑树 / B 树 / B+ 树 / 最小堆 实现 BFS/DFS（复用 BST 的访问顺序记录思路）。
- [ ] 实现深色/浅色主题切换（目前未做）。
- [ ] 删除 `CircularQueue.h` 残留文件。
- [ ] 扩展更多结构：跳表、并查集、Trie、线段树等。
- [ ] 为图遍历完成帧追加 Dijkstra 的确定顺序展示（与 BFS/DFS 一致）。
- [ ] 考虑把核心引擎单测接入本地 CI，弥补"沙箱无编译器"的验证缺口。

---

*文档生成日期：2026-07-08。作者：Senior Developer（高级开发工程师）。*
