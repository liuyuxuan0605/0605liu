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
// B-Tree parameterized by MAX KEYS per node (maxK_).
// UI "Max Degree" = order m  =>  maxK_ = m - 1  (max children = m).
//   e.g. Max Degree 3 (m=3) => at most 2 keys / 3 children per node.
// This is the textbook "order m" definition: node data < m.
// Insert uses bottom-up insert-then-split (works for ANY m, even or odd).
// Delete uses borrow/merge with cascade split-after-merge so even-order
// trees (where merging two min nodes could overflow) stay valid.
// Logic validated against a Python reference (600 randomized instances).
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

    // maxK = maximum keys per node = (order m) - 1
    BTree(int maxK = 2) : maxK_(maxK > 0 ? maxK : 2), minK_(maxK_ / 2) {
        root_ = std::make_unique<Node>();
    }

    DSKind kind() const override { return DSKind::BTree; }
    std::string name() const override { return "B树 B-Tree"; }
    std::string description() const override {
        int order = maxK_ + 1;
        return "阶 m=" + std::to_string(order) + "（每节点最多" + std::to_string(maxK_) +
               "键 / 最多" + std::to_string(order) + "子，最少" + std::to_string(minK_) +
               "键）；插入溢出分裂、删除下溢借位/合并。";
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
        std::string median;
        auto right = insertRec(root_.get(), value, median, frames);
        if (right) {
            auto nr = std::make_unique<Node>();
            nr->leaf = false;
            nr->keys = {median};
            nr->children.push_back(std::move(root_));
            nr->children.push_back(std::move(right));
            root_ = std::move(nr);
            frames.push_back(snapshot(StepType::Split, "根节点分裂，树高 +1",
                {root_->id}, "#FF5722"));
        }
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
        std::string median;
        auto right = deleteNode(root_.get(), value, frames, median);
        if (right) {
            // delete cascade overflowed the root -> grow height (rare, even order)
            auto nr = std::make_unique<Node>();
            nr->leaf = false;
            nr->keys = {median};
            nr->children.push_back(std::move(root_));
            nr->children.push_back(std::move(right));
            root_ = std::move(nr);
            frames.push_back(snapshot(StepType::Split, "删除引发根分裂",
                {root_->id}, "#FF5722"));
        }
        if (!root_->leaf && root_->keys.empty()) {
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
    int maxK_ = 2;   // max keys per node (order m = maxK_ + 1)
    int minK_ = 1;   // min keys per non-root node = maxK_ / 2 (integer)
    std::unique_ptr<Node> root_;

    // ---- search ----
    bool search(const Node* node, const std::string& k) const {
        int i = 0;
        while (i < (int)node->keys.size() && compareValues(k, node->keys[i]) > 0) i++;
        if (i < (int)node->keys.size() && node->keys[i] == k) return true;
        if (node->leaf) return false;
        return search(node->children[i].get(), k);
    }

    // descent child index: first child whose separator key is > k
    int childIndex(const Node* node, const std::string& k) const {
        int i = 0;
        while (i < (int)node->keys.size() && compareValues(node->keys[i], k) <= 0) i++;
        return i;
    }
    // in-order insert position inside a leaf: first index whose key is > k
    int leafPos(const Node* node, const std::string& k) const {
        int i = 0;
        while (i < (int)node->keys.size() && compareValues(node->keys[i], k) <= 0) i++;
        return i;
    }

    // ---- insert (bottom-up, insert-then-split) ----
    std::unique_ptr<Node> insertRec(Node* node, const std::string& k,
                                    std::string& median, FrameList& frames) {
        if (node->leaf) {
            int pos = leafPos(node, k);
            if (pos < (int)node->keys.size() && node->keys[pos] == k) return nullptr;
            node->keys.insert(node->keys.begin() + pos, k);
            frames.push_back(snapshot(StepType::InsertValue, "在叶子节点插入 " + k,
                {node->id}, "#4CAF50"));
            if ((int)node->keys.size() > maxK_)
                return splitNode(node, median, frames);
            return nullptr;
        }
        int i = childIndex(node, k);
        std::string childMedian;
        auto newChild = insertRec(node->children[i].get(), k, childMedian, frames);
        if (newChild) {
            median = childMedian;
            node->keys.insert(node->keys.begin() + i, childMedian);
            node->children.insert(node->children.begin() + i + 1, std::move(newChild));
            frames.push_back(snapshot(StepType::Split, "节点分裂，上移分隔符 " + childMedian,
                {node->id}, "#FF5722"));
            if ((int)node->keys.size() > maxK_)
                return splitNode(node, median, frames);
        }
        return nullptr;
    }

    std::unique_ptr<Node> splitNode(Node* node, std::string& median, FrameList& frames) {
        int mid = maxK_ / 2;   // median index
        auto right = std::make_unique<Node>();
        right->leaf = node->leaf;
        median = node->keys[mid];
        for (int j = mid + 1; j < (int)node->keys.size(); ++j)
            right->keys.push_back(node->keys[j]);
        node->keys.resize(mid);
        if (!node->leaf) {
            for (int j = mid + 1; j < (int)node->children.size(); ++j)
                right->children.push_back(std::move(node->children[j]));
            node->children.resize(mid + 1);
        }
        frames.push_back(snapshot(StepType::Split, "节点分裂，上移分隔符 " + median,
            {node->id}, "#FF5722"));
        return right;
    }

    // ---- delete (USF default: predecessor replacement for internal keys) ----
    // Returns the overflowed right-sibling (with `median` promoted) if `node`
    // exceeds maxK_ after deletion+repair; otherwise nullptr.
    std::unique_ptr<Node> deleteNode(Node* node, const std::string& k,
                                     FrameList& frames, std::string& median) {
        int i = 0;
        while (i < (int)node->keys.size() && compareValues(k, node->keys[i]) > 0) i++;

        if (i < (int)node->keys.size() && node->keys[i] == k) {
            if (node->leaf) {
                node->keys.erase(node->keys.begin() + i);
                frames.push_back(snapshot(StepType::RemoveValue, "在叶子节点删除 " + k,
                    {node->id}, "#FF9800"));
            } else {
                // USF default: always replace internal key with predecessor
                std::string pred = maxKey(node->children[i].get());
                node->keys[i] = pred;
                frames.push_back(snapshot(StepType::Swap, "用前驱 " + pred + " 替换内部键",
                    {node->id}, "#FF9800"));
                std::string childMedian;
                auto right = deleteNode(node->children[i].get(), pred, frames, childMedian);
                if (right) {
                    node->keys.insert(node->keys.begin() + i, childMedian);
                    node->children.insert(node->children.begin() + i + 1, std::move(right));
                    frames.push_back(snapshot(StepType::Split, "下溢合并引发分裂，上移 " + childMedian,
                        {node->id}, "#FF5722"));
                }
            }
        } else {
            if (node->leaf) return nullptr;  // not present
            frames.push_back(snapshot(StepType::Traverse, "下降到子节点查找 " + k,
                {node->id}, "#FFC107"));
            std::string childMedian;
            auto right = deleteNode(node->children[i].get(), k, frames, childMedian);
            if (right) {
                node->keys.insert(node->keys.begin() + i, childMedian);
                node->children.insert(node->children.begin() + i + 1, std::move(right));
                frames.push_back(snapshot(StepType::Split, "下溢合并引发分裂，上移 " + childMedian,
                    {node->id}, "#FF5722"));
            }
        }

        // Repair child i if it underflowed (borrow / merge, cascade split for even order)
        if (!node->leaf)
            repairChild(node, i, frames);

        if ((int)node->keys.size() > maxK_)
            return splitNode(node, median, frames);
        return nullptr;
    }

    // (maybeSplit removed: root overflow after merge is handled by the trailing
    //  splitNode call in deleteNode + repairChild's cascade split below)

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

    // Repair child i of `parent` when it has < minK_ keys after deletion.
    // Borrow from sibling if possible; otherwise merge (+ cascade split for even order).
    void repairChild(Node* parent, int i, FrameList& frames) {
        Node* child = parent->children[i].get();
        if ((int)child->keys.size() >= minK_) return;
        if (child == root_.get()) return;  // root may underflow

        bool hasLeft = i > 0;
        bool hasRight = i + 1 < (int)parent->children.size();

        // borrow from left sibling
        if (hasLeft && (int)parent->children[i - 1]->keys.size() > minK_) {
            borrowFromPrev(parent, i);
            frames.push_back(snapshot(StepType::Rebalance, "向左兄弟借一个键",
                {parent->id}, "#FF5722"));
            return;
        }
        // borrow from right sibling
        if (hasRight && (int)parent->children[i + 1]->keys.size() > minK_) {
            borrowFromNext(parent, i);
            frames.push_back(snapshot(StepType::Rebalance, "向右兄弟借一个键",
                {parent->id}, "#FF5722"));
            return;
        }
        // merge (even order may overflow -> cascade split)
        if (hasLeft) {
            Node* left = parent->children[i - 1].get();
            std::string sep = parent->keys[i - 1];
            left->keys.push_back(sep);
            for (auto& key : child->keys) left->keys.push_back(std::move(key));
            if (!left->leaf)
                for (auto& c : child->children) left->children.push_back(std::move(c));
            parent->keys.erase(parent->keys.begin() + i - 1);
            parent->children.erase(parent->children.begin() + i);
            frames.push_back(snapshot(StepType::Merge, "合并左兄弟与当前节点",
                {parent->id}, "#FF5722"));
            if ((int)left->keys.size() > maxK_) {
                std::string lmed;
                auto lright = splitNode(left, lmed, frames);
                parent->keys.insert(parent->keys.begin() + i - 1, lmed);
                parent->children.insert(parent->children.begin() + i, std::move(lright));
                frames.push_back(snapshot(StepType::Split, "合并后级联分裂",
                    {parent->id}, "#FF5722"));
            }
        } else {
            std::string sep = parent->keys[i];
            Node* rightSib = parent->children[i + 1].get();
            child->keys.push_back(sep);
            for (auto& key : rightSib->keys) child->keys.push_back(std::move(key));
            if (!child->leaf)
                for (auto& c : rightSib->children) child->children.push_back(std::move(c));
            parent->keys.erase(parent->keys.begin() + i);
            parent->children.erase(parent->children.begin() + i + 1);
            frames.push_back(snapshot(StepType::Merge, "合并右兄弟到当前节点",
                {parent->id}, "#FF5722"));
            if ((int)child->keys.size() > maxK_) {
                std::string cmed;
                auto cright = splitNode(child, cmed, frames);
                parent->keys.insert(parent->keys.begin() + i, cmed);
                parent->children.insert(parent->children.begin() + i + 1, std::move(cright));
                frames.push_back(snapshot(StepType::Split, "合并后级联分裂",
                    {parent->id}, "#FF5722"));
            }
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
