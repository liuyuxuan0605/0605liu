"""
RedBlackTree C++ 内存安全诊断器 —— 精确模拟 unique_ptr + raw pointer 语义
目标：在 11 -> 14 -> 12 序列中检测:
  1. 空指针解引用 (nullptr dereference)
  2. Use-after-free (访问已被释放的对象)
  3. 悬垂指针 (dangling pointer from moved-from unique_ptr)
  4. parent 指针链断裂 (parent chain broken after rotation)

模拟 C++ RedBlackTree.h 的精确行为，包括:
- unique_ptr 所有权语义 (move = 所有权转移, source 变空)
- raw pointer 非 owning (仅观测, 不影响生命周期)
- rotateLeft / rotateRight / rotateLeftAt / rotateRightAt 的精确实现
- makeFrame / collectVisual 的遍历路径
"""

import sys
import traceback

# ============================================================
# 模拟 C++ 内存模型
# ============================================================

class UniquePtr:
    """模拟 std::unique_ptr -- 所有权唯一, move 后 source 为空"""
    _next_addr = 0x1000  # 模拟堆地址

    def __init__(self, obj=None):
        if obj is not None:
            self._obj = obj
            self._addr = UniquePtr._next_addr
            UniquePtr._next_addr += 0x40
        else:
            self._obj = None
            self._addr = 0
        self._moved_from = False

    @property
    def raw(self):
        """相当于 .get() -- 返回裸指针 (对象地址或 None)"""
        if self._moved_from or self._obj is None:
            return None
        return self._obj

    @property
    def is_valid(self):
        return not self._moved_from and self._obj is not None

    def move(self):
        """模拟 std::move -- 转移所有权, 返回新的 UniquePtr, self 变空/moved-from"""
        new_up = UniquePtr.__new__(UniquePtr)
        new_up._obj = self._obj
        new_up._addr = self._addr
        new_up._moved_from = False
        self._obj = None
        self._addr = 0
        self._moved_from = True
        return new_up

    def __bool__(self):
        return self.is_valid

    def __repr__(self):
        if self.is_valid:
            return f"UP@{self._addr:#x}({self._obj})"
        return "UP(null)"


class Node:
    """模拟 C++ Node 对象"""
    _id_counter = 0

    def __init__(self, value):
        Node._id_counter += 1
        self.id = Node._id_counter
        self.value = value
        self.color = "RED"
        self.left = UniquePtr()     # unique_ptr<Node>
        self.right = UniquePtr()    # unique_ptr<Node>
        self.parent = None          # raw Node*, non-owning
        self._birth_order = Node._id_counter

    def __repr__(self):
        c = "R" if self.color == "RED" else "B"
        p_val = self.parent.value if self.parent else "None"
        return f"Node(id={self.id},val={value_repr(self.value)},color={c},parent={p_val})"


def value_repr(v):
    return v


class SegFaultError(RuntimeError):
    pass


class MemoryChecker:
    """跟踪所有活跃对象, 检测 use-after-free"""

    def __init__(self):
        self.alive = set()       # set of id(node objects)
        self.access_log = []     # 所有访问记录

    def allocate(self, node):
        self.alive.add(id(node))
        return node

    def check(self, node, label=""):
        """检查 node 是否可安全访问"""
        if node is None:
            raise SegFaultError(f"[SEGFAULT] NULLPTR DEREF at: {label}")
        if id(node) not in self.alive:
            raise SegFaultError(f"[SEGFAULT] USE-AFTER-FREE at: {label} (node id={getattr(node,'id','?')})")
        self.access_log.append((label, node))
        return node

    def free(self, node):
        if node is not None:
            self.alive.discard(id(node))

    def dump_tree(self, root_raw, label=""):
        """递归打印树结构"""
        if root_raw is None:
            return "(empty)"
        lines = []
        def dump(n, depth=0):
            mc.check(n, f"dump({label})")
            c = "R" if n.color == "RED" else "B"
            pv = n.parent.value if n.parent else "*ROOT*"
            left_val = n.left.raw.value if n.left.raw else "-"
            right_val = n.right.raw.value if n.right.raw else "-"
            lines.append("  " * depth + f"{n.value}({c}) parent={pv} L={left_val} R={right_val}")
            if n.left.raw:
                dump(n.left.raw, depth+1)
            if n.right.raw:
                dump(n.right.raw, depth+1)
        dump(root_raw)
        return "\n".lines


mc = MemoryChecker()


# ============================================================
# RedBlackTree 操作 (忠实移植 C++ RedBlackTree.h)
# ============================================================

def bstInsert(root_up, value, frames):
    """
    对应 C++ 的 bstInsert.
    root_up: UniquePtr (持有根节点, 通过 list 包裹实现按引用传递)
    返回: (root_up, new_node_raw_or_None)
    """
    print(f"\n=== bstInsert({value}) ===")
    parent = None
    cur = root_up.raw

    step = 0
    while cur is not None:
        mc.check(cur, f"bstInsert while-cur step{step}")
        # makeFrame 模拟 (略, 只关注指针操作)
        c = compareValues(value, cur.value)
        if c == 0:
            print(f"  -> 已存在, 返回 None")
            return root_up, None
        parent = cur
        cur = cur.left.raw if c < 0 else cur.right.raw
        step += 1

    mc.check(parent, f"bstInsert-parent before create")
    n = Node(value)
    mc.allocate(n)
    n.color = "RED"
    raw = n  # raw pointer
    n.parent = parent

    if compareValues(value, parent.value) < 0:
        parent.left = UniquePtr(n)
        print(f"  -> 创建 {value}(R), 作为 {parent.value} 的左孩子")
    else:
        parent.right = UniquePtr(n)
        print(f"  -> 创建 {value}(R), 作为 {parent.value} 的右孩子")

    print(f"  -> 树结构:")
    print_tree(root_up.raw)
    return root_up, raw


def rotateLeft(x_up):
    """
    对应 C++:
    std::unique_ptr<Node> rotateLeft(std::unique_ptr<Node> x)
    注意: x_up 是按值传入 (C++ 里 unique_ptr 是按值传的, 但实际上是从 move 传来的)
    """
    x = x_up.raw
    mc.check(x, "rotateLeft-x")
    print(f"  [rotL] 旋转子树根: {x.value}")

    if not x.right.is_valid:
        print(f"  [rotL] 无右孩子, 无法左旋, 原样返回")
        return x_up

    y_up = x_right_move = x.right.move()  # y = std::move(x->right)
    y = y_up.raw
    T2_up = y_left_move = y.left.move() if y.left.is_valid else UniquePtr()  # T2 = std::move(y->left)

    # y->left = std::move(x)
    y.left = x_up
    # x->right = std::move(T2)
    x.right = T2_up
    # y->parent = x->parent
    y.parent = x.parent
    # x->parent = y.get()
    x.parent = y
    # if (x->right) x->right->parent = x.get()
    if x.right.is_valid:
        mc.check(x.right.raw, "rotL-x->right->parent set")
        x.right.raw.parent = x

    print(f"  [rotL] 旋转完成, 新根: {y.value}")
    return y_up


def rotateRight(y_up):
    """
    对应 C++:
    std::unique_ptr<Node> rotateRight(std::unique_ptr<Node> y)
    """
    y = y_up.raw
    mc.check(y, "rotateRight-y")
    print(f"  [rotR] 旋转子树根: {y.value}")

    if not y.left.is_valid:
        print(f"  [rotR] 无左孩子, 无法右旋, 原样返回")
        return y_up

    x_up = y_left_move = y.left.move()  # x = std::move(y->left)
    x = x_up.raw
    T2_up = x_right_move = x.right.move() if x.right.is_valid else UniquePtr()  # T2 = std::move(x->right)

    # x->right = std::move(y)
    x.right = y_up
    # y->left = std::move(T2)
    y.left = T2_up
    # x->parent = y->parent
    x.parent = y.parent
    # y->parent = x.get()
    y.parent = x
    # if (y->left) y->left->parent = y.get()
    if y.left.is_valid:
        mc.check(y.left.raw, "rotR-y->left->parent set")
        y.left.raw.parent = y

    print(f"  [rotR] 旋转完成, 新根: {x.value}")
    return x_up


def rotateLeftAt(x, root_holder):
    """
    对应 C++:
    Node* rotateLeftAt(Node* x)
    root_holder: dict with 'up' key for root_ UniquePtr (按引用修改)
    """
    mc.check(x, "rotateLeftAt-x")
    print(f"  [rotLAt] 对节点 {x.value} 执行原地左旋")

    p = x.parent
    isLeft = False
    if p is not None:
        mc.check(p, "rotLAt-p")
        isLeft = (p.left.raw == x)

    # 取出子树所有权
    if p is not None:
        if isLeft:
            sub = p.left.move()
            print(f"  [rotLAt] 从 p({p.value}).left 取出子树 (根:{x.value})")
        else:
            sub = p.right.move()
            print(f"  [rotLAt] 从 p({p.value}).right 取出子树 (根:{x.value})")
    else:
        sub = root_holder['up'].move()
        print(f"  [rotLAt] 从 root_ 取出整棵树 (根:{x.value})")

    sub = rotateLeft(sub)

    # 挂回去
    if p is not None:
        if isLeft:
            p.left = sub
            new_root = p.left.raw
        else:
            p.right = sub
            new_root = p.right.raw
        print(f"  [rotLAt] 挂回 p({p.value}).{'left' if isLeft else 'right'}, 新子树根: {new_root.value}")
    else:
        root_holder['up'] = sub
        new_root = root_holder['up'].raw
        print(f"  [rotLAt] 挂回 root_, 新整树根: {new_root.value}")

    mc.check(new_root, "rotLAt-return")
    return new_root


def rotateRightAt(y, root_holder):
    """
    对应 C++:
    Node* rotateRightAt(Node* y)
    """
    mc.check(y, "rotateRightAt-y")
    print(f"  [rotRAt] 对节点 {y.value} 执行原地右旋")

    p = y.parent
    isLeft = False
    if p is not None:
        mc.check(p, "rotRAt-p")
        isLeft = (p.left.raw == y)

    if p is not None:
        if isLeft:
            sub = p.left.move()
            print(f"  [rotRAt] 从 p({p.value}).left 取出子树 (根:{y.value})")
        else:
            sub = p.right.move()
            print(f"  [rotRAt] 从 p({p.value}).right 取出子树 (根:{y.value})")
    else:
        sub = root_holder['up'].move()
        print(f"  [rotRAt] 从 root_ 取出整棵树 (根:{y.value})")

    sub = rotateRight(sub)

    if p is not None:
        if isLeft:
            p.left = sub
            new_root = p.left.raw
        else:
            p.right = sub
            new_root = p.right.raw
        print(f"  [rotRAt] 挂回 p({p.value}).{'left' if isLeft else 'right'}, 新子树根: {new_root.value}")
    else:
        root_holder['up'] = sub
        new_root = root_holder['up'].raw
        print(f"  [rotRAt] 挂回 root_, 新整树根: {new_root.value}")

    mc.check(new_root, "rotRAt-return")
    return new_root


def compareValues(a, b):
    try:
        da = float(a)
        db = float(b)
        if da < db: return -1
        if da > db: return 1
        return 0
    except:
        if a < b: return -1
        if a > b: return 1
        return 0


def collectVisual(n, frame_nodes, frame_edges):
    """对应 C++ 的 collectVisual — 遍历收集帧数据"""
    if n is None:
        return
    mc.check(n, f"collectVisual({n.value})")
    frame_nodes.append({
        'id': n.id,
        'value': n.value,
        'sublabel': '红' if n.color == 'RED' else '黑',
        'color': '#E53935' if n.color == 'RED' else '#263238'
    })
    if n.left.is_valid:
        mc.check(n.left.raw, f"collectVisual-left-edge({n.value}->{n.left.raw.value})")
        frame_edges.append({'from': n.id, 'to': n.left.raw.id, 'kind': 'left'})
        collectVisual(n.left.raw, frame_nodes, frame_edges)
    if n.right.is_valid:
        mc.check(n.right.raw, f"collectVisual-right-edge({n.value}->{n.right.raw.value})")
        frame_edges.append({'from': n.id, 'to': n.right.raw.id, 'kind': 'right'})
        collectVisual(n.right.raw, frame_nodes, frame_edges)


def makeFrame(root_raw, desc, highlight_ids=None):
    """对应 C++ 的 makeFrame — 采集整棵树快照"""
    nodes = []
    edges = []
    if root_raw is not None:
        mc.check(root_raw, f"makeFrame-root({desc})")
        collectVisual(root_raw, nodes, edges)
    return {'desc': desc, 'nodes': nodes, 'edges': edges, 'highlights': highlight_ids or []}


def print_tree(root_raw, label=""):
    """打印树结构用于调试"""
    if root_raw is None:
        print(f"  Tree({label}): (empty)")
        return
    lines = []
    def show(n, d=0):
        mc.check(n, f"print_tree-show")
        c = "R" if n.color == "RED" else "B"
        pv = n.parent.value if n.parent else "*"
        lv = n.left.raw.value if n.left.raw else "."
        rv = n.right.raw.value if n.right.raw else "."
        lines.append("  "*d + f"{n.value}({c}) p={pv} l=[{lv}] r=[{rv}] id={n.id}")
        if n.left.raw: show(n.left.raw, d+1)
        if n.right.raw: show(n.right.raw, d+1)
    show(root_raw)
    for line in lines:
        print(f"  {line}")


def validate_rb(root_raw, label=""):
    """完整的红黑树性质校验"""
    errors = []
    if root_raw is None:
        return errors

    # 性质2: 根是黑色
    if root_raw.color != "BLACK":
        errors.append(f"[{label}] ROOT NOT BLACK: {root_raw.color}")

    def check(n, path="root"):
        if n is None:
            return 1  # 空节点算黑色高度1

        # 性质4: 红节点的两个子女都是黑色
        if n.color == "RED":
            if n.left.is_valid and n.left.raw.color == "RED":
                errors.append(f"[{label}] RED VIOLATION at {n.value} (path={path}): left child {n.left.raw.value} also RED")
            if n.right.is_valid and n.right.raw.color == "RED":
                errors.append(f"[{label}] RED VIOLATION at {n.value} (path={path}): right child {n.right.raw.value} also RED")

        # 性质5: 黑高度一致
        lh = check(n.left.raw, path+"L") if n.left.is_valid else 1
        rh = check(n.right.raw, path+"R") if n.right.is_valid else 1
        if lh != rh:
            errors.append(f"[{label}] BLACK HEIGHT MISMATCH at {n.value}: left_bh={lh} right_bh={rh} (path={path})")

        own_bh = (1 if n.color == "BLACK" else 0) + max(lh, rh)

        # parent 一致性
        if n.left.is_valid and n.left.raw.parent != n:
            errors.append(f"[{label}] PARENT CHAIN BROKEN: {n.value}.left={n.left.raw.value} but its parent is {n.left.raw.parent.value if n.left.raw.parent else 'None'} (expected {n.value})")
        if n.right.is_valid and n.right.raw.parent != n:
            errors.append(f"[{label}] PARENT CHAIN BROKEN: {n.value}.right={n.right.raw.value} but its parent is {n.right.raw.parent.value if n.right.raw.parent else 'None'} (expected {n.value})")

        return own_bh

    bh = check(root_raw)
    return errors


# ============================================================
# 主测试: 11 -> 14 -> 12 (触发 RL 旋转)
# ============================================================

def test_11_14_12():
    """精确模拟 C++ RedBlackTree::insert 对 11, 14, 12 的处理"""
    print("=" * 70)
    print("RedBlackTree 内存安全诊断: 插入序列 11 -> 14 -> 12")
    print("=" * 70)

    root_holder = {'up': UniquePtr()}  # 模拟 root_
    size = 0
    frames = []

    def do_insert(value):
        nonlocal size
        print(f"\n{'='*60}")
        print(f"INSERT {value}")
        print(f"{'='*60}")

        if not root_holder['up'].is_valid:
            # 空树: 创建黑色根
            print(f"  空树, 创建黑色根 {value}")
            n = Node(value)
            mc.allocate(n)
            n.color = "BLACK"
            root_holder['up'] = UniquePtr(n)
            size = 1
            f = makeFrame(root_holder['up'].raw, f"创建黑色根节点 {value}")
            frames.append(f)
            print_tree(root_holder['up'].raw, f"after-insert-{value}")
            errs = validate_rb(root_holder['up'].raw, f"ins-{value}")
            if errs:
                for e in errs: print(f"  ERROR: {e}")
            else:
                print(f"  RB validate OK")
            return

        # bstInsert
        root_holder['up'], z = bstInsert(root_holder['up'], value, frames)
        if z is None:
            print(f"  已存在 {value}, 跳过")
            return

        size += 1
        print(f"  BST 插入完成, 开始 fixInsert(z={z.value})")
        print_tree(root_holder['up'].raw, f"pre-fixInsert-{value}")

        # fixInsert (核心!)
        fix_insert(z, root_holder, frames)

        # 循环结束后: 根染黑
        if root_holder['up'].is_valid:
            mc.check(root_holder['up'].raw, "post-fixInsert-root-color")
            root_holder['up'].raw.color = "BLACK"

        f = makeFrame(root_holder['up'].raw, f"插入完成，节点数 {size}")
        frames.append(f)
        print_tree(root_holder['up'].raw, f"after-insert-{value}")
        errs = validate_rb(root_holder['up'].raw, f"ins-{value}-final")
        if errs:
            for e in errs: print(f"  ERROR: {e}")
            return False
        else:
            print(f"  RB validate OK ✓")
            return True


    def fix_insert(z, root_holder, frames):
        """对应 C++ fixInsert — 完整复制控制流"""
        iteration = 0
        while True:
            iteration += 1
            print(f"\n  --- fixInsert iter #{iteration} ---")
            mc.check(z, f"fixInsert-while-check-z")
            print(f"  z = {z.value}({z.color})")

            if z.parent is None:
                print(f"  z.parent == nullptr → 退出循环")
                break

            mc.check(z.parent, f"fixInsert-while-check-parent")
            print(f"  z.parent = {z.parent.value}({z.parent.color})")

            if z.parent.color != "RED":
                print(f"  父节点不是红色 → 退出循环")
                break

            # 父是红色, 进入修复
            gp = z.parent.parent
            print(f"  gp = z.parent.parent = {gp.value if gp else 'None'}")
            if gp is None:
                print(f"  gp == nullptr (防御性 break)")
                break

            mc.check(gp, "fixInsert-gp")

            if z.parent == gp.left.raw:
                # === 左分支 ===
                print(f"  [分支] 父是祖父的左孩子")
                uncle = gp.right.raw if gp.right.is_valid else None
                u_color = uncle.color if uncle else "NONE"
                print(f"  叔叔 = {uncle.value if uncle else 'None'} ({u_color})")

                if uncle is not None and uncle.color == "RED":
                    # Case 1:叔叔为红
                    print(f"  -> CASE 1: recolor (叔叔为红)")
                    z.parent.color = "BLACK"
                    uncle.color = "BLACK"
                    gp.color = "RED"
                    frames.append(makeFrame(root_holder['up'].raw, "情况1"))
                    z = gp
                else:
                    # Case 2/3
                    if z == z.parent.right.raw:
                        print(f"  -> CASE 2: LR情形, 先左旋父节点 {z.parent.value}")
                        z = z.parent
                        z = rotateLeftAt(z, root_holder)
                        frames.append(makeFrame(root_holder['up'].raw, "情况2-左旋"))

                    print(f"  -> CASE 3: 右旋祖父 {gp.value}")
                    mc.check(z.parent, "case3-set-parent-color")
                    z.parent.color = "BLACK"
                    gp.color = "RED"
                    frames.append(makeFrame(root_holder['up'].raw, "情况3-recolor"))
                    rotateRightAt(gp, root_holder)
                    frames.append(makeFrame(root_holder['up'].raw, "情况3-右旋"))
            else:
                # === 右分支 (镜像) ===
                print(f"  [分支] 父是祖父的右孩子")
                uncle = gp.left.raw if gp.left.is_valid else None
                u_color = uncle.color if uncle else "NONE"
                print(f"  叔叔 = {uncle.value if uncle else 'None'} ({u_color})")

                if uncle is not None and uncle.color == "RED":
                    # Case 1:叔叔为红
                    print(f"  -> CASE 1: recolor (叔叔为红)")
                    z.parent.color = "BLACK"
                    uncle.color = "BLACK"
                    gp.color = "RED"
                    frames.append(makeFrame(root_holder['up'].raw, "情况1"))
                    z = gp
                else:
                    # Case 2/3 (镜像)
                    if z == z.parent.left.raw:
                        print(f"  -> CASE 2: RL情形, 先右旋父节点 {z.parent.value}")
                        z = z.parent
                        z = rotateRightAt(z, root_holder)  # ★★ 这是 11->14->12 触发的关键行! ★★
                        frames.append(makeFrame(root_holder['up'].raw, "情况2-右旋"))

                    print(f"  -> CASE 3: 左旋祖父 {gp.value}")
                    mc.check(z.parent, "case3-mirror-set-parent-color")
                    z.parent.color = "BLACK"      # ★★ 旋转后访问 z.parent ★★
                    gp.color = "RED"
                    frames.append(makeFrame(root_holder['up'].raw, "情况3-recolor-mirror"))
                    rotateLeftAt(gp, root_holder)   # ★★ 对祖父做左旋 ★★
                    frames.append(makeFrame(root_holder['up'].raw, "情况3-左旋"))

            print_tree(root_holder['up'].raw, f"fixAfter-iter#{iteration}")

        print(f"  fixInsert 结束 (共 {iteration} 次迭代)")

    # ===== 执行插入序列 =====
    all_ok = True
    for val in ["11", "14", "12"]:
        try:
            ok = do_insert(val)
            if ok is False:
                all_ok = False
        except SegFaultError as e:
            print(f"\n{'!'*70}")
            print(f"!!! SEGFAULT DETECTED !!!")
            print(f"{e}")
            print(f"{'!'*70}")
            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n{'!'*70}")
            print(f"!!! EXCEPTION !!!")
            print(f"{e}")
            traceback.print_exc()
            print(f"{'!'*70}")
            return False

    # 最终验证
    print(f"\n{'='*70}")
    print(f"最终树结构:")
    print_tree(root_holder['up'].raw, "final")
    errs = validate_rb(root_holder['up'].raw, "FINAL")
    if errs:
        print(f"VALIDATE FAILED:")
        for e in errs:
            print(f"  {e}")
        return False
    else:
        print(f"ALL CHECKS PASSED ✓✓✓")
        print(f"(无 SEGFAULT, 无 USE-AFTER-FREE, 无 PARENT CHAIN BREAK)")
        return True


if __name__ == "__main__":
    ok = test_11_14_12()
    sys.exit(0 if ok else 1)
