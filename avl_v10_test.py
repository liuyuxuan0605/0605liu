#!/usr/bin/env python3
"""
AVL Tree 第10轮重写验证 —— parent 指针 + 原地旋转架构
忠实移植新 AVLTree.h 的算法逻辑，验证插入/删除/旋转正确性。

与旧版的区别：
- Node 有 parent 属性
- 旋转通过 rotateLeftAt/rotateRightAt 在原地完成
- insert = bstInsert + balanceInsert（沿 parent 上溯）
- remove = transplant + deleteOneChild + balanceDelete
"""

import random
import sys

# ===================== 全局 ID 生成器 =====================
_id_counter = [0]
def next_id():
    _id_counter[0] += 1
    return _id_counter[0]

def reset_id():
    _id_counter[0] = 0


class Node:
    __slots__ = ('value', 'id', 'height', 'left', 'right', 'parent')
    def __init__(self, value):
        self.value = value
        self.id = next_id()
        self.height = 1
        self.left = None       # Node or None (owning ref in C++ unique_ptr)
        self.right = None
        self.parent = None     # non-owning raw pointer
    
    def __repr__(self):
        return f"Node({self.value}, h={self.height})"


# ===================== 辅助函数 =====================
def height(n):
    return n.height if n else 0

def upd(n):
    if n:
        n.height = 1 + max(height(n.left), height(n.right))

def get_balance(n):
    return height(n.left) - height(n.right) if n else 0


def compare_values(a, b):
    """与 Common.h::compareValues 一致：数值优先比较，否则字典序"""
    try:
        da, db = float(a), float(b)
        if da < db: return -1
        if da > db: return 1
        return 0
    except (ValueError, TypeError):
        if a < b: return -1
        if a > b: return 1
        return 0


def collect_nodes(root):
    """收集所有节点值（中序），用于验证 BST 性质"""
    result = []
    def inorder(n):
        if not n: return
        inorder(n.left)
        result.append((n.value, n.id))
        inorder(n.right)
    inorder(root)
    return result


def check_avl(root, path="root"):
    """
    完整 AVL 合规检查：
    1. BST 有序性
    2. 高度正确性
    3. 平衡因子 ∈ [-1, 1]
    4. parent 指针一致性
    返回 (ok: bool, msg: str)
    """
    errors = []

    # 检查 BST + 收集所有节点
    values = []
    nodes_list = []
    def walk(n):
        if not n: return
        # 检查左子树值 < 当前 < 右子树值
        if n.left and compare_values(n.left.value, n.value) >= 0:
            errors.append(f"{path}: BST violation at {n.value} (left={n.left.value})")
        if n.right and compare_values(n.right.value, n.value) <= 0:
            errors.append(f"{path}: BST violation at {n.value} (right={n.right.value})")
        walk(n.left)
        values.append(n.value)
        nodes_list.append(n)
        walk(n.right)

    walk(root)

    # 检查有序
    for i in range(1, len(values)):
        if compare_values(values[i-1], values[i]) >= 0:
            errors.append(f"{path}: Not sorted at index {i-1},{i}: {values[i-1]} >= {values[i]}")

    # 检查每个节点
    for n in nodes_list:
        expected_h = 1 + max(height(n.left), height(n.right))
        if n.height != expected_h:
            errors.append(f"{path}/{n.value}: height={n.height}, expected={expected_h}")
        b = get_balance(n)
        if abs(b) > 1:
            errors.append(f"{path}/{n.value}: balance={b} out of [-1,1]")
        # 检查 parent 指针
        if n.left and n.left.parent is not n:
            errors.append(f"{path}/{n.value}: left child parent mismatch")
        if n.right and n.right.parent is not n:
            errors.append(f"{path}/{n.value}: right child parent mismatch")

    if root and root.parent is not None:
        errors.append(f"{path}: root.parent should be None, got {root.parent}")

    if errors:
        return False, "; ".join(errors[:5])
    return True, "OK"


# ===================== 底层旋转函数（对应 AVLTree.h 的 rotateLeft/rotateRight）=====================
#
# 注意：Python 没有 unique_ptr 语义，这里用"返回新根，调用者负责替换引用"来模拟。
# 关键：rotateLeftAt / rotateRightAt 负责把返回值写回正确的位置。

def rotate_left(x):
    """对应 C++ std::unique_ptr<Node> rotateLeft(std::unique_ptr<Node> x)
    返回 (new_root, y_raw) 其中 new_root 是旋转后的子树根"""
    if not x or not x.right:
        return x, None
    y = x.right
    T2 = y.left
    x_raw = x   # 裸指针
    y_raw = y

    y.left = x          # y 获得 x 的所有权（Python 引用）
    x_raw.right = T2

    # 维护 parent 指针（C++ 版本中也有）
    y_raw.parent = x_raw.parent
    x_raw.parent = y_raw
    if x_raw.right:
        x_raw.right.parent = x_raw

    upd(x_raw)
    upd(y_raw)
    return y, y_raw   # y 是新子树根


def rotate_right(y):
    """对应 C++ std::unique_ptr<Node> rotateRight(std::unique_ptr<Node> y)"""
    if not y or not y.left:
        return y, None
    x = y.left
    T2 = x.right
    y_raw = y
    x_raw = x

    x.right = y         # x 获得 y 的所有权
    y_raw.left = T2

    # 维护 parent 指针
    x_raw.parent = y_raw.parent
    y_raw.parent = x_raw
    if y_raw.left:
        y_raw.left.parent = y_raw

    upd(y_raw)
    upd(x_raw)
    return x, x_raw   # x 是新子树根


# ===================== 原地旋转包装（对应 rotateLeftAt / rotateRightAt）=====================

class AVLTree:
    """忠实移植第10版 AVLTree.h 的完整算法"""
    
    def __init__(self):
        self.root = None
        self.size = 0

    def rotate_left_at(self, x_node):
        """对应 C++ Node* rotateLeftAt(Node* x)"""
        p = x_node.parent
        is_left = (p.left is x_node) if p else False
        
        # 取出 owning 引用（Python 中直接取属性）
        if p:
            sub = p.left if is_left else p.right
        else:
            sub = self.root

        # 旋转
        new_sub, _ = rotate_left(sub)

        # 放回原位
        if p:
            if is_left:
                p.left = new_sub
            else:
                p.right = new_sub
        else:
            self.root = new_sub

        # 返回新子树根
        return p.left if (p and is_left) else (p.right if (p and not is_left) else self.root)

    def rotate_right_at(self, y_node):
        """对应 C++ Node* rotateRightAt(Node* y)"""
        p = y_node.parent
        is_left = (p.left is y_node) if p else False

        if p:
            sub = p.left if is_left else p.right
        else:
            sub = self.root

        new_sub, _ = rotate_right(sub)

        if p:
            if is_left:
                p.left = new_sub
            else:
                p.right = new_sub
        else:
            self.root = new_sub

        return p.left if (p and is_left) else (p.right if (p and not is_left) else self.root)

    # ---- BST 插入（对应 bstInsert）----

    def bst_insert(self, value):
        """返回新建的 Node 或 None（已存在）。不自动平衡。"""
        if not self.root:
            self.root = Node(value)
            # root.parent = None (already None by default)
            return self.root

        parent = None
        cur = self.root
        while cur:
            c = compare_values(value, cur.value)
            if c == 0:
                return None  # 已存在
            parent = cur
            cur = cur.left if c < 0 else cur.right

        n = Node(value)
        n.parent = parent
        if compare_values(value, parent.value) < 0:
            parent.left = n
        else:
            parent.right = n
        return n

    # ---- 插入后平衡（对应 balanceInsert）----

    def balance_insert(self, z):
        """从 z 向上平衡"""
        cur = z.parent
        while cur:
            old_h = cur.height
            upd(cur)
            b = get_balance(cur)

            if b > 1:
                if get_balance(cur.left) >= 0:
                    # LL
                    self.rotate_right_at(cur)
                else:
                    # LR
                    self.rotate_left_at(cur.left)
                    self.rotate_right_at(cur)
                break  # AVL: 一次旋转足够

            if b < -1:
                if get_balance(cur.right) <= 0:
                    # RR
                    self.rotate_left_at(cur)
                else:
                    # RL
                    self.rotate_right_at(cur.right)
                    self.rotate_left_at(cur)
                break

            if cur.height == old_h:
                break
            cur = cur.parent

    def insert(self, value):
        """完整插入操作"""
        z = self.bst_insert(value)
        if not z:
            return False  # 已存在
        self.size += 1
        self.balance_insert(z)
        return True

    # ---- 删除辅助（transplant / deleteOneChild / balanceDelete）----

    def transplant(self, target, child):
        """把 target 在树中的位置替换为 child（与 C++ transplant 一致）"""
        p = target.parent
        if not p:
            self.root = child
            if self.root:
                self.root.parent = None     # 新根的 parent 必须为空
        elif p.left is target:
            p.left = child
            if p.left:
                p.left.parent = p           # 更新新子的 parent
        else:
            p.right = child
            if p.right:
                p.right.parent = p         # 更新新子的 parent

    def delete_one_child(self, target):
        """删除至多一个子节点的 target，并启动平衡（与 C++ deleteOneChild 一致）"""
        p = target.parent

        if not target.left and not target.right:
            self.transplant(target, None)              # 叶子 → 直接移除
        elif target.left:
            self.transplant(target, target.left)        # 只有左孩子
        else:
            self.transplant(target, target.right)       # 只有右孩子
        # target 离开作用域后即被 Python GC 回收（类似 C++ unique_ptr 离开作用域）

        # ★ 从 parent 开始向上平衡（C++ 版本在 deleteOneChild 内调用 balanceDelete）
        self.balance_delete(p)

    def balance_delete(self, node):
        """从 node 向上平衡（删除可能需要多次旋转）"""
        while node:
            upd(node)
            b = get_balance(node)

            if b > 1:
                if get_balance(node.left) >= 0:
                    node = self.rotate_right_at(node)
                else:
                    self.rotate_left_at(node.left)
                    node = self.rotate_right_at(node)
                continue

            if b < -1:
                if get_balance(node.right) <= 0:
                    node = self.rotate_left_at(node)
                else:
                    self.rotate_right_at(node.right)
                    node = self.rotate_left_at(node)
                continue

            node = node.parent

    def remove(self, value):
        """完整删除操作"""
        if not self.root:
            return False

        # BST 查找
        z = self.root
        while z:
            c = compare_values(value, z.value)
            if c == 0:
                break
            z = z.left if c < 0 else z.right
        if not z:
            return False  # 未找到

        # 双子节点 → 后继替换
        if z.left and z.right:
            succ = z.right
            while succ.left:
                succ = succ.left
            sval = succ.value
            z.value = sval  # 值替换
            z = succ        # 改为删后继（后继至多一个子节点）

        self.delete_one_child(z)
        self.size -= 1
        return True


# ===================== 测试套件 =====================

def test_basic():
    """基础功能测试"""
    print("=== Test 1: Basic insert ===")
    t = AVLTree()
    for v in [10, 20, 30, 25, 28]:
        t.insert(str(v))
    ok, msg = check_avl(t.root)
    print(f"  Insert [10,20,30,25,28]: {msg}")
    assert ok, f"BASIC INSERT FAIL: {msg}"
    
    vals = [x[0] for x in collect_nodes(t.root)]
    print(f"  Inorder: {vals}")
    assert vals == ['10','20','25','28','30'], f"Bad order: {vals}"
    print("  PASS\n")


def test_ll_rotation():
    """LL 旋转测试"""
    print("=== Test 2: LL Rotation ===")
    t = AVLTree()
    # 插入 30, 20, 10 → LL @ 30
    for v in [30, 20, 10]:
        t.insert(str(v))
    ok, msg = check_avl(t.root)
    print(f"  LL (30,20,10): {msg}")
    assert ok, f"LL FAIL: {msg}"
    
    # 根应该是 20
    assert t.root.value == '20', f"Root should be 20, got {t.root.value}"
    assert t.root.left.value == '10'
    assert t.root.right.value == '30'
    assert t.root.parent is None
    assert t.root.left.parent is t.root
    assert t.root.right.parent is t.root
    print("  Structure verified: root=20, left=10, right=30")
    print("  PASS\n")


def test_rr_rotation():
    """RR 旋转测试"""
    print("=== Test 3: RR Rotation ===")
    t = AVLTree()
    # 插入 10, 20, 30 → RR @ 10
    for v in [10, 20, 30]:
        t.insert(str(v))
    ok, msg = check_avl(t.root)
    print(f"  RR (10,20,30): {msg}")
    assert ok, f"RR FAIL: {msg}"
    assert t.root.value == '20'
    print("  PASS\n")


def test_lr_rotation():
    """LR 旋转测试"""
    print("=== Test 4: LR Rotation ===")
    t = AVLTree()
    # 插入 30, 10, 20 → LR @ 30
    for v in [30, 10, 20]:
        t.insert(str(v))
    ok, msg = check_avl(t.root)
    print(f"  LR (30,10,20): {msg}")
    assert ok, f"LR FAIL: {msg}"
    assert t.root.value == '20'
    assert t.root.left.value == '10'
    assert t.root.right.value == '30'
    print("  PASS\n")


def test_rl_rotation():
    """RL 旋转测试"""
    print("=== Test 5: RL Rotation ===")
    t = AVLTree()
    # 插入 10, 30, 20 → RL @ 10
    for v in [10, 30, 20]:
        t.insert(str(v))
    ok, msg = check_avl(t.root)
    print(f"  RL (10,30,20): {msg}")
    assert ok, f"RL FAIL: {msg}"
    assert t.root.value == '20'
    print("  PASS\n")


def test_delete_leaf():
    """删除叶子节点"""
    print("=== Test 6: Delete leaf ===")
    t = AVLTree()
    for v in [20, 10, 30]:
        t.insert(str(v))
    t.remove('10')
    ok, msg = check_avl(t.root)
    print(f"  After del leaf 10 from (20,10,30): {msg}")
    assert ok, f"DEL LEAF FAIL: {msg}"
    assert t.root.left is None
    assert t.size == 2
    print("  PASS\n")


def test_delete_one_child():
    """删除单子节点"""
    print("=== Test 7: Delete one-child ===")
    t = AVLTree()
    # 构造: 20 为根, 10 有左孩子 5
    for v in [20, 10, 5, 30]:
        t.insert(str(v))
    t.remove('10')
    ok, msg = check_avl(t.root)
    print(f"  After del one-child 10: {msg}")
    assert ok, f"DEL ONE CHILD FAIL: {msg}"
    assert t.root.left.value == '5' if t.root.left else True
    print("  PASS\n")


def test_delete_two_children():
    """删除双子节点（后继替换）"""
    print("=== Test 8: Delete two-children (successor) ===")
    t = AVLTree()
    for v in [50, 30, 70, 20, 40, 60, 80]:
        t.insert(str(v))
    t.remove('30')  # 30 的右子树最小是 40
    ok, msg = check_avl(t.root)
    print(f"  After del 30 (has both children): {msg}")
    assert ok, f"DEL TWO CHILD FAIL: {msg}"
    vals = [x[0] for x in collect_nodes(t.root)]
    print(f"  Inorder after del 30: {vals}")
    assert '30' not in vals
    print("  PASS\n")


def test_delete_root():
    """删除根节点"""
    print("=== Test 9: Delete root ===")
    t = AVLTree()
    for v in [20, 10, 30]:
        t.insert(str(v))
    t.remove('20')
    ok, msg = check_avl(t.root)
    print(f"  After del root 20: {msg}")
    assert ok, f"DEL ROOT FAIL: {msg}"
    assert t.root.value in ('10', '30')  # 取决于实现细节
    print("  PASS\n")


def test_random_insert_delete(rounds=2000):
    """随机压力测试"""
    print(f"=== Test 10: Random stress ({rounds} rounds) ===")
    random.seed(42)
    pool = list(range(1, 101))  # 值域 1-100
    t = AVLTree()
    ops = {'insert': 0, 'delete': 0, 'dup': 0, 'nf': 0}
    failures = []
    
    for i in range(rounds):
        op = random.choice(['ins', 'del', 'del'])
        val = str(random.choice(pool))

        if op == 'ins':
            if t.insert(val):
                ops['insert'] += 1
            else:
                ops['dup'] += 1
        else:
            if t.remove(val):
                ops['delete'] += 1
            else:
                ops['nf'] += 1

        # 每 10 步检查一次（加速）
        if i % 10 == 0:
            ok, msg = check_avl(t.root)
            if not ok:
                failures.append(f"Round {i}: {msg}")
                break

    ok, msg = check_avl(t.root)
    print(f"  Ops: ins={ops['insert']} del={ops['delete']} dup={ops['dup']} nf={ops['nf']}")
    print(f"  Final size={t.size}, tree valid: {msg}")
    
    if failures:
        print(f"  FAILURES: {failures}")
    assert ok, f"RANDOM FAIL: {msg}"
    print("  PASS\n")


def test_known_crash_sequence():
    """测试已知的崩溃序列（用户之前触发的操作）"""
    print("=== Test 11: Known crash sequences ===")
    
    # 序列 1: 连续插入触发旋转
    sequences = [
        ("insert 11,14,12", ["11","14","12"]),
        ("insert 1..7 ascending", [str(i) for i in range(1,8)]),
        ("insert 7..1 descending", [str(i) for i in range(7,0,-1)]),
        ("mixed ins/del", ["50","25","75","10","30","60","90","5","15",
                           "27","35","62","80","95","remove_50","remove_25",
                           "remove_75","remove_10"]),
    ]
    
    for name, seq in sequences:
        reset_id()
        t = AVLTree()
        try:
            for item in seq:
                if item.startswith("remove_"):
                    val = item[7:]
                    t.remove(val)
                else:
                    t.insert(item)
            ok, msg = check_avl(t.root)
            status = "PASS" if ok else f"FAIL: {msg}"
            print(f"  [{name}]: {status}")
            assert ok, f"CRASH SEQ FAIL [{name}]: {msg}"
        except Exception as e:
            print(f"  [{name}]: CRASH: {e}")
            raise
    print()


def test_parent_consistency_after_rotations():
    """旋转后的 parent 指针一致性专项测试"""
    print("=== Test 12: Parent pointer consistency after rotations ===")
    t = AVLTree()
    
    # 构造一棵会触发多种旋转的树
    values = [50, 25, 75, 10, 30, 60, 85, 5, 15, 27, 35,
              55, 65, 80, 90, 3, 8, 12, 18, 28, 33]
    for v in values:
        t.insert(str(v))
    
    ok, msg = check_avl(t.root)
    print(f"  After complex inserts: {msg}")
    assert ok, f"PARENT CONSISTENCY INS FAIL: {msg}"

    # 做一些删除
    for to_del in ['25', '50', '75']:
        t.remove(to_del)
        ok, msg = check_avl(t.root)
        assert ok, f"PARENT CONSISTENCY DEL({to_del}) FAIL: {msg}"
    print(f"  After deletes: {msg}")
    print("  PASS\n")


# ===================== 主入口 =====================

if __name__ == '__main__':
    tests = [
        test_basic,
        test_ll_rotation,
        test_rr_rotation,
        test_lr_rotation,
        test_rl_rotation,
        test_delete_leaf,
        test_delete_one_child,
        test_delete_two_children,
        test_delete_root,
        test_known_crash_sequence,
        test_parent_consistency_after_rotations,
    ]

    passed = 0
    failed = 0
    for fn in tests:
        try:
            fn()
            passed += 1
        except Exception as e:
            print(f"  ✗ {fn.__name__} FAILED: {e}\n")
            failed += 1

    # 随机测试单独跑（参数化）
    try:
        test_random_insert_delete(3000)
        passed += 1
    except Exception as e:
        print(f"  ✗ test_random_insert_delete FAILED: {e}\n")
        failed += 1

    print("=" * 50)
    print(f"Results: {passed} PASSED, {failed} FAILED out of {len(tests)+1} tests")
    if failed == 0:
        print("ALL TESTS PASSED ✓ — 第10版 AVL (parent+inplace) 算法正确！")
    else:
        sys.exit(1)
