"""AVL 内存安全模拟器 v4：忠实模拟 unique_ptr move 语义，检测 move 后解引用。"""
import random

class SegFaultError(Exception):
    def __init__(self, msg): super().__init__("SIGSEGV @ " + msg)

class Node:
    _c = [4000]
    def __init__(self, value):
        self.addr = Node._c[0]; Node._c[0] += 1
        self.value = value; self.id = self.addr; self.height = 1
        self.left = OwnPtr(None); self.right = OwnPtr(None)

class OwnPtr:
    def __init__(self, node): self.node = node
    def get(self): return self.node
    def is_null(self): return self.node is None
    def move(self):
        n = self.node; self.node = None; return OwnPtr(n)
    def assign(self, other):
        self.node = other.node; return self

def make_unique(value): return OwnPtr(Node(value))
def height(n): return 0 if n is None else n.height
def upd(n):
    if n is None: return
    n.height = 1 + max(height(n.left.get()), height(n.right.get()))
def balance(n): return 0 if n is None else height(n.left.get()) - height(n.right.get())

def D(p):
    if p.node is None: raise SegFaultError("通过已 move 的 unique_ptr 解引用 (null)")
    return p.node

class AVL:
    def __init__(self): self.root = OwnPtr(None); self.size = 0
    def rotateRight(self, y):
        yN = D(y); x = yN.left.move(); T2 = D(x).right.move()
        y_raw = yN; x_raw = D(x)
        D(x).right = y.move()
        y_raw.left = T2
        upd(y_raw); upd(x_raw)
        return OwnPtr(D(x))
    def rotateLeft(self, x):
        xN = D(x); y = xN.right.move(); T2 = D(y).left.move()
        x_raw = xN; y_raw = D(y)
        D(y).left = x.move()
        x_raw.right = T2
        upd(x_raw); upd(y_raw)
        return OwnPtr(D(y))
    def insert(self, value):
        if self.root.is_null(): self.root = make_unique(value); self.size = 1; return
        added = [False]; realRoot = self.root.get()
        self.root = self.insertRec(self.root.move(), value, added, realRoot, True)
    def insertRec(self, node, value, added, realRoot, isTop):
        if node.is_null():
            n = make_unique(value); added[0] = True; return n
        c = cmp(value, D(node).value)
        if c == 0: return node
        if c < 0: D(node).left = self.insertRec(D(node).left.move(), value, added, realRoot, False)
        else: D(node).right = self.insertRec(D(node).right.move(), value, added, realRoot, False)
        upd(D(node)); b = balance(D(node))
        if b > 1 and balance(D(node).left.get()) >= 0:
            nr = self.rotateRight(node.move())
            if isTop: realRoot = nr.get()
            return nr
        if b > 1 and balance(D(node).left.get()) < 0:
            D(node).left = self.rotateLeft(D(node).left.move())
            nr = self.rotateRight(node.move())
            if isTop: realRoot = nr.get()
            return nr
        if b < -1 and balance(D(node).right.get()) <= 0:
            nr = self.rotateLeft(node.move())
            if isTop: realRoot = nr.get()
            return nr
        if b < -1 and balance(D(node).right.get()) > 0:
            D(node).right = self.rotateRight(D(node).right.move())
            nr = self.rotateLeft(node.move())
            if isTop: realRoot = nr.get()
            return nr
        return node
    def remove(self, value):
        if self.root.is_null(): return
        removed = [False]; realRoot = self.root.get()
        nr = self.removeRec(self.root.move(), value, removed, realRoot, True)
        self.root = nr if nr is not None else OwnPtr(None)
    def removeRec(self, node, value, removed, realRoot, isTop):
        if node.is_null(): return None
        c = cmp(value, D(node).value)
        if c < 0:
            ch = self.removeRec(D(node).left.move(), value, removed, realRoot, False)
            D(node).left = ch if ch is not None else OwnPtr(None)
        elif c > 0:
            ch = self.removeRec(D(node).right.move(), value, removed, realRoot, False)
            D(node).right = ch if ch is not None else OwnPtr(None)
        else:
            removed[0] = True
            if D(node).left.is_null() or D(node).right.is_null():
                return D(node).left.move() if not D(node).left.is_null() else D(node).right.move()
            succ = D(node).right.get()
            while not succ.left.is_null(): succ = succ.left.get()
            D(node).value = succ.value
            ch = self.removeRec(D(node).right.move(), succ.value, removed, realRoot, False)
            D(node).right = ch if ch is not None else OwnPtr(None)
        if node.node is None: return None
        upd(D(node)); b = balance(D(node))
        if b > 1 and balance(D(node).left.get()) >= 0:
            nr = self.rotateRight(node.move()); 
            if isTop: realRoot = nr.get()
            return nr
        if b > 1 and balance(D(node).left.get()) < 0:
            D(node).left = self.rotateLeft(D(node).left.move())
            nr = self.rotateRight(node.move())
            if isTop: realRoot = nr.get()
            return nr
        if b < -1 and balance(D(node).right.get()) <= 0:
            nr = self.rotateLeft(node.move())
            if isTop: realRoot = nr.get()
            return nr
        if b < -1 and balance(D(node).right.get()) > 0:
            D(node).right = self.rotateRight(D(node).right.move())
            nr = self.rotateLeft(node.move())
            if isTop: realRoot = nr.get()
            return nr
        return node
    def validate(self):
        errs = []
        def check(n, lo, hi):
            if n is None: return 0
            if (lo is not None and cmp(n.value, lo) <= 0) or (hi is not None and cmp(n.value, hi) >= 0):
                errs.append(f"BST {n.value}")
            lh = check(n.left.get(), lo, n.value) if not n.left.is_null() else 0
            rh = check(n.right.get(), n.value, hi) if not n.right.is_null() else 0
            h = 1 + max(lh, rh)
            if h != n.height: errs.append(f"h {n.value}")
            if abs(lh - rh) > 1: errs.append(f"bal {n.value}")
            return h
        check(self.root.get(), None, None)
        return errs

def cmp(a, b):
    try:
        ia, ib = int(a), int(b); return (ia > ib) - (ia < ib)
    except: return (a > b) - (a < b)

def run_known():
    seqs = [["10","20","30"],["30","20","10"],["10","30","20"],["30","10","20"],
            ["11","14","12"],["1","2","3","4","5","6","7"],["7","6","5","4","3","2","1"],
            ["50","30","70","20","40","60","80","10"]]
    for s in seqs:
        t = AVL()
        for v in s: t.insert(v)
        print(f"insert {s}: {'OK' if not t.validate() else t.validate()[:2]}")

def run_random(n=3000):
    for rnd in range(n):
        t = AVL()
        try:
            for _ in range(random.randint(1, 30)):
                v = str(random.randint(0, 50))
                if random.random() < 0.6: t.insert(v)
                else: t.remove(v)
                if t.validate():
                    print(f"FAIL rnd{rnd}"); return False
        except SegFaultError as ex:
            print(f"SEGFAULT rnd{rnd}: {ex}"); return False
    print(f"随机 {n} 回合: ALL PASS (无 move 后解引用)")
    return True

if __name__ == "__main__":
    run_known(); run_random(3000)
