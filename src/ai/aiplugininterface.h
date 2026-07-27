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
    // 主题切换通知：主程序在浅色/深色切换后调用，插件事先无需知道主题细节。
    // 默认空实现，保证旧插件也能加载。
    virtual void setTheme(bool /*dark*/) {}
};

#define AIPluginInterface_iid "dsv.AIPluginInterface/1.0"
Q_DECLARE_INTERFACE(AIPluginInterface, AIPluginInterface_iid)
