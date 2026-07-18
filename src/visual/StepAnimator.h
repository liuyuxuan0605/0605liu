#pragma once
#include <QObject>
#include <QTimer>
#include "../core/Common.h"
#include "DSScene.h"

namespace dsv {

// Drives playback of a FrameList through DSScene. A QTimer advances frames
// at a speed-dependent interval; manual stepping is also supported.
class StepAnimator : public QObject {
    Q_OBJECT
public:
    explicit StepAnimator(DSScene* scene, QObject* parent = nullptr)
        : QObject(parent), m_scene(scene) {
        m_timer = new QTimer(this);
        connect(m_timer, &QTimer::timeout, this, &StepAnimator::onTimeout);
    }

    void setFrames(FrameList frames) {
        m_timer->stop();
        m_playing = false;
        emit playStateChanged(false);
        m_frames = std::move(frames);
        m_index = 0;
        if (!m_frames.empty()) showCurrent();
    }

    void play() {
        if (m_frames.empty()) return;
        if (m_index >= (int)m_frames.size() - 1) { m_index = 0; showCurrent(); }
        m_playing = true;
        emit playStateChanged(true);
        m_timer->start(static_cast<int>(BASE_MS / m_speed));
    }
    void pause() {
        m_playing = false;
        m_timer->stop();
        emit playStateChanged(false);
    }
    void stop() { pause(); toStart(); }

    void next() {
        m_timer->stop();
        m_playing = false;
        emit playStateChanged(false);
        if (m_index < (int)m_frames.size() - 1) {
            m_index++;
            showCurrent();
            emit frameChanged(m_index, total(), currentDesc());
        }
    }
    void prev() {
        m_timer->stop();
        m_playing = false;
        emit playStateChanged(false);
        if (m_index > 0) {
            m_index--;
            showCurrent();
            emit frameChanged(m_index, total(), currentDesc());
        }
    }
    void toStart() {
        // jump to the very first frame and stop playback
        m_timer->stop();
        m_playing = false;
        emit playStateChanged(false);
        m_index = 0;
        showCurrent();
        emit frameChanged(m_index, total(), currentDesc());
    }
    void toEnd() {
        m_timer->stop();
        m_playing = false;
        emit playStateChanged(false);
        m_index = (int)m_frames.size() - 1;
        showCurrent();
        emit frameChanged(m_index, total(), currentDesc());
    }

    void setSpeed(double s) {
        m_speed = qBound(0.25, s, 4.0);
        if (m_playing) m_timer->start(static_cast<int>(BASE_MS / m_speed));
    }
    double speed() const { return m_speed; }
    bool isPlaying() const { return m_playing; }
    int currentIndex() const { return m_index; }
    int total() const { return static_cast<int>(m_frames.size()); }

signals:
    void frameChanged(int index, int total, const QString& desc);
    void playStateChanged(bool playing);

private slots:
    void onTimeout() {
        if (m_index < (int)m_frames.size() - 1) {
            m_index++;
            showCurrent();
            emit frameChanged(m_index, total(), currentDesc());
        } else {
            pause();
        }
    }

private:
    void showCurrent() {
        if (!m_frames.empty()) m_scene->applyFrame(m_frames[m_index], true);
    }
    QString currentDesc() const {
        if (m_frames.empty()) return "";
        return QString::fromStdString(m_frames[m_index].description);
    }

    DSScene* m_scene;
    FrameList m_frames;
    int m_index = 0;
    double m_speed = 1.0;
    bool m_playing = false;
    QTimer* m_timer;
    static constexpr int BASE_MS = 750;
};

} // namespace dsv
