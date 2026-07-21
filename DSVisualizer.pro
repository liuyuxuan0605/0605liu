# DSVisualizer - qmake project file (Qt 5.12.11 + MinGW 7.3)
#
# How to build:
#   Option A (Qt Creator):  File -> Open File or Project -> select this DSVisualizer.pro
#                           -> pick "Desktop Qt 5.12.11 MinGW 64-bit" -> Configure -> Build (hammer) -> Run
#   Option B (command line): qmake DSVisualizer.pro && mingw32-make
#
# The core data-structure engine (src/core/*.h) is header-only, pure C++17,
# and does NOT depend on Qt, so it can also be unit-tested standalone
# (see tests/DSVisualizerTests.pro).

QT += widgets

TARGET  = DSVisualizer
TEMPLATE = app

# 统一产物到 bin/，与 AI 插件对齐，便于 QPluginLoader 定位
DESTDIR = $$PWD/bin

# 让 AI 插件 DLL 能反向调用主程序中的 DSScene / StepAnimator：
# 导出 EXE 全部符号，并生成导入库 bin/libDSVisualizer.a，供插件链接。
win32 {
    QMAKE_LFLAGS += -Wl,--export-all-symbols -Wl,--out-implib,bin/libDSVisualizer.a
}

# C++17 (MinGW 7.3 supports it)
CONFIG += c++17
QMAKE_CXXFLAGS += -std=c++17

INCLUDEPATH += src

# --- Compiled translation units ---
SOURCES += \
    src/app/main.cpp \
    src/visual/LayoutEngine.cpp \
    src/visual/DSScene.cpp \
    src/ui/OperationPanel.cpp \
    src/ui/LogViewer.cpp \
    src/ui/MainWindow.cpp

# --- Headers (qmake/moc processes those containing Q_OBJECT) ---
HEADERS += \
    src/core/Common.h \
    src/core/IDataStructure.h \
    src/core/Factory.h \
    src/core/SinglyLinkedList.h \
    src/core/DoublyLinkedList.h \
    src/core/Stack.h \
    src/core/Queue.h \
    src/core/BinarySearchTree.h \
    src/core/AVLTree.h \
    src/core/RedBlackTree.h \
    src/core/HashMap.h \
    src/core/Deque.h \
    src/core/BlockingQueue.h \
    src/core/BTree.h \
    src/core/BPlusTree.h \
    src/core/RingBuffer.h \
    src/core/Graph.h \
    src/core/LRUCache.h \
    src/visual/VisualNode.h \
    src/visual/VisualEdge.h \
    src/visual/LayoutEngine.h \
    src/visual/DSScene.h \
    src/visual/StepAnimator.h \
    src/ui/OperationPanel.h \
    src/ui/LogViewer.h \
    src/ui/MainWindow.h
