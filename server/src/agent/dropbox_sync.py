import logging
import os
import threading

logger = logging.getLogger(__name__)


def _sync() -> None:
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
            dropbox_folder_path=os.environ.get("DROPBOX_FOLDER", "/"),
            recursive=True,
        )
        docs = loader.load()
        logger.info(f"Dropbox sync: loaded {len(docs)} document(s).")

        # Chunk and ingest
        splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=400)
        chunks = splitter.split_documents(docs)
        get_vectorstore().add_documents(chunks)
        logger.info(f"Dropbox sync: ingested {len(chunks)} chunks. Done.")

    except Exception:
        logger.exception("Dropbox sync failed.")


def start_dropbox_sync() -> None:
    """Start the Dropbox sync in a background thread."""
    thread = threading.Thread(target=_sync, daemon=True)
    thread.start()
