# 预设序列（Presets）

当前演示序列在 `src/ui/MainWindow.cpp` 的 `buildPreset()` 中内置，
按当前选择的数据结构自动生成一组操作。未来可改为从此目录加载 JSON：

```json
{
  "kind": "AVLTree",
  "steps": [
    { "op": "insert", "value": "30" },
    { "op": "insert", "value": "20" },
    { "op": "insert", "value": "10" },
    { "op": "remove", "value": "30" }
  ]
}
```

op 取值：`insert`（列表/树/堆/哈希表）、`remove`、`find`、`clear`。
哈希表的 value 用 `key:value` 格式。
