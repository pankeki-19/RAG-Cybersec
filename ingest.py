"""Carga los PDFs de docs/, los divide en fragmentos y guarda sus embeddings en PostgreSQL."""
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag import get_vector_store


def main() -> None:
    pdfs = sorted(Path("docs").glob("*.pdf"))
    if not pdfs:
        raise SystemExit("No hay PDFs en docs/. Descarga los documentos primero (ver README).")

    pages = []
    for pdf in pdfs:
        print(f"Cargando {pdf.name}...")
        pages.extend(PyPDFLoader(str(pdf)).load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(pages)
    print(f"{len(pages)} páginas -> {len(chunks)} fragmentos")

    store = get_vector_store(reset=True)  # borra la colección anterior para no duplicar
    store.add_documents(chunks)
    print("Listo: embeddings guardados en PostgreSQL.")


if __name__ == "__main__":
    main()
