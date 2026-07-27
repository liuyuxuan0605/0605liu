#include "LogViewer.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGroupBox>
#include <QPushButton>
#include <QLabel>
#include <QSizePolicy>

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
    h->setSpacing(6);
    h->setContentsMargins(2, 0, 2, 0);
    auto* btnStart = new QPushButton("|◀");
    auto* btnPrev  = new QPushButton("◀");
    m_playBtn      = new QPushButton("播放");
    auto* btnNext  = new QPushButton("▶");
    auto* btnEnd   = new QPushButton("▶|");
    connect(btnStart, &QPushButton::clicked, this, [this]() { emit undo(); });
    connect(btnPrev,  &QPushButton::clicked, this, [this]() { emit stepPrev(); });
    connect(m_playBtn,&QPushButton::clicked, this, [this]() {
        if (m_playing) emit pause(); else emit play();
    });
    connect(btnNext,  &QPushButton::clicked, this, [this]() { emit stepNext(); });
    connect(btnEnd,   &QPushButton::clicked, this, [this]() { emit redo(); });
    // 5 个按钮全部固定宽高，避免中间播放按钮伸展后挤占/遮挡两侧符号按钮
    const int SYM_W = 42;
    const int PLAY_W = 58;
    const int BTN_H = 32;
    h->setSpacing(8);
    auto styleSym = QString("QPushButton { padding: 6px 2px; min-width: %1px; max-width: %1px; }").arg(SYM_W);
    auto stylePlay = QString("QPushButton { padding: 6px 4px; min-width: %1px; max-width: %1px; }").arg(PLAY_W);
    btnStart->setFixedSize(SYM_W, BTN_H);
    btnPrev ->setFixedSize(SYM_W, BTN_H);
    btnNext ->setFixedSize(SYM_W, BTN_H);
    btnEnd  ->setFixedSize(SYM_W, BTN_H);
    btnStart->setStyleSheet(styleSym);
    btnPrev ->setStyleSheet(styleSym);
    btnNext ->setStyleSheet(styleSym);
    btnEnd  ->setStyleSheet(styleSym);
    m_playBtn->setFixedSize(PLAY_W, BTN_H);
    m_playBtn->setStyleSheet(stylePlay);
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
    m_playBtn->setText(playing ? "暂停" : "播放");
}
void LogViewer::highlightCurrent(int index) {
    if (index >= 0 && index < m_log->count()) {
        m_log->setCurrentRow(index);
        m_log->scrollToItem(m_log->item(index));
    }
}

} // namespace dsv
