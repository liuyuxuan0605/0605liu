# -*- coding: utf-8 -*-
"""
红黑树 插入+删除 忠实逻辑测试（验证算法/RB 不变量正确性）。
注意：Python 无 unique_ptr，内存安全由 C++ 中遵守“move 前捕获裸指针”保证；
本测试只验证：删除后树仍满足全部红黑树性质 + BST 有序 + 父指针一致。

端口严格对应 RedBlackTree.h 的 insert / remove / fixInsert / fixDelete / transplant。
"""
import random

RED, BLACK = 'R', 'B'

class RB:
    _id = 0
    def __init__(self):
        self.root = None
        self.size = 0

    class Node:
        def __init__(self, v, color=RED):
            RB._id += 1
            self.id = RB._id
            self.value = v
            self.color = color
            self.left = None
            self.right = None
            self.parent = None

    @staticmethod
    def cmp(a, b):
        try:
            return (int(a) > int(b)) - (int(a) < int(b))
        except:
            return (a > b) - (a < b)

    # ---------- 旋转（对应 rotateLeft/rotateRight + rotateLeftAt/rotateRightAt）----------
    @staticmethod
    def rotateLeft(x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        y.parent = x.parent
        x.parent = y
        if T2: T2.parent = x
        return y
    @staticmethod
    def rotateRight(y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        x.parent = y.parent
        y.parent = x
        if T2: T2.parent = y
        return x
    def rotateLeftAt(self, x):
        p = x.parent
        isLeft = p and (p.left is x)
        if p is None: sub = self.root
        elif isLeft: sub = p.left
        else: sub = p.right
        sub = self.rotateLeft(sub)
        if p is None: self.root = sub
        elif isLeft: p.left = sub
        else: p.right = sub
        return sub
    def rotateRightAt(self, y):
        p = y.parent
        isLeft = p and (p.left is y)
        if p is None: sub = self.root
        elif isLeft: sub = p.left
        else: sub = p.right
        sub = self.rotateRight(sub)
        if p is None: self.root = sub
        elif isLeft: p.left = sub
        else: p.right = sub
        return sub

    # ---------- fixInsert ----------
    def fixInsert(self, z):
        while z.parent and z.parent.color == RED:
            gp = z.parent.parent
            if gp is None: break
            if z.parent is gp.left:
                uncle = gp.right
                if uncle and uncle.color == RED:
                    z.parent.color = BLACK; uncle.color = BLACK; gp.color = RED
                    z = gp
                else:
                    if z is z.parent.right:
                        z = z.parent
                        self.rotateLeftAt(z)
                    z.parent.color = BLACK; gp.color = RED
                    self.rotateRightAt(gp)
            else:
                uncle = gp.left
                if uncle and uncle.color == RED:
                    z.parent.color = BLACK; uncle.color = BLACK; gp.color = RED
                    z = gp
                else:
                    if z is z.parent.left:
                        z = z.parent
                        self.rotateRightAt(z)
                    z.parent.color = BLACK; gp.color = RED
                    self.rotateLeftAt(gp)
        if self.root: self.root.color = BLACK

    # ---------- insert ----------
    def insert(self, value):
        if self.root is None:
            self.root = RB.Node(value, BLACK)
            self.size = 1
            return
        parent = None; cur = self.root
        while cur:
            c = self.cmp(value, cur.value)
            if c == 0: return
            parent = cur
            cur = cur.left if c < 0 else cur.right
        n = RB.Node(value, RED)
        n.parent = parent
        if self.cmp(value, parent.value) < 0: parent.left = n
        else: parent.right = n
        self.fixInsert(n)
        self.size += 1

    # ---------- delete ----------
    @staticmethod
    def colorOf(n):
        return n.color if n else BLACK

    def transplant(self, u, v):
        if u.parent is None: self.root = v
        elif u.parent.left is u: u.parent.left = v
        else: u.parent.right = v
        if v: v.parent = u.parent
        # 模拟 C++ 中 u 被析构：脱离
        u.parent = None; u.left = None; u.right = None

    def deleteOneChild(self, target):
        orig = target.color
        if target.left is None:
            x = target.right
            xp = target.parent
            xIsLeft = (xp and xp.left is target)
            self.transplant(target, target.right)
        else:
            x = target.left
            xp = target.parent
            xIsLeft = (xp and xp.left is target)
            self.transplant(target, target.left)
        if orig == BLACK:
            self.fixDelete(x, xp, xIsLeft)

    def fixDelete(self, x, xp, xIsLeft):
        if self.root is None: return
        while x is not self.root and self.colorOf(x) == BLACK:
            if xp is None: break
            if xIsLeft:
                w = xp.right
                if self.colorOf(w) == RED:
                    w.color = BLACK; xp.color = RED
                    self.rotateLeftAt(xp)
                    w = xp.right
                if self.colorOf(w.left if w else None) == BLACK and self.colorOf(w.right if w else None) == BLACK:
                    if w: w.color = RED
                    x = xp
                    if x is self.root: break
                    xp = x.parent
                    xIsLeft = (xp and xp.left is x)
                else:
                    if self.colorOf(w.right if w else None) == BLACK:
                        if w and w.left: w.left.color = BLACK
                        if w: w.color = RED
                        self.rotateRightAt(w)
                        w = xp.right
                    if w: w.color = xp.color if xp else BLACK
                    if xp: xp.color = BLACK
                    if w and w.right: w.right.color = BLACK
                    self.rotateLeftAt(xp)
                    x = self.root
            else:
                w = xp.left
                if self.colorOf(w) == RED:
                    w.color = BLACK; xp.color = RED
                    self.rotateRightAt(xp)
                    w = xp.left
                if self.colorOf(w.left if w else None) == BLACK and self.colorOf(w.right if w else None) == BLACK:
                    if w: w.color = RED
                    x = xp
                    if x is self.root: break
                    xp = x.parent
                    xIsLeft = (xp and xp.left is x)
                else:
                    if self.colorOf(w.left if w else None) == BLACK:
                        if w and w.right: w.right.color = BLACK
                        if w: w.color = RED
                        self.rotateLeftAt(w)
                        w = xp.left
                    if w: w.color = xp.color if xp else BLACK
                    if xp: xp.color = BLACK
                    if w and w.left: w.left.color = BLACK
                    self.rotateRightAt(xp)
                    x = self.root
        if x: x.color = BLACK

    def remove(self, value):
        z = self.root
        while z:
            c = self.cmp(value, z.value)
            if c == 0: break
            z = z.left if c < 0 else z.right
        if z is None: return
        self.size -= 1
        if z.left and z.right:
            succ = z.right
            while succ.left: succ = succ.left
            z.value = succ.value
            self.deleteOneChild(succ)
        else:
            self.deleteOneChild(z)
        if self.root: self.root.color = BLACK

    # ---------- 校验 ----------
    def validate(self):
        errs = []
        if self.root and self.root.color != BLACK:
            errs.append("根非黑")
        # BST + 父指针 + 红不连红 + 黑高
        def bh(n):
            if n is None: return 1
            if n.left and (self.cmp(n.left.value, n.value) >= 0): errs.append(f"BST 违反 {n.value}<-{n.left.value}")
            if n.right and (self.cmp(n.right.value, n.value) <= 0): errs.append(f"BST 违反 {n.value}->{n.right.value}")
            if n.parent is None and n is not self.root: errs.append(f"父指针错误(应为根) {n.value}")
            if n.parent and n is not n.parent.left and n is not n.parent.right:
                errs.append(f"父指针不一致 {n.value}")
            if n.color == RED:
                if (n.left and n.left.color == RED) or (n.right and n.right.color == RED):
                    errs.append(f"红连红 {n.value}")
            l = bh(n.left); r = bh(n.right)
            if l != r: errs.append(f"黑高不一致 at {n.value}: L={l} R={r}")
            return l + (0 if n.color == RED else 1)
        bh(self.root)
        return errs

# ---------------- 测试 ----------------
def test_known():
    # 已知序列：构造一棵含旋转的树，再删除若干节点
    t = RB()
    for v in ["10","20","30","15","25","5","1"]:
        t.insert(v)
    e = t.validate()
    if e: return False, f"插入后校验失败: {e[:3]}"
    for v in ["10","30","15"]:
        t.remove(v)
        e = t.validate()
        if e: return False, f"删除 {v} 后校验失败: {e[:3]}"
    return True, "已知序列通过"

def test_random(n_rounds=3000, max_ops=50):
    for r in range(n_rounds):
        t = RB()
        present = set()
        ops = random.randint(5, max_ops)
        for _ in range(ops):
            v = str(random.randint(0, 60))
            if random.random() < 0.55:
                t.insert(v); present.add(v)
            else:
                t.remove(v); present.discard(v)
            e = t.validate()
            if e:
                return False, f"回合{r} 校验失败: {e[:3]}"
        # 一致性：size == len(present)（按（值,出现次数）？这里允许重复值吗？）
        # 本项目按值唯一（compareValues==0 视为已存在），故 size==len(present)
        if t.size != len(present):
            return False, f"回合{r} size={t.size} 但理论={len(present)}"
        # 中序应等于 sorted(present)
        vals = []
        def io(n):
            if n: io(n.left); vals.append(n.value); io(n.right)
        io(t.root)
        if vals != sorted(present, key=lambda x:(int(x),x)):
            return False, f"回合{r} 中序与理论集合不一致"
    return True, f"{n_rounds} 回合随机插入/删除全部通过"

if __name__ == "__main__":
    ok1, m1 = test_known()
    print("已知序列:", "PASS" if ok1 else "FAIL", "-", m1)
    ok2, m2 = test_random()
    print("随机混合:", "PASS" if ok2 else "FAIL", "-", m2)
    print("OVERALL:", "ALL PASS" if (ok1 and ok2) else "HAS FAILURE")
