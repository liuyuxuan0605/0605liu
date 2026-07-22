# -*- coding: utf-8 -*-
# 正确的包容式(inclusive) B+ 树删除：
# 删除内部键 v(=右孩子最左叶首键副本)时：
#   1) 把右孩子最左叶首位的 v 换成 predecessor(左子树最大叶键)
#   2) 内部键 v 也改成 predecessor
#   3) 从左侧叶子递归删除 predecessor(可能引发下溢修复)
#   4) resync 把所有层级的 v 副本统一更新为 predecessor
import random

class BPlusTreeInc:
    def __init__(self, degree=3):
        self.degree = degree
        self.maxK = degree - 1
        self.minK = (degree + 1) // 2 - 1
        self.splitIdx = (degree - 1) // 2
        self.root = None
        self.nid = 0

    class Node:
        def __init__(self, i, leaf=True):
            self.nid = i; self.keys = []; self.children = []; self.is_leaf = leaf; self.next = None
    def new_node(self, leaf=True):
        n = self.Node(self.nid, leaf); self.nid += 1; return n

    def insert(self, v):
        if self.root is None:
            self.root = self.new_node(True); self.root.keys = [v]; return
        sep, right = self._insert(self.root, v)
        if right:
            nr = self.new_node(False)
            nr.keys = [sep]; nr.children = [self.root, right]
            self.root = nr
        self.resync()  # 维持包容式不变式: 所有分隔符 = 右孩子最左叶首键副本

    def _insert(self, n, v):
        if n.is_leaf:
            i = 0
            while i < len(n.keys) and n.keys[i] < v: i += 1
            if i < len(n.keys) and n.keys[i] == v: return None, None
            n.keys.insert(i, v)
            if len(n.keys) > self.maxK:
                return self._split_leaf(n)
            return None, None
        else:
            i = 0
            while i < len(n.keys) and v >= n.keys[i]: i += 1
            sep, right = self._insert(n.children[i], v)
            if right:
                n.keys.insert(i, sep); n.children.insert(i + 1, right)
                if len(n.keys) > self.maxK:
                    return self._split_internal(n)
            return None, None

    def _split_leaf(self, n):
        r = self.new_node(True)
        r.keys = n.keys[self.splitIdx:]
        n.keys = n.keys[:self.splitIdx]
        r.next = n.next; n.next = r
        return r.keys[0], r

    def _split_internal(self, n):
        r = self.new_node(False)
        sep = n.keys[self.splitIdx]
        r.keys = n.keys[self.splitIdx + 1:]
        n.keys = n.keys[:self.splitIdx]
        r.children = n.children[self.splitIdx + 1:]
        n.children = n.children[:self.splitIdx + 1]
        return sep, r

    def search(self, v):
        n = self.root
        while n and not n.is_leaf:
            i = 0
            while i < len(n.keys) and v >= n.keys[i]: i += 1
            n = n.children[i]
        return n is not None and v in n.keys

    def remove(self, v):
        if not self.search(v): return False
        self._delete(self.root, v)
        if not self.root.is_leaf and len(self.root.keys) == 0:
            self.root = self.root.children[0]
        self.resync()
        return True

    def _max_leaf_key(self, n):
        while not n.is_leaf: n = n.children[-1]
        return n.keys[-1]
    def _leftmost_leaf(self, n):
        while not n.is_leaf: n = n.children[0]
        return n

    def _delete(self, n, v):
        if n.is_leaf:
            if v in n.keys:
                n.keys.remove(v); return True
            return False
        i = 0
        while i < len(n.keys) and v > n.keys[i]: i += 1
        if i < len(n.keys) and n.keys[i] == v:
            # v 是内部分隔符(包容式: =右孩子最左叶首键副本)
            pred = self._max_leaf_key(n.children[i])
            rleaf = self._leftmost_leaf(n.children[i + 1])
            rleaf.keys[0] = pred          # 把右叶首位的 v 副本换成 pred
            n.keys[i] = pred              # 内部键也改成 pred
            deleted = self._delete(n.children[i], pred)  # 从左子树删 pred
            if deleted: self._fix_child(n, i)
            return True
        else:
            deleted = self._delete(n.children[i], v)
            if deleted: self._fix_child(n, i)
            return deleted

    def _fix_child(self, parent, i):
        child = parent.children[i]
        if len(child.keys) >= self.minK or child == self.root: return
        if i > 0 and len(parent.children[i-1].keys) > self.minK:
            self._borrow_from_left(parent, i)
        elif i + 1 < len(parent.children) and len(parent.children[i+1].keys) > self.minK:
            self._borrow_from_right(parent, i)
        else:
            if i > 0: self._merge_with_left(parent, i)
            else: self._merge_with_right(parent, i)

    def _borrow_from_left(self, parent, i):
        child = parent.children[i]; left = parent.children[i-1]
        if child.is_leaf:
            child.keys.insert(0, left.keys[-1]); left.keys.pop()
            parent.keys[i-1] = child.keys[0]
        else:
            child.keys.insert(0, parent.keys[i-1])
            parent.keys[i-1] = left.keys[-1]; left.keys.pop()
            child.children.insert(0, left.children.pop())

    def _borrow_from_right(self, parent, i):
        child = parent.children[i]; right = parent.children[i+1]
        if child.is_leaf:
            child.keys.append(right.keys[0]); right.keys.pop(0)
            parent.keys[i] = right.keys[0] if right.keys else ""
        else:
            child.keys.append(parent.keys[i]); parent.keys[i] = right.keys[0]
            right.keys.pop(0); child.children.append(right.children.pop(0))

    def _merge_with_left(self, parent, i):
        child = parent.children[i]; left = parent.children[i-1]
        sep = parent.keys[i-1]
        parent.keys.pop(i-1); parent.children.pop(i)
        if not child.is_leaf: left.keys.append(sep)
        left.keys.extend(child.keys)
        if not child.is_leaf: left.children.extend(child.children)

    def _merge_with_right(self, parent, i):
        child = parent.children[i]; right = parent.children[i+1]
        sep = parent.keys[i]
        parent.keys.pop(i); parent.children.pop(i+1)
        if not child.is_leaf: child.keys.append(sep)
        child.keys.extend(right.keys)
        if not child.is_leaf: child.children.extend(right.children)

    def resync(self):
        def rec(n):
            if n.is_leaf: return n.keys[0] if n.keys else None
            mins = [rec(c) for c in n.children]
            for j in range(len(n.keys)):
                n.keys[j] = mins[j+1] if j+1 < len(mins) else n.keys[j]
            return mins[0] if mins else None
        if self.root: rec(self.root)

    def validate(self, expect_set=None):
        if self.root is None:
            if expect_set is not None and len(expect_set) != 0:
                return False, "empty but expect non-empty"
            return True, "ok"
        E = []
        def chk(n, d):
            if n != self.root and len(n.keys) < self.minK:
                E.append(f"@d{d} DEFICIENT {len(n.keys)}<{self.minK}")
            if len(n.keys) > self.maxK:
                E.append(f"@d{d} OVERFLOW {len(n.keys)}>{self.maxK}")
            if not n.is_leaf:
                if len(n.children) != len(n.keys)+1: E.append(f"@d{d} ch!=k+1")
                for j in range(len(n.keys)):
                    ln = n.children[j]; lm = ln
                    while not lm.is_leaf: lm = lm.children[-1]
                    lmax = lm.keys[-1] if lm.keys else None
                    rn = n.children[j+1]; rm = rn
                    while not rm.is_leaf: rm = rm.children[0]
                    rmin = rm.keys[0] if rm.keys else None
                    if lmax is not None and lmax >= n.keys[j]: E.append(f"sep[{j}]={n.keys[j]}<=lmax={lmax}")
                    if rmin is not None and n.keys[j] > rmin: E.append(f"sep[{j}]={n.keys[j]}>rmin={rmin}")
                for c in n.children: chk(c, d+1)
        chk(self.root, 0)
        ld = []
        def coll(n):
            if n.is_leaf: ld.extend(n.keys)
            else:
                for c in n.children: coll(c)
        coll(self.root)
        for i in range(len(ld)-1):
            if ld[i] >= ld[i+1]: E.append(f"leaf order @{i}")
        if len(ld) != len(set(ld)): E.append("dup in leaves")
        if expect_set is not None and set(ld) != expect_set:
            E.append(f"DATA LOSS/EXTRA: leaf={sorted(set(ld))[:6]}.. expect={sorted(expect_set)[:6]}..")
        return len(E)==0, "; ".join(E[:5]) if E else "ok"

    def shape(self):
        def rec(n, d=0):
            s = "  "*d + ("L" if n.is_leaf else "N") + str(n.keys)
            if not n.is_leaf: s += " ch=" + str(len(n.children))
            s += "\n"
            if not n.is_leaf:
                for c in n.children: s += rec(c, d+1)
            return s
        return rec(self.root) if self.root else "empty"


# 验证
print("=== 插入+删除联合验证 (inclusive 正确删除 + 数据完整性) ===")
for deg in [3,4,5,6,7]:
    ok = 0
    for _ in range(300):
        t = BPlusTreeInc(deg)
        pool = list(range(1,101)); inserted = []
        for step in range(60):
            if pool and (not inserted or random.random() < 0.6):
                v = random.choice(pool); pool.remove(v); inserted.append(v); t.insert(v)
            elif inserted:
                v = random.choice(inserted); inserted.remove(v); pool.append(v); t.remove(v)
        if t.validate(set(inserted))[0]: ok += 1
    print(f"  degree={deg}: {ok}/300 通过")

# 用户示例 (degree 5, 与参考图一致)
t = BPlusTreeInc(5)
for v in [1,2,4,6,10,15,20,21,42,60,100]:
    t.insert(v)
print("\n插入后:")
print(t.shape())
print("valid:", t.validate())
t.remove(15)
print("删除15后:")
print(t.shape())
print("valid:", t.validate())
