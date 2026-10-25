import sys
from PySide6.QtQuick import QQuickView
from PySide6.QtGui import QGuiApplication, QIcon, QStandardItem, QStandardItemModel
from PySide6.QtCore import QUrl
from pathlib import Path

import fnbn_backend.backend as backend
import fnbn_backend.file_table as file_table
import fnbn_backend.treemodel as treemodel
from pathlib import Path
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication


BASE_DIR = Path(__file__).resolve().parent

def main() -> int:

    QQuickStyle.setStyle("Fusion")

    app = QGuiApplication(sys.argv)

    #app.setWindowIcon(QIcon("./assets/app-icons/qt/app.png"))

    icon_path = Path(__file__).resolve().parent / "App/app-icons/AppIcon.png"
    app.setWindowIcon(QIcon(str(icon_path)))


    app.setApplicationName("FNBN 0.0.1")
    app.setApplicationDisplayName("FNBN - Files Need Bettet Names 0.0.1")
    app.setOrganizationName("Baddonkey")
 
    # setup main view
    view = QQuickView()
    #view.engine().addImportPath(sys.path[0])
    view.engine().addImportPath(str(BASE_DIR))
    view.setTitle("FNBN - Files Need Better Names 0.0.1 | PDF-only")
    view.setResizeMode(QQuickView.ResizeMode.SizeRootObjectToView)
    

    # setup the left side bar
    treeModel = treemodel.TreeModel()
    treeModel.setHorizontalHeaderLabels(["Name"])
    view.engine().rootContext().setContextProperty("treeModel", treeModel)

    # setup the content bar
    tableModel = file_table.FileTableModel()
    view.engine().rootContext().setContextProperty("tableModel", tableModel)

    # setup the backend
    home = Path.home()
    backendx = backend.Backend(treeModel, tableModel)
    view.engine().rootContext().setContextProperty("backend", backendx)

    # load QML
    view.loadFromModule("App", "Main")

    # load root node
    backendx.folder_selected(QUrl.fromLocalFile(str(home)))

    if view.status() == QQuickView.Status.Error:
        sys.exit(-1)

    view.showMaximized()

    app.exec()
    del view

if __name__ == "__main__":
    sys.exit(main())