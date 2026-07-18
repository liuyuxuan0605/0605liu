#pragma once
#include "Common.h"
#include "IDataStructure.h"
#include <vector>
#include <string>
#include <algorithm>
#include <stdexcept>

namespace dsv {

// ---------------------------------------------------------------------------
// MinHeap (binary min-heap using array storage, 0-indexed)
//
// Layout: the LayoutEngine MinHeap branch uses FrameNode.index as the
// array index to place nodes in a complete binary tree shape.
// Edges: parent -> left child (kind "left"), parent -> right child ("right").
//
// Algorithms:
//   push/insert: append at end, sift up (compare with parent, swap until heap order)
//   pop/remove: swap root with last element, remove last, sift down root
//   find: linear scan (heap is not ordered for search)
// ---------------------------------------------------------------------------

class MinHeap : public IDataStructure {
public:
    struct HeapNode {
        std::string value;
        int id;                     // stable visual id (assigned once, never reused)
        int arrIndex = -1;          // current position in the backing array
        HeapNode(const std::string& v) : value(v), id(nextId()) {}
    };

    DSKind kind() const override { return DSKind::MinHeap; }
    std::string name() const override { return "最小堆 MinHeap"; }
    std::string description() const override {
        return "二叉最小堆：插入(上浮)/删除(下沉)，根节点始终为最小值。";
    }

    int size() const override { return static_cast<int>(data_.size()); }
    bool empty() const override { return data_.empty(); }

    // --- public operations (each returns a frame list for animation) ---

    FrameList insert(const std::string& value) override { return push(value); }

    FrameList insertAt(int /*pos*/, const std::string& value) override {
        // MinHeap does not support positional insertion; ignore pos and push normally.
        return push(value);
    }

    FrameList remove(const std::string& value) override {
        // In a min-heap, "remove" by value means:
        //   - if value == root's value → pop (remove min)
        //   - otherwise find and remove that element (decrease-key style: replace with -inf, sift up, then pop)
        // For simplicity: if empty or not found → no-op frames.
        // If found at non-root: swap to end then pop.
        FrameList frames;

        auto it = findIter(value);
        if (it == data_.end()) {
            frames.push_back(makeFrame("未找到值 '" + value + "'，无操作"));
            return frames;
        }

        size_t idx = static_cast<size_t>(it - data_.begin());
        if (idx == 0) {
            // Removing the root = standard pop
            return pop();
        }

        // Remove at arbitrary index: swap with last element, pop last, then sift down from idx
        frames.push_back(makeFrame("找到要删除的元素 [" + value + "]，位置 #" + std::to_string(idx)));
        std::swap(data_[idx], data_[data_.size() - 1]);
        data_[idx]->arrIndex = static_cast<int>(idx);
        data_[data_.size() - 1]->arrIndex = static_cast<int>(data_.size() - 1);
        updateAllIndices();
        frames.push_back(makeFrame("将末尾元素交换到位置 #" + std::to_string(idx)));

        std::string removedVal = data_.back()->value;
        int removedId = data_.back()->id;
        data_.pop_back();
        frames.push_back(makeFrame("删除元素 [" + removedVal + "]"));

        // Sift down from idx
        siftDownFrames(idx, frames);
        frames.push_back(makeFrame("删除完成"));
        return frames;
    }

    FrameList find(const std::string& value) override {
        FrameList frames;
        frames.push_back(makeFrame("开始查找 '" + value + "'..."));

        bool found = false;
        for (size_t i = 0; i < data_.size(); ++i) {
            Frame f = makeFrame("检查位置 #" + std::to_string(i) + ": [" + data_[i]->value + "]");
            if (data_[i]->value == value) {
                f.highlightIds.push_back(data_[i]->id);
                found = true;
                f.description = "找到 [" + value + "] 在位置 #" + std::to_string(i);
            }
            frames.push_back(std::move(f));
        }

        if (!found) {
            Frame f = makeFrame("未找到 '" + value + "'");
            frames.push_back(std::move(f));
        } else {
            Frame f = makeFrame("查找完成：找到 [" + value + "]");
            frames.push_back(std::move(f));
        }
        return frames;
    }

    FrameList clear() override {
        FrameList frames;
        frames.push_back(makeFrame("清空堆"));
        data_.clear();
        idCounter();  // reset? No, keep monotonic for animation stability
        frames.push_back(makeFrame("已清空"));
        return frames;
    }

    FrameList removeAt(int /*pos*/) override {
        // MinHeap does not support positional removal by index.
        FrameList frames;
        frames.push_back(makeFrame("最小堆不支持按位置删除"));
        return frames;
    }

    // --- push / pop helpers ---

    FrameList push(const std::string& value) {
        FrameList frames;
        frames.push_back(makeFrame("插入 [" + value + "] 到堆尾"));

        data_.push_back(std::make_unique<HeapNode>(value));
        size_t idx = data_.size() - 1;
        data_[idx]->arrIndex = static_cast<int>(idx);

        frames.push_back(makeFrame("新元素位于位置 #" + std::to_string(idx) + ", 开始上浮"));

        // Sift up
        while (idx > 0) {
            size_t parent = (idx - 1) / 2;
            frames.push_back(makeFrameWithHighlight(
                "比较位置 #" + std::to_string(idx) + " [" + data_[idx]->value +
                "] 与父节点 #" + std::to_string(parent) + " [" + data_[parent]->value + "]",
                {data_[idx]->id, data_[parent]->id}));

            if (compareValues(data_[idx]->value, data_[parent]->value) < 0) {
                // Swap
                frames.push_back(makeFrameWithHighlight(
                    "[" + data_[idx]->value + "] < [" + data_[parent]->value + "]，交换",
                    {data_[idx]->id, data_[parent]->id}));
                std::swap(data_[idx], data_[parent]);
                data_[idx]->arrIndex = static_cast<int>(idx);
                data_[parent]->arrIndex = static_cast<int>(parent);
                updateAllIndices();
                frames.push_back(makeFrame(
                    "交换完成：" + data_[parent]->value + " 上浮到位置 #" + std::to_string(parent)));
                idx = parent;
            } else {
                frames.push_back(makeFrameWithHighlight(
                    "[" + data_[idx]->value + "] >= [" + data_[parent]->value + "]，上浮结束，堆性质满足",
                    {data_[idx]->id, data_[parent]->id}));
                break;
            }
        }

        if (idx == 0 && data_.size() > 1) {
            frames.push_back(makeFrame("已到达根节点位置 #0，上浮完成"));
        }

        frames.push_back(makeFrame("插入完成，当前最小值为 [" + topValue() + "]"));
        return frames;
    }

    FrameList pop() {
        FrameList frames;
        if (data_.empty()) {
            frames.push_back(makeFrame("堆为空，无法弹出"));
            return frames;
        }

        std::string minVal = data_[0]->value;
        frames.push_back(makeFrame("弹出最小值 [" + minVal + "] (根节点位置 #0)"));

        if (data_.size() == 1) {
            data_.pop_back();
            frames.push_back(makeFrame("已弹出唯一元素，堆为空"));
            return frames;
        }

        // Swap root with last element
        frames.push_back(makeFrame("将末尾元素 [" + data_.back()->value + "] 移到根节点位置 #0"));
        std::swap(data_[0], data_.back());
        data_[0]->arrIndex = 0;
        data_[data_.size() - 1]->arrIndex = static_cast<int>(data_.size() - 1);

        // Remove last (which is now the old root)
        data_.pop_back();
        frames.push_back(makeFrame("已移除原根节点 [" + minVal + "]，开始从根下沉"));

        // Sift down from root
        siftDownFrames(0, frames);

        frames.push_back(makeFrame("弹出完成，当前最小值 [" + topValue() + "]"));
        return frames;
    }

    Frame currentFrame() const override {
        return makeFrame("");
    }

    std::vector<std::string> snapshotValues() const override {
        std::vector<std::string> vals;
        for (const auto& n : data_) vals.push_back(n->value);
        return vals;
    }

private:
    std::vector<std::unique_ptr<HeapNode>> data_;

    // --- internal helpers ---

    std::string topValue() const {
        return data_.empty() ? "(空)" : data_[0]->value;
    }

    typename std::vector<std::unique_ptr<HeapNode>>::iterator findIter(const std::string& value) {
        for (auto it = data_.begin(); it != data_.end(); ++it) {
            if ((*it)->value == value) return it;
        }
        return data_.end();
    }

    void updateAllIndices() {
        for (size_t i = 0; i < data_.size(); ++i)
            data_[i]->arrIndex = static_cast<int>(i);
    }

    void siftDownFrames(size_t idx, FrameList& frames) {
        size_t n = data_.size();
        while (true) {
            size_t smallest = idx;
            size_t left = 2 * idx + 1;
            size_t right = 2 * idx + 2;

            if (left < n) {
                frames.push_back(makeFrameWithHighlight(
                    "比较位置 #" + std::to_string(smallest) + " [" + data_[smallest]->value +
                    "] 与左子 #" + std::to_string(left) + " [" + data_[left]->value + "]",
                    {data_[smallest]->id, data_[left]->id}));
                if (compareValues(data_[left]->value, data_[smallest]->value) < 0)
                    smallest = left;
            }
            if (right < n) {
                frames.push_back(makeFrameWithHighlight(
                    "比较位置 #" + std::to_string(smallest) + " [" + data_[smallest]->value +
                    "] 与右子 #" + std::to_string(right) + " [" + data_[right]->value + "]",
                    {data_[smallest]->id, data_[right]->id}));
                if (compareValues(data_[right]->value, data_[smallest]->value) < 0)
                    smallest = right;
            }

            if (smallest != idx) {
                frames.push_back(makeFrameWithHighlight(
                    "[" + data_[smallest]->value + "] < [" + data_[idx]->value + "]，交换位置 #" +
                    std::to_string(idx) + " <-> #" + std::to_string(smallest),
                    {data_[idx]->id, data_[smallest]->id}));
                std::swap(data_[idx], data_[smallest]);
                updateAllIndices();
                frames.push_back(makeFrame(
                    "交换完成：" + data_[smallest]->value + " 下沉到位置 #" + std::to_string(smallest)));
                idx = smallest;
            } else {
                frames.push_back(makeFrameWithHighlight(
                    "位置 #" + std::to_string(idx) + " [" + data_[idx]->value + "] 已是最小子节点，下沉结束",
                    {data_[idx]->id}));
                break;
            }
        }
    }

    // --- frame builders ---

    Frame makeFrame(const std::string& desc, StepType type = StepType::Done) const {
        Frame f;
        f.type = type;
        f.description = desc;

        // Emit all heap nodes with their array indices (for LayoutEngine placement)
        for (size_t i = 0; i < data_.size(); ++i) {
            FrameNode fn;
            fn.id = data_[i]->id;
            fn.value = data_[i]->value;
            fn.index = data_[i]->arrIndex;     // ← critical: used by LayoutEngine MinHeap branch
            if (i == 0) fn.sublabel = "根(最小)";
            f.nodes.push_back(fn);
        }

        // Emit edges: parent -> left child ("left"), parent -> right child ("right")
        for (size_t i = 0; i < data_.size(); ++i) {
            size_t left = 2 * i + 1;
            size_t right = 2 * i + 2;
            if (left < data_.size()) {
                FrameEdge fe;
                fe.fromId = data_[i]->id;
                fe.toId = data_[left]->id;
                fe.kind = "left";
                f.edges.push_back(fe);
            }
            if (right < data_.size()) {
                FrameEdge fe;
                fe.fromId = data_[i]->id;
                fe.toId = data_[right]->id;
                fe.kind = "right";
                f.edges.push_back(fe);
            }
        }

        return f;
    }

    Frame makeFrameWithHighlight(const std::string& desc,
                                 const std::vector<int>& hIds,
                                 StepType type = StepType::Done) const {
        Frame f = makeFrame(desc, type);
        f.highlightIds = hIds;
        return f;
    }
};

} // namespace dsv
