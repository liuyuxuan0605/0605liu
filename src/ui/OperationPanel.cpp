#include "OperationPanel.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGroupBox>
#include <QSignalBlocker>
#include <QStandardItem>

namespace dsv {

OperationPanel::OperationPanel(QWidget* parent) : QWidget(parent) {
    auto* root = new QVBoxLayout(this);
    root->setSpacing(10);

    // --- data structure selector (categorized) ---
    auto* gbKind = new QGroupBox("数据结构");
    auto* v1 = new QVBoxLayout(gbKind);
    m_kind = new QComboBox();
    m_kindModel = new QStandardItemModel(this);
    buildKindCombo();
    m_kind->setModel(m_kindModel);
    connect(m_kind, QOverload<int>::of(&QComboBox::currentIndexChanged), this, &OperationPanel::onKindChanged);
    v1->addWidget(m_kind);
    root->addWidget(gbKind);

    // --- data input ---
    auto* gbData = new QGroupBox("数据输入");
    auto* v2 = new QVBoxLayout(gbData);
    m_valueHint = new QLabel("输入值（数字或文本）");
    m_value = new QLineEdit();
    m_value->setPlaceholderText("例如 42");
    v2->addWidget(m_valueHint);
    v2->addWidget(m_value);
    root->addWidget(gbData);

    // --- operations ---
    m_opGroup = new QGroupBox("操作");
    auto* grid = new QVBoxLayout(m_opGroup);
    m_insertBtn = new QPushButton("插入");
    m_removeBtn = new QPushButton("删除");
    m_findBtn   = new QPushButton("查找");
    m_clearBtn  = new QPushButton("清空");
    connect(m_insertBtn, &QPushButton::clicked, this, &OperationPanel::onInsert);
    connect(m_removeBtn, &QPushButton::clicked, this, &OperationPanel::onRemove);
    connect(m_findBtn,   &QPushButton::clicked, this, &OperationPanel::onFind);
    connect(m_clearBtn,  &QPushButton::clicked, this, &OperationPanel::onClear);
    grid->addWidget(m_insertBtn);
    grid->addWidget(m_removeBtn);
    grid->addWidget(m_findBtn);
    grid->addWidget(m_clearBtn);
    root->addWidget(m_opGroup);

    // --- deque-specific operations (only visible for Deque) ---
    m_dequeGroup = new QGroupBox("双端专属");
    auto* dgrid = new QVBoxLayout(m_dequeGroup);
    m_pushFrontBtn = new QPushButton("头插 pushFront");
    m_pushBackBtn  = new QPushButton("尾插 pushBack");
    m_popFrontBtn  = new QPushButton("头删 popFront");
    m_popBackBtn   = new QPushButton("尾删 popBack");
    connect(m_pushFrontBtn, &QPushButton::clicked, this, &OperationPanel::onPushFront);
    connect(m_pushBackBtn,  &QPushButton::clicked, this, &OperationPanel::onPushBack);
    connect(m_popFrontBtn,  &QPushButton::clicked, this, &OperationPanel::onPopFront);
    connect(m_popBackBtn,   &QPushButton::clicked, this, &OperationPanel::onPopBack);
    dgrid->addWidget(m_pushFrontBtn);
    dgrid->addWidget(m_pushBackBtn);
    dgrid->addWidget(m_popFrontBtn);
    dgrid->addWidget(m_popBackBtn);
    m_dequeGroup->setVisible(false);
    root->addWidget(m_dequeGroup);

    // --- graph-specific operations (only visible for Graph) ---
    m_graphGroup = new QGroupBox("图操作");
    auto* ggrid = new QVBoxLayout(m_graphGroup);
    m_addVertexBtn = new QPushButton("加顶点 addVertex");
    m_addEdgeBtn   = new QPushButton("加边 addEdge");
    m_bfsBtn       = new QPushButton("广度优先 BFS");
    m_dfsBtn       = new QPushButton("深度优先 DFS");
    m_dijkstraBtn  = new QPushButton("最短路径 Dijkstra");
    m_graphClearBtn = new QPushButton("清空 clear");
    connect(m_addVertexBtn, &QPushButton::clicked,
            this, [this](){ emit operationRequested("addVertex", m_value->text()); });
    connect(m_addEdgeBtn, &QPushButton::clicked,
            this, [this](){ emit operationRequested("addEdge", m_value->text()); });
    connect(m_bfsBtn, &QPushButton::clicked,
            this, [this](){ emit operationRequested("bfs", m_value->text()); });
    connect(m_dfsBtn, &QPushButton::clicked,
            this, [this](){ emit operationRequested("dfs", m_value->text()); });
    connect(m_dijkstraBtn, &QPushButton::clicked,
            this, [this](){ emit operationRequested("dijkstra", m_value->text()); });
    connect(m_graphClearBtn, &QPushButton::clicked,
            this, [this](){ emit operationRequested("clear", ""); });
    ggrid->addWidget(m_addVertexBtn);
    ggrid->addWidget(m_addEdgeBtn);
    ggrid->addWidget(m_bfsBtn);
    ggrid->addWidget(m_dfsBtn);
    ggrid->addWidget(m_dijkstraBtn);
    ggrid->addWidget(m_graphClearBtn);
    m_graphGroup->setVisible(false);
    root->addWidget(m_graphGroup);

    // --- tree traversal operations (only visible for BST) ---
    m_treeGroup = new QGroupBox("树遍历");
    auto* tgrid = new QVBoxLayout(m_treeGroup);
    m_treeBfsBtn = new QPushButton("广度优先 BFS(层序)");
    m_treeDfsBtn = new QPushButton("深度优先 DFS(先序)");
    connect(m_treeBfsBtn, &QPushButton::clicked,
            this, [this](){ emit operationRequested("bfs", m_value->text()); });
    connect(m_treeDfsBtn, &QPushButton::clicked,
            this, [this](){ emit operationRequested("dfs", m_value->text()); });
    tgrid->addWidget(m_treeBfsBtn);
    tgrid->addWidget(m_treeDfsBtn);
    m_treeGroup->setVisible(false);
    root->addWidget(m_treeGroup);

    // --- speed ---
    auto* gbSpeed = new QGroupBox("动画速度");
    auto* v3 = new QVBoxLayout(gbSpeed);
    auto* slider = new QSlider(Qt::Horizontal);
    slider->setRange(25, 400);     // 0.25x .. 4x
    slider->setValue(100);
    auto* speedLabel = new QLabel("1.00x");
    speedLabel->setAlignment(Qt::AlignCenter);
    connect(slider, &QSlider::valueChanged, this, [slider, speedLabel, this](int v) {
        double s = v / 100.0;
        speedLabel->setText(QString::number(s, 'f', 2) + "x");
        onSpeed(v);
    });
    v3->addWidget(slider);
    v3->addWidget(speedLabel);
    root->addWidget(gbSpeed);

    // --- Max Degree (only for BTree / BPlusTree) --- radio buttons like reference UI ---
    m_degreeGroup = new QGroupBox("Max. Degree (阶)");
    auto* ddgrid = new QHBoxLayout(m_degreeGroup);   // horizontal: radios in a row
    m_degreeBtnGroup = new QButtonGroup(this);
    m_degreeBtnGroup->setExclusive(true);
    for (int d = DEGREE_MIN; d <= DEGREE_MAX; ++d) {
        auto* rb = new QRadioButton(QString::number(d));
        if (d == DEGREE_MIN) rb->setChecked(true);  // default: 3
        m_degreeBtnGroup->addButton(rb, d);         // button id = degree value
        m_degreeRadios.push_back(rb);
        ddgrid->addWidget(rb);
    }
    connect(m_degreeBtnGroup, QOverload<int>::of(&QButtonGroup::buttonClicked), this,
        [this](int id) { emit degreeChanged(id); });
    m_degreeGroup->setVisible(false);   // only shown for BTree/BPlusTree
    root->addWidget(m_degreeGroup);

    // --- presets ---
    m_presetBtn = new QPushButton("运行演示序列");
    connect(m_presetBtn, &QPushButton::clicked, this, &OperationPanel::presetRequested);
    root->addWidget(m_presetBtn);

    root->addStretch(1);
    setKindIndex(static_cast<int>(DSKind::SinglyLinkedList));
}

void OperationPanel::buildKindCombo() {
    // 分类下拉：分组标题为不可选项，数据项携带 DSKind（Qt::UserRole），
    // 与枚举顺序解耦，后续增删结构不会破坏映射。
    struct Entry { QString label; DSKind kind; };
    struct Group { QString title; std::vector<Entry> items; };
    std::vector<Group> groups = {
        {"链表类", {
            {"单链表 SinglyLinkedList", DSKind::SinglyLinkedList},
            {"双链表 DoublyLinkedList", DSKind::DoublyLinkedList},
        }},
        {"栈与队列", {
            {"栈 Stack",            DSKind::Stack},
            {"队列 Queue",          DSKind::Queue},
            {"双端队列 Deque",      DSKind::Deque},
            {"阻塞队列 BlockingQueue", DSKind::BlockingQueue},
            {"环形缓冲区 RingBuffer",  DSKind::RingBuffer},
        }},
        {"树结构", {
            {"二叉搜索树 BST",  DSKind::BinarySearchTree},
            {"AVL 平衡树",      DSKind::AVLTree},
            {"红黑树 RedBlackTree", DSKind::RedBlackTree},
            {"B 树 B-Tree",     DSKind::BTree},
            {"B+ 树 B+Tree",    DSKind::BPlusTree},
            {"最小堆 MinHeap",  DSKind::MinHeap},
        }},
        {"哈希与缓存", {
            {"哈希表 HashMap",  DSKind::HashMap},
            {"LRU 缓存 LRUCache", DSKind::LRUCache},
        }},
        {"图", {
            {"图 Graph", DSKind::Graph},
        }},
    };
    for (auto& g : groups) {
        auto* header = new QStandardItem(g.title);
        header->setEnabled(false);
        header->setSelectable(false);
        header->setData(-1, Qt::UserRole);
        QFont hf = header->font(); hf.setBold(true); header->setFont(hf);
        m_kindModel->appendRow(header);
        for (auto& it : g.items) {
            auto* item = new QStandardItem(it.label);
            item->setData(static_cast<int>(it.kind), Qt::UserRole);
            m_kindModel->appendRow(item);
        }
    }
}

void OperationPanel::setKindIndex(int kind) {
    // 避免 switchKind 被重复调用（原本会发生一次额外初始化）。
    QSignalBlocker blocker(m_kind);
    for (int r = 0; r < m_kind->count(); ++r) {
        if (m_kind->itemData(r, Qt::UserRole).toInt() == kind) {
            m_kind->setCurrentIndex(r);
            break;
        }
    }
    relabel(static_cast<DSKind>(kind));
}

int OperationPanel::currentDegree() const {
    QAbstractButton* b = m_degreeBtnGroup->checkedButton();
    if (!b) return DEGREE_MIN;
    return m_degreeBtnGroup->id(b);  // 按钮 id 在创建时设为阶数值
}

void OperationPanel::onKindChanged(int row) {
    int kind = m_kind->itemData(row, Qt::UserRole).toInt();
    if (kind < 0) return;   // 分组标题行，不可选，忽略
    DSKind k = static_cast<DSKind>(kind);
    relabel(k);
    emit kindChanged(kind);
}

void OperationPanel::relabel(DSKind kind) {
    bool isGraph = (kind == DSKind::Graph);
    bool isLRU   = (kind == DSKind::LRUCache);
    bool isBST   = (kind == DSKind::BinarySearchTree);  // 本版仅 BST 实现 BFS/DFS
    bool isBTreeFamily = (kind == DSKind::BTree || kind == DSKind::BPlusTree);
    // 通用操作组对非图隐藏；双端组仅 Deque；图操作组仅 Graph；树遍历组仅 BST；阶数仅 B/B+
    m_opGroup->setVisible(!isGraph);
    m_dequeGroup->setVisible(kind == DSKind::Deque);
    m_graphGroup->setVisible(isGraph);
    m_treeGroup->setVisible(isBST);
    m_degreeGroup->setVisible(isBTreeFamily);
    m_findBtn->setVisible(true);

    // 默认通用标签（链表 / BST / AVL / RB / BTree / B+Tree 用 插入/删除）
    QString insertTxt = "插入", removeTxt = "删除";
    QString hint = "输入值（数字或文本）", ph = "例如 42";
    switch (kind) {
        case DSKind::Stack:
            insertTxt = "压入 push"; removeTxt = "弹出 pop"; break;
        case DSKind::Queue:
        case DSKind::BlockingQueue:
            insertTxt = "入队 enqueue"; removeTxt = "出队 dequeue"; break;
        case DSKind::RingBuffer:
            insertTxt = "写入 write"; removeTxt = "读取 read"; break;
        case DSKind::HashMap:
            insertTxt = "插入 put"; removeTxt = "删除 remove";
            hint = "格式 key:value"; ph = "例如 name:tom"; break;
        case DSKind::MinHeap:
            insertTxt = "插入 push"; removeTxt = "弹出 pop"; break;
        case DSKind::Deque:
            insertTxt = "尾插(默认)"; removeTxt = "头删(默认)";
            hint = "输入值；或用下方双端按钮"; ph = "例如 42"; break;
        default: break;
    }
    m_insertBtn->setText(insertTxt);
    m_removeBtn->setText(removeTxt);
    m_valueHint->setText(hint);
    m_value->setPlaceholderText(ph);

    if (isLRU) {
        m_insertBtn->setText("put 写入(key或key:value)");
        m_removeBtn->setText("get 读取(命中移到队首)");
        m_findBtn->setVisible(false);
        m_valueHint->setText("输入 key（如 A）或 key:value（如 A:x）");
        m_value->setPlaceholderText("A 或 A:x");
    }
    if (isGraph) {
        m_valueHint->setText("加顶点填标签(如 A)；加边填 u-v 或 u-v:w(如 A-B:5)；遍历填起点(可空)");
        m_value->setPlaceholderText("A 或 A-B:5");
    }
    if (isBST) {
        m_valueHint->setText("BFS/DFS 起点可留空（从根开始），或填子树根的值（如 30）");
        m_value->setPlaceholderText("（可空）或 30");
    }
}

} // namespace dsv
