#pragma once
#include <QGraphicsView>
#include <QPoint>
#include <QResizeEvent>

namespace dsv {

// Custom QGraphicsView that adds:
// 1. Pan the canvas by dragging EMPTY space with the LEFT button, or with the MIDDLE button.
// 2. Ctrl + mouse wheel to zoom (centered on cursor position).
// Left-clicking a node is preserved for node interaction.
class DSSceneView : public QGraphicsView {
    Q_OBJECT
public:
    explicit DSSceneView(QGraphicsScene* scene, QWidget* parent = nullptr);
    double zoomFactor() const { return m_zoomFactor; }

public slots:
    void resetView();                         // reset to 100% + identity transform
    void setZoomFactor(double factor);        // 0.1 .. 10.0, centered on viewport
    void fitInContent(const QRectF& rect);    // fitInView + sync zoom factor
    void fitToContent();                       // fit to scene items bounding rect

signals:
    void zoomChanged(double factor);

private:
    void wheelEvent(QWheelEvent* event) override;
    void mousePressEvent(QMouseEvent* event) override;
    void mouseMoveEvent(QMouseEvent* event) override;
    void mouseReleaseEvent(QMouseEvent* event) override;
    void resizeEvent(QResizeEvent* event) override;

    double m_zoomFactor = 1.0;        // current scale (1.0 = default)
    QPoint m_panStart;                 // pan start position
    bool m_panning = false;            // whether a pan drag is in progress
};

} // namespace dsv
