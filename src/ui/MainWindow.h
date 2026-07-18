#pragma once
#include <QMainWindow>
#include <QGraphicsView>
#include <QLabel>
#include <memory>
#include <QVector>
#include <QPair>
#include "../core/Common.h"
#include "../core/IDataStructure.h"
#include "../visual/DSScene.h"
#include "../visual/StepAnimator.h"
#include "OperationPanel.h"
#include "LogViewer.h"

namespace dsv {

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindow(QWidget* parent = nullptr);

private slots:
    void switchKind(int index);
    void runOperation(const QString& op, const QString& value);
    void runPreset();
    void onFrameChanged(int index, int total, const QString& desc);
    void toggleTheme();
    void undo();
    void redo();

private:
    QVector<QPair<QString, QString>> buildPreset(DSKind kind) const;
    void loadFrames(FrameList frames);
    void applyTheme(bool dark);
    void updateStatus();
    void rebuildAndShow(const QString& actionLabel);  // undo/redo 共用的重建+展示逻辑

    std::unique_ptr<IDataStructure> m_ds;
    DSKind m_kind = DSKind::SinglyLinkedList;
    DSScene* m_scene = nullptr;
    QGraphicsView* m_view = nullptr;
    StepAnimator* m_animator = nullptr;
    OperationPanel* m_ops = nullptr;
    LogViewer* m_log = nullptr;
    QLabel* m_header = nullptr;
    QLabel* m_status = nullptr;
    int m_opCount = 0;
    bool m_dark = false;
    std::vector<std::string> m_values;                 // 当前有序值集合（插入顺序，撤销依据）
    std::vector<std::vector<std::string>> m_history;   // 撤销栈
    std::vector<std::vector<std::string>> m_redo;      // 重做栈（undo 时压入，新操作时清空）
};

} // namespace dsv
