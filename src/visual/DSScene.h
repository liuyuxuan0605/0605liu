#pragma once
#include <QGraphicsScene>
#include <unordered_map>
#include <map>
#include "../core/Common.h"
#include "VisualNode.h"
#include "VisualEdge.h"

namespace dsv {

// Integrates a FrameList with the Qt graphics scene: diffs consecutive
// frames and animates node/edge creation, movement, highlighting and removal.
class DSScene : public QGraphicsScene {
    Q_OBJECT
public:
    explicit DSScene(QObject* parent = nullptr);

    void setKind(DSKind kind) { m_kind = kind; }
    void setViewSize(double w, double h) { m_viewW = w; m_viewH = h; }

    // Render a single frame. `animated` controls transition vs instant set.
    void applyFrame(const Frame& frame, bool animated);

    // Wipe everything (used when switching data structure).
    void clearAll();

signals:
    void nodeClicked(int id);

private:
    void animate(QObject* obj, const char* prop, const QVariant& end, int dur, bool animated);
    void stopPropertyAnimations(QObject* obj, const QByteArray& propName);
    void fitView(const std::unordered_map<int, QPointF>& pos);

    DSKind m_kind = DSKind::SinglyLinkedList;
    double m_viewW = 920, m_viewH = 600;
    std::unordered_map<int, VisualNode*> m_nodes;
    std::map<std::pair<int,int>, VisualEdge*> m_edges;
    int m_lastNodeCount = -1;
};

} // namespace dsv
