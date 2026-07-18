#pragma once
#include "Common.h"
#include "IDataStructure.h"
#include <memory>
#include <algorithm>

namespace dsv {

// ---------------------------------------------------------------------------
// AVL Tree  (self-balancing BST, parent-pointer + in-place rotation)
//
// 第10轮重写：从"递归传递 unique_ptr"架构迁移到"parent 裸指针 + 原地旋转"
// 架构，与已验证安全的 RedBlackTree 完全同构。
//
// 核心改变：
//   - Node 新增 parent 指针（非拥有，仅导航用）
//   - 旋转通过 rotateLeftAt/rotateRightAt 在原地完成（不传 unique_ptr 进旋转）
//   - insert = bstInsert + balanceInsert（沿 parent 上溯平衡）
//   - remove = transplant + deleteOneChild + balanceDelete
//   - 彻底消除"unique_ptr 参数 move 后解引用"整类风险
// ---------------------------------------------------------------------------

class AVLTree : public IDataStructure {
public:
    struct Node {
        std::string value; int id; int height = 1;
        std::unique_ptr<Node> left, right;
        Node* parent = nullptr;          // 非拥有父指针（第10轮新增）
        Node(const std::string& v) : value(v), id(nextId()) {}
    };

    DSKind kind() const override { return DSKind::AVLTree; }
    std::string name() const override { return "AVL 平衡树"; }
    std::string description() const override {
        return "带平衡因子的自平衡 BST，插入/删除后通过旋转保持 O(log n) 高度。";
    }

    int size() const override { return size_; }
    bool empty() const override { return size_ == 0; }

    // ===================== 插入 =====================
    FrameList insert(const std::string& value) override {
        FrameList frames;
        if (!root_) {
            root_ = std::make_unique<Node>(value);
            frames.push_back(makeFrame(root_.get(), nullptr, StepType::CreateNode,
                "创建根节点 " + value, {root_->id}, "#4CAF50"));
            size_ = 1;
            frames.push_back(doneFrame("插入完成，节点数 1"));
            return frames;
        }

        // Step 1: BST 插入（与 RB 的 bstInsert 同构）
        Node* z = bstInsert(value, frames);
        if (!z) {
            frames.push_back(doneFrame("已存在 " + value));
            return frames;
        }
        size_++;

        // Step 2: 从 z 向上平衡（沿 parent 链上溯）
        balanceInsert(z, frames);

        frames.push_back(doneFrame("插入完成，节点数 " + std::to_string(size_)));
        return frames;
    }

    FrameList insertAt(int, const std::string&) override { return FrameList{}; }

    // ===================== 删除 =====================
    FrameList remove(const std::string& value) override {
        FrameList frames;
        if (!root_) { frames.push_back(doneFrame("树为空")); return frames; }

        // Step 1: BST 查找目标节点
        Node* z = root_.get();
        while (z) {
            int c = compareValues(value, z->value);
            if (c == 0) break;
            z = (c < 0) ? z->left.get() : z->right.get();
        }
        if (!z) { frames.push_back(doneFrame("未找到 " + value)); return frames; }

        frames.push_back(makeFrame(root_.get(), nullptr, StepType::Highlight,
            "找到待删除节点 " + value, {z->id}, "#FF9800"));

        // Step 2: 双子节点 → 用后继值替换，再删后继
        if (z->left && z->right) {
            Node* succ = z->right.get();
            while (succ->left) succ = succ->left.get();
            std::string sval = succ->value;
            frames.push_back(makeFrame(root_.get(), nullptr, StepType::Highlight,
                "后继 = " + sval, {succ->id}, "#FFC107"));
            z->value = sval;
            frames.push_back(makeFrame(root_.get(), nullptr, StepType::Swap,
                "用后继值替换目标值", {z->id}, "#BA68C8"));
            deleteOneChild(succ, frames);   // 后继至多一个子节点
        } else {
            deleteOneChild(z, frames);      // 至多一个子节点，直接删
        }

        size_ = std::max(0, size_ - 1);
        frames.push_back(doneFrame("删除完成，节点数 " + std::to_string(size_)));
        return frames;
    }

    FrameList removeAt(int) override { return FrameList{}; }

    // ===================== 查找 =====================
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
        return makeFrame(root_.get(), nullptr, StepType::Done, "当前 AVL 状态", {}, "#FFC107");
    }

    std::vector<std::string> snapshotValues() const override {
        std::vector<std::string> v; inorder(root_.get(), v); return v;
    }

private:
    std::unique_ptr<Node> root_;
    int size_ = 0;

    // ========== 高度 / 平衡因子辅助 ==========

    static int height(Node* n) { return n ? n->height : 0; }

    static void upd(Node* n) {
        if (n)
            n->height = 1 + std::max(height(n->left.get()), height(n->right.get()));
    }

    static int getBalance(Node* n) {
        return n ? height(n->left.get()) - height(n->right.get()) : 0;
    }

    // ========== 底层旋转函数（unique_ptr 参数，只被 rotateLeftAt/rotateRightAt 调用）==========
    //
    // ⚠️ 这些函数内部仍需遵守 unique_ptr move 纪律：move 前保存裸指针。
    // 但它们不再被 insertRec/removeRec 直接调用——所有调用都经过
    // rotateLeftAt/rotateRightAt 包装。move 只发生在函数内部的局部变量间。

    std::unique_ptr<Node> rotateLeft(std::unique_ptr<Node> x) {
        if (!x || !x->right) return x;
        std::unique_ptr<Node> y = std::move(x->right);
        std::unique_ptr<Node> T2 = std::move(y->left);
        Node* x_raw = x.get();
        Node* y_raw = y.get();
        y->left     = std::move(x);       // x 所有权移给 y.left → x 空
        x_raw->right = std::move(T2);     // 用裸指针
        // 维护 parent 指针（与 RB 的 rotateLeft 一致）
        y_raw->parent = x_raw->parent;
        x_raw->parent = y_raw;
        if (x_raw->right) x_raw->right->parent = x_raw;
        upd(x_raw); upd(y_raw);
        return y;
    }

    std::unique_ptr<Node> rotateRight(std::unique_ptr<Node> y) {
        if (!y || !y->left) return y;
        std::unique_ptr<Node> x = std::move(y->left);
        std::unique_ptr<Node> T2 = std::move(x->right);
        Node* y_raw = y.get();
        Node* x_raw = x.get();
        x->right    = std::move(y);       // y 所有权移给 x.right → y 空
        y_raw->left = std::move(T2);      // 用裸指针
        // 维护 parent 指针（与 RB 的 rotateRight 一致）
        x_raw->parent = y_raw->parent;
        y_raw->parent = x_raw;
        if (y_raw->left) y_raw->left->parent = y_raw;
        upd(y_raw); upd(x_raw);
        return x;
    }

    // ========== 原地旋转包装（与 RB 的 rotateLeftAt/rotateRightAt 完全同构）==========
    //
    // 通过 parent 指针找到 owning 引用位置，取出所有权→旋转→放回。
    // unique_ptr 只在 rotateLeft/rotateRight 内部流动，不跨越函数边界。

    Node* rotateLeftAt(Node* x) {
        Node* p = x->parent;
        bool isLeft = p ? (p->left.get() == x) : false;
        // 取出 owning 引用
        std::unique_ptr<Node> sub = p
            ? (isLeft ? std::move(p->left) : std::move(p->right))
            : std::move(root_);
        // 旋转（sub 流入 rotateLeft，流出新根）
        sub = rotateLeft(std::move(sub));
        // 放回原位
        if (p) {
            if (isLeft) p->left = std::move(sub);
            else         p->right = std::move(sub);
        } else {
            root_ = std::move(sub);
        }
        // 返回新子树根的裸指针
        return p ? (isLeft ? p->left.get() : p->right.get()) : root_.get();
    }

    Node* rotateRightAt(Node* y) {
        Node* p = y->parent;
        bool isLeft = p ? (p->left.get() == y) : false;
        std::unique_ptr<Node> sub = p
            ? (isLeft ? std::move(p->left) : std::move(p->right))
            : std::move(root_);
        sub = rotateRight(std::move(sub));
        if (p) {
            if (isLeft) p->left = std::move(sub);
            else         p->right = std::move(sub);
        } else {
            root_ = std::move(sub);
        }
        return p ? (isLeft ? p->left.get() : p->right.get()) : root_.get();
    }

    // ========== BST 插入（与 RB 的 bstInsert 同构）==========

    Node* bstInsert(const std::string& value, FrameList& frames) {
        Node* parent = nullptr;
        Node* cur = root_.get();
        while (cur) {
            frames.push_back(makeFrame(root_.get(), nullptr, StepType::Compare,
                "比较 " + value + " 与 " + cur->value, {cur->id}, "#FFC107"));
            int c = compareValues(value, cur->value);
            if (c == 0) return nullptr;          // 已存在
            parent = cur;
            cur = (c < 0) ? cur->left.get() : cur->right.get();
        }
        auto n = std::make_unique<Node>(value);
        Node* raw = n.get();
        n->parent = parent;
        if (compareValues(value, parent->value) < 0)
            parent->left  = std::move(n);
        else
            parent->right = std::move(n);
        frames.push_back(makeFrame(root_.get(), nullptr, StepType::CreateNode,
            "创建节点 " + value, {raw->id}, "#4CAF50"));
        frames.push_back(makeFrame(root_.get(), nullptr, StepType::Link,
            "挂接到 " + parent->value, {parent->id, raw->id}, "#4CAF50"));
        return raw;
    }

    // ========== 插入后平衡（从新节点沿 parent 上溯）==========

    void balanceInsert(Node* z, FrameList& frames) {
        Node* cur = z->parent;
        while (cur) {
            int oldH = cur->height;
            upd(cur);
            int b = getBalance(cur);

            if (b > 1) {
                if (getBalance(cur->left.get()) >= 0) {
                    // LL → 单次右旋
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                        "LL 型：右旋 " + cur->value, {cur->id}, "#BA68C8"));
                    rotateRightAt(cur);
                } else {
                    // LR → 先左旋左孩子，再右旋 cur
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                        "LR 型：先左旋后右旋 " + cur->value, {cur->id}, "#BA68C8"));
                    rotateLeftAt(cur->left.get());
                    rotateRightAt(cur);
                }
                break;   // AVL 特性：一次旋转足以恢复平衡
            }

            if (b < -1) {
                if (getBalance(cur->right.get()) <= 0) {
                    // RR → 单次左旋
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                        "RR 型：左旋 " + cur->value, {cur->id}, "#BA68C8"));
                    rotateLeftAt(cur);
                } else {
                    // RL → 先右旋右孩子，再左旋 cur
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                        "RL 型：先右旋后左旋 " + cur->value, {cur->id}, "#BA68C8"));
                    rotateRightAt(cur->right.get());
                    rotateLeftAt(cur);
                }
                break;   // AVL 特性：一次旋转足以恢复平衡
            }

            if (cur->height == oldH) break;   // 高度未变，上层不受影响
            cur = cur->parent;
        }
    }

    // ========== 删除辅助（transplant + 单子删除 + 删除后平衡）==========

    // 把 target 在树中的位置替换为 child 子树
    void transplant(Node* target, std::unique_ptr<Node> child) {
        Node* p = target->parent;
        if (!p) {
            root_ = std::move(child);
            if (root_) root_->parent = nullptr;     // 新根的 parent 必须为空
        } else if (p->left.get() == target) {
            p->left = std::move(child);
            if (p->left) p->left->parent = p;       // 更新新子的 parent
        } else {
            p->right = std::move(child);
            if (p->right) p->right->parent = p;     // 更新新子的 parent
        }
    }

    // 删除"至多一个子节点"的目标节点，并启动平衡修复
    void deleteOneChild(Node* target, FrameList& frames) {
        Node* p = target->parent;   // 记录父节点，用于后续平衡

        frames.push_back(makeFrame(root_.get(), nullptr, StepType::BreakLink,
            "删除 " + target->value, {target->id}, "#FF9800"));

        // 用唯一的孩子（或 null）替换 target
        if (!target->left && !target->right) {
            transplant(target, nullptr);              // 叶子 → 直接移除
        } else if (target->left) {
            transplant(target, std::move(target->left));  // 只有左孩子
        } else {
            transplant(target, std::move(target->right)); // 只有右孩子
        }
        // ★ 此时 target 对象已被销毁（unique_ptr 移出后离开作用域）

        // 从 parent 开始向上平衡（删除可能级联影响多层）
        balanceDelete(p, frames);
    }

    // 从 node 向上平衡（可能需要 O(log n) 次旋转）
    void balanceDelete(Node* node, FrameList& frames) {
        while (node) {
            upd(node);
            int b = getBalance(node);

            if (b > 1) {
                if (getBalance(node->left.get()) >= 0) {
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                        "LL 型：右旋 " + node->value, {node->id}, "#BA68C8"));
                    node = rotateRightAt(node);
                } else {
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                        "LR 型：先左旋后右旋 " + node->value, {node->id}, "#BA68C8"));
                    rotateLeftAt(node->left.get());
                    node = rotateRightAt(node);
                }
                continue;   // 删除后可能需要继续平衡
            }

            if (b < -1) {
                if (getBalance(node->right.get()) <= 0) {
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                        "RR 型：左旋 " + node->value, {node->id}, "#BA68C8"));
                    node = rotateLeftAt(node);
                } else {
                    frames.push_back(makeFrame(root_.get(), nullptr, StepType::Rotate,
                        "RL 型：先右旋后左旋 " + node->value, {node->id}, "#BA68C8"));
                    rotateRightAt(node->right.get());
                    node = rotateLeftAt(node);
                }
                continue;
            }

            node = node->parent;
        }
    }

    // ========== 遍历 & 帧采集 ==========

    void inorder(const Node* n, std::vector<std::string>& v) const {
        if (!n) return;
        inorder(n->left.get(), v); v.push_back(n->value); inorder(n->right.get(), v);
    }

    Frame makeFrame(const Node* rootForFrame, const Node* staging, StepType t,
                    const std::string& d, const std::vector<int>& hl,
                    const std::string& c) const {
        Frame f; f.type = t; f.description = d;
        f.highlightColor = c; f.highlightIds = hl;
        if (rootForFrame) collectVisual(rootForFrame, f);
        if (staging)
            f.nodes.push_back({staging->id, staging->value,
                               std::to_string(staging->height), -1});
        return f;
    }

    void collectVisual(const Node* n, Frame& f) const {
        if (!n) return;
        f.nodes.push_back({n->id, n->value, std::to_string(n->height), -1});
        if (n->left) {
            f.edges.push_back({n->id, n->left->id, "left"});
            collectVisual(n->left.get(), f);
        }
        if (n->right) {
            f.edges.push_back({n->id, n->right->id, "right"});
            collectVisual(n->right.get(), f);
        }
    }

    Frame doneFrame(const std::string& d) const {
        return makeFrame(root_.get(), nullptr, StepType::Done, d, {}, "#FFC107");
    }
};

} // namespace dsv
