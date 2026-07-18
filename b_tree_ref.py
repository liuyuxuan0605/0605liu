"""
B-Tree reference implementation (min degree t=2 -> max 3 keys per node).
Used as the algorithm oracle: validate insert/delete invariants with random
workloads, then mirror the exact logic into C++ (src/core/BTree.h).
"""
import random

class BNode:
    __slots__ = ("keys", "children", "leaf")
    def __init__(self, leaf=True):
        self.keys = []
        self.children = []
        self.leaf = leaf

class BTree:
    def __init__(self, t=2):
        self.t = t
        self.root = BNode()

    # ---- search ----
    def search(self, node, k):
        i = 0
        while i < len(node.keys) and k > node.keys[i]:
            i += 1
        if i < len(node.keys) and node.keys[i] == k:
            return True
        if node.leaf:
            return False
        return self.search(node.children[i], k)

    # ---- insert ----
    def split_child(self, parent, i):
        t = self.t
        y = parent.children[i]
        z = BNode(y.leaf)
        mid = t - 1
        median = y.keys[mid]
        z.keys = y.keys[mid+1:]
        y.keys = y.keys[:mid]
        if not y.leaf:
            z.children = y.children[mid+1:]
            y.children = y.children[:mid+1]
        parent.keys.insert(i, median)
        parent.children.insert(i+1, z)

    def insert_non_full(self, node, k):
        i = len(node.keys) - 1
        if node.leaf:
            while i >= 0 and k < node.keys[i]:
                i -= 1
            node.keys.insert(i+1, k)
        else:
            while i >= 0 and k < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == 2*self.t - 1:
                self.split_child(node, i)
                if k > node.keys[i]:
                    i += 1
            self.insert_non_full(node.children[i], k)

    def insert(self, k):
        if self.search(self.root, k):
            return  # idempotent: ignore duplicates (teaching tool)
        r = self.root
        if len(r.keys) == 2*self.t - 1:
            s = BNode(leaf=False)
            s.children.append(r)
            self.root = s
            self.split_child(s, 0)
            self.insert_non_full(s, k)
        else:
            self.insert_non_full(r, k)

    # ---- delete helpers ----
    def min_key(self, node):
        while not node.leaf:
            node = node.children[0]
        return node.keys[0]

    def max_key(self, node):
        while not node.leaf:
            node = node.children[-1]
        return node.keys[-1]

    def borrow_from_prev(self, parent, i):
        child = parent.children[i]
        sibling = parent.children[i-1]
        child.keys.insert(0, parent.keys[i-1])
        parent.keys[i-1] = sibling.keys.pop()
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())

    def borrow_from_next(self, parent, i):
        child = parent.children[i]
        sibling = parent.children[i+1]
        child.keys.append(parent.keys[i])
        parent.keys[i] = sibling.keys.pop(0)
        if not child.leaf:
            child.children.append(sibling.children.pop(0))

    def merge(self, parent, i):
        child = parent.children[i]
        sibling = parent.children[i+1]
        child.keys.append(parent.keys.pop(i))
        child.keys.extend(sibling.keys)
        if not child.leaf:
            child.children.extend(sibling.children)
        parent.children.pop(i+1)

    def delete_node(self, node, k):
        t = self.t
        i = 0
        while i < len(node.keys) and k > node.keys[i]:
            i += 1
        if i < len(node.keys) and node.keys[i] == k:
            if node.leaf:
                node.keys.pop(i)
            else:
                if len(node.children[i].keys) >= t:
                    pred = self.max_key(node.children[i])
                    node.keys[i] = pred
                    self.delete_node(node.children[i], pred)
                elif len(node.children[i+1].keys) >= t:
                    succ = self.min_key(node.children[i+1])
                    node.keys[i] = succ
                    self.delete_node(node.children[i+1], succ)
                else:
                    self.merge(node, i)
                    self.delete_node(node.children[i], k)
        else:
            if node.leaf:
                return
            if len(node.children[i].keys) < t:
                if i > 0 and len(node.children[i-1].keys) >= t:
                    self.borrow_from_prev(node, i)
                elif i < len(node.children)-1 and len(node.children[i+1].keys) >= t:
                    self.borrow_from_next(node, i)
                else:
                    if i < len(node.children)-1:
                        self.merge(node, i)
                        recurse = i
                    else:
                        self.merge(node, i-1)
                        recurse = i-1
                    self.delete_node(node.children[recurse], k)
                    return
            self.delete_node(node.children[i], k)

    def delete(self, k):
        if not self.search(self.root, k):
            return False
        self.delete_node(self.root, k)
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]
        return True

    # ---- invariant checks ----
    def inorder(self, node):
        out = []
        if node.leaf:
            out.extend(node.keys)
        else:
            for i in range(len(node.keys)):
                out.extend(self.inorder(node.children[i]))
                out.append(node.keys[i])
            out.extend(self.inorder(node.children[-1]))
        return out

    def check(self):
        t = self.t
        errors = []
        # all keys sorted within every node
        def visit(node, lo, hi, depth, leaf_depths):
            for k in node.keys:
                if lo is not None and k <= lo: errors.append("key order lo")
                if hi is not None and k >= hi: errors.append("key order hi")
            # key count
            if node is not self.root:
                if len(node.keys) < t-1: errors.append("underflow")
                if len(node.keys) > 2*t-1: errors.append("overflow")
            else:
                if len(node.keys) > 2*t-1: errors.append("root overflow")
            if node.leaf:
                leaf_depths.append(depth)
            else:
                if len(node.children) != len(node.keys)+1:
                    errors.append("child count mismatch")
                for j, c in enumerate(node.children):
                    clo = lo if j == 0 else node.keys[j-1]
                    chi = hi if j == len(node.keys) else node.keys[j]
                    visit(c, clo, chi, depth+1, leaf_depths)
        leaf_depths = []
        visit(self.root, None, None, 0, leaf_depths)
        if len(set(leaf_depths)) > 1:
            errors.append("uneven leaf depths " + str(leaf_depths))
        return errors


def test():
    random.seed(1234)
    for trial in range(300):
        bt = BTree(t=2)
        ref = []
        ops = random.randint(1, 200)
        for _ in range(ops):
            if random.random() < 0.6 or not ref:
                v = random.randint(0, 40)
                bt.insert(v)
                if v not in ref:
                    ref.append(v)
            else:
                v = random.choice(ref)
                bt.delete(v)
                ref.remove(v)
            inv = bt.check()
            if inv:
                print(f"TRIAL {trial} FAIL invariants {inv}, ref={sorted(ref)}")
                return False
            got = bt.inorder(bt.root)
            if got != sorted(ref):
                print(f"TRIAL {trial} FAIL inorder {got} vs {sorted(ref)}")
                return False
    print("BTree reference: ALL 300 randomized trials passed (insert/delete invariants OK)")
    return True


if __name__ == "__main__":
    test()
