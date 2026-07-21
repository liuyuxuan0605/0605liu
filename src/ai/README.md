# AI 讲解助教外挂（Qt Plugin）

把 RAG 能力做成**独立插件**，主程序运行期通过 `QPluginLoader` 加载；DLL 不存在或加载失败 → 主程序**静默跳过**，零 AI 依赖照常运行。这就是"外挂"的核心：插上就有，拔掉照跑。

## 已集成到 MainWindow

`MainWindow::loadAiPlugin()` 已实现（在构造函数末尾调用）：

- 按多个候选路径查找 `aichatplugin.dll`（覆盖 Qt Creator 影子构建、手动部署等情形）
- `QPluginLoader` 加载 → `qobject_cast<AIPluginInterface*>` → `createDock(m_animator, m_scene)`
- 把返回控件挂到右停靠区（`QDockWidget("AI 讲解助教")`）
- `loader` 作为成员保持存活，避免插件被提前卸载导致 Dock 悬空崩溃

> 注意：`src/ai/aiplugininterface.h` 是主程序与插件共享的接口契约，MainWindow 编译时 include 它。

## 文件

- `aiplugininterface.h`：插件接口（`createDock(StepAnimator*, DSScene*)`）
- `aichatplugin.h/.cpp`：Dock 实现，监听 `StepAnimator::frameChanged`，把当前帧上下文 POST 给 `rag-service`，收到回答后调用 `DSScene::highlightByValue` 联动高亮
- 联动依赖 `DSScene::highlightByValue / clearHighlights`（已在 `DSScene.h/.cpp` 增量添加）

## 构建（两步，产物自动对齐到 bin/）

主程序与插件都通过 `DESTDIR` 输出到统一的 `bin/` 结构，QPluginLoader 一定能找到 DLL。

```bash
# 1) 主程序 → bin/DSVisualizer.exe
qmake DSVisualizer.pro
mingw32-make

# 2) 插件 → bin/plugins/aichatplugin.dll（务必与主程序同 Qt 版本 / 同编译器 MinGW 7.3）
cd src/ai
qmake aiplugin.pro
mingw32-make
cd ../..
```

> 插件必须和主程序使用**相同的 Qt 版本与编译器**，否则 `QPluginLoader` 加载失败（此时主程序自动禁用 AI，不影响运行）。

## 运行顺序

```bash
# 终端 A：启动 RAG 后端（默认 naive+offline，零依赖）
cd rag-service
python server.py

# 终端 B：启动主程序
cd bin
DSVisualizer.exe
```

打开后在左侧选 AVLTree 点"演示预设"，右侧"AI 讲解助教"Dock 会**自动跟随每一帧**讲解原理，并把回答里涉及的节点（如 `[15, 20]`）**高亮到图上**；也可在 Dock 输入框手动提问。

## 切换到语义检索 / 真实 LLM

编辑 `rag-service/.env`（先 `cp .env.example .env`）：

```
RETRIEVER=chroma          # 语义向量检索（需 pip install chromadb）
LLM_PROVIDER=openai       # 调用大模型总结（需 OPENAI_API_KEY）
OPENAI_API_KEY=sk-xxxx
OPENAI_BASE_URL=https://api.openai.com/v1   # 或兼容端点
```

然后 `pip install -r rag-service/requirements.txt`，重启 `python rag-service/app.py`（生产入口）即可。Qt 端无需改代码。
