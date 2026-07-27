"""扩展标注集 2：29 条新增测试查询（总计 51+29=80 条）。

覆盖维度（与前两批互补）：
- "为什么"类（原理追问，非"怎么做"）
- 反事实/否定问法（"如果不做X会怎样"）
- 中英混杂 / 非标准术语
- 极短模糊查询（2-5 个字）
- 应用场景选型（"什么情况下该用"）
- 同族结构内部对比（队列家族、链表家族）
- 实现细节追问（指针/内存/并发）
- 多跳组合问题（需要跨 chunk 拼答案）
"""

NEW_QUERIES_2 = [
    # ========== "为什么"类（原理追问）==========
    {"q": "为什么红黑树不要求严格平衡还能保证O(logn)",
     "structure": "RedBlackTree",
     "rel": ["notes/node_coloring.md", "generated/RedBlackTree.md", "notes/avl_vs_rbtree.md"]},

    {"q": "为什么B+树的叶子节点要用链表串起来",
     "structure": "BPlusTree",
     "rel": ["generated/BPlusTree.md", "notes/b_tree_operations.md"]},

    {"q": "为什么哈希表负载因子到0.75就要扩容",
     "structure": "HashMap",
     "rel": ["knowledge/hashtable.md", "generated/HashMap.md", "notes/hash_collision.md"]},

    {"q": "为什么LRU用哈希表加双向链表而不是只用数组",
     "structure": "LRUCache",
     "rel": ["notes/lru_mechanism.md", "generated/LRUCache.md", "generated/DoublyLinkedList.md"]},

    # ========== 反事实 / "如果不做X会怎样" ==========
    {"q": "AVL树如果不做旋转直接插会退化成什么样",
     "structure": "AVLTree",
     "rel": ["notes/avl_rotation.md", "generated/AVLTree.md", "knowledge/bst.md"]},

    {"q": "哈希表如果不处理冲突所有元素都堆一个桶里会怎样",
     "structure": "HashMap",
     "rel": ["notes/hash_collision.md", "knowledge/hashtable.md", "generated/HashMap.md"]},

    {"q": "堆如果插入后不做上浮调整还能保证堆序性吗",
     "structure": "MinHeap",
     "rel": ["notes/heapify.md", "generated/MinHeap.md", "knowledge/heap.md"]},

    {"q": "并查集不做路径压缩最坏复杂度是多少",
     "structure": "UFDS",
     "rel": ["knowledge/ufds.md"]},

    # ========== 中英混杂 / 非标准术语 ==========
    {"q": "red-black tree的rotate操作什么时候触发",
     "structure": "RedBlackTree",
     "rel": ["notes/rb_insert.md", "notes/rb_delete.md", "generated/RedBlackTree.md"]},

    {"q": "hashmap的rehash和resize是一回事吗",
     "structure": "HashMap",
     "rel": ["generated/HashMap.md", "knowledge/hashtable.md", "notes/hash_collision.md"]},

    {"q": "binary search tree的successor怎么找",
     "structure": "BinarySearchTree",
     "rel": ["generated/BinarySearchTree.md", "notes/bst_delete.md", "knowledge/bst.md"]},

    {"q": "heap的top k问题一般怎么解",
     "structure": "",
     "rel": ["knowledge/heap.md", "generated/MinHeap.md", "notes/heapify.md"]},

    # ========== 极短模糊查询 ==========
    {"q": "左旋右旋",
     "structure": "AVLTree",
     "rel": ["notes/avl_rotation.md", "generated/AVLTree.md"]},

    {"q": "双黑",
     "structure": "RedBlackTree",
     "rel": ["notes/rb_delete.md", "generated/RedBlackTree.md"]},

    {"q": "开放寻址",
     "structure": "HashMap",
     "rel": ["notes/hash_collision.md", "knowledge/hashtable.md", "generated/HashMap.md"]},

    {"q": "层序遍历",
     "structure": "Graph",
     "rel": ["notes/graph_traversal.md", "knowledge/dfsbfs.md", "generated/Graph.md"]},

    # ========== 应用场景选型 ==========
    {"q": "实现一个消息队列应该用哪种数据结构",
     "structure": "",
     "rel": ["notes/queue_family.md", "generated/Queue.md", "generated/BlockingQueue.md", "generated/CircularQueue.md"]},

    {"q": "浏览器的前进后退功能用什么结构实现",
     "structure": "",
     "rel": ["notes/stack_selection.md", "generated/Stack.md", "generated/DoublyLinkedList.md"]},

    {"q": "操作系统任务调度适合用什么结构",
     "structure": "",
     "rel": ["knowledge/heap.md", "generated/MinHeap.md", "generated/Queue.md"]},

    # ========== 同族结构内部对比 ==========
    {"q": "单链表双链表循环链表各自的优势在哪",
     "structure": "",
     "rel": ["generated/SinglyLinkedList.md", "generated/DoublyLinkedList.md",
             "generated/CircularQueue.md", "knowledge/list.md"]},

    {"q": "普通队列循环队列阻塞队列分别解决什么问题",
     "structure": "",
     "rel": ["notes/queue_family.md", "generated/Queue.md", "generated/CircularQueue.md", "generated/BlockingQueue.md"]},

    # ========== 实现细节追问 ==========
    {"q": "红黑树旋转的时候parent指针怎么更新才不会断",
     "structure": "RedBlackTree",
     "rel": ["notes/rb_insert.md", "notes/rb_delete.md", "generated/RedBlackTree.md"]},

    {"q": "B树分裂时中间key上提到父节点具体怎么操作的",
     "structure": "BTree",
     "rel": ["notes/b_tree_operations.md", "generated/BTree.md"]},

    {"q": "图的邻接表和邻接矩阵存稀疏图哪个更省空间",
     "structure": "Graph",
     "rel": ["knowledge/graphds.md", "generated/Graph.md"]},

    # ========== 多跳组合（需跨 chunk 拼答案）==========
    {"q": "AVL树的旋转和堆的sift up有什么共同点",
     "structure": "",
     "rel": ["notes/avl_rotation.md", "notes/heapify.md", "knowledge/heap.md"]},

    {"q": "用栈实现递归转迭代的一般方法是什么",
     "structure": "",
     "rel": ["generated/Stack.md", "knowledge/recursion.md"]},

    {"q": "Dijkstra里面用的优先队列是不是就是最小堆",
     "structure": "Graph",
     "rel": ["knowledge/sssp.md", "knowledge/heap.md", "generated/MinHeap.md"]},

    # ========== 面试高频综合题 ==========
    {"q": "手写一个LRU要多久，关键难点在哪",
     "structure": "LRUCache",
     "rel": ["notes/lru_mechanism.md", "generated/LRUCache.md", "generated/DoublyLinkedList.md"]},

    {"q": "面试被问到红黑树怎么答才能不翻车",
     "structure": "RedBlackTree",
     "rel": ["notes/node_coloring.md", "notes/rb_insert.md", "notes/rb_delete.md",
             "generated/RedBlackTree.md", "notes/avl_vs_rbtree.md"]},
]
