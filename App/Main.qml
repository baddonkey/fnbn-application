import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQml.Models


Page {
    id: page
    width: 640
    height: 480

    header: ToolBar {
        RowLayout {
            anchors.fill: parent
            ToolButton {
                icon.color: palette.buttonText
                text: qsTr("Open Folder")
                icon.source: "icons/folder-open.svg"
                onClicked: {
                    folderDialog.open();
                }
                ToolTip.visible: hovered
                ToolTip.text: "Open the top foler to browse for files"

            }

            ToolButton {
                icon.color: palette.buttonText
                text: qsTr("Suggest Selected")
                icon.source: "icons/cpu-ai.svg"
                onClicked: {

                    const indexes = tableView.selectionModel.selectedRows(0)
                    const rows = []

                    for (let i = 0; i < indexes.length; i++)
                        rows.push(indexes[i].row)

                    rows.sort(function(a, b) { return a -b})

                    backend.suggestSelectedRows(rows);
                }
                ToolTip.visible: hovered
                ToolTip.text: "Create the suggestion for all selected files"
            }

            Item {
                Layout.fillWidth: true
            }

            ToolButton {
                icon.color: palette.buttonText
                icon.source: "icons/settings.svg"
                font.pixelSize: 24
                ToolTip.visible: hovered
                ToolTip.text: "Settings"
                onClicked: settingsDialog.open()
            }

        }
    }

    FolderDialog {
        id: folderDialog

        title: "Select a folder"
        acceptLabel: "Select"

        onAccepted: {
            backend.folder_selected(selectedFolder);
        }
    }

    SplitView {
        anchors.fill: parent
        spacing: 0
        orientation: Qt.Horizontal

        handle: Rectangle {
            implicitWidth: 6
            implicitHeight: 6
            color: SplitHandle.pressed ? "#5294d6" : SplitHandle.hovered ? "#a0a0a0" : "#dddddd"
        }

        Rectangle {
            id: sidebar

            SplitView.preferredWidth: 250
            SplitView.minimumWidth: 150
            SplitView.maximumWidth: 450

            color: palette.base
            

            property var treeModel: null

            TreeView {
                id: treeView
                model: treeModel
                anchors.fill: parent
                anchors.margins: 10
                clip: true


                // Make the single tree column fill the viewport
                columnWidthProvider: function(column) {
                    return treeView.width
                }

                // Recalculate column width when splitter moves
                onWidthChanged: forceLayout()

                Connections {
                    target: backend

                    function onTreeReloaded() {
                        Qt.callLater(function () {
                            treeView.expand(0);

                            // Select root
                            let index = treeView.index(0, 0);

                            treeView.selectionModel.setCurrentIndex(
                                index,
                                ItemSelectionModel.ClearAndSelect
                            );
                        });
                    }
                }

                onExpanded: function(row, depth) {
                    let index = treeView.index(row, 0);
                    backend.treeNodeExpanded(index);
                }

                selectionModel: ItemSelectionModel {
                    model: treeModel

                    onCurrentChanged: function (current, previous) {
                        if (!current.valid)
                            return;

                        // Notify the Python/C++ backend
                        backend.treeNodeSelected(current);
                    }


                }

                delegate: Item {
                    id: root

                    implicitWidth: 300
                    implicitHeight: 36

                    readonly property real indentation: 20
                    readonly property real padding: 10

                    required property TreeView treeView
                    required property bool isTreeNode
                    required property bool expanded
                    required property bool hasChildren
                    required property int depth
                    required property int row
                    required property int column
                    required property bool current

                    Rectangle {
                        anchors.fill: parent
                        height: 2
                    color: root.current
                        ? palette.highlight
                        : palette.base

                    }




                    Label {
                        id: indicator

                        x: root.padding + root.depth * root.indentation
                        anchors.verticalCenter: parent.verticalCenter

                        visible: root.isTreeNode && root.hasChildren
                        text: root.expanded ? "▼" : "▶"
                        color: palette.text
                        font.pixelSize: 12

                        TapHandler {
                            onTapped: {
                                treeView.toggleExpanded(root.row);
                            }
                        }
                    }

                    Label {
                        id: label

                        x: root.padding + (root.isTreeNode ? (root.depth + 1) * root.indentation : 0)

                        anchors.verticalCenter: parent.verticalCenter

                        width: parent.width - x - root.padding
                        clip: true

                        text: model.display
                        color: palette.text
                        font.pixelSize: 14
                    }

                    TapHandler {
                        onTapped: {
                            let index = treeView.index(root.row, root.column);

                            treeView.selectionModel.setCurrentIndex(index, ItemSelectionModel.ClearAndSelect);
                        }

                        onDoubleTapped: {
                            if (root.hasChildren) {
                                treeView.toggleExpanded(root.row);
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true

            color: palette.base

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 0

                HorizontalHeaderView {
                    id: header
                    Layout.fillWidth: true
                    syncView: tableView
                    clip: true
                }

                TableView {
                    id: tableView
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    clip: true
                    columnSpacing: 1
                    rowSpacing: 1

                    model: tableModel

                    acceptedButtons: Qt.NoButton
                    selectionBehavior: TableView.SelectRows
                    selectionMode: TableView.ExtendedSelection
                    pointerNavigationEnabled: false
                    property int selectionAnchorRow: -1

                    selectionModel: ItemSelectionModel {
                        model: tableView.model
                    }

                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                    }

                    columnWidthProvider: function(column) {
                        const actionsWidth = 220;
                        const availableWidth = Math.max(
                            0,
                            tableView.width - actionsWidth - 2 * tableView.columnSpacing
                        );

                        switch (column) {
                        case 0: return availableWidth * 0.5; // Filename
                        case 1: return availableWidth * 0.5; // Better Filename
                        case 2: return actionsWidth;          // Actions
                        }

                        return 100;
                    }

                    onWidthChanged: forceLayout()

                    delegate: Rectangle {
                        id: cell

                        implicitWidth: 160
                        implicitHeight: 45

                        required property int row
                        required property int column
                        required property var display
                        required property var edit
                        required property bool selected


                        color: cell.selected ? palette.highlight : palette.base
                        Rectangle {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom

                            height: 2
                            color: Qt.alpha(palette.text, 0.25)

                            z: 10
                        }


                        // Column 0: Original Filename
                        Text {
                            id:filename
                            visible: cell.column === 0

                            anchors.fill: parent
                            anchors.leftMargin: 10

                            horizontalAlignment: Text.AlignLeft
                            verticalAlignment: Text.AlignVCenter

                            text: cell.display ?? ""
                            color: cell.selected ? palette.highlightedText : palette.text


                            TapHandler {
                                id: rowTapHandler
                                acceptedButtons: Qt.LeftButton
                                gesturePolicy: TapHandler.DragThreshold

                                onTapped: function(eventPoint, button) {
                                    const selection = tableView.selectionModel
                                    const index = tableView.index(cell.row, 0)
                                    const ctrl = (rowTapHandler.point.modifiers & Qt.ControlModifier) !== 0
                                    const shift = (rowTapHandler.point.modifiers & Qt.ShiftModifier) !== 0

                                    tableView.forceActiveFocus()

                                    if (shift && tableView.selectionAnchorRow >= 0) {
                                        if (!ctrl)
                                            selection.clearSelection()

                                        const first = Math.min(tableView.selectionAnchorRow, cell.row)
                                        const last = Math.max(tableView.selectionAnchorRow, cell.row)

                                        for (let r = first; r <= last; ++r) {
                                            selection.select(
                                                tableView.index(r, 0),
                                                ItemSelectionModel.Select | ItemSelectionModel.Rows
                                            )
                                        }
                                    } else {
                                        selection.select(
                                            index,
                                            (ctrl
                                                ? ItemSelectionModel.Toggle
                                                : ItemSelectionModel.ClearAndSelect)
                                                | ItemSelectionModel.Rows
                                        )

                                        tableView.selectionAnchorRow = cell.row
                                    }

                                    selection.setCurrentIndex(index, ItemSelectionModel.NoUpdate)
                                }

                                //onDoubleTapped: backend.openFile(cell.row)
                            }

                        }

                        TextField {
                            id: new_filename
                            visible: cell.column === 1
                            anchors.fill: parent
                            anchors.margins: 4
                            
                            color: (cell.selected || tableModel.item_at(cell.row).dirty) ? palette.highlightedText : palette.text

                            text: display ?? ""
                            horizontalAlignment: Text.AlignLeft
                            verticalAlignment: Text.AlignVCenter

                            onTextEdited: {
                                let index = tableView.index(cell.row, cell.column)
                                tableModel.setData(index, text, Qt.EditRole)
                            }

                            background: Rectangle {
                                radius: 4
                                color:  (tableModel.item_at(cell.row).dirty) ? palette.accent : palette.base
                            }
                        }

                        // Actions
                        RowLayout {
                            visible: cell.column === 2

                            anchors.fill: parent
                            anchors.margins: 4

                            ToolButton {
                                id: resetButton

                                icon.source: "icons/x.svg"
                                icon.color: palette.buttonText
                                icon.width: 18
                                icon.height: 18

                                Layout.preferredWidth: 32
                                Layout.fillHeight: true

                                enabled: tableModel.item_at(cell.row).dirty

                                ToolTip.visible: hovered
                                ToolTip.text: "Reset filename"

                                onClicked: backend.resetFilename(cell.row)
                            }

                            Button {
                                id: suggestButton

                                text: qsTr("Suggest")
                                Layout.fillWidth: true
                                hoverEnabled: true

                                background: Rectangle {
                                    radius: 5

                                    color: suggestButton.down ? "#1565c0"
                                        : suggestButton.hovered ? "#bbdefb"
                                        : "#e3f2fd"

                                    border.color: "#90caf9"
                                    border.width: 1
                                }

                                contentItem: Text {
                                    text: suggestButton.text
                                    color: suggestButton.down ? "#ffffff" : "#1565c0"

                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }

                                onClicked: backend.suggestFilename(cell.row)
                            }

                            Button {
                                id: acceptButton

                                text: qsTr("Accept")
                                Layout.fillWidth: true
                                hoverEnabled: true

                                background: Rectangle {
                                    radius: 5

                                    color: acceptButton.down ? "#2e7d32"
                                        : acceptButton.hovered ? "#c8e6c9"
                                        : "#e8f5e9"

                                    border.color: "#a5d6a7"
                                    border.width: 1
                                }

                                contentItem: Text {
                                    text: acceptButton.text
                                    color: acceptButton.down ? "#ffffff" : "#2e7d32"

                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }

                                onClicked: backend.acceptFilename(cell.row)
                            }

                            ToolButton {
                                id: trashButton

                                icon.source: "icons/trash.svg"
                                icon.color: palette.buttonText
                                icon.width: 18
                                icon.height: 18

                                Layout.preferredWidth: 32
                                Layout.fillHeight: true

                                ToolTip.visible: hovered
                                ToolTip.text: "Reset filename"

                                onClicked: {
                                    console.log("Row", cell.row)
                                    trashDialog.targetRow = cell.row
                                    let index = tableModel.index(cell.row, 0)
                                    trashDialog.filename = tableModel.filenameAt(cell.row)
                                    trashDialog.open()
                                }
                            }

                            MessageDialog {
                                id: trashDialog

                                title: "Attention: Delete it?"
                                text: `Do you really want to permanently delete "${trashDialog.filename}"? It's gone forever!`

                                buttons: MessageDialog.Yes | MessageDialog.No

                                property int targetRow: -1
                                property string filename: ""

                                onAccepted: backend.trashFile(targetRow)
                            }
                        }
                    }
                }
            }
        }
    }
}