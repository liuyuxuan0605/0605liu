#pragma once
#include "Common.h"
#include "IDataStructure.h"
#include <memory>

namespace dsv {

// ---------------------------------------------------------------------------
// Stack  (LIFO, top = head of internal list)
// ---------------------------------------------------------------------------
class Stack : public IDataStructure {
public:
    struct Node {
        std::string value; int id;
        std::unique_ptr<Node> next;
        Node(const std::string& v) : value(v), id(nextId()) {}
    };

    DSKind kind() const override { return DSKind::Stack; }
    std::string name() const override { return "栈 Stack"; }
    std::string description() const override {
        return "后进先出，仅能在栈顶压入(push)与弹出(pop)。";
    }

    int size() const override { return size_; }
    bool empty() const override { return size_ == 0; }

    FrameList insert(const std::string& value) override { return push(value); }
    FrameList insertAt(int, const std::string&) override { return FrameList{}; }

    FrameList push(const std::string& value) {
        FrameList frames;
        auto n = std::make_unique<Node>(value);
        frames.push_back(makeFrame(StepType::CreateNode, "创建栈顶节点 " + value,
            {n->id}, "#4CAF50", n.get()));
        n->next = std::move(head_);
        head_ = std::move(n);
        frames.push_back(makeFrame(StepType::Link, "新节点压入栈顶",
            {head_->id}, "#4CAF50"));
        size_++;
        frames.push_back(doneFrame("push 完成，栈深度 " + std::to_string(size_)));
        return frames;
    }

    FrameList pop() {
        FrameList frames;
        if (!head_) { frames.push_back(doneFrame("栈为空，无法 pop")); return frames; }
        frames.push_back(makeFrame(StepType::Highlight, "栈顶元素出栈 (值 " + head_->value + ")",
            {head_->id}, "#FF9800"));
        head_ = std::move(head_->next);
        frames.push_back(makeFrame(StepType::BreakLink, "栈顶指针下移",
            head_ ? std::vector<int>{head_->id} : std::vector<int>{}, "#FF9800"));
        size_ = std::max(0, size_ - 1);
        frames.push_back(doneFrame("pop 完成，栈深度 " + std::to_string(size_)));
        return frames;
    }

    FrameList remove(const std::string&) override { return pop(); }
    FrameList removeAt(int) override { return pop(); }

    FrameList find(const std::string& value) override {
        FrameList frames;
        Node* cur = head_.get(); int idx = 0;
        while (cur) {
            bool match = (cur->value == value);
            frames.push_back(makeFrame(match ? StepType::Highlight : StepType::Compare,
                "从栈顶向下比较 (深度 " + std::to_string(idx) + ", 值 " + cur->value + ")",
                {cur->id}, match ? "#4CAF50" : "#FFC107"));
            if (match) { frames.push_back(doneFrame("查找成功，深度 " + std::to_string(idx))); return frames; }
            cur = cur->next.get(); idx++;
        }
        frames.push_back(doneFrame("未找到 " + value));
        return frames;
    }

    FrameList clear() override { head_.reset(); size_ = 0; FrameList f; f.push_back(doneFrame("已清空栈")); return f; }

    Frame currentFrame() const override { return makeFrame(StepType::Done, "当前栈状态", {}, "#FFC107"); }

    std::vector<std::string> snapshotValues() const override {
        std::vector<std::string> v; Node* c = head_.get();
        while (c) { v.push_back(c->value); c = c->next.get(); }
        return v;
    }

private:
    std::unique_ptr<Node> head_;
    int size_ = 0;
    Frame makeFrame(StepType t, const std::string& d, const std::vector<int>& hl,
                    const std::string& c, const Node* s = nullptr) const {
        Frame f; f.type = t; f.description = d; f.highlightColor = c; f.highlightIds = hl;
        const Node* cur = head_.get();
        while (cur) {
            f.nodes.push_back({cur->id, cur->value, "", -1});
            if (cur->next) f.edges.push_back({cur->id, cur->next->id, "next"});
            cur = cur->next.get();
        }
        if (s) f.nodes.push_back({s->id, s->value, "", -1});
        return f;
    }
    Frame doneFrame(const std::string& d) const { return makeFrame(StepType::Done, d, {}, "#FFC107"); }
};

} // namespace dsv
