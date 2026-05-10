# from pathlib import Path
# from typing import Dict, List, Optional
# import logging
# import hashlib
# import gc

# from langchain_core.documents import Document
# from langchain_chroma import Chroma

# from src.embeddings import get_embedding_model
# from src.session_manager import (
#     get_chroma_path,
#     create_user_folders,
#     update_total_chunks,
# )


# logger = logging.getLogger(__name__)

# DEFAULT_COLLECTION_NAME = "rag_interview_notes"


# def get_collection_name(session_id: str) -> str:
#     clean_session = str(session_id).replace("-", "_")
#     return f"{DEFAULT_COLLECTION_NAME}_{clean_session[:12]}"


# def clean_metadata_value(value):
#     if value is None:
#         return ""

#     if isinstance(value, (str, int, float, bool)):
#         return value

#     return str(value)


# def clean_document_metadata(document: Document) -> Document:
#     metadata = document.metadata or {}
#     clean_metadata = {}

#     for key, value in metadata.items():
#         clean_metadata[str(key)] = clean_metadata_value(value)

#     return Document(
#         page_content=document.page_content,
#         metadata=clean_metadata,
#     )


# def clean_documents_for_chroma(documents: List[Document]) -> List[Document]:
#     cleaned_docs = []

#     for doc in documents:
#         if not doc:
#             continue

#         if not doc.page_content or not doc.page_content.strip():
#             continue

#         cleaned_docs.append(clean_document_metadata(doc))

#     return cleaned_docs


# def create_stable_document_id(document: Document, fallback_index: int) -> str:
#     metadata = document.metadata or {}

#     pdf_name = metadata.get("pdf_name", metadata.get("source", "pdf"))
#     page = metadata.get("page_number", metadata.get("page", "page"))
#     chunk_id = metadata.get("chunk_id", fallback_index)

#     text_hash = hashlib.md5(
#         document.page_content.encode("utf-8", errors="ignore")
#     ).hexdigest()[:12]

#     raw_id = f"{pdf_name}_{page}_{chunk_id}_{text_hash}"

#     safe_id = (
#         raw_id.replace(" ", "_")
#         .replace("/", "_")
#         .replace("\\", "_")
#         .replace(":", "_")
#         .replace("|", "_")
#         .replace(".", "_")
#         .replace("(", "_")
#         .replace(")", "_")
#         .replace("[", "_")
#         .replace("]", "_")
#     )

#     return safe_id


# def create_document_ids(documents: List[Document]) -> List[str]:
#     ids = []

#     for index, doc in enumerate(documents, start=1):
#         ids.append(create_stable_document_id(doc, index))

#     return ids


# def get_vector_store(
#     session_id: str,
#     collection_name: Optional[str] = None,
# ) -> Chroma:
#     create_user_folders(session_id)

#     chroma_path = get_chroma_path(session_id)

#     if collection_name is None:
#         collection_name = get_collection_name(session_id)

#     embedding_model = get_embedding_model()

#     vector_store = Chroma(
#         collection_name=collection_name,
#         persist_directory=chroma_path,
#         embedding_function=embedding_model,
#     )

#     return vector_store


# def get_vector_store_path(session_id: str) -> str:
#     return get_chroma_path(session_id)


# def delete_existing_collection_items(session_id: str) -> bool:
#     try:
#         vector_store = get_vector_store(session_id=session_id)
#         collection = vector_store._collection

#         existing = collection.get()
#         ids = existing.get("ids", [])

#         if ids:
#             collection.delete(ids=ids)

#         update_total_chunks(session_id, 0)

#         del vector_store
#         gc.collect()

#         return True

#     except Exception as e:
#         logger.error(f"Failed to delete existing collection items: {str(e)}")
#         return False


# def reset_vector_store(session_id: str) -> bool:
#     return delete_existing_collection_items(session_id=session_id)


# def delete_collection(session_id: str) -> bool:
#     return delete_existing_collection_items(session_id=session_id)


# def add_documents_to_vector_store(
#     session_id: str,
#     documents: List[Document],
#     collection_name: Optional[str] = None,
#     reset_before_add: bool = True,
# ) -> Dict:
#     if not documents:
#         return {
#             "success": False,
#             "total_added": 0,
#             "message": "No documents provided for vector storage.",
#         }

#     try:
#         cleaned_docs = clean_documents_for_chroma(documents)

#         if not cleaned_docs:
#             return {
#                 "success": False,
#                 "total_added": 0,
#                 "message": "No valid documents after cleaning.",
#             }

#         if collection_name is None:
#             collection_name = get_collection_name(session_id)

#         if reset_before_add:
#             delete_existing_collection_items(session_id=session_id)

#         vector_store = get_vector_store(
#             session_id=session_id,
#             collection_name=collection_name,
#         )

#         ids = create_document_ids(cleaned_docs)

#         unique_docs = []
#         unique_ids = []
#         seen_ids = set()

#         for doc, doc_id in zip(cleaned_docs, ids):
#             if doc_id in seen_ids:
#                 continue

#             seen_ids.add(doc_id)
#             unique_docs.append(doc)
#             unique_ids.append(doc_id)

#         vector_store.add_documents(
#             documents=unique_docs,
#             ids=unique_ids,
#         )

#         update_total_chunks(session_id, len(unique_docs))

#         result = {
#             "success": True,
#             "total_added": len(unique_docs),
#             "persist_directory": get_chroma_path(session_id),
#             "collection_name": collection_name,
#             "message": "Documents stored in ChromaDB successfully.",
#         }

#         del vector_store
#         gc.collect()

#         return result

#     except Exception as e:
#         logger.error(f"Failed to add documents to vector store: {str(e)}")

#         return {
#             "success": False,
#             "total_added": 0,
#             "message": str(e),
#         }


# def build_vector_store_from_chunks(
#     session_id: str,
#     chunks: List[Document],
#     reset_before_add: bool = True,
# ) -> Dict:
#     return add_documents_to_vector_store(
#         session_id=session_id,
#         documents=chunks,
#         reset_before_add=reset_before_add,
#     )


# def similarity_search(
#     session_id: str,
#     query: str,
#     top_k: int = 5,
#     collection_name: Optional[str] = None,
# ) -> List[Document]:
#     if not query or not query.strip():
#         return []

#     vector_store = get_vector_store(
#         session_id=session_id,
#         collection_name=collection_name,
#     )

#     results = vector_store.similarity_search(
#         query=query,
#         k=top_k,
#     )

#     del vector_store
#     gc.collect()

#     return results


# def similarity_search_with_score(
#     session_id: str,
#     query: str,
#     top_k: int = 5,
#     collection_name: Optional[str] = None,
# ) -> List[Dict]:
#     if not query or not query.strip():
#         return []

#     vector_store = get_vector_store(
#         session_id=session_id,
#         collection_name=collection_name,
#     )

#     results = vector_store.similarity_search_with_score(
#         query=query,
#         k=top_k,
#     )

#     formatted_results = []

#     for doc, score in results:
#         metadata = doc.metadata or {}

#         formatted_results.append(
#             {
#                 "score": score,
#                 "pdf_name": metadata.get("pdf_name", metadata.get("source", "Unknown PDF")),
#                 "page": metadata.get("page_number", metadata.get("page", "Unknown page")),
#                 "chunk_id": metadata.get("chunk_id", ""),
#                 "content_preview": doc.page_content[:500],
#             }
#         )

#     del vector_store
#     gc.collect()

#     return formatted_results


# def get_retriever(
#     session_id: str,
#     top_k: int = 5,
#     search_type: str = "similarity",
# ):
#     vector_store = get_vector_store(session_id=session_id)

#     if search_type == "mmr":
#         return vector_store.as_retriever(
#             search_type="mmr",
#             search_kwargs={
#                 "k": top_k,
#                 "fetch_k": max(top_k * 4, 20),
#             },
#         )

#     return vector_store.as_retriever(
#         search_type="similarity",
#         search_kwargs={"k": top_k},
#     )


# def get_vector_store_status(session_id: str) -> Dict:
#     try:
#         vector_store = get_vector_store(session_id=session_id)
#         data = vector_store.get()

#         ids = data.get("ids", [])
#         metadatas = data.get("metadatas", [])

#         pdfs = {}

#         for metadata in metadatas:
#             metadata = metadata or {}

#             pdf_name = metadata.get("pdf_name", metadata.get("source", "Unknown PDF"))
#             page = metadata.get("page_number", metadata.get("page", "Unknown page"))

#             if pdf_name not in pdfs:
#                 pdfs[pdf_name] = {
#                     "chunks": 0,
#                     "pages": set(),
#                 }

#             pdfs[pdf_name]["chunks"] += 1
#             pdfs[pdf_name]["pages"].add(str(page))

#         clean_pdfs = {}

#         for pdf_name, info in pdfs.items():
#             clean_pdfs[pdf_name] = {
#                 "chunks": info["chunks"],
#                 "pages": sorted(
#                     list(info["pages"]),
#                     key=lambda x: int(x) if str(x).isdigit() else 999999,
#                 ),
#                 "total_pages_found": len(info["pages"]),
#             }

#         result = {
#             "success": True,
#             "ready": len(ids) > 0,
#             "total_vectors": len(ids),
#             "pdfs": clean_pdfs,
#             "persist_directory": get_chroma_path(session_id),
#             "collection_name": get_collection_name(session_id),
#         }

#         del vector_store
#         gc.collect()

#         return result

#     except Exception as e:
#         return {
#             "success": False,
#             "ready": False,
#             "total_vectors": 0,
#             "pdfs": {},
#             "persist_directory": get_chroma_path(session_id),
#             "collection_name": get_collection_name(session_id),
#             "error": str(e),
#         }


# def is_vector_store_ready(session_id: str) -> bool:
#     status = get_vector_store_status(session_id)
#     return bool(status.get("ready"))


# def index_documents_pipeline(
#     session_id: str,
#     documents: List[Document],
#     chunk_size: Optional[int] = None,
#     chunk_overlap: Optional[int] = None,
#     reset_before_add: bool = True,
# ) -> Dict:
#     try:
#         from src.chunker import chunk_documents
#         from src.config import CHUNK_SIZE, CHUNK_OVERLAP

#         if not documents:
#             return {
#                 "success": False,
#                 "stage": "input",
#                 "message": "No documents received for indexing.",
#                 "total_chunks": 0,
#             }

#         if chunk_size is None:
#             chunk_size = CHUNK_SIZE

#         if chunk_overlap is None:
#             chunk_overlap = CHUNK_OVERLAP

#         chunk_result = chunk_documents(
#             documents=documents,
#             session_id=session_id,
#             chunk_size=chunk_size,
#             chunk_overlap=chunk_overlap,
#         )

#         if not chunk_result.get("success"):
#             return {
#                 "success": False,
#                 "stage": "chunking",
#                 "message": chunk_result.get("error", "Chunking failed."),
#                 "total_chunks": 0,
#             }

#         chunks = chunk_result["chunks"]

#         store_result = build_vector_store_from_chunks(
#             session_id=session_id,
#             chunks=chunks,
#             reset_before_add=reset_before_add,
#         )

#         if not store_result.get("success"):
#             return {
#                 "success": False,
#                 "stage": "vector_store",
#                 "message": store_result.get("message", "Vector store failed."),
#                 "total_chunks": len(chunks),
#             }

#         return {
#             "success": True,
#             "stage": "completed",
#             "message": "Documents indexed successfully.",
#             "total_chunks": len(chunks),
#             "chunk_stats": {
#                 "pdf_chunk_counts": chunk_result.get("pdf_chunk_counts", {}),
#                 "pdf_page_counts": chunk_result.get("pdf_page_counts", {}),
#             },
#             "vector_store": store_result,
#         }

#     except Exception as e:
#         logger.error(f"Index pipeline failed: {str(e)}")

#         return {
#             "success": False,
#             "stage": "error",
#             "message": str(e),
#             "total_chunks": 0,
#         }


# def run_vector_store_self_test(session_id: str) -> Dict:
#     try:
#         test_docs = [
#             Document(
#                 page_content="Machine learning is a branch of artificial intelligence.",
#                 metadata={
#                     "pdf_name": "test_notes.pdf",
#                     "source": "test_notes.pdf",
#                     "page_number": 1,
#                     "page": 1,
#                     "chunk_id": 1,
#                 },
#             ),
#             Document(
#                 page_content="DBMS is used to store, organize, and manage data.",
#                 metadata={
#                     "pdf_name": "test_notes.pdf",
#                     "source": "test_notes.pdf",
#                     "page_number": 2,
#                     "page": 2,
#                     "chunk_id": 2,
#                 },
#             ),
#         ]

#         store_result = build_vector_store_from_chunks(
#             session_id=session_id,
#             chunks=test_docs,
#             reset_before_add=True,
#         )

#         search_result = similarity_search_with_score(
#             session_id=session_id,
#             query="What is DBMS?",
#             top_k=2,
#         )

#         status = get_vector_store_status(session_id)

#         return {
#             "success": store_result.get("success", False),
#             "store_result": store_result,
#             "search_result": search_result,
#             "status": status,
#             "message": "Vector store self-test completed.",
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "message": str(e),
#         }


# if __name__ == "__main__":
#     test_session_id = "test_session"
#     print(run_vector_store_self_test(test_session_id))
























# from pathlib import Path
# from typing import Dict, List, Optional
# import logging
# import hashlib
# import gc

# from langchain_core.documents import Document
# from langchain_chroma import Chroma

# from src.embeddings import get_embedding_model
# from src.session_manager import (
#     get_chroma_path,
#     create_user_folders,
#     update_total_chunks,
# )

# from src.config import (
#     CHROMA_COLLECTION_NAME,
#     CHROMA_SEARCH_TYPE,
#     CHROMA_TOP_K,
# )


# logger = logging.getLogger(__name__)

# DEFAULT_COLLECTION_NAME = CHROMA_COLLECTION_NAME or "rag_interview_notes"


# # ---------------------------------------------------------
# # Collection helpers
# # ---------------------------------------------------------

# def get_collection_name(session_id: str) -> str:
#     clean_session = str(session_id).replace("-", "_")
#     clean_session = clean_session.replace(" ", "_")

#     return f"{DEFAULT_COLLECTION_NAME}_{clean_session[:12]}"


# def clean_metadata_value(value):
#     if value is None:
#         return ""

#     if isinstance(value, (str, int, float, bool)):
#         return value

#     return str(value)


# def clean_document_metadata(document: Document) -> Document:
#     metadata = document.metadata or {}
#     clean_metadata = {}

#     for key, value in metadata.items():
#         clean_metadata[str(key)] = clean_metadata_value(value)

#     return Document(
#         page_content=document.page_content,
#         metadata=clean_metadata,
#     )


# def clean_documents_for_chroma(documents: List[Document]) -> List[Document]:
#     cleaned_docs = []

#     if not documents:
#         return cleaned_docs

#     for doc in documents:
#         if not doc:
#             continue

#         if not doc.page_content or not doc.page_content.strip():
#             continue

#         cleaned_docs.append(clean_document_metadata(doc))

#     return cleaned_docs


# # ---------------------------------------------------------
# # Stable document IDs
# # ---------------------------------------------------------

# def create_stable_document_id(document: Document, fallback_index: int) -> str:
#     metadata = document.metadata or {}

#     pdf_name = metadata.get("pdf_name", metadata.get("source", "pdf"))
#     page = metadata.get("page_number", metadata.get("page", "page"))
#     chunk_id = metadata.get("chunk_id", fallback_index)

#     text_hash = hashlib.md5(
#         document.page_content.encode("utf-8", errors="ignore")
#     ).hexdigest()[:12]

#     raw_id = f"{pdf_name}_{page}_{chunk_id}_{text_hash}"

#     safe_id = (
#         raw_id.replace(" ", "_")
#         .replace("/", "_")
#         .replace("\\", "_")
#         .replace(":", "_")
#         .replace("|", "_")
#         .replace(".", "_")
#         .replace("(", "_")
#         .replace(")", "_")
#         .replace("[", "_")
#         .replace("]", "_")
#     )

#     return safe_id


# def create_document_ids(documents: List[Document]) -> List[str]:
#     ids = []

#     for index, doc in enumerate(documents, start=1):
#         ids.append(create_stable_document_id(doc, index))

#     return ids


# # ---------------------------------------------------------
# # Vector store creation
# # ---------------------------------------------------------

# def get_vector_store(
#     session_id: str,
#     collection_name: Optional[str] = None,
# ) -> Chroma:
#     create_user_folders(session_id)

#     chroma_path = get_chroma_path(session_id)

#     if collection_name is None:
#         collection_name = get_collection_name(session_id)

#     embedding_model = get_embedding_model()

#     vector_store = Chroma(
#         collection_name=collection_name,
#         persist_directory=chroma_path,
#         embedding_function=embedding_model,
#     )

#     return vector_store


# def get_vector_store_path(session_id: str) -> str:
#     return get_chroma_path(session_id)


# # ---------------------------------------------------------
# # Reset / delete helpers
# # ---------------------------------------------------------

# def delete_existing_collection_items(session_id: str) -> bool:
#     try:
#         vector_store = get_vector_store(session_id=session_id)
#         collection = vector_store._collection

#         existing = collection.get()
#         ids = existing.get("ids", [])

#         if ids:
#             collection.delete(ids=ids)

#         update_total_chunks(session_id, 0)

#         del vector_store
#         gc.collect()

#         return True

#     except Exception as e:
#         logger.error(f"Failed to delete existing collection items: {str(e)}")
#         return False


# def reset_vector_store(session_id: str) -> bool:
#     return delete_existing_collection_items(session_id=session_id)


# def delete_collection(session_id: str) -> bool:
#     return delete_existing_collection_items(session_id=session_id)


# # ---------------------------------------------------------
# # Add documents
# # ---------------------------------------------------------

# def add_documents_to_vector_store(
#     session_id: str,
#     documents: List[Document],
#     collection_name: Optional[str] = None,
#     reset_before_add: bool = True,
# ) -> Dict:
#     if not documents:
#         return {
#             "success": False,
#             "total_added": 0,
#             "message": "No documents provided for vector storage.",
#         }

#     try:
#         cleaned_docs = clean_documents_for_chroma(documents)

#         if not cleaned_docs:
#             return {
#                 "success": False,
#                 "total_added": 0,
#                 "message": "No valid documents after cleaning.",
#             }

#         if collection_name is None:
#             collection_name = get_collection_name(session_id)

#         if reset_before_add:
#             delete_existing_collection_items(session_id=session_id)

#         vector_store = get_vector_store(
#             session_id=session_id,
#             collection_name=collection_name,
#         )

#         ids = create_document_ids(cleaned_docs)

#         unique_docs = []
#         unique_ids = []
#         seen_ids = set()

#         for doc, doc_id in zip(cleaned_docs, ids):
#             if doc_id in seen_ids:
#                 continue

#             seen_ids.add(doc_id)
#             unique_docs.append(doc)
#             unique_ids.append(doc_id)

#         if not unique_docs:
#             return {
#                 "success": False,
#                 "total_added": 0,
#                 "message": "No unique documents to add.",
#             }

#         vector_store.add_documents(
#             documents=unique_docs,
#             ids=unique_ids,
#         )

#         update_total_chunks(session_id, len(unique_docs))

#         result = {
#             "success": True,
#             "total_added": len(unique_docs),
#             "persist_directory": get_chroma_path(session_id),
#             "collection_name": collection_name,
#             "message": "Documents stored in ChromaDB successfully.",
#         }

#         del vector_store
#         gc.collect()

#         return result

#     except Exception as e:
#         logger.error(f"Failed to add documents to vector store: {str(e)}")

#         return {
#             "success": False,
#             "total_added": 0,
#             "message": str(e),
#         }


# def build_vector_store_from_chunks(
#     session_id: str,
#     chunks: List[Document],
#     reset_before_add: bool = True,
# ) -> Dict:
#     return add_documents_to_vector_store(
#         session_id=session_id,
#         documents=chunks,
#         reset_before_add=reset_before_add,
#     )


# # ---------------------------------------------------------
# # Search helpers
# # ---------------------------------------------------------

# def similarity_search(
#     session_id: str,
#     query: str,
#     top_k: int = CHROMA_TOP_K,
#     collection_name: Optional[str] = None,
# ) -> List[Document]:
#     if not query or not query.strip():
#         return []

#     safe_top_k = int(top_k or CHROMA_TOP_K)

#     if safe_top_k <= 0:
#         safe_top_k = CHROMA_TOP_K

#     vector_store = get_vector_store(
#         session_id=session_id,
#         collection_name=collection_name,
#     )

#     results = vector_store.similarity_search(
#         query=query,
#         k=safe_top_k,
#     )

#     del vector_store
#     gc.collect()

#     return results


# def similarity_search_with_score(
#     session_id: str,
#     query: str,
#     top_k: int = CHROMA_TOP_K,
#     collection_name: Optional[str] = None,
# ) -> List[Dict]:
#     if not query or not query.strip():
#         return []

#     safe_top_k = int(top_k or CHROMA_TOP_K)

#     if safe_top_k <= 0:
#         safe_top_k = CHROMA_TOP_K

#     vector_store = get_vector_store(
#         session_id=session_id,
#         collection_name=collection_name,
#     )

#     results = vector_store.similarity_search_with_score(
#         query=query,
#         k=safe_top_k,
#     )

#     formatted_results = []

#     for doc, score in results:
#         metadata = doc.metadata or {}

#         formatted_results.append(
#             {
#                 "score": float(score) if score is not None else None,
#                 "pdf_name": metadata.get(
#                     "pdf_name",
#                     metadata.get("source", "Unknown PDF"),
#                 ),
#                 "page": metadata.get(
#                     "page_number",
#                     metadata.get("page", "Unknown page"),
#                 ),
#                 "chunk_id": metadata.get("chunk_id", ""),
#                 "content_preview": doc.page_content[:500],
#                 "content": doc.page_content,
#                 "metadata": metadata,
#             }
#         )

#     del vector_store
#     gc.collect()

#     return formatted_results


# def get_retriever(
#     session_id: str,
#     top_k: int = CHROMA_TOP_K,
#     search_type: str = CHROMA_SEARCH_TYPE,
# ):
#     vector_store = get_vector_store(session_id=session_id)

#     safe_top_k = int(top_k or CHROMA_TOP_K)

#     if safe_top_k <= 0:
#         safe_top_k = CHROMA_TOP_K

#     safe_search_type = search_type or "similarity"

#     if safe_search_type == "mmr":
#         return vector_store.as_retriever(
#             search_type="mmr",
#             search_kwargs={
#                 "k": safe_top_k,
#                 "fetch_k": max(safe_top_k * 4, 20),
#             },
#         )

#     return vector_store.as_retriever(
#         search_type="similarity",
#         search_kwargs={"k": safe_top_k},
#     )


# # ---------------------------------------------------------
# # Status helpers
# # ---------------------------------------------------------

# def get_vector_store_status(session_id: str) -> Dict:
#     try:
#         vector_store = get_vector_store(session_id=session_id)
#         data = vector_store.get()

#         ids = data.get("ids", [])
#         metadatas = data.get("metadatas", [])

#         pdfs = {}

#         for metadata in metadatas:
#             metadata = metadata or {}

#             pdf_name = metadata.get(
#                 "pdf_name",
#                 metadata.get("source", "Unknown PDF"),
#             )

#             page = metadata.get(
#                 "page_number",
#                 metadata.get("page", "Unknown page"),
#             )

#             if pdf_name not in pdfs:
#                 pdfs[pdf_name] = {
#                     "chunks": 0,
#                     "pages": set(),
#                 }

#             pdfs[pdf_name]["chunks"] += 1
#             pdfs[pdf_name]["pages"].add(str(page))

#         clean_pdfs = {}

#         for pdf_name, info in pdfs.items():
#             clean_pdfs[pdf_name] = {
#                 "chunks": info["chunks"],
#                 "pages": sorted(
#                     list(info["pages"]),
#                     key=lambda x: int(x) if str(x).isdigit() else 999999,
#                 ),
#                 "total_pages_found": len(info["pages"]),
#             }

#         result = {
#             "success": True,
#             "ready": len(ids) > 0,
#             "total_vectors": len(ids),
#             "pdfs": clean_pdfs,
#             "persist_directory": get_chroma_path(session_id),
#             "collection_name": get_collection_name(session_id),
#         }

#         del vector_store
#         gc.collect()

#         return result

#     except Exception as e:
#         return {
#             "success": False,
#             "ready": False,
#             "total_vectors": 0,
#             "pdfs": {},
#             "persist_directory": get_chroma_path(session_id),
#             "collection_name": get_collection_name(session_id),
#             "error": str(e),
#         }


# def is_vector_store_ready(session_id: str) -> bool:
#     status = get_vector_store_status(session_id)
#     return bool(status.get("ready"))


# # ---------------------------------------------------------
# # Full indexing pipeline
# # ---------------------------------------------------------

# def index_documents_pipeline(
#     session_id: str,
#     documents: List[Document],
#     chunk_size: Optional[int] = None,
#     chunk_overlap: Optional[int] = None,
#     reset_before_add: bool = True,
# ) -> Dict:
#     try:
#         from src.chunker import chunk_documents
#         from src.config import CHUNK_SIZE, CHUNK_OVERLAP

#         if not documents:
#             return {
#                 "success": False,
#                 "stage": "input",
#                 "message": "No documents received for indexing.",
#                 "total_chunks": 0,
#             }

#         if chunk_size is None:
#             chunk_size = CHUNK_SIZE

#         if chunk_overlap is None:
#             chunk_overlap = CHUNK_OVERLAP

#         chunk_result = chunk_documents(
#             documents=documents,
#             session_id=session_id,
#             chunk_size=chunk_size,
#             chunk_overlap=chunk_overlap,
#         )

#         if not chunk_result.get("success"):
#             return {
#                 "success": False,
#                 "stage": "chunking",
#                 "message": chunk_result.get("error", "Chunking failed."),
#                 "total_chunks": 0,
#             }

#         chunks = chunk_result["chunks"]

#         store_result = build_vector_store_from_chunks(
#             session_id=session_id,
#             chunks=chunks,
#             reset_before_add=reset_before_add,
#         )

#         if not store_result.get("success"):
#             return {
#                 "success": False,
#                 "stage": "vector_store",
#                 "message": store_result.get("message", "Vector store failed."),
#                 "total_chunks": len(chunks),
#             }

#         return {
#             "success": True,
#             "stage": "completed",
#             "message": "Documents indexed successfully.",
#             "total_chunks": len(chunks),
#             "chunk_stats": {
#                 "pdf_chunk_counts": chunk_result.get("pdf_chunk_counts", {}),
#                 "pdf_page_counts": chunk_result.get("pdf_page_counts", {}),
#             },
#             "vector_store": store_result,
#         }

#     except Exception as e:
#         logger.error(f"Index pipeline failed: {str(e)}")

#         return {
#             "success": False,
#             "stage": "error",
#             "message": str(e),
#             "total_chunks": 0,
#         }


# # ---------------------------------------------------------
# # API helper
# # ---------------------------------------------------------

# def get_vector_store_api_summary(session_id: str) -> Dict:
#     status = get_vector_store_status(session_id)

#     return {
#         "session_id": session_id,
#         "ready": status.get("ready", False),
#         "total_vectors": status.get("total_vectors", 0),
#         "pdfs": status.get("pdfs", {}),
#         "persist_directory": status.get("persist_directory"),
#         "collection_name": status.get("collection_name"),
#     }


# # ---------------------------------------------------------
# # Self test
# # ---------------------------------------------------------

# def run_vector_store_self_test(session_id: str) -> Dict:
#     try:
#         test_docs = [
#             Document(
#                 page_content="Machine learning is a branch of artificial intelligence.",
#                 metadata={
#                     "pdf_name": "test_notes.pdf",
#                     "source": "test_notes.pdf",
#                     "page_number": 1,
#                     "page": 1,
#                     "chunk_id": 1,
#                 },
#             ),
#             Document(
#                 page_content="DBMS is used to store, organize, and manage data.",
#                 metadata={
#                     "pdf_name": "test_notes.pdf",
#                     "source": "test_notes.pdf",
#                     "page_number": 2,
#                     "page": 2,
#                     "chunk_id": 2,
#                 },
#             ),
#         ]

#         store_result = build_vector_store_from_chunks(
#             session_id=session_id,
#             chunks=test_docs,
#             reset_before_add=True,
#         )

#         search_result = similarity_search_with_score(
#             session_id=session_id,
#             query="What is DBMS?",
#             top_k=2,
#         )

#         status = get_vector_store_status(session_id)

#         return {
#             "success": store_result.get("success", False),
#             "store_result": store_result,
#             "search_result": search_result,
#             "status": status,
#             "message": "Vector store self-test completed.",
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "message": str(e),
#         }


# if __name__ == "__main__":
#     test_session_id = "test_session"
#     print(run_vector_store_self_test(test_session_id))



















from pathlib import Path
from typing import Dict, List, Optional
import logging
import hashlib
import gc
import shutil

from langchain_core.documents import Document
from langchain_chroma import Chroma

from src.embeddings import get_embedding_model
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

# Better defaults for deep RAG
DEFAULT_VECTOR_TOP_K = max(int(CHROMA_TOP_K or 10), 10)
DEFAULT_VECTOR_FETCH_K = 40


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

        # Keep stripped content only
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
# Vector store creation
# ---------------------------------------------------------

def get_vector_store(
    session_id: str,
    collection_name: Optional[str] = None,
) -> Chroma:
    create_user_folders(session_id)

    chroma_path = get_chroma_path(session_id)

    if collection_name is None:
        collection_name = get_collection_name(session_id)

    embedding_model = get_embedding_model()

    vector_store = Chroma(
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
    Delete all items inside the current Chroma collection.

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
    Hard delete Chroma directory for the session.

    Use this if old chunks/vectors are still being picked after config changes.
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

        # Important:
        # Delete old vectors before adding new chunked documents.
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

            # Avoid exact duplicate content chunks
            if content_hash in seen_content_hashes:
                continue

            seen_ids.add(doc_id)
            seen_content_hashes.add(content_hash)

            metadata = dict(doc.metadata or {})
            metadata["vector_id"] = doc_id
            metadata["content_hash"] = content_hash[:14]

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

        # Chroma can handle batch insert, but very large inserts may be memory heavy.
        batch_size = 500
        total_added = 0

        for start in range(0, len(unique_docs), batch_size):
            end = start + batch_size

            vector_store.add_documents(
                documents=unique_docs[start:end],
                ids=unique_ids[start:end],
            )

            total_added += len(unique_docs[start:end])

        update_total_chunks(session_id, total_added)

        result = {
            "success": True,
            "total_added": total_added,
            "persist_directory": get_chroma_path(session_id),
            "collection_name": collection_name,
            "message": "Documents stored in ChromaDB successfully.",
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

    safe_top_k = max(safe_top_k, DEFAULT_VECTOR_TOP_K)

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

    safe_top_k = max(safe_top_k, DEFAULT_VECTOR_TOP_K)

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
    MMR search gives more diverse chunks.
    Better for detailed answers where one query needs multiple related pages/chunks.
    """

    if not query or not query.strip():
        return []

    safe_top_k = max(int(top_k or DEFAULT_VECTOR_TOP_K), DEFAULT_VECTOR_TOP_K)
    safe_fetch_k = max(int(fetch_k or DEFAULT_VECTOR_FETCH_K), safe_top_k * 4)

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

    safe_top_k = max(safe_top_k, DEFAULT_VECTOR_TOP_K)

    safe_search_type = search_type or "mmr"

    if safe_search_type == "mmr":
        return vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": safe_top_k,
                "fetch_k": max(safe_top_k * 4, DEFAULT_VECTOR_FETCH_K),
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
    Helper to test if a specific topic is actually indexed and retrievable.
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
            "message": "Vector store self-test completed.",
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
        }


if __name__ == "__main__":
    test_session_id = "test_session"
    print(run_vector_store_self_test(test_session_id))