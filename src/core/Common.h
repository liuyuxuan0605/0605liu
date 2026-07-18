#pragma once

// Core data model for the visualizer. Pure C++17, NO Qt dependency.
// This header is shared by the data-structure engine (core/) and the
// visualization layer (visual/). Keeping it Qt-free lets the engine be
// unit-tested without any GUI dependency.

#include <string>
#include <vector>
#include <cmath>
#include <algorithm>
#include <utility>
#include <stdexcept>

namespace dsv {

// ---------------------------------------------------------------------------
// Enumerations
// ---------------------------------------------------------------------------

// Which kind of data structure is currently active. Drives layout + UI.
enum class DSKind {
    SinglyLinkedList,
    DoublyLinkedList,
    Stack,
    Queue,
    BinarySearchTree,
    AVLTree,
    HashMap,
    MinHeap,
    RedBlackTree,
    Deque,
    BlockingQueue,
    BTree,
    BPlusTree,
    RingBuffer,
    Graph,
    LRUCache
};

// A single micro-step in an operation. The animator turns consecutive
// frames into smooth transitions.
enum class StepType {
    Start,
    CreateNode,
    Traverse,
    Compare,
    BreakLink,
    Link,
    Rotate,
    Rebalance,
    Split,
    Merge,
    Swap,
    SiftUp,
    SiftDown,
    HashCompute,
    BucketLocate,
    Highlight,
    InsertValue,
    RemoveValue,
    Done
};

inline const char* stepTypeString(StepType t) {
    switch (t) {
        case StepType::Start:         return "开始";
        case StepType::CreateNode:    return "创建节点";
        case StepType::Traverse:      return "遍历";
        case StepType::Compare:       return "比较";
        case StepType::BreakLink:     return "断开链接";
        case StepType::Link:          return "连接";
        case StepType::Rotate:        return "旋转";
        case StepType::Rebalance:     return "重平衡";
        case StepType::Split:          return "分裂";
        case StepType::Merge:          return "合并";
        case StepType::Swap:          return "交换";
        case StepType::SiftUp:        return "上浮";
        case StepType::SiftDown:      return "下沉";
        case StepType::HashCompute:   return "计算哈希";
        case StepType::BucketLocate:  return "定位桶";
        case StepType::Highlight:     return "高亮";
        case StepType::InsertValue:   return "插入";
        case StepType::RemoveValue:   return "删除";
        case StepType::Done:          return "完成";
    }
    return "";
}

// ---------------------------------------------------------------------------
// Frame primitives (logical data for each visualization snapshot)
// ---------------------------------------------------------------------------

struct FrameNode {
    int id = -1;            // stable id for animation tracking across frames
    std::string value;      // primary label shown inside the node
    std::string sublabel;   // secondary label (e.g. "bucket 3", key, index, 红/黑)
    int index = -1;         // heap/array index (used by layout for MinHeap)
    std::string color = {}; // per-node fill color (hex); empty = use default
};

struct FrameEdge {
    int fromId = -1;
    int toId = -1;
    std::string kind;       // "next" | "prev" | "left" | "right" | "bucket" | "edge"
};

// A complete snapshot of the structure's visual state plus narration.
struct Frame {
    StepType type = StepType::Done;
    std::string description;
    std::vector<FrameNode> nodes;
    std::vector<FrameEdge> edges;
    std::vector<int> highlightIds;        // nodes to color in this frame
    std::string highlightColor = "#FFC107"; // amber by default
    int focusId = -1;                     // the "current" node (optional emphasis)
};

using FrameList = std::vector<Frame>;

// ---------------------------------------------------------------------------
// Shared helpers
// ---------------------------------------------------------------------------

// Monotonic id generator so every logical node has a stable identity that
// survives across frames, enabling the animator to track movement.
inline int& idCounter() {
    static int c = 0;
    return c;
}
inline int nextId() { return ++idCounter(); }

// Generic ordering: numeric when both parse as double, otherwise lexicographic.
inline int compareValues(const std::string& a, const std::string& b) {
    try {
        double da = std::stod(a);
        double db = std::stod(b);
        if (da < db) return -1;
        if (da > db) return 1;
        return 0;
    } catch (...) {
        if (a < b) return -1;
        if (a > b) return 1;
        return 0;
    }
}

} // namespace dsv
