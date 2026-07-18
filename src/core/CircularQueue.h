#pragma once
#include "Common.h"
#include "IDataStructure.h"
#include <vector>
#include <string>

namespace dsv {

// ---------------------------------------------------------------------------
// CircularQueue (教科书标准实现)
//
// 固定容量环形缓冲区，使用 front/rear 双指针 + 取模运算实现循环。
// 采用"牺牲一个存储单元"方案判空满：
//   判空：front == rear
//   判满：(rear + 1) % Capacity == front
// 当前元素个数：(rear - front + Capacity) % Capacity
//
// 布局：环形排列（类似旋转寿司传送带），槽位按索引排成圆环，
//       有值的显示数据，空槽显示虚线框。front 标记 F，rear 标记 R。
// ---------------------------------------------------------------------------
class CircularQueue : public IDataStructure {
public:
    // 默认容量 8（实际可用 7，牺牲 1 个判满）
    static constexpr int Capacity = 8;

    struct Slot {
        std::string value;      // 空时为 ""
        int id;                 // 稳定 id（空槽也有 id，用于动画追踪）
        bool occupied;          // 是否有数据
        Slot() : id(nextId()), occupied(false) {}
    };

    CircularQueue() {
        // 初始化所有槽位
        for (int i = 0; i < Capacity; ++i)
            slots_.push_back(Slot());
        front_ = 0;
        rear_ = 0;
    }

    DSKind kind() const override { return DSKind::CircularQueue; }
    std::string name() const override { return "循环队列 CircularQueue"; }
    std::string description() const override {
        return "首尾相连的环形缓冲区，front/rear 指针取模运算，牺牲1单元判空满。"
               "判空: front==rear，判满: (rear+1)%N==front，元素数: (rear-front+N)%N";
    }

    int size() const override { return count(); }
    bool empty() const override { return front_ == rear_; }
    bool full() const { return (rear_ + 1) % Capacity == front_; }

    // 当前元素个数：(rear - front + Capacity) % Capacity
    int count() const {
        return (rear_ - front_ + Capacity) % Capacity;
    }

    FrameList insert(const std::string& value) override { return enqueue(value); }
    FrameList insertAt(int /*pos*/, const std::string& value) override { return enqueue(value); }
    FrameList remove(const std::string&) override { return dequeue(); }
    FrameList removeAt(int) override { return dequeue(); }

    FrameList enqueue(const std::string& value) {
        FrameList frames;
        if (full()) {
            frames.push_back(makeFrame("队列已满！无法入队（牺牲1单元判满）", {}, "#FF5722"));
            return frames;
        }

        // 指针移动动画：rear 后移一步
        int oldRear = rear_;
        frames.push_back(makeFrame("rear 指针移动：(" + std::to_string(oldRear) + "+1) % " +
            std::to_string(Capacity) + " = " + std::to_string((oldRear + 1) % Capacity), {}, "#FFC107"));

        rear_ = (rear_ + 1) % Capacity;
        slots_[rear_].value = value;
        slots_[rear_].occupied = true;

        frames.push_back(makeFrameWithHighlight(
            "入队 [" + value + "] → 索引 #" + std::to_string(rear_) +
            "，元素数 = (rear-front+N)%N = (" + std::to_string(rear_) + "-" +
            std::to_string(front_) + "+" + std::to_string(Capacity) + ") % " +
            std::to_string(Capacity) + " = " + std::to_string(count()),
            {slots_[rear_].id}, "#4CAF50"));

        return frames;
    }

    FrameList dequeue() {
        FrameList frames;
        if (empty()) {
            frames.push_back(makeFrame("队列为空！无法出队（front==rear）", {}, "#FF5722"));
            return frames;
        }

        // 指针移动动画：front 后移一步
        int oldFront = front_;
        std::string val = slots_[front_].value;
        frames.push_back(makeFrameWithHighlight(
            "出队 [" + val + "] ← 索引 #" + std::to_string(front_),
            {slots_[front_].id}, "#FF9800"));

        slots_[front_].value = "";
        slots_[front_].occupied = false;

        front_ = (front_ + 1) % Capacity;
        frames.push_back(makeFrame(
            "front 指针移动：(" + std::to_string(oldFront) + "+1) % " +
            std::to_string(Capacity) + " = " + std::to_string(front_) +
            "，元素数 = " + std::to_string(count()), {}, "#FFC107"));

        return frames;
    }

    FrameList find(const std::string& value) override {
        FrameList frames;
        if (empty()) {
            frames.push_back(makeFrame("队列为空", {}, "#FFC107"));
            return frames;
        }
        frames.push_back(makeFrame("从 front=" + std::to_string(front_) +
            " 开始环形扫描查找 '" + value + "'...", {}, "#FFC107"));

        bool found = false;
        int cur = front_;
        int cnt = count();
        for (int step = 0; step < cnt; ++step) {
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
        frames.push_back(makeFrame("清空循环队列", {}, "#FF9800"));
        for (int i = 0; i < Capacity; ++i) {
            slots_[i].value = "";
            slots_[i].occupied = false;
        }
        front_ = 0;
        rear_ = 0;
        frames.push_back(makeFrame("已清空（front=rear=0）", {}, "#4CAF50"));
        return frames;
    }

    Frame currentFrame() const override { return makeFrame(""); }

    std::vector<std::string> snapshotValues() const override {
        std::vector<std::string> v;
        int cnt = count();
        for (int step = 0; step < cnt; ++step)
            v.push_back(slots_[(front_ + step) % Capacity].value);
        return v;
    }

private:
    std::vector<Slot> slots_;
    int front_;     // 队头指针（出队方向）
    int rear_;      // 队尾指针（入队方向，指向下一个可插入位置）

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
            fn.value = slots_[i].occupied ? slots_[i].value : "";  // 空槽不显示值
            fn.index = i;  // 环形布局用索引

            // sublabel: 显示索引 + F/R 标记
            std::string sub = "#" + std::to_string(i);
            if (i == front_) sub += " F";
            if (i == rear_)  sub += " R";
            fn.sublabel = sub;

            // 空槽用灰色，有值槽用默认色
            if (!slots_[i].occupied) fn.color = "#B0BEC5";  // 虚灰表示空槽

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
