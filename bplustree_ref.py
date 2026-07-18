"""
B+Tree reference implementation (max 3 keys per node, min 1).
Validated with random insert/delete, then mirrored into C++ (src/core/BPlusTree.h).
Convention: internal keys are separators; separator[j] = min key of children[j+1].
All data lives in leaves; leaves are connected via an implicit chain (computed by
in-order traversal) -> emitted as "next" edges in the C++ frame generator.
"""
import random
import bisect

MAX = 3
MIN = 1  # underflow when keys.size() < MIN (i.e. 0)

class BPNode:
    __slots__ = ("keys", "children", "leaf")
    def __init__(self, leaf=False):
        self.keys = []
        self.children = []
        self.leaf = leaf

class BPlusTree:
    def __init__(self):
        self.root = BPNode(leaf=True)

    def search(self, k):
        node = self.root
        while not node.leaf:
            i = bisect.bisect_right(node.keys, k)
            node = node.children[i]
        return k in node.keys

    def _insert(self, node, k):
        if node.leaf:
            pos = bisect.bisect_left(node.keys, k)
            if pos < len(node.keys) and node.keys[pos] == k:
                return None  # duplicate ignored
            node.keys.insert(pos, k)
            if len(node.keys) > MAX:
                return self._split_leaf(node)
            return None
        i = bisect.bisect_right(node.keys, k)
        res = self._insert(node.children[i], k)
        if res:
            sep, newnode = res
            node.keys.insert(i, sep)
            node.children.insert(i + 1, newnode)
            if len(node.keys) > MAX:
                return self._split_internal(node)
        return None

    def _split_leaf(self, node):
        mid = (len(node.keys) + 1) // 2
        right = BPNode(leaf=True)
        right.keys = node.keys[mid:]
        node.keys = node.keys[:mid]
        sep = right.keys[0]
        return (sep, right)

    def _split_internal(self, node):
        mid = len(node.keys) // 2
        right = BPNode(leaf=False)
        sep = node.keys[mid]
        right.keys = node.keys[mid + 1:]
        right.children = node.children[mid + 1:]
        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]
        return (sep, right)

    def insert(self, k):
        if self.search(k):
            return
        res = self._insert(self.root, k)
        if res:
            sep, right = res
            newroot = BPNode(leaf=False)
            newroot.keys = [sep]
            newroot.children = [self.root, right]
            self.root = newroot

    def _delete(self, node, k):
        if node.leaf:
            if k in node.keys:
                node.keys.remove(k)
            return
        i = bisect.bisect_right(node.keys, k)
        self._delete(node.children[i], k)
        if len(node.children[i].keys) < MIN:
            self._fix_child(node, i)

    def _fix_child(self, parent, i):
        # Structural rebalance only; separators are recomputed by resync().
        def _assert_struct(n, path):
            if n.leaf:
                return
            if len(n.children) != len(n.keys) + 1:
                raise RuntimeError("STRUCT FAIL at %s: keys=%d children=%d %r"
                                   % (path, len(n.keys), len(n.children), n.keys))
            for c in n.children:
                _assert_struct(c, path + ">")
        child = parent.children[i]
        if i > 0 and len(parent.children[i - 1].keys) > MIN:
            left = parent.children[i - 1]
            if child.leaf:
                child.keys.insert(0, left.keys.pop())
            else:
                moved = left.children.pop()
                child.children.insert(0, moved)
                child.keys.insert(0, left.keys.pop())
        elif i < len(parent.children) - 1 and len(parent.children[i + 1].keys) > MIN:
            right = parent.children[i + 1]
            if child.leaf:
                child.keys.append(right.keys.pop(0))
            else:
                moved = right.children.pop(0)
                child.children.append(moved)
                child.keys.append(right.keys.pop(0))
        else:
            if i > 0:
                left = parent.children[i - 1]
                if not child.leaf:
                    left.keys.append(parent.keys[i - 1])   # internal: separator is data
                left.keys.extend(child.keys)               # leaf: no separator data
                if not child.leaf:
                    left.children.extend(child.children)
                parent.keys.pop(i - 1)              # drop separator between left & child
                parent.children.pop(i)
            else:
                right = parent.children[i + 1]
                if not child.leaf:
                    child.keys.append(parent.keys[i])      # internal: separator is data
                child.keys.extend(right.keys)              # leaf: no separator data
                if not child.leaf:
                    child.children.extend(right.children)
                parent.keys.pop(i)                  # drop separator between child & right
                parent.children.pop(i + 1)
        _assert_struct(parent, "parent")

    def resync(self):
        # Recompute every separator: separator[j] = min key of children[j+1].
        def fix(node):
            if node.leaf:
                return node.keys[0] if node.keys else None
            mins = [fix(c) for c in node.children]
            for j in range(len(node.keys)):
                node.keys[j] = mins[j + 1]
            return mins[0]
        if self.root.leaf:
            return
        fix(self.root)

    def delete(self, k):
        if not self.search(k):
            return False
        self._delete(self.root, k)
        if not self.root.leaf and len(self.root.keys) == 0:
            self.root = self.root.children[0]
        self.resync()
        return True

    # ---- invariant checks ----
    def subtree_min(self, node):
        while not node.leaf:
            node = node.children[0]
        return node.keys[0] if node.keys else None

    def leaf_chain(self):
        # in-order traversal of leaves -> list of leaf key-lists
        leaves = []
        def collect(node):
            if node.leaf:
                leaves.append(node.keys)
            else:
                for c in node.children:
                    collect(c)
        collect(self.root)
        return leaves

    def check(self):
        errors = []
        depths = []
        def visit(node, depth, is_root=False):
            if node.leaf:
                depths.append(depth)
                for j in range(len(node.keys) - 1):
                    if node.keys[j] >= node.keys[j + 1]:
                        errors.append("leaf not sorted")
                # empty root leaf is a valid empty tree
                if len(node.keys) < MIN and not (is_root and len(node.keys) == 0):
                    errors.append("leaf underflow " + str(node.keys))
            else:
                if len(node.children) != len(node.keys) + 1:
                    errors.append("internal child count")
                for j in range(len(node.keys)):
                    # separator[j] = min of children[j+1] = leftmost leaf's first key
                    mn = self.subtree_min(node.children[j + 1])
                    if mn is not None and node.keys[j] != mn:
                        errors.append("separator mismatch %r vs %r" % (node.keys[j], mn))
                for j in range(len(node.keys)):
                    visit(node.children[j], depth + 1)
                visit(node.children[-1], depth + 1)  # last child: no upper bound
        visit(self.root, 0, is_root=True)
        if len(set(depths)) > 1:
            errors.append("uneven leaf depths " + str(depths))
        chain = self.leaf_chain()
        flat = []
        for lf in chain:
            flat.extend(lf)
        if flat != sorted(flat):
            errors.append("chain not globally sorted " + str(flat))
        return errors


def test():
    random.seed(99)
    for trial in range(300):
        tree = BPlusTree()
        ref = []
        ops = random.randint(1, 200)
        for _ in range(ops):
            if random.random() < 0.6 or not ref:
                v = random.randint(0, 30)
                tree.insert(v)
                if v not in ref:
                    ref.append(v)
            else:
                v = random.choice(ref)
                tree.delete(v)
                ref.remove(v)
            inv = tree.check()
            if inv:
                print(f"TRIAL {trial} FAIL {inv}; ref={sorted(ref)}")
                return False
            chain = []
            for lf in tree.leaf_chain():
                chain.extend(lf)
            if chain != sorted(ref):
                print(f"TRIAL {trial} FAIL chain {chain} vs {sorted(ref)}")
                return False
    print("BPlusTree reference: ALL 300 randomized trials passed")
    return True


if __name__ == "__main__":
    test()
