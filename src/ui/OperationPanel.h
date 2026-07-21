#pragma once
#include <QWidget>
#include <QComboBox>
#include <QLineEdit>
#include <QPushButton>
#include <QSlider>
#include <QLabel>
#include <QGroupBox>
#include <QRadioButton>
#include <QButtonGroup>
#include <QStandardItemModel>
#include <vector>
#include "../core/Common.h"

namespace dsv {

// Left-side control panel: choose data structure, enter data, trigger
// operations, adjust animation speed, run demo presets.
class OperationPanel : public QWidget {
    Q_OBJECT
public:
    explicit OperationPanel(QWidget* parent = nullptr);

signals:
    // 传递的是 DSKind 的整数值（不再是 combo 行号），与枚举解耦
    void kindChanged(int kind);
    void operationRequested(const QString& op, const QString& value);
    void presetRequested();
    void speedChanged(double);
    void degreeChanged(int maxDegree);   // B-tree / B+tree max degree (keys per node)

public slots:
    void setKindIndex(int kind);   // 以 DSKind 值为参数，保持下拉与结构同步

private slots:
    void onKindChanged(int row);
    void onInsert() { emit operationRequested("insert", m_value->text()); }
    void onRemove() { emit operationRequested("remove", m_value->text()); }
    void onFind()   { emit operationRequested("find", m_value->text()); }
    void onClear()  { emit operationRequested("clear", ""); }
    void onPushFront() { emit operationRequested("pushFront", m_value->text()); }
    void onPushBack()  { emit operationRequested("pushBack", m_value->text()); }
    void onPopFront()  { emit operationRequested("popFront", ""); }
    void onPopBack()   { emit operationRequested("popBack", ""); }
    void onSpeed(int v) { emit speedChanged(v / 100.0); }

private:
    void buildKindCombo();                 // 分类填充下拉（分组标题 + DSKind 数据）
    void relabel(DSKind kind);             // 按 DSKind 调整按钮文案与分组可见性
    QComboBox* m_kind;
    QStandardItemModel* m_kindModel;
    QLineEdit* m_value;
    QLabel* m_valueHint;
    QPushButton* m_insertBtn;
    QPushButton* m_removeBtn;
    QPushButton* m_findBtn;
    QPushButton* m_clearBtn;
    QPushButton* m_presetBtn;
    QGroupBox* m_opGroup;       // generic insert/remove/find/clear group (hidden for Graph)
    QGroupBox* m_dequeGroup;
    QPushButton* m_pushFrontBtn;
    QPushButton* m_pushBackBtn;
    QPushButton* m_popFrontBtn;
    QPushButton* m_popBackBtn;
    QGroupBox* m_graphGroup;    // Graph-specific operations (visible only for Graph)
    QPushButton* m_addVertexBtn;
    QPushButton* m_addEdgeBtn;
    QPushButton* m_bfsBtn;
    QPushButton* m_dfsBtn;
    QPushButton* m_dijkstraBtn;
    QPushButton* m_graphClearBtn;
    QGroupBox* m_treeGroup;     // 树遍历（BFS/DFS），仅 BST 等实现遍历的树可见
    QPushButton* m_treeBfsBtn;
    QPushButton* m_treeDfsBtn;
    QGroupBox* m_degreeGroup;   // Max Degree (仅 BTree/BPlusTree 可见)
    QButtonGroup* m_degreeBtnGroup;  // radio button group for degree selection
    std::vector<QRadioButton*> m_degreeRadios;  // radio buttons: 3,4,5,6,7
    static constexpr int DEGREE_MIN = 3;
    static constexpr int DEGREE_MAX = 7;
};

} // namespace dsv
