#pragma once
#include <QGraphicsView>
#include <QPoint>

namespace dsv {

// Custom QGraphicsView that adds:
// 1. Pan the canvas by dragging EMPTY space with the LEFT button, or with the MIDDLE button.
// 2. Ctrl + mouse wheel to zoom (centered on cursor position).
// Left-clicking a node is preserved for node interaction.
class DSSceneView : public QGraphicsView {
    Q_OBJECT
public:
    explicit DSSceneView(QGraphicsScene* scene, QWidget* parent = nullptr);
    void resetView();   // reset zoom factor + transform to default (100%)

signals:
    void zoomChanged(double factor);   // current zoom level (1.0 = 100%)

private:
    void wheelEvent(QWheelEvent* event) override;
    void mousePressEvent(QMouseEvent* event) override;
    void mouseMoveEvent(QMouseEvent* event) override;
    void mouseReleaseEvent(QMouseEvent* event) override;

    double m_zoomFactor = 1.0;        // current scale (1.0 = default)
    QPoint m_panStart;                 // pan start position
    bool m_panning = false;            // whether a pan drag is in progress
};

} // namespace dsv
