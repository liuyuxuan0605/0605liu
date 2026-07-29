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
#include <QScrollBar>
#include <QRegularExpression>
#include <map>
#include <set>
#include <functional>

namespace {

// 行内 Markdown（**粗体**、`代码`、*斜体*）转 HTML。输入先整体 HTML 转义，杜绝注入。
QString inlineMdToHtml(const QString& s) {
    QString t = s.toHtmlEscaped();
    // 行内代码 `code`
    t.replace(QRegularExpression("`([^`]+)`"),
              "<code style=\"font-family:'Courier New',Consolas,monospace;"
              "background-color:#EEF1F6;padding:1px 5px;border-radius:4px;"
              "font-size:12px;color:#C2185B;\">\\1</code>");
    // 粗体 **text**
    t.replace(QRegularExpression("\\*\\*(.+?)\\*\\*"), "<b>\\1</b>");
    // 斜体 *text*（仅在单词边界，避免误伤已处理的 **）
    t.replace(QRegularExpression("(^|\\s)\\*([^*]+?)\\*(\\s|$)"), "\\1<i>\\2</i>\\3");
    return t;
}

// 把 LLM 返回的 Markdown 讲解转成 QTextEdit 可渲染的 HTML（代码块/列表/标题/段落）。
QString markdownToHtml(const QString& md) {
    const QString codeStyle =
        "font-family:'Courier New',Consolas,monospace;background-color:#F4F6F9;"
        "padding:8px 10px;border-radius:6px;white-space:pre-wrap;font-size:12px;color:#1F2329;";
    QStringList lines = md.split('\n');
    QString out;
    enum State { NONE, UL, OL, CODE } state = NONE;
    QString codeBuf;

    auto flushList = [&]() {
        if (state == UL) { out += "</ul>"; state = NONE; }
        else if (state == OL) { out += "</ol>"; state = NONE; }
    };
    auto flushCode = [&]() {
        if (state == CODE) {
            out += "<pre style=\"" + codeStyle + "\">" + codeBuf.toHtmlEscaped() + "</pre>";
            codeBuf.clear();
            state = NONE;
        }
    };

    QRegularExpression reUl(R"(^\s*[-*]\s+(.*)$)");
    QRegularExpression reOl(R"(^\s*\d+[.)]\s+(.*)$)");

    for (const QString& rawLine : lines) {
        QString line = rawLine;
        // 围栏代码块 ```
        if (line.trimmed().startsWith("```")) {
            if (state == CODE) flushCode();
            else { flushList(); state = CODE; }
            continue;
        }
        if (state == CODE) { codeBuf += line + "\n"; continue; }

        if (line.trimmed().isEmpty()) {
            flushList();
            if (state == NONE) out += "<br>";
            continue;
        }
        QRegularExpressionMatch m;
        if ((m = reUl.match(line)).hasMatch()) {
            if (state != UL) { flushList(); out += "<ul style=\"margin:4px 0;padding-left:20px;\">"; state = UL; }
            out += "<li style=\"margin:2px 0;\">" + inlineMdToHtml(m.captured(1)) + "</li>";
            continue;
        }
        if ((m = reOl.match(line)).hasMatch()) {
            if (state != OL) { flushList(); out += "<ol style=\"margin:4px 0;padding-left:20px;\">"; state = OL; }
            out += "<li style=\"margin:2px 0;\">" + inlineMdToHtml(m.captured(1)) + "</li>";
            continue;
        }
        // 普通行：标题 # 降级为加粗段落
        flushList();
        QString para = line;
        if (para.startsWith("#")) {
            int h = 0;
            while (h < para.size() && para[h] == '#') ++h;
            para = para.mid(h).trimmed();
            out += "<b style=\"font-size:14px;\">" + inlineMdToHtml(para) + "</b><br>";
        } else {
            out += inlineMdToHtml(para) + "<br>";
        }
    }
    flushList();
    flushCode();
    return out;
}

// 把当前帧(Frame)的真实结构状态序列化成可读文本，供 RAG 上下文使用。
// 树结构(left/right 边)递归缩进打印；其余结构退化为"节点+边"列表。
// 注：始终发送完整结构，保证 AI 对左右子树/旋转等关系的讲解准确性（正确性 > token 成本）。
QString frameToText(const dsv::Frame& f) {
    std::map<int, QString> val;
    for (const auto& n : f.nodes)
        val[n.id] = QString::fromStdString(n.value) +
                    (n.sublabel.empty() ? "" : (" (" + QString::fromStdString(n.sublabel) + ")"));

    std::map<int, std::vector<std::pair<int, QString>>> children;
    std::set<int> hasParent;
    bool isTree = false;
    for (const auto& e : f.edges) {
        if (e.kind == "left" || e.kind == "right") {
            isTree = true;
            children[e.fromId].push_back({e.toId, QString::fromStdString(e.kind)});
            hasParent.insert(e.toId);
        }
    }

    QString out;
    if (isTree) {
        std::set<int> roots;
        for (const auto& n : f.nodes)
            if (!hasParent.count(n.id)) roots.insert(n.id);
        std::function<void(int, int)> walk = [&](int id, int depth) {
            QString line;
            for (int i = 0; i < depth; ++i) line += "  ";
            auto it = val.find(id);
            line += (it != val.end() ? it->second : QString::number(id));
            line += QString("  [id=%1]").arg(id);
            out += line + "\n";
            auto cit = children.find(id);
            if (cit != children.end())
                for (const auto& c : cit->second) walk(c.first, depth + 1);
        };
        for (int r : roots) walk(r, 0);
    } else {
        out += "节点: ";
        for (const auto& n : f.nodes)
            out += QString("%1[id=%2] ").arg(QString::fromStdString(n.value)).arg(n.id);
        out += "\n边: ";
        for (const auto& e : f.edges)
            out += QString("%1 -> %2 [%3]  ").arg(e.fromId).arg(e.toId)
                      .arg(QString::fromStdString(e.kind));
        out += "\n";
    }

    if (!f.highlightIds.empty()) {
        QStringList hl;
        for (int id : f.highlightIds) {
            auto it = val.find(id);
            hl << (it != val.end() ? it->second + QString("(%1)").arg(id)
                                  : QString::number(id));
        }
        out += "本步高亮节点: " + hl.join(", ") + "\n";
    }
    return out;
}

}

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
    v->setContentsMargins(12, 12, 12, 12);
    v->setSpacing(10);

    // 头部：标题 + 连接状态
    auto* header = new QLabel("AI 讲解助教");
    header->setStyleSheet("font-weight:700;font-size:15px;color:#1F2329;");
    v->addWidget(header);

    m_statusLabel = new QLabel("● 准备中…");
    m_statusLabel->setStyleSheet("font-size:11px;color:#8A94A6;");
    v->addWidget(m_statusLabel);

    // 消息区
    m_log = new QTextEdit();
    m_log->setReadOnly(true);
    m_log->setMinimumHeight(160);
    m_log->document()->setDocumentMargin(8);
    m_log->setStyleSheet(
        "QTextEdit{border:1px solid #DDE0E5;border-radius:10px;"
        "background-color:#F7F8FA;padding:4px;}");
    v->addWidget(m_log, 1);

    // 输入框 + 发送
    auto* h = new QHBoxLayout();
    h->setSpacing(8);
    m_input = new QLineEdit();
    m_input->setPlaceholderText("问 AI 这一步的原理，或回车自动跟随…");
    m_sendBtn = new QPushButton("发送");
    m_sendBtn->setStyleSheet(
        "QPushButton{background-color:#4A90E2;color:#FFFFFF;border:none;"
        "border-radius:8px;padding:6px 16px;font-weight:600;}"
        "QPushButton:hover{background-color:#3D7BC8;}"
        "QPushButton:pressed{background-color:#356BB0;}");
    h->addWidget(m_input, 1);
    h->addWidget(m_sendBtn);
    v->addLayout(h);

    connect(m_sendBtn, &QPushButton::clicked, this, &AIChatPlugin::onAskClicked);
    connect(m_input, &QLineEdit::returnPressed, this, &AIChatPlugin::onAskClicked);
    connect(m_net, &QNetworkAccessManager::finished, this, &AIChatPlugin::onReply);
    if (m_animator)
        connect(m_animator, &dsv::StepAnimator::frameChanged,
                this, &AIChatPlugin::onFrameChanged);

    // 初始欢迎语
    appendBubble("AI", "#0F6E56",
                 "你好，我是数据结构讲解助教。操作可视化时我会自动跟随当前步骤给出讲解；"
                 "也可以直接在下方提问，例如“为什么要旋转？”。", false);
    m_statusLabel->setText("● 已就绪（需先启动 RAG 后端）");
    return dock;
}

void AIChatPlugin::setTheme(bool dark) {
    m_dark = dark;
    if (!m_log) return;
    QString border = dark ? "#333A47" : "#DDE0E5";
    QString bg = dark ? "#2A2F3A" : "#F7F8FA";
    m_log->setStyleSheet(QString("QTextEdit{border:1px solid %1;border-radius:10px;"
                                 "background-color:%2;padding:4px;}")
                         .arg(border, bg));
}

void AIChatPlugin::appendBubble(const QString& sender, const QString& color,
                                const QString& text, bool userSide) {
    // 气泡：右侧=用户(蓝底白字)，左侧=AI(浅底深字)
    QString bubbleBg, textColor, align;
    if (userSide) {
        bubbleBg = "#4A90E2";
        textColor = "#FFFFFF";
        align = "right";
    } else {
        bubbleBg = m_dark ? "#242935" : "#EDF1F7";
        textColor = m_dark ? "#E6E6E6" : "#1F2329";
        align = "left";
    }
    QString html = QString(
        "<div style='margin:6px 0;text-align:%1;'>"
        "<span style='font-size:11px;color:%2;font-weight:600;'>%3</span>"
        "<div style='display:inline-block;max-width:88%;margin-top:2px;padding:8px 12px;"
        "border-radius:12px;background:%4;color:%5;font-size:13px;line-height:1.5;"
        "text-align:left;'>%6</div></div>")
        .arg(align, color, sender, bubbleBg, textColor, markdownToHtml(text));
    m_log->append(html);
    scrollLogToBottom();
}

void AIChatPlugin::scrollLogToBottom() {
    QScrollBar* bar = m_log->verticalScrollBar();
    if (bar) bar->setValue(bar->maximum());
}

void AIChatPlugin::onFrameChanged(int index, int total, const QString& desc) {
    // 自动跟随：把当前帧描述 + 当前数据结构类型作为上下文，让 RAG 解释“这一步在做什么”
    QJsonObject ctx;
    ctx["desc"] = desc;
    ctx["index"] = index;
    ctx["total"] = total;
    if (m_scene)
        ctx["structure"] = QString::fromUtf8(dsv::kindToString(m_scene->kind()));
    // 把当前帧的真实结构状态（节点值+父子关系）喂给 RAG，让回答接地气、不泛泛而谈
    if (m_animator) {
        if (const dsv::Frame* f = m_animator->currentFrame()) {
            ctx["tree_state"] = frameToText(*f);
            QStringList hl;
            for (int id : f->highlightIds) hl << QString::number(id);
            if (!hl.isEmpty()) ctx["highlight_ids"] = hl.join(",");
        }
    }
    postAsk(desc, ctx, /*autoFollow=*/true);
}

void AIChatPlugin::onAskClicked() {
    QString q = m_input->text().trimmed();
    if (q.isEmpty()) return;
    m_input->clear();
    QJsonObject ctx;
    if (m_scene)
        ctx["structure"] = QString::fromUtf8(dsv::kindToString(m_scene->kind()));
    // 手动提问也带上当前帧真实状态，便于大模型针对你屏幕上实际的树作答
    if (m_animator) {
        if (const dsv::Frame* f = m_animator->currentFrame()) {
            ctx["tree_state"] = frameToText(*f);
            QStringList hl;
            for (int id : f->highlightIds) hl << QString::number(id);
            if (!hl.isEmpty()) ctx["highlight_ids"] = hl.join(",");
        }
    }
    postAsk(q, ctx, /*autoFollow=*/false);
}

void AIChatPlugin::postAsk(const QString& question, const QJsonObject& ctx, bool autoFollow) {
    // autoFollow：步骤自动跟随的提问不明确时，不打用户气泡，只显示思考指示
    if (!autoFollow)
        appendBubble("你", "#4A90E2", question, /*userSide=*/true);

    m_waiting = true;
    m_statusLabel->setText("● 正在思考…");
    m_sendBtn->setEnabled(false);

    QJsonObject body;
    body["question"] = question;
    body["context"] = ctx;
    QNetworkRequest req = QNetworkRequest(QUrl(m_endpoint));
    req.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    m_net->post(req, QJsonDocument(body).toJson());
}

void AIChatPlugin::onReply(QNetworkReply* reply) {
    reply->deleteLater();
    m_waiting = false;
    m_sendBtn->setEnabled(true);

    if (reply->error() != QNetworkReply::NoError) {
        m_statusLabel->setText("● 离线（RAG 服务未连接）");
        appendBubble("AI", "#C0392B",
                     "无法连接 RAG 服务 (" + m_endpoint + ")。\n"
                     "请先在本机启动 rag-service/server.py 并保持窗口运行，再回来提问。\n"
                     "（若服务在别的机器/端口，设置环境变量 RAG_ENDPOINT 指向它。）",
                     /*userSide=*/false);
        return;
    }
    m_statusLabel->setText("● 已连接 RAG");

    QJsonObject obj = QJsonDocument::fromJson(reply->readAll()).object();
    appendBubble("AI", "#0F6E56", obj.value("answer").toString(), /*userSide=*/false);

    // 高亮联动：把返回的节点值高亮到图上
    QVariantList hl = obj.value("highlight_nodes").toArray().toVariantList();
    if (!hl.isEmpty() && m_scene) {
        QStringList vals;
        for (const auto& v : hl) vals << QString::number(v.toInt());
        m_scene->highlightByValue(vals, QColor("#0F6E56"));
        appendBubble("AI", "#0F6E56", "[已高亮节点] " + vals.join(", "), false);
    }

    // 来源
    QVariantList src = obj.value("sources").toArray().toVariantList();
    if (!src.isEmpty()) {
        QStringList s;
        for (const auto& v : src) s << v.toString();
        appendBubble("AI", "#8A94A6", "来源: " + s.join(" | "), false);
    }

    // actions：让 AI 主动驱动前端（如切换数据结构视图）
    QJsonArray actions = obj.value("actions").toArray();
    for (const QJsonValue& v : actions) {
        QJsonObject act = v.toObject();
        if (act.value("type").toString() == "jump") {
            QString structure = act.value("structure").toString().trimmed();
            if (!structure.isEmpty()) {
                emit requestJump(structure);
                appendBubble("AI", "#0F6E56", "[已切换视图] " + structure, false);
            }
        }
    }
}
