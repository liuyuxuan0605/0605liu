import random

class RB:
    RED, BLACK = 0, 1
    def __init__(self):
        self.nodes = {}
        self.next_id = 1
        self.root = None

    def _new(self, value, color):
        nid = self.next_id; self.next_id += 1
        self.nodes[nid] = {"value": value, "color": color, "left": None, "right": None, "parent": None}
        return nid

    def rotL(self, x):
        if self.nodes[x]["right"] is None: return x
        y = self.nodes[x]["right"]
        T2 = self.nodes[y]["left"]
        self.nodes[y]["left"] = x
        self.nodes[x]["right"] = T2
        self.nodes[y]["parent"] = self.nodes[x]["parent"]
        self.nodes[x]["parent"] = y
        if T2 is not None: self.nodes[T2]["parent"] = x
        return y
    def rotR(self, y):
        if self.nodes[y]["left"] is None: return y
        x = self.nodes[y]["left"]
        T2 = self.nodes[x]["right"]
        self.nodes[x]["right"] = y
        self.nodes[y]["left"] = T2
        self.nodes[x]["parent"] = self.nodes[y]["parent"]
        self.nodes[y]["parent"] = x
        if T2 is not None: self.nodes[T2]["parent"] = y
        return x

    def rotL_at(self, x):
        p = self.nodes[x]["parent"]
        isLeft = self.nodes[p]["left"] == x if p is not None else False
        sub = self.nodes[p]["left"] if (p is not None and isLeft) else (self.nodes[p]["right"] if p is not None else self.root)
        sub = self.rotL(sub)
        if p is not None:
            if isLeft: self.nodes[p]["left"] = sub
            else: self.nodes[p]["right"] = sub
        else:
            self.root = sub
        return sub
    def rotR_at(self, y):
        p = self.nodes[y]["parent"]
        isLeft = self.nodes[p]["left"] == y if p is not None else False
        sub = self.nodes[p]["left"] if (p is not None and isLeft) else (self.nodes[p]["right"] if p is not None else self.root)
        sub = self.rotR(sub)
        if p is not None:
            if isLeft: self.nodes[p]["left"] = sub
            else: self.nodes[p]["right"] = sub
        else:
            self.root = sub
        return sub

    def insert(self, value):
        parent = None
        cur = self.root
        while cur is not None:
            parent = cur
            c = (value > self.nodes[cur]["value"]) - (value < self.nodes[cur]["value"])
            if c == 0: return
            cur = self.nodes[cur]["left"] if c < 0 else self.nodes[cur]["right"]
        z = self._new(value, self.RED)
        self.nodes[z]["parent"] = parent
        if parent is None:
            self.root = z
        elif (value > self.nodes[parent]["value"]) - (value < self.nodes[parent]["value"]) < 0:
            self.nodes[parent]["left"] = z
        else:
            self.nodes[parent]["right"] = z
        self.fix(z)

    def fix(self, z):
        while self.nodes[z]["parent"] is not None and self.nodes[self.nodes[z]["parent"]]["color"] == self.RED:
            gp = self.nodes[self.nodes[z]["parent"]]["parent"]
            if gp is None: break
            if self.nodes[z]["parent"] == self.nodes[gp]["left"]:
                uncle = self.nodes[gp]["right"]
                if uncle is not None and self.nodes[uncle]["color"] == self.RED:
                    self.nodes[self.nodes[z]["parent"]]["color"] = self.BLACK
                    self.nodes[uncle]["color"] = self.BLACK
                    self.nodes[gp]["color"] = self.RED
                    z = gp
                else:
                    if z == self.nodes[self.nodes[z]["parent"]]["right"]:
                        z = self.nodes[z]["parent"]
                        self.rotL_at(z)
                    self.nodes[self.nodes[z]["parent"]]["color"] = self.BLACK
                    self.nodes[gp]["color"] = self.RED
                    self.rotR_at(gp)
            else:
                uncle = self.nodes[gp]["left"]
                if uncle is not None and self.nodes[uncle]["color"] == self.RED:
                    self.nodes[self.nodes[z]["parent"]]["color"] = self.BLACK
                    self.nodes[uncle]["color"] = self.BLACK
                    self.nodes[gp]["color"] = self.RED
                    z = gp
                else:
                    if z == self.nodes[self.nodes[z]["parent"]]["left"]:
                        z = self.nodes[z]["parent"]
                        self.rotR_at(z)
                    self.nodes[self.nodes[z]["parent"]]["color"] = self.BLACK
                    self.nodes[gp]["color"] = self.RED
                    self.rotL_at(gp)
        if self.root is not None:
            self.nodes[self.root]["color"] = self.BLACK

    def validate(self):
        if self.root is not None and self.nodes[self.root]["color"] != self.BLACK:
            raise Exception("root not black")
        def check(nid, black, lo, hi):
            if nid is None: return black
            n = self.nodes[nid]
            if lo is not None and not (n["value"] > lo): raise Exception(f"BST viol {n['value']}<={lo}")
            if hi is not None and not (n["value"] < hi): raise Exception(f"BST viol {n['value']}>={hi}")
            if n["color"] == self.RED:
                for c in (n["left"], n["right"]):
                    if c is not None and self.nodes[c]["color"] == self.RED:
                        raise Exception(f"red-red at {n['value']}")
            nb = black + (1 if n["color"] == self.BLACK else 0)
            l = check(n["left"], nb, lo, n["value"])
            r = check(n["right"], nb, n["value"], hi)
            if l != r: raise Exception(f"black-height mismatch at {n['value']}: {l},{r}")
            # parent pointer consistency
            for c in (n["left"], n["right"]):
                if c is not None and self.nodes[c]["parent"] != nid:
                    raise Exception(f"parent ptr mismatch at child {self.nodes[c]['value']}")
            return l
        check(self.root, 0, None, None)

random.seed(999)
fails = 0
for trial in range(5000):
    t = RB()
    vals = set()
    try:
        for _ in range(random.randint(1, 50)):
            v = random.randint(0, 25)
            t.insert(v); vals.add(v)
            t.validate()
        order = []
        def io(nid):
            if nid is None: return
            io(t.nodes[nid]["left"]); order.append(t.nodes[nid]["value"]); io(t.nodes[nid]["right"])
        io(t.root)
        if order != sorted(vals):
            raise Exception(f"inorder mismatch {order} vs {sorted(vals)}")
    except Exception as e:
        fails += 1
        if fails <= 3:
            print(f"RB TRIAL {trial} FAIL: {e}")
print(f"RB insert trials done, fails={fails}")
