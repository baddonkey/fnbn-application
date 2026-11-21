from datetime import datetime
import json
import os
from pathlib import Path
import fnbn_backend.proto_extractor as proto_extractor
from fnbn_backend.settings_cli import SettingsCli
import fnbn_backend.tikaContent as tikaContent


class BackendCli:

    def __init__(self, settings: SettingsCli):
        self.settings = settings
        pass

    def processFile(self, filename: str, dryRun: str):

        print(f"Process file {filename}")

        try:

            absolute_path = Path(filename).resolve()

            # read metadata without content
            result = tikaContent.TikaContent().extract_content(str(absolute_path))

            creation_date = ""

            try:
                creation_date = str(result["metadata"]["dcterms:created"])
            except:
                stat = absolute_path.stat()
                creation_date = (
                    datetime.fromtimestamp(stat.st_birthtime).strftime("%Y%m%d")
                    if hasattr(stat, "st_birthtime")
                    else ""
                )

            # resolve prompt
            prompt = next(
                (
                    p["value"]
                    for p in self.settings.prompts
                    if p["name"] == self.settings.promptName
                ),
                None,
            )
            prompt = prompt.format(
                suffix=absolute_path.suffix.lstrip("."), creation_date=creation_date
            )

            print(f"Prompt: {prompt}")

            extractor = proto_extractor.PDFTitleExtractor(
                model=self.settings.modelName,
                dpi=100,
                host=self.settings.ollamaUrl,
                prompt=prompt,
            )

            result = extractor.extract_title(absolute_path)
            new_title = json.loads(result)["filename"]
            new_absolute_path = (absolute_path.parent / new_title).resolve()

            if dryRun == "False":
                os.rename(absolute_path, new_absolute_path)

        except Exception as inst:
            print(inst)

    def _load(self, path: str):
        data = json.loads(path.read_text(encoding="utf-8"))
        self._values.update({key: data[key] for key in self.DEFAULTS if key in data})
