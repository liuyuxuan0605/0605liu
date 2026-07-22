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
// B+Tree (max 3 keys per node, min 1). Internal nodes store SEPARATORS only
// (routing keys); all data lives in leaves. Leaves are linked via an implicit
// chain (in-order traversal) -> emitted as "next" edges for visualization.
// Node value = keys joined by " | "; child j edge kind = "c" + j.
// Algorithm mirrors bplustree_ref.py (validated 300 randomized trials).
// ---------------------------------------------------------------------------
class BPlusTree : public IDataStructure {
public:
    struct Node {
        std::vector<std::string> keys;
        std::vector<std::unique_ptr<Node>> children;
        bool leaf = false;
        int id;
        Node(bool l = false) : leaf(l), id(nextId()) {}
    };

    BPlusTree(int maxK = 3) : maxK_(maxK), minK_(maxK > 0 ? maxK / 2 : 1) { root_ = std::make_unique<Node>(true); }

    DSKind kind() const override { return DSKind::BPlusTree; }
    std::string name() const override { return "B+树 B+Tree"; }
    std::string description() const override {
        return "阶数 m=" + std::to_string(maxK_) + "（每节点最多" + std::to_string(maxK_) +
               "键，最少" + std::to_string(minK_) + "键）；叶存数据、内部仅路由。插入溢出分裂、删除下溢借位/合并。";
    }

    int size() const override {
        int n = 0;
        std::function<void(const Node*)> w = [&](const Node* p) {
            if (!p) return;
            if (p->leaf) n += (int)p->keys.size();
            else for (auto& c : p->children) w(c.get());
        };
        w(root_.get());
        return n;
    }
    bool empty() const override { return root_->leaf && root_->keys.empty(); }

    FrameList insert(const std::string& value) override {
        FrameList frames;
        if (search(value)) {
            frames.push_back(snapshot(StepType::Done, "值 " + value + " 已存在，忽略",
                {}, "#FFC107"));
            return frames;
        }
        std::string sep;
        auto newRight = insertRec(root_.get(), value, sep, frames);
        if (newRight) {
            auto nr = std::make_unique<Node>(false);
            nr->keys = {sep};
            nr->children.push_back(std::move(root_));
            nr->children.push_back(std::move(newRight));
            root_ = std::move(nr);
            frames.push_back(snapshot(StepType::Split, "根分裂，树高 +1",
                {root_->id}, "#FF5722"));
        }
        frames.push_back(snapshot(StepType::Done, "插入 " + value + " 完成", {}, "#FFC107"));
        return frames;
    }

    FrameList insertAt(int, const std::string&) override { return FrameList{}; }

    FrameList remove(const std::string& value) override {
        FrameList frames;
        if (!search(value)) {
            frames.push_back(snapshot(StepType::Done, "未找到 " + value, {}, "#FFC107"));
            return frames;
        }
        deleteRec(root_.get(), value, frames);
        if (!root_->leaf && root_->keys.empty()) {
            root_ = std::move(root_->children[0]);
            frames.push_back(snapshot(StepType::Merge, "根高度下降一层",
                {root_->id}, "#FF5722"));
        }
        resync();
        frames.push_back(snapshot(StepType::Done, "删除 " + value + " 完成", {}, "#FFC107"));
        return frames;
    }

    FrameList removeAt(int) override { return FrameList{}; }

    FrameList find(const std::string& value) override {
        FrameList frames;
        Node* cur = root_.get();
        while (cur) {
            frames.push_back(snapshot(StepType::Compare, "在节点比较 " + value,
                {cur->id}, "#FFC107"));
            if (cur->leaf) {
                if (std::find(cur->keys.begin(), cur->keys.end(), value) != cur->keys.end()) {
                    frames.push_back(snapshot(StepType::Highlight, "找到 " + value,
                        {cur->id}, "#4CAF50"));
                    return frames;
                }
                frames.push_back(snapshot(StepType::Done, "未找到 " + value,
                    {cur->id}, "#FFC107"));
                return frames;
            }
            int i = childIndex(cur, value);
            cur = cur->children[i].get();
        }
        return frames;
    }

    FrameList clear() override {
        root_ = std::make_unique<Node>(true);
        FrameList f; f.push_back(snapshot(StepType::Done, "已清空 B+ 树", {}, "#FFC107"));
        return f;
    }

    Frame currentFrame() const override {
        return snapshot(StepType::Done, "当前 B+ 树状态", {}, "#FFC107");
    }

    std::vector<std::string> snapshotValues() const override {
        std::vector<std::string> v;
        std::function<void(const Node*)> ino = [&](const Node* n) {
            if (!n) return;
            if (n->leaf) { for (auto& k : n->keys) v.push_back(k); }
            else { for (auto& c : n->children) ino(c.get()); }
        };
        ino(root_.get());
        return v;
    }

private:
    int maxK_ = 3;   // max keys per node (max degree = maxK + 1)
    int minK_ = 1;   // min keys per node (for underflow detection)
    std::unique_ptr<Node> root_;

    // child index for descent: count of keys <= k  (B+tree separator convention)
    int childIndex(const Node* node, const std::string& k) const {
        int i = 0;
        while (i < (int)node->keys.size() && compareValues(k, node->keys[i]) >= 0) i++;
        return i;
    }
    // insert position inside a leaf (first index where key > k)
    int leafPos(const Node* node, const std::string& k) const {
        int i = 0;
        while (i < (int)node->keys.size() && compareValues(k, node->keys[i]) > 0) i++;
        return i;
    }

    bool search(const std::string& k) const {
        Node* node = root_.get();
        while (!node->leaf) {
            int i = childIndex(node, k);
            node = node->children[i].get();
        }
        return std::find(node->keys.begin(), node->keys.end(), k) != node->keys.end();
    }

    // ---- insert ----
    std::unique_ptr<Node> insertRec(Node* node, const std::string& k,
                                    std::string& sep, FrameList& frames) {
        if (node->leaf) {
            int pos = leafPos(node, k);
            if (pos < (int)node->keys.size() && node->keys[pos] == k) return nullptr;
            node->keys.insert(node->keys.begin() + pos, k);
            frames.push_back(snapshot(StepType::InsertValue, "在叶子插入 " + k,
                {node->id}, "#4CAF50"));
            if ((int)node->keys.size() > maxK_) {
                auto sp = splitLeaf(node, sep);
                frames.push_back(snapshot(StepType::Split, "叶子分裂",
                    {node->id}, "#FF5722"));
                return sp;
            }
            return nullptr;
        }
        int i = childIndex(node, k);
        std::string childSep;
        auto newChild = insertRec(node->children[i].get(), k, childSep, frames);
        if (newChild) {
            sep = childSep;
            node->keys.insert(node->keys.begin() + i, childSep);
            node->children.insert(node->children.begin() + i + 1, std::move(newChild));
            frames.push_back(snapshot(StepType::Split, "节点分裂，上移分隔符 " + childSep,
                {node->id}, "#FF5722"));
            if ((int)node->keys.size() > maxK_) {
                auto sp = splitInternal(node, sep);
                frames.push_back(snapshot(StepType::Split, "内部节点溢出，再次分裂",
                    {node->id}, "#FF5722"));
                return sp;
            }
        }
        return nullptr;
    }

    std::unique_ptr<Node> splitLeaf(Node* node, std::string& sep) {
        int mid = (int)(node->keys.size() + 1) / 2;
        auto right = std::make_unique<Node>(true);
        for (int j = mid; j < (int)node->keys.size(); ++j)
            right->keys.push_back(node->keys[j]);
        node->keys.resize(mid);
        sep = right->keys[0];
        return right;
    }

    std::unique_ptr<Node> splitInternal(Node* node, std::string& sep) {
        int mid = (int)node->keys.size() / 2;
        auto right = std::make_unique<Node>(false);
        sep = node->keys[mid];
        for (int j = mid + 1; j < (int)node->keys.size(); ++j)
            right->keys.push_back(node->keys[j]);
        node->keys.resize(mid);
        for (int j = mid + 1; j < (int)node->children.size(); ++j)
            right->children.push_back(std::move(node->children[j]));
        node->children.resize(mid + 1);
        return right;
    }

    // ---- delete ----
    void deleteRec(Node* node, const std::string& k, FrameList& frames) {
        if (node->leaf) {
            auto it = std::find(node->keys.begin(), node->keys.end(), k);
            if (it != node->keys.end()) {
                node->keys.erase(it);
                frames.push_back(snapshot(StepType::RemoveValue, "在叶子删除 " + k,
                    {node->id}, "#FF9800"));
            }
            return;
        }
        int i = childIndex(node, k);
        deleteRec(node->children[i].get(), k, frames);
        if ((int)node->children[i]->keys.size() < minK_)
            fixChild(node, i, frames);
    }

    void fixChild(Node* parent, int i, FrameList& frames) {
        Node* child = parent->children[i].get();
        if (i > 0 && (int)parent->children[i - 1]->keys.size() > minK_) {
            Node* left = parent->children[i - 1].get();
            if (child->leaf) {
                child->keys.insert(child->keys.begin(), left->keys.back());
                left->keys.pop_back();
            } else {
                std::unique_ptr<Node> moved = std::move(left->children.back());
                left->children.pop_back();
                child->children.insert(child->children.begin(), std::move(moved));
                child->keys.insert(child->keys.begin(), left->keys.back());
                left->keys.pop_back();
            }
            frames.push_back(snapshot(StepType::Rebalance, "向左兄弟借键",
                {parent->id}, "#FF5722"));
        } else if (i < (int)parent->children.size() - 1 &&
                   (int)parent->children[i + 1]->keys.size() > minK_) {
            Node* right = parent->children[i + 1].get();
            if (child->leaf) {
                child->keys.push_back(right->keys.front());
                right->keys.erase(right->keys.begin());
            } else {
                std::unique_ptr<Node> moved = std::move(right->children.front());
                right->children.erase(right->children.begin());
                child->children.push_back(std::move(moved));
                child->keys.push_back(right->keys.front());
                right->keys.erase(right->keys.begin());
            }
            frames.push_back(snapshot(StepType::Rebalance, "向右兄弟借键",
                {parent->id}, "#FF5722"));
        } else {
            if (i > 0) {
                Node* left = parent->children[i - 1].get();
                if (!child->leaf) left->keys.push_back(parent->keys[i - 1]);  // separator is data
                left->keys.insert(left->keys.end(), child->keys.begin(), child->keys.end());
                if (!child->leaf)
                    for (auto& c : child->children) left->children.push_back(std::move(c));
                parent->keys.erase(parent->keys.begin() + i - 1);
                parent->children.erase(parent->children.begin() + i);
                frames.push_back(snapshot(StepType::Merge, "与左兄弟合并",
                    {parent->id}, "#FF5722"));
            } else {
                Node* right = parent->children[i + 1].get();
                if (!child->leaf) child->keys.push_back(parent->keys[i]);     // separator is data
                child->keys.insert(child->keys.end(), right->keys.begin(), right->keys.end());
                if (!child->leaf)
                    for (auto& c : right->children) child->children.push_back(std::move(c));
                parent->keys.erase(parent->keys.begin() + i);
                parent->children.erase(parent->children.begin() + i + 1);
                frames.push_back(snapshot(StepType::Merge, "与右兄弟合并",
                    {parent->id}, "#FF5722"));
            }
        }
    }

    // Recompute every separator: separator[j] = min key of children[j+1].
    void resync() {
        if (root_->leaf) return;
        resyncRec(root_.get());
    }
    std::string resyncRec(Node* node) {
        if (node->leaf) return node->keys.empty() ? "" : node->keys[0];
        std::vector<std::string> mins;
        for (auto& c : node->children) mins.push_back(resyncRec(c.get()));
        for (int j = 0; j < (int)node->keys.size(); ++j)
            node->keys[j] = (j + 1 < (int)mins.size()) ? mins[j + 1] : "";
        return mins.empty() ? "" : mins[0];
    }

    // ---- frame support ----
    void collect(const Node* node, Frame& f, std::vector<int>& leafIds) const {
        std::string val;
        for (size_t i = 0; i < node->keys.size(); ++i) {
            val += node->keys[i];
            if (i + 1 < node->keys.size()) val += " | ";
        }
        f.nodes.push_back({node->id, val, node->leaf ? "叶" : "索引", -1});
        if (node->leaf) {
            leafIds.push_back(node->id);
        } else {
            for (size_t j = 0; j < node->children.size(); ++j) {
                f.edges.push_back({node->id, node->children[j]->id, "c" + std::to_string(j)});
                collect(node->children[j].get(), f, leafIds);
            }
        }
    }

    Frame snapshot(StepType t, const std::string& d, const std::vector<int>& hl,
                   const std::string& c) const {
        Frame f; f.type = t; f.description = d; f.highlightColor = c; f.highlightIds = hl;
        std::vector<int> leafIds;
        collect(root_.get(), f, leafIds);
        for (size_t k = 0; k + 1 < leafIds.size(); ++k)
            f.edges.push_back({leafIds[k], leafIds[k + 1], "next"});
        return f;
    }
};

} // namespace dsv
