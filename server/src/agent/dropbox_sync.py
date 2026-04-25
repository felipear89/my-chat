import logging
import os
import threading

logger = logging.getLogger(__name__)


def _sync(folder: str) -> None:
    try:
        from langchain_community.document_loaders import DropboxLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        from agent.vectorstore import COLLECTION, _client, get_vectorstore

        logger.info("Dropbox sync: starting...")

        # Clear the entire collection and recreate it
        client = _client()
        client.delete_collection(COLLECTION)
        logger.info("Dropbox sync: vector database cleared.")

        # Load all files from the Dropbox folder
        loader = DropboxLoader(
            dropbox_access_token=os.environ["DROPBOX_ACCESS_TOKEN"],
            dropbox_folder_path=folder,
            recursive=True,
        )
        docs = [d for d in loader.load() if d.metadata.get("source", "").lower().endswith((".pdf"))]

        for doc in docs:
            source = doc.metadata.get("source", "")
            dirs = source.strip("/").split("/")[:-1]  # strip filename, keep directories
            doc.metadata["folder"] = folder
            doc.metadata["subfolder"] = dirs[5] if len(dirs) >= 5 else None

        logger.info(f"Dropbox sync: loaded {len(docs)} document(s).")

        # Chunk and ingest
        splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=400)
        chunks = splitter.split_documents(docs)
        get_vectorstore().add_documents(chunks)
        logger.info(f"Dropbox sync: ingested {len(chunks)} chunks. Done.")

    except Exception:
        logger.exception("Dropbox sync failed.")


def start_dropbox_sync(folder: str) -> None:
    """Start the Dropbox sync in a background thread."""
    thread = threading.Thread(target=_sync, args=(folder,), daemon=True)
    thread.start()
