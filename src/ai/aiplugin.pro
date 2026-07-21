# 独立构建 AI 讲解插件（不影响主程序编译依赖）
# qmake aiplugin.pro && mingw32-make
# 产物 aichatplugin.dll 放到主程序同级的 plugins/ 目录
TEMPLATE = lib
CONFIG += plugin
QT += core network widgets
TARGET = aichatplugin
# 与主程序 bin/ 对齐：DSVisualizer.exe 在 bin/，插件在 bin/plugins/
DESTDIR = $$PWD/../../bin/plugins

INCLUDEPATH += $$PWD/../visual $$PWD/../core
DEPENDPATH  += $$PWD/../visual $$PWD/../core

HEADERS += aiplugininterface.h \
           aichatplugin.h
SOURCES += aichatplugin.cpp
