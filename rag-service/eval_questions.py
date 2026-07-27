"""检索质量评估的标注集（ground truth）。

每条标注包含：
- q         : 模拟用户提出的真实问题（中文口语化）
- structure : 当前正在查看的数据结构（对应 app 里 context.structure）。
              "" 表示没有特定结构上下文（例如从面试笔记/通用问题入口提问），
              此时检索器不做结构过滤，纯靠相关性召回——用于暴露跨结构检索能力。
- rel       : 与本问题相关的源文档列表（相对 data/ 的路径，统一用正斜杠）。
              只要 top-k 里出现其中任意一个文档，即算"命中"。

标注口径：rel 里的文档是"真正包含该问题答案"的资料，而非泛泛提及。
多写几个相关文档更稳妥，避免漏标导致指标偏低（属于保守标注）。

注意：structure 的取值必须与数据里 frontmatter 的 structure 字段一致，
否则检索器会按结构过滤掉这些文档，评估就测的是"结构过滤 + 检索"的合效果。
"""

QUERIES = [
    # ---- 红黑树（structure=RedBlackTree 会召回 generated/RedBlackTree + notes/rb_*）----
    {"q": "红黑树删除一个节点后怎么保持平衡、怎么修复",
     "structure": "RedBlackTree",
     "rel": ["generated/RedBlackTree.md", "notes/rb_delete.md", "notes/node_coloring.md"]},
    {"q": "红黑树插入时颜色冲突怎么修复",
     "structure": "RedBlackTree",
     "rel": ["generated/RedBlackTree.md", "notes/rb_insert.md"]},
    {"q": "红黑树的节点颜色有哪些性质/规则",
     "structure": "RedBlackTree",
     "rel": ["generated/RedBlackTree.md", "notes/node_coloring.md"]},
    {"q": "红黑树删除的双黑问题怎么处理",
     "structure": "RedBlackTree",
     "rel": ["notes/rb_delete.md", "generated/RedBlackTree.md"]},

    # ---- AVL 树 ----
    {"q": "AVL树怎么通过旋转修复失衡",
     "structure": "AVLTree",
     "rel": ["generated/AVLTree.md", "notes/avl_rotation.md"]},
    {"q": "AVL树删除节点后怎么重新平衡",
     "structure": "AVLTree",
     "rel": ["generated/AVLTree.md", "notes/avl_delete.md"]},
    {"q": "AVL树什么时候用左旋、什么时候用右旋",
     "structure": "AVLTree",
     "rel": ["notes/avl_rotation.md", "generated/AVLTree.md"]},

    # ---- 哈希表 ----
    {"q": "哈希表怎么解决哈希冲突",
     "structure": "HashMap",
     "rel": ["generated/HashMap.md", "notes/hash_collision.md", "knowledge/hashtable.md"]},
    {"q": "哈希表什么时候扩容、怎么 rehash",
     "structure": "HashMap",
     "rel": ["generated/HashMap.md", "knowledge/hashtable.md", "notes/hash_collision.md"]},

    # ---- B 树 / B+ 树 ----
    {"q": "B树插入时节点什么时候分裂",
     "structure": "BTree",
     "rel": ["generated/BTree.md", "notes/b_tree_operations.md", "scenarios/btree_split_demo.md"]},
    {"q": "B+树和B树有什么区别",
     "structure": "BPlusTree",
     "rel": ["generated/BPlusTree.md", "notes/b_tree_operations.md"]},

    # ---- 最小堆 ----
    {"q": "最小堆怎么下沉调整（sift down / heapify）",
     "structure": "MinHeap",
     "rel": ["generated/MinHeap.md", "notes/heapify.md", "knowledge/heap.md"]},

    # ---- 二叉搜索树 ----
    {"q": "二叉搜索树删除有两个孩子的节点怎么处理",
     "structure": "BinarySearchTree",
     "rel": ["generated/BinarySearchTree.md", "notes/bst_delete.md", "knowledge/bst.md"]},
    {"q": "二叉搜索树怎么插入一个新值",
     "structure": "BinarySearchTree",
     "rel": ["generated/BinarySearchTree.md", "notes/bst_insert.md", "knowledge/bst.md"]},

    # ---- LRU 缓存 ----
    {"q": "LRU缓存怎么淘汰最久没使用的元素",
     "structure": "LRUCache",
     "rel": ["generated/LRUCache.md", "notes/lru_mechanism.md"]},

    # ---- 图 ----
    {"q": "图的深度优先和广度优先遍历分别怎么实现",
     "structure": "Graph",
     "rel": ["notes/graph_traversal.md", "knowledge/dfsbfs.md", "knowledge/graphds.md"]},

    # ---- 并查集 ----
    {"q": "并查集怎么实现，路径压缩是什么",
     "structure": "UFDS",
     "rel": ["knowledge/ufds.md"]},

    # ---- 跨结构 / 通用问题（structure="" 不做结构过滤）----
    {"q": "链表和数组有什么区别",
     "structure": "",
     "rel": ["knowledge/list.md", "knowledge/array.md",
             "generated/SinglyLinkedList.md", "generated/DoublyLinkedList.md"]},
    {"q": "常见的排序算法时间复杂度是多少",
     "structure": "",
     "rel": ["knowledge/sorting.md", "knowledge/heap.md", "knowledge/segmenttree.md"]},
    {"q": "堆排序怎么利用堆来完成排序",
     "structure": "",
     "rel": ["knowledge/heap.md", "notes/heapify.md", "generated/MinHeap.md"]},
    {"q": "AVL树和红黑树有什么区别，各自适合什么场景",
     "structure": "",
     "rel": ["generated/AVLTree.md", "generated/RedBlackTree.md", "notes/avl_rotation.md",
             "notes/avl_vs_rbtree.md"]},
]
