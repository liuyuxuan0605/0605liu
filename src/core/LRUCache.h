#pragma once
#include "Common.h"
#include "IDataStructure.h"
#include <vector>
#include <string>
#include <unordered_map>
#include <memory>
#include <cstdio>

namespace dsv {

// ---------------------------------------------------------------------------
// LRUCache (最近最少使用缓存)
//
// 经典组合数据结构：哈希表(查找 O(1)) + 双向链表(维护访问顺序)。
//   - head = 最近使用(MRU)，tail = 最久未用(LRU，满时淘汰)
//   - put(key,value)：存在则更新并移到头部；不存在则插入头部；
//                      超出容量则淘汰尾部(LRU)
//   - get(key)：命中则移到头部并返回；未命中返回提示
//
// 面试第一高频手写题。布局复用双向链表水平链（head 在左），
// 用 index 表示访问顺序，节点移动时由布局驱动平滑动画。
// ---------------------------------------------------------------------------
class LRUCache : public IDataStructure {
public:
    struct Node {
        std::string key;
        std::string value;
        int id;
        Node* prev = nullptr;   // non-owning
        Node* next = nullptr;   // non-owning
        Node(const std::string& k, const std::string& val, int i) : key(k), value(val), id(i) {}
    };

    static constexpr int Capacity = 4;   // 演示用容量

    DSKind kind() const override { return DSKind::LRUCache; }
    std::string name() const override { return "LRU 缓存 LRUCache"; }
    std::string description() const override {
        return "哈希表 + 双向链表实现的 LRU 缓存（容量 " + std::to_string(Capacity) +
               "）。put 插入/更新并移到队首，get 命中移到队首，超容量淘汰队尾(LRU)。"
               "面试第一高频手写题，展示组合数据结构解决工程问题。";
    }

    int size() const override { return static_cast<int>(cache_.size()); }
    bool empty() const override { return cache_.empty(); }

    FrameList insert(const std::string& spec) override { return put(spec); }
    FrameList insertAt(int, const std::string&) override { return {}; }
    FrameList remove(const std::string& key) override { return get(key); }
    FrameList removeAt(int) override { return {}; }
    FrameList find(const std::string& key) override { return get(key); }

    // spec: "key" 或 "key:value"
    FrameList put(const std::string& spec) {
        FrameList frames;
        std::string key, val;
        auto colon = spec.find(':');
        if (colon != std::string::npos) { key = spec.substr(0, colon); val = spec.substr(colon + 1); }
        else { key = spec; val = spec; }
        if (key.empty()) { frames.push_back(snapshotFrame("请输入 key", {}, "#FF5722")); return frames; }

        auto it = cache_.find(key);
        if (it != cache_.end()) {
            it->second->value = val;
            moveToHead(it->second.get());
            frames.push_back(snapshotFrameWithHighlight(
                "put [" + key + "] 已存在 → 更新值并移到 MRU 队首", {it->second->id}, "#4CAF50"));
            return frames;
        }
        // new node
        int id = nextId();
        auto node = std::make_unique<Node>(key, val, id);
        Node* raw = node.get();
        cache_[key] = std::move(node);
        addToHead(raw);
        frames.push_back(snapshotFrameWithHighlight(
            "put [" + key + "] 新插入 → 放到 MRU 队首", {id}, "#4CAF50"));
        if (static_cast<int>(cache_.size()) > Capacity) {
            Node* tail = tail_;
            frames.push_back(snapshotFrameWithHighlight(
                "超出容量 " + std::to_string(Capacity) + " → 淘汰 LRU 队尾 [" + tail->key + "]",
                {tail->id}, "#FF5722"));
            removeNode(tail);
            cache_.erase(tail->key);
        }
        return frames;
    }

    FrameList get(const std::string& key) {
        FrameList frames;
        if (key.empty()) { frames.push_back(snapshotFrame("请输入要读取的 key", {}, "#FF5722")); return frames; }
        auto it = cache_.find(key);
        if (it == cache_.end()) {
            frames.push_back(snapshotFrame("get [" + key + "] 未命中（不在缓存中）", {}, "#FF9800"));
            return frames;
        }
        moveToHead(it->second.get());
        frames.push_back(snapshotFrameWithHighlight(
            "get [" + key + "] 命中 → 移到 MRU 队首", {it->second->id}, "#FF7043"));
        return frames;
    }

    FrameList clear() override {
        FrameList frames;
        cache_.clear(); head_ = tail_ = nullptr;
        frames.push_back(snapshotFrame("已清空 LRU 缓存", {}, "#4CAF50"));
        return frames;
    }

    Frame currentFrame() const override { return snapshotFrame(""); }

    std::vector<std::string> snapshotValues() const override {
        std::vector<std::string> v;
        for (Node* cur = head_; cur; cur = cur->next) v.push_back(cur->key);
        return v;
    }

private:
    std::unordered_map<std::string, std::unique_ptr<Node>> cache_;
    Node* head_ = nullptr;   // MRU
    Node* tail_ = nullptr;   // LRU

    void addToHead(Node* n) {
        n->prev = nullptr; n->next = head_;
        if (head_) head_->prev = n;
        else tail_ = n;
        head_ = n;
    }
    void removeNode(Node* n) {
        if (n->prev) n->prev->next = n->next;
        else head_ = n->next;
        if (n->next) n->next->prev = n->prev;
        else tail_ = n->prev;
        n->prev = n->next = nullptr;
    }
    void moveToHead(Node* n) {
        removeNode(n);
        addToHead(n);
    }

    Frame snapshotFrame(const std::string& desc,
                        const std::vector<int>& hIds = {},
                        const std::string& color = "#EDE7F6") const {
        Frame f; f.type = StepType::Done; f.description = desc;
        f.highlightColor = color; f.highlightIds = hIds;
        int idx = 0;
        for (Node* cur = head_; cur; cur = cur->next) {
            FrameNode fn; fn.id = cur->id; fn.value = cur->key; fn.index = idx;
            fn.sublabel = (cur == head_) ? "MRU" : (cur == tail_ ? "LRU" : "");
            f.nodes.push_back(fn);
            if (cur->next) {
                FrameEdge fe; fe.fromId = cur->id; fe.toId = cur->next->id; fe.kind = "next";
                f.edges.push_back(fe);
            }
            idx++;
        }
        return f;
    }
    Frame snapshotFrameWithHighlight(const std::string& desc,
                                     const std::vector<int>& hIds,
                                     const std::string& color) const {
        Frame f = snapshotFrame(desc, {}, color);
        f.highlightIds = hIds;
        return f;
    }
};

} // namespace dsv
