#include "aichatplugin.h"
#include "../visual/StepAnimator.h"
#include "../visual/DSScene.h"

#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QNetworkRequest>
#include <QJsonObject>
#include <QJsonDocument>
#include <QJsonArray>
#include <QColor>
#include <QStringList>

AIChatPlugin::AIChatPlugin(QObject* parent) : QObject(parent) {}

QWidget* AIChatPlugin::createDock(StepAnimator* animator, DSScene* scene) {
    m_animator = animator;
    m_scene = scene;
    m_net = new QNetworkAccessManager(this);

    auto* dock = new QWidget();
    auto* v = new QVBoxLayout(dock);
    v->setContentsMargins(8, 8, 8, 8);

    auto* header = new QLabel("AI 讲解助教");
    header->setStyleSheet("font-weight:600;font-size:14px;");
    v->addWidget(header);

    m_log = new QTextEdit();
    m_log->setReadOnly(true);
    v->addWidget(m_log, 1);

    auto* h = new QHBoxLayout();
    m_input = new QLineEdit();
    m_input->setPlaceholderText("问问 AI 这一步的原理...");
    auto* send = new QPushButton("发送");
    h->addWidget(m_input, 1);
    h->addWidget(send);
    v->addLayout(h);

    connect(send, &QPushButton::clicked, this, &AIChatPlugin::onAskClicked);
    connect(m_input, &QLineEdit::returnPressed, this, &AIChatPlugin::onAskClicked);
    connect(m_net, &QNetworkAccessManager::finished, this, &AIChatPlugin::onReply);
    if (m_animator)
        connect(m_animator, &StepAnimator::frameChanged,
                this, &AIChatPlugin::onFrameChanged);

    return dock;
}

void AIChatPlugin::onFrameChanged(int index, int total, const QString& desc) {
    // 自动跟随：把当前帧描述作为上下文，让 RAG 解释“这一步在做什么”
    QJsonObject ctx;
    ctx["desc"] = desc;
    ctx["index"] = index;
    ctx["total"] = total;
    postAsk(desc, ctx);
}

void AIChatPlugin::onAskClicked() {
    QString q = m_input->text().trimmed();
    if (q.isEmpty()) return;
    m_input->clear();
    postAsk(q, QJsonObject());
}

void AIChatPlugin::postAsk(const QString& question, const QJsonObject& ctx) {
    QJsonObject body;
    body["question"] = question;
    body["context"] = ctx;
    QNetworkRequest req(QUrl(m_endpoint));
    req.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    m_log->append("你: " + question);
    m_net->post(req, QJsonDocument(body).toJson());
}

void AIChatPlugin::onReply(QNetworkReply* reply) {
    reply->deleteLater();
    if (reply->error() != QNetworkReply::NoError) {
        m_log->append("[错误] 无法连接 RAG 服务: " + reply->errorString());
        return;
    }
    QJsonObject obj = QJsonDocument::fromJson(reply->readAll()).object();
    m_log->append("AI: " + obj.value("answer").toString());

    // 高亮联动：把返回的节点值高亮到图上
    QVariantList hl = obj.value("highlight_nodes").toArray().toVariantList();
    if (!hl.isEmpty() && m_scene) {
        QStringList vals;
        for (const auto& v : hl) vals << QString::number(v.toInt());
        m_scene->highlightByValue(vals, QColor("#0F6E56"));
        m_log->append("[已高亮节点] " + vals.join(", "));
    }

    // 来源
    QVariantList src = obj.value("sources").toArray().toVariantList();
    if (!src.isEmpty()) {
        QStringList s;
        for (const auto& v : src) s << v.toString();
        m_log->append("[来源] " + s.join(" | "));
    }
}
