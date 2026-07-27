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

private slots:
    void onFrameChanged(int index, int total, const QString& desc);
    void onAskClicked();
    void onReply(QNetworkReply* reply);

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
};
