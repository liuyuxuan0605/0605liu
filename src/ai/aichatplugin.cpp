#include "aichatplugin.h"
#include "../visual/StepAnimator.h"
#include "../visual/DSScene.h"
#include "../core/Factory.h"

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
#include <QByteArray>

AIChatPlugin::AIChatPlugin(QObject* parent) : QObject(parent) {
    // 允许通过环境变量覆盖 RAG 服务地址（默认 http://localhost:8000/ask）
    QByteArray env = qgetenv("RAG_ENDPOINT");
    if (!env.isEmpty()) {
        m_endpoint = QString::fromUtf8(env);
    }
}

QWidget* AIChatPlugin::createDock(dsv::StepAnimator* animator, dsv::DSScene* scene) {
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
        connect(m_animator, &dsv::StepAnimator::frameChanged,
                this, &AIChatPlugin::onFrameChanged);

    return dock;
}

void AIChatPlugin::onFrameChanged(int index, int total, const QString& desc) {
    // 自动跟随：把当前帧描述 + 当前数据结构类型作为上下文，让 RAG 解释“这一步在做什么”
    QJsonObject ctx;
    ctx["desc"] = desc;
    ctx["index"] = index;
    ctx["total"] = total;
    if (m_scene)
        ctx["structure"] = QString::fromUtf8(dsv::kindToString(m_scene->kind()));
    postAsk(desc, ctx);
}

void AIChatPlugin::onAskClicked() {
    QString q = m_input->text().trimmed();
    if (q.isEmpty()) return;
    m_input->clear();
    // 把当前正在可视化的数据结构类型带上，让服务端检索器按结构过滤
    // （看红黑树时不返回 AVL 的旋转笔记，反之亦然）
    QJsonObject ctx;
    if (m_scene)
        ctx["structure"] = QString::fromUtf8(dsv::kindToString(m_scene->kind()));
    postAsk(q, ctx);
}

void AIChatPlugin::postAsk(const QString& question, const QJsonObject& ctx) {
    QJsonObject body;
    body["question"] = question;
    body["context"] = ctx;
    QNetworkRequest req = QNetworkRequest(QUrl(m_endpoint));
    req.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    m_log->append("你: " + question);
    m_net->post(req, QJsonDocument(body).toJson());
}

void AIChatPlugin::onReply(QNetworkReply* reply) {
    reply->deleteLater();
    if (reply->error() != QNetworkReply::NoError) {
        m_log->append("[错误] 无法连接 RAG 服务 (" + m_endpoint + ")。\n"
                      "请先在本机启动 rag-service/server.py 并保持窗口运行，再回来提问。\n"
                      "（若服务在别的机器/端口，设置环境变量 RAG_ENDPOINT 指向它。）");
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
