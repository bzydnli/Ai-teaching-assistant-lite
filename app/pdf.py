from io import BytesIO

from pypdf import PdfReader


def extract_pages(file_content: bytes) -> list[tuple[int, str]]:
    reader = PdfReader(BytesIO(file_content))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = " ".join(text.split())

        if text:
            pages.append((page_number, text))

    return pages


def split_text(
    text: str,
    chunk_size: int = 220,
    overlap: int = 40,
) -> list[str]:
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])

        if chunk:
            chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap

    return chunks
