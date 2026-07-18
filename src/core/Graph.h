#pragma once
#include "Common.h"
#include "IDataStructure.h"
#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <map>
#include <algorithm>
#include <cmath>
#include <cstdio>

namespace dsv {

// ---------------------------------------------------------------------------
// Graph (无向加权图)
//
// 顶点(Vertex) + 边(Edge, 带权)。布局按顶点顺序 index 排在圆环上。
// 边使用 kind="edge"（无向，无箭头），由 VisualEdge 渲染为蓝色连线。
//
// 提供四类分步演示：
//   - addVertex(label)   添加顶点
//   - addEdge("u-v"|"u-v:w")  添加带权边
//   - bfs(start)        广度优先遍历（队列）
//   - dfs(start)        深度优先遍历（栈）
//   - dijkstra(start)   带权最短路径（贪心 + 松弛）
// 每个操作返回逐帧 FrameList，高亮当前访问节点，直观展示遍历/搜索过程。
// ---------------------------------------------------------------------------
class Graph : public IDataStructure {
public:
    struct Vertex { std::string label; int id; int order; };
    struct Edge { int u, v; double w;
        bool operator<(const Edge& o) const { return (u < o.u) || (u == o.u && v < o.v); } };

    DSKind kind() const override { return DSKind::Graph; }
    std::string name() const override { return "图 Graph"; }
    std::string description() const override {
        return "无向加权图，顶点 + 带权边。支持 BFS/DFS 遍历与 Dijkstra 最短路径，"
               "分步高亮访问顺序，是算法面试的主战场（岛屿、最短路径、拓扑排序等）。";
    }

    int size() const override { return static_cast<int>(vertices_.size()); }
    bool empty() const override { return vertices_.empty(); }

    // ---- vertex / edge construction ----
    FrameList addVertex(const std::string& label) override {
        FrameList frames;
        std::string lbl = label.empty() ? ("V" + std::to_string(autoCounter_++)) : label;
        if (labelOf_.count(lbl)) {
            frames.push_back(snapshotFrame("顶点 [" + lbl + "] 已存在", {}, "#FF9800"));
            return frames;
        }
        int id = nextId();
        int order = static_cast<int>(vertices_.size());
        vertices_.push_back({lbl, id, order});
        labelOf_[lbl] = id;
        idOf_[id] = lbl;
        frames.push_back(snapshotFrameWithHighlight("添加顶点 [" + lbl + "]", {id}, "#4CAF50"));
        return frames;
    }

    FrameList addEdge(const std::string& spec) override {
        FrameList frames;
        std::string s = spec;
        double w = 1.0;
        auto colon = s.find(':');
        if (colon != std::string::npos) { w = parseDouble(s.substr(colon + 1)); s = s.substr(0, colon); }
        auto dash = s.find('-');
        if (dash == std::string::npos) {
            frames.push_back(snapshotFrame("边格式应为 u-v 或 u-v:w，例如 A-B 或 A-B:5", {}, "#FF5722"));
            return frames;
        }
        std::string a = s.substr(0, dash), b = s.substr(dash + 1);
        if (!labelOf_.count(a) || !labelOf_.count(b)) {
            frames.push_back(snapshotFrame("顶点 [" + a + "] 或 [" + b + "] 不存在", {}, "#FF5722"));
            return frames;
        }
        int u = labelOf_[a], v = labelOf_[b];
        if (u == v) { frames.push_back(snapshotFrame("暂不支持自环", {}, "#FF5722")); return frames; }
        Edge e{std::min(u, v), std::max(u, v), w};
        if (edgeW_.count(e)) {
            frames.push_back(snapshotFrame("边 [" + a + "-" + b + "] 已存在", {}, "#FF9800"));
            return frames;
        }
        edgeW_[e] = w;
        frames.push_back(snapshotFrameWithHighlight(
            "添加边 [" + a + "-" + b + "]  权重 " + fmtW(w), {u, v}, "#2196F3"));
        return frames;
    }

    FrameList insert(const std::string& value) override { return addVertex(value); }
    FrameList insertAt(int, const std::string&) override { return {}; }
    FrameList remove(const std::string&) override { return {}; }
    FrameList removeAt(int) override { return {}; }
    FrameList find(const std::string&) override { return {}; }

    // ---- traversals ----
    FrameList bfs(const std::string& startLabel) override {
        FrameList frames;
        if (vertices_.empty()) { frames.push_back(snapshotFrame("图为空", {}, "#FFC107")); return frames; }
        int start = resolveStart(startLabel);
        std::unordered_set<int> visited;
        std::vector<int> q;
        std::vector<int> order;   // 首次访问顺序（天然去重，仿 VisuAlgo 在完成帧列出）
        q.push_back(start); visited.insert(start); order.push_back(start);
        frames.push_back(snapshotFrameWithHighlight(
            "BFS 从 [" + idOf_[start] + "] 入队开始", {start}, "#42A5F5"));
        size_t head = 0;
        while (head < q.size()) {
            int cur = q[head++];
            for (auto& e : edgeW_) {
                int nb = neighbor(e.first, cur);
                if (nb == -1) continue;
                if (!visited.count(nb)) {
                    visited.insert(nb);
                    q.push_back(nb);
                    order.push_back(nb);
                    frames.push_back(snapshotFrameWithHighlight(
                        "访问 [" + idOf_[cur] + "] 的邻居 [" + idOf_[nb] + "]，入队",
                        {cur, nb}, "#4CAF50"));
                } else {
                    frames.push_back(snapshotFrameWithHighlight(
                        "邻居 [" + idOf_[nb] + "] 已访问，跳过", {nb}, "#B0BEC5"));
                }
            }
            frames.push_back(snapshotFrameWithHighlight(
                "[" + idOf_[cur] + "] 出队（已访问）", {cur}, "#42A5F5"));
        }
        frames.push_back(snapshotFrame(
            "BFS 完成\n遍历顺序（去重）：" + orderStr(order), {}, "#4CAF50"));
        return frames;
    }

    FrameList dfs(const std::string& startLabel) override {
        FrameList frames;
        if (vertices_.empty()) { frames.push_back(snapshotFrame("图为空", {}, "#FFC107")); return frames; }
        int start = resolveStart(startLabel);
        std::unordered_set<int> visited;
        std::vector<int> stack;
        std::vector<int> order;   // 首次访问顺序（天然去重）
        stack.push_back(start);
        frames.push_back(snapshotFrameWithHighlight(
            "DFS 从 [" + idOf_[start] + "] 压栈开始", {start}, "#AB47BC"));
        while (!stack.empty()) {
            int cur = stack.back(); stack.pop_back();
            if (visited.count(cur)) continue;
            visited.insert(cur);
            order.push_back(cur);
            frames.push_back(snapshotFrameWithHighlight(
                "访问 [" + idOf_[cur] + "]（出栈并标记）", {cur}, "#4CAF50"));
            // push neighbors in reverse order so leftmost is visited first
            std::vector<int> nbs;
            for (auto& e : edgeW_) {
                int nb = neighbor(e.first, cur);
                if (nb != -1 && !visited.count(nb)) nbs.push_back(nb);
            }
            std::reverse(nbs.begin(), nbs.end());
            for (int nb : nbs) {
                frames.push_back(snapshotFrameWithHighlight(
                    "[" + idOf_[cur] + "] 的未访问邻居 [" + idOf_[nb] + "] 压栈",
                    {nb}, "#AB47BC"));
                stack.push_back(nb);
            }
        }
        frames.push_back(snapshotFrame(
            "DFS 完成\n遍历顺序（去重）：" + orderStr(order), {}, "#4CAF50"));
        return frames;
    }

    FrameList dijkstra(const std::string& startLabel) override {
        FrameList frames;
        if (vertices_.empty()) { frames.push_back(snapshotFrame("图为空", {}, "#FFC107")); return frames; }
        int start = resolveStart(startLabel);
        std::unordered_map<int, double> dist;
        std::unordered_set<int> done;
        for (auto& v : vertices_) dist[v.id] = 1e18;
        dist[start] = 0;
        frames.push_back(snapshotFrameWithHighlight(
            "Dijkstra 从 [" + idOf_[start] + "] 开始，dist=0", {start}, "#FF7043"));
        for (size_t iter = 0; iter < vertices_.size(); ++iter) {
            // pick unvisited node with smallest dist
            int u = -1; double best = 1e18;
            for (auto& v : vertices_) if (!done.count(v.id) && dist[v.id] < best) { best = dist[v.id]; u = v.id; }
            if (u == -1) break;
            done.insert(u);
            frames.push_back(snapshotFrameWithHighlight(
                "选定最近未确定节点 [" + idOf_[u] + "]，dist=" + fmtW(dist[u]), {u}, "#FF7043"));
            for (auto& e : edgeW_) {
                int nb = neighbor(e.first, u);
                if (nb == -1 || done.count(nb)) continue;
                double nd = dist[u] + e.second;
                if (nd < dist[nb]) {
                    dist[nb] = nd;
                    frames.push_back(snapshotFrameWithHighlight(
                        "松弛 [" + idOf_[u] + "]→[" + idOf_[nb] + "]：新距离 " + fmtW(nd),
                        {u, nb}, "#4CAF50"));
                }
            }
        }
        frames.push_back(snapshotFrame("Dijkstra 完成：各点 dist 即最短路径权重和", {}, "#4CAF50"));
        return frames;
    }

    FrameList clear() override {
        FrameList frames;
        vertices_.clear(); labelOf_.clear(); idOf_.clear(); edgeW_.clear(); autoCounter_ = 1;
        frames.push_back(snapshotFrame("已清空图", {}, "#4CAF50"));
        return frames;
    }

    Frame currentFrame() const override { return snapshotFrame(""); }

    std::vector<std::string> snapshotValues() const override {
        std::vector<std::string> v;
        for (auto& vert : vertices_) v.push_back(vert.label);
        return v;
    }

private:
    std::vector<Vertex> vertices_;
    std::unordered_map<std::string, int> labelOf_;
    std::unordered_map<int, std::string> idOf_;
    std::map<Edge, double> edgeW_;   // ordered so stable iteration
    int autoCounter_ = 1;

    static double parseDouble(const std::string& s) {
        try { return std::stod(s); } catch (...) { return 1.0; }
    }
    static std::string fmtW(double w) {
        int i = static_cast<int>(w);
        if (w == static_cast<double>(i)) return std::to_string(i);
        char buf[32]; std::snprintf(buf, sizeof(buf), "%.2f", w); return std::string(buf);
    }
    int resolveStart(const std::string& lbl) const {
        if (!lbl.empty() && labelOf_.count(lbl)) return labelOf_.at(lbl);
        return vertices_.empty() ? -1 : vertices_[0].id;
    }
    static int neighbor(const Edge& e, int x) {
        if (e.u == x) return e.v;
        if (e.v == x) return e.u;
        return -1;
    }
    // 将首次访问顺序（id 序列）拼成 "A → B → C → ..." 形式，供完成帧展示
    std::string orderStr(const std::vector<int>& order) const {
        std::string s;
        for (size_t i = 0; i < order.size(); ++i) {
            if (i) s += " → ";
            s += idOf_.at(order[i]);
        }
        return s;
    }

    Frame snapshotFrame(const std::string& desc,
                        const std::vector<int>& hIds = {},
                        const std::string& color = "#EDE7F6") const {
        Frame f; f.type = StepType::Done; f.description = desc;
        f.highlightColor = color; f.highlightIds = hIds;
        for (auto& v : vertices_) {
            FrameNode fn; fn.id = v.id; fn.value = v.label; fn.index = v.order;
            f.nodes.push_back(fn);
        }
        for (auto& e : edgeW_) {
            FrameEdge fe; fe.fromId = e.first.u; fe.toId = e.first.v; fe.kind = "edge";
            f.edges.push_back(fe);
        }
        return f;
    }
    Frame snapshotFrameWithHighlight(const std::string& desc,
                                     const std::vector<int>& hIds,
                                     const std::string& color) const {
        Frame f = snapshotFrame(desc, {}, color);
        f.highlightIds = hIds;
        return f;
    }
};

} // namespace dsv
