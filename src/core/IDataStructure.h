#pragma once

// Abstract interface for every data structure in the visualizer.
// Operations mutate the structure AND return a FrameList describing the
// sequence of micro-steps, so the UI can animate them one by one.
//
// Design note: values are stored as std::string so the engine stays generic
// and Qt-free; numeric ordering is handled in compareValues() (Common.h).

#include "Common.h"
#include <string>
#include <vector>

namespace dsv {

class IDataStructure {
public:
    virtual ~IDataStructure() = default;

    // --- metadata ---
    virtual DSKind kind() const = 0;
    virtual std::string name() const = 0;
    virtual std::string description() const = 0;

    // --- core operations: mutate + return step frames ---
    virtual FrameList insert(const std::string& value) = 0;
    virtual FrameList insertAt(int pos, const std::string& value) = 0;
    virtual FrameList remove(const std::string& value) = 0;
    virtual FrameList removeAt(int pos) = 0;
    virtual FrameList find(const std::string& value) = 0;
    virtual FrameList clear() = 0;

    // --- deque-style endpoints (default no-op so existing structures compile) ---
    virtual FrameList pushFront(const std::string& value) { return {}; }
    virtual FrameList pushBack(const std::string& value)  { return {}; }
    virtual FrameList popFront()                           { return {}; }
    virtual FrameList popBack()                            { return {}; }

    // --- graph-specific operations (default no-op so existing structures compile) ---
    virtual FrameList addVertex(const std::string& /*label*/) { return {}; }
    virtual FrameList addEdge(const std::string& /*spec*/)   { return {}; }
    virtual FrameList bfs(const std::string& /*start*/)      { return {}; }
    virtual FrameList dfs(const std::string& /*start*/)      { return {}; }
    virtual FrameList dijkstra(const std::string& /*start*/) { return {}; }

    // A single frame of the current state (for static rendering).
    virtual Frame currentFrame() const = 0;

    // --- state queries ---
    virtual int size() const = 0;
    virtual bool empty() const = 0;

    // Snapshot of all values, in insertion/iteration order, for undo support.
    virtual std::vector<std::string> snapshotValues() const = 0;
};

} // namespace dsv
