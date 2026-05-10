# from typing import Dict, List, Optional
# import logging

# from langchain_core.documents import Document
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# from src.config import (
#     CHUNK_SIZE,
#     CHUNK_OVERLAP,
#     MIN_CHUNK_CHARS,
# )
# from src.session_manager import (
#     mark_pdf_processed,
#     update_total_chunks,
# )


# logger = logging.getLogger(__name__)


# # ---------------------------------------------------------
# # Text cleaning
# # ---------------------------------------------------------

# def clean_chunk_text(text: str) -> str:
#     """
#     Clean text before chunking.
#     """

#     if not text:
#         return ""

#     text = str(text)

#     text = text.replace("\x00", " ")
#     text = text.replace("\t", " ")
#     text = text.replace("\r", "\n")

#     lines = text.splitlines()
#     cleaned_lines = []

#     for line in lines:
#         line = line.strip()

#         if not line:
#             continue

#         cleaned_lines.append(line)

#     return "\n".join(cleaned_lines).strip()


# def is_valid_chunk_text(text: str, min_chars: int = MIN_CHUNK_CHARS) -> bool:
#     """
#     Check whether chunk text is useful.
#     """

#     if not text:
#         return False

#     text = text.strip()

#     if len(text) < min_chars:
#         return False

#     alnum_count = sum(ch.isalnum() for ch in text)

#     if alnum_count < min_chars // 2:
#         return False

#     return True


# # ---------------------------------------------------------
# # Splitter
# # ---------------------------------------------------------

# def get_text_splitter(
#     chunk_size: int = CHUNK_SIZE,
#     chunk_overlap: int = CHUNK_OVERLAP,
# ) -> RecursiveCharacterTextSplitter:
#     """
#     Create LangChain text splitter.

#     Separators are ordered from bigger structure to smaller structure.
#     This helps preserve headings, points, formulas, and paragraphs.
#     """

#     return RecursiveCharacterTextSplitter(
#         chunk_size=chunk_size,
#         chunk_overlap=chunk_overlap,
#         length_function=len,
#         separators=[
#             "\n\n",
#             "\n",
#             ". ",
#             "? ",
#             "! ",
#             "; ",
#             ", ",
#             " ",
#             "",
#         ],
#     )


# # ---------------------------------------------------------
# # Chunk single document
# # ---------------------------------------------------------

# def chunk_single_document(
#     document: Document,
#     chunk_size: int = CHUNK_SIZE,
#     chunk_overlap: int = CHUNK_OVERLAP,
#     start_chunk_id: int = 1,
# ) -> List[Document]:
#     """
#     Split one LangChain Document into smaller chunks.

#     Input document usually represents one PDF page.
#     Output documents represent smaller RAG chunks.
#     """

#     if document is None:
#         return []

#     page_content = clean_chunk_text(document.page_content)

#     if not is_valid_chunk_text(page_content, min_chars=10):
#         return []

#     metadata = document.metadata or {}

#     splitter = get_text_splitter(
#         chunk_size=chunk_size,
#         chunk_overlap=chunk_overlap,
#     )

#     text_chunks = splitter.split_text(page_content)

#     chunked_documents = []

#     for index, chunk_text in enumerate(text_chunks, start=start_chunk_id):
#         chunk_text = clean_chunk_text(chunk_text)

#         if not is_valid_chunk_text(chunk_text):
#             continue

#         new_metadata = dict(metadata)

#         pdf_name = (
#             new_metadata.get("pdf_name")
#             or new_metadata.get("source")
#             or new_metadata.get("file_name")
#             or "Unknown PDF"
#         )

#         page_number = (
#             new_metadata.get("page_number")
#             or new_metadata.get("page")
#             or "Unknown page"
#         )

#         new_metadata.update(
#             {
#                 "pdf_name": pdf_name,
#                 "source": pdf_name,
#                 "page_number": page_number,
#                 "page": page_number,
#                 "chunk_id": index,
#                 "chunk_size": len(chunk_text),
#                 "content_type": "pdf_chunk",
#             }
#         )

#         chunked_documents.append(
#             Document(
#                 page_content=chunk_text,
#                 metadata=new_metadata,
#             )
#         )

#     return chunked_documents


# # ---------------------------------------------------------
# # Chunk multiple documents
# # ---------------------------------------------------------

# def chunk_documents(
#     documents: List[Document],
#     session_id: Optional[str] = None,
#     chunk_size: int = CHUNK_SIZE,
#     chunk_overlap: int = CHUNK_OVERLAP,
# ) -> Dict:
#     """
#     Chunk multiple LangChain Documents.

#     Usually called after:
#         process_uploaded_pdfs_for_session(session_id)

#     Returns:
#         {
#             "success": True,
#             "chunks": [Document, Document],
#             "total_chunks": 100,
#             "pdf_chunk_counts": {...}
#         }
#     """

#     if not documents:
#         return {
#             "success": False,
#             "chunks": [],
#             "total_chunks": 0,
#             "pdf_chunk_counts": {},
#             "error": "No documents provided for chunking.",
#         }

#     all_chunks = []
#     pdf_chunk_counts = {}
#     pdf_page_counts = {}

#     global_chunk_id = 1

#     for document in documents:
#         metadata = document.metadata or {}

#         pdf_name = (
#             metadata.get("pdf_name")
#             or metadata.get("source")
#             or metadata.get("file_name")
#             or "Unknown PDF"
#         )

#         page_number = (
#             metadata.get("page_number")
#             or metadata.get("page")
#             or "Unknown page"
#         )

#         chunks = chunk_single_document(
#             document=document,
#             chunk_size=chunk_size,
#             chunk_overlap=chunk_overlap,
#             start_chunk_id=global_chunk_id,
#         )

#         if not chunks:
#             continue

#         all_chunks.extend(chunks)

#         global_chunk_id += len(chunks)

#         pdf_chunk_counts[pdf_name] = pdf_chunk_counts.get(pdf_name, 0) + len(chunks)

#         try:
#             page_as_int = int(page_number)
#             pdf_page_counts[pdf_name] = max(
#                 pdf_page_counts.get(pdf_name, 0),
#                 page_as_int,
#             )
#         except Exception:
#             pdf_page_counts[pdf_name] = pdf_page_counts.get(pdf_name, 0)

#     if session_id:
#         update_total_chunks(session_id, len(all_chunks))

#         for pdf_name, chunk_count in pdf_chunk_counts.items():
#             pages = pdf_page_counts.get(pdf_name, 0)

#             mark_pdf_processed(
#                 session_id=session_id,
#                 pdf_name=pdf_name,
#                 pages=pages,
#                 chunks=chunk_count,
#             )

#     return {
#         "success": len(all_chunks) > 0,
#         "chunks": all_chunks,
#         "total_chunks": len(all_chunks),
#         "pdf_chunk_counts": pdf_chunk_counts,
#         "pdf_page_counts": pdf_page_counts,
#         "error": None if all_chunks else "No valid chunks created.",
#     }


# # ---------------------------------------------------------
# # Chunk by text directly
# # ---------------------------------------------------------

# def chunk_text(
#     text: str,
#     metadata: Optional[Dict] = None,
#     chunk_size: int = CHUNK_SIZE,
#     chunk_overlap: int = CHUNK_OVERLAP,
# ) -> List[Document]:
#     """
#     Chunk raw text directly.

#     Useful for testing or API usage.
#     """

#     if metadata is None:
#         metadata = {}

#     document = Document(
#         page_content=text,
#         metadata=metadata,
#     )

#     return chunk_single_document(
#         document=document,
#         chunk_size=chunk_size,
#         chunk_overlap=chunk_overlap,
#         start_chunk_id=1,
#     )


# # ---------------------------------------------------------
# # Preview helpers
# # ---------------------------------------------------------

# def preview_chunks(
#     chunks: List[Document],
#     max_chunks: int = 5,
#     max_chars: int = 400,
# ) -> List[Dict]:
#     """
#     Return chunk preview for Streamlit/API.
#     """

#     previews = []

#     for index, chunk in enumerate(chunks[:max_chunks], start=1):
#         metadata = chunk.metadata or {}

#         previews.append(
#             {
#                 "index": index,
#                 "pdf_name": metadata.get("pdf_name", metadata.get("source", "Unknown PDF")),
#                 "page": metadata.get("page_number", metadata.get("page", "Unknown page")),
#                 "chunk_id": metadata.get("chunk_id", index),
#                 "text_preview": chunk.page_content[:max_chars],
#                 "chunk_size": len(chunk.page_content),
#             }
#         )

#     return previews


# def get_chunk_stats(chunks: List[Document]) -> Dict:
#     """
#     Return stats about chunks.
#     """

#     if not chunks:
#         return {
#             "total_chunks": 0,
#             "average_chunk_size": 0,
#             "min_chunk_size": 0,
#             "max_chunk_size": 0,
#             "pdfs": {},
#         }

#     chunk_sizes = [len(chunk.page_content) for chunk in chunks]

#     pdfs = {}

#     for chunk in chunks:
#         metadata = chunk.metadata or {}

#         pdf_name = metadata.get("pdf_name", metadata.get("source", "Unknown PDF"))
#         page_number = metadata.get("page_number", metadata.get("page", "Unknown page"))

#         if pdf_name not in pdfs:
#             pdfs[pdf_name] = {
#                 "chunks": 0,
#                 "pages": set(),
#             }

#         pdfs[pdf_name]["chunks"] += 1
#         pdfs[pdf_name]["pages"].add(str(page_number))

#     clean_pdfs = {}

#     for pdf_name, data in pdfs.items():
#         clean_pdfs[pdf_name] = {
#             "chunks": data["chunks"],
#             "pages": sorted(list(data["pages"])),
#             "total_pages_found": len(data["pages"]),
#         }

#     return {
#         "total_chunks": len(chunks),
#         "average_chunk_size": round(sum(chunk_sizes) / len(chunk_sizes), 2),
#         "min_chunk_size": min(chunk_sizes),
#         "max_chunk_size": max(chunk_sizes),
#         "pdfs": clean_pdfs,
#     }


# # ---------------------------------------------------------
# # Search within chunks
# # ---------------------------------------------------------

# def search_chunks_by_keyword(
#     chunks: List[Document],
#     keyword: str,
#     max_results: int = 10,
# ) -> List[Dict]:
#     """
#     Simple keyword search inside created chunks.

#     This is only for debugging/testing.
#     Real search happens through ChromaDB retriever.
#     """

#     if not chunks or not keyword:
#         return []

#     keyword_lower = keyword.lower()
#     results = []

#     for chunk in chunks:
#         text = chunk.page_content

#         if keyword_lower in text.lower():
#             metadata = chunk.metadata or {}

#             results.append(
#                 {
#                     "pdf_name": metadata.get("pdf_name", metadata.get("source", "Unknown PDF")),
#                     "page": metadata.get("page_number", metadata.get("page", "Unknown page")),
#                     "chunk_id": metadata.get("chunk_id"),
#                     "text_preview": text[:500],
#                 }
#             )

#         if len(results) >= max_results:
#             break

#     return results


# # ---------------------------------------------------------
# # Self test
# # ---------------------------------------------------------

# def run_chunker_self_test() -> Dict:
#     """
#     Self-test for chunker.py.
#     """

#     try:
#         sample_text = """
#         Machine learning is a branch of artificial intelligence.
#         It allows systems to learn from data without being explicitly programmed.

#         Supervised learning uses labelled data.
#         Unsupervised learning finds hidden patterns in unlabelled data.
#         Reinforcement learning uses rewards and penalties.

#         In interviews, machine learning questions usually focus on algorithms,
#         datasets, training, testing, overfitting, and evaluation metrics.
#         """

#         sample_doc = Document(
#             page_content=sample_text,
#             metadata={
#                 "pdf_name": "sample_notes.pdf",
#                 "source": "sample_notes.pdf",
#                 "page_number": 1,
#                 "page": 1,
#             },
#         )

#         result = chunk_documents(
#             documents=[sample_doc],
#             session_id=None,
#             chunk_size=200,
#             chunk_overlap=40,
#         )

#         return {
#             "success": result["success"],
#             "total_chunks": result["total_chunks"],
#             "stats": get_chunk_stats(result["chunks"]),
#             "preview": preview_chunks(result["chunks"]),
#             "message": "Chunker self-test completed.",
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "message": str(e),
#         }


# if __name__ == "__main__":
#     print(run_chunker_self_test())





















































# from typing import Dict, List, Optional
# import logging

# from langchain_core.documents import Document
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# from src.config import (
#     CHUNK_SIZE,
#     CHUNK_OVERLAP,
#     MIN_CHUNK_CHARS,
# )

# from src.session_manager import (
#     mark_pdf_processed,
#     update_total_chunks,
# )


# logger = logging.getLogger(__name__)


# # ---------------------------------------------------------
# # Text cleaning
# # ---------------------------------------------------------

# def clean_chunk_text(text: str) -> str:
#     """
#     Clean text before chunking.
#     """

#     if not text:
#         return ""

#     text = str(text)

#     text = text.replace("\x00", " ")
#     text = text.replace("\t", " ")
#     text = text.replace("\r", "\n")

#     lines = text.splitlines()
#     cleaned_lines = []

#     for line in lines:
#         line = line.strip()

#         if not line:
#             continue

#         cleaned_lines.append(line)

#     return "\n".join(cleaned_lines).strip()


# def is_valid_chunk_text(text: str, min_chars: int = MIN_CHUNK_CHARS) -> bool:
#     """
#     Check whether chunk text is useful.
#     """

#     if not text:
#         return False

#     text = str(text).strip()

#     if len(text) < min_chars:
#         return False

#     alnum_count = sum(ch.isalnum() for ch in text)

#     if alnum_count < max(1, min_chars // 2):
#         return False

#     return True


# # ---------------------------------------------------------
# # Splitter
# # ---------------------------------------------------------

# def get_text_splitter(
#     chunk_size: int = CHUNK_SIZE,
#     chunk_overlap: int = CHUNK_OVERLAP,
# ) -> RecursiveCharacterTextSplitter:
#     """
#     Create LangChain text splitter.

#     Separators are ordered from bigger structure to smaller structure.
#     This helps preserve headings, points, formulas, and paragraphs.
#     """

#     safe_chunk_size = int(chunk_size or CHUNK_SIZE)
#     safe_chunk_overlap = int(chunk_overlap or CHUNK_OVERLAP)

#     if safe_chunk_size <= 0:
#         safe_chunk_size = CHUNK_SIZE

#     if safe_chunk_overlap < 0:
#         safe_chunk_overlap = 0

#     if safe_chunk_overlap >= safe_chunk_size:
#         safe_chunk_overlap = max(0, safe_chunk_size // 5)

#     return RecursiveCharacterTextSplitter(
#         chunk_size=safe_chunk_size,
#         chunk_overlap=safe_chunk_overlap,
#         length_function=len,
#         separators=[
#             "\n\n",
#             "\n",
#             ". ",
#             "? ",
#             "! ",
#             "; ",
#             ", ",
#             " ",
#             "",
#         ],
#     )


# # ---------------------------------------------------------
# # Chunk single document
# # ---------------------------------------------------------

# def chunk_single_document(
#     document: Document,
#     chunk_size: int = CHUNK_SIZE,
#     chunk_overlap: int = CHUNK_OVERLAP,
#     start_chunk_id: int = 1,
# ) -> List[Document]:
#     """
#     Split one LangChain Document into smaller chunks.

#     Input document usually represents one PDF page.
#     Output documents represent smaller RAG chunks.
#     """

#     if document is None:
#         return []

#     page_content = clean_chunk_text(document.page_content)

#     if not is_valid_chunk_text(page_content, min_chars=10):
#         return []

#     metadata = document.metadata or {}

#     splitter = get_text_splitter(
#         chunk_size=chunk_size,
#         chunk_overlap=chunk_overlap,
#     )

#     text_chunks = splitter.split_text(page_content)

#     chunked_documents = []

#     current_chunk_id = int(start_chunk_id or 1)

#     for chunk_text in text_chunks:
#         chunk_text = clean_chunk_text(chunk_text)

#         if not is_valid_chunk_text(chunk_text):
#             continue

#         new_metadata = dict(metadata)

#         pdf_name = (
#             new_metadata.get("pdf_name")
#             or new_metadata.get("source")
#             or new_metadata.get("file_name")
#             or "Unknown PDF"
#         )

#         page_number = (
#             new_metadata.get("page_number")
#             or new_metadata.get("page")
#             or "Unknown page"
#         )

#         new_metadata.update(
#             {
#                 "pdf_name": pdf_name,
#                 "source": pdf_name,
#                 "page_number": page_number,
#                 "page": page_number,
#                 "chunk_id": current_chunk_id,
#                 "chunk_size": len(chunk_text),
#                 "content_type": "pdf_chunk",
#             }
#         )

#         chunked_documents.append(
#             Document(
#                 page_content=chunk_text,
#                 metadata=new_metadata,
#             )
#         )

#         current_chunk_id += 1

#     return chunked_documents


# # ---------------------------------------------------------
# # Chunk multiple documents
# # ---------------------------------------------------------

# def chunk_documents(
#     documents: List[Document],
#     session_id: Optional[str] = None,
#     chunk_size: int = CHUNK_SIZE,
#     chunk_overlap: int = CHUNK_OVERLAP,
# ) -> Dict:
#     """
#     Chunk multiple LangChain Documents.

#     Usually called after:
#         process_uploaded_pdfs_for_session(session_id)

#     Returns:
#         {
#             "success": True,
#             "chunks": [Document, Document],
#             "total_chunks": 100,
#             "pdf_chunk_counts": {...}
#         }
#     """

#     if not documents:
#         return {
#             "success": False,
#             "chunks": [],
#             "total_chunks": 0,
#             "pdf_chunk_counts": {},
#             "pdf_page_counts": {},
#             "error": "No documents provided for chunking.",
#         }

#     all_chunks = []
#     pdf_chunk_counts = {}
#     pdf_page_counts = {}

#     global_chunk_id = 1

#     for document in documents:
#         if document is None:
#             continue

#         metadata = document.metadata or {}

#         pdf_name = (
#             metadata.get("pdf_name")
#             or metadata.get("source")
#             or metadata.get("file_name")
#             or "Unknown PDF"
#         )

#         page_number = (
#             metadata.get("page_number")
#             or metadata.get("page")
#             or "Unknown page"
#         )

#         chunks = chunk_single_document(
#             document=document,
#             chunk_size=chunk_size,
#             chunk_overlap=chunk_overlap,
#             start_chunk_id=global_chunk_id,
#         )

#         if not chunks:
#             continue

#         all_chunks.extend(chunks)

#         global_chunk_id += len(chunks)

#         pdf_chunk_counts[pdf_name] = pdf_chunk_counts.get(pdf_name, 0) + len(chunks)

#         try:
#             page_as_int = int(page_number)
#             pdf_page_counts[pdf_name] = max(
#                 pdf_page_counts.get(pdf_name, 0),
#                 page_as_int,
#             )
#         except Exception:
#             pdf_page_counts[pdf_name] = pdf_page_counts.get(pdf_name, 0)

#     if session_id:
#         update_total_chunks(session_id, len(all_chunks))

#         for pdf_name, chunk_count in pdf_chunk_counts.items():
#             pages = pdf_page_counts.get(pdf_name, 0)

#             mark_pdf_processed(
#                 session_id=session_id,
#                 pdf_name=pdf_name,
#                 pages=pages,
#                 chunks=chunk_count,
#             )

#     return {
#         "success": len(all_chunks) > 0,
#         "chunks": all_chunks,
#         "total_chunks": len(all_chunks),
#         "pdf_chunk_counts": pdf_chunk_counts,
#         "pdf_page_counts": pdf_page_counts,
#         "error": None if all_chunks else "No valid chunks created.",
#     }


# # ---------------------------------------------------------
# # Chunk by raw text directly
# # ---------------------------------------------------------

# def chunk_text(
#     text: str,
#     metadata: Optional[Dict] = None,
#     chunk_size: int = CHUNK_SIZE,
#     chunk_overlap: int = CHUNK_OVERLAP,
# ) -> List[Document]:
#     """
#     Chunk raw text directly.

#     Useful for testing or API usage.
#     """

#     if metadata is None:
#         metadata = {}

#     document = Document(
#         page_content=text or "",
#         metadata=metadata,
#     )

#     return chunk_single_document(
#         document=document,
#         chunk_size=chunk_size,
#         chunk_overlap=chunk_overlap,
#         start_chunk_id=1,
#     )


# # ---------------------------------------------------------
# # Preview helpers
# # ---------------------------------------------------------

# def preview_chunks(
#     chunks: List[Document],
#     max_chunks: int = 5,
#     max_chars: int = 400,
# ) -> List[Dict]:
#     """
#     Return chunk preview for Streamlit/API.
#     """

#     previews = []

#     if not chunks:
#         return previews

#     for index, chunk in enumerate(chunks[:max_chunks], start=1):
#         metadata = chunk.metadata or {}

#         previews.append(
#             {
#                 "index": index,
#                 "pdf_name": metadata.get(
#                     "pdf_name",
#                     metadata.get("source", "Unknown PDF"),
#                 ),
#                 "page": metadata.get(
#                     "page_number",
#                     metadata.get("page", "Unknown page"),
#                 ),
#                 "chunk_id": metadata.get("chunk_id", index),
#                 "text_preview": chunk.page_content[:max_chars],
#                 "chunk_size": len(chunk.page_content),
#             }
#         )

#     return previews


# def get_chunk_stats(chunks: List[Document]) -> Dict:
#     """
#     Return stats about chunks.
#     """

#     if not chunks:
#         return {
#             "total_chunks": 0,
#             "average_chunk_size": 0,
#             "min_chunk_size": 0,
#             "max_chunk_size": 0,
#             "pdfs": {},
#         }

#     chunk_sizes = [len(chunk.page_content) for chunk in chunks]

#     pdfs = {}

#     for chunk in chunks:
#         metadata = chunk.metadata or {}

#         pdf_name = metadata.get(
#             "pdf_name",
#             metadata.get("source", "Unknown PDF"),
#         )

#         page_number = metadata.get(
#             "page_number",
#             metadata.get("page", "Unknown page"),
#         )

#         if pdf_name not in pdfs:
#             pdfs[pdf_name] = {
#                 "chunks": 0,
#                 "pages": set(),
#             }

#         pdfs[pdf_name]["chunks"] += 1
#         pdfs[pdf_name]["pages"].add(str(page_number))

#     clean_pdfs = {}

#     for pdf_name, data in pdfs.items():
#         clean_pdfs[pdf_name] = {
#             "chunks": data["chunks"],
#             "pages": sorted(list(data["pages"])),
#             "total_pages_found": len(data["pages"]),
#         }

#     return {
#         "total_chunks": len(chunks),
#         "average_chunk_size": round(sum(chunk_sizes) / len(chunk_sizes), 2),
#         "min_chunk_size": min(chunk_sizes),
#         "max_chunk_size": max(chunk_sizes),
#         "pdfs": clean_pdfs,
#     }


# # ---------------------------------------------------------
# # Search within chunks
# # ---------------------------------------------------------

# def search_chunks_by_keyword(
#     chunks: List[Document],
#     keyword: str,
#     max_results: int = 10,
# ) -> List[Dict]:
#     """
#     Simple keyword search inside created chunks.

#     This is only for debugging/testing.
#     Real search happens through vector DB retriever.
#     """

#     if not chunks or not keyword:
#         return []

#     keyword_lower = keyword.lower()
#     results = []

#     for chunk in chunks:
#         text = chunk.page_content or ""

#         if keyword_lower in text.lower():
#             metadata = chunk.metadata or {}

#             results.append(
#                 {
#                     "pdf_name": metadata.get(
#                         "pdf_name",
#                         metadata.get("source", "Unknown PDF"),
#                     ),
#                     "page": metadata.get(
#                         "page_number",
#                         metadata.get("page", "Unknown page"),
#                     ),
#                     "chunk_id": metadata.get("chunk_id"),
#                     "text_preview": text[:500],
#                 }
#             )

#         if len(results) >= max_results:
#             break

#     return results


# # ---------------------------------------------------------
# # API helper
# # ---------------------------------------------------------

# def chunks_to_api_preview(
#     chunks: List[Document],
#     max_chunks: int = 10,
#     max_chars: int = 500,
# ) -> Dict:
#     """
#     Helper for FastAPI response.
#     """

#     return {
#         "stats": get_chunk_stats(chunks),
#         "preview": preview_chunks(
#             chunks=chunks,
#             max_chunks=max_chunks,
#             max_chars=max_chars,
#         ),
#     }


# # ---------------------------------------------------------
# # Self test
# # ---------------------------------------------------------

# def run_chunker_self_test() -> Dict:
#     """
#     Self-test for chunker.py.
#     """

#     try:
#         sample_text = """
#         Machine learning is a branch of artificial intelligence.
#         It allows systems to learn from data without being explicitly programmed.

#         Supervised learning uses labelled data.
#         Unsupervised learning finds hidden patterns in unlabelled data.
#         Reinforcement learning uses rewards and penalties.

#         In interviews, machine learning questions usually focus on algorithms,
#         datasets, training, testing, overfitting, and evaluation metrics.
#         """

#         sample_doc = Document(
#             page_content=sample_text,
#             metadata={
#                 "pdf_name": "sample_notes.pdf",
#                 "source": "sample_notes.pdf",
#                 "page_number": 1,
#                 "page": 1,
#             },
#         )

#         result = chunk_documents(
#             documents=[sample_doc],
#             session_id=None,
#             chunk_size=200,
#             chunk_overlap=40,
#         )

#         return {
#             "success": result["success"],
#             "total_chunks": result["total_chunks"],
#             "stats": get_chunk_stats(result["chunks"]),
#             "preview": preview_chunks(result["chunks"]),
#             "message": "Chunker self-test completed.",
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "message": str(e),
#         }


# if __name__ == "__main__":
#     print(run_chunker_self_test())









































from typing import Dict, List, Optional
import logging
import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    MIN_CHUNK_CHARS,
)

from src.session_manager import (
    mark_pdf_processed,
    update_total_chunks,
)


logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------

def clean_chunk_text(text: str) -> str:
    """
    Clean text before chunking.

    Important:
    - Do not over-clean because RAG needs context.
    - Preserve headings, bullet points, formulas, and paragraphs.
    """

    if not text:
        return ""

    text = str(text)

    text = text.replace("\x00", " ")
    text = text.replace("\t", " ")
    text = text.replace("\r", "\n")

    # Normalize weird spaces
    text = text.replace("\u00a0", " ")
    text = text.replace("\u200b", "")

    # Fix broken hyphenated words across lines:
    # "classifi-\ncation" -> "classification"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Remove too many spaces inside lines
    lines = text.splitlines()
    cleaned_lines = []

    previous_blank = False

    for line in lines:
        line = line.strip()

        # Collapse internal spaces
        line = re.sub(r"[ ]{2,}", " ", line)

        if not line:
            if not previous_blank:
                cleaned_lines.append("")
            previous_blank = True
            continue

        cleaned_lines.append(line)
        previous_blank = False

    cleaned = "\n".join(cleaned_lines)

    # Max 2 continuous newlines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


def is_valid_chunk_text(text: str, min_chars: int = MIN_CHUNK_CHARS) -> bool:
    """
    Check whether chunk text is useful.
    """

    if not text:
        return False

    text = str(text).strip()

    if len(text) < min_chars:
        return False

    alnum_count = sum(ch.isalnum() for ch in text)

    if alnum_count < max(1, min_chars // 2):
        return False

    return True


def detect_section_title(text: str) -> str:
    """
    Try to detect a heading/topic from the chunk.

    This helps debugging and can improve metadata quality.
    """

    if not text:
        return "Unknown section"

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines[:8]:
        clean_line = re.sub(r"^[\-\*\•\d\.\)\s]+", "", line).strip()

        if 3 <= len(clean_line) <= 90:
            # Heading-like line: not too long, not ending like a full paragraph
            if not clean_line.endswith(".") or clean_line.isupper():
                return clean_line

    return lines[0][:90] if lines else "Unknown section"


# ---------------------------------------------------------
# Splitter
# ---------------------------------------------------------

def get_text_splitter(
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> RecursiveCharacterTextSplitter:
    """
    Create LangChain text splitter.

    Better separators help preserve:
    - headings
    - numbered lists
    - bullet points
    - formulas
    - paragraphs
    """

    safe_chunk_size = int(chunk_size or CHUNK_SIZE)
    safe_chunk_overlap = int(chunk_overlap or CHUNK_OVERLAP)

    if safe_chunk_size <= 0:
        safe_chunk_size = CHUNK_SIZE

    if safe_chunk_overlap < 0:
        safe_chunk_overlap = 0

    if safe_chunk_overlap >= safe_chunk_size:
        safe_chunk_overlap = max(0, safe_chunk_size // 5)

    return RecursiveCharacterTextSplitter(
        chunk_size=safe_chunk_size,
        chunk_overlap=safe_chunk_overlap,
        length_function=len,
        separators=[
            "\n\n# ",
            "\n\n## ",
            "\n\n### ",
            "\n\n",
            "\n• ",
            "\n- ",
            "\n* ",
            "\n1. ",
            "\n2. ",
            "\n3. ",
            "\n4. ",
            "\n5. ",
            "\n",
            ". ",
            "? ",
            "! ",
            "; ",
            ", ",
            " ",
            "",
        ],
    )


# ---------------------------------------------------------
# Chunk single document
# ---------------------------------------------------------

def chunk_single_document(
    document: Document,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    start_chunk_id: int = 1,
) -> List[Document]:
    """
    Split one LangChain Document into smaller chunks.

    Input document usually represents one PDF page.
    Output documents represent RAG chunks.
    """

    if document is None:
        return []

    page_content = clean_chunk_text(document.page_content)

    if not is_valid_chunk_text(page_content, min_chars=10):
        return []

    metadata = document.metadata or {}

    splitter = get_text_splitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    text_chunks = splitter.split_text(page_content)

    # Fallback:
    # If page is useful but splitter somehow creates no chunks, keep whole page.
    if not text_chunks and is_valid_chunk_text(page_content, min_chars=MIN_CHUNK_CHARS):
        text_chunks = [page_content]

    chunked_documents = []
    current_chunk_id = int(start_chunk_id or 1)

    pdf_name = (
        metadata.get("pdf_name")
        or metadata.get("source")
        or metadata.get("file_name")
        or "Unknown PDF"
    )

    page_number = (
        metadata.get("page_number")
        or metadata.get("page")
        or "Unknown page"
    )

    total_local_chunks = len(text_chunks)

    for local_index, chunk_text in enumerate(text_chunks, start=1):
        chunk_text = clean_chunk_text(chunk_text)

        if not is_valid_chunk_text(chunk_text):
            continue

        section_title = detect_section_title(chunk_text)

        new_metadata = dict(metadata)

        new_metadata.update(
            {
                "pdf_name": pdf_name,
                "source": pdf_name,
                "page_number": page_number,
                "page": page_number,
                "chunk_id": current_chunk_id,
                "local_chunk_index": local_index,
                "local_chunk_total": total_local_chunks,
                "chunk_size": len(chunk_text),
                "section_title": section_title,
                "content_type": "pdf_chunk",
                "has_previous_chunk": local_index > 1,
                "has_next_chunk": local_index < total_local_chunks,
            }
        )

        chunked_documents.append(
            Document(
                page_content=chunk_text,
                metadata=new_metadata,
            )
        )

        current_chunk_id += 1

    return chunked_documents


# ---------------------------------------------------------
# Chunk multiple documents
# ---------------------------------------------------------

def chunk_documents(
    documents: List[Document],
    session_id: Optional[str] = None,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> Dict:
    """
    Chunk multiple LangChain Documents.

    Usually called after:
        process_uploaded_pdfs_for_session(session_id)

    Returns:
        {
            "success": True,
            "chunks": [Document, Document],
            "total_chunks": 100,
            "pdf_chunk_counts": {...}
        }
    """

    if not documents:
        return {
            "success": False,
            "chunks": [],
            "total_chunks": 0,
            "pdf_chunk_counts": {},
            "pdf_page_counts": {},
            "stats": {},
            "error": "No documents provided for chunking.",
        }

    all_chunks: List[Document] = []
    pdf_chunk_counts: Dict[str, int] = {}
    pdf_page_counts: Dict[str, int] = {}

    global_chunk_id = 1

    safe_chunk_size = int(chunk_size or CHUNK_SIZE)
    safe_chunk_overlap = int(chunk_overlap or CHUNK_OVERLAP)

    if safe_chunk_size <= 0:
        safe_chunk_size = CHUNK_SIZE

    if safe_chunk_overlap < 0:
        safe_chunk_overlap = 0

    if safe_chunk_overlap >= safe_chunk_size:
        safe_chunk_overlap = max(0, safe_chunk_size // 5)

    for document in documents:
        if document is None:
            continue

        metadata = document.metadata or {}

        pdf_name = (
            metadata.get("pdf_name")
            or metadata.get("source")
            or metadata.get("file_name")
            or "Unknown PDF"
        )

        page_number = (
            metadata.get("page_number")
            or metadata.get("page")
            or "Unknown page"
        )

        chunks = chunk_single_document(
            document=document,
            chunk_size=safe_chunk_size,
            chunk_overlap=safe_chunk_overlap,
            start_chunk_id=global_chunk_id,
        )

        if not chunks:
            continue

        all_chunks.extend(chunks)
        global_chunk_id += len(chunks)

        pdf_chunk_counts[pdf_name] = pdf_chunk_counts.get(pdf_name, 0) + len(chunks)

        try:
            page_as_int = int(page_number)

            # If page numbers are 0-based, convert only for count tracking.
            if page_as_int == 0:
                page_as_int = 1

            pdf_page_counts[pdf_name] = max(
                pdf_page_counts.get(pdf_name, 0),
                page_as_int,
            )
        except Exception:
            pdf_page_counts[pdf_name] = pdf_page_counts.get(pdf_name, 0)

    if session_id:
        update_total_chunks(session_id, len(all_chunks))

        for pdf_name, chunk_count in pdf_chunk_counts.items():
            pages = pdf_page_counts.get(pdf_name, 0)

            mark_pdf_processed(
                session_id=session_id,
                pdf_name=pdf_name,
                pages=pages,
                chunks=chunk_count,
            )

    return {
        "success": len(all_chunks) > 0,
        "chunks": all_chunks,
        "total_chunks": len(all_chunks),
        "pdf_chunk_counts": pdf_chunk_counts,
        "pdf_page_counts": pdf_page_counts,
        "stats": get_chunk_stats(all_chunks),
        "error": None if all_chunks else "No valid chunks created.",
    }


# ---------------------------------------------------------
# Chunk by raw text directly
# ---------------------------------------------------------

def chunk_text(
    text: str,
    metadata: Optional[Dict] = None,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Document]:
    """
    Chunk raw text directly.

    Useful for testing or API usage.
    """

    if metadata is None:
        metadata = {}

    document = Document(
        page_content=text or "",
        metadata=metadata,
    )

    return chunk_single_document(
        document=document,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        start_chunk_id=1,
    )


# ---------------------------------------------------------
# Preview helpers
# ---------------------------------------------------------

def preview_chunks(
    chunks: List[Document],
    max_chunks: int = 5,
    max_chars: int = 500,
) -> List[Dict]:
    """
    Return chunk preview for Streamlit/API.
    """

    previews = []

    if not chunks:
        return previews

    for index, chunk in enumerate(chunks[:max_chunks], start=1):
        metadata = chunk.metadata or {}

        previews.append(
            {
                "index": index,
                "pdf_name": metadata.get(
                    "pdf_name",
                    metadata.get("source", "Unknown PDF"),
                ),
                "page": metadata.get(
                    "page_number",
                    metadata.get("page", "Unknown page"),
                ),
                "chunk_id": metadata.get("chunk_id", index),
                "section_title": metadata.get("section_title", "Unknown section"),
                "text_preview": chunk.page_content[:max_chars],
                "chunk_size": len(chunk.page_content),
                "local_chunk_index": metadata.get("local_chunk_index"),
                "local_chunk_total": metadata.get("local_chunk_total"),
            }
        )

    return previews


def get_chunk_stats(chunks: List[Document]) -> Dict:
    """
    Return stats about chunks.
    """

    if not chunks:
        return {
            "total_chunks": 0,
            "average_chunk_size": 0,
            "min_chunk_size": 0,
            "max_chunk_size": 0,
            "pdfs": {},
        }

    chunk_sizes = [len(chunk.page_content or "") for chunk in chunks]

    pdfs = {}

    for chunk in chunks:
        metadata = chunk.metadata or {}

        pdf_name = metadata.get(
            "pdf_name",
            metadata.get("source", "Unknown PDF"),
        )

        page_number = metadata.get(
            "page_number",
            metadata.get("page", "Unknown page"),
        )

        section_title = metadata.get("section_title", "Unknown section")

        if pdf_name not in pdfs:
            pdfs[pdf_name] = {
                "chunks": 0,
                "pages": set(),
                "sections": set(),
            }

        pdfs[pdf_name]["chunks"] += 1
        pdfs[pdf_name]["pages"].add(str(page_number))

        if section_title:
            pdfs[pdf_name]["sections"].add(str(section_title))

    clean_pdfs = {}

    for pdf_name, data in pdfs.items():
        clean_pdfs[pdf_name] = {
            "chunks": data["chunks"],
            "pages": sorted(list(data["pages"])),
            "total_pages_found": len(data["pages"]),
            "sample_sections": sorted(list(data["sections"]))[:10],
        }

    return {
        "total_chunks": len(chunks),
        "average_chunk_size": round(sum(chunk_sizes) / len(chunk_sizes), 2),
        "min_chunk_size": min(chunk_sizes),
        "max_chunk_size": max(chunk_sizes),
        "pdfs": clean_pdfs,
    }


# ---------------------------------------------------------
# Search within chunks
# ---------------------------------------------------------

def search_chunks_by_keyword(
    chunks: List[Document],
    keyword: str,
    max_results: int = 10,
) -> List[Dict]:
    """
    Simple keyword search inside created chunks.

    This is only for debugging/testing.
    Real search happens through vector DB retriever.
    """

    if not chunks or not keyword:
        return []

    keyword_lower = keyword.lower()
    results = []

    for chunk in chunks:
        text = chunk.page_content or ""

        if keyword_lower in text.lower():
            metadata = chunk.metadata or {}

            results.append(
                {
                    "pdf_name": metadata.get(
                        "pdf_name",
                        metadata.get("source", "Unknown PDF"),
                    ),
                    "page": metadata.get(
                        "page_number",
                        metadata.get("page", "Unknown page"),
                    ),
                    "chunk_id": metadata.get("chunk_id"),
                    "section_title": metadata.get("section_title", "Unknown section"),
                    "text_preview": text[:700],
                    "chunk_size": len(text),
                }
            )

        if len(results) >= max_results:
            break

    return results


# ---------------------------------------------------------
# API helper
# ---------------------------------------------------------

def chunks_to_api_preview(
    chunks: List[Document],
    max_chunks: int = 10,
    max_chars: int = 700,
) -> Dict:
    """
    Helper for FastAPI response.
    """

    return {
        "stats": get_chunk_stats(chunks),
        "preview": preview_chunks(
            chunks=chunks,
            max_chunks=max_chunks,
            max_chars=max_chars,
        ),
    }


# ---------------------------------------------------------
# Self test
# ---------------------------------------------------------

def run_chunker_self_test() -> Dict:
    """
    Self-test for chunker.py.
    """

    try:
        sample_text = """
Machine Learning

Machine learning is a branch of artificial intelligence.
It allows systems to learn from data without being explicitly programmed.

Types of Machine Learning

1. Supervised Learning
Supervised learning uses labelled data.
The model learns a mapping between input and output.

2. Unsupervised Learning
Unsupervised learning finds hidden patterns in unlabelled data.

3. Reinforcement Learning
Reinforcement learning uses rewards and penalties.

Interview Important Points

In interviews, machine learning questions usually focus on algorithms,
datasets, training, testing, overfitting, and evaluation metrics.

Advantages

- It can automate prediction tasks.
- It can handle large datasets.
- It improves with more data.

Limitations

- It needs good quality data.
- It can overfit.
- It may be difficult to interpret.
        """

        sample_doc = Document(
            page_content=sample_text,
            metadata={
                "pdf_name": "sample_notes.pdf",
                "source": "sample_notes.pdf",
                "page_number": 1,
                "page": 1,
            },
        )

        result = chunk_documents(
            documents=[sample_doc],
            session_id=None,
            chunk_size=300,
            chunk_overlap=80,
        )

        return {
            "success": result["success"],
            "total_chunks": result["total_chunks"],
            "stats": get_chunk_stats(result["chunks"]),
            "preview": preview_chunks(result["chunks"]),
            "message": "Chunker self-test completed.",
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
        }


if __name__ == "__main__":
    print(run_chunker_self_test())