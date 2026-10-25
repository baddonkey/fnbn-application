from pathlib import Path
import pymupdf
import ollama

class PDFTitleExtractor:

    def __init__(
        self,
        model: str = "gemma3:12b",
        dpi: int = 200,
        host: str | None = None,
        prompt: str | None = None,
    ):
        self.model = model
        self.dpi = dpi
        self.prompt = prompt
        self.client = ollama.Client(host=host) if host else ollama.Client()

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

    def extract_title_from_image(self, image: bytes) -> str:
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": self.prompt,
                    "images": [image],
                }
            ],
            options={
                "temperature": 0,
            },
        )

        return (response.message.content or "").strip()

    def extract_title(self, pdf_path: str | Path) -> str | None:
        image = self.render_first_page(pdf_path)
        title = self.extract_title_from_image(image)

        if not title or title.upper() == "UNKNOWN":
            return None

        return title