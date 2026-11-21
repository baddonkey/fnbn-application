import json
from pathlib import Path

class SettingsCli(): 

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

    def ollamaUrl(self) -> str:
        return self._values["ollamaUrl"]

    def modelName(self) -> str:
        return self._values["modelName"]

    def promptName(self) -> str:
        return self._values["promptName"]

    def prompts(self):
        return self._values["prompts"]