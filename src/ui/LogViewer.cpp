#include "LogViewer.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGroupBox>
#include <QPushButton>
#include <QLabel>

namespace dsv {

LogViewer::LogViewer(QWidget* parent) : QWidget(parent) {
    auto* root = new QVBoxLayout(this);
    root->setSpacing(10);

    // current step description
    auto* gbDesc = new QGroupBox("当前步骤");
    auto* v1 = new QVBoxLayout(gbDesc);
    m_desc = new QLabel("选择一个数据结构并触发操作");
    m_desc->setWordWrap(true);
    QFont f = m_desc->font(); f.setPointSize(13); m_desc->setFont(f);
    v1->addWidget(m_desc);
    m_progress = new QLabel("步骤 0 / 0");
    m_progress->setAlignment(Qt::AlignRight);
    v1->addWidget(m_progress);
    root->addWidget(gbDesc);

    // playback controls
    auto* gbCtrl = new QGroupBox("播放控制");
    auto* h = new QHBoxLayout(gbCtrl);
    auto* btnStart = new QPushButton("|◀");
    auto* btnPrev  = new QPushButton("◀");
    m_playBtn      = new QPushButton("▶ 播放");
    auto* btnNext  = new QPushButton("▶");
    auto* btnEnd   = new QPushButton("▶|");
    connect(btnStart, &QPushButton::clicked, this, [this]() { emit undo(); });
    connect(btnPrev,  &QPushButton::clicked, this, [this]() { emit stepPrev(); });
    connect(m_playBtn,&QPushButton::clicked, this, [this]() {
        if (m_playing) emit pause(); else emit play();
    });
    connect(btnNext,  &QPushButton::clicked, this, [this]() { emit stepNext(); });
    connect(btnEnd,   &QPushButton::clicked, this, [this]() { emit redo(); });
    h->addWidget(btnStart);
    h->addWidget(btnPrev);
    h->addWidget(m_playBtn);
    h->addWidget(btnNext);
    h->addWidget(btnEnd);
    root->addWidget(gbCtrl);

    // step log
    auto* gbLog = new QGroupBox("步骤日志");
    auto* v2 = new QVBoxLayout(gbLog);
    m_log = new QListWidget();
    m_log->setAlternatingRowColors(true);
    v2->addWidget(m_log);
    root->addWidget(gbLog, 1);

    root->addStretch(0);
}

void LogViewer::setDescription(const QString& desc) { m_desc->setText(desc); }
void LogViewer::setProgress(int index, int total) {
    m_progress->setText(QString("步骤 %1 / %2").arg(index + 1).arg(total));
}
void LogViewer::setLog(const QStringList& steps) {
    m_log->clear();
    for (const auto& s : steps) m_log->addItem(s);
}
void LogViewer::setPlaying(bool playing) {
    m_playing = playing;
    m_playBtn->setText(playing ? "⏸ 暂停" : "▶ 播放");
}
void LogViewer::highlightCurrent(int index) {
    if (index >= 0 && index < m_log->count()) {
        m_log->setCurrentRow(index);
        m_log->scrollToItem(m_log->item(index));
    }
}

} // namespace dsv
