#pragma once
#include "IDataStructure.h"
#include "SinglyLinkedList.h"
#include "DoublyLinkedList.h"
#include "Stack.h"
#include "Queue.h"
#include "BinarySearchTree.h"
#include "AVLTree.h"
#include "HashMap.h"
#include "MinHeap.h"
#include "RedBlackTree.h"
#include "Deque.h"
#include "BlockingQueue.h"
#include "BTree.h"
#include "BPlusTree.h"
#include "RingBuffer.h"
#include "Graph.h"
#include "LRUCache.h"
#include <memory>

namespace dsv {

// Build a concrete data structure by kind. Caller owns the unique_ptr.
inline std::unique_ptr<IDataStructure> createDataStructure(DSKind kind) {
    switch (kind) {
        case DSKind::SinglyLinkedList:  return std::make_unique<SinglyLinkedList>();
        case DSKind::DoublyLinkedList:  return std::make_unique<DoublyLinkedList>();
        case DSKind::Stack:             return std::make_unique<Stack>();
        case DSKind::Queue:             return std::make_unique<Queue>();
        case DSKind::BinarySearchTree:  return std::make_unique<BinarySearchTree>();
        case DSKind::AVLTree:           return std::make_unique<AVLTree>();
        case DSKind::HashMap:           return std::make_unique<HashMap>();
        case DSKind::MinHeap:           return std::make_unique<MinHeap>();
        case DSKind::RedBlackTree:       return std::make_unique<RedBlackTree>();
        case DSKind::Deque:              return std::make_unique<Deque>();
        case DSKind::BlockingQueue:      return std::make_unique<BlockingQueue>();
        case DSKind::BTree:              return std::make_unique<BTree>();          // default t=2 (max degree 4)
        case DSKind::BPlusTree:          return std::make_unique<BPlusTree>();      // default maxK=3
        case DSKind::RingBuffer:          return std::make_unique<RingBuffer>();
        case DSKind::Graph:               return std::make_unique<Graph>();
        case DSKind::LRUCache:            return std::make_unique<LRUCache>();
    }
    return nullptr;
}

// Overload with configurable degree for B-tree / B+tree.
// UI "Max Degree (阶)" = order m (textbook definition): a node holds at
// most m-1 keys / m children, i.e. "node data < m".
// For BTree / BPlusTree: maxK = degree - 1  (max keys per node).
// Other structures ignore this parameter.
inline std::unique_ptr<IDataStructure> createDataStructure(DSKind kind, int degree) {
    switch (kind) {
        case DSKind::BTree:     return std::make_unique<BTree>(degree - 1);     // maxK = degree-1
        case DSKind::BPlusTree: return std::make_unique<BPlusTree>(degree);     // degree = 阶 m
        default:                return createDataStructure(kind);                // fallback
    }
}

inline const char* kindToString(DSKind k) {
    switch (k) {
        case DSKind::SinglyLinkedList:  return "SinglyLinkedList";
        case DSKind::DoublyLinkedList:  return "DoublyLinkedList";
        case DSKind::Stack:             return "Stack";
        case DSKind::Queue:             return "Queue";
        case DSKind::BinarySearchTree:  return "BinarySearchTree";
        case DSKind::AVLTree:           return "AVLTree";
        case DSKind::HashMap:           return "HashMap";
        case DSKind::MinHeap:           return "MinHeap";
        case DSKind::RedBlackTree:       return "RedBlackTree";
        case DSKind::Deque:             return "Deque";
        case DSKind::BlockingQueue:      return "BlockingQueue";
        case DSKind::BTree:             return "BTree";
        case DSKind::BPlusTree:          return "BPlusTree";
        case DSKind::RingBuffer:          return "RingBuffer";
        case DSKind::Graph:               return "Graph";
        case DSKind::LRUCache:            return "LRUCache";
    }
    return "";
}

// AI 跳转用：把后端返回的字符串名（与 kindToString 完全对应）解析为 DSKind。
// 返回 false 表示无法识别（AI 可能返回了非法名），调用方应忽略。
inline bool kindFromString(const std::string& s, DSKind& out) {
    if (s == "SinglyLinkedList")       out = DSKind::SinglyLinkedList;
    else if (s == "DoublyLinkedList")  out = DSKind::DoublyLinkedList;
    else if (s == "Stack")             out = DSKind::Stack;
    else if (s == "Queue")             out = DSKind::Queue;
    else if (s == "BinarySearchTree")  out = DSKind::BinarySearchTree;
    else if (s == "AVLTree")           out = DSKind::AVLTree;
    else if (s == "HashMap")           out = DSKind::HashMap;
    else if (s == "MinHeap")           out = DSKind::MinHeap;
    else if (s == "RedBlackTree")      out = DSKind::RedBlackTree;
    else if (s == "Deque")             out = DSKind::Deque;
    else if (s == "BlockingQueue")     out = DSKind::BlockingQueue;
    else if (s == "BTree")             out = DSKind::BTree;
    else if (s == "BPlusTree")         out = DSKind::BPlusTree;
    else if (s == "RingBuffer")        out = DSKind::RingBuffer;
    else if (s == "Graph")             out = DSKind::Graph;
    else if (s == "LRUCache")          out = DSKind::LRUCache;
    else return false;
    return true;
}

} // namespace dsv
