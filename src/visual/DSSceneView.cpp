#include "DSSceneView.h"
#include <QWheelEvent>
#include <QMouseEvent>
#include <QScrollBar>

namespace dsv {

DSSceneView::DSSceneView(QGraphicsScene* scene, QWidget* parent)
    : QGraphicsView(scene, parent)
{
    setRenderHint(QPainter::Antialiasing);
    setViewportUpdateMode(QGraphicsView::FullViewportUpdate);
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
        QPointF targetScenePos = mapToScene(event->position().toPointF());
        QPointF targetViewportPos = event->position().toPointF();

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
    if (e->button() == Qt::MiddleButton) {
        m_panStart = e->pos();
        setCursor(Qt::ClosedHandCursor);
        e->accept();
    } else {
        QGraphicsView::mousePressEvent(e);  // left-click for node interaction
    }
}

void DSSceneView::mouseMoveEvent(QMouseEvent* e) {
    if ((e->buttons() & Qt::MiddleButton) && !m_panStart.isNull()) {
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
    if (e->button() == Qt::MiddleButton) {
        setCursor(Qt::ArrowCursor);
        m_panStart = QPoint();
        e->accept();
    } else {
        QGraphicsView::mouseReleaseEvent(e);
    }
}

} // namespace dsv
