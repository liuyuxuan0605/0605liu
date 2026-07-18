// AVL 崩溃定位测试（Qt 无关，仅依赖 core/ 头文件）
// 编译（需 MinGW，项目里有）：
//   g++.exe -std=c++17 -O0 -g -fsanitize=address -I. avl_san_test.cpp -o avl_san.exe
// 运行：
//   avl_san.exe
// 若 ASan 不支持 MinGW，则在 Qt Creator 里把它当“非 Qt 控制台项目” Debug 运行（F5），
// 崩溃时会自动停在 AVLTree.h 出错行，把那一行告诉我即可。
#include "src/core/AVLTree.h"
#include <cstdio>
#include <string>
#include <vector>
#include <cstdlib>
#include <ctime>

using namespace dsv;

static void exercise(AVLTree& t, const std::string& v, bool isInsert) {
    if (isInsert) t.insert(v); else t.remove(v);
    // 关键：每次操作后遍历整棵树（snapshotValues / inorder），
    // 如果树结构在旋转后损坏（悬空指针 / use-after-free），这里会立刻崩溃并给出行号。
    std::vector<std::string> vals = t.snapshotValues();
    (void)vals;
}

int main() {
    std::srand(12345);

    // 1) 已知旋转触发序列
    const char* knownSeqs[][8] = {
        {"10","20","30",nullptr},
        {"30","20","10",nullptr},
        {"10","30","20",nullptr},
        {"30","10","20",nullptr},
        {"11","14","12",nullptr},
        {"1","2","3","4","5","6","7",nullptr},
        {"7","6","5","4","3","2","1",nullptr},
        {"50","30","70","20","40","60","80","10",nullptr},
    };
    for (auto& seq : knownSeqs) {
        AVLTree t;
        for (int i = 0; seq[i]; ++i) {
            exercise(t, seq[i], true);
            printf("[known] insert %s ok, size=%d\n", seq[i], t.size());
        }
    }

    // 2) 随机插入 + 删除混合，每步遍历检测结构损坏
    for (int round = 0; round < 8000; ++round) {
        AVLTree u;
        int ops = 5 + (std::rand() % 25);
        for (int i = 0; i < ops; ++i) {
            std::string v = std::to_string(std::rand() % 60);
            bool ins = (std::rand() % 10) < 6;
            exercise(u, v, ins);
        }
    }

    printf("ALL DONE - no crash\n");
    return 0;
}
