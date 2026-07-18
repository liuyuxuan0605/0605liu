#pragma once
#include "Common.h"
#include "IDataStructure.h"
#include <memory>
#include <algorithm>

namespace dsv {

// ---------------------------------------------------------------------------
// Deque  (double-ended queue: push/pop at both front and back)
// Modeled on Queue but with a doubly-linked chain so both ends are O(1).
// Frames emit only "next" edges (head -> ... -> tail, left to right),
// matching the horizontal layout shared with Queue.
// ---------------------------------------------------------------------------
class Deque : public IDataStructure {
public:
    struct Node {
        std::string value; int id;
        std::unique_ptr<Node> next;
        Node* prev = nullptr;
        Node(const std::string& v) : value(v), id(nextId()) {}
    };

    DSKind kind() const override { return DSKind::Deque; }
    std::string name() const override { return "双端队列 Deque"; }
    std::string description() const override {
        return "可在队首/队尾两端插入与删除：pushFront / pushBack / popFront / popBack。";
    }

    int size() const override { return size_; }
    bool empty() const override { return size_ == 0; }

    // generic UI channel maps onto back / front
    FrameList insert(const std::string& value) override { return pushBack(value); }
    FrameList insertAt(int, const std::string&) override { return FrameList{}; }
    FrameList remove(const std::string&) override { return popFront(); }
    FrameList removeAt(int) override { return popFront(); }

    FrameList pushFront(const std::string& value) override {
        FrameList frames;
        auto n = std::make_unique<Node>(value);
        frames.push_back(makeFrame(StepType::CreateNode, "创建新节点 " + value + "，插入队首",
            {n->id}, "#4CAF50", n.get()));
        if (!head_) {
            head_ = std::move(n);
            tail_ = head_.get();
        } else {
            n->next = std::move(head_);    // 旧首节点挂到新节点之后
            n->next->prev = n.get();       // 旧首的 prev 指向新节点（n 仍有效）
            head_ = std::move(n);          // 新节点成为 head（持有所有权）
        }
        size_++;
        frames.push_back(makeFrame(StepType::Link, "新节点成为队首",
            {head_->id}, "#4CAF50"));
        frames.push_back(doneFrame("pushFront 完成，长度 " + std::to_string(size_)));
        return frames;
    }

    FrameList pushBack(const std::string& value) override {
        FrameList frames;
        auto n = std::make_unique<Node>(value);
        frames.push_back(makeFrame(StepType::CreateNode, "创建新节点 " + value + "，插入队尾",
            {n->id}, "#4CAF50", n.get()));
        if (!head_) {
            head_ = std::move(n);
            tail_ = head_.get();
        } else {
            tail_->next = std::move(n);    // 新节点挂到尾后
            tail_->next->prev = tail_;     // 新节点的 prev 指向旧尾
            tail_ = tail_->next.get();     // 更新尾指针
        }
        size_++;
        frames.push_back(makeFrame(StepType::Link, "新节点成为队尾",
            {tail_->id}, "#4CAF50"));
        frames.push_back(doneFrame("pushBack 完成，长度 " + std::to_string(size_)));
        return frames;
    }

    FrameList popFront() override {
        FrameList frames;
        if (!head_) { frames.push_back(doneFrame("双端队列为空，无法 popFront")); return frames; }
        frames.push_back(makeFrame(StepType::Highlight, "队首出队 (值 " + head_->value + ")",
            {head_->id}, "#FF9800"));
        head_ = std::move(head_->next);
        if (head_) head_->prev = nullptr; else tail_ = nullptr;
        size_ = std::max(0, size_ - 1);
        frames.push_back(makeFrame(StepType::BreakLink, "队首指针后移",
            head_ ? std::vector<int>{head_->id} : std::vector<int>{}, "#FF9800"));
        frames.push_back(doneFrame("popFront 完成，长度 " + std::to_string(size_)));
        return frames;
    }

    FrameList popBack() override {
        FrameList frames;
        if (!tail_) { frames.push_back(doneFrame("双端队列为空，无法 popBack")); return frames; }
        frames.push_back(makeFrame(StepType::Highlight, "队尾出队 (值 " + tail_->value + ")",
            {tail_->id}, "#FF9800"));
        if (tail_->prev) {
            Node* newTail = tail_->prev;
            tail_ = newTail;
            newTail->next.reset();         // 释放旧尾节点（所有权在 newTail->next）
        } else {
            head_.reset();
            tail_ = nullptr;
        }
        size_ = std::max(0, size_ - 1);
        frames.push_back(makeFrame(StepType::BreakLink, "队尾指针前移",
            tail_ ? std::vector<int>{tail_->id} : std::vector<int>{}, "#FF9800"));
        frames.push_back(doneFrame("popBack 完成，长度 " + std::to_string(size_)));
        return frames;
    }

    FrameList find(const std::string& value) override {
        FrameList frames;
        Node* cur = head_.get(); int idx = 0;
        while (cur) {
            bool match = (cur->value == value);
            frames.push_back(makeFrame(match ? StepType::Highlight : StepType::Compare,
                "从队首比较 (位置 " + std::to_string(idx) + ", 值 " + cur->value + ")",
                {cur->id}, match ? "#4CAF50" : "#FFC107"));
            if (match) { frames.push_back(doneFrame("查找成功")); return frames; }
            cur = cur->next.get(); idx++;
        }
        frames.push_back(doneFrame("未找到 " + value));
        return frames;
    }

    FrameList clear() override { head_.reset(); tail_ = nullptr; size_ = 0;
        FrameList f; f.push_back(doneFrame("已清空双端队列")); return f; }

    Frame currentFrame() const override { return makeFrame(StepType::Done, "当前双端队列状态", {}, "#FFC107"); }

    std::vector<std::string> snapshotValues() const override {
        std::vector<std::string> v; Node* c = head_.get();
        while (c) { v.push_back(c->value); c = c->next.get(); }
        return v;
    }

private:
    std::unique_ptr<Node> head_;
    Node* tail_ = nullptr;
    int size_ = 0;

    Frame makeFrame(StepType t, const std::string& d, const std::vector<int>& hl,
                    const std::string& c, const Node* s = nullptr) const {
        Frame f; f.type = t; f.description = d; f.highlightColor = c; f.highlightIds = hl;
        const Node* cur = head_.get();
        while (cur) {
            std::string sub;
            if (cur == head_.get() && cur == tail_) sub = "首/尾";
            else if (cur == head_.get())           sub = "首";
            else if (cur == tail_)                 sub = "尾";
            f.nodes.push_back({cur->id, cur->value, sub, -1});
            if (cur->next) f.edges.push_back({cur->id, cur->next->id, "next"});
            cur = cur->next.get();
        }
        if (s && s != cur) {  // 暂存（孤立）节点也画出
            bool already = false;
            for (const auto& n : f.nodes) if (n.id == s->id) { already = true; break; }
            if (!already) f.nodes.push_back({s->id, s->value, "", -1});
        }
        return f;
    }
    Frame doneFrame(const std::string& d) const { return makeFrame(StepType::Done, d, {}, "#FFC107"); }
};

} // namespace dsv
