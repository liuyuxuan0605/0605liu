#pragma once
#include "Common.h"
#include "IDataStructure.h"
#include <memory>
#include <vector>
#include <string>
#include <algorithm>
#include <functional>

namespace dsv {

// ---------------------------------------------------------------------------
// B-Tree (min degree t = 2 -> max 3 keys / 4 children per node)
// Each B-tree node maps to ONE VisualNode whose value = keys joined by " | ".
// Child j is connected with an edge of kind "c" + j  (e.g. "c0","c1","c2"),
// which the n-ary layout branch in LayoutEngine parses to place children.
// Algorithm mirrors b_tree_ref.py (validated with 300 randomized trials).
// ---------------------------------------------------------------------------
class BTree : public IDataStructure {
public:
    struct Node {
        std::vector<std::string> keys;
        std::vector<std::unique_ptr<Node>> children;
        bool leaf = true;
        int id;
        Node() : id(nextId()) {}
    };

    BTree(int t = 2) : t_(t) { root_ = std::make_unique<Node>(); }

    DSKind kind() const override { return DSKind::BTree; }
    std::string name() const override { return "B树 B-Tree"; }
    std::string description() const override {
        int maxKeys = 2 * t_ - 1;
        int maxChildren = 2 * t_;
        return "最小度 t=" + std::to_string(t_) + "（每节点最多" + std::to_string(maxKeys) +
               "键/" + std::to_string(maxChildren) + "子）；插入溢出分裂、删除下溢借位/合并。";
    }

    int size() const override { return countKeys(); }
    bool empty() const override { return root_->keys.empty(); }

    FrameList insert(const std::string& value) override {
        FrameList frames;
        if (search(root_.get(), value)) {
            frames.push_back(snapshot(StepType::Done, "值 " + value + " 已存在，忽略",
                {}, "#FFC107"));
            return frames;
        }
        if ((int)root_->keys.size() == 2 * t_ - 1) {
            auto s = std::make_unique<Node>();
            s->leaf = false;
            s->children.push_back(std::move(root_));
            root_ = std::move(s);
            splitChild(root_.get(), 0, frames);
            frames.push_back(snapshot(StepType::Split, "根节点已满，先分裂",
                {root_->id}, "#FF5722"));
        }
        insertNonFull(root_.get(), value, frames);
        frames.push_back(snapshot(StepType::Done,
            "插入 " + value + " 完成，共 " + std::to_string(countKeys()) + " 个键",
            {}, "#FFC107"));
        return frames;
    }

    FrameList insertAt(int, const std::string&) override { return FrameList{}; }

    FrameList remove(const std::string& value) override {
        FrameList frames;
        if (!search(root_.get(), value)) {
            frames.push_back(snapshot(StepType::Done, "未找到 " + value, {}, "#FFC107"));
            return frames;
        }
        deleteNode(root_.get(), value, frames);
        if (root_->keys.empty() && !root_->leaf) {
            root_ = std::move(root_->children[0]);
            frames.push_back(snapshot(StepType::Merge, "根高度下降一层",
                {root_->id}, "#FF5722"));
        }
        frames.push_back(snapshot(StepType::Done,
            "删除 " + value + " 完成，共 " + std::to_string(countKeys()) + " 个键",
            {}, "#FFC107"));
        return frames;
    }

    FrameList removeAt(int) override { return FrameList{}; }

    FrameList find(const std::string& value) override {
        FrameList frames;
        Node* cur = root_.get();
        while (cur) {
            frames.push_back(snapshot(StepType::Compare, "在节点比较 " + value,
                {cur->id}, "#FFC107"));
            int i = 0;
            while (i < (int)cur->keys.size() && compareValues(value, cur->keys[i]) > 0) i++;
            if (i < (int)cur->keys.size() && cur->keys[i] == value) {
                frames.push_back(snapshot(StepType::Highlight, "找到 " + value,
                    {cur->id}, "#4CAF50"));
                return frames;
            }
            if (cur->leaf) {
                frames.push_back(snapshot(StepType::Done, "未找到 " + value,
                    {cur->id}, "#FFC107"));
                return frames;
            }
            cur = cur->children[i].get();
        }
        return frames;
    }

    FrameList clear() override {
        root_ = std::make_unique<Node>();
        FrameList f; f.push_back(snapshot(StepType::Done, "已清空 B 树", {}, "#FFC107"));
        return f;
    }

    Frame currentFrame() const override {
        return snapshot(StepType::Done, "当前 B 树状态", {}, "#FFC107");
    }

    std::vector<std::string> snapshotValues() const override {
        std::vector<std::string> v;
        std::function<void(const Node*)> ino = [&](const Node* p) {
            if (!p) return;
            if (p->leaf) { for (auto& k : p->keys) v.push_back(k); }
            else {
                for (size_t i = 0; i < p->keys.size(); ++i) {
                    ino(p->children[i].get());
                    v.push_back(p->keys[i]);
                }
                ino(p->children.back().get());
            }
        };
        ino(root_.get());
        return v;
    }

private:
    int t_ = 2;
    std::unique_ptr<Node> root_;

    // ---- search ----
    bool search(const Node* node, const std::string& k) const {
        int i = 0;
        while (i < (int)node->keys.size() && compareValues(k, node->keys[i]) > 0) i++;
        if (i < (int)node->keys.size() && node->keys[i] == k) return true;
        if (node->leaf) return false;
        return search(node->children[i].get(), k);
    }

    // ---- insert ----
    void splitChild(Node* parent, int i, FrameList& frames) {
        Node* y = parent->children[i].get();
        auto z = std::make_unique<Node>();
        z->leaf = y->leaf;
        int mid = t_ - 1;
        std::string median = y->keys[mid];
        for (int j = mid + 1; j < (int)y->keys.size(); ++j) z->keys.push_back(y->keys[j]);
        y->keys.resize(mid);
        if (!y->leaf) {
            for (int j = mid + 1; j < (int)y->children.size(); ++j)
                z->children.push_back(std::move(y->children[j]));
            y->children.resize(mid + 1);
        }
        parent->keys.insert(parent->keys.begin() + i, median);
        parent->children.insert(parent->children.begin() + i + 1, std::move(z));
    }

    void insertNonFull(Node* node, const std::string& k, FrameList& frames) {
        int i = (int)node->keys.size() - 1;
        if (node->leaf) {
            while (i >= 0 && compareValues(k, node->keys[i]) < 0) i--;
            node->keys.insert(node->keys.begin() + i + 1, k);
            frames.push_back(snapshot(StepType::InsertValue, "在叶子节点插入 " + k,
                {node->id}, "#4CAF50"));
        } else {
            while (i >= 0 && compareValues(k, node->keys[i]) < 0) i--;
            i++;
            frames.push_back(snapshot(StepType::Traverse, "下降到子节点 (比较键 " + k + ")",
                {node->id}, "#FFC107"));
            if ((int)node->children[i]->keys.size() == 2 * t_ - 1) {
                splitChild(node, i, frames);
                frames.push_back(snapshot(StepType::Split, "子节点已满，分裂",
                    {node->id}, "#FF5722"));
                if (compareValues(k, node->keys[i]) > 0) i++;
            }
            insertNonFull(node->children[i].get(), k, frames);
        }
    }

    // ---- delete helpers ----
    std::string maxKey(Node* node) {
        while (!node->leaf) node = node->children.back().get();
        return node->keys.back();
    }
    std::string minKey(Node* node) {
        while (!node->leaf) node = node->children.front().get();
        return node->keys.front();
    }

    void borrowFromPrev(Node* parent, int i) {
        Node* child = parent->children[i].get();
        Node* sibling = parent->children[i - 1].get();
        child->keys.insert(child->keys.begin(), parent->keys[i - 1]);
        parent->keys[i - 1] = sibling->keys.back();
        sibling->keys.pop_back();
        if (!child->leaf) {
            child->children.insert(child->children.begin(),
                std::move(sibling->children.back()));
            sibling->children.pop_back();
        }
    }

    void borrowFromNext(Node* parent, int i) {
        Node* child = parent->children[i].get();
        Node* sibling = parent->children[i + 1].get();
        child->keys.push_back(parent->keys[i]);
        parent->keys[i] = sibling->keys.front();
        sibling->keys.erase(sibling->keys.begin());
        if (!child->leaf) {
            child->children.push_back(std::move(sibling->children.front()));
            sibling->children.erase(sibling->children.begin());
        }
    }

    void merge(Node* parent, int i) {
        Node* child = parent->children[i].get();
        std::unique_ptr<Node> sibling = std::move(parent->children[i + 1]);
        child->keys.push_back(parent->keys[i]);
        for (auto& key : sibling->keys) child->keys.push_back(std::move(key));
        if (!child->leaf)
            for (auto& c : sibling->children) child->children.push_back(std::move(c));
        parent->keys.erase(parent->keys.begin() + i);
        parent->children.erase(parent->children.begin() + i + 1);
    }

    void deleteNode(Node* node, const std::string& k, FrameList& frames) {
        int i = 0;
        while (i < (int)node->keys.size() && compareValues(k, node->keys[i]) > 0) i++;
        if (i < (int)node->keys.size() && node->keys[i] == k) {
            if (node->leaf) {
                node->keys.erase(node->keys.begin() + i);
                frames.push_back(snapshot(StepType::RemoveValue, "在叶子节点删除 " + k,
                    {node->id}, "#FF9800"));
            } else {
                if ((int)node->children[i]->keys.size() >= t_) {
                    std::string pred = maxKey(node->children[i].get());
                    node->keys[i] = pred;
                    frames.push_back(snapshot(StepType::Swap, "用前驱 " + pred + " 替换",
                        {node->id}, "#FF9800"));
                    deleteNode(node->children[i].get(), pred, frames);
                } else if ((int)node->children[i + 1]->keys.size() >= t_) {
                    std::string succ = minKey(node->children[i + 1].get());
                    node->keys[i] = succ;
                    frames.push_back(snapshot(StepType::Swap, "用后继 " + succ + " 替换",
                        {node->id}, "#FF9800"));
                    deleteNode(node->children[i + 1].get(), succ, frames);
                } else {
                    merge(node, i);
                    frames.push_back(snapshot(StepType::Merge, "合并子节点",
                        {node->id}, "#FF5722"));
                    deleteNode(node->children[i].get(), k, frames);
                }
            }
        } else {
            if (node->leaf) {
                frames.push_back(snapshot(StepType::Done, "未找到 " + k, {node->id}, "#FFC107"));
                return;
            }
            frames.push_back(snapshot(StepType::Traverse, "下降到子节点查找 " + k,
                {node->id}, "#FFC107"));
            if ((int)node->children[i]->keys.size() < t_) {
                if (i > 0 && (int)node->children[i - 1]->keys.size() >= t_) {
                    borrowFromPrev(node, i);
                    frames.push_back(snapshot(StepType::Rebalance, "向左兄弟借一个键",
                        {node->id}, "#FF5722"));
                } else if (i < (int)node->children.size() - 1 &&
                           (int)node->children[i + 1]->keys.size() >= t_) {
                    borrowFromNext(node, i);
                    frames.push_back(snapshot(StepType::Rebalance, "向右兄弟借一个键",
                        {node->id}, "#FF5722"));
                } else {
                    if (i < (int)node->children.size() - 1) {
                        merge(node, i);
                        frames.push_back(snapshot(StepType::Merge, "合并子节点",
                            {node->id}, "#FF5722"));
                        deleteNode(node->children[i].get(), k, frames);
                    } else {
                        merge(node, i - 1);
                        frames.push_back(snapshot(StepType::Merge, "合并子节点",
                            {node->id}, "#FF5722"));
                        deleteNode(node->children[i - 1].get(), k, frames);
                    }
                    return;
                }
            }
            deleteNode(node->children[i].get(), k, frames);
        }
    }

    // ---- frame support ----
    void collect(const Node* node, Frame& f) const {
        if (!node) return;
        std::string val;
        for (size_t i = 0; i < node->keys.size(); ++i) {
            val += node->keys[i];
            if (i + 1 < node->keys.size()) val += " | ";
        }
        f.nodes.push_back({node->id, val, node->leaf ? "叶" : "内部", -1});
        for (size_t j = 0; j < node->children.size(); ++j) {
            f.edges.push_back({node->id, node->children[j]->id, "c" + std::to_string(j)});
            collect(node->children[j].get(), f);
        }
    }

    Frame snapshot(StepType t, const std::string& d, const std::vector<int>& hl,
                   const std::string& c) const {
        Frame f; f.type = t; f.description = d; f.highlightColor = c; f.highlightIds = hl;
        collect(root_.get(), f);
        return f;
    }

    int countKeys() const {
        int n = 0;
        std::function<void(const Node*)> w = [&](const Node* p) {
            if (!p) return;
            n += (int)p->keys.size();
            for (auto& c : p->children) w(c.get());
        };
        w(root_.get());
        return n;
    }
};

} // namespace dsv
