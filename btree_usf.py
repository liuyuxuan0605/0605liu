#!/usr/bin/env python3
"""USF-style B-Tree (default mode): predecessor replacement for internal deletion."""
import random

class Node:
    __slots__ = ('keys','children','leaf')
    def __init__(self, leaf=True):
        self.keys = []
        self.children = []
        self.leaf = leaf
    def __repr__(self):
        return f"{'L' if self.leaf else 'N'}{self.keys}"

class BTree:
    def __init__(self, order):
        self.order = order
        self.maxK = order - 1
        self.minK = self.maxK // 2   # = ceil(order/2) - 1, matches USF
        self.root = Node()

    def insert(self, v):
        promoted, right = self._insert(self.root, v)
        if right:
            nr = Node(leaf=False)
            nr.keys = [promoted]
            nr.children = [self.root, right]
            self.root = nr

    def _insert(self, n, v):
        if n.leaf:
            i = 0
            while i < len(n.keys) and n.keys[i] < v:
                i += 1
            if i < len(n.keys) and n.keys[i] == v:
                return None, None  # duplicate
            n.keys.insert(i, v)
            if len(n.keys) > self.maxK:
                return self._split(n)
            return None, None
        i = 0
        while i < len(n.keys) and v > n.keys[i]:
            i += 1
        if i < len(n.keys) and v == n.keys[i]:
            return None, None  # duplicate
        promoted, right = self._insert(n.children[i], v)
        if right:
            n.keys.insert(i, promoted)
            n.children.insert(i + 1, right)
            if len(n.keys) > self.maxK:
                return self._split(n)
        return None, None

    def _split(self, n):
        # B-tree split: median index = maxK // 2 (lower median, keeps left smaller)
        mid = self.maxK // 2
        sep = n.keys[mid]
        r = Node(leaf=n.leaf)
        r.keys = n.keys[mid + 1:]
        n.keys = n.keys[:mid]
        if not n.leaf:
            r.children = n.children[mid + 1:]
            n.children = n.children[:mid + 1]
        return sep, r

    def remove(self, v):
        res = self._delete(self.root, v)
        if res:
            promoted, right = res
            nr = Node(leaf=False)
            nr.keys = [promoted]
            nr.children = [self.root, right]
            self.root = nr
        if not self.root.leaf and len(self.root.keys) == 0:
            self.root = self.root.children[0]

    def _delete(self, n, v):
        """递归删除 v，若当前节点 overflow 则返回 (promoted_key, right_node)。"""
        i = 0
        while i < len(n.keys) and v > n.keys[i]:
            i += 1

        if i < len(n.keys) and n.keys[i] == v:
            if n.leaf:
                n.keys.pop(i)
            else:
                # USF default: always predecessor replacement
                pred = self._max_key(n.children[i])
                n.keys[i] = pred
                res = self._delete(n.children[i], pred)
                if res:
                    pmed, pright = res
                    n.keys.insert(i, pmed)
                    n.children.insert(i + 1, pright)
        else:
            if n.leaf:
                return None  # not present
            res = self._delete(n.children[i], v)
            if res:
                pmed, pright = res
                n.keys.insert(i, pmed)
                n.children.insert(i + 1, pright)

        # After recursion, repair child i if it underflowed
        if not n.leaf:
            self._repair_child(n, i)

        if len(n.keys) > self.maxK:
            return self._split(n)
        return None

    def _max_key(self, n):
        while not n.leaf:
            n = n.children[-1]
        return n.keys[-1]

    def _repair_child(self, parent, i):
        child = parent.children[i]
        if len(child.keys) >= self.minK:
            return
        if child is self.root:
            return  # root may underflow

        left_sib = parent.children[i - 1] if i > 0 else None
        right_sib = parent.children[i + 1] if i + 1 < len(parent.children) else None

        # Try borrow from left
        if left_sib and len(left_sib.keys) > self.minK:
            sep = parent.keys[i - 1]
            child.keys.insert(0, sep)
            parent.keys[i - 1] = left_sib.keys.pop()
            if not child.leaf:
                child.children.insert(0, left_sib.children.pop())
            return

        # Try borrow from right
        if right_sib and len(right_sib.keys) > self.minK:
            sep = parent.keys[i]
            child.keys.append(sep)
            parent.keys[i] = right_sib.keys.pop(0)
            if not child.leaf:
                child.children.append(right_sib.children.pop(0))
            return

        # Must merge (even order may overflow -> cascade split)
        if left_sib:
            sep = parent.keys[i - 1]
            left_sib.keys.append(sep)
            left_sib.keys.extend(child.keys)
            if not left_sib.leaf:
                left_sib.children.extend(child.children)
            parent.keys.pop(i - 1)
            parent.children.pop(i)
            if len(left_sib.keys) > self.maxK:
                # split left_sib (now at position i-1 in parent.children)
                mid = len(left_sib.keys) // 2
                promoted = left_sib.keys[mid]
                r = Node(leaf=left_sib.leaf)
                r.keys = left_sib.keys[mid + 1:]
                left_sib.keys = left_sib.keys[:mid]
                if not left_sib.leaf:
                    r.children = left_sib.children[mid + 1:]
                    left_sib.children = left_sib.children[:mid + 1]
                parent.keys.insert(i - 1, promoted)
                parent.children.insert(i, r)
        else:
            sep = parent.keys[i]
            child.keys.append(sep)
            child.keys.extend(right_sib.keys)
            if not child.leaf:
                child.children.extend(right_sib.children)
            parent.keys.pop(i)
            parent.children.pop(i + 1)
            if len(child.keys) > self.maxK:
                # split child (still at position i in parent.children)
                mid = len(child.keys) // 2
                promoted = child.keys[mid]
                r = Node(leaf=child.leaf)
                r.keys = child.keys[mid + 1:]
                child.keys = child.keys[:mid]
                if not child.leaf:
                    r.children = child.children[mid + 1:]
                    child.children = child.children[:mid + 1]
                parent.keys.insert(i, promoted)
                parent.children.insert(i + 1, r)

    def shape(self):
        lines = []
        def walk(n, d):
            lines.append("  " * d + str(n))
            if not n.leaf:
                for c in n.children:
                    walk(c, d + 1)
        walk(self.root, 0)
        return "\n".join(lines)

    def inorder_values(self):
        out = []
        def walk(n):
            if n.leaf:
                out.extend(n.keys)
            else:
                for i in range(len(n.keys)):
                    walk(n.children[i])
                    out.append(n.keys[i])
                walk(n.children[-1])
        walk(self.root)
        return out

    def validate(self, expect_set=None):
        E = []
        def chk(n, d):
            if n is not self.root and len(n.keys) < self.minK:
                E.append(f"deficient d={d} keys={len(n.keys)}")
            if len(n.keys) > self.maxK:
                E.append(f"overflow d={d} keys={len(n.keys)}")
            if not n.leaf:
                if len(n.children) != len(n.keys) + 1:
                    E.append(f"children mismatch")
                for j in range(len(n.keys)):
                    lmax = self._sub_max(n.children[j])
                    rmin = self._sub_min(n.children[j+1])
                    if lmax is not None and lmax >= n.keys[j]:
                        E.append(f"sep {n.keys[j]} <= lmax {lmax}")
                    if rmin is not None and rmin < n.keys[j]:
                        E.append(f"sep {n.keys[j]} > rmin {rmin}")
                for c in n.children:
                    chk(c, d + 1)
        chk(self.root, 0)
        iv = self.inorder_values()
        if any(iv[i] >= iv[i+1] for i in range(len(iv)-1)):
            E.append(f"inorder order: {iv[:10]}")
        if len(iv) != len(set(iv)):
            E.append("dup keys")
        if expect_set is not None and set(iv) != expect_set:
            E.append(f"data mismatch iv={sorted(set(iv))[:8]} expect={sorted(expect_set)[:8]}")
        return len(E) == 0, "; ".join(E[:5])

    def _sub_max(self, n):
        while not n.leaf:
            n = n.children[-1]
        return n.keys[-1] if n.keys else None
    def _sub_min(self, n):
        while not n.leaf:
            n = n.children[0]
        return n.keys[0] if n.keys else None


# 用户示例
print("=== 用户示例：order=5，删 15 ===")
t = BTree(5)
for v in [4, 15, 42, 1, 2, 6, 10, 20, 21, 60, 100]:
    t.insert(v)
print("初始：")
print(t.shape())
t.remove(15)
print("\n删除 15 后：")
print(t.shape())
print("验证:", t.validate(set([1,2,4,6,10,20,21,42,60,100])))
print("中序:", t.inorder_values())

print("\n=== 随机插删验证 ===")
for order in [3, 4, 5, 6, 7]:
    ok = 0
    for _ in range(300):
        t = BTree(order)
        pool = list(range(1, 101)); ins = []
        for step in range(60):
            if pool and (not ins or random.random() < 0.6):
                v = random.choice(pool); pool.remove(v); ins.append(v); t.insert(v)
            elif ins:
                v = random.choice(ins); ins.remove(v); pool.append(v); t.remove(v)
        if t.validate(set(ins))[0]:
            ok += 1
    print(f"  order={order}: {ok}/300")
