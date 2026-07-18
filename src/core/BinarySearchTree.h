#pragma once
#include "Common.h"
#include "IDataStructure.h"
#include <memory>
#include <unordered_set>
#include <vector>

namespace dsv {

// ---------------------------------------------------------------------------
// Binary Search Tree  (iterative insert/remove, comparison-path animation)
// ---------------------------------------------------------------------------
class BinarySearchTree : public IDataStructure {
public:
    struct Node {
        std::string value; int id; int height = 1;
        std::unique_ptr<Node> left, right;
        Node* parent = nullptr;                 // non-owning
        Node(const std::string& v) : value(v), id(nextId()) {}
    };

    DSKind kind() const override { return DSKind::BinarySearchTree; }
    std::string name() const override { return "二叉搜索树 BST"; }
    std::string description() const override {
        return "左子树小于根、右子树大于根；插入/查找沿比较路径下行。";
    }

    int size() const override { return size_; }
    bool empty() const override { return size_ == 0; }

    FrameList insert(const std::string& value) override {
        FrameList frames;
        if (!root_) {
            auto n = std::make_unique<Node>(value);
            frames.push_back(makeFrame(StepType::CreateNode, "创建根节点 " + value,
                {n->id}, "#4CAF50", n.get()));
            root_ = std::move(n);
            frames.push_back(makeFrame(StepType::Link, "设为根", {root_->id}, "#4CAF50"));
            size_ = 1; frames.push_back(doneFrame("插入完成，节点数 1"));
            return frames;
        }
        Node* cur = root_.get();
        while (true) {
            frames.push_back(makeFrame(StepType::Compare,
                "比较 " + value + " 与 " + cur->value, {cur->id}, "#FFC107"));
            int c = compareValues(value, cur->value);
            if (c == 0) {
                frames.push_back(doneFrame("已存在 " + value + "，忽略重复"));
                return frames;
            }
            if (c < 0) {
                if (!cur->left) {
                    auto n = std::make_unique<Node>(value);
                    int newId = n->id;
                    frames.push_back(makeFrame(StepType::CreateNode, "创建节点 " + value,
                        {newId}, "#4CAF50", n.get()));
                    n->parent = cur; cur->left = std::move(n);
                    frames.push_back(makeFrame(StepType::Link, cur->value + " 的左子指向新节点",
                        {cur->id, newId}, "#4CAF50"));
                    size_++; frames.push_back(doneFrame("插入完成，节点数 " + std::to_string(size_)));
                    return frames;
                }
                cur = cur->left.get();
            } else {
                if (!cur->right) {
                    auto n = std::make_unique<Node>(value);
                    int newId = n->id;
                    frames.push_back(makeFrame(StepType::CreateNode, "创建节点 " + value,
                        {newId}, "#4CAF50", n.get()));
                    n->parent = cur; cur->right = std::move(n);
                    frames.push_back(makeFrame(StepType::Link, cur->value + " 的右子指向新节点",
                        {cur->id, newId}, "#4CAF50"));
                    size_++; frames.push_back(doneFrame("插入完成，节点数 " + std::to_string(size_)));
                    return frames;
                }
                cur = cur->right.get();
            }
        }
    }

    FrameList insertAt(int, const std::string&) override { return FrameList{}; }

    FrameList remove(const std::string& value) override {
        FrameList frames;
        Node* target = findNode(value, frames);
        if (!target) { frames.push_back(doneFrame("未找到 " + value)); return frames; }

        // case 1 & 2: at most one child
        if (!target->left || !target->right) {
            std::unique_ptr<Node> child = target->left ? std::move(target->left)
                                                       : std::move(target->right);
            frames.push_back(makeFrame(StepType::BreakLink, "断开目标节点",
                {target->id}, "#FF9800"));
            replaceInParent(target, std::move(child));
            frames.push_back(makeFrame(StepType::Link, "子节点接替目标位置",
                {}, "#4CAF50"));
        } else {
            // case 3: two children -> successor (min of right subtree)
            Node* succ = target->right.get();
            frames.push_back(makeFrame(StepType::Highlight, "目标有两子，找右子树最小(后继)",
                {target->id}, "#FFC107"));
            while (succ->left) {
                frames.push_back(makeFrame(StepType::Traverse, "后继向左下行 (值 " + succ->value + ")",
                    {succ->id}, "#FFC107"));
                succ = succ->left.get();
            }
            frames.push_back(makeFrame(StepType::Highlight, "后继为 " + succ->value,
                {succ->id}, "#FFC107"));
            target->value = succ->value;          // copy value (keep target id)
            frames.push_back(makeFrame(StepType::Swap, "用后继值替换目标值",
                {target->id}, "#BA68C8"));
            std::unique_ptr<Node> succChild = succ->right ? std::move(succ->right) : nullptr;
            replaceInParent(succ, std::move(succChild));
            frames.push_back(makeFrame(StepType::Link, "后继被移除，结构保持有序",
                {}, "#4CAF50"));
        }
        size_ = std::max(0, size_ - 1);
        frames.push_back(doneFrame("删除完成，节点数 " + std::to_string(size_)));
        return frames;
    }

    FrameList removeAt(int) override { return FrameList{}; }

    FrameList find(const std::string& value) override {
        FrameList frames;
        findNode(value, frames);
        return frames;
    }

    FrameList clear() override { root_.reset(); size_ = 0; FrameList f; f.push_back(doneFrame("已清空")); return f; }

    Frame currentFrame() const override { return makeFrame(StepType::Done, "当前 BST 状态", {}, "#FFC107"); }

    // --- 遍历：层序 BFS / 先序 DFS（仿 Graph 在完成帧列出去重顺序） ---
    FrameList bfs(const std::string& startLabel) override {
        FrameList frames;
        if (!root_) { frames.push_back(doneFrame("树为空")); return frames; }
        Node* start = resolveStart(startLabel);
        std::vector<Node*> q;
        std::vector<std::string> order;   // 首次访问顺序（天然去重）
        q.push_back(start);
        frames.push_back(makeFrame(StepType::Traverse,
            "BFS(层序) 从 [" + start->value + "] 入队开始", {start->id}, "#42A5F5"));
        size_t head = 0;
        while (head < q.size()) {
            Node* cur = q[head++];
            order.push_back(cur->value);
            frames.push_back(makeFrame(StepType::Traverse,
                "访问 [" + cur->value + "]", {cur->id}, "#4CAF50"));
            if (cur->left) {
                q.push_back(cur->left.get());
                frames.push_back(makeFrame(StepType::Traverse,
                    "[" + cur->value + "] 左子入队", {cur->left->id}, "#42A5F5"));
            }
            if (cur->right) {
                q.push_back(cur->right.get());
                frames.push_back(makeFrame(StepType::Traverse,
                    "[" + cur->value + "] 右子入队", {cur->right->id}, "#42A5F5"));
            }
        }
        frames.push_back(doneFrame("BFS(层序) 完成\n遍历顺序（去重）：" + joinOrder(order)));
        return frames;
    }

    FrameList dfs(const std::string& startLabel) override {
        FrameList frames;
        if (!root_) { frames.push_back(doneFrame("树为空")); return frames; }
        Node* start = resolveStart(startLabel);
        std::vector<Node*> stack;
        std::vector<std::string> order;   // 首次访问顺序（天然去重）
        std::unordered_set<const Node*> visited;
        stack.push_back(start);
        frames.push_back(makeFrame(StepType::Traverse,
            "DFS(先序) 从 [" + start->value + "] 压栈开始", {start->id}, "#AB47BC"));
        while (!stack.empty()) {
            Node* cur = stack.back(); stack.pop_back();
            if (visited.count(cur)) continue;
            visited.insert(cur);
            order.push_back(cur->value);
            frames.push_back(makeFrame(StepType::Traverse,
                "访问 [" + cur->value + "]（出栈并标记）", {cur->id}, "#4CAF50"));
            // 先压右子再压左子 → 左子先出栈 → 先序：根-左-右
            if (cur->right) {
                stack.push_back(cur->right.get());
                frames.push_back(makeFrame(StepType::Traverse,
                    "[" + cur->value + "] 右子压栈", {cur->right->id}, "#AB47BC"));
            }
            if (cur->left) {
                stack.push_back(cur->left.get());
                frames.push_back(makeFrame(StepType::Traverse,
                    "[" + cur->value + "] 左子压栈", {cur->left->id}, "#AB47BC"));
            }
        }
        frames.push_back(doneFrame("DFS(先序) 完成\n遍历顺序（去重）：" + joinOrder(order)));
        return frames;
    }

    std::vector<std::string> snapshotValues() const override {
        std::vector<std::string> v; collect(root_.get(), v); return v;
    }

private:
    std::unique_ptr<Node> root_;
    int size_ = 0;

    Node* findNode(const std::string& value, FrameList& frames) const {
        Node* cur = root_.get();
        while (cur) {
            bool match = (cur->value == value);
            frames.push_back(makeFrame(match ? StepType::Highlight : StepType::Compare,
                "比较 " + value + " 与 " + cur->value, {cur->id},
                match ? "#4CAF50" : "#FFC107"));
            if (match) return cur;
            int c = compareValues(value, cur->value);
            if (c < 0) cur = cur->left.get(); else cur = cur->right.get();
        }
        frames.push_back(doneFrame("查找失败：不存在 " + value));
        return nullptr;
    }

    // Replace 'node' (detached) in its parent / root with 'replacement'.
    void replaceInParent(Node* node, std::unique_ptr<Node> replacement) {
        if (replacement) replacement->parent = node->parent;
        if (!node->parent) { root_ = std::move(replacement); return; }
        if (node->parent->left.get() == node) node->parent->left = std::move(replacement);
        else node->parent->right = std::move(replacement);
    }

    void collect(const Node* n, std::vector<std::string>& v) const {
        if (!n) return; collect(n->left.get(), v); v.push_back(n->value); collect(n->right.get(), v);
    }

    // 解析遍历起点：按值查找子树根；为空或找不到则回退到整树根
    Node* resolveStart(const std::string& label) const {
        if (!label.empty()) {
            Node* found = findNodeRaw(label);
            if (found) return found;
        }
        return root_.get();
    }
    Node* findNodeRaw(const std::string& value) const {
        Node* cur = root_.get();
        while (cur) {
            if (cur->value == value) return cur;
            int c = compareValues(value, cur->value);
            if (c < 0) cur = cur->left.get(); else cur = cur->right.get();
        }
        return nullptr;
    }
    static std::string joinOrder(const std::vector<std::string>& order) {
        std::string s;
        for (size_t i = 0; i < order.size(); ++i) { if (i) s += " → "; s += order[i]; }
        return s;
    }

    Frame makeFrame(StepType t, const std::string& d, const std::vector<int>& hl,
                    const std::string& c, const Node* s = nullptr) const {
        Frame f; f.type = t; f.description = d; f.highlightColor = c; f.highlightIds = hl;
        collectVisual(root_.get(), f);
        if (s) f.nodes.push_back({s->id, s->value, "", -1});
        return f;
    }
    void collectVisual(const Node* n, Frame& f) const {
        if (!n) return;
        f.nodes.push_back({n->id, n->value, "", -1});
        if (n->left) { f.edges.push_back({n->id, n->left->id, "left"}); collectVisual(n->left.get(), f); }
        if (n->right) { f.edges.push_back({n->id, n->right->id, "right"}); collectVisual(n->right.get(), f); }
    }
    Frame doneFrame(const std::string& d) const { return makeFrame(StepType::Done, d, {}, "#FFC107"); }
};

} // namespace dsv
