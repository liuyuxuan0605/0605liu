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
// B+Tree (USF 风格, 包容式 inclusive 分裂).
//  - 阶 m = degree; 每节点最多 maxK_ = m-1 键 / 最多 m 子, 最少 minK_ 键.
//  - 叶存全部数据; 内部分隔符 = 右孩子最左叶首键的"副本"(包容式), 便于与
//    参考工具(USF B+ Tree Visualization)树形一致. 分裂左留 splitIdx_ 键.
//  - 删除内部分隔符 v 时: 用前驱(左子树最大叶键)替换 v 在右叶的副本与内部键,
//    再从左侧叶递归删前驱, 触发下溢修复(借位/合并); 每次操作后 resync() 重算
//    所有分隔符, 维持"分隔符=右孩子最左叶首键"不变式, 杜绝副本陈旧/丢数据.
//  - 节点值 = keys 用 " | " 连接; 子节点边 kind = "c" + j; 叶子按中序遍历
//    用 "next" 边串成链表供可视化.
// 算法经 Python 镜像 300 轮随机插删(degree 3~7)验证: 结构合法 + 数据零丢失.
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

    // degree = 阶 m (textbook): 节点最多 m-1 键.
    BPlusTree(int degree = 3)
        : maxK_(degree - 1),
          minK_((degree + 1) / 2 - 1),
          splitIdx_((degree - 1) / 2) {
        if (maxK_ < 1) { maxK_ = 1; minK_ = 1; splitIdx_ = 1; }
        root_ = std::make_unique<Node>(true);
    }

    DSKind kind() const override { return DSKind::BPlusTree; }
    std::string name() const override { return "B+树 B+Tree"; }
    std::string description() const override {
        int order = maxK_ + 1;
        return "阶 m=" + std::to_string(order) + "（每节点最多" + std::to_string(maxK_) +
               "键，最少" + std::to_string(minK_) + "键）；叶存全部数据并向上复制分隔符，"
               "内部仅路由。USF 风格分裂（左留" + std::to_string(splitIdx_) +
               "键）+ 前驱替换删除（借位/合并）。";
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
        resync();
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
    int maxK_ = 2;
    int minK_ = 1;
    int splitIdx_ = 1;
    std::unique_ptr<Node> root_;

    // ---- descent helpers ----
    // 下降(插入用): 计 "键 <= k" 的个数 (分隔符落在右子树, 包容式约定)
    int childIndex(const Node* node, const std::string& k) const {
        int i = 0;
        while (i < (int)node->keys.size() && compareValues(k, node->keys[i]) >= 0) i++;
        return i;
    }
    // 叶内插入位置: 第一个 "键 > k" 的下标
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

    // 包容式叶子分裂: 左留 splitIdx_ 键; 上升键 = 右叶首键(副本保留在右叶首).
    std::unique_ptr<Node> splitLeaf(Node* node, std::string& sep) {
        auto right = std::make_unique<Node>(true);
        for (int j = splitIdx_; j < (int)node->keys.size(); ++j)
            right->keys.push_back(node->keys[j]);
        sep = right->keys.empty() ? "" : right->keys[0];
        node->keys.resize(splitIdx_);
        return right;
    }

    std::unique_ptr<Node> splitInternal(Node* node, std::string& sep) {
        auto right = std::make_unique<Node>(false);
        sep = node->keys[splitIdx_];
        for (int j = splitIdx_ + 1; j < (int)node->keys.size(); ++j)
            right->keys.push_back(node->keys[j]);
        node->keys.resize(splitIdx_);
        for (int j = splitIdx_ + 1; j < (int)node->children.size(); ++j)
            right->children.push_back(std::move(node->children[j]));
        node->children.resize(splitIdx_ + 1);
        return right;
    }

    // ---- delete ----
    std::string maxLeafKey(Node* n) {
        while (!n->leaf) n = n->children.back().get();
        return n->keys.back();
    }
    Node* leftmostLeaf(Node* n) {
        while (!n->leaf) n = n->children[0].get();
        return n;
    }

    // 返回是否找到并删除. 删除内部分隔符时维持包容式不变式.
    bool deleteRec(Node* node, const std::string& k, FrameList& frames) {
        if (node->leaf) {
            auto it = std::find(node->keys.begin(), node->keys.end(), k);
            if (it != node->keys.end()) {
                node->keys.erase(it);
                frames.push_back(snapshot(StepType::RemoveValue, "在叶子删除 " + k,
                    {node->id}, "#FF9800"));
                return true;
            }
            return false;
        }
        int i = 0;
        while (i < (int)node->keys.size() && compareValues(k, node->keys[i]) > 0) i++;
        bool found;
        if (i < (int)node->keys.size() && node->keys[i] == k) {
            // k 是内部分隔符(包容式: =右孩子最左叶首键副本)
            std::string pred = maxLeafKey(node->children[i].get());   // 左子树最大叶键
            Node* rleaf = leftmostLeaf(node->children[i + 1].get());  // 右孩子最左叶
            rleaf->keys[0] = pred;        // 把右叶首位的 k 副本换成前驱
            node->keys[i] = pred;         // 内部键也改成前驱
            frames.push_back(snapshot(StepType::Swap,
                "内部键 " + k + " 用前驱 " + pred + " 替换(同步右叶副本)",
                {node->id}, "#FF9800"));
            found = deleteRec(node->children[i].get(), pred, frames);
            if (found) fixChild(node, i, frames);
        } else {
            found = deleteRec(node->children[i].get(), k, frames);
            if (found) fixChild(node, i, frames);
        }
        return found;
    }

    void fixChild(Node* parent, int i, FrameList& frames) {
        Node* child = parent->children[i].get();
        if ((int)child->keys.size() >= minK_ || child == root_.get()) return;
        if (i > 0 && (int)parent->children[i - 1]->keys.size() > minK_) {
            borrowFromLeft(parent, i, frames);
        } else if (i + 1 < (int)parent->children.size() &&
                   (int)parent->children[i + 1]->keys.size() > minK_) {
            borrowFromRight(parent, i, frames);
        } else {
            if (i > 0) mergeWithLeft(parent, i, frames);
            else mergeWithRight(parent, i, frames);
        }
    }

    void borrowFromLeft(Node* parent, int i, FrameList& frames) {
        Node* child = parent->children[i].get();
        Node* left = parent->children[i - 1].get();
        if (child->leaf) {
            child->keys.insert(child->keys.begin(), left->keys.back());
            left->keys.pop_back();
            parent->keys[i - 1] = child->keys[0];
        } else {
            child->keys.insert(child->keys.begin(), parent->keys[i - 1]);
            parent->keys[i - 1] = left->keys.back();
            left->keys.pop_back();
            std::unique_ptr<Node> moved = std::move(left->children.back());
            left->children.pop_back();
            child->children.insert(child->children.begin(), std::move(moved));
        }
        frames.push_back(snapshot(StepType::Rebalance, "向左兄弟借键",
            {parent->id}, "#FF5722"));
    }

    void borrowFromRight(Node* parent, int i, FrameList& frames) {
        Node* child = parent->children[i].get();
        Node* right = parent->children[i + 1].get();
        if (child->leaf) {
            child->keys.push_back(right->keys.front());
            right->keys.erase(right->keys.begin());
            parent->keys[i] = right->keys.empty() ? "" : right->keys.front();
        } else {
            child->keys.push_back(parent->keys[i]);
            parent->keys[i] = right->keys.front();
            right->keys.erase(right->keys.begin());
            std::unique_ptr<Node> moved = std::move(right->children.front());
            right->children.erase(right->children.begin());
            child->children.push_back(std::move(moved));
        }
        frames.push_back(snapshot(StepType::Rebalance, "向右兄弟借键",
            {parent->id}, "#FF5722"));
    }

    void mergeWithLeft(Node* parent, int i, FrameList& frames) {
        Node* child = parent->children[i].get();
        Node* left = parent->children[i - 1].get();
        std::string sep = parent->keys[i - 1];
        if (!child->leaf) left->keys.push_back(sep);
        for (auto& kv : child->keys) left->keys.push_back(kv);
        if (!child->leaf) {
            for (auto& c : child->children) left->children.push_back(std::move(c));
        }
        // 注意: 必须在用完 child 原始指针后再从 parent 移除(避免悬空)
        parent->keys.erase(parent->keys.begin() + i - 1);
        parent->children.erase(parent->children.begin() + i);
        frames.push_back(snapshot(StepType::Merge, "与左兄弟合并",
            {parent->id}, "#FF5722"));
    }

    void mergeWithRight(Node* parent, int i, FrameList& frames) {
        Node* child = parent->children[i].get();
        Node* right = parent->children[i + 1].get();
        std::string sep = parent->keys[i];
        if (!child->leaf) child->keys.push_back(sep);
        for (auto& kv : right->keys) child->keys.push_back(kv);
        if (!child->leaf) {
            for (auto& c : right->children) child->children.push_back(std::move(c));
        }
        parent->keys.erase(parent->keys.begin() + i);
        parent->children.erase(parent->children.begin() + i + 1);
        frames.push_back(snapshot(StepType::Merge, "与右兄弟合并",
            {parent->id}, "#FF5722"));
    }

    // 重算所有分隔符 = 右孩子最左叶首键 (维持包容式不变式)
    void resync() {
        if (root_->leaf) return;
        resyncRec(root_.get());
    }
    std::string resyncRec(Node* node) {
        if (node->leaf) return node->keys.empty() ? "" : node->keys[0];
        std::vector<std::string> mins;
        for (auto& c : node->children) mins.push_back(resyncRec(c.get()));
        for (int j = 0; j < (int)node->keys.size(); ++j)
            node->keys[j] = (j + 1 < (int)mins.size()) ? mins[j + 1] : node->keys[j];
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
