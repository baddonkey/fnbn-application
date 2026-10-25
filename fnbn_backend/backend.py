import json
from fnbn_backend import file_table
from fnbn_backend.treemodel import TreeModel
from PySide6.QtCore import QModelIndex, QObject, QUrl, Qt, Signal, Slot
from PySide6.QtGui import QDesktopServices
import os
from pathlib import Path
import fnbn_backend.tikaContent as tikaContent
import fnbn_backend.proto_extractor as proto_extractor
from send2trash import send2trash

class Backend(QObject):
    treeReloaded = Signal()

    def __init__(self, model: TreeModel, tableModel: file_table.FileTableModel):
        super().__init__()
        self.model = model
        self.tableModel = tableModel

    @Slot(QUrl)
    def folder_selected(self, folder_url: QUrl):
        folder_path = folder_url.toLocalFile()
        self.__loadFolderToModel(folder_path)

    @Slot(QModelIndex)
    def treeNodeSelected(self, index):
        if not index.isValid():
            return

        absolute_path = index.data(TreeModel.AbsolutePathRole)
        self.tableModel.reload(absolute_path)

    @Slot(QModelIndex)
    def treeNodeExpanded(self, index):
        self.model.load_children(index)

    @Slot(int)
    def suggestFilename(self, row):
        
        item = self.tableModel.item_at(row)
        absolute_path = item.original_path.resolve()

        # read metadata without content
        result = tikaContent.TikaContent().extract_content(str(absolute_path))
        creation_date = str(result['metadata']["dcterms:created"])

        # extract the title by sending the first PDF-page as an image to ollama
        prompt = f"""
        You are a filename generator, not a document summarizer.

        Generate exactly ONE filename using the exact title of the document. If no title is found use to a maximum of 5 descriptive keywords.

        Use this creation date of no date is found on the document: {creation_date}

        Rules:
        - Format: YYYYMMDD_Title.{item.original_path.suffix.lstrip('.')}
        - Use an actual 8-digit document date.
        - Never repeat words.
        - Use underscores instead of spaces.
        - Never include the literal word "extension".
        - Never summarize the document.
        - Never output explanations.
        - The filename must be at most 120 characters long.
        - Return only the JSON object requested by the output schema.
        """

        extractor = proto_extractor.PDFTitleExtractor(
            model="qwen3-vl:4b-instruct-q8_0",
            dpi=200,
            host="http://192.168.1.49:11434",
            prompt = prompt
        )

        new_title = json.loads(extractor.extract_title(absolute_path))["filename"]
        index_newfilename = self.tableModel.index(row, 1)
        item.dirty = True
        self.tableModel.setData(index_newfilename, new_title, Qt.ItemDataRole.EditRole)

    @Slot(int)
    def openFile(self, row):
        item = self.tableModel.item_at(row)
        absolute_path = item.original_path.resolve()
        QDesktopServices.openUrl(QUrl.fromLocalFile(absolute_path))

    @Slot(int)
    def acceptFilename(self, row):
        item = self.tableModel.item_at(row)
        absolute_path = item.original_path.resolve()

        new_absolute_path = (item.original_path.parent / item.new_filename).resolve()
        os.rename(absolute_path, new_absolute_path)

        item.original_path = new_absolute_path
        #self.tableModel.setData(self.tableModel.index(row,0), new_absolute_path, Qt.ItemDataRole.DisplayRole)
        item.dirty = False

        top_left = self.tableModel.index(row, 0)
        bottom_right = self.tableModel.index(row, 1)

        self.tableModel.dataChanged.emit(
            top_left,
            bottom_right,
            [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]
        )

    @Slot(int)
    def trashFile(self, row):
        item = self.tableModel.item_at(row)

        if item is None:
            return

        absolute_path = item.original_path.resolve()

        try:
            # Move file to OS Trash / Recycle Bin
            #send2trash(str(absolute_path))

            absolute_path.unlink()

            # Remove row from the table model
            self.tableModel.removeRows(row, 1)

        except Exception as e:
            print(f"Failed to trash {absolute_path}: {e}")

    def __loadFolderToModel(self, folder_path: str):

        self.model.clear()

        root = self.model.add_node(self.model, Path(folder_path).name, folder_path, True)
        self.model.load_children(self.model.indexFromItem(root))

        self.treeReloaded.emit()
