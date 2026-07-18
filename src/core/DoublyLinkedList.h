#pragma once
#include "Common.h"
#include "IDataStructure.h"
#include <memory>

namespace dsv {

// ---------------------------------------------------------------------------
// Doubly Linked List  (both directions linked)
// ---------------------------------------------------------------------------
class DoublyLinkedList : public IDataStructure {
public:
    struct Node {
        std::string value;
        int id;
        std::unique_ptr<Node> next;
        Node* prev = nullptr;           // non-owning
        Node(const std::string& v) : value(v), id(nextId()) {}
    };

    DSKind kind() const override { return DSKind::DoublyLinkedList; }
    std::string name() const override { return "双链表 DoublyLinkedList"; }
    std::string description() const override {
        return "每个节点同时持有前驱与后继指针，可双向遍历。";
    }

    int size() const override { return size_; }
    bool empty() const override { return size_ == 0; }

    FrameList insert(const std::string& value) override { return insertAt(size_, value); }

    FrameList insertAt(int pos, const std::string& value) override {
        FrameList frames;
        if (pos < 0) pos = 0;
        if (pos > size_) pos = size_;

        if (!head_) {
            auto n = std::make_unique<Node>(value);
            frames.push_back(makeFrame(StepType::CreateNode, "创建新节点 " + value,
                {n->id}, "#4CAF50", n.get()));
            head_ = std::move(n); tail_ = head_.get();
            frames.push_back(makeFrame(StepType::Link, "头指针指向新节点",
                {head_->id}, "#4CAF50"));
            size_ = 1; frames.push_back(doneFrame("插入完成，链表长度 1"));
            return frames;
        }

        Node* cur = head_.get();
        for (int i = 0; i < pos - 1; ++i) {
            frames.push_back(makeFrame(StepType::Traverse,
                "正向遍历到位置 " + std::to_string(i) + " (值 " + cur->value + ")",
                {cur->id}, "#FFC107"));
            cur = cur->next.get();
        }
        frames.push_back(makeFrame(StepType::Traverse,
            "到达前驱 (值 " + cur->value + ")", {cur->id}, "#FFC107"));

        auto n = std::make_unique<Node>(value);
        int newId = n->id;
        frames.push_back(makeFrame(StepType::CreateNode, "创建新节点 " + value,
            {newId}, "#4CAF50", n.get()));
        n->next = std::move(cur->next);
        if (n->next) n->next->prev = n.get();
        n->prev = cur;
        frames.push_back(makeFrame(StepType::BreakLink,
            "新节点连接后继", {newId, cur->id}, "#FF9800", n.get()));
        cur->next = std::move(n);
        cur->next->prev = cur;                 // re-link prev (n moved)
        if (cur == tail_) tail_ = cur->next.get();
        frames.push_back(makeFrame(StepType::Link,
            "前驱连接新节点 (双向)", {cur->id, newId}, "#4CAF50"));
        size_++;
        frames.push_back(doneFrame("插入完成，链表长度 " + std::to_string(size_)));
        return frames;
    }

    FrameList remove(const std::string& value) override {
        FrameList frames;
        if (!head_) { frames.push_back(doneFrame("链表为空")); return frames; }
        Node* cur = head_.get();
        int idx = 0;
        while (cur) {
            bool match = (cur->value == value);
            frames.push_back(makeFrame(match ? StepType::Highlight : StepType::Compare,
                "比较位置 " + std::to_string(idx) + " (值 " + cur->value + ")",
                {cur->id}, match ? "#4CAF50" : "#FFC107"));
            if (match) {
                // unlink
                if (cur->prev) cur->prev->next = std::move(cur->next);
                else head_ = std::move(cur->next);
                if (cur->next) cur->next->prev = cur->prev;
                else tail_ = cur->prev;
                frames.push_back(makeFrame(StepType::Link,
                    "前驱/后继重新相连，目标移除", {}, "#4CAF50"));
                size_ = std::max(0, size_ - 1);
                frames.push_back(doneFrame("删除完成，链表长度 " + std::to_string(size_)));
                return frames;
            }
            cur = cur->next.get(); idx++;
        }
        frames.push_back(doneFrame("未找到值 " + value));
        return frames;
    }

    FrameList removeAt(int pos) override {
        FrameList frames;
        if (pos < 0 || pos >= size_ || !head_) { frames.push_back(doneFrame("位置非法")); return frames; }
        Node* cur = head_.get();
        for (int i = 0; i < pos; ++i) cur = cur->next.get();
        frames.push_back(makeFrame(StepType::Highlight, "定位位置 " + std::to_string(pos),
            {cur->id}, "#FFC107"));
        if (cur->prev) cur->prev->next = std::move(cur->next);
        else head_ = std::move(cur->next);
        if (cur->next) cur->next->prev = cur->prev;
        else tail_ = cur->prev;
        frames.push_back(makeFrame(StepType::Link, "重新连接，移除目标", {}, "#4CAF50"));
        size_ = std::max(0, size_ - 1);
        frames.push_back(doneFrame("删除完成，链表长度 " + std::to_string(size_)));
        return frames;
    }

    FrameList find(const std::string& value) override {
        FrameList frames;
        Node* cur = head_.get(); int idx = 0;
        while (cur) {
            bool match = (cur->value == value);
            frames.push_back(makeFrame(match ? StepType::Highlight : StepType::Compare,
                "比较位置 " + std::to_string(idx) + " (值 " + cur->value + ")",
                {cur->id}, match ? "#4CAF50" : "#FFC107"));
            if (match) { frames.push_back(doneFrame("查找成功")); return frames; }
            cur = cur->next.get(); idx++;
        }
        frames.push_back(doneFrame("查找失败"));
        return frames;
    }

    FrameList clear() override {
        head_ = nullptr; tail_ = nullptr; size_ = 0;
        FrameList frames; frames.push_back(doneFrame("已清空")); return frames;
    }

    Frame currentFrame() const override { return makeFrame(StepType::Done, "当前状态", {}, "#FFC107"); }

    std::vector<std::string> snapshotValues() const override {
        std::vector<std::string> v; Node* c = head_.get();
        while (c) { v.push_back(c->value); c = c->next.get(); }
        return v;
    }

private:
    std::unique_ptr<Node> head_;
    Node* tail_ = nullptr;
    int size_ = 0;

    Frame makeFrame(StepType type, const std::string& desc,
                    const std::vector<int>& hl, const std::string& color,
                    const Node* staging = nullptr) const {
        Frame f; f.type = type; f.description = desc;
        f.highlightColor = color; f.highlightIds = hl;
        const Node* cur = head_.get();
        while (cur) {
            f.nodes.push_back({cur->id, cur->value, "", -1});
            if (cur->next) f.edges.push_back({cur->id, cur->next->id, "next"});
            if (cur->prev) f.edges.push_back({cur->id, cur->prev->id, "prev"});
            cur = cur->next.get();
        }
        if (staging) f.nodes.push_back({staging->id, staging->value, "", -1});
        return f;
    }
    Frame doneFrame(const std::string& desc) const { return makeFrame(StepType::Done, desc, {}, "#FFC107"); }
};

} // namespace dsv
