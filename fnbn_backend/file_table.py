from enum import IntEnum
from pathlib import Path
from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    Qt,
    Signal,
    Slot,
    Property
)

class FileColumn(IntEnum):
    FILENAME = 0,
    NEW_FILENAME = 1,
    ACTIONS = 2

class FileItem(QObject):

    dirtyChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.new_filename: str = ""
        self.original_path: Path = None
        self._dirty = False

    @property
    def filename(self) -> str:
        return self.original_path.name

    @Property(bool, notify=dirtyChanged)
    def dirty(self) -> bool:
        return self._dirty

    @dirty.setter
    def dirty(self, value):
        if self._dirty != value:
            self._dirty = value
            self.dirtyChanged.emit()

class FileTableModel(QAbstractTableModel):

    HEADERS = (
        "Filename",
        "New Filename",
        "Actions"
    )

    def __init__(self, items: list[FileItem] | None = None, parent = None):
        super().__init__(parent)
        self._items = list(items) if items is not None else []

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._items)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(FileColumn)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):

        if not index.isValid():
            return None

        item = self._items[index.row()]
        column = index.column()

        if role in (
            Qt.ItemDataRole.DisplayRole,
            Qt.ItemDataRole.EditRole
        ):
            if column == FileColumn.FILENAME:
                return item.filename

            if column == FileColumn.NEW_FILENAME:
                return item.new_filename

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False

        if (role == Qt.ItemDataRole.EditRole and index.column() == FileColumn.NEW_FILENAME):

            item = self.item_at(index.row())

            if item.new_filename == str(value):
                return False

            item.new_filename = str(value)
            item.dirty = (value != item.original_path.name)
            
            self.dataChanged.emit(
                index,
                index,
                [
                    Qt.ItemDataRole.DisplayRole,
                    Qt.ItemDataRole.EditRole
                ],
            )

            return True

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        flags = (Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

        if index.column() == FileColumn.NEW_FILENAME: 
            flags |= Qt.ItemFlag.ItemIsEditable

        return flags

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if (
            orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole
        ):
            return self.HEADERS[section]

    @Slot(int, result=QObject)
    def item_at(self, row: int) -> FileItem:
        ret = self._items[row]
        return ret

    @Slot(int, result=str)
    def filenameAt(self, row):
        return self.item_at(row).original_path.name
    

    def reload(self, absolute_path: str):
        if not absolute_path:
            return

        folder = Path(absolute_path)

        if not folder.is_dir():
            return

        self._items.clear()

        items = list([])

        for entry in sorted(folder.iterdir()):

            # ignore hidden ones
            if entry.name.startswith("."):
                continue

            # for the moment only PDFs
            if not entry.name.lower().endswith(".pdf"):
                continue

            if entry.is_file():
                item = FileItem(parent=self)
                item.original_path = entry
                item.new_filename = entry.name
                items.append(item)
                
        self.beginResetModel()
        self._items = items
        self.endResetModel()

    @Slot(int, int, result=bool)
    def removeRows(self, row: int, count: int = 1, parent=QModelIndex()) -> bool:
        if row < 0 or count <= 0 or row + count > len(self._items):
            return False

        self.beginRemoveRows(parent, row, row + count - 1)

        del self._items[row:row + count]

        self.endRemoveRows()

        return True        