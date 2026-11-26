"""Leitura local de bases didáticas em TXT e PDF."""

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


MAX_BYTES = 20 * 1024 * 1024
MAX_PAGES = 100
MAX_CHARS = 250_000


def extract_document(filename: str, data: bytes) -> str:
    """Extrai texto de um arquivo enviado, com limites adequados ao app gratuito."""
    if not data:
        raise ValueError("O arquivo está vazio.")
    if len(data) > MAX_BYTES:
        raise ValueError("O arquivo ultrapassa o limite de 20 MB.")

    extension = Path(filename).suffix.lower()
    if extension == ".txt":
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("Salve o arquivo TXT com codificação UTF-8.") from exc
    elif extension == ".pdf":
        try:
            reader = PdfReader(BytesIO(data))
            if reader.is_encrypted:
                raise ValueError("Envie um PDF sem senha para permitir a leitura do texto.")
            if len(reader.pages) > MAX_PAGES:
                raise ValueError("O PDF deve ter no máximo 100 páginas.")
            pages = []
            for number, page in enumerate(reader.pages, 1):
                content = (page.extract_text() or "").strip()
                if content:
                    pages.append(f"Página {number}\n{content}")
            text = "\n\n".join(pages)
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError("Não foi possível ler este PDF. Verifique se o arquivo está íntegro.") from exc
    else:
        raise ValueError("Envie um arquivo TXT ou PDF.")

    if not text.strip():
        raise ValueError("Nenhum texto foi encontrado. PDFs escaneados precisam de OCR antes do envio.")
    if len(text) > MAX_CHARS:
        raise ValueError("O texto extraído é muito extenso. Envie um arquivo menor.")
    return text
