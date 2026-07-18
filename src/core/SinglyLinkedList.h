#pragma once
#include "Common.h"
#include "IDataStructure.h"
#include <memory>
#include <sstream>

namespace dsv {

// ---------------------------------------------------------------------------
// Singly Linked List  (append + positional insert/remove)
// ---------------------------------------------------------------------------
class SinglyLinkedList : public IDataStructure {
public:
    struct Node {
        std::string value;
        int id;
        std::unique_ptr<Node> next;
        Node(const std::string& v) : value(v), id(nextId()) {}
    };

    DSKind kind() const override { return DSKind::SinglyLinkedList; }
    std::string name() const override { return "单链表 SinglyLinkedList"; }
    std::string description() const override {
        return "指针串联的线性结构，支持表头/表尾/任意位置插入与删除。";
    }

    int size() const override { return size_; }
    bool empty() const override { return size_ == 0; }

    FrameList insert(const std::string& value) override {
        return insertAt(size_, value);   // default = append
    }

    FrameList insertAt(int pos, const std::string& value) override {
        FrameList frames;
        if (pos < 0) pos = 0;
        if (pos > size_) pos = size_;

        if (!head_) {
            auto n = std::make_unique<Node>(value);
            frames.push_back(makeFrame(StepType::CreateNode,
                "创建新节点 " + value, {n->id}, "#4CAF50", n.get()));
            head_ = std::move(n);
            frames.push_back(makeFrame(StepType::Link,
                "头指针指向新节点", {head_->id}, "#4CAF50"));
            size_ = 1;
            frames.push_back(doneFrame("插入完成，链表长度 1"));
            return frames;
        }

        Node* cur = head_.get();
        for (int i = 0; i < pos - 1; ++i) {
            frames.push_back(makeFrame(StepType::Traverse,
                "遍历到位置 " + std::to_string(i) + " (值 " + cur->value + ")",
                {cur->id}, "#FFC107"));
            cur = cur->next.get();
        }
        frames.push_back(makeFrame(StepType::Traverse,
            "到达插入位置的前驱 (值 " + cur->value + ")", {cur->id}, "#FFC107"));

        auto n = std::make_unique<Node>(value);
        int newId = n->id;
        frames.push_back(makeFrame(StepType::CreateNode,
            "创建新节点 " + value, {newId}, "#4CAF50", n.get()));
        n->next = std::move(cur->next);
        frames.push_back(makeFrame(StepType::BreakLink,
            "新节点指向原后继", {newId, cur->id}, "#FF9800", n.get()));
        cur->next = std::move(n);
        frames.push_back(makeFrame(StepType::Link,
            "前驱指向新节点", {cur->id, newId}, "#4CAF50"));
        size_++;
        frames.push_back(doneFrame("插入完成，链表长度 " + std::to_string(size_)));
        return frames;
    }

    FrameList remove(const std::string& value) override {
        FrameList frames;
        if (!head_) { frames.push_back(doneFrame("链表为空，无法删除")); return frames; }

        if (head_->value == value) {
            frames.push_back(makeFrame(StepType::Compare,
                "表头即为目标 (值 " + value + ")", {head_->id}, "#FFC107"));
            head_ = std::move(head_->next);
            frames.push_back(makeFrame(StepType::BreakLink,
                "头指针跳过目标节点", head_ ? std::vector<int>{head_->id} : std::vector<int>{},
                "#FF9800"));
            size_ = std::max(0, size_ - 1);
            frames.push_back(doneFrame("删除完成，链表长度 " + std::to_string(size_)));
            return frames;
        }

        Node* prev = head_.get();
        Node* cur = head_->next.get();
        int idx = 1;
        while (cur) {
            frames.push_back(makeFrame(StepType::Compare,
                "比较位置 " + std::to_string(idx) + " (值 " + cur->value + ") 与目标 " + value,
                {cur->id}, "#FFC107"));
            if (cur->value == value) {
                prev->next = std::move(cur->next);
                frames.push_back(makeFrame(StepType::Link,
                    "前驱指向后继，目标被移除", {prev->id}, "#4CAF50"));
                size_ = std::max(0, size_ - 1);
                frames.push_back(doneFrame("删除完成，链表长度 " + std::to_string(size_)));
                return frames;
            }
            prev = cur; cur = cur->next.get(); idx++;
        }
        frames.push_back(doneFrame("未找到值 " + value));
        return frames;
    }

    FrameList removeAt(int pos) override {
        FrameList frames;
        if (pos < 0 || pos >= size_ || !head_) {
            frames.push_back(doneFrame("位置非法或链表为空"));
            return frames;
        }
        if (pos == 0) return remove(head_->value);
        Node* prev = head_.get();
        for (int i = 0; i < pos - 1; ++i) prev = prev->next.get();
        frames.push_back(makeFrame(StepType::Traverse,
            "定位前驱 (值 " + prev->value + ")", {prev->id}, "#FFC107"));
        frames.push_back(makeFrame(StepType::BreakLink,
            "前驱指向后继，移除位置 " + std::to_string(pos), {prev->id}, "#FF9800"));
        prev->next = std::move(prev->next->next);
        frames.push_back(makeFrame(StepType::Link,
            "删除完成", {prev->id}, "#4CAF50"));
        size_ = std::max(0, size_ - 1);
        frames.push_back(doneFrame("删除完成，链表长度 " + std::to_string(size_)));
        return frames;
    }

    FrameList find(const std::string& value) override {
        FrameList frames;
        Node* cur = head_.get();
        int idx = 0;
        while (cur) {
            bool match = (cur->value == value);
            frames.push_back(makeFrame(match ? StepType::Highlight : StepType::Compare,
                "比较位置 " + std::to_string(idx) + " (值 " + cur->value + ")" +
                (match ? " = 命中!" : " 不等于目标"),
                {cur->id}, match ? "#4CAF50" : "#FFC107"));
            if (match) { frames.push_back(doneFrame("查找成功，位置 " + std::to_string(idx))); return frames; }
            cur = cur->next.get(); idx++;
        }
        frames.push_back(doneFrame("查找失败，链表中不存在 " + value));
        return frames;
    }

    FrameList clear() override {
        head_.reset(); size_ = 0;
        FrameList frames; frames.push_back(doneFrame("已清空链表"));
        return frames;
    }

    Frame currentFrame() const override {
        return makeFrame(StepType::Done, "当前链表状态", {}, "#FFC107");
    }

    std::vector<std::string> snapshotValues() const override {
        std::vector<std::string> v; Node* c = head_.get();
        while (c) { v.push_back(c->value); c = c->next.get(); }
        return v;
    }

private:
    std::unique_ptr<Node> head_;
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
            cur = cur->next.get();
        }
        if (staging) f.nodes.push_back({staging->id, staging->value, "", -1});
        return f;
    }
    Frame doneFrame(const std::string& desc) const {
        return makeFrame(StepType::Done, desc, {}, "#FFC107");
    }
};

} // namespace dsv
