# __version__ = "1.0.0"
# __app_name__ = "RAG Interview Assistant"


# # Main session helpers
# from src.session_manager import (
#     get_or_create_session_id,
#     save_uploaded_pdf,
#     create_user_folders,
#     get_user_paths,
#     get_chroma_path,
#     get_uploaded_pdfs,
#     clear_user_data,
# )

# # PDF processing
# from src.pdf_processor import (
#     process_uploaded_pdfs_for_session,
#     process_single_pdf,
#     process_multiple_pdfs,
# )

# # Chunking
# from src.chunker import (
#     chunk_documents,
#     chunk_text,
#     get_chunk_stats,
#     preview_chunks,
# )

# # Embeddings
# from src.embeddings import (
#     get_embedding_model,
#     embed_texts,
#     embed_query,
#     get_embedding_status,
# )

# # RAG
# from src.rag_chain import (
#     ask_rag,
#     summarize_notes,
#     generate_questions,
#     generate_flashcards,
#     check_rag_ready,
#     get_rag_status,
# )

# # Config
# from src.config import (
#     APP_NAME,
#     APP_VERSION,
#     DEFAULT_LLM_MODEL,
#     DEFAULT_EMBEDDING_MODEL,
#     CHUNK_SIZE,
#     CHUNK_OVERLAP,
# )


# __all__ = [
#     "__version__",
#     "__app_name__",

#     # Session
#     "get_or_create_session_id",
#     "save_uploaded_pdf",
#     "create_user_folders",
#     "get_user_paths",
#     "get_chroma_path",
#     "get_uploaded_pdfs",
#     "clear_user_data",

#     # PDF
#     "process_uploaded_pdfs_for_session",
#     "process_single_pdf",
#     "process_multiple_pdfs",

#     # Chunking
#     "chunk_documents",
#     "chunk_text",
#     "get_chunk_stats",
#     "preview_chunks",

#     # Embeddings
#     "get_embedding_model",
#     "embed_texts",
#     "embed_query",
#     "get_embedding_status",

#     # RAG
#     "ask_rag",
#     "summarize_notes",
#     "generate_questions",
#     "generate_flashcards",
#     "check_rag_ready",
#     "get_rag_status",

#     # Config
#     "APP_NAME",
#     "APP_VERSION",
#     "DEFAULT_LLM_MODEL",
#     "DEFAULT_EMBEDDING_MODEL",
#     "CHUNK_SIZE",
#     "CHUNK_OVERLAP",
# ]

__version__ = "1.0.0"
__app_name__ = "InterviewIQ RAG Backend"


# ---------------------------------------------------------
# Main session helpers
# ---------------------------------------------------------

from src.session_manager import (
    generate_session_id,
    get_or_create_session_id,
    save_uploaded_pdf,
    save_uploaded_pdf_bytes,
    create_user_folders,
    get_user_paths,
    get_chroma_path,
    get_uploaded_pdfs,
    get_session_summary,
    clear_user_data,
    clear_all_session_files,
    clear_only_uploaded_files,
)


# ---------------------------------------------------------
# PDF processing
# ---------------------------------------------------------

from src.pdf_processor import (
    process_uploaded_pdfs_for_session,
    process_single_pdf,
    process_multiple_pdfs,
    get_session_pdf_summary,
    preview_pdf_text,
)


# ---------------------------------------------------------
# Chunking
# ---------------------------------------------------------

from src.chunker import (
    chunk_documents,
    chunk_text,
    get_chunk_stats,
    preview_chunks,
    chunks_to_api_preview,
)


# ---------------------------------------------------------
# Embeddings
# ---------------------------------------------------------

from src.embeddings import (
    get_embedding_model,
    embed_texts,
    embed_query,
    get_embedding_status,
    clear_embedding_cache,
)


# ---------------------------------------------------------
# Vector store
# ---------------------------------------------------------

from src.vector_store import (
    index_documents_pipeline,
    build_vector_store_from_chunks,
    get_vector_store,
    get_vector_store_status,
    get_vector_store_api_summary,
    similarity_search,
    similarity_search_with_score,
    reset_vector_store,
)


# ---------------------------------------------------------
# RAG
# ---------------------------------------------------------

from src.rag_chain import (
    ask_rag,
    summarize_notes,
    generate_questions,
    generate_flashcards,
    ask_direct_llm,
    check_rag_ready,
    get_rag_status,
)


# ---------------------------------------------------------
# Resume Gap Finder
# ---------------------------------------------------------

from src.resume import (
    analyze_resume_file_bytes_and_jd_with_rag,
    analyze_resume_against_jd_with_rag,
    extract_text_from_file_bytes,
    extract_text_from_pdf_bytes,
    extract_text_from_txt_bytes,
    extract_text_from_docx_bytes,
)


# ---------------------------------------------------------
# OCR
# ---------------------------------------------------------

from src.ocr_processor import (
    extract_text_from_image,
    get_ocr_status,
    clear_ocr_cache,
)


# ---------------------------------------------------------
# Config
# ---------------------------------------------------------

from src.config import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    API_DESCRIPTION,
    FRONTEND_URL,
    BACKEND_URL,
    CORS_ALLOWED_ORIGINS,
    DEFAULT_LLM_MODEL,
    DEFAULT_EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    MAX_UPLOAD_SIZE_MB,
    MAX_PDFS_PER_SESSION,
    get_config_summary,
    is_groq_configured,
)


__all__ = [
    "__version__",
    "__app_name__",

    # Session
    "generate_session_id",
    "get_or_create_session_id",
    "save_uploaded_pdf",
    "save_uploaded_pdf_bytes",
    "create_user_folders",
    "get_user_paths",
    "get_chroma_path",
    "get_uploaded_pdfs",
    "get_session_summary",
    "clear_user_data",
    "clear_all_session_files",
    "clear_only_uploaded_files",

    # PDF
    "process_uploaded_pdfs_for_session",
    "process_single_pdf",
    "process_multiple_pdfs",
    "get_session_pdf_summary",
    "preview_pdf_text",

    # Chunking
    "chunk_documents",
    "chunk_text",
    "get_chunk_stats",
    "preview_chunks",
    "chunks_to_api_preview",

    # Embeddings
    "get_embedding_model",
    "embed_texts",
    "embed_query",
    "get_embedding_status",
    "clear_embedding_cache",

    # Vector store
    "index_documents_pipeline",
    "build_vector_store_from_chunks",
    "get_vector_store",
    "get_vector_store_status",
    "get_vector_store_api_summary",
    "similarity_search",
    "similarity_search_with_score",
    "reset_vector_store",

    # RAG
    "ask_rag",
    "summarize_notes",
    "generate_questions",
    "generate_flashcards",
    "ask_direct_llm",
    "check_rag_ready",
    "get_rag_status",

    # Resume
    "analyze_resume_file_bytes_and_jd_with_rag",
    "analyze_resume_against_jd_with_rag",
    "extract_text_from_file_bytes",
    "extract_text_from_pdf_bytes",
    "extract_text_from_txt_bytes",
    "extract_text_from_docx_bytes",

    # OCR
    "extract_text_from_image",
    "get_ocr_status",
    "clear_ocr_cache",

    # Config
    "APP_NAME",
    "APP_VERSION",
    "APP_DESCRIPTION",
    "API_TITLE",
    "API_VERSION",
    "API_DESCRIPTION",
    "FRONTEND_URL",
    "BACKEND_URL",
    "CORS_ALLOWED_ORIGINS",
    "DEFAULT_LLM_MODEL",
    "DEFAULT_EMBEDDING_MODEL",
    "CHUNK_SIZE",
    "CHUNK_OVERLAP",
    "MAX_UPLOAD_SIZE_MB",
    "MAX_PDFS_PER_SESSION",
    "get_config_summary",
    "is_groq_configured",
]