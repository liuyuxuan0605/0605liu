# -*- coding: utf-8 -*-
"""
AVL 忠实逻辑测试（验证算法正确性，不含 unique_ptr 内存安全——
内存安全已由 C++ 中 rotate 函数改用裸指针捕获保证）。
重点验证：插入/删除触发旋转后，树仍满足 BST 性质 + AVL 平衡 + 高度一致。
"""
import random

class AVL:
    _id = 0
    def __init__(self):
        self.root = None
        self.size = 0

    class Node:
        def __init__(self, v):
            AVL._id += 1
            self.id = AVL._id
            self.value = v
            self.height = 1
            self.left = None
            self.right = None

    @staticmethod
    def h(n):
        return n.height if n else 0
    @staticmethod
    def upd(n):
        if n: n.height = 1 + max(AVL.h(n.left), AVL.h(n.right))
    @staticmethod
    def bal(n):
        return AVL.h(n.left) - AVL.h(n.right) if n else 0

    # 与 C++ rotateRight 同构（裸指针版逻辑等价）
    @staticmethod
    def rotateRight(y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        AVL.upd(y); AVL.upd(x)
        return x
    @staticmethod
    def rotateLeft(x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        AVL.upd(x); AVL.upd(y)
        return y

    def insertRec(self, node, value, added):
        if node is None:
            added[0] = True
            return AVL.Node(value)
        c = self.cmp(value, node.value)
        if c == 0:
            return node
        if c < 0:
            node.left = self.insertRec(node.left, value, added)
        else:
            node.right = self.insertRec(node.right, value, added)
        AVL.upd(node)
        b = AVL.bal(node)
        if b > 1 and AVL.bal(node.left) >= 0:
            return AVL.rotateRight(node)
        if b > 1 and AVL.bal(node.left) < 0:
            node.left = AVL.rotateLeft(node.left)
            return AVL.rotateRight(node)
        if b < -1 and AVL.bal(node.right) <= 0:
            return AVL.rotateLeft(node)
        if b < -1 and AVL.bal(node.right) > 0:
            node.right = AVL.rotateRight(node.right)
            return AVL.rotateLeft(node)
        return node

    def removeRec(self, node, value, removed):
        if node is None:
            return None
        c = self.cmp(value, node.value)
        if c < 0:
            node.left = self.removeRec(node.left, value, removed)
        elif c > 0:
            node.right = self.removeRec(node.right, value, removed)
        else:
            removed[0] = True
            if node.left is None or node.right is None:
                child = node.left if node.left else node.right
                return child
            # 双子节点：找右子树最小（中序后继），递归删除后继
            succ = node.right
            while succ.left: succ = succ.left
            node.value = succ.value
            node.right = self.removeRec(node.right, succ.value, removed)
        AVL.upd(node)
        b = AVL.bal(node)
        if b > 1 and AVL.bal(node.left) >= 0:
            return AVL.rotateRight(node)
        if b > 1 and AVL.bal(node.left) < 0:
            node.left = AVL.rotateLeft(node.left)
            return AVL.rotateRight(node)
        if b < -1 and AVL.bal(node.right) <= 0:
            return AVL.rotateLeft(node)
        if b < -1 and AVL.bal(node.right) > 0:
            node.right = AVL.rotateRight(node.right)
            return AVL.rotateLeft(node)
        return node

    @staticmethod
    def cmp(a, b):
        try:
            return (int(a) > int(b)) - (int(a) < int(b))
        except:
            return (a > b) - (a < b)

    def insert(self, v):
        added = [False]
        self.root = self.insertRec(self.root, v, added)
        if added[0]: self.size += 1
    def remove(self, v):
        removed = [False]
        self.root = self.removeRec(self.root, v, removed)
        if removed[0]: self.size -= 1

    # ---------- 校验 ----------
    def validate(self):
        errs = []
        def check(n, lo, hi):
            if n is None: return 0
            if (lo is not None and self.cmp(n.value, lo) <= 0) or (hi is not None and self.cmp(n.value, hi) >= 0):
                errs.append(f"BST 性质违反 at {n.value} (范围 {lo},{hi})")
            lh = check(n.left, lo, n.value)
            rh = check(n.right, n.value, hi)
            if abs(lh - rh) > 1:
                errs.append(f"AVL 平衡违反 at {n.value}: L={lh} R={rh}")
            if n.height != 1 + max(lh, rh):
                errs.append(f"高度不一致 at {n.value}: 存={n.height} 算={1+max(lh,rh)}")
            return 1 + max(lh, rh)
        check(self.root, None, None)
        return errs

# ---------------- 测试 ----------------
def test_known_sequences():
    cases = [
        ["11","14","12"],                 # RL 触发
        ["30","50","40"],                 # RL 触发
        ["10","20","30"],                 # RR 触发
        ["30","20","10"],                 # LL 触发
        ["10","30","20"],                 # LR 触发
        ["50","30","70","20","40","60","80","10","25"],
    ]
    for seq in cases:
        t = AVL()
        for v in seq:
            t.insert(v)
            e = t.validate()
            if e:
                return False, f"序列 {seq} 插入 {v} 后校验失败: {e[:3]}"
    return True, "已知序列全部通过"

def test_random(n_rounds=2000, max_vals=40):
    for r in range(n_rounds):
        t = AVL()
        present = set()
        ops = random.randint(5, max_vals)
        for _ in range(ops):
            v = str(random.randint(0, 99))
            if random.random() < 0.62:
                t.insert(v); present.add(v)
            else:
                t.remove(v); present.discard(v)
            e = t.validate()
            if e:
                return False, f"回合{r} 校验失败: {e[:3]}"
        # 结构校验：size 与 present 一致
        # （用 inorder 收集值）
        vals = []
        def io(n):
            if n: io(n.left); vals.append(n.value); io(n.right)
        io(t.root)
        if vals != sorted(present, key=lambda x:(int(x),x)):
            return False, f"回合{r} inorder 与理论集合不一致"
    return True, f"{n_rounds} 回合随机插入/删除全部通过"

if __name__ == "__main__":
    ok1, m1 = test_known_sequences()
    print("已知序列:", "PASS" if ok1 else "FAIL", "-", m1)
    ok2, m2 = test_random()
    print("随机混合:", "PASS" if ok2 else "FAIL", "-", m2)
    print("OVERALL:", "ALL PASS" if (ok1 and ok2) else "HAS FAILURE")
