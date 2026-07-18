#pragma once
#include "Common.h"
#include "IDataStructure.h"
#include <memory>

namespace dsv {

// ---------------------------------------------------------------------------
// Red-Black Tree  (BST insert + recolor + rotation fixup)
//
// New nodes are RED; the fixup walks up via parent pointers, recoloring and
// rotating to restore the RB invariants. The visualizer colors each node by
// its RB color (red / black) and animates the recolor + rotation steps.
// ---------------------------------------------------------------------------
class RedBlackTree : public IDataStructure {
public:
    enum Color { RED, BLACK };

    struct Node {
        std::string value; int id;
        Color color = RED;
        std::unique_ptr<Node> left, right;
        Node* parent = nullptr;                 // non-owning
        Node(const std::string& v) : value(v), id(nextId()) {}
    };

    DSKind kind() const override { return DSKind::RedBlackTree; }
    std::string name() const override { return "红黑树 RedBlackTree"; }
    std::string description() const override {
        return "近似平衡的 BST：红/黑着色 + 旋转，保证最长路径不超过最短的 2 倍。";
    }

    int size() const override { return size_; }
    bool empty() const override { return size_ == 0; }

    FrameList insert(const std::string& value) override {
        FrameList frames;
        if (!root_) {
            root_ = std::make_unique<Node>(value);
            root_->color = BLACK;
            frames.push_back(makeFrame(root_.get(), nullptr, StepType::CreateNode,
                "创建黑色根节点 " + value, {root_->id}, "#4CAF50"));
            size_ = 1;
            frames.push_back(doneFrame("插入完成，节点数 1"));
            return frames;
        }
        Node* z = bstInsert(value, frames);
        if (!z) { frames.push_back(doneFrame("已存在 " + value)); return frames; }
        size_++;
        fixInsert(z, frames);
        root_->color = BLACK;
        frames.push_back(doneFrame("插入完成，节点数 " + std::to_string(size_)));
        return frames;
    }

    FrameList insertAt(int, const std::string&) override { return FrameList{}; }
    FrameList remove(const std::string& value) override {
        FrameList frames;
        if (!root_) { frames.push_back(doneFrame("树为空")); return frames; }
        // 1) BST 查找目标节点 z
        Node* z = root_.get();
        while (z) {
            int c = compareValues(value, z->value);
            if (c == 0) break;
            z = (c < 0) ? z->left.get() : z->right.get();
        }
        if (!z) { frames.push_back(doneFrame("未找到 " + value)); return frames; }
        frames.push_back(makeFrame(root_.get(), nullptr, StepType::Highlight,
            "找到待删除节点 " + value, {z->id}, "#FF9800"));

        // 2) 双子节点：用中序后继的值替换，再删除后继（后继至多一个子节点）
        if (z->left && z->right) {
            Node* succ = z->right.get();
            while (succ->left) succ = succ->left.get();
            std::string sval = succ->value;
            frames.push_back(makeFrame(root_.get(), nullptr, StepType::Highlight,
                "后继 = " + sval, {succ->id}, "#FFC107"));
            z->value = sval;
            frames.push_back(makeFrame(root_.get(), nullptr, StepType::Swap,
                "用后继值替换目标值", {z->id}, "#BA68C8"));
            deleteOneChild(succ, frames);
        } else {
            deleteOneChild(z, frames);
        }
        if (root_) root_->color = BLACK;
        size_ = std::max(0, size_ - 1);
        frames.push_back(doneFrame("删除完成，节点数 " + std::to_string(size_)));
        return frames;
    }
    FrameList removeAt(int) override { return FrameList{}; }
    FrameList find(const std::string& value) override {
        FrameList frames;
        Node* cur = root_.get();
        while (cur) {
            bool match = (cur->value == value);
            frames.push_back(makeFrame(root_.get(), nullptr,
                match ? StepType::Highlight : StepType::Compare,
                "比较 " + value + " 与 " + cur->value, {cur->id},
                match ? "#4CAF50" : "#FFC107"));
            if (match) { frames.push_back(doneFrame("查找成功")); return frames; }
            int c = compareValues(value, cur->value);
            cur = (c < 0) ? cur->left.get() : cur->right.get();
        }
        frames.push_back(doneFrame("查找失败"));
        return frames;
    }
    FrameList clear() override {
        root_.reset(); size_ = 0;
        FrameList f; f.push_back(doneFrame("已清空")); return f;
    }
    Frame currentFrame() const override {
        return makeFrame(root_.get(), nullptr, StepType::Done, "当前红黑树状态", {}, "#FFC107");
    }
    std::vector<std::string> snapshotValues() const override {
        std::vector<std::string> v; inorder(root_.get(), v); return v;
    }

private:
    std::unique_ptr<Node> root_;
    int size_ = 0;

    // --- rotations (maintain parent pointers + root_) ---
    // ⚠️ 关键：std::move(unique_ptr) 后原对象即失效（内部指针变 null），
    //    后续不可再通过它访问成员。必须在 move 前保存裸指针供后续使用。
    std::unique_ptr<Node> rotateLeft(std::unique_ptr<Node> x) {
        if (!x->right) return x;  // 无右孩子则无法左旋，原样返回（防御性保护）
        std::unique_ptr<Node> y = std::move(x->right);
        std::unique_ptr<Node> T2 = std::move(y->left);
        Node* x_raw = x.get();   // ★ 在 x 被 move 前保存裸指针
        Node* y_raw = y.get();   // ★ 在 y 被 move 前保存裸指针
        y->left = std::move(x);      // x 的所有权被移走，x 现在为空
        x_raw->right = std::move(T2); // 用 x_raw 代替已空的 x
        y_raw->parent = x_raw->parent;
        x_raw->parent = y_raw;
        if (x_raw->right) x_raw->right->parent = x_raw;
        return y;
    }
    std::unique_ptr<Node> rotateRight(std::unique_ptr<Node> y) {
        if (!y->left) return y;  // 无左孩子则无法右旋，原样返回（防御性保护）
        std::unique_ptr<Node> x = std::move(y->left);
        std::unique_ptr<Node> T2 = std::move(x->right);
        Node* y_raw = y.get();   // ★ 在 y 被 move 前保存裸指针
        Node* x_raw = x.get();   // ★ 在 x 被 move 前保存裸指针
        x->right = std::move(y);     // y 的所有权被移走，y 现在为空
        y_raw->left = std::move(T2);  // 用 y_raw 代替已空的 y
        x_raw->parent = y_raw->parent;
        y_raw->parent = x_raw;
        if (y_raw->left) y_raw->left->parent = y_raw;
        return x;
    }

    // Rotate the subtree rooted at raw node `x` in place; returns new subtree root.
    Node* rotateLeftAt(Node* x) {
        Node* p = x->parent;
        bool isLeft = p ? (p->left.get() == x) : false;
        std::unique_ptr<Node> sub = p ? (isLeft ? std::move(p->left) : std::move(p->right))
                                      : std::move(root_);
        sub = rotateLeft(std::move(sub));
        if (p) { if (isLeft) p->left = std::move(sub); else p->right = std::move(sub); }
        else root_ = std::move(sub);
        return p ? (isLeft ? p->left.get() : p->right.get()) : root_.get();
    }
    Node* rotateRightAt(Node* y) {
        Node* p = y->parent;
        bool isLeft = p ? (p->left.get() == y) : false;
        std::unique_ptr<Node> sub = p ? (isLeft ? std::move(p->left) : std::move(p->right))
                                      : std::move(root_);
        sub = rotateRight(std::move(sub));
        if (p) { if (isLeft) p->left = std::move(sub); else p->right = std::move(sub); }
        else root_ = std::move(sub);
        return p ? (isLeft ? p->left.get() : p->right.get()) : root_.get();
    }

    // ---- 红黑树删除（CLRS 标准：transplant + 双黑 fixup）----
    // 注意：所有 unique_ptr 移交都用 transplant/裸指针，绝不在 move 后解引用。
    static Color colorOf(Node* n) { return n ? n->color : BLACK; }

    // 把 u 在树中的位置（root_ 或父节点的 left/right）替换为子树 v
    void transplant(Node* u, std::unique_ptr<Node> v) {
        if (!u->parent) root_ = std::move(v);
        else if (u->parent->left.get() == u) u->parent->left = std::move(v);
        else u->parent->right = std::move(v);
        if (v) v->parent = u->parent;
    }

    // 删除“至多一个子节点”的 target，并在 target 为黑时启动双黑修复
    void deleteOneChild(Node* target, FrameList& frames) {
        Color orig = target->color;
        Node* x = nullptr;       // 取代 target 的节点（裸指针，可为 null = NIL）
        Node* xp = nullptr;      // x 的父节点
        bool xIsLeft = false;
        frames.push_back(makeFrame(root_.get(), nullptr, StepType::BreakLink,
            "删除 " + target->value, {target->id}, "#FF9800"));
        if (!target->left) {
            x = target->right.get();
            xp = target->parent;
            xIsLeft = (xp && xp->left.get() == target);
            transplant(target, std::move(target->right));
        } else {
            x = target->left.get();
            xp = target->parent;
            xIsLeft = (xp && xp->left.get() == target);
            transplant(target, std::move(target->left));
        }
        if (orig == BLACK) fixDelete(x, xp, xIsLeft, frames);
    }

    // 双黑修复（迭代式，沿父指针上溯）。x 可为 null（NIL）；xp 为 x 的父。
    void fixDelete(Node* x, Node* xp, bool xIsLeft, FrameList& frames) {
        if (!root_) return;
        while (x != root_.get() && colorOf(x) == BLACK) {
            if (!xp) break;                 // 安全护栏：x 已到根
            if (xIsLeft) {
                Node* w = xp->right.get();  // 兄弟
                if (colorOf(w) == RED) {
                    w->color = BLACK; xp->color = RED;
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rebalance,
                        "删除修复：兄红→重着色并左旋父", {xp->id, w->id}, "#BA68C8"));
                    rotateLeftAt(xp);
                    w = xp->right.get();
                }
                if (colorOf(w ? w->left.get() : nullptr) == BLACK && colorOf(w ? w->right.get() : nullptr) == BLACK) {
                    if (w) w->color = RED;
                    x = xp;
                    if (x == root_.get()) break;
                    xp = x->parent;
                    xIsLeft = (xp && xp->left.get() == x);
                } else {
                    if (colorOf(w ? w->right.get() : nullptr) == BLACK) {
                        if (w && w->left) w->left->color = BLACK;
                        if (w) w->color = RED;
                        frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                            "删除修复：先右旋兄", {w->id}, "#BA68C8"));
                        rotateRightAt(w);
                        w = xp->right.get();
                    }
                    if (w) w->color = xp ? xp->color : BLACK;
                    if (xp) xp->color = BLACK;
                    if (w && w->right) w->right->color = BLACK;
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                        "删除修复：右旋父", {xp->id}, "#BA68C8"));
                    rotateLeftAt(xp);
                    x = root_.get();
                }
            } else {
                Node* w = xp->left.get();
                if (colorOf(w) == RED) {
                    w->color = BLACK; xp->color = RED;
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rebalance,
                        "删除修复：兄红→重着色并右旋父", {xp->id, w->id}, "#BA68C8"));
                    rotateRightAt(xp);
                    w = xp->left.get();
                }
                if (colorOf(w ? w->left.get() : nullptr) == BLACK && colorOf(w ? w->right.get() : nullptr) == BLACK) {
                    if (w) w->color = RED;
                    x = xp;
                    if (x == root_.get()) break;
                    xp = x->parent;
                    xIsLeft = (xp && xp->left.get() == x);
                } else {
                    if (colorOf(w ? w->left.get() : nullptr) == BLACK) {
                        if (w && w->right) w->right->color = BLACK;
                        if (w) w->color = RED;
                        frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                            "删除修复：先左旋兄", {w->id}, "#BA68C8"));
                        rotateLeftAt(w);
                        w = xp->left.get();
                    }
                    if (w) w->color = xp ? xp->color : BLACK;
                    if (xp) xp->color = BLACK;
                    if (w && w->left) w->left->color = BLACK;
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                        "删除修复：左旋父", {xp->id}, "#BA68C8"));
                    rotateRightAt(xp);
                    x = root_.get();
                }
            }
        }
        if (x) x->color = BLACK;
    }

    Node* bstInsert(const std::string& value, FrameList& frames) {
        Node* parent = nullptr;
        Node* cur = root_.get();
        while (cur) {
            frames.push_back(makeFrame(root_.get(), nullptr, StepType::Compare,
                "比较 " + value + " 与 " + cur->value, {cur->id}, "#FFC107"));
            int c = compareValues(value, cur->value);
            if (c == 0) return nullptr;
            parent = cur;
            cur = (c < 0) ? cur->left.get() : cur->right.get();
        }
        auto n = std::make_unique<Node>(value);
        n->color = RED;
        Node* raw = n.get();
        n->parent = parent;
        if (compareValues(value, parent->value) < 0) parent->left = std::move(n);
        else parent->right = std::move(n);
        frames.push_back(makeFrame(root_.get(), nullptr, StepType::CreateNode,
            "创建红色节点 " + value, {raw->id}, "#4CAF50"));
        frames.push_back(makeFrame(root_.get(), nullptr, StepType::Link,
            "挂接到 " + parent->value, {parent->id, raw->id}, "#4CAF50"));
        return raw;
    }

    void fixInsert(Node* z, FrameList& frames) {
        while (z->parent && z->parent->color == RED) {
            Node* gp = z->parent->parent;
            if (!gp) break;   // 防御：父是红色根节点时 gp 为 null，直接退出（根会在循环后被染黑）
            if (z->parent == gp->left.get()) {
                Node* uncle = gp->right.get();
                if (uncle && uncle->color == RED) {
                    z->parent->color = BLACK;
                    uncle->color = BLACK;
                    gp->color = RED;
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rebalance,
                        "情况1: 叔叔为红 → 父/叔变黑，祖父变红",
                        {z->parent->id, uncle->id, gp->id}, "#BA68C8"));
                    z = gp;
                } else {
                    if (z == z->parent->right.get()) {
                        z = z->parent;
                        rotateLeftAt(z);
                        frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                            "情况2/3: 左旋 " + z->value, {z->id}, "#BA68C8"));
                    }
                    z->parent->color = BLACK;
                    gp->color = RED;
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rebalance,
                        "情况2/3: 重新着色（父黑祖红）", {z->parent->id, gp->id}, "#BA68C8"));
                    rotateRightAt(gp);
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                        "右旋 " + gp->value, {gp->id}, "#BA68C8"));
                }
            } else {
                Node* uncle = gp->left.get();
                if (uncle && uncle->color == RED) {
                    z->parent->color = BLACK;
                    uncle->color = BLACK;
                    gp->color = RED;
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rebalance,
                        "情况1: 叔叔为红 → 父/叔变黑，祖父变红",
                        {z->parent->id, uncle->id, gp->id}, "#BA68C8"));
                    z = gp;
                } else {
                    if (z == z->parent->left.get()) {
                        z = z->parent;
                        rotateRightAt(z);
                        frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                            "情况2/3: 右旋 " + z->value, {z->id}, "#BA68C8"));
                    }
                    z->parent->color = BLACK;
                    gp->color = RED;
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rebalance,
                        "情况2/3: 重新着色（父黑祖红）", {z->parent->id, gp->id}, "#BA68C8"));
                    rotateLeftAt(gp);
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                        "左旋 " + gp->value, {gp->id}, "#BA68C8"));
                }
            }
        }
        root_->color = BLACK;
    }

    void inorder(const Node* n, std::vector<std::string>& v) const {
        if (!n) return;
        inorder(n->left.get(), v); v.push_back(n->value); inorder(n->right.get(), v);
    }

    static std::string colorHex(Color c) { return (c == RED) ? "#E53935" : "#263238"; }
    static std::string colorTag(Color c) { return (c == RED) ? "红" : "黑"; }

    Frame makeFrame(const Node* rootForFrame, const Node* staging, StepType t,
                    const std::string& d, const std::vector<int>& hl,
                    const std::string& c) const {
        Frame f; f.type = t; f.description = d; f.highlightColor = c; f.highlightIds = hl;
        if (rootForFrame) collectVisual(rootForFrame, f);
        if (staging) f.nodes.push_back({staging->id, staging->value,
            colorTag(staging->color), -1, colorHex(staging->color)});
        return f;
    }
    void collectVisual(const Node* n, Frame& f) const {
        if (!n) return;
        f.nodes.push_back({n->id, n->value, colorTag(n->color), -1, colorHex(n->color)});
        if (n->left) { f.edges.push_back({n->id, n->left->id, "left"}); collectVisual(n->left.get(), f); }
        if (n->right) { f.edges.push_back({n->id, n->right->id, "right"}); collectVisual(n->right.get(), f); }
    }
    Frame doneFrame(const std::string& d) const {
        return makeFrame(root_.get(), nullptr, StepType::Done, d, {}, "#FFC107");
    }
};

} // namespace dsv
