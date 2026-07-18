#include "DSScene.h"
#include "VisualNode.h"
#include "VisualEdge.h"
#include "LayoutEngine.h"
#include <QPropertyAnimation>
#include <QTimer>
#include <QGraphicsView>
#include <algorithm>
#include <unordered_set>
#include <set>

namespace dsv {

DSScene::DSScene(QObject* parent) : QGraphicsScene(parent) {}

void DSScene::clearAll() {
    // 先停止所有动画（子对象 QPropertyAnimation），再删除图元
    // 动画可能以 DeleteWhenStopped 启动，stop() 会自动删除，所以先收集指针再逐一停止
    for (auto& kv : m_nodes) {
        QList<QPropertyAnimation*> anims;
        for (auto* child : kv.second->children()) {
            auto* anim = qobject_cast<QPropertyAnimation*>(child);
            if (anim) anims.append(anim);
        }
        // 关键：先停止动画并把它从 item 上 detach，否则 item 析构会级联删除
        // 这个子动画，而 DeleteWhenStopped 的 deleteLater 稍后再次删除它 → 双重释放崩溃。
        // detach 后由 DeleteWhenStopped 的 deleteLater 安全回收，不再受 item 析构影响。
        for (auto* anim : anims) { anim->stop(); anim->setParent(nullptr); }
        removeItem(kv.second);
        delete kv.second;
    }
    for (auto& kv : m_edges) {
        QList<QPropertyAnimation*> anims;
        for (auto* child : kv.second->children()) {
            auto* anim = qobject_cast<QPropertyAnimation*>(child);
            if (anim) anims.append(anim);
        }
        for (auto* anim : anims) { anim->stop(); anim->setParent(nullptr); }
        removeItem(kv.second);
        delete kv.second;
    }
    m_nodes.clear();
    m_edges.clear();
    m_lastNodeCount = -1;
}

void DSScene::stopPropertyAnimations(QObject* obj, const QByteArray& propName) {
    // 查找并停止 obj 上正在运行的同属性 QPropertyAnimation 子对象
    // 这是防止同一属性上两个动画同时运行导致冲突的关键措施
    // 注意：旧动画可能以 DeleteWhenStopped 模式启动，stop() 会自动删除它
    // 所以不能用 deleteLater() 二次删除，只需 stop() 即可
    // 先收集指针再停止，避免迭代时 DeleteWhenStopped 修改 children() 列表
    QList<QPropertyAnimation*> toStop;
    for (auto* child : obj->children()) {
        auto* anim = qobject_cast<QPropertyAnimation*>(child);
        if (anim && anim->propertyName() == propName && anim->state() != QAbstractAnimation::Stopped) {
            toStop.append(anim);
        }
    }
    for (auto* anim : toStop) anim->stop();
}

void DSScene::animate(QObject* obj, const char* prop, const QVariant& end,
                      int dur, bool animated) {
    if (!animated) {
        // 非动画模式：先停止可能存在的旧动画，再直接设置属性值
        stopPropertyAnimations(obj, QByteArray(prop));
        obj->setProperty(prop, end);
        return;
    }
    // 动画模式：先停止同属性的旧动画，避免双动画冲突
    QByteArray propName(prop);
    stopPropertyAnimations(obj, propName);

    auto* a = new QPropertyAnimation(obj, prop, obj);
    a->setDuration(dur);
    a->setEndValue(end);
    a->start(QAbstractAnimation::DeleteWhenStopped);  // 动画停止时自动删除，无需手动 deleteLater
}

void DSScene::fitView(const std::unordered_map<int, QPointF>& pos) {
    if (pos.empty()) return;
    if (views().isEmpty()) return;
    bool widerNode = (m_kind == DSKind::BTree || m_kind == DSKind::BPlusTree);
    qreal nodeW = widerNode ? 140 : 58;
    qreal nodeH = widerNode ? 48 : 40;
    QRectF r;
    for (const auto& kv : pos) r = r.united(QRectF(kv.second, QSizeF(nodeW, nodeH)));
    views().first()->fitInView(r.adjusted(-60, -60, 60, 60), Qt::KeepAspectRatio);
}

void DSScene::applyFrame(const Frame& frame, bool animated) {
    const int DUR = animated ? 340 : 0;
    auto pos = LayoutEngine::layout(m_kind, frame, m_viewW, m_viewH);

    // ---- Phase 1: compute what's present in this frame ----
    std::unordered_set<int> present;
    for (const auto& vn : frame.nodes) present.insert(vn.id);
    std::set<std::pair<int,int>> presentEdges;
    for (const auto& e : frame.edges)
        presentEdges.insert({e.fromId, e.toId});

    // ---- Phase 2: remove stale edges FIRST (before touching nodes) ----
    for (auto it = m_edges.begin(); it != m_edges.end(); ) {
        if (presentEdges.find(it->first) == presentEdges.end()) {
            VisualEdge* item = it->second;
            // 立即删除旧边：边不拥有子对象，不会触发级联 deleteLater 崩溃
            removeItem(item);
            delete item;
            it = m_edges.erase(it);
        } else ++it;
    }

    // ---- Phase 3: remove stale nodes (SYNCHRONOUS immediate delete) ----
    // 关键安全措施：节点删除必须同步完成，不能使用 deleteLater 动画淡出。
    // 原因：StepAnimator 自动播放时帧间隔约750ms，但动画持续340ms。
    // 如果节点用 deleteLater 淡出，在340ms窗口内旧节点仍在场景中但已从 m_nodes 移除，
    // 下一帧可能创建同 ID 的新节点，造成 QGraphicsScene 中两个同位置图元冲突。
    // 同步删除确保旧图元在 applyFrame 返回时已完全消失，新帧处理无冲突。
    for (auto it = m_nodes.begin(); it != m_nodes.end(); ) {
        if (present.find(it->first) == present.end()) {
            VisualNode* item = it->second;
            // 先收集所有动画指针（避免迭代 children 时因 DeleteWhenStopped 删除而修改列表）
            QList<QPropertyAnimation*> anims;
            for (auto* child : item->children()) {
                auto* anim = qobject_cast<QPropertyAnimation*>(child);
                if (anim) anims.append(anim);
            }
            // 停止动画并 detach：DeleteWhenStopped 的 deleteLater 会安全回收动画，
            // 避免 item 析构级联删除动画导致的双重释放。
            for (auto* anim : anims) { anim->stop(); anim->setParent(nullptr); }
            removeItem(item);
            delete item;   // 同步删除，无延迟
            it = m_nodes.erase(it);
        } else ++it;
    }

    // ---- Phase 4: create / update nodes ----
    bool widerNode = (m_kind == DSKind::BTree || m_kind == DSKind::BPlusTree);
    for (const auto& vn : frame.nodes) {
        VisualNode* item = m_nodes[vn.id];
        if (!item) {
            item = new VisualNode();
            item->id = vn.id;
            item->setWider(widerNode);
            item->setZValue(2);
            addItem(item);
            m_nodes[vn.id] = item;
            connect(item, &VisualNode::nodeClicked, this, &DSScene::nodeClicked);
            QPointF p = pos[vn.id];
            item->setNodePos(p);
            if (animated) { item->setNodeScale(0.0); animate(item, "nodeScale", 1.0, DUR, true); }
        } else {
            QPointF p = pos[vn.id];
            if (animated) animate(item, "nodePos", QVariant::fromValue(p), DUR, true);
            else item->setNodePos(p);
        }
        item->value = QString::fromStdString(vn.value);
        item->sublabel = QString::fromStdString(vn.sublabel);
        item->update();

        QColor fill = (vn.id < 0) ? QColor("#B0BEC5") : QColor("#EDE7F6");
        if (!vn.color.empty()) fill = QColor(QString::fromStdString(vn.color));
        if (std::find(frame.highlightIds.begin(), frame.highlightIds.end(), vn.id)
                != frame.highlightIds.end())
            fill = QColor(QString::fromStdString(frame.highlightColor));
        if (animated) animate(item, "fillColor", QVariant::fromValue(fill), DUR, true);
        else item->setFillColor(fill);
    }

    // ---- Phase 5: create / update edges (all referenced nodes guaranteed to exist) ----
    for (const auto& e : frame.edges) {
        std::pair<int,int> key = {e.fromId, e.toId};
        VisualEdge* item = m_edges[key];
        // ★ 统一使用 layout 目标坐标（不混用屏幕坐标），确保新旧边行为一致
        QPointF tp1 = pos[e.fromId], tp2 = pos[e.toId];
        if (!item) {
            item = new VisualEdge();
            item->kind = QString::fromStdString(e.kind);
            item->setZValue(1);
            addItem(item);
            m_edges[key] = item;
            // ★ 新建边：初始端点设为目标布局位置（与旧边统一来源）
            // 如果需要动画，从当前节点实际位置（或目标位置）开始动画到目标位置
            VisualNode* f = m_nodes[e.fromId]; VisualNode* t = m_nodes[e.toId];
            QPointF fromPos = f ? f->nodePos() : tp1;
            QPointF toPos   = t ? t->nodePos() : tp2;
            item->setP1(fromPos); item->setP2(toPos);
            if (animated) {
                // ★ 关键修复：新建边不仅要 fade-in，还要做位置动画！
                // 否则节点移动 340ms 期间边端点固定不动 → 脱节/闪烁/卡顿
                item->setEdgeOpacity(0.0);
                animate(item, "edgeOpacity", 1.0, DUR, true);
                animate(item, "p1", QVariant::fromValue(tp1), DUR, true);
                animate(item, "p2", QVariant::fromValue(tp2), DUR, true);
            } else {
                item->setP1(tp1); item->setP2(tp2);
                item->setEdgeOpacity(1.0);
            }
        } else {
            if (animated) {
                animate(item, "p1", QVariant::fromValue(tp1), DUR, true);
                animate(item, "p2", QVariant::fromValue(tp2), DUR, true);
            } else { item->setP1(tp1); item->setP2(tp2); }
        }
    }

    // fit only when the structure's size changes (avoids per-step zoom jumps)
    if ((int)present.size() != m_lastNodeCount) {
        fitView(pos);
        m_lastNodeCount = static_cast<int>(present.size());
    }
}

} // namespace dsv
