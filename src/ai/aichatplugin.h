#pragma once
#include <QObject>
#include <QWidget>
#include <QTextEdit>
#include <QLineEdit>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QPushButton>
#include <QLabel>
#include <QJsonObject>
#include <QJsonArray>
#include <QTimer>
#include "aiplugininterface.h"

namespace dsv {
class StepAnimator;
class DSScene;
}

// AI 讲解助教外挂。编译为独立插件(.dll/.so)，主程序不链接任何 AI/网络库。
class AIChatPlugin : public QObject, public AIPluginInterface {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "dsv.AIPluginInterface/1.0")
    Q_INTERFACES(AIPluginInterface)
public:
    AIChatPlugin(QObject* parent = nullptr);
    QWidget* createDock(dsv::StepAnimator* animator, dsv::DSScene* scene) override;
    void setTheme(bool dark) override;

signals:
    void requestJump(const QString& structure);
    void requestRunOperation(const QString& op, const QString& value);

private slots:
    void onFrameChanged(int index, int total, const QString& desc);
    void onAskClicked();
    void onReply(QNetworkReply* reply);
    void onStepPlayState(bool playing);   // 多步演示：动画播完→进入下一步
    void onStepTimeout();                 // 看门狗：某步未产生动画也能继续

private:
    void postAsk(const QString& question, const QJsonObject& ctx, bool autoFollow);
    void appendBubble(const QString& sender, const QString& color, const QString& text,
                      bool userSide);
    void scrollLogToBottom();
    dsv::StepAnimator* m_animator = nullptr;
    dsv::DSScene* m_scene = nullptr;
    QTextEdit* m_log = nullptr;
    QLineEdit* m_input = nullptr;
    QPushButton* m_sendBtn = nullptr;
    QLabel* m_statusLabel = nullptr;
    QNetworkAccessManager* m_net = nullptr;
    QString m_endpoint = "http://localhost:8000/ask";
    bool m_dark = false;
    bool m_waiting = false;

    // step_explain 多步演示排队状态
    QJsonArray m_stepQueue;
    int m_stepIndex = 0;
    bool m_stepping = false;
    bool m_stepPlaying = false;
    QTimer* m_stepWatchdog = nullptr;
    bool m_animatorConnected = false;
    void emitNextStep();                          // 取 m_stepQueue[m_stepIndex] 发出 requestRunOperation（含看门狗）
    void startStepExplain(const QJsonObject& act); // 解析 step_explain action 并启动队列
};
