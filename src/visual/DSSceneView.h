#pragma once
#include <QGraphicsView>
#include <QPoint>

namespace dsv {

// Custom QGraphicsView that adds:
// 1. Middle-button drag to pan the canvas
// 2. Ctrl + mouse wheel to zoom (centered on cursor position)
// Left-click behavior is preserved for node interaction.
class DSSceneView : public QGraphicsView {
    Q_OBJECT
public:
    explicit DSSceneView(QGraphicsScene* scene, QWidget* parent = nullptr);

signals:
    void zoomChanged(double factor);   // current zoom level (1.0 = 100%)

private:
    void wheelEvent(QWheelEvent* event) override;
    void mousePressEvent(QMouseEvent* event) override;
    void mouseMoveEvent(QMouseEvent* event) override;
    void mouseReleaseEvent(QMouseEvent* event) override;

    double m_zoomFactor = 1.0;        // current scale (1.0 = default)
    QPoint m_panStart;                 // pan start position (middle button)
};

} // namespace dsv
