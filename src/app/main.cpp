#include <QApplication>
#include "ui/MainWindow.h"

int main(int argc, char* argv[]) {
    // High-DPI / 4K scaling: Qt 5.x must enable this manually (automatic in Qt 6)
    QApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    QApplication::setAttribute(Qt::AA_UseHighDpiPixmaps);
    QApplication app(argc, argv);
    app.setApplicationName("DSVisualizer");
    app.setStyle("Fusion");   // clean, cross-platform look

    dsv::MainWindow w;
    w.show();
    return app.exec();
}
