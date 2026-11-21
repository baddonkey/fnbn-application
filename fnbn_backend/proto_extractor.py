from abc import ABC
from pathlib import Path
import pymupdf
import ollama


class TitleExtractorFactory(ABC):

    def getInstance(
        file_path: str,
        model: str = "gemma3:4b",
        dpi: int = 200,
        host: str | None = None,
        prompt: str | None = None,
    ):

        absolute_path = Path(file_path)

        suffix = absolute_path.suffix

        match suffix.lower():
            case ".pdf":
                return PDFTitleExtractor(model, dpi, host, prompt)
            case ".png":
                return ImageTitleExtractor(model, dpi, host, prompt)
            case _:
                SystemExit(f"Not supported file format {suffix.lower()}")


class ImageTitleExtractor(ABC):

    def __init__(
        self,
        model: str = "gemma3:4b",
        dpi: int = 200,
        host: str | None = None,
        prompt: str | None = None,
    ):
        super().__init__()
        self.model = model
        self.dpi = dpi
        self.prompt = prompt
        self.client = ollama.Client(host=host) if host else ollama.Client()

    def extract_title_with_image(self, image: bytes) -> str:
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": self.prompt,
                    "images": [image],
                }
            ],
            format="json",
            stream=False,
            options={
                "temperature": 0,
            },
        )

        return (response.message.content or "").strip()

    def extract_title(self, filepath: str | Path) -> str | None:
        image = Path(filepath).read_bytes()
        title = self.extract_title_with_image(image)

        if not title or title.upper() == "UNKNOWN":
            return None
        return title


class PDFTitleExtractor(ImageTitleExtractor):

    def __init__(self, model="gemma3:4b", dpi=200, host=None, prompt=None):
        super().__init__(model, dpi, host, prompt)

    def render_first_page(self, pdf_path: str | Path) -> bytes:
        pdf_path = Path(pdf_path)

        if not pdf_path.is_file():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        with pymupdf.open(pdf_path) as doc:
            if len(doc) == 0:
                raise ValueError("PDF contains no pages")

            page = doc[0]
            pix = page.get_pixmap(dpi=self.dpi, alpha=False)

            return pix.tobytes("png")

    def extract_title(self, file_path: str | Path) -> str | None:
        image = self.render_first_page(file_path)
        title = self.extract_title_from_image(image)

        if not title or title.upper() == "UNKNOWN":
            return None

        return title
