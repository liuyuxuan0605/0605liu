#pragma once
#include <QObject>
#include <QWidget>

namespace dsv {
class StepAnimator;
class DSScene;
}

// 外挂 AI 插件接口：主程序通过 QPluginLoader 加载 .dll/.so，
// 调用 createDock() 拿到“AI 讲解”Dock 控件并挂到右停靠区。
class AIPluginInterface {
public:
    virtual ~AIPluginInterface() = default;
    virtual QWidget* createDock(dsv::StepAnimator* animator, dsv::DSScene* scene) = 0;
};

#define AIPluginInterface_iid "dsv.AIPluginInterface/1.0"
Q_DECLARE_INTERFACE(AIPluginInterface, AIPluginInterface_iid)
