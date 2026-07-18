import random, sys, traceback

# =====================================================================
# 原样移植 AVL / RB 核心逻辑（含疑似 bug），用于暴露结构性崩溃点
# 节点用字典模拟，parent 用 id 引用；旋转用引用重写
# =====================================================================

class AVL:
    def __init__(self):
        self.nodes = {}      # id -> dict(value,left,right,height)
        self.next_id = 1
        self.root = None

    def _new(self, value):
        nid = self.next_id; self.next_id += 1
        self.nodes[nid] = {"value": value, "left": None, "right": None, "height": 1}
        return nid

    def h(self, nid):
        return 0 if nid is None else self.nodes[nid]["height"]
    def upd(self, nid):
        if nid is not None:
            self.nodes[nid]["height"] = 1 + max(self.h(self.nodes[nid]["left"]), self.h(self.nodes[nid]["right"]))
    def bal(self, nid):
        return 0 if nid is None else self.h(self.nodes[nid]["left"]) - self.h(self.nodes[nid]["right"])

    def rotR(self, y):
        x = self.nodes[y]["left"]
        T2 = self.nodes[x]["right"]
        self.nodes[x]["right"] = y
        self.nodes[y]["left"] = T2
        self.upd(y); self.upd(x)
        return x
    def rotL(self, x):
        y = self.nodes[x]["right"]
        T2 = self.nodes[y]["left"]
        self.nodes[y]["left"] = x
        self.nodes[x]["right"] = T2
        self.upd(x); self.upd(y)
        return y

    def insert(self, value):
        added = [False]
        self.root = self._ins(self.root, value, added)
    def _ins(self, node, value, added):
        if node is None:
            added[0] = True
            return self._new(value)
        c = (value > self.nodes[node]["value"]) - (value < self.nodes[node]["value"])
        if c == 0:
            return node
        if c < 0:
            self.nodes[node]["left"] = self._ins(self.nodes[node]["left"], value, added)
        else:
            self.nodes[node]["right"] = self._ins(self.nodes[node]["right"], value, added)
        self.upd(node)
        b = self.bal(node)
        if b > 1 and self.bal(self.nodes[node]["left"]) >= 0:
            return self.rotR(node)
        if b > 1 and self.bal(self.nodes[node]["left"]) < 0:
            self.nodes[node]["left"] = self.rotL(self.nodes[node]["left"])
            return self.rotR(node)
        if b < -1 and self.bal(self.nodes[node]["right"]) <= 0:
            return self.rotL(node)
        if b < -1 and self.bal(self.nodes[node]["right"]) > 0:
            self.nodes[node]["right"] = self.rotR(self.nodes[node]["right"])
            return self.rotL(node)
        return node

    def remove(self, value):
        removed = [False]
        self.root = self._rem(self.root, value, removed)
    def _rem(self, node, value, removed):
        if node is None:
            return None
        c = (value > self.nodes[node]["value"]) - (value < self.nodes[node]["value"])
        if c < 0:
            self.nodes[node]["left"] = self._rem(self.nodes[node]["left"], value, removed)
        elif c > 0:
            self.nodes[node]["right"] = self._rem(self.nodes[node]["right"], value, removed)
        else:
            removed[0] = True
            if self.nodes[node]["left"] is None or self.nodes[node]["right"] is None:
                child = self.nodes[node]["left"] if self.nodes[node]["left"] is not None else self.nodes[node]["right"]
                # 原 C++ 在这里返回 child 并销毁 node
                del self.nodes[node]
                return child
            # 双子节点：用后继的值替换，并递归从右子树删除后继
            # （递归删除会让 height 更新沿路径正确回传，避免陈旧高度）
            succ = self.nodes[node]["right"]
            while self.nodes[succ]["left"] is not None:
                succ = self.nodes[succ]["left"]
            succVal = self.nodes[succ]["value"]
            self.nodes[node]["right"] = self._rem(self.nodes[node]["right"], succVal, removed)
            self.nodes[node]["value"] = succVal
        if node is None:
            return None
        self.upd(node)
        b = self.bal(node)
        if b > 1 and self.bal(self.nodes[node]["left"]) >= 0:
            return self.rotR(node)
        if b > 1 and self.bal(self.nodes[node]["left"]) < 0:
            self.nodes[node]["left"] = self.rotL(self.nodes[node]["left"])
            return self.rotR(node)
        if b < -1 and self.bal(self.nodes[node]["right"]) <= 0:
            return self.rotL(node)
        if b < -1 and self.bal(self.nodes[node]["right"]) > 0:
            self.nodes[node]["right"] = self.rotR(self.nodes[node]["right"])
            return self.rotL(node)
        return node

    def validate(self):
        # BST + AVL 高度/平衡校验
        def check(nid, lo, hi):
            if nid is None:
                return 0
            n = self.nodes[nid]
            if lo is not None and not (n["value"] > lo): raise Exception(f"BST viol left {n['value']}<={lo}")
            if hi is not None and not (n["value"] < hi): raise Exception(f"BST viol right {n['value']}>={hi}")
            lh = check(n["left"], lo, n["value"])
            rh = check(n["right"], n["value"], hi)
            if abs(lh - rh) > 1: raise Exception(f"AVL bal viol at {n['value']}: {lh},{rh}")
            if n["height"] != 1 + max(lh, rh): raise Exception(f"height viol at {n['value']}")
            return 1 + max(lh, rh)
        check(self.root, None, None)
        # 检查所有节点可达
        seen = set()
        def walk(nid):
            if nid is None: return
            if nid in seen: raise Exception("cycle/duplicate ref")
            seen.add(nid); walk(self.nodes[nid]["left"]); walk(self.nodes[nid]["right"])
        walk(self.root)
        if len(seen) != len(self.nodes):
            raise Exception(f"unreachable nodes: total={len(self.nodes)} reachable={len(seen)}")

# ---- 主测试 ----
random.seed(12345)
fails = 0
DUMPED = False
for trial in range(3000):
    t = AVL()
    vals = []
    ops = []
    try:
        for _ in range(random.randint(1, 40)):
            v = random.randint(0, 20)
            if random.random() < 0.65:
                t.insert(v)
                if v not in vals: vals.append(v)
                ops.append(('ins', v))
            else:
                t.remove(v)
                if v in vals: vals.remove(v)
                ops.append(('rem', v))
            t.validate()
        # 最终 inorder 必须等于 vals 排序
        order = []
        def io(nid):
            if nid is None: return
            io(t.nodes[nid]["left"]); order.append(t.nodes[nid]["value"]); io(t.nodes[nid]["right"])
        io(t.root)
        if order != sorted(vals):
            raise Exception(f"inorder mismatch: {order} vs {sorted(vals)}")
    except Exception as e:
        fails += 1
        if not DUMPED:
            print(f"TRIAL {trial} FAIL: {e}")
            print("  ops:", ops)
            def dump(nid, d=0):
                if nid is None: return
                n = t.nodes[nid]
                print('  '*d, n['value'], 'h=', n['height'], 'L=', n['left'], 'R=', n['right'])
                dump(n['left'], d+1); dump(n['right'], d+1)
            print("  tree:")
            dump(t.root)
            DUMPED = True
        if fails <= 5 and DUMPED:
            print(f"TRIAL {trial} FAIL: {e}")
            print("  vals:", sorted(vals))
print(f"AVL mixed trials done, fails={fails}")

# ---- 纯插入（旋转密集）测试 ----
fails2 = 0
for trial in range(3000):
    t = AVL()
    vals = []
    try:
        for _ in range(random.randint(1, 40)):
            v = random.randint(0, 25)
            t.insert(v)
            if v not in vals: vals.append(v)
            t.validate()
        order = []
        def io(nid):
            if nid is None: return
            io(t.nodes[nid]["left"]); order.append(t.nodes[nid]["value"]); io(t.nodes[nid]["right"])
        io(t.root)
        if order != sorted(vals):
            raise Exception(f"inorder mismatch: {order} vs {sorted(vals)}")
    except Exception as e:
        fails2 += 1
        if fails2 <= 5:
            print(f"INSERT-ONLY TRIAL {trial} FAIL: {e}")
print(f"AVL insert-only trials done, fails={fails2}")
