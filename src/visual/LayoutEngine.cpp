#include "LayoutEngine.h"
#include <functional>
#include <cmath>
#include <unordered_set>
#include <algorithm>
#include <string>

namespace dsv {

std::unordered_map<int, QPointF> LayoutEngine::layout(DSKind kind,
                                                      const Frame& frame,
                                                      double viewW, double viewH) {
    std::unordered_map<int, QPointF> pos;
    const double baseX = 90, baseY = 90;
    const double HS = 96, VS = 78;

    auto nextOf = [&](int from) -> int {
        for (const auto& e : frame.edges)
            if (e.fromId == from && e.kind == "next") return e.toId;
        return -1;
    };

    if (kind == DSKind::Stack) {
        int order = 0;
        // head = node with no incoming "next" (prefer one that also has an outgoing "next",
        // so an isolated "create" node is not mistaken for the list head)
        std::unordered_map<int, bool> incoming, outgoing;
        for (const auto& e : frame.edges) if (e.kind == "next") { incoming[e.toId] = true; outgoing[e.fromId] = true; }
        int head = -1;
        for (const auto& n : frame.nodes) if (!incoming[n.id] && outgoing[n.id]) { head = n.id; break; }
        if (head == -1) for (const auto& n : frame.nodes) if (!incoming[n.id]) { head = n.id; break; }
        int cur = head;
        while (cur != -1) { pos[cur] = QPointF(baseX, baseY + order * VS); cur = nextOf(cur); order++; }
        // staging (isolated) nodes: above
        for (const auto& n : frame.nodes) if (pos.find(n.id) == pos.end())
            pos[n.id] = QPointF(baseX, baseY - 80);
        return pos;
    }

    if (kind == DSKind::SinglyLinkedList || kind == DSKind::DoublyLinkedList ||
        kind == DSKind::Queue || kind == DSKind::Deque) {
        int order = 0;
        std::unordered_map<int, bool> incoming, outgoing;
        for (const auto& e : frame.edges) if (e.kind == "next") { incoming[e.toId] = true; outgoing[e.fromId] = true; }
        int head = -1;
        for (const auto& n : frame.nodes) if (!incoming[n.id] && outgoing[n.id]) { head = n.id; break; }
        if (head == -1) for (const auto& n : frame.nodes) if (!incoming[n.id]) { head = n.id; break; }
        int cur = head;
        while (cur != -1) { pos[cur] = QPointF(baseX + order * HS, baseY); cur = nextOf(cur); order++; }
        for (const auto& n : frame.nodes) if (pos.find(n.id) == pos.end())
            pos[n.id] = QPointF(baseX + order * HS, baseY - 80);
        return pos;
    }

    if (kind == DSKind::BinarySearchTree || kind == DSKind::AVLTree ||
        kind == DSKind::RedBlackTree) {
        std::unordered_map<int, int> leftC, rightC, parentOf;
        for (const auto& e : frame.edges) {
            if (e.kind == "left")  { leftC[e.fromId] = e.toId; parentOf[e.toId] = e.fromId; }
            if (e.kind == "right") { rightC[e.fromId] = e.toId; parentOf[e.toId] = e.fromId; }
        }
        // root: a node with no parent; prefer one that actually has a child,
        // so an isolated "create" node is not mistaken for the root.
        std::vector<int> candidates;
        for (const auto& n : frame.nodes) if (parentOf.find(n.id) == parentOf.end()) candidates.push_back(n.id);
        std::unordered_set<int> fromSet;
        for (const auto& e : frame.edges) fromSet.insert(e.fromId);
        int root = -1;
        for (int c : candidates) if (fromSet.count(c)) { root = c; break; }
        if (root == -1 && !candidates.empty()) root = candidates.front();
        int xIdx = 0;
        std::function<void(int, int)> inorder = [&](int id, int depth) {
            if (id == -1) return;
            inorder(leftC.count(id) ? leftC[id] : -1, depth + 1);
            pos[id] = QPointF(baseX + xIdx * HS, baseY + depth * VS);
            xIdx++;
            inorder(rightC.count(id) ? rightC[id] : -1, depth + 1);
        };
        inorder(root, 0);
        for (const auto& n : frame.nodes) if (pos.find(n.id) == pos.end())
            pos[n.id] = QPointF(baseX + xIdx * HS, baseY - 80);
        return pos;
    }

    if (kind == DSKind::MinHeap) {
        for (const auto& n : frame.nodes) {
            if (n.index < 0) continue;
            int idx = n.index;
            int level = static_cast<int>(std::floor(std::log2(idx + 1)));
            int posInLevel = idx - (static_cast<int>(std::pow(2, level)) - 1);
            int count = static_cast<int>(std::pow(2, level));
            double cx = baseX + viewW / 2.0 + (posInLevel - (count - 1) / 2.0) * HS;
            double cy = baseY + level * VS;
            pos[n.id] = QPointF(cx, cy);
        }
        return pos;
    }

    if (kind == DSKind::HashMap) {
        for (const auto& n : frame.nodes) {
            if (n.id < 0) {  // bucket header: index holds bucket number
                double bx = baseX + n.index * HS;
                pos[n.id] = QPointF(bx, baseY);
                // walk chain
                int chainPos = 0;
                int cur = -1;
                for (const auto& e : frame.edges)
                    if (e.kind == "bucket" && e.fromId == n.id) { cur = e.toId; break; }
                while (cur != -1) {
                    pos[cur] = QPointF(bx, baseY + (chainPos + 1) * VS);
                    cur = nextOf(cur); chainPos++;
                }
            }
        }
        return pos;
    }

    // ---- BlockingQueue / RingBuffer: ring layout by index ----
    if (kind == DSKind::BlockingQueue || kind == DSKind::RingBuffer) {
        int cap = 0;
        for (const auto& n : frame.nodes)
            if (n.index >= 0) cap = std::max(cap, n.index + 1);
        if (cap == 0) cap = 8;  // default
        const double PI = 3.141592653589793;
        double R = std::max(150.0, cap * 35.0);
        double cx = viewW / 2.0, cy = viewH / 2.0;
        for (const auto& n : frame.nodes) {
            if (n.index < 0) continue;
            double ang = -PI / 2.0 + (double)n.index / cap * 2.0 * PI;
            pos[n.id] = QPointF(cx + R * std::cos(ang), cy + R * std::sin(ang));
        }
        return pos;
    }

    // ---- Graph: vertices arranged on a circle by index (order added) ----
    if (kind == DSKind::Graph) {
        int n = static_cast<int>(frame.nodes.size());
        if (n == 0) return pos;
        const double PI = 3.141592653589793;
        double R = std::max(170.0, n * 42.0);
        double cx = viewW / 2.0, cy = viewH / 2.0;
        for (const auto& node : frame.nodes) {
            int idx = (node.index >= 0) ? node.index : 0;
            double ang = -PI / 2.0 + (double)idx / n * 2.0 * PI;
            pos[node.id] = QPointF(cx + R * std::cos(ang), cy + R * std::sin(ang));
        }
        return pos;
    }

    // ---- BTree / BPlusTree: n-ary layout (parse "cN" edges) ----
    if (kind == DSKind::BTree || kind == DSKind::BPlusTree) {
        const double BHS = 170;   // wider horizontal spacing for multi-key nodes
        const double BVS = 90;    // more vertical space for taller nodes
        std::unordered_map<int, std::vector<std::pair<int, int>>> childMap; // parent -> (idx, child)
        std::unordered_set<int> hasParent;
        for (const auto& e : frame.edges) {
            if (!e.kind.empty() && e.kind[0] == 'c') {
                int idx = 0;
                try { idx = std::stoi(e.kind.substr(1)); } catch (...) { idx = 0; }
                childMap[e.fromId].push_back({idx, e.toId});
                hasParent.insert(e.toId);
            }
        }
        for (auto& kv : childMap)
            std::sort(kv.second.begin(), kv.second.end());
        int root = -1;
        for (const auto& n : frame.nodes)
            if (!hasParent.count(n.id)) { root = n.id; break; }
        if (root == -1 && !frame.nodes.empty()) root = frame.nodes[0].id;
        std::unordered_map<int, int> leafCount;
        std::function<int(int)> countLeaves = [&](int id) -> int {
            auto it = childMap.find(id);
            if (it == childMap.end() || it->second.empty()) { leafCount[id] = 1; return 1; }
            int sum = 0;
            for (auto& pr : it->second) sum += countLeaves(pr.second);
            leafCount[id] = sum; return sum;
        };
        if (root != -1) countLeaves(root);
        int cursor = 0;
        std::function<void(int, int)> place = [&](int id, int depth) {
            auto it = childMap.find(id);
            if (it == childMap.end() || it->second.empty()) {
                pos[id] = QPointF(baseX + cursor * BHS, baseY + depth * BVS);
                cursor++;
                return;
            }
            double minx = 1e9, maxx = -1e9;
            for (auto& pr : it->second) {
                place(pr.second, depth + 1);
                double x = pos[pr.second].x();
                if (x < minx) minx = x;
                if (x > maxx) maxx = x;
            }
            pos[id] = QPointF((minx + maxx) / 2.0, baseY + depth * BVS);
        };
        if (root != -1) place(root, 0);
        for (const auto& n : frame.nodes)
            if (pos.find(n.id) == pos.end())
                pos[n.id] = QPointF(baseX + cursor * BHS, baseY - 80);
        return pos;
    }

    // fallback: grid
    int i = 0;
    for (const auto& n : frame.nodes) {
        pos[n.id] = QPointF(baseX + (i % 8) * HS, baseY + (i / 8) * VS);
        i++;
    }
    return pos;
}

} // namespace dsv
