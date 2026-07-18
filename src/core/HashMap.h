#pragma once
#include "Common.h"
#include "IDataStructure.h"
#include <memory>
#include <vector>
#include <functional>

namespace dsv {

// ---------------------------------------------------------------------------
// HashMap  (chaining: each bucket is a singly linked list of entries)
// ---------------------------------------------------------------------------
class HashMap : public IDataStructure {
public:
    struct Entry {
        std::string key, value; int id;
        std::unique_ptr<Entry> next;
        Entry(const std::string& k, const std::string& v) : key(k), value(v), id(nextId()) {}
    };

    static constexpr int CAP = 8;

    DSKind kind() const override { return DSKind::HashMap; }
    std::string name() const override { return "哈希表 HashMap"; }
    std::string description() const override {
        return "链式冲突解决：键经哈希定位到桶，桶内以链表串接键值对。";
    }

    int size() const override { return size_; }
    bool empty() const override { return size_ == 0; }

    FrameList insert(const std::string& kv) override {
        // accept "key" or "key:value"
        auto pos = kv.find(':');
        std::string key = (pos == std::string::npos) ? kv : kv.substr(0, pos);
        std::string val = (pos == std::string::npos) ? kv : kv.substr(pos + 1);
        return put(key, val);
    }
    FrameList insertAt(int, const std::string&) override { return FrameList{}; }

    FrameList put(const std::string& key, const std::string& value) {
        FrameList frames;
        int b = bucket(key);
        frames.push_back(makeFrame(StepType::HashCompute,
            "hash(\"" + key + "\") % " + std::to_string(CAP) + " = " + std::to_string(b),
            {bucketId(b)}, "#FFC107"));
        Entry* cur = buckets_[b].get();
        Entry* prev = nullptr;
        while (cur) {
            frames.push_back(makeFrame(StepType::Compare,
                "桶内比较 key=" + cur->key, {cur->id, bucketId(b)}, "#FFC107"));
            if (cur->key == key) {
                cur->value = value;
                frames.push_back(makeFrame(StepType::Swap, "键已存在，更新值", {cur->id}, "#BA68C8"));
                frames.push_back(doneFrame("更新完成"));
                return frames;
            }
            prev = cur; cur = cur->next.get();
        }
        auto e = std::make_unique<Entry>(key, value);
        int newId = e->id;
        frames.push_back(makeFrame(StepType::BucketLocate, "在桶 " + std::to_string(b) + " 追加新条目",
            {bucketId(b), newId}, "#4CAF50"));
        if (prev) prev->next = std::move(e);
        else buckets_[b] = std::move(e);
        frames.push_back(makeFrame(StepType::Link, "新条目挂入桶链",
            {newId, bucketId(b)}, "#4CAF50"));
        size_++; frames.push_back(doneFrame("插入完成，条目数 " + std::to_string(size_)));
        return frames;
    }

    FrameList remove(const std::string& key) override {
        FrameList frames;
        int b = bucket(key);
        frames.push_back(makeFrame(StepType::HashCompute,
            "hash(\"" + key + "\") % " + std::to_string(CAP) + " = " + std::to_string(b),
            {bucketId(b)}, "#FFC107"));
        Entry* cur = buckets_[b].get();
        Entry* prev = nullptr;
        while (cur) {
            frames.push_back(makeFrame(StepType::Compare, "桶内比较 key=" + cur->key,
                {cur->id, bucketId(b)}, "#FFC107"));
            if (cur->key == key) {
                if (prev) prev->next = std::move(cur->next);
                else buckets_[b] = std::move(cur->next);
                frames.push_back(makeFrame(StepType::Link, "前驱/后继重连，条目移除",
                    {bucketId(b)}, "#4CAF50"));
                size_ = std::max(0, size_ - 1);
                frames.push_back(doneFrame("删除完成，条目数 " + std::to_string(size_)));
                return frames;
            }
            prev = cur; cur = cur->next.get();
        }
        frames.push_back(doneFrame("未找到 key=" + key));
        return frames;
    }

    FrameList removeAt(int) override { return FrameList{}; }

    FrameList find(const std::string& key) override {
        FrameList frames;
        int b = bucket(key);
        frames.push_back(makeFrame(StepType::HashCompute,
            "hash(\"" + key + "\") % " + std::to_string(CAP) + " = " + std::to_string(b),
            {bucketId(b)}, "#FFC107"));
        Entry* cur = buckets_[b].get();
        while (cur) {
            bool match = (cur->key == key);
            frames.push_back(makeFrame(match ? StepType::Highlight : StepType::Compare,
                "桶内比较 key=" + cur->key, {cur->id, bucketId(b)}, match ? "#4CAF50" : "#FFC107"));
            if (match) { frames.push_back(doneFrame("命中 value=" + cur->value)); return frames; }
            cur = cur->next.get();
        }
        frames.push_back(doneFrame("未找到 key=" + key));
        return frames;
    }

    FrameList clear() override {
        for (auto& b : buckets_) b.reset();
        size_ = 0; FrameList f; f.push_back(doneFrame("已清空")); return f;
    }

    Frame currentFrame() const override { return makeFrame(StepType::Done, "当前哈希表状态", {}, "#FFC107"); }

    std::vector<std::string> snapshotValues() const override {
        std::vector<std::string> v;
        for (auto& b : buckets_) {
            Entry* c = b.get();
            while (c) { v.push_back(c->key + ":" + c->value); c = c->next.get(); }
        }
        return v;
    }

private:
    std::vector<std::unique_ptr<Entry>> buckets_{CAP};
    int size_ = 0;

    static int bucket(const std::string& key) {
        return static_cast<int>(std::hash<std::string>{}(key) % CAP);
    }
    static int bucketId(int b) { return -(b + 1); }   // stable negative ids for headers

    Frame makeFrame(StepType t, const std::string& d, const std::vector<int>& hl,
                    const std::string& c) const {
        Frame f; f.type = t; f.description = d; f.highlightColor = c; f.highlightIds = hl;
        for (int i = 0; i < CAP; ++i) {
            f.nodes.push_back({bucketId(i), "B" + std::to_string(i), "", i});
            const Entry* c0 = buckets_[i].get();
            if (c0) {
                f.edges.push_back({bucketId(i), c0->id, "bucket"});
                const Entry* p = c0;
                while (p) {
                    f.nodes.push_back({p->id, p->value, "k=" + p->key, -1});
                    if (p->next) f.edges.push_back({p->id, p->next->id, "next"});
                    p = p->next.get();
                }
            }
        }
        return f;
    }
    Frame doneFrame(const std::string& d) const { return makeFrame(StepType::Done, d, {}, "#FFC107"); }
};

} // namespace dsv
