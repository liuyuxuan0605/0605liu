# Overview — jump_to_structure 全链路落地

## 完成内容
前端 `MainWindow` 侧补全后，AI 讲解插件的"跳转数据结构"能力已端到端打通：用户说"切换到 AVL 树"，AI 返回 `actions`，前端自动重建对应结构视图。

## 改动文件（均在 `D:\ai_canshow\DSVisualizer_push`）
1. `src/core/Factory.h` — 新增 `kindFromString()`，把后端返回的结构名字符串映射成 `DSKind`（与 `kindToString` 完全对应，16 个结构）。
2. `src/ui/MainWindow.cpp` — 新增 `switchStructure(const QString&)` 槽；在 `loadAiPlugin()` 内用 `qobject_cast<AIChatPlugin*>` 把插件 `requestJump` 信号连接到该槽。
3. `src/ai/aichatplugin.h` / `.cpp` —（前几轮已完成）声明 `requestJump` 信号；`onReply` 解析 `actions` 并 emit。
4. `rag-service/llm.py` / `server.py` —（前几轮已完成）四元组返回 + `actions` 透传，`py_compile` 通过。

## 数据流
```
LLM 返回 {"actions":[{"type":"jump","structure":"AVLTree"}]}
  → server.py answer() 透传 actions
  → aichatplugin.cpp onReply 解析并 emit requestJump("AVLTree")
  → MainWindow::switchStructure 解析字符串 → switchKind 重建视图
     （下拉框同步、画布重置，QSignalBlocker 防递归已确认）
```

## 静态审查要点
- `OperationPanel::setKindIndex` 用 `QSignalBlocker` 包裹，AI 跳转不会递归触发 `kindChanged`。
- `llm.py` SYSTEM_PROMPT 枚举名与 `kindFromString` 字符串逐一一致。
- C++ 改动：仅新增 include + 一个槽 + 一处 connect，无既有逻辑修改；信号/槽签名匹配。

## ⚠️ 待你验证（重要）
沙箱无 MinGW，**我无法编译 Qt 程序**。请在 `DSVisualizer_push` 副本执行：
```bash
qmake && mingw32-make
```
并重生成 `aichatplugin.dll` 放到 exe 旁 `plugins/`。然后：
1. 启动后端：`cd rag-service && python server.py`
2. 运行主程序，在 AI 面板问"切换到 AVL 树" / "演示一下红黑树"
3. 应看到主视图自动切到对应结构。

若编译报错，把**第一行 error** 发我，我立刻定位。
