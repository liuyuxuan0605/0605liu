#include "DSSceneView.h"
#include "DSScene.h"
#include <QWheelEvent>
#include <QMouseEvent>
#include <QScrollBar>

namespace dsv {

DSSceneView::DSSceneView(QGraphicsScene* scene, QWidget* parent)
    : QGraphicsView(scene, parent)
{
    setRenderHint(QPainter::Antialiasing);
    setViewportUpdateMode(QGraphicsView::FullViewportUpdate);
    // 横竖滚动条始终显示，方便用户像图片里那样拖动查看超出视口的节点
    setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOn);
    setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOn);
    // Keep default drag mode (NoDrag) so left-click works for node interaction.
    // Pan is handled by middle button, zoom by Ctrl+wheel.
}

void DSSceneView::wheelEvent(QWheelEvent* event) {
    if (event->modifiers() & Qt::ControlModifier) {
        // Ctrl + scroll wheel → zoom centered on mouse cursor
        double factor = (event->angleDelta().y() > 0) ? 1.15 : (1.0 / 1.15);
        double newScale = m_zoomFactor * factor;
        if (newScale < 0.1 || newScale > 10.0) return;  // clamp range
        m_zoomFactor = newScale;

        // Zoom centered on the point under the mouse cursor
        QPointF targetScenePos = mapToScene(event->pos());
        QPointF targetViewportPos = event->pos();

        scale(factor, factor);

        // Adjust scroll bars to keep the target point stationary
        QPointF newPos = mapFromScene(targetScenePos) - targetViewportPos;
        horizontalScrollBar()->setValue(horizontalScrollBar()->value() + static_cast<int>(newPos.x()));
        verticalScrollBar()->setValue(verticalScrollBar()->value() + static_cast<int>(newPos.y()));

        emit zoomChanged(m_zoomFactor);
        event->accept();
    } else {
        QGraphicsView::wheelEvent(event);  // normal scrolling without Ctrl
    }
}

void DSSceneView::mousePressEvent(QMouseEvent* e) {
    // Pan when:
    //  - middle button (classic), or
    //  - LEFT button on EMPTY canvas (most intuitive, like whiteboard tools)
    bool wantPan = (e->button() == Qt::MiddleButton) ||
                   (e->button() == Qt::LeftButton && itemAt(e->pos()) == nullptr);
    if (wantPan) {
        m_panning = true;
        m_panStart = e->pos();
        setCursor(Qt::ClosedHandCursor);
        e->accept();
    } else {
        QGraphicsView::mousePressEvent(e);  // left-click on a node → node interaction
    }
}

void DSSceneView::mouseMoveEvent(QMouseEvent* e) {
    if (m_panning) {
        QPoint delta = e->pos() - m_panStart;
        horizontalScrollBar()->setValue(horizontalScrollBar()->value() - delta.x());
        verticalScrollBar()->setValue(verticalScrollBar()->value() - delta.y());
        m_panStart = e->pos();
        e->accept();
    } else {
        QGraphicsView::mouseMoveEvent(e);
    }
}

void DSSceneView::mouseReleaseEvent(QMouseEvent* e) {
    if (m_panning) {
        m_panning = false;
        setCursor(Qt::ArrowCursor);
        m_panStart = QPoint();
        e->accept();
    } else {
        QGraphicsView::mouseReleaseEvent(e);
    }
}

void DSSceneView::resizeEvent(QResizeEvent* e) {
    QGraphicsView::resizeEvent(e);
    // 让布局引擎以当前视口大小为参考，内容超出时滚动条自然出现
    if (scene()) {
        auto* ds = qobject_cast<DSScene*>(scene());
        if (ds) ds->setViewSize(viewport()->width(), viewport()->height());
    }
}

void DSSceneView::resetView() {
    resetTransform();       // reset visual transform to identity
    m_zoomFactor = 1.0;    // keep zoom factor in sync (fixes Ctrl+wheel jump after switch)
    emit zoomChanged(m_zoomFactor);
}

void DSSceneView::setZoomFactor(double factor) {
    if (factor < 0.1) factor = 0.1;
    if (factor > 10.0) factor = 10.0;
    double ratio = factor / m_zoomFactor;
    if (qFuzzyCompare(ratio, 1.0)) return;

    // zoom centered on the current viewport center so the slider feels predictable
    QPointF center = mapToScene(viewport()->rect().center());
    scale(ratio, ratio);
    centerOn(center);

    m_zoomFactor = factor;
    emit zoomChanged(m_zoomFactor);
}

void DSSceneView::fitInContent(const QRectF& rect) {
    if (!scene()) return;
    resetTransform();
    fitInView(rect, Qt::KeepAspectRatio);
    m_zoomFactor = transform().m11();
    emit zoomChanged(m_zoomFactor);
}

void DSSceneView::fitToContent() {
    if (!scene()) return;
    fitInContent(scene()->itemsBoundingRect().adjusted(-40, -40, 40, 40));
}

} // namespace dsv
