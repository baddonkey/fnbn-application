import os
from PySide6.QtGui import QStandardItem, QStandardItemModel, Qt
from PySide6.QtCore import QModelIndex

class TreeModel(QStandardItemModel):

    AbsolutePathRole = Qt.UserRole + 1
    PlaceholderRole = Qt.UserRole + 2
    TreeNodeRole = Qt.UserRole + 3

    def __init__(self, parent=None):
        super().__init__(parent)

    def roleNames(self):
        roles = super().roleNames()
        roles[self.AbsolutePathRole] = b"absolutePath"
        return roles

    def add_node(self, parent, name, absolute_path, lazy=True):
        item = QStandardItem(name)
        item.setColumnCount(1)    
        item.setData(absolute_path, self.AbsolutePathRole)

        if lazy:
            placeholder = QStandardItem()
            item.setColumnCount(1)    

            placeholder.setData(True, self.PlaceholderRole)
            item.appendRow(placeholder)

        parent.appendRow(item)
        return item

    def load_children(self, index: QModelIndex):
        if not index.isValid():
            return

        item = self.itemFromIndex(index)

        if item.rowCount() != 1:
            return

        placeholder = item.child(0)

        if not placeholder.data(self.PlaceholderRole):
            return

        absolute_path = item.data(self.AbsolutePathRole)

        try:
            with os.scandir(absolute_path) as entries:
                directories = sorted(
                    [
                        (entry.name, entry.path)
                        for entry in entries
                        if not entry.name.startswith(".")
                        and entry.is_dir(follow_symlinks=False)
                    ],
                    key=lambda x: x[0].lower(),
                )

        except OSError as error:
            print(f"Error loading {absolute_path}: {error}")
            return

        # Remove placeholder
        item.removeRow(0)

        # Add immediate subdirectories
        for name, path in directories:
            self.add_node(item, name, path, lazy=True)