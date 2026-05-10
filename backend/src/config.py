# import os
# from pathlib import Path
# from typing import Dict, Optional

# from dotenv import load_dotenv


# load_dotenv()


# BASE_DIR = Path(__file__).resolve().parent.parent

# SRC_DIR = BASE_DIR / "src"
# STORAGE_DIR = BASE_DIR / "storage"
# USERS_DIR = STORAGE_DIR / "users"
# LOGS_DIR = BASE_DIR / "logs"


# APP_NAME = "RAG Interview Assistant"
# APP_VERSION = "1.0.0"
# APP_DESCRIPTION = (
#     "Study from uploaded PDF notes using RAG, LangChain, "
#     "ChromaDB, local embeddings, and Groq LLM API."
# )


# ENV = os.getenv("ENV", "development")
# DEBUG = os.getenv("DEBUG", "true").lower() == "true"
# IS_PRODUCTION = ENV.lower() == "production"


# BACKEND_ANSWER_MODE = os.getenv("BACKEND_ANSWER_MODE", "interview")
# BACKEND_SEARCH_TYPE = os.getenv("BACKEND_SEARCH_TYPE", "similarity")
# BACKEND_TOP_K = int(os.getenv("BACKEND_TOP_K", "5"))
# PARALLEL_PDF_WORKERS = int(os.getenv("PARALLEL_PDF_WORKERS", "4"))


# CLEAR_FILES_ON_APP_START = os.getenv("CLEAR_FILES_ON_APP_START", "false").lower() == "true"
# ENABLE_CLEAR_FILES_BUTTON = os.getenv("ENABLE_CLEAR_FILES_BUTTON", "true").lower() == "true"
# CLEAR_CHROMA_ON_FILE_CLEAR = os.getenv("CLEAR_CHROMA_ON_FILE_CLEAR", "true").lower() == "true"


# LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()


# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# GROQ_MODEL = os.getenv(
#     "GROQ_MODEL",
#     "llama-3.1-8b-instant",
# )

# AVAILABLE_GROQ_MODELS = {
#     "fast": {
#         "name": "llama-3.1-8b-instant",
#         "description": "Fast and good for demo/deployment.",
#     },
#     "balanced": {
#         "name": "llama-3.3-70b-versatile",
#         "description": "Better quality, may use more limits.",
#     },
#     "gemma": {
#         "name": "gemma2-9b-it",
#         "description": "Good open model option on Groq.",
#     },
# }

# GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.2"))
# GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "900"))


# OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# AVAILABLE_OLLAMA_MODELS = {
#     "fast": {
#         "name": "qwen2.5:3b",
#         "description": "Small, local, needs Ollama model downloaded.",
#     },
#     "balanced": {
#         "name": "mistral:7b",
#         "description": "Better local answer quality, needs more RAM.",
#     },
#     "accurate": {
#         "name": "llama3.1:8b",
#         "description": "Good local accuracy, heavier model.",
#     },
#     "coding": {
#         "name": "qwen2.5-coder:3b",
#         "description": "Good for programming/interview coding notes.",
#     },
# }

# DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", GROQ_MODEL)

# LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", str(GROQ_TEMPERATURE)))
# LLM_TOP_K = int(os.getenv("LLM_TOP_K", str(BACKEND_TOP_K)))
# LLM_MAX_CONTEXT_CHARS = int(os.getenv("LLM_MAX_CONTEXT_CHARS", "12000"))


# DEFAULT_EMBEDDING_MODEL = os.getenv(
#     "DEFAULT_EMBEDDING_MODEL",
#     "sentence-transformers/all-MiniLM-L6-v2",
# )

# AVAILABLE_EMBEDDING_MODELS = {
#     "fast": {
#         "name": "sentence-transformers/all-MiniLM-L6-v2",
#         "description": "Small, fast, CPU friendly, best for deployment demo.",
#     },
#     "balanced": {
#         "name": "BAAI/bge-small-en-v1.5",
#         "description": "Good balance between speed and accuracy.",
#     },
#     "accurate": {
#         "name": "sentence-transformers/all-mpnet-base-v2",
#         "description": "Better accuracy, heavier model.",
#     },
# }

# EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")
# NORMALIZE_EMBEDDINGS = os.getenv("NORMALIZE_EMBEDDINGS", "true").lower() == "true"


# CHROMA_COLLECTION_NAME = os.getenv(
#     "CHROMA_COLLECTION_NAME",
#     "rag_interview_notes",
# )

# CHROMA_SEARCH_TYPE = os.getenv("CHROMA_SEARCH_TYPE", BACKEND_SEARCH_TYPE)
# CHROMA_TOP_K = int(os.getenv("CHROMA_TOP_K", str(BACKEND_TOP_K)))


# ALLOWED_FILE_TYPES = [".pdf"]

# MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
# MAX_PDFS_PER_SESSION = int(os.getenv("MAX_PDFS_PER_SESSION", "10"))

# PDF_TEXT_MAX_CHARS_PER_PAGE = int(
#     os.getenv("PDF_TEXT_MAX_CHARS_PER_PAGE", "12000")
# )

# EXTRACT_IMAGES_FROM_PDF = os.getenv(
#     "EXTRACT_IMAGES_FROM_PDF",
#     "false",
# ).lower() == "true"

# ENABLE_OCR = os.getenv("ENABLE_OCR", "false").lower() == "true"


# OCR_ENGINE = os.getenv("OCR_ENGINE", "none")
# OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "en").split(",")
# OCR_USE_GPU = os.getenv("OCR_USE_GPU", "false").lower() == "true"
# OCR_PREPROCESS_IMAGE = os.getenv("OCR_PREPROCESS_IMAGE", "true").lower() == "true"


# CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "900"))
# CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
# MIN_CHUNK_CHARS = int(os.getenv("MIN_CHUNK_CHARS", "50"))


# STREAMLIT_PAGE_TITLE = "Study From Notes - RAG Interview Assistant"
# STREAMLIT_PAGE_ICON = "📚"
# STREAMLIT_LAYOUT = "wide"


# API_TITLE = "RAG Interview Assistant API"
# API_VERSION = "1.0.0"
# API_DESCRIPTION = "API for PDF upload, RAG retrieval, and Groq LLM answer generation."

# API_HOST = os.getenv("API_HOST", "0.0.0.0")
# API_PORT = int(os.getenv("API_PORT", "8000"))

# CORS_ALLOWED_ORIGINS = os.getenv(
#     "CORS_ALLOWED_ORIGINS",
#     "http://localhost:5173,http://localhost:3000,http://localhost:8501",
# ).split(",")


# def create_base_folders() -> None:
#     STORAGE_DIR.mkdir(parents=True, exist_ok=True)
#     USERS_DIR.mkdir(parents=True, exist_ok=True)
#     LOGS_DIR.mkdir(parents=True, exist_ok=True)


# def get_user_base_dir(session_id: str) -> Path:
#     return USERS_DIR / str(session_id)


# def get_user_pdf_dir(session_id: str) -> Path:
#     return get_user_base_dir(session_id) / "pdfs"


# def get_user_image_dir(session_id: str) -> Path:
#     return get_user_base_dir(session_id) / "images"


# def get_user_chroma_dir(session_id: str) -> Path:
#     return get_user_base_dir(session_id) / "chroma_db"


# def get_user_metadata_file(session_id: str) -> Path:
#     return get_user_base_dir(session_id) / "metadata.json"


# def is_allowed_file(filename: str) -> bool:
#     if not filename:
#         return False

#     suffix = Path(filename).suffix.lower()

#     return suffix in ALLOWED_FILE_TYPES


# def bytes_to_mb(size_bytes: int) -> float:
#     return round(size_bytes / (1024 * 1024), 2)


# def is_file_size_allowed(size_bytes: int) -> bool:
#     size_mb = bytes_to_mb(size_bytes)

#     return size_mb <= MAX_UPLOAD_SIZE_MB


# def validate_upload_file(
#     filename: str,
#     size_bytes: Optional[int] = None,
# ) -> Dict:
#     if not filename:
#         return {
#             "valid": False,
#             "message": "Filename is missing.",
#         }

#     if not is_allowed_file(filename):
#         return {
#             "valid": False,
#             "message": "Only PDF files are allowed.",
#         }

#     if size_bytes is not None:
#         if not is_file_size_allowed(size_bytes):
#             return {
#                 "valid": False,
#                 "message": f"File size must be less than {MAX_UPLOAD_SIZE_MB} MB.",
#             }

#     return {
#         "valid": True,
#         "message": "File is valid.",
#     }


# def get_llm_provider() -> str:
#     return LLM_PROVIDER


# def get_groq_api_key() -> str:
#     return GROQ_API_KEY


# def get_groq_model() -> str:
#     return GROQ_MODEL


# def get_groq_temperature() -> float:
#     return GROQ_TEMPERATURE


# def get_groq_max_tokens() -> int:
#     return GROQ_MAX_TOKENS


# def is_groq_configured() -> bool:
#     return bool(GROQ_API_KEY and GROQ_API_KEY.strip())


# def get_backend_llm_model() -> str:
#     if LLM_PROVIDER == "groq":
#         return GROQ_MODEL

#     return DEFAULT_LLM_MODEL


# def get_backend_top_k() -> int:
#     return BACKEND_TOP_K


# def get_backend_search_type() -> str:
#     return BACKEND_SEARCH_TYPE


# def get_backend_answer_mode() -> str:
#     return BACKEND_ANSWER_MODE


# def get_parallel_pdf_workers() -> int:
#     return PARALLEL_PDF_WORKERS


# def should_clear_files_on_app_start() -> bool:
#     return CLEAR_FILES_ON_APP_START


# def should_show_clear_files_button() -> bool:
#     return ENABLE_CLEAR_FILES_BUTTON


# def should_clear_chroma_on_file_clear() -> bool:
#     return CLEAR_CHROMA_ON_FILE_CLEAR


# def get_llm_model(model_type: str = "fast") -> str:
#     if LLM_PROVIDER == "groq":
#         if model_type in AVAILABLE_GROQ_MODELS:
#             return AVAILABLE_GROQ_MODELS[model_type]["name"]
#         return GROQ_MODEL

#     if model_type in AVAILABLE_OLLAMA_MODELS:
#         return AVAILABLE_OLLAMA_MODELS[model_type]["name"]

#     return DEFAULT_LLM_MODEL


# def get_embedding_model(model_type: str = "fast") -> str:
#     if model_type in AVAILABLE_EMBEDDING_MODELS:
#         return AVAILABLE_EMBEDDING_MODELS[model_type]["name"]

#     return DEFAULT_EMBEDDING_MODEL


# def get_available_models() -> Dict:
#     return {
#         "llm_provider": LLM_PROVIDER,
#         "groq_models": AVAILABLE_GROQ_MODELS,
#         "ollama_models": AVAILABLE_OLLAMA_MODELS,
#         "embedding_models": AVAILABLE_EMBEDDING_MODELS,
#         "default_llm": get_backend_llm_model(),
#         "default_embedding": DEFAULT_EMBEDDING_MODEL,
#     }


# def get_config_summary() -> Dict:
#     return {
#         "app_name": APP_NAME,
#         "app_version": APP_VERSION,
#         "env": ENV,
#         "debug": DEBUG,
#         "storage_dir": str(STORAGE_DIR),
#         "users_dir": str(USERS_DIR),
#         "llm_provider": LLM_PROVIDER,
#         "groq_configured": is_groq_configured(),
#         "groq_model": GROQ_MODEL,
#         "groq_temperature": GROQ_TEMPERATURE,
#         "groq_max_tokens": GROQ_MAX_TOKENS,
#         "ollama_base_url": OLLAMA_BASE_URL,
#         "default_llm_model": get_backend_llm_model(),
#         "llm_temperature": LLM_TEMPERATURE,
#         "default_embedding_model": DEFAULT_EMBEDDING_MODEL,
#         "embedding_device": EMBEDDING_DEVICE,
#         "chroma_collection_name": CHROMA_COLLECTION_NAME,
#         "chroma_search_type": CHROMA_SEARCH_TYPE,
#         "chroma_top_k": CHROMA_TOP_K,
#         "backend_answer_mode": BACKEND_ANSWER_MODE,
#         "backend_search_type": BACKEND_SEARCH_TYPE,
#         "backend_top_k": BACKEND_TOP_K,
#         "chunk_size": CHUNK_SIZE,
#         "chunk_overlap": CHUNK_OVERLAP,
#         "min_chunk_chars": MIN_CHUNK_CHARS,
#         "enable_ocr": ENABLE_OCR,
#         "ocr_engine": OCR_ENGINE,
#         "extract_images_from_pdf": EXTRACT_IMAGES_FROM_PDF,
#         "parallel_pdf_workers": PARALLEL_PDF_WORKERS,
#         "max_upload_size_mb": MAX_UPLOAD_SIZE_MB,
#         "max_pdfs_per_session": MAX_PDFS_PER_SESSION,
#         "clear_files_on_app_start": CLEAR_FILES_ON_APP_START,
#         "enable_clear_files_button": ENABLE_CLEAR_FILES_BUTTON,
#         "clear_chroma_on_file_clear": CLEAR_CHROMA_ON_FILE_CLEAR,
#     }


# def print_config() -> None:
#     summary = get_config_summary()

#     print("\n========== RAG Interview Assistant Config ==========")

#     for key, value in summary.items():
#         print(f"{key}: {value}")

#     print("===================================================\n")


# create_base_folders()


# if __name__ == "__main__":
#     print_config()


import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv


# ---------------------------------------------------------
# Path setup
# ---------------------------------------------------------
# Current file:
# interviewiq-main/rag-backend/src/config.py
#
# BASE_DIR:
# interviewiq-main/rag-backend
#
# PROJECT_ROOT:
# interviewiq-main
# ---------------------------------------------------------


























# BASE_DIR = Path(__file__).resolve().parent.parent
# PROJECT_ROOT = BASE_DIR.parent

# SRC_DIR = BASE_DIR / "src"
# STORAGE_DIR = BASE_DIR / "storage"
# USERS_DIR = STORAGE_DIR / "users"
# LOGS_DIR = BASE_DIR / "logs"


# # ---------------------------------------------------------
# # Load one central env file from project root
# # ---------------------------------------------------------
# # Root env:
# # interviewiq-main/.env.local
# # ---------------------------------------------------------

# ROOT_ENV_FILE = PROJECT_ROOT / ".env.local"
# BACKEND_ENV_FILE = BASE_DIR / ".env"

# if ROOT_ENV_FILE.exists():
#     load_dotenv(dotenv_path=ROOT_ENV_FILE, override=True)
# else:
#     load_dotenv(dotenv_path=BACKEND_ENV_FILE, override=True)


# # ---------------------------------------------------------
# # App info
# # ---------------------------------------------------------

# APP_NAME = "InterviewIQ RAG Backend"
# APP_VERSION = "1.0.0"
# APP_DESCRIPTION = (
#     "Study from uploaded PDF notes using RAG, LangChain, "
#     "ChromaDB, local embeddings, and Groq LLM API."
# )

# ENV = os.getenv("ENV", "development")
# DEBUG = os.getenv("DEBUG", "true").lower() == "true"
# IS_PRODUCTION = ENV.lower() == "production"


# # ---------------------------------------------------------
# # Backend / API config
# # ---------------------------------------------------------

# API_TITLE = "InterviewIQ RAG Backend API"
# API_VERSION = "1.0.0"
# API_DESCRIPTION = "API for PDF upload, RAG retrieval, flashcards, and resume gap analysis."

# API_HOST = os.getenv("API_HOST", "0.0.0.0")
# API_PORT = int(os.getenv("API_PORT", "8000"))

# FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
# BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# CORS_ALLOWED_ORIGINS = os.getenv(
#     "CORS_ALLOWED_ORIGINS",
#     "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
# ).split(",")

# CORS_ALLOWED_ORIGINS = [
#     origin.strip()
#     for origin in CORS_ALLOWED_ORIGINS
#     if origin.strip()
# ]

# if FRONTEND_URL not in CORS_ALLOWED_ORIGINS:
#     CORS_ALLOWED_ORIGINS.append(FRONTEND_URL)


# # ---------------------------------------------------------
# # RAG behavior config
# # ---------------------------------------------------------

# BACKEND_ANSWER_MODE = os.getenv("BACKEND_ANSWER_MODE", "interview")
# BACKEND_SEARCH_TYPE = os.getenv("BACKEND_SEARCH_TYPE", "similarity")
# BACKEND_TOP_K = int(os.getenv("BACKEND_TOP_K", "5"))
# PARALLEL_PDF_WORKERS = int(os.getenv("PARALLEL_PDF_WORKERS", "4"))


# # ---------------------------------------------------------
# # Clear / reset behavior
# # ---------------------------------------------------------

# CLEAR_FILES_ON_APP_START = os.getenv(
#     "CLEAR_FILES_ON_APP_START",
#     "false",
# ).lower() == "true"

# ENABLE_CLEAR_FILES_BUTTON = os.getenv(
#     "ENABLE_CLEAR_FILES_BUTTON",
#     "true",
# ).lower() == "true"

# CLEAR_CHROMA_ON_FILE_CLEAR = os.getenv(
#     "CLEAR_CHROMA_ON_FILE_CLEAR",
#     "true",
# ).lower() == "true"


# # ---------------------------------------------------------
# # LLM provider config
# # ---------------------------------------------------------

# LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()


# # ---------------------------------------------------------
# # Groq config
# # ---------------------------------------------------------

# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# GROQ_MODEL = os.getenv(
#     "GROQ_MODEL",
#     "llama-3.1-8b-instant",
# )

# AVAILABLE_GROQ_MODELS = {
#     "fast": {
#         "name": "llama-3.1-8b-instant",
#         "description": "Fast and good for demo/deployment.",
#     },
#     "balanced": {
#         "name": "llama-3.3-70b-versatile",
#         "description": "Better quality, may use more limits.",
#     },
#     "gemma": {
#         "name": "gemma2-9b-it",
#         "description": "Good open model option on Groq.",
#     },
# }

# GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.2"))
# GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "900"))


# # ---------------------------------------------------------
# # Ollama config, optional local mode
# # ---------------------------------------------------------

# OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# AVAILABLE_OLLAMA_MODELS = {
#     "fast": {
#         "name": "qwen2.5:3b",
#         "description": "Small, local, needs Ollama model downloaded.",
#     },
#     "balanced": {
#         "name": "mistral:7b",
#         "description": "Better local answer quality, needs more RAM.",
#     },
#     "accurate": {
#         "name": "llama3.1:8b",
#         "description": "Good local accuracy, heavier model.",
#     },
#     "coding": {
#         "name": "qwen2.5-coder:3b",
#         "description": "Good for programming/interview coding notes.",
#     },
# }

# DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", GROQ_MODEL)

# LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", str(GROQ_TEMPERATURE)))
# LLM_TOP_K = int(os.getenv("LLM_TOP_K", str(BACKEND_TOP_K)))
# LLM_MAX_CONTEXT_CHARS = int(os.getenv("LLM_MAX_CONTEXT_CHARS", "12000"))


# # ---------------------------------------------------------
# # Embeddings config
# # ---------------------------------------------------------

# DEFAULT_EMBEDDING_MODEL = os.getenv(
#     "DEFAULT_EMBEDDING_MODEL",
#     "sentence-transformers/all-MiniLM-L6-v2",
# )

# AVAILABLE_EMBEDDING_MODELS = {
#     "fast": {
#         "name": "sentence-transformers/all-MiniLM-L6-v2",
#         "description": "Small, fast, CPU friendly, best for deployment demo.",
#     },
#     "balanced": {
#         "name": "BAAI/bge-small-en-v1.5",
#         "description": "Good balance between speed and accuracy.",
#     },
#     "accurate": {
#         "name": "sentence-transformers/all-mpnet-base-v2",
#         "description": "Better accuracy, heavier model.",
#     },
# }

# EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")
# NORMALIZE_EMBEDDINGS = os.getenv("NORMALIZE_EMBEDDINGS", "true").lower() == "true"


# # ---------------------------------------------------------
# # Vector DB config
# # Keeping your old Chroma naming because your existing vector_store.py may use it.
# # ---------------------------------------------------------

# VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "chroma").lower()

# CHROMA_COLLECTION_NAME = os.getenv(
#     "CHROMA_COLLECTION_NAME",
#     "rag_interview_notes",
# )

# CHROMA_SEARCH_TYPE = os.getenv("CHROMA_SEARCH_TYPE", BACKEND_SEARCH_TYPE)
# CHROMA_TOP_K = int(os.getenv("CHROMA_TOP_K", str(BACKEND_TOP_K)))


# # ---------------------------------------------------------
# # File upload config
# # ---------------------------------------------------------

# ALLOWED_FILE_TYPES = [".pdf"]

# MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
# MAX_PDFS_PER_SESSION = int(os.getenv("MAX_PDFS_PER_SESSION", "10"))

# PDF_TEXT_MAX_CHARS_PER_PAGE = int(
#     os.getenv("PDF_TEXT_MAX_CHARS_PER_PAGE", "12000")
# )

# EXTRACT_IMAGES_FROM_PDF = os.getenv(
#     "EXTRACT_IMAGES_FROM_PDF",
#     "false",
# ).lower() == "true"

# ENABLE_OCR = os.getenv("ENABLE_OCR", "false").lower() == "true"


# # ---------------------------------------------------------
# # OCR config
# # ---------------------------------------------------------

# OCR_ENGINE = os.getenv("OCR_ENGINE", "none")
# OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "en").split(",")
# OCR_USE_GPU = os.getenv("OCR_USE_GPU", "false").lower() == "true"
# OCR_PREPROCESS_IMAGE = os.getenv("OCR_PREPROCESS_IMAGE", "true").lower() == "true"


# # ---------------------------------------------------------
# # Chunking config
# # ---------------------------------------------------------

# CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "900"))
# CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
# MIN_CHUNK_CHARS = int(os.getenv("MIN_CHUNK_CHARS", "50"))


# # ---------------------------------------------------------
# # Old Streamlit config kept for compatibility
# # ---------------------------------------------------------

# STREAMLIT_PAGE_TITLE = "Study From Notes - RAG Interview Assistant"
# STREAMLIT_PAGE_ICON = "📚"
# STREAMLIT_LAYOUT = "wide"


# # ---------------------------------------------------------
# # Folder helpers
# # ---------------------------------------------------------

# def create_base_folders() -> None:
#     STORAGE_DIR.mkdir(parents=True, exist_ok=True)
#     USERS_DIR.mkdir(parents=True, exist_ok=True)
#     LOGS_DIR.mkdir(parents=True, exist_ok=True)


# def get_user_base_dir(session_id: str) -> Path:
#     return USERS_DIR / str(session_id)


# def get_user_pdf_dir(session_id: str) -> Path:
#     return get_user_base_dir(session_id) / "pdfs"


# def get_user_image_dir(session_id: str) -> Path:
#     return get_user_base_dir(session_id) / "images"


# def get_user_chroma_dir(session_id: str) -> Path:
#     return get_user_base_dir(session_id) / "chroma_db"


# def get_user_vector_dir(session_id: str) -> Path:
#     return get_user_chroma_dir(session_id)


# def get_user_metadata_file(session_id: str) -> Path:
#     return get_user_base_dir(session_id) / "metadata.json"


# # ---------------------------------------------------------
# # File validation helpers
# # ---------------------------------------------------------

# def is_allowed_file(filename: str) -> bool:
#     if not filename:
#         return False

#     suffix = Path(filename).suffix.lower()

#     return suffix in ALLOWED_FILE_TYPES


# def bytes_to_mb(size_bytes: int) -> float:
#     return round(size_bytes / (1024 * 1024), 2)


# def is_file_size_allowed(size_bytes: int) -> bool:
#     size_mb = bytes_to_mb(size_bytes)

#     return size_mb <= MAX_UPLOAD_SIZE_MB


# def validate_upload_file(
#     filename: str,
#     size_bytes: Optional[int] = None,
# ) -> Dict:
#     if not filename:
#         return {
#             "valid": False,
#             "message": "Filename is missing.",
#         }

#     if not is_allowed_file(filename):
#         return {
#             "valid": False,
#             "message": "Only PDF files are allowed.",
#         }

#     if size_bytes is not None:
#         if not is_file_size_allowed(size_bytes):
#             return {
#                 "valid": False,
#                 "message": f"File size must be less than {MAX_UPLOAD_SIZE_MB} MB.",
#             }

#     return {
#         "valid": True,
#         "message": "File is valid.",
#     }


# # ---------------------------------------------------------
# # Getter helpers
# # ---------------------------------------------------------

# def get_llm_provider() -> str:
#     return LLM_PROVIDER


# def get_groq_api_key() -> str:
#     return GROQ_API_KEY


# def get_groq_model() -> str:
#     return GROQ_MODEL


# def get_groq_temperature() -> float:
#     return GROQ_TEMPERATURE


# def get_groq_max_tokens() -> int:
#     return GROQ_MAX_TOKENS


# def is_groq_configured() -> bool:
#     return bool(GROQ_API_KEY and GROQ_API_KEY.strip())


# def get_backend_llm_model() -> str:
#     if LLM_PROVIDER == "groq":
#         return GROQ_MODEL

#     return DEFAULT_LLM_MODEL


# def get_backend_top_k() -> int:
#     return BACKEND_TOP_K


# def get_backend_search_type() -> str:
#     return BACKEND_SEARCH_TYPE


# def get_backend_answer_mode() -> str:
#     return BACKEND_ANSWER_MODE


# def get_parallel_pdf_workers() -> int:
#     return PARALLEL_PDF_WORKERS


# def should_clear_files_on_app_start() -> bool:
#     return CLEAR_FILES_ON_APP_START


# def should_show_clear_files_button() -> bool:
#     return ENABLE_CLEAR_FILES_BUTTON


# def should_clear_chroma_on_file_clear() -> bool:
#     return CLEAR_CHROMA_ON_FILE_CLEAR


# def get_llm_model(model_type: str = "fast") -> str:
#     if LLM_PROVIDER == "groq":
#         if model_type in AVAILABLE_GROQ_MODELS:
#             return AVAILABLE_GROQ_MODELS[model_type]["name"]

#         return GROQ_MODEL

#     if model_type in AVAILABLE_OLLAMA_MODELS:
#         return AVAILABLE_OLLAMA_MODELS[model_type]["name"]

#     return DEFAULT_LLM_MODEL


# def get_embedding_model(model_type: str = "fast") -> str:
#     if model_type in AVAILABLE_EMBEDDING_MODELS:
#         return AVAILABLE_EMBEDDING_MODELS[model_type]["name"]

#     return DEFAULT_EMBEDDING_MODEL


# def get_available_models() -> Dict:
#     return {
#         "llm_provider": LLM_PROVIDER,
#         "groq_models": AVAILABLE_GROQ_MODELS,
#         "ollama_models": AVAILABLE_OLLAMA_MODELS,
#         "embedding_models": AVAILABLE_EMBEDDING_MODELS,
#         "default_llm": get_backend_llm_model(),
#         "default_embedding": DEFAULT_EMBEDDING_MODEL,
#     }


# def get_config_summary() -> Dict:
#     return {
#         "app_name": APP_NAME,
#         "app_version": APP_VERSION,
#         "env": ENV,
#         "debug": DEBUG,
#         "base_dir": str(BASE_DIR),
#         "project_root": str(PROJECT_ROOT),
#         "root_env_file": str(ROOT_ENV_FILE),
#         "root_env_exists": ROOT_ENV_FILE.exists(),
#         "storage_dir": str(STORAGE_DIR),
#         "users_dir": str(USERS_DIR),
#         "frontend_url": FRONTEND_URL,
#         "backend_url": BACKEND_URL,
#         "cors_allowed_origins": CORS_ALLOWED_ORIGINS,
#         "llm_provider": LLM_PROVIDER,
#         "groq_configured": is_groq_configured(),
#         "groq_model": GROQ_MODEL,
#         "groq_temperature": GROQ_TEMPERATURE,
#         "groq_max_tokens": GROQ_MAX_TOKENS,
#         "ollama_base_url": OLLAMA_BASE_URL,
#         "default_llm_model": get_backend_llm_model(),
#         "llm_temperature": LLM_TEMPERATURE,
#         "llm_max_context_chars": LLM_MAX_CONTEXT_CHARS,
#         "default_embedding_model": DEFAULT_EMBEDDING_MODEL,
#         "embedding_device": EMBEDDING_DEVICE,
#         "normalize_embeddings": NORMALIZE_EMBEDDINGS,
#         "vector_store_type": VECTOR_STORE_TYPE,
#         "chroma_collection_name": CHROMA_COLLECTION_NAME,
#         "chroma_search_type": CHROMA_SEARCH_TYPE,
#         "chroma_top_k": CHROMA_TOP_K,
#         "backend_answer_mode": BACKEND_ANSWER_MODE,
#         "backend_search_type": BACKEND_SEARCH_TYPE,
#         "backend_top_k": BACKEND_TOP_K,
#         "chunk_size": CHUNK_SIZE,
#         "chunk_overlap": CHUNK_OVERLAP,
#         "min_chunk_chars": MIN_CHUNK_CHARS,
#         "enable_ocr": ENABLE_OCR,
#         "ocr_engine": OCR_ENGINE,
#         "ocr_languages": OCR_LANGUAGES,
#         "extract_images_from_pdf": EXTRACT_IMAGES_FROM_PDF,
#         "parallel_pdf_workers": PARALLEL_PDF_WORKERS,
#         "max_upload_size_mb": MAX_UPLOAD_SIZE_MB,
#         "max_pdfs_per_session": MAX_PDFS_PER_SESSION,
#         "clear_files_on_app_start": CLEAR_FILES_ON_APP_START,
#         "enable_clear_files_button": ENABLE_CLEAR_FILES_BUTTON,
#         "clear_chroma_on_file_clear": CLEAR_CHROMA_ON_FILE_CLEAR,
#     }


# def print_config() -> None:
#     summary = get_config_summary()

#     print("\n========== InterviewIQ RAG Backend Config ==========")

#     for key, value in summary.items():
#         print(f"{key}: {value}")

#     print("===================================================\n")


# create_base_folders()


# if __name__ == "__main__":
#     print_config()















import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

SRC_DIR = BASE_DIR / "src"
STORAGE_DIR = BASE_DIR / "storage"
USERS_DIR = STORAGE_DIR / "users"
LOGS_DIR = BASE_DIR / "logs"


# ---------------------------------------------------------
# Load one central env file from project root
# ---------------------------------------------------------
# Root env:
# interviewiq-main/.env.local
# Backend env fallback:
# backend/.env
# ---------------------------------------------------------

ROOT_ENV_FILE = PROJECT_ROOT / ".env.local"
BACKEND_ENV_FILE = BASE_DIR / ".env"

if ROOT_ENV_FILE.exists():
    load_dotenv(dotenv_path=ROOT_ENV_FILE, override=True)
else:
    load_dotenv(dotenv_path=BACKEND_ENV_FILE, override=True)


# ---------------------------------------------------------
# App info
# ---------------------------------------------------------

APP_NAME = "InterviewIQ RAG Backend"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = (
    "Study from uploaded PDF notes using RAG, LangChain, "
    "ChromaDB, local embeddings, and Groq LLM API."
)

ENV = os.getenv("ENV", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
IS_PRODUCTION = ENV.lower() == "production"


# ---------------------------------------------------------
# Backend / API config
# ---------------------------------------------------------

API_TITLE = "InterviewIQ RAG Backend API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "API for PDF upload, RAG retrieval, flashcards, and resume gap analysis."

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
).split(",")

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in CORS_ALLOWED_ORIGINS
    if origin.strip()
]

if FRONTEND_URL not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_URL)


# ---------------------------------------------------------
# RAG behavior config
# ---------------------------------------------------------

# Default answer mode should be "rag" so the stronger detailed RAG prompt is used.
BACKEND_ANSWER_MODE = os.getenv("BACKEND_ANSWER_MODE", "rag")

# MMR gives better variety of chunks than pure similarity.
BACKEND_SEARCH_TYPE = os.getenv("BACKEND_SEARCH_TYPE", "mmr")

# More chunks = better detailed answers.
BACKEND_TOP_K = int(os.getenv("BACKEND_TOP_K", "10"))

PARALLEL_PDF_WORKERS = int(os.getenv("PARALLEL_PDF_WORKERS", "4"))


# ---------------------------------------------------------
# Clear / reset behavior
# ---------------------------------------------------------

CLEAR_FILES_ON_APP_START = os.getenv(
    "CLEAR_FILES_ON_APP_START",
    "false",
).lower() == "true"

ENABLE_CLEAR_FILES_BUTTON = os.getenv(
    "ENABLE_CLEAR_FILES_BUTTON",
    "true",
).lower() == "true"

CLEAR_CHROMA_ON_FILE_CLEAR = os.getenv(
    "CLEAR_CHROMA_ON_FILE_CLEAR",
    "true",
).lower() == "true"


# ---------------------------------------------------------
# LLM provider config
# ---------------------------------------------------------

# Groq only.
LLM_PROVIDER = "groq"


# ---------------------------------------------------------
# Groq config
# ---------------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.1-8b-instant",
)

AVAILABLE_GROQ_MODELS = {
    "fast": {
        "name": "llama-3.1-8b-instant",
        "description": "Fast and good for demo/deployment.",
    },
    "balanced": {
        "name": "llama-3.3-70b-versatile",
        "description": "Better quality for detailed explanations.",
    },
    "gemma": {
        "name": "gemma2-9b-it",
        "description": "Good open model option on Groq.",
    },
}

GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.2"))

# Increased for detailed explanations.
# Old value 900 was too short.
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "2200"))


DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", GROQ_MODEL)

LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", str(GROQ_TEMPERATURE)))
LLM_TOP_K = int(os.getenv("LLM_TOP_K", str(BACKEND_TOP_K)))

# Increased because detailed RAG needs more retrieved context.
LLM_MAX_CONTEXT_CHARS = int(os.getenv("LLM_MAX_CONTEXT_CHARS", "30000"))


# ---------------------------------------------------------
# Embeddings config
# ---------------------------------------------------------

DEFAULT_EMBEDDING_MODEL = os.getenv(
    "DEFAULT_EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

AVAILABLE_EMBEDDING_MODELS = {
    "fast": {
        "name": "sentence-transformers/all-MiniLM-L6-v2",
        "description": "Small, fast, CPU friendly, best for deployment demo.",
    },
    "balanced": {
        "name": "BAAI/bge-small-en-v1.5",
        "description": "Good balance between speed and accuracy.",
    },
    "accurate": {
        "name": "sentence-transformers/all-mpnet-base-v2",
        "description": "Better accuracy, heavier model.",
    },
}

EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")
NORMALIZE_EMBEDDINGS = os.getenv("NORMALIZE_EMBEDDINGS", "true").lower() == "true"


# ---------------------------------------------------------
# Vector DB config
# ---------------------------------------------------------

VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "chroma").lower()

CHROMA_COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION_NAME",
    "rag_interview_notes",
)

CHROMA_SEARCH_TYPE = os.getenv("CHROMA_SEARCH_TYPE", BACKEND_SEARCH_TYPE)
CHROMA_TOP_K = int(os.getenv("CHROMA_TOP_K", str(BACKEND_TOP_K)))


# ---------------------------------------------------------
# File upload config
# ---------------------------------------------------------

ALLOWED_FILE_TYPES = [".pdf"]

MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
MAX_PDFS_PER_SESSION = int(os.getenv("MAX_PDFS_PER_SESSION", "10"))

PDF_TEXT_MAX_CHARS_PER_PAGE = int(
    os.getenv("PDF_TEXT_MAX_CHARS_PER_PAGE", "15000")
)

EXTRACT_IMAGES_FROM_PDF = os.getenv(
    "EXTRACT_IMAGES_FROM_PDF",
    "false",
).lower() == "true"

ENABLE_OCR = os.getenv("ENABLE_OCR", "false").lower() == "true"


# ---------------------------------------------------------
# OCR config
# ---------------------------------------------------------

OCR_ENGINE = os.getenv("OCR_ENGINE", "none")
OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "en").split(",")
OCR_USE_GPU = os.getenv("OCR_USE_GPU", "false").lower() == "true"
OCR_PREPROCESS_IMAGE = os.getenv("OCR_PREPROCESS_IMAGE", "true").lower() == "true"


# ---------------------------------------------------------
# Chunking config
# ---------------------------------------------------------

# Increased chunk size and overlap for deeper explanations.
# Old:
# CHUNK_SIZE = 900
# CHUNK_OVERLAP = 150
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "250"))
MIN_CHUNK_CHARS = int(os.getenv("MIN_CHUNK_CHARS", "80"))


# ---------------------------------------------------------
# Old Streamlit config kept for compatibility
# ---------------------------------------------------------

STREAMLIT_PAGE_TITLE = "Study From Notes - RAG Interview Assistant"
STREAMLIT_PAGE_ICON = "📚"
STREAMLIT_LAYOUT = "wide"


# ---------------------------------------------------------
# Folder helpers
# ---------------------------------------------------------

def create_base_folders() -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    USERS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def get_user_base_dir(session_id: str) -> Path:
    return USERS_DIR / str(session_id)


def get_user_pdf_dir(session_id: str) -> Path:
    return get_user_base_dir(session_id) / "pdfs"


def get_user_image_dir(session_id: str) -> Path:
    return get_user_base_dir(session_id) / "images"


def get_user_chroma_dir(session_id: str) -> Path:
    return get_user_base_dir(session_id) / "chroma_db"


def get_user_vector_dir(session_id: str) -> Path:
    return get_user_chroma_dir(session_id)


def get_user_metadata_file(session_id: str) -> Path:
    return get_user_base_dir(session_id) / "metadata.json"


# ---------------------------------------------------------
# File validation helpers
# ---------------------------------------------------------

def is_allowed_file(filename: str) -> bool:
    if not filename:
        return False

    suffix = Path(filename).suffix.lower()

    return suffix in ALLOWED_FILE_TYPES


def bytes_to_mb(size_bytes: int) -> float:
    return round(size_bytes / (1024 * 1024), 2)


def is_file_size_allowed(size_bytes: int) -> bool:
    size_mb = bytes_to_mb(size_bytes)

    return size_mb <= MAX_UPLOAD_SIZE_MB


def validate_upload_file(
    filename: str,
    size_bytes: Optional[int] = None,
) -> Dict:
    if not filename:
        return {
            "valid": False,
            "message": "Filename is missing.",
        }

    if not is_allowed_file(filename):
        return {
            "valid": False,
            "message": "Only PDF files are allowed.",
        }

    if size_bytes is not None:
        if not is_file_size_allowed(size_bytes):
            return {
                "valid": False,
                "message": f"File size must be less than {MAX_UPLOAD_SIZE_MB} MB.",
            }

    return {
        "valid": True,
        "message": "File is valid.",
    }


# ---------------------------------------------------------
# Getter helpers
# ---------------------------------------------------------

def get_llm_provider() -> str:
    return LLM_PROVIDER


def get_groq_api_key() -> str:
    return GROQ_API_KEY


def get_groq_model() -> str:
    return GROQ_MODEL


def get_groq_temperature() -> float:
    return GROQ_TEMPERATURE


def get_groq_max_tokens() -> int:
    return GROQ_MAX_TOKENS


def is_groq_configured() -> bool:
    return bool(GROQ_API_KEY and GROQ_API_KEY.strip())


def get_backend_llm_model() -> str:
    return GROQ_MODEL


def get_backend_top_k() -> int:
    return BACKEND_TOP_K


def get_backend_search_type() -> str:
    return BACKEND_SEARCH_TYPE


def get_backend_answer_mode() -> str:
    return BACKEND_ANSWER_MODE


def get_parallel_pdf_workers() -> int:
    return PARALLEL_PDF_WORKERS


def should_clear_files_on_app_start() -> bool:
    return CLEAR_FILES_ON_APP_START


def should_show_clear_files_button() -> bool:
    return ENABLE_CLEAR_FILES_BUTTON


def should_clear_chroma_on_file_clear() -> bool:
    return CLEAR_CHROMA_ON_FILE_CLEAR


def get_llm_model(model_type: str = "fast") -> str:
    if model_type in AVAILABLE_GROQ_MODELS:
        return AVAILABLE_GROQ_MODELS[model_type]["name"]

    return GROQ_MODEL


def get_embedding_model(model_type: str = "fast") -> str:
    if model_type in AVAILABLE_EMBEDDING_MODELS:
        return AVAILABLE_EMBEDDING_MODELS[model_type]["name"]

    return DEFAULT_EMBEDDING_MODEL


def get_available_models() -> Dict:
    return {
        "llm_provider": LLM_PROVIDER,
        "groq_models": AVAILABLE_GROQ_MODELS,
        "embedding_models": AVAILABLE_EMBEDDING_MODELS,
        "default_llm": get_backend_llm_model(),
        "default_embedding": DEFAULT_EMBEDDING_MODEL,
    }


def get_config_summary() -> Dict:
    return {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "env": ENV,
        "debug": DEBUG,
        "base_dir": str(BASE_DIR),
        "project_root": str(PROJECT_ROOT),
        "root_env_file": str(ROOT_ENV_FILE),
        "root_env_exists": ROOT_ENV_FILE.exists(),
        "storage_dir": str(STORAGE_DIR),
        "users_dir": str(USERS_DIR),
        "frontend_url": FRONTEND_URL,
        "backend_url": BACKEND_URL,
        "cors_allowed_origins": CORS_ALLOWED_ORIGINS,
        "llm_provider": LLM_PROVIDER,
        "groq_configured": is_groq_configured(),
        "groq_model": GROQ_MODEL,
        "groq_temperature": GROQ_TEMPERATURE,
        "groq_max_tokens": GROQ_MAX_TOKENS,
        "default_llm_model": get_backend_llm_model(),
        "llm_temperature": LLM_TEMPERATURE,
        "llm_top_k": LLM_TOP_K,
        "llm_max_context_chars": LLM_MAX_CONTEXT_CHARS,
        "default_embedding_model": DEFAULT_EMBEDDING_MODEL,
        "embedding_device": EMBEDDING_DEVICE,
        "normalize_embeddings": NORMALIZE_EMBEDDINGS,
        "vector_store_type": VECTOR_STORE_TYPE,
        "chroma_collection_name": CHROMA_COLLECTION_NAME,
        "chroma_search_type": CHROMA_SEARCH_TYPE,
        "chroma_top_k": CHROMA_TOP_K,
        "backend_answer_mode": BACKEND_ANSWER_MODE,
        "backend_search_type": BACKEND_SEARCH_TYPE,
        "backend_top_k": BACKEND_TOP_K,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "min_chunk_chars": MIN_CHUNK_CHARS,
        "pdf_text_max_chars_per_page": PDF_TEXT_MAX_CHARS_PER_PAGE,
        "enable_ocr": ENABLE_OCR,
        "ocr_engine": OCR_ENGINE,
        "ocr_languages": OCR_LANGUAGES,
        "extract_images_from_pdf": EXTRACT_IMAGES_FROM_PDF,
        "parallel_pdf_workers": PARALLEL_PDF_WORKERS,
        "max_upload_size_mb": MAX_UPLOAD_SIZE_MB,
        "max_pdfs_per_session": MAX_PDFS_PER_SESSION,
        "clear_files_on_app_start": CLEAR_FILES_ON_APP_START,
        "enable_clear_files_button": ENABLE_CLEAR_FILES_BUTTON,
        "clear_chroma_on_file_clear": CLEAR_CHROMA_ON_FILE_CLEAR,
    }


def print_config() -> None:
    summary = get_config_summary()

    print("\n========== InterviewIQ RAG Backend Config ==========")

    for key, value in summary.items():
        print(f"{key}: {value}")

    print("===================================================\n")


create_base_folders()


if __name__ == "__main__":
    print_config()