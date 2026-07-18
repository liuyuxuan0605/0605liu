#pragma once
#include <QPointF>
#include <unordered_map>
#include "../core/Common.h"

namespace dsv {

// Computes scene coordinates for every node id in a frame, based on the
// active data-structure kind. Returns a map id -> center position.
class LayoutEngine {
public:
    static std::unordered_map<int, QPointF> layout(DSKind kind,
                                                   const Frame& frame,
                                                   double viewW, double viewH);
};

} // namespace dsv
