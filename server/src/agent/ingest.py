"""
Teacher utility: upload files to the vector store.

Usage:
    python -m agent.ingest path/to/file.pdf
    python -m agent.ingest path/to/folder/
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

CHROMA_DIR = "./data/chroma"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

LOADERS = {
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
    ".md": TextLoader,
    ".docx": UnstructuredWordDocumentLoader,
}


def load_documents(path: Path):
    if path.is_dir():
        loader = DirectoryLoader(str(path), glob="**/*.*", show_progress=True)
        return loader.load()

    suffix = path.suffix.lower()
    loader_cls = LOADERS.get(suffix)
    if not loader_cls:
        raise ValueError(f"Unsupported file type: {suffix}")
    return loader_cls(str(path)).load()


def ingest(path: str):
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"Path not found: {target}")

    print(f"Loading documents from: {target}")
    docs = load_documents(target)
    print(f"Loaded {len(docs)} document(s)")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        collection_name="documents",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    vectorstore.add_documents(chunks)
    print(f"Ingested {len(chunks)} chunks into the vector store.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m agent.ingest <file_or_folder>")
        sys.exit(1)
    ingest(sys.argv[1])
