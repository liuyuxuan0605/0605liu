"""扩展标注集：30 条新增测试查询。

覆盖维度：
- 口语化/模糊问法（真实用户不会说"sift down"，会说"那个往下沉的操作"）
- 原 21 条未覆盖的结构（栈、队列、双端队列、单/双链表、环形缓冲、阻塞队列）
- 图算法进阶（最短路、最小生成树、环检测）
- 高级结构（线段树、树状数组）
- 跨结构对比 & 选型题
- 复杂度/分析类
- 边界/陷阱问法（"如果…会怎样"）

使用方式：把 NEW_QUERIES 追加到 eval_questions.py 的 QUERIES 列表末尾，
或在 eval_retrieval.py 里 import 后合并：
    from eval_questions_ext import NEW_QUERIES
    QUERIES = QUERIES + NEW_QUERIES
"""

NEW_QUERIES = [
    # ========== 口语化 / 模糊问法（测鲁棒性）==========
    {"q": "那个树转来转去的是怎么回事",
     "structure": "AVLTree",
     "rel": ["notes/avl_rotation.md", "generated/AVLTree.md"]},

    {"q": "就是那个红黑色的树，插进去之后颜色不对了咋办",
     "structure": "RedBlackTree",
     "rel": ["notes/rb_insert.md", "notes/node_coloring.md", "generated/RedBlackTree.md"]},

    {"q": "哈希表撞了怎么办",
     "structure": "HashMap",
     "rel": ["notes/hash_collision.md", "generated/HashMap.md", "knowledge/hashtable.md"]},

    {"q": "堆那个往下掉的操作是叫啥来着，怎么做的",
     "structure": "MinHeap",
     "rel": ["notes/heapify.md", "generated/MinHeap.md", "knowledge/heap.md"]},

    {"q": "缓存满了踢谁",
     "structure": "LRUCache",
     "rel": ["notes/lru_mechanism.md", "generated/LRUCache.md"]},

    # ========== 原 21 条未覆盖的结构 ==========
    {"q": "栈和队列有什么区别，分别什么场景用",
     "structure": "",
     "rel": ["generated/Stack.md", "generated/Queue.md", "knowledge/list.md"]},

    {"q": "双端队列两端都能进出是怎么实现的",
     "structure": "Deque",
     "rel": ["notes/deque_impl.md", "generated/Deque.md"]},

    {"q": "单链表怎么在某个节点后面插入一个新节点",
     "structure": "SinglyLinkedList",
     "rel": ["notes/singly_linkedlist_ops.md", "generated/SinglyLinkedList.md", "knowledge/list.md"]},

    {"q": "双向链表删除一个节点需要改哪些指针",
     "structure": "DoublyLinkedList",
     "rel": ["notes/doubly_linkedlist_ops.md", "generated/DoublyLinkedList.md", "knowledge/list.md"]},

    {"q": "环形缓冲区满了之后新数据会怎样",
     "structure": "RingBuffer",
     "rel": ["notes/ringbuffer_impl.md", "generated/RingBuffer.md"]},

    {"q": "阻塞队列在多线程里是怎么等待和唤醒的",
     "structure": "BlockingQueue",
     "rel": ["notes/blockingqueue_impl.md", "generated/BlockingQueue.md", "generated/Queue.md"]},

    {"q": "循环队列怎么判断是满还是空",
     "structure": "CircularQueue",
     "rel": ["notes/circularqueue_impl.md", "generated/CircularQueue.md", "generated/Queue.md"]},

    # ========== 图算法进阶 ==========
    {"q": "Dijkstra求最短路为什么不能有负权边",
     "structure": "Graph",
     "rel": ["knowledge/sssp.md", "knowledge/graphds.md", "generated/Graph.md"]},

    {"q": "最小生成树的Kruskal和Prim算法怎么选",
     "structure": "Graph",
     "rel": ["knowledge/mst.md", "knowledge/graphds.md", "generated/Graph.md"]},

    {"q": "怎么判断图里有没有环",
     "structure": "Graph",
     "rel": ["knowledge/cyclefinding.md", "knowledge/dfsbfs.md", "generated/Graph.md"]},

    # ========== 高级结构 ==========
    {"q": "线段树怎么做区间查询和单点更新",
     "structure": "",
     "rel": ["knowledge/segmenttree.md"]},

    {"q": "树状数组和线段树比有什么优劣",
     "structure": "",
     "rel": ["knowledge/fenwicktree.md", "knowledge/segmenttree.md"]},

    # ========== 跨结构对比 & 选型 ==========
    {"q": "什么时候该用哈希表什么时候该用平衡树",
     "structure": "",
     "rel": ["knowledge/hashtable.md", "generated/HashMap.md",
             "generated/AVLTree.md", "generated/RedBlackTree.md"]},

    {"q": "B+树为什么比B树更适合做数据库索引",
     "structure": "BPlusTree",
     "rel": ["generated/BPlusTree.md", "generated/BTree.md", "notes/b_tree_operations.md"]},

    {"q": "用数组实现栈和用链表实现栈各有什么优缺点",
     "structure": "",
     "rel": ["generated/Stack.md", "knowledge/array.md", "knowledge/list.md"]},

    {"q": "优先队列和普通队列有什么区别，底层是不是堆",
     "structure": "",
     "rel": ["knowledge/heap.md", "generated/MinHeap.md", "generated/Queue.md"]},

    # ========== 复杂度 / 分析类 ==========
    {"q": "红黑树和AVL树查找的最坏时间复杂度分别是多少",
     "structure": "",
     "rel": ["notes/avl_vs_rbtree.md", "generated/AVLTree.md",
             "generated/RedBlackTree.md", "interview/complexity_analysis.md"]},

    {"q": "哈希表平均O(1)但最坏情况是什么，为什么会退化",
     "structure": "HashMap",
     "rel": ["notes/hash_collision.md", "knowledge/hashtable.md",
             "generated/HashMap.md", "interview/complexity_analysis.md"]},

    {"q": "各种排序算法哪些是稳定的哪些不稳定",
     "structure": "",
     "rel": ["knowledge/sorting.md", "interview/complexity_analysis.md"]},

    # ========== 边界 / 陷阱 / "如果…会怎样" ==========
    {"q": "AVL树如果连续插入1到7会发生什么，最终长什么样",
     "structure": "AVLTree",
     "rel": ["notes/avl_rotation.md", "generated/AVLTree.md"]},

    {"q": "红黑树如果把根节点染成红色会违反哪条性质",
     "structure": "RedBlackTree",
     "rel": ["notes/node_coloring.md", "generated/RedBlackTree.md"]},

    {"q": "BST如果按顺序插入1234567会退化成什么",
     "structure": "BinarySearchTree",
     "rel": ["generated/BinarySearchTree.md", "knowledge/bst.md", "notes/bst_insert.md"]},

    {"q": "LRU缓存如果容量设成1会怎样",
     "structure": "LRUCache",
     "rel": ["notes/lru_mechanism.md", "generated/LRUCache.md"]},

    # ========== 递归 / 通用算法思想 ==========
    {"q": "递归和迭代有什么区别，什么时候必须用递归",
     "structure": "",
     "rel": ["knowledge/recursion.md", "interview/complexity_analysis.md"]},

    {"q": "位运算能解决哪些常见问题",
     "structure": "",
     "rel": ["knowledge/bitmask.md"]},
]
