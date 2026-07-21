#include "MainWindow.h"
#include "../core/Factory.h"
#include <algorithm>
#include <QApplication>
#include <QGraphicsView>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QMenuBar>
#include <QMenu>
#include <QAction>
#include <QLabel>
#include <QStatusBar>
#include <QPair>
#include <QPluginLoader>
#include <QDir>
#include <QFile>
#include <QDebug>
#include <QDockWidget>

namespace dsv {

MainWindow::MainWindow(QWidget* parent) : QMainWindow(parent) {
    setWindowTitle("数据结构可视化演示工具  DSVisualizer");
    resize(1180, 720);

    // scene + view (DSSceneView adds middle-button pan + Ctrl+wheel zoom)
    m_scene = new DSScene(this);
    m_view = new DSSceneView(m_scene, this);
    m_view->setBackgroundBrush(QColor("#F7F8FA"));
    m_view->setMinimumSize(400, 400);

    m_animator = new StepAnimator(m_scene, this);

    // panels
    m_ops = new OperationPanel(this);
    m_log = new LogViewer(this);

    m_header = new QLabel();
    m_header->setWordWrap(true);
    QFont hf = m_header->font(); hf.setPointSize(13); hf.setBold(true);
    m_header->setFont(hf);

    // layout
    auto* center = new QWidget(this);
    auto* cv = new QVBoxLayout(center);
    cv->addWidget(m_header);
    cv->addWidget(m_view, 1);

    auto* root = new QHBoxLayout();
    root->addWidget(m_ops, 0);
    root->addWidget(center, 1);
    root->addWidget(m_log, 0);
    auto* cw = new QWidget(this);
    cw->setLayout(root);
    setCentralWidget(cw);

    // menu
    auto* viewMenu = menuBar()->addMenu("视图");
    auto* themeAct = new QAction("切换深色 / 浅色主题", this);
    connect(themeAct, &QAction::triggered, this, &MainWindow::toggleTheme);
    viewMenu->addAction(themeAct);

    // status bar
    m_status = new QLabel();
    statusBar()->addWidget(m_status);

    // connections
    connect(m_ops, &OperationPanel::kindChanged, this, &MainWindow::switchKind);
    connect(m_ops, &OperationPanel::operationRequested, this, &MainWindow::runOperation);
    connect(m_ops, &OperationPanel::presetRequested, this, &MainWindow::runPreset);
    connect(m_ops, &OperationPanel::speedChanged, m_animator, &StepAnimator::setSpeed);
    connect(m_ops, &OperationPanel::degreeChanged, this, &MainWindow::onDegreeChanged);

    connect(m_log, &LogViewer::play, m_animator, &StepAnimator::play);
    connect(m_log, &LogViewer::pause, m_animator, &StepAnimator::pause);
    connect(m_log, &LogViewer::stepNext, m_animator, &StepAnimator::next);
    connect(m_log, &LogViewer::stepPrev, m_animator, &StepAnimator::prev);
    connect(m_log, &LogViewer::undo, this, &MainWindow::undo);
    connect(m_log, &LogViewer::redo, this, &MainWindow::redo);

    connect(m_animator, &StepAnimator::frameChanged, this, &MainWindow::onFrameChanged);
    connect(m_animator, &StepAnimator::playStateChanged, m_log, &LogViewer::setPlaying);

    // initial structure
    switchKind(static_cast<int>(DSKind::SinglyLinkedList));
    updateStatus();

    // 外挂：尝试加载 AI 讲解插件（DLL 不存在 / 加载失败 → 静默跳过，程序照常运行）
    loadAiPlugin();
}

void MainWindow::switchKind(int index) {
    m_kind = static_cast<DSKind>(index);
    m_ds = createDataStructure(m_kind);
    m_history.clear();
    m_values.clear();
    m_redo.clear();
    m_scene->setKind(m_kind);
    // 切换时彻底清空画布：先停动画（避免删图元时动画仍持有旧指针），
    // 再清场景，最后复位视图缩放，确保图形界面完全重置。
    m_animator->stop();
    m_animator->setFrames({});
    m_scene->clearAll();
    m_view->resetTransform();
    m_ops->setKindIndex(index);
    m_header->setText(QString::fromStdString(m_ds->name()) + "  —  " +
                      QString::fromStdString(m_ds->description()));
    m_log->setLog({});
    m_log->setDescription("已加载 " + QString::fromStdString(m_ds->name()) +
                          "，输入数据并点击操作开始演示。");
    m_log->setProgress(0, 0);
    m_opCount = 0;
    updateStatus();
}

void MainWindow::runOperation(const QString& op, const QString& value) {
    if (!m_ds) return;
    std::string v = value.toStdString();

    // ---- Graph-specific operations ----
    if (op == "addVertex") {
        m_redo.clear();
        std::vector<std::string> snapshot = m_values;
        FrameList frames = m_ds->addVertex(v);
        if (!frames.empty()) {
            m_history.push_back(snapshot);
            if (!v.empty()) m_values.push_back(v);
            loadFrames(std::move(frames));
        }
        return;
    }
    if (op == "addEdge") {
        if (v.empty()) { m_log->setDescription("请在左侧输入边，如 A-B 或 A-B:5"); return; }
        m_redo.clear();
        std::vector<std::string> snapshot = m_values;
        FrameList frames = m_ds->addEdge(v);
        if (!frames.empty()) { m_history.push_back(snapshot); loadFrames(std::move(frames)); }
        return;
    }
    if (op == "bfs" || op == "dfs" || op == "dijkstra") {
        // read-only traversals: no structure change, no undo snapshot
        FrameList frames;
        if (op == "bfs")          frames = m_ds->bfs(v);
        else if (op == "dfs")     frames = m_ds->dfs(v);
        else                      frames = m_ds->dijkstra(v);
        if (!frames.empty()) loadFrames(std::move(frames));
        return;
    }

    if ((op == "insert" || op == "find" || op == "pushFront" || op == "pushBack")
        && value.isEmpty()) {
        m_log->setDescription("请先在左侧输入一个值。");
        return;
    }
    // 查找不改变结构，不记录撤销快照
    if (op == "find") {
        FrameList frames = m_ds->find(value.toStdString());
        if (!frames.empty()) loadFrames(std::move(frames));
        return;
    }
    // 变更操作：操作前对当前值集合做一次快照；新操作清空 redo 栈
    m_redo.clear();
    std::vector<std::string> snapshot = m_values;
    int before = m_ds->size();
    FrameList frames;
    if (op == "insert")          frames = m_ds->insert(v);
    else if (op == "remove")     frames = m_ds->remove(v);
    else if (op == "clear")      frames = m_ds->clear();
    else if (op == "pushFront")  frames = m_ds->pushFront(v);
    else if (op == "pushBack")   frames = m_ds->pushBack(v);
    else if (op == "popFront")   frames = m_ds->popFront();
    else if (op == "popBack")    frames = m_ds->popBack();
    if (frames.empty()) return;
    int after = m_ds->size();
    if (op == "clear") {
        m_history.push_back(snapshot);
        m_values.clear();
    } else if (op == "pushFront") {            // 双端：前插
        m_history.push_back(snapshot);
        m_values.insert(m_values.begin(), v);
    } else if (op == "pushBack") {             // 双端：后插
        m_history.push_back(snapshot);
        m_values.push_back(v);
    } else if (op == "popFront") {             // 双端：前删
        m_history.push_back(snapshot);
        if (!m_values.empty()) m_values.erase(m_values.begin());
    } else if (op == "popBack") {              // 双端：后删
        m_history.push_back(snapshot);
        if (!m_values.empty()) m_values.pop_back();
    } else if (op == "remove" && m_kind == DSKind::Deque) {
        // Deque.remove 即 popFront，按位置撤销
        m_history.push_back(snapshot);
        if (!m_values.empty()) m_values.erase(m_values.begin());
    } else if (op == "remove" && (m_kind == DSKind::BlockingQueue)) {
        // BlockingQueue.remove = dequeue (remove front, value may be empty)
        m_history.push_back(snapshot);
        if (!m_values.empty()) m_values.erase(m_values.begin());
    } else if (op == "remove" && m_kind == DSKind::RingBuffer) {
        // RingBuffer.remove = read (remove front, value may be empty)
        m_history.push_back(snapshot);
        if (!m_values.empty()) m_values.erase(m_values.begin());
    } else if (op == "insert" && m_kind == DSKind::RingBuffer && after <= before) {
        // RingBuffer insert when full: overwrites oldest → m_values: drop front, add new
        m_history.push_back(snapshot);
        if (!m_values.empty()) m_values.erase(m_values.begin());
        m_values.push_back(v);
    } else if (op == "insert" && m_kind == DSKind::LRUCache) {
        // LRU put：命中则移到队首(MRU)，未命中则插入队首；超容量淘汰队尾
        m_history.push_back(snapshot);
        auto it = std::find(m_values.begin(), m_values.end(), v);
        if (it != m_values.end()) m_values.erase(it);   // move to front
        m_values.insert(m_values.begin(), v);            // MRU first
        if ((int)m_values.size() > LRUCache::Capacity) m_values.pop_back();  // evict LRU tail
    } else if (op == "remove" && m_kind == DSKind::LRUCache) {
        // LRU get：命中则移到队首（MRU）
        m_history.push_back(snapshot);
        auto it = std::find(m_values.begin(), m_values.end(), v);
        if (it != m_values.end()) { m_values.erase(it); m_values.insert(m_values.begin(), v); }
    } else if (after > before) {              // 真正新增（去重后）
        m_history.push_back(snapshot);
        m_values.push_back(v);
    } else if (after < before) {              // 真正删除
        m_history.push_back(snapshot);
        auto it = std::find(m_values.begin(), m_values.end(), v);
        if (it != m_values.end()) m_values.erase(it);
    }
    // 去重失败 / 删除不存在 等无实际变更：不记录快照
    loadFrames(std::move(frames));
}

void MainWindow::runPreset() {
    if (!m_ds) return;
    std::vector<std::string> snapshot = m_values;   // 整个演示序列作为一次可撤销单元
    m_ds->clear();
    m_values.clear();
    m_redo.clear();  // 新操作清空重做栈
    auto seq = buildPreset(m_kind);
    FrameList all;
    for (const auto& step : seq) {
        FrameList fr;
        std::string v = step.second.toStdString();
        if (step.first == "addVertex") {
            fr = m_ds->addVertex(v);
            if (!v.empty()) m_values.push_back(v);
        } else if (step.first == "addEdge") {
            fr = m_ds->addEdge(v);   // 边不计入撤销值序列
        } else if (step.first == "bfs") {
            fr = m_ds->bfs(v);
        } else if (step.first == "dfs") {
            fr = m_ds->dfs(v);
        } else if (step.first == "dijkstra") {
            fr = m_ds->dijkstra(v);
        } else if (step.first == "insert") {
            int before = m_ds->size();
            fr = m_ds->insert(v);
            int after = m_ds->size();
            if (m_kind == DSKind::RingBuffer && after == before && !m_values.empty()) {
                // 满时覆写最旧：删队首 + 加新值
                m_values.erase(m_values.begin());
                m_values.push_back(v);
            } else if (m_kind == DSKind::LRUCache) {
                auto it = std::find(m_values.begin(), m_values.end(), v);
                if (it != m_values.end()) m_values.erase(it);   // move to front
                m_values.insert(m_values.begin(), v);            // MRU first
                if ((int)m_values.size() > LRUCache::Capacity) m_values.pop_back();  // evict
            } else if (after > before) {
                // 真正新增
                m_values.push_back(v);
            }
            // BlockingQueue 满时阻塞拒绝：after == before，不加入 m_values
        } else if (step.first == "remove") {
            fr = m_ds->remove(v);
            if (m_kind == DSKind::LRUCache) {
                // LRU get：命中移到队首
                auto it = std::find(m_values.begin(), m_values.end(), v);
                if (it != m_values.end()) { m_values.erase(it); m_values.insert(m_values.begin(), v); }
            } else if (!v.empty()) {
                auto it = std::find(m_values.begin(), m_values.end(), v);
                if (it != m_values.end()) m_values.erase(it);
            } else if (!m_values.empty()) {
                m_values.erase(m_values.begin());   // 队列/循环队列：出队即删队首
            }
        } else if (step.first == "find") {
            fr = m_ds->find(v);
        } else if (step.first == "pushFront") {
            fr = m_ds->pushFront(v);
            m_values.insert(m_values.begin(), v);
        } else if (step.first == "pushBack") {
            fr = m_ds->pushBack(v);
            m_values.push_back(v);
        } else if (step.first == "popFront") {
            fr = m_ds->popFront();
            if (!m_values.empty()) m_values.erase(m_values.begin());
        } else if (step.first == "popBack") {
            fr = m_ds->popBack();
            if (!m_values.empty()) m_values.pop_back();
        }
        for (auto& f : fr) all.push_back(std::move(f));
    }
    m_history.push_back(snapshot);        // 撤销可回退到演示前的状态
    if (!all.empty()) loadFrames(std::move(all));
}

void MainWindow::undo() {
    if (m_history.empty()) {
        m_log->setDescription("没有可撤销的操作。");
        return;
    }
    // 当前状态压入 redo 栈（之后可以用 ▶| 恢复）
    m_redo.push_back(m_values);
    // 弹出 undo 栈恢复
    m_values = m_history.back();
    m_history.pop_back();
    rebuildAndShow("↶ 撤销上一步操作");
}

void MainWindow::redo() {
    if (m_redo.empty()) {
        // redo 为空时，▶| 退化为跳到末帧
        m_animator->toEnd();
        return;
    }
    // 当前状态压回 undo 栈
    m_history.push_back(m_values);
    // 弹出 redo 栈恢复
    m_values = m_redo.back();
    m_redo.pop_back();
    rebuildAndShow("▶| 重做操作");
}

void MainWindow::rebuildAndShow(const QString& actionLabel) {
    // 依据值列表重建结构（按插入顺序重放 insert，可恢复原树形）
    m_ds->clear();
    for (const auto& v : m_values) m_ds->insert(v);
    // 展示重建后的当前状态（单帧，差异动画呈现"回退/重做"效果）
    FrameList fl = { m_ds->currentFrame() };
    m_log->setLog({ actionLabel,
                    QString::fromStdString(m_ds->currentFrame().description) });
    m_animator->setFrames(std::move(fl));
    m_animator->toEnd();
    m_opCount = std::max(0, m_opCount - 1);
    updateStatus();
}

void MainWindow::onDegreeChanged(int maxDegree) {
    if (!m_ds) return;
    if (m_kind != DSKind::BTree && m_kind != DSKind::BPlusTree) return;

    // 保存当前值 → 用新 degree 重建数据结构 → 重插所有值
    auto currentValues = m_values;   // copy
    m_animator->stop();
    m_animator->setFrames({});
    m_scene->clearAll();
    m_view->resetTransform();

    // 用新 degree 创建新数据结构
    m_ds = createDataStructure(m_kind, maxDegree);
    m_scene->setKind(m_kind);

    // 重插所有值（如果有的话）
    for (const auto& v : currentValues) {
        m_ds->insert(v);
    }
    m_values = currentValues;

    // 展示当前状态
    FrameList fl = { m_ds->currentFrame() };
    m_log->setLog({ QString("Max Degree 改为 %1，已重建数据结构").arg(maxDegree),
                    QString::fromStdString(m_ds->currentFrame().description) });
    m_animator->setFrames(std::move(fl));
    m_animator->toEnd();
    updateStatus();
}

QVector<QPair<QString, QString>> MainWindow::buildPreset(DSKind kind) const {
    using P = QPair<QString, QString>;
    switch (kind) {
        case DSKind::SinglyLinkedList:
        case DSKind::DoublyLinkedList:
            return { P("insert","10"), P("insert","20"), P("insert","30"),
                     P("insert","15"), P("remove","20"), P("find","15") };
        case DSKind::Stack:
            return { P("insert","1"), P("insert","2"), P("insert","3"),
                     P("remove",""), P("insert","4") };
        case DSKind::Queue:
            return { P("insert","A"), P("insert","B"), P("insert","C"),
                     P("remove",""), P("insert","D") };
        case DSKind::BinarySearchTree:
            return { P("insert","50"), P("insert","30"), P("insert","70"),
                     P("insert","20"), P("insert","40"), P("insert","60"),
                     P("insert","80"), P("find","40"),
                     P("bfs",""), P("dfs","") };
        case DSKind::AVLTree:
            // triggers multiple rotations
            return { P("insert","30"), P("insert","20"), P("insert","10"),
                     P("insert","40"), P("insert","50"), P("insert","60"),
                     P("insert","25"), P("remove","30") };
        case DSKind::HashMap:
            return { P("insert","name:tom"), P("insert","age:18"),
                     P("insert","city:ny"), P("find","age"), P("remove","city") };
        case DSKind::MinHeap:
            return { P("insert","5"), P("insert","3"), P("insert","8"),
                     P("insert","1"), P("insert","9"), P("insert","2"),
                     P("remove","") };
        case DSKind::RedBlackTree:
            // triggers recolor (uncle red) and rotations
            return { P("insert","50"), P("insert","30"), P("insert","70"),
                     P("insert","20"), P("insert","40"), P("insert","60"),
                     P("insert","80"), P("insert","10"), P("insert","25") };
        case DSKind::Deque:
            return { P("pushFront","1"), P("pushBack","2"), P("pushFront","3"),
                     P("pushBack","4"), P("popFront",""), P("popBack","") };
        case DSKind::BlockingQueue:
            // 教科书阻塞队列演示：7次入队（填满可用空间）+ 1次满时阻塞提示 + 2次出队 + 2次再入队（展示环绕）
            return { P("insert","1"), P("insert","2"), P("insert","3"),
                     P("insert","4"), P("insert","5"), P("insert","6"),
                     P("insert","7"),  // 此时 (rear+1)%8==front → 满！
                     P("insert","X"),  // 满时阻塞等待提示
                     P("remove",""), P("remove",""),  // front 后移 2 步，腾出空间
                     P("insert","8"), P("insert","9") }; // 环绕入队
        case DSKind::BTree:
            return { P("insert","10"), P("insert","20"), P("insert","5"),
                     P("insert","30"), P("insert","15"), P("insert","25"),
                     P("insert","35"), P("remove","20"), P("find","25") };
        case DSKind::BPlusTree:
            return { P("insert","10"), P("insert","20"), P("insert","5"),
                     P("insert","30"), P("insert","15"), P("insert","25"),
                     P("insert","35"), P("remove","20"), P("find","15") };
        case DSKind::RingBuffer:
            // 环形缓冲区演示：8次写入填满 + 覆写（最旧被丢弃） + 2次读取 + 再写入
            return { P("insert","A"), P("insert","B"), P("insert","C"),
                     P("insert","D"), P("insert","E"), P("insert","F"),
                     P("insert","G"), P("insert","H"),  // 满！
                     P("insert","I"),  // 覆写 A（最旧被丢弃）
                     P("insert","J"),  // 覆写 B
                     P("remove",""), P("remove","") };
        case DSKind::Graph:
            // 演示图：6 个顶点 + 带权边，最后跑 BFS/DFS/Dijkstra
            return { P("addVertex","A"), P("addVertex","B"), P("addVertex","C"),
                     P("addVertex","D"), P("addVertex","E"), P("addVertex","F"),
                     P("addEdge","A-B:4"), P("addEdge","A-C:2"), P("addEdge","B-C:5"),
                     P("addEdge","B-D:10"), P("addEdge","C-D:3"), P("addEdge","C-E:8"),
                     P("addEdge","D-E:11"), P("addEdge","D-F:6"), P("addEdge","E-F:1"),
                     P("bfs","A"), P("dfs","A"), P("dijkstra","A") };
        case DSKind::LRUCache:
            // LRU 演示：填满容量4 → 超出淘汰最旧 → get 命中移到队首 → 再插入淘汰
            return { P("insert","A"), P("insert","B"), P("insert","C"), P("insert","D"),
                     P("insert","E"),   // 超出容量4 → 淘汰 A(LRU队尾)
                     P("remove","B"),   // get B → 移到 MRU 队首
                     P("insert","F") }; // 淘汰 C(LRU队尾)
        default: return {};
    }
}

void MainWindow::loadFrames(FrameList frames) {
    QStringList log;
    for (const auto& f : frames) log.append(QString::fromStdString(f.description));
    m_log->setLog(log);
    m_animator->setFrames(std::move(frames));
    m_animator->play();
    m_opCount++;
    updateStatus();
}

void MainWindow::onFrameChanged(int index, int total, const QString& desc) {
    m_log->setDescription(desc);
    m_log->setProgress(index, total);
    m_log->highlightCurrent(index);
}

void MainWindow::toggleTheme() {
    m_dark = !m_dark;
    applyTheme(m_dark);
}

void MainWindow::loadAiPlugin() {
    // 外挂核心：DLL 不在这些候选路径中 → 直接返回，主程序零 AI 依赖照常运行
    QString exeDir = QCoreApplication::applicationDirPath();
    QStringList candidates = {
        exeDir + "/plugins/aichatplugin.dll",
        exeDir + "/aichatplugin.dll",
        QDir(exeDir).filePath("../src/plugins/aichatplugin.dll"),
        QDir(exeDir).filePath("../../src/plugins/aichatplugin.dll"),
        QDir(exeDir).filePath("../../../src/plugins/aichatplugin.dll"),
    };
    QString path;
    for (const auto& c : candidates) {
        if (QFile::exists(c)) { path = c; break; }
    }
    if (path.isEmpty()) {
        qDebug() << "[AI] aichatplugin.dll not found in" << candidates
                 << "-> AI tutor disabled (program runs normally).";
        return;
    }

    // 必须保持 loader 存活，否则插件在 MainWindow 析构前就被卸载，Dock 控件悬空崩溃
    m_aiLoader = new QPluginLoader(path, this);
    QObject* inst = m_aiLoader->instance();
    if (!inst) {
        qDebug() << "[AI] plugin load failed:" << m_aiLoader->errorString();
        return;
    }
    m_aiPlugin = qobject_cast<AIPluginInterface*>(inst);
    if (!m_aiPlugin) {
        qDebug() << "[AI] plugin does not implement AIPluginInterface";
        return;
    }

    QWidget* dock = m_aiPlugin->createDock(m_animator, m_scene);
    if (!dock) {
        qDebug() << "[AI] createDock() returned null";
        return;
    }
    m_aiDock = new QDockWidget("AI 讲解助教", this);
    m_aiDock->setWidget(dock);
    m_aiDock->setMinimumWidth(300);
    m_aiDock->setAllowedAreas(Qt::RightDockWidgetArea | Qt::LeftDockWidgetArea);
    addDockWidget(Qt::RightDockWidgetArea, m_aiDock);
    qDebug() << "[AI] tutor plugin loaded from" << path;
}

void MainWindow::applyTheme(bool dark) {
    if (dark) {
        QPalette p = qApp->palette();
        p.setColor(QPalette::Window, QColor("#20242E"));
        p.setColor(QPalette::WindowText, QColor("#E6E6E6"));
        p.setColor(QPalette::Base, QColor("#2A2F3A"));
        p.setColor(QPalette::Text, QColor("#E6E6E6"));
        p.setColor(QPalette::Button, QColor("#333A47"));
        p.setColor(QPalette::ButtonText, QColor("#E6E6E6"));
        qApp->setPalette(p);
        m_view->setBackgroundBrush(QColor("#20242E"));
    } else {
        qApp->setPalette(QPalette());
        m_view->setBackgroundBrush(QColor("#F7F8FA"));
    }
}

void MainWindow::updateStatus() {
    m_status->setText(QString("操作次数: %1   内存: std::unique_ptr 管理（零泄漏）   结构: %2")
        .arg(m_opCount).arg(QString::fromStdString(kindToString(m_kind))));
}

} // namespace dsv
