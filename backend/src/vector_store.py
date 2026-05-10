from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
import hashlib
import gc
import shutil
import json
import math
import time

from langchain_core.documents import Document

from src.embeddings import get_embedding_model, cosine_similarity
from src.session_manager import (
    get_chroma_path,
    create_user_folders,
    update_total_chunks,
)

from src.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_SEARCH_TYPE,
    CHROMA_TOP_K,
)


logger = logging.getLogger(__name__)

DEFAULT_COLLECTION_NAME = CHROMA_COLLECTION_NAME or "rag_interview_notes"

# Lightweight defaults for Render Free / 512 MB RAM.
# Keep same config usage, but prevent huge retrieval memory.
DEFAULT_VECTOR_TOP_K = min(max(int(CHROMA_TOP_K or 5), 3), 5)
DEFAULT_VECTOR_FETCH_K = 12

# File name kept inside chroma path so existing folder structure remains same.
LIGHTWEIGHT_STORE_FILE = "lightweight_vector_store.json"


# ---------------------------------------------------------
# Collection helpers
# ---------------------------------------------------------

def get_collection_name(session_id: str) -> str:
    clean_session = str(session_id).replace("-", "_")
    clean_session = clean_session.replace(" ", "_")

    return f"{DEFAULT_COLLECTION_NAME}_{clean_session[:12]}"


def clean_metadata_value(value):
    if value is None:
        return ""

    if isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


def clean_document_metadata(document: Document) -> Document:
    metadata = document.metadata or {}
    clean_metadata = {}

    for key, value in metadata.items():
        clean_metadata[str(key)] = clean_metadata_value(value)

    return Document(
        page_content=document.page_content or "",
        metadata=clean_metadata,
    )


def clean_documents_for_chroma(documents: List[Document]) -> List[Document]:
    cleaned_docs = []

    if not documents:
        return cleaned_docs

    for doc in documents:
        if not doc:
            continue

        content = (doc.page_content or "").strip()

        if not content:
            continue

        cleaned_doc = clean_document_metadata(doc)

        cleaned_docs.append(
            Document(
                page_content=content,
                metadata=cleaned_doc.metadata,
            )
        )

    return cleaned_docs


# ---------------------------------------------------------
# Stable document IDs
# ---------------------------------------------------------

def create_stable_document_id(document: Document, fallback_index: int) -> str:
    metadata = document.metadata or {}

    pdf_name = metadata.get("pdf_name", metadata.get("source", "pdf"))
    page = metadata.get("page_number", metadata.get("page", "page"))
    chunk_id = metadata.get("chunk_id", fallback_index)
    local_chunk_index = metadata.get("local_chunk_index", "")

    text_hash = hashlib.md5(
        (document.page_content or "").encode("utf-8", errors="ignore")
    ).hexdigest()[:14]

    raw_id = f"{pdf_name}_{page}_{chunk_id}_{local_chunk_index}_{text_hash}"

    safe_id = (
        raw_id.replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace("|", "_")
        .replace(".", "_")
        .replace("(", "_")
        .replace(")", "_")
        .replace("[", "_")
        .replace("]", "_")
        .replace(",", "_")
        .replace(";", "_")
        .replace("'", "_")
        .replace('"', "_")
    )

    return safe_id


def create_document_ids(documents: List[Document]) -> List[str]:
    ids = []

    for index, doc in enumerate(documents, start=1):
        ids.append(create_stable_document_id(doc, index))

    return ids


# ---------------------------------------------------------
# Lightweight persistent vector store helpers
# ---------------------------------------------------------

def get_lightweight_store_path(session_id: str) -> Path:
    create_user_folders(session_id)

    chroma_path = Path(get_chroma_path(session_id))
    chroma_path.mkdir(parents=True, exist_ok=True)

    return chroma_path / LIGHTWEIGHT_STORE_FILE


def get_empty_store(collection_name: str) -> Dict[str, Any]:
    return {
        "collection_name": collection_name,
        "created_at": time.time(),
        "updated_at": time.time(),
        "ids": [],
        "documents": [],
        "metadatas": [],
        "embeddings": [],
    }


def load_lightweight_store(
    session_id: str,
    collection_name: Optional[str] = None,
) -> Dict[str, Any]:
    if collection_name is None:
        collection_name = get_collection_name(session_id)

    store_path = get_lightweight_store_path(session_id)

    if not store_path.exists():
        return get_empty_store(collection_name)

    try:
        with store_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return get_empty_store(collection_name)

        data.setdefault("collection_name", collection_name)
        data.setdefault("ids", [])
        data.setdefault("documents", [])
        data.setdefault("metadatas", [])
        data.setdefault("embeddings", [])
        data.setdefault("created_at", time.time())
        data["updated_at"] = data.get("updated_at", time.time())

        return data

    except Exception as e:
        logger.error(f"Failed to load lightweight vector store: {str(e)}")
        return get_empty_store(collection_name)


def save_lightweight_store(session_id: str, data: Dict[str, Any]) -> bool:
    try:
        store_path = get_lightweight_store_path(session_id)

        data["updated_at"] = time.time()

        with store_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)

        return True

    except Exception as e:
        logger.error(f"Failed to save lightweight vector store: {str(e)}")
        return False


def document_from_store_item(content: str, metadata: Dict) -> Document:
    return Document(
        page_content=content or "",
        metadata=metadata or {},
    )


def score_documents_by_query(
    query: str,
    documents: List[str],
    metadatas: List[Dict],
    embeddings: List[List[float]],
    top_k: int,
) -> List[Tuple[Document, float]]:
    if not query or not query.strip():
        return []

    if not documents or not embeddings:
        return []

    embedding_model = get_embedding_model()
    query_embedding = embedding_model.embed_query(query.strip())

    scored_items = []

    for content, metadata, embedding in zip(documents, metadatas, embeddings):
        score = cosine_similarity(query_embedding, embedding)

        scored_items.append(
            (
                document_from_store_item(content, metadata),
                float(score),
            )
        )

    scored_items.sort(key=lambda item: item[1], reverse=True)

    return scored_items[:top_k]


def keyword_score(query: str, text: str) -> float:
    if not query or not text:
        return 0.0

    query_tokens = set(query.lower().split())
    text_tokens = set(text.lower().split())

    if not query_tokens or not text_tokens:
        return 0.0

    overlap = query_tokens.intersection(text_tokens)

    return len(overlap) / max(len(query_tokens), 1)


def hybrid_score_documents_by_query(
    query: str,
    documents: List[str],
    metadatas: List[Dict],
    embeddings: List[List[float]],
    top_k: int,
) -> List[Tuple[Document, float]]:
    if not query or not query.strip():
        return []

    if not documents:
        return []

    embedding_model = get_embedding_model()
    query_embedding = embedding_model.embed_query(query.strip())

    scored_items = []

    for content, metadata, embedding in zip(documents, metadatas, embeddings):
        vector_score = cosine_similarity(query_embedding, embedding)
        lexical_score = keyword_score(query, content)

        # Hybrid scoring improves lightweight hash retrieval quality.
        final_score = (0.75 * vector_score) + (0.25 * lexical_score)

        scored_items.append(
            (
                document_from_store_item(content, metadata),
                float(final_score),
            )
        )

    scored_items.sort(key=lambda item: item[1], reverse=True)

    return scored_items[:top_k]


def select_mmr_documents(
    query: str,
    scored_items: List[Tuple[Document, float]],
    top_k: int,
) -> List[Document]:
    """
    Lightweight MMR-like selection.

    Keeps diverse chunks by avoiding many chunks from same page/source where possible.
    """

    if not scored_items:
        return []

    selected = []
    seen_pages = set()

    for doc, score in scored_items:
        metadata = doc.metadata or {}

        pdf_name = metadata.get("pdf_name", metadata.get("source", "Unknown PDF"))
        page = metadata.get("page_number", metadata.get("page", "Unknown page"))

        page_key = f"{pdf_name}_{page}"

        if page_key not in seen_pages:
            selected.append(doc)
            seen_pages.add(page_key)

        if len(selected) >= top_k:
            return selected

    for doc, score in scored_items:
        if len(selected) >= top_k:
            break

        if doc not in selected:
            selected.append(doc)

    return selected[:top_k]


# ---------------------------------------------------------
# Lightweight vector store compatibility classes
# ---------------------------------------------------------

class LightweightCollection:
    def __init__(self, session_id: str, collection_name: Optional[str] = None):
        self.session_id = session_id
        self.collection_name = collection_name or get_collection_name(session_id)

    def get(self) -> Dict:
        data = load_lightweight_store(
            session_id=self.session_id,
            collection_name=self.collection_name,
        )

        return {
            "ids": data.get("ids", []),
            "documents": data.get("documents", []),
            "metadatas": data.get("metadatas", []),
            "embeddings": data.get("embeddings", []),
        }

    def delete(self, ids: List[str]) -> bool:
        if not ids:
            return True

        data = load_lightweight_store(
            session_id=self.session_id,
            collection_name=self.collection_name,
        )

        existing_ids = data.get("ids", [])
        documents = data.get("documents", [])
        metadatas = data.get("metadatas", [])
        embeddings = data.get("embeddings", [])

        delete_set = set(ids)

        new_ids = []
        new_documents = []
        new_metadatas = []
        new_embeddings = []

        for doc_id, document, metadata, embedding in zip(
            existing_ids,
            documents,
            metadatas,
            embeddings,
        ):
            if doc_id in delete_set:
                continue

            new_ids.append(doc_id)
            new_documents.append(document)
            new_metadatas.append(metadata)
            new_embeddings.append(embedding)

        data["ids"] = new_ids
        data["documents"] = new_documents
        data["metadatas"] = new_metadatas
        data["embeddings"] = new_embeddings

        return save_lightweight_store(self.session_id, data)


class LightweightRetriever:
    def __init__(
        self,
        vector_store: "LightweightVectorStore",
        search_type: str = "similarity",
        search_kwargs: Optional[Dict] = None,
    ):
        self.vector_store = vector_store
        self.search_type = search_type or "similarity"
        self.search_kwargs = search_kwargs or {}

    def get_relevant_documents(self, query: str) -> List[Document]:
        k = int(self.search_kwargs.get("k", DEFAULT_VECTOR_TOP_K))

        if self.search_type == "mmr":
            fetch_k = int(self.search_kwargs.get("fetch_k", DEFAULT_VECTOR_FETCH_K))
            return self.vector_store.max_marginal_relevance_search(
                query=query,
                k=k,
                fetch_k=fetch_k,
                lambda_mult=float(self.search_kwargs.get("lambda_mult", 0.6)),
            )

        return self.vector_store.similarity_search(
            query=query,
            k=k,
        )

    def invoke(self, query: str) -> List[Document]:
        return self.get_relevant_documents(query)


class LightweightVectorStore:
    def __init__(
        self,
        session_id: str,
        collection_name: Optional[str] = None,
        persist_directory: Optional[str] = None,
        embedding_function=None,
    ):
        self.session_id = session_id
        self.collection_name = collection_name or get_collection_name(session_id)
        self.persist_directory = persist_directory or get_chroma_path(session_id)
        self.embedding_function = embedding_function or get_embedding_model()
        self._collection = LightweightCollection(
            session_id=session_id,
            collection_name=self.collection_name,
        )

    def add_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        if not documents:
            return []

        cleaned_docs = clean_documents_for_chroma(documents)

        if not cleaned_docs:
            return []

        if ids is None:
            ids = create_document_ids(cleaned_docs)

        data = load_lightweight_store(
            session_id=self.session_id,
            collection_name=self.collection_name,
        )

        existing_ids = data.get("ids", [])
        existing_documents = data.get("documents", [])
        existing_metadatas = data.get("metadatas", [])
        existing_embeddings = data.get("embeddings", [])

        id_to_index = {
            doc_id: index
            for index, doc_id in enumerate(existing_ids)
        }

        texts = [doc.page_content or "" for doc in cleaned_docs]
        embeddings = self.embedding_function.embed_documents(texts)

        for doc, doc_id, embedding in zip(cleaned_docs, ids, embeddings):
            metadata = dict(doc.metadata or {})

            if doc_id in id_to_index:
                index = id_to_index[doc_id]
                existing_documents[index] = doc.page_content or ""
                existing_metadatas[index] = metadata
                existing_embeddings[index] = embedding
                continue

            existing_ids.append(doc_id)
            existing_documents.append(doc.page_content or "")
            existing_metadatas.append(metadata)
            existing_embeddings.append(embedding)

        data["ids"] = existing_ids
        data["documents"] = existing_documents
        data["metadatas"] = existing_metadatas
        data["embeddings"] = existing_embeddings

        save_lightweight_store(self.session_id, data)

        return ids

    def get(self) -> Dict:
        data = load_lightweight_store(
            session_id=self.session_id,
            collection_name=self.collection_name,
        )

        return {
            "ids": data.get("ids", []),
            "documents": data.get("documents", []),
            "metadatas": data.get("metadatas", []),
            "embeddings": data.get("embeddings", []),
        }

    def similarity_search(
        self,
        query: str,
        k: int = DEFAULT_VECTOR_TOP_K,
    ) -> List[Document]:
        data = self.get()

        safe_k = min(max(int(k or DEFAULT_VECTOR_TOP_K), 1), 10)

        scored_items = hybrid_score_documents_by_query(
            query=query,
            documents=data.get("documents", []),
            metadatas=data.get("metadatas", []),
            embeddings=data.get("embeddings", []),
            top_k=safe_k,
        )

        return [doc for doc, score in scored_items]

    def similarity_search_with_score(
        self,
        query: str,
        k: int = DEFAULT_VECTOR_TOP_K,
    ) -> List[Tuple[Document, float]]:
        data = self.get()

        safe_k = min(max(int(k or DEFAULT_VECTOR_TOP_K), 1), 10)

        return hybrid_score_documents_by_query(
            query=query,
            documents=data.get("documents", []),
            metadatas=data.get("metadatas", []),
            embeddings=data.get("embeddings", []),
            top_k=safe_k,
        )

    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = DEFAULT_VECTOR_TOP_K,
        fetch_k: int = DEFAULT_VECTOR_FETCH_K,
        lambda_mult: float = 0.6,
    ) -> List[Document]:
        data = self.get()

        safe_k = min(max(int(k or DEFAULT_VECTOR_TOP_K), 1), 10)
        safe_fetch_k = min(max(int(fetch_k or DEFAULT_VECTOR_FETCH_K), safe_k), 20)

        scored_items = hybrid_score_documents_by_query(
            query=query,
            documents=data.get("documents", []),
            metadatas=data.get("metadatas", []),
            embeddings=data.get("embeddings", []),
            top_k=safe_fetch_k,
        )

        return select_mmr_documents(
            query=query,
            scored_items=scored_items,
            top_k=safe_k,
        )

    def as_retriever(
        self,
        search_type: str = "similarity",
        search_kwargs: Optional[Dict] = None,
    ) -> LightweightRetriever:
        return LightweightRetriever(
            vector_store=self,
            search_type=search_type,
            search_kwargs=search_kwargs,
        )


# ---------------------------------------------------------
# Vector store creation
# ---------------------------------------------------------

def get_vector_store(
    session_id: str,
    collection_name: Optional[str] = None,
) -> LightweightVectorStore:
    create_user_folders(session_id)

    chroma_path = get_chroma_path(session_id)

    if collection_name is None:
        collection_name = get_collection_name(session_id)

    embedding_model = get_embedding_model()

    vector_store = LightweightVectorStore(
        session_id=session_id,
        collection_name=collection_name,
        persist_directory=chroma_path,
        embedding_function=embedding_model,
    )

    return vector_store


def get_vector_store_path(session_id: str) -> str:
    return get_chroma_path(session_id)


# ---------------------------------------------------------
# Reset / delete helpers
# ---------------------------------------------------------

def delete_existing_collection_items(session_id: str) -> bool:
    """
    Delete all items inside the current lightweight collection.

    This is useful when re-uploading/indexing the same PDF with new chunk settings.
    """

    try:
        vector_store = get_vector_store(session_id=session_id)
        collection = vector_store._collection

        existing = collection.get()
        ids = existing.get("ids", [])

        if ids:
            collection.delete(ids=ids)

        update_total_chunks(session_id, 0)

        del vector_store
        gc.collect()

        return True

    except Exception as e:
        logger.error(f"Failed to delete existing collection items: {str(e)}")
        return False


def delete_chroma_directory(session_id: str) -> bool:
    """
    Hard delete vector directory for the session.

    Kept same function name for existing code compatibility.
    """

    try:
        chroma_path = Path(get_chroma_path(session_id))

        if chroma_path.exists():
            shutil.rmtree(chroma_path, ignore_errors=True)

        update_total_chunks(session_id, 0)
        gc.collect()

        return True

    except Exception as e:
        logger.error(f"Failed to delete Chroma directory: {str(e)}")
        return False


def reset_vector_store(session_id: str, hard_reset: bool = False) -> bool:
    if hard_reset:
        return delete_chroma_directory(session_id=session_id)

    return delete_existing_collection_items(session_id=session_id)


def delete_collection(session_id: str) -> bool:
    return delete_existing_collection_items(session_id=session_id)


# ---------------------------------------------------------
# Add documents
# ---------------------------------------------------------

def add_documents_to_vector_store(
    session_id: str,
    documents: List[Document],
    collection_name: Optional[str] = None,
    reset_before_add: bool = True,
) -> Dict:
    if not documents:
        return {
            "success": False,
            "total_added": 0,
            "message": "No documents provided for vector storage.",
        }

    try:
        cleaned_docs = clean_documents_for_chroma(documents)

        if not cleaned_docs:
            return {
                "success": False,
                "total_added": 0,
                "message": "No valid documents after cleaning.",
            }

        if collection_name is None:
            collection_name = get_collection_name(session_id)

        if reset_before_add:
            delete_existing_collection_items(session_id=session_id)

        vector_store = get_vector_store(
            session_id=session_id,
            collection_name=collection_name,
        )

        ids = create_document_ids(cleaned_docs)

        unique_docs = []
        unique_ids = []
        seen_ids = set()
        seen_content_hashes = set()

        for doc, doc_id in zip(cleaned_docs, ids):
            content = (doc.page_content or "").strip()

            content_hash = hashlib.md5(
                content.encode("utf-8", errors="ignore")
            ).hexdigest()

            if doc_id in seen_ids:
                continue

            if content_hash in seen_content_hashes:
                continue

            seen_ids.add(doc_id)
            seen_content_hashes.add(content_hash)

            metadata = dict(doc.metadata or {})
            metadata["vector_id"] = doc_id
            metadata["content_hash"] = content_hash[:14]
            metadata["store_type"] = "lightweight_json"

            unique_docs.append(
                Document(
                    page_content=content,
                    metadata=metadata,
                )
            )
            unique_ids.append(doc_id)

        if not unique_docs:
            return {
                "success": False,
                "total_added": 0,
                "message": "No unique documents to add.",
            }

        # Small batches keep memory low on Render Free.
        batch_size = 16
        total_added = 0

        for start in range(0, len(unique_docs), batch_size):
            end = start + batch_size

            vector_store.add_documents(
                documents=unique_docs[start:end],
                ids=unique_ids[start:end],
            )

            total_added += len(unique_docs[start:end])

            gc.collect()

        update_total_chunks(session_id, total_added)

        result = {
            "success": True,
            "total_added": total_added,
            "persist_directory": get_chroma_path(session_id),
            "collection_name": collection_name,
            "store_type": "lightweight_json",
            "message": "Documents stored in lightweight vector store successfully.",
            "sample_ids": unique_ids[:5],
        }

        del vector_store
        gc.collect()

        return result

    except Exception as e:
        logger.error(f"Failed to add documents to vector store: {str(e)}")

        return {
            "success": False,
            "total_added": 0,
            "message": str(e),
        }


def build_vector_store_from_chunks(
    session_id: str,
    chunks: List[Document],
    reset_before_add: bool = True,
) -> Dict:
    return add_documents_to_vector_store(
        session_id=session_id,
        documents=chunks,
        reset_before_add=reset_before_add,
    )


# ---------------------------------------------------------
# Search helpers
# ---------------------------------------------------------

def similarity_search(
    session_id: str,
    query: str,
    top_k: int = DEFAULT_VECTOR_TOP_K,
    collection_name: Optional[str] = None,
) -> List[Document]:
    if not query or not query.strip():
        return []

    safe_top_k = int(top_k or DEFAULT_VECTOR_TOP_K)

    if safe_top_k <= 0:
        safe_top_k = DEFAULT_VECTOR_TOP_K

    safe_top_k = min(max(safe_top_k, 1), 10)

    vector_store = get_vector_store(
        session_id=session_id,
        collection_name=collection_name,
    )

    results = vector_store.similarity_search(
        query=query,
        k=safe_top_k,
    )

    del vector_store
    gc.collect()

    return results


def similarity_search_with_score(
    session_id: str,
    query: str,
    top_k: int = DEFAULT_VECTOR_TOP_K,
    collection_name: Optional[str] = None,
) -> List[Dict]:
    if not query or not query.strip():
        return []

    safe_top_k = int(top_k or DEFAULT_VECTOR_TOP_K)

    if safe_top_k <= 0:
        safe_top_k = DEFAULT_VECTOR_TOP_K

    safe_top_k = min(max(safe_top_k, 1), 10)

    vector_store = get_vector_store(
        session_id=session_id,
        collection_name=collection_name,
    )

    results = vector_store.similarity_search_with_score(
        query=query,
        k=safe_top_k,
    )

    formatted_results = []

    for doc, score in results:
        metadata = doc.metadata or {}

        formatted_results.append(
            {
                "score": float(score) if score is not None else None,
                "pdf_name": metadata.get(
                    "pdf_name",
                    metadata.get("source", "Unknown PDF"),
                ),
                "page": metadata.get(
                    "page_number",
                    metadata.get("page", "Unknown page"),
                ),
                "chunk_id": metadata.get("chunk_id", ""),
                "section_title": metadata.get("section_title", ""),
                "chunk_size": metadata.get("chunk_size", len(doc.page_content or "")),
                "content_preview": (doc.page_content or "")[:700],
                "content": doc.page_content,
                "metadata": metadata,
            }
        )

    del vector_store
    gc.collect()

    return formatted_results


def mmr_search(
    session_id: str,
    query: str,
    top_k: int = DEFAULT_VECTOR_TOP_K,
    fetch_k: int = DEFAULT_VECTOR_FETCH_K,
    collection_name: Optional[str] = None,
) -> List[Document]:
    """
    Lightweight MMR search gives more diverse chunks.
    """

    if not query or not query.strip():
        return []

    safe_top_k = min(max(int(top_k or DEFAULT_VECTOR_TOP_K), 1), 10)
    safe_fetch_k = min(max(int(fetch_k or DEFAULT_VECTOR_FETCH_K), safe_top_k), 20)

    vector_store = get_vector_store(
        session_id=session_id,
        collection_name=collection_name,
    )

    results = vector_store.max_marginal_relevance_search(
        query=query,
        k=safe_top_k,
        fetch_k=safe_fetch_k,
        lambda_mult=0.6,
    )

    del vector_store
    gc.collect()

    return results


def get_retriever(
    session_id: str,
    top_k: int = DEFAULT_VECTOR_TOP_K,
    search_type: str = CHROMA_SEARCH_TYPE,
):
    vector_store = get_vector_store(session_id=session_id)

    safe_top_k = int(top_k or DEFAULT_VECTOR_TOP_K)

    if safe_top_k <= 0:
        safe_top_k = DEFAULT_VECTOR_TOP_K

    safe_top_k = min(max(safe_top_k, 1), 10)

    safe_search_type = search_type or "mmr"

    if safe_search_type == "mmr":
        return vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": safe_top_k,
                "fetch_k": min(max(safe_top_k * 3, DEFAULT_VECTOR_FETCH_K), 20),
                "lambda_mult": 0.6,
            },
        )

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": safe_top_k},
    )


def debug_search_topic(
    session_id: str,
    topic: str,
    top_k: int = DEFAULT_VECTOR_TOP_K,
) -> Dict:
    """
    Helper to test if a specific topic is indexed and retrievable.
    Call this from API/self-test when RAG gives weak answers.
    """

    try:
        results = similarity_search_with_score(
            session_id=session_id,
            query=topic,
            top_k=top_k,
        )

        return {
            "success": True,
            "topic": topic,
            "total_results": len(results),
            "results": results,
        }

    except Exception as e:
        return {
            "success": False,
            "topic": topic,
            "total_results": 0,
            "results": [],
            "error": str(e),
        }


# ---------------------------------------------------------
# Status helpers
# ---------------------------------------------------------

def get_vector_store_status(session_id: str) -> Dict:
    try:
        vector_store = get_vector_store(session_id=session_id)
        data = vector_store.get()

        ids = data.get("ids", [])
        metadatas = data.get("metadatas", [])
        documents = data.get("documents", [])

        pdfs = {}

        for metadata, content in zip(metadatas, documents):
            metadata = metadata or {}

            pdf_name = metadata.get(
                "pdf_name",
                metadata.get("source", "Unknown PDF"),
            )

            page = metadata.get(
                "page_number",
                metadata.get("page", "Unknown page"),
            )

            section_title = metadata.get("section_title", "")

            if pdf_name not in pdfs:
                pdfs[pdf_name] = {
                    "chunks": 0,
                    "pages": set(),
                    "sections": set(),
                    "total_chars": 0,
                }

            pdfs[pdf_name]["chunks"] += 1
            pdfs[pdf_name]["pages"].add(str(page))
            pdfs[pdf_name]["total_chars"] += len(content or "")

            if section_title:
                pdfs[pdf_name]["sections"].add(str(section_title))

        clean_pdfs = {}

        for pdf_name, info in pdfs.items():
            clean_pdfs[pdf_name] = {
                "chunks": info["chunks"],
                "pages": sorted(
                    list(info["pages"]),
                    key=lambda x: int(x) if str(x).isdigit() else 999999,
                ),
                "total_pages_found": len(info["pages"]),
                "total_chars": info["total_chars"],
                "average_chunk_chars": round(
                    info["total_chars"] / info["chunks"],
                    2,
                )
                if info["chunks"]
                else 0,
                "sample_sections": sorted(list(info["sections"]))[:10],
            }

        result = {
            "success": True,
            "ready": len(ids) > 0,
            "total_vectors": len(ids),
            "pdfs": clean_pdfs,
            "persist_directory": get_chroma_path(session_id),
            "collection_name": get_collection_name(session_id),
            "store_type": "lightweight_json",
            "default_top_k": DEFAULT_VECTOR_TOP_K,
            "default_fetch_k": DEFAULT_VECTOR_FETCH_K,
            "search_type": CHROMA_SEARCH_TYPE or "mmr",
        }

        del vector_store
        gc.collect()

        return result

    except Exception as e:
        return {
            "success": False,
            "ready": False,
            "total_vectors": 0,
            "pdfs": {},
            "persist_directory": get_chroma_path(session_id),
            "collection_name": get_collection_name(session_id),
            "store_type": "lightweight_json",
            "error": str(e),
        }


def is_vector_store_ready(session_id: str) -> bool:
    status = get_vector_store_status(session_id)
    return bool(status.get("ready"))


# ---------------------------------------------------------
# Full indexing pipeline
# ---------------------------------------------------------

def index_documents_pipeline(
    session_id: str,
    documents: List[Document],
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
    reset_before_add: bool = True,
) -> Dict:
    try:
        from src.chunker import chunk_documents
        from src.config import CHUNK_SIZE, CHUNK_OVERLAP

        if not documents:
            return {
                "success": False,
                "stage": "input",
                "message": "No documents received for indexing.",
                "total_chunks": 0,
            }

        if chunk_size is None:
            chunk_size = CHUNK_SIZE

        if chunk_overlap is None:
            chunk_overlap = CHUNK_OVERLAP

        chunk_result = chunk_documents(
            documents=documents,
            session_id=session_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        if not chunk_result.get("success"):
            return {
                "success": False,
                "stage": "chunking",
                "message": chunk_result.get("error", "Chunking failed."),
                "total_chunks": 0,
            }

        chunks = chunk_result["chunks"]

        store_result = build_vector_store_from_chunks(
            session_id=session_id,
            chunks=chunks,
            reset_before_add=reset_before_add,
        )

        if not store_result.get("success"):
            return {
                "success": False,
                "stage": "vector_store",
                "message": store_result.get("message", "Vector store failed."),
                "total_chunks": len(chunks),
            }

        return {
            "success": True,
            "stage": "completed",
            "message": "Documents indexed successfully.",
            "total_chunks": len(chunks),
            "chunk_stats": {
                "pdf_chunk_counts": chunk_result.get("pdf_chunk_counts", {}),
                "pdf_page_counts": chunk_result.get("pdf_page_counts", {}),
                "stats": chunk_result.get("stats", {}),
            },
            "vector_store": store_result,
        }

    except Exception as e:
        logger.error(f"Index pipeline failed: {str(e)}")

        return {
            "success": False,
            "stage": "error",
            "message": str(e),
            "total_chunks": 0,
        }


# ---------------------------------------------------------
# API helper
# ---------------------------------------------------------

def get_vector_store_api_summary(session_id: str) -> Dict:
    status = get_vector_store_status(session_id)

    return {
        "session_id": session_id,
        "ready": status.get("ready", False),
        "total_vectors": status.get("total_vectors", 0),
        "pdfs": status.get("pdfs", {}),
        "persist_directory": status.get("persist_directory"),
        "collection_name": status.get("collection_name"),
        "store_type": status.get("store_type", "lightweight_json"),
        "default_top_k": status.get("default_top_k"),
        "default_fetch_k": status.get("default_fetch_k"),
        "search_type": status.get("search_type"),
    }


# ---------------------------------------------------------
# Self test
# ---------------------------------------------------------

def run_vector_store_self_test(session_id: str) -> Dict:
    try:
        test_docs = [
            Document(
                page_content=(
                    "Machine learning is a branch of artificial intelligence. "
                    "It allows systems to learn from data without being explicitly programmed. "
                    "It includes supervised learning, unsupervised learning, and reinforcement learning."
                ),
                metadata={
                    "pdf_name": "test_notes.pdf",
                    "source": "test_notes.pdf",
                    "page_number": 1,
                    "page": 1,
                    "chunk_id": 1,
                    "section_title": "Machine Learning",
                },
            ),
            Document(
                page_content=(
                    "DBMS is used to store, organize, and manage data. "
                    "It supports tables, queries, indexing, transactions, and normalization."
                ),
                metadata={
                    "pdf_name": "test_notes.pdf",
                    "source": "test_notes.pdf",
                    "page_number": 2,
                    "page": 2,
                    "chunk_id": 2,
                    "section_title": "DBMS",
                },
            ),
        ]

        store_result = build_vector_store_from_chunks(
            session_id=session_id,
            chunks=test_docs,
            reset_before_add=True,
        )

        search_result = similarity_search_with_score(
            session_id=session_id,
            query="What is DBMS?",
            top_k=2,
        )

        mmr_result = [
            {
                "content_preview": doc.page_content[:300],
                "metadata": doc.metadata,
            }
            for doc in mmr_search(
                session_id=session_id,
                query="Explain machine learning types",
                top_k=2,
            )
        ]

        status = get_vector_store_status(session_id)

        return {
            "success": store_result.get("success", False),
            "store_result": store_result,
            "search_result": search_result,
            "mmr_result": mmr_result,
            "status": status,
            "message": "Lightweight vector store self-test completed.",
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
        }


if __name__ == "__main__":
    test_session_id = "test_session"
    print(run_vector_store_self_test(test_session_id))
