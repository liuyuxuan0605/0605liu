#!/bin/bash
# ============================================================
#  启动 DSVisualizer 的 AI 讲解助教后端 (RAG 服务)
#  在 MINGW64 / Git Bash 中运行:  ./start_rag.sh
#  Ctrl+C 停止服务
# ============================================================
cd "/d/ai_canshow/DSVisualizer_push/rag-service" || {
    echo "[错误] 无法进入目录 /d/ai_canshow/DSVisualizer_push/rag-service"
    exit 1
}

PY="D:/ai_course/python.exe"
if [ ! -x "$PY" ]; then
    echo "[提示] 未找到 $PY，尝试使用系统 python 命令"
    PY="python"
fi

echo "============================================================"
echo "  正在启动 RAG 服务 ( http://localhost:8000 ) ..."
echo "  按 Ctrl+C 停止服务。"
echo "============================================================"
"$PY" server.py
