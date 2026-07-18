#pragma once
#include <QGraphicsObject>
#include <QGraphicsItem>
#include <QPainter>
#include <QGraphicsSceneMouseEvent>
#include <QGraphicsSceneHoverEvent>
#include <QColor>
#include <QCursor>

// A single visualized node. Custom properties (nodePos / nodeScale /
// fillColor) are animated by QPropertyAnimation for smooth transitions.
class VisualNode : public QGraphicsObject {
    Q_OBJECT
    Q_PROPERTY(QPointF nodePos READ nodePos WRITE setNodePos)
    Q_PROPERTY(qreal nodeScale READ nodeScale WRITE setNodeScale)
    Q_PROPERTY(QColor fillColor READ fillColor WRITE setFillColor)
public:
    explicit VisualNode(QGraphicsItem* parent = nullptr) : QGraphicsObject(parent) {
        setFlag(ItemSendsGeometryChanges);
        setAcceptHoverEvents(true);
    }

    QRectF boundingRect() const override {
        qreal w = m_wider ? W_WIDE : W;
        qreal h = m_wider ? H_WIDE : H;
        return QRectF(-w/2.0, -h/2.0, w, h);
    }

    void paint(QPainter* p, const QStyleOptionGraphicsItem*, QWidget*) override {
        p->setRenderHint(QPainter::Antialiasing);
        QRectF r = boundingRect();
        qreal radius = m_wider ? 12 : 9;
        QColor border = m_fill.darker(135);
        p->setPen(QPen(border, 1.5));
        p->setBrush(m_fill);
        p->drawRoundedRect(r, radius, radius);

        QColor text = (m_fill.lightness() > 140) ? QColor("#1f2430") : QColor("#ffffff");
        int fontSize = m_wider ? 11 : 12;
        QFont f = p->font(); f.setPointSize(fontSize); f.setWeight(QFont::Medium);
        p->setFont(f); p->setPen(text);
        QRectF vr = r; vr.setBottom(r.bottom() - (sublabel.isEmpty() ? 0 : 9));
        p->drawText(vr, Qt::AlignCenter, value);

        if (!sublabel.isEmpty()) {
            QFont sf = f; sf.setPointSize(8); sf.setWeight(QFont::Normal);
            p->setFont(sf); p->setPen(text.lighter(115));
            qreal subH = 12;
            p->drawText(QRectF(r.x(), r.bottom()-subH, r.width(), subH), Qt::AlignCenter, sublabel);
        }
    }

    int id = -1;
    QString value;
    QString sublabel;
    bool m_wider = false;

    void setWider(bool w) { m_wider = w; update(); }

    QPointF nodePos() const { return pos(); }
    void setNodePos(const QPointF& pt) { setPos(pt); }
    qreal nodeScale() const { return scale(); }
    void setNodeScale(qreal s) { setScale(s); }
    QColor fillColor() const { return m_fill; }
    void setFillColor(const QColor& c) { m_fill = c; update(); }

signals:
    void nodeClicked(int id);

protected:
    void mousePressEvent(QGraphicsSceneMouseEvent*) override { emit nodeClicked(id); }
    void hoverEnterEvent(QGraphicsSceneHoverEvent*) override { setCursor(QCursor(Qt::PointingHandCursor)); }

private:
    QColor m_fill = QColor("#EDE7F6");
    static constexpr qreal W = 58, H = 40;
    static constexpr qreal W_WIDE = 140, H_WIDE = 48;
};
