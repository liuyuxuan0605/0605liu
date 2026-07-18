#pragma once
#include <QWidget>
#include <QLabel>
#include <QPushButton>
#include <QListWidget>
#include <QStringList>

namespace dsv {

// Right-side panel: shows the current step narration, playback controls,
// and a scrollable log of every step in the active operation.
class LogViewer : public QWidget {
    Q_OBJECT
public:
    explicit LogViewer(QWidget* parent = nullptr);

signals:
    void play();
    void pause();
    void stepNext();
    void stepPrev();
    void toStart();
    void toEnd();
    void undo();
    void redo();

public slots:
    void setDescription(const QString& desc);
    void setProgress(int index, int total);
    void setLog(const QStringList& steps);
    void setPlaying(bool playing);
    void highlightCurrent(int index);

private:
    QLabel* m_desc;
    QLabel* m_progress;
    QListWidget* m_log;
    QPushButton* m_playBtn;
    bool m_playing = false;
};

} // namespace dsv
