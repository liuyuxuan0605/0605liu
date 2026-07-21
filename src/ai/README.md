# AI 讲解助教外挂（Qt Plugin）

把 RAG 能力做成**独立插件**，主程序编译期不链接任何 AI / 网络库：
插件 DLL 不存在 → 主程序没有这个功能；存在 → 自动挂载“AI 讲解” Dock。

## 文件
- `aiplugininterface.h`：插件接口（`createDock`）。
- `aichatplugin.h/.cpp`：Dock 实现，监听 `StepAnimator::frameChanged`，
  把当前帧上下文 POST 给 `rag-service`，收到回答后调用 `DSScene::highlightByValue` 联动高亮。
- 联动依赖 `DSScene::highlightByValue`（已在 `DSScene.h/.cpp` 增量添加）。

## 集成到 MainWindow（一次性 patch，建议用宏开关包起来）
在 `MainWindow.cpp` 顶部加 include：
```cpp
#include "ai/aiplugininterface.h"
#include <QPluginLoader>
#include <QDockWidget>
#include <QFile>
```
在构造函数 `setup` 之后（确保 `m_scene` / `m_animator` 已创建）加入：
```cpp
#ifdef DSV_ENABLE_AI_PLUGIN
    const QString pluginPath = "plugins/aichatplugin.dll"; // macOS/Linux 换成 .so
    if (QFile::exists(pluginPath)) {
        QPluginLoader loader(pluginPath);
        auto* iface = qobject_cast<AIPluginInterface*>(loader.instance());
        if (iface) {
            QWidget* w = iface->createDock(m_animator, m_scene);
            auto* dw = new QDockWidget("AI 讲解", this);
            dw->setWidget(w);
            addDockWidget(Qt::RightDockWidgetArea, dw);
        } else {
            qWarning() << "AI 插件加载失败:" << loader.errorString();
        }
    }
#endif
```
构建时给 qmake 传 `DEFINES+=DSV_ENABLE_AI_PLUGIN` 才启用。

## 构建插件（独立 qmake 子工程）
见 `aiplugin.pro`，产物放到 `plugins/` 目录即可被主程序在运行时加载。
注意：插件必须和主程序使用**相同的 Qt 版本与编译器**（MinGW 7.3），否则 QPluginLoader 加载失败。

## 运行顺序
1. 启动后端：`cd rag-service && python server.py`（默认 naive+offline，零依赖）。
2. 启动主程序（带插件），操作任意数据结构，右侧 Dock 会自动讲解并高亮节点。
