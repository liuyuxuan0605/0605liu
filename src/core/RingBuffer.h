#pragma once
#include "Common.h"
#include "IDataStructure.h"
#include <vector>
#include <string>

namespace dsv {

// ---------------------------------------------------------------------------
// RingBuffer (环形缓冲区 / 覆写式环形队列)
//
// 固定容量环形缓冲区，与 BlockingQueue 的关键区别：
//   BlockingQueue：满时阻塞等待（拒绝入队，牺牲1单元判满）
//   RingBuffer：满时覆盖最旧数据（永不阻塞写端，适用于音频/视频流缓冲）
//
// 实现：front/rear 双指针 + 取模运算 + 实际元素计数(count)。
//   入队：直接写 rear 位置，rear=(rear+1)%N
//         若满则同步推进 front=(front+1)%N（丢弃最旧数据）
//   出队：读 front 位置，front=(front+1)%N
//   判空：count == 0
//   判满：count == Capacity
//   元素数：count 变量维护
//
// 布局：环形排列（与 BlockingQueue 相同的环形布局），有值槽显示数据，
//       空槽显示虚线框，front 标记 F，rear 标记 R。
// ---------------------------------------------------------------------------
class RingBuffer : public IDataStructure {
public:
    static constexpr int Capacity = 8;

    struct Slot {
        std::string value;
        int id;
        bool occupied;
        Slot() : id(nextId()), occupied(false) {}
    };

    RingBuffer() {
        for (int i = 0; i < Capacity; ++i)
            slots_.push_back(Slot());
        front_ = 0;
        rear_ = 0;
        count_ = 0;
    }

    DSKind kind() const override { return DSKind::RingBuffer; }
    std::string name() const override { return "环形缓冲区 RingBuffer"; }
    std::string description() const override {
        return "固定容量环形缓冲区，满时覆写最旧数据（永不阻塞写端）。"
               "与循环队列区别：循环队列满时拒绝入队，环形缓冲区满时覆盖队首。"
               "典型应用：音频/视频流缓冲、生产者-消费者模式。";
    }

    int size() const override { return count_; }
    bool empty() const override { return count_ == 0; }
    bool full() const { return count_ == Capacity; }

    FrameList insert(const std::string& value) override { return write(value); }
    FrameList insertAt(int /*pos*/, const std::string& value) override { return write(value); }
    FrameList remove(const std::string&) override { return read(); }
    FrameList removeAt(int) override { return read(); }

    FrameList write(const std::string& value) {
        FrameList frames;

        if (full()) {
            // 覆写模式：丢弃最旧数据，front 同步推进
            std::string oldVal = slots_[front_].value;
            frames.push_back(makeFrameWithHighlight(
                "缓冲区已满！覆写最旧数据 [" + oldVal + "]（front 同步推进）",
                {slots_[front_].id}, "#FF5722"));
            slots_[front_].value = "";
            slots_[front_].occupied = false;
            front_ = (front_ + 1) % Capacity;
            count_--;
            frames.push_back(makeFrame(
                "front 推进到 #" + std::to_string(front_) + "，为新数据腾出空间", {}, "#FF5722"));
        }

        // 写入 rear 位置
        int writeIdx = rear_;
        slots_[writeIdx].value = value;
        slots_[writeIdx].occupied = true;
        rear_ = (rear_ + 1) % Capacity;
        count_++;

        frames.push_back(makeFrameWithHighlight(
            "写入 [" + value + "] → 索引 #" + std::to_string(writeIdx) +
            "，rear → #" + std::to_string(rear_) +
            "，元素数 = " + std::to_string(count_),
            {slots_[writeIdx].id}, "#4CAF50"));

        return frames;
    }

    FrameList read() {
        FrameList frames;
        if (empty()) {
            frames.push_back(makeFrame("缓冲区为空！无法读取（count=0）", {}, "#FF5722"));
            return frames;
        }

        std::string val = slots_[front_].value;
        frames.push_back(makeFrameWithHighlight(
            "读取 [" + val + "] ← 索引 #" + std::to_string(front_),
            {slots_[front_].id}, "#FF9800"));

        slots_[front_].value = "";
        slots_[front_].occupied = false;
        front_ = (front_ + 1) % Capacity;
        count_--;

        frames.push_back(makeFrame(
            "front → #" + std::to_string(front_) + "，元素数 = " + std::to_string(count_), {}, "#FFC107"));

        return frames;
    }

    FrameList find(const std::string& value) override {
        FrameList frames;
        if (empty()) {
            frames.push_back(makeFrame("缓冲区为空", {}, "#FFC107"));
            return frames;
        }
        frames.push_back(makeFrame("从 front=#" + std::to_string(front_) +
            " 开始环形扫描查找 '" + value + "'...", {}, "#FFC107"));

        bool found = false;
        for (int step = 0; step < count_; ++step) {
            int idx = (front_ + step) % Capacity;
            bool match = (slots_[idx].value == value);
            frames.push_back(makeFrameWithHighlight(
                "比较索引 #" + std::to_string(idx) + " (值 [" + slots_[idx].value + "])",
                {slots_[idx].id}, match ? "#4CAF50" : "#FFC107"));
            if (match) { found = true; break; }
        }

        if (found)
            frames.push_back(makeFrame("查找成功：找到 [" + value + "]", {}, "#4CAF50"));
        else
            frames.push_back(makeFrame("查找失败：未找到 [" + value + "]", {}, "#FF9800"));
        return frames;
    }

    FrameList clear() override {
        FrameList frames;
        frames.push_back(makeFrame("清空环形缓冲区", {}, "#FF9800"));
        for (int i = 0; i < Capacity; ++i) {
            slots_[i].value = "";
            slots_[i].occupied = false;
        }
        front_ = 0;
        rear_ = 0;
        count_ = 0;
        frames.push_back(makeFrame("已清空（front=rear=0, count=0）", {}, "#4CAF50"));
        return frames;
    }

    Frame currentFrame() const override { return makeFrame(""); }

    std::vector<std::string> snapshotValues() const override {
        std::vector<std::string> v;
        for (int step = 0; step < count_; ++step)
            v.push_back(slots_[(front_ + step) % Capacity].value);
        return v;
    }

private:
    std::vector<Slot> slots_;
    int front_;
    int rear_;
    int count_;  // 实际元素计数（判空：0，判满：Capacity）

    Frame makeFrame(const std::string& desc,
                    const std::vector<int>& hIds = {},
                    const std::string& color = "#EDE7F6") const {
        Frame f;
        f.type = StepType::Done;
        f.description = desc;
        f.highlightColor = color;
        f.highlightIds = hIds;

        for (int i = 0; i < Capacity; ++i) {
            FrameNode fn;
            fn.id = slots_[i].id;
            fn.value = slots_[i].occupied ? slots_[i].value : "";
            fn.index = i;

            std::string sub = "#" + std::to_string(i);
            if (i == front_) sub += " F";
            if (i == rear_)  sub += " R";
            fn.sublabel = sub;

            if (!slots_[i].occupied) fn.color = "#B0BEC5";

            f.nodes.push_back(fn);
        }

        // 环形边：slot i → slot (i+1)%Capacity
        for (int i = 0; i < Capacity; ++i) {
            FrameEdge fe;
            fe.fromId = slots_[i].id;
            fe.toId = slots_[(i + 1) % Capacity].id;
            fe.kind = "next";
            f.edges.push_back(fe);
        }

        return f;
    }

    Frame makeFrameWithHighlight(const std::string& desc,
                                 const std::vector<int>& hIds,
                                 const std::string& color) const {
        Frame f = makeFrame(desc, {}, color);
        f.highlightIds = hIds;
        return f;
    }
};

} // namespace dsv
