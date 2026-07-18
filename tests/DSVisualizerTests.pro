# DSVisualizerTests - standalone unit tests for the pure-C++ core engine.
# No Qt required; builds with just the MinGW compiler bundled with Qt 5.12.11.
#
# Build & run:
#   qmake DSVisualizerTests.pro && mingw32-make && debug\DSVisualizerTests.exe

TEMPLATE = app
TARGET   = DSVisualizerTests

# Do NOT link Qt at all
CONFIG -= qt
QT     -= core gui
CONFIG += console c++17
QMAKE_CXXFLAGS += -std=c++17

INCLUDEPATH += ../src

SOURCES += ../tests/test_core.cpp
