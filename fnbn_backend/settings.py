import json
from pathlib import Path
from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtGui import QFont, QFontDatabase

class Settings(QObject): 
    settingsChanged = Signal()
    loaded = Signal(str)
    error = Signal(str)

    DEFAULTS = {
        "ollamaUrl": "http://localhost:11434",
        "modelName": "qwen3-vl:2b-instruct-q8_0",
        "promptName": "Default",
        "prompts": [],
    }    

    def __init__(self, path, parent=None):
        super().__init__(parent)

        self._path = Path(path)

        # load from user's home
        try:
            self._values = {}
            self._values = self.DEFAULTS.copy()
            self._load(self._path)
        except:
            self._values = {}
            self._values = self.DEFAULTS.copy()

            

            self._load(Path(__file__).resolve().parent / "settings-template.json")

    def _load(self, path: str):
        data = json.loads(path.read_text(encoding="utf-8"))
        self._values.update({
            key: data[key]
            for key in self.DEFAULTS
            if key in data
        })

    @Property(str, notify=settingsChanged)
    def ollamaUrl(self) -> str:
        return self._values["ollamaUrl"]

    @Property(str, notify=settingsChanged)
    def modelName(self) -> str:
        return self._values["modelName"]

    @Property(str, notify=settingsChanged)
    def promptName(self) -> str:
        return self._values["promptName"]

    @Property("QVariantList", notify=settingsChanged)
    def prompts(self):
        return self._values["prompts"]
    
    @Slot(str, str, str)
    def save(self, ollamaUrl: str, modelName: str, promptName: str) -> bool:

        self._path.parent.mkdir(parents=True, exist_ok=True)

        values = self._values.copy()
        values["ollamaUrl"] = ollamaUrl.strip()
        values["modelName"] = modelName.strip()
        values["promptName"] = promptName.strip()
       
        print(f"Url: {ollamaUrl}, Model: {modelName}, Prompt-Name: {promptName}")

        temporary_path = self._path.with_suffix(".json.tmp")
        temporary_path.write_text(
                json.dumps(values, indent=4) + "\n",
                encoding="utf-8",
            )
        temporary_path.replace(self._path)

        self._values = values.copy()

        self.settingsChanged.emit()

        return True

    @Property(QFont, constant=True)
    def fixedFont(self):
        return QFontDatabase.systemFont(
            QFontDatabase.SystemFont.FixedFont
        )


    @Slot(int, str)
    def updatePromptValue(self, index: int, value: str):
        
        print('Update prompt value')

        prompts = self._values["prompts"]

        if 0 <= index < len(prompts):
            prompts[index]["value"] = value