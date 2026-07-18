#pragma once
#include <QGraphicsObject>
#include <QGraphicsItem>
#include <QPainter>
#include <QColor>
#include <cmath>

// A visualized edge (pointer / link). Endpoints animate so the line stays
// attached to its nodes as they move.
class VisualEdge : public QGraphicsObject {
    Q_OBJECT
    Q_PROPERTY(QPointF p1 READ p1 WRITE setP1)
    Q_PROPERTY(QPointF p2 READ p2 WRITE setP2)
    Q_PROPERTY(qreal edgeOpacity READ edgeOpacity WRITE setEdgeOpacity)
public:
    explicit VisualEdge(QGraphicsItem* parent = nullptr) : QGraphicsObject(parent) {}

    QRectF boundingRect() const override {
        qreal x1 = qMin(p1_.x(), p2_.x()), y1 = qMin(p1_.y(), p2_.y());
        qreal x2 = qMax(p1_.x(), p2_.x()), y2 = qMax(p1_.y(), p2_.y());
        return QRectF(x1 - 24, y1 - 24, (x2 - x1) + 48, (y2 - y1) + 48);
    }

    void paint(QPainter* p, const QStyleOptionGraphicsItem*, QWidget*) override {
        // ★ 使用缓存的 borderPoint，避免每帧重复 sqrt
        if (!m_borderValid) {
            m_cachedA = borderPoint(p1_, p2_);
            m_cachedB = borderPoint(p2_, p1_);
            m_borderValid = true;
        }
        QPointF a = m_cachedA, b = m_cachedB;
        if (a == b) return;
        p->setRenderHint(QPainter::Antialiasing);
        // 无向边（kind=="edge"，用于图）：蓝色、无箭头
        bool undirected = (kind == "edge");
        QColor col = undirected ? QColor("#42A5F5")
                                : (kind == "prev" ? QColor("#AB47BC") : QColor("#78909C"));
        p->setPen(QPen(col, 2));
        p->drawLine(a, b);
        if (!undirected) {
            // arrowhead at b
            QPointF d = b - a; qreal len = std::hypot(d.x(), d.y());
            if (len < 1) return;
            d /= len;
            QPointF n(-d.y(), d.x());
            QPointF tip = b;
            QPointF base = b - d * 9;
            QPointF wing1 = base + n * 5;
            QPointF wing2 = base - n * 5;
            p->setBrush(col); p->setPen(Qt::NoPen);
            p->drawPolygon(QPolygonF({tip, wing1, wing2}));
        }
    }

    QString kind;
    QPointF p1() const { return p1_; }
    void setP1(const QPointF& v) {
        prepareGeometryChange();   // ★ 必须：修改几何属性前通知场景更新空间索引
        p1_ = v;
        m_borderValid = false;     // ★ 使缓存失效
        update();
    }
    QPointF p2() const { return p2_; }
    void setP2(const QPointF& v) {
        prepareGeometryChange();   // ★ 必须：修改几何属性前通知场景
        p2_ = v;
        m_borderValid = false;     // ★ 使缓存失效
        update();
    }
    qreal edgeOpacity() const { return m_op; }
    void setEdgeOpacity(qreal o) { m_op = o; setOpacity(o); update(); }

private:
    QPointF p1_, p2_;
    qreal m_op = 1.0;

    // ★ 缓存：避免每帧 paint() 重复计算 borderPoint（含 sqrt + 椭圆交点）
    mutable QPointF m_cachedA, m_cachedB;
    mutable bool m_borderValid = false;

    // Intersect the segment from c1 toward c2 with the node's bounding ellipse.
    static QPointF borderPoint(const QPointF& c1, const QPointF& c2) {
        QPointF d = c2 - c1;
        qreal len = std::hypot(d.x(), d.y());
        if (len < 1e-3) return c1;
        d /= len;
        qreal rx = 29 + 4, ry = 20 + 4;   // half node size + padding
        qreal t = 1.0 / std::sqrt((d.x()*d.x())/(rx*rx) + (d.y()*d.y())/(ry*ry));
        return c1 + d * t;
    }
};
