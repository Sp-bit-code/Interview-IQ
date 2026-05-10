# from typing import Dict, List, Optional, Union
# import logging

# from langchain_huggingface import HuggingFaceEmbeddings


# # ---------------------------------------------------------
# # Logging setup
# # ---------------------------------------------------------

# logger = logging.getLogger(__name__)


# # ---------------------------------------------------------
# # Default model settings
# # ---------------------------------------------------------

# DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# # Use CPU by default because this project should be deployable.
# # Later, if GPU is available, change to "cuda".
# DEFAULT_DEVICE = "cpu"

# # Cache model so it is not loaded again and again.
# _embedding_model_cache: Dict[str, HuggingFaceEmbeddings] = {}


# # ---------------------------------------------------------
# # Model selection helper
# # ---------------------------------------------------------

# def get_available_embedding_models() -> Dict[str, Dict[str, str]]:
#     """
#     Return available recommended embedding models.

#     This is useful for:
#     - Streamlit dropdown
#     - FastAPI model status endpoint
#     - Future settings page
#     """

#     return {
#         "fast": {
#             "name": "sentence-transformers/all-MiniLM-L6-v2",
#             "description": "Fast, small, CPU friendly, best for deployment demo.",
#         },
#         "accurate": {
#             "name": "sentence-transformers/all-mpnet-base-v2",
#             "description": "Better accuracy, heavier than MiniLM.",
#         },
#         "balanced": {
#             "name": "BAAI/bge-small-en-v1.5",
#             "description": "Good balance of accuracy and speed.",
#         },
#     }


# def resolve_embedding_model(model_type: str = "fast") -> str:
#     """
#     Convert simple model type into actual HuggingFace model name.

#     Example:
#         resolve_embedding_model("fast")
#         -> sentence-transformers/all-MiniLM-L6-v2
#     """

#     models = get_available_embedding_models()

#     if model_type in models:
#         return models[model_type]["name"]

#     return DEFAULT_EMBEDDING_MODEL


# # ---------------------------------------------------------
# # Main embedding model loader
# # ---------------------------------------------------------

# def get_embedding_model(
#     model_name: str = DEFAULT_EMBEDDING_MODEL,
#     device: str = DEFAULT_DEVICE,
#     normalize_embeddings: bool = True,
# ) -> HuggingFaceEmbeddings:
#     """
#     Load and return local embedding model.

#     This function is used by ChromaDB in vector_store.py and rag_chain.py.

#     Args:
#         model_name:
#             HuggingFace embedding model name.

#         device:
#             "cpu" or "cuda".

#         normalize_embeddings:
#             True is good for similarity search.

#     Returns:
#         HuggingFaceEmbeddings object.
#     """

#     cache_key = f"{model_name}_{device}_{normalize_embeddings}"

#     if cache_key in _embedding_model_cache:
#         return _embedding_model_cache[cache_key]

#     try:
#         logger.info(f"Loading embedding model: {model_name} on {device}")

#         embedding_model = HuggingFaceEmbeddings(
#             model_name=model_name,
#             model_kwargs={
#                 "device": device,
#             },
#             encode_kwargs={
#                 "normalize_embeddings": normalize_embeddings,
#             },
#         )

#         _embedding_model_cache[cache_key] = embedding_model

#         logger.info("Embedding model loaded successfully.")

#         return embedding_model

#     except Exception as e:
#         logger.error(f"Failed to load embedding model: {str(e)}")
#         raise RuntimeError(
#             f"Could not load embedding model '{model_name}'. Error: {str(e)}"
#         )


# # ---------------------------------------------------------
# # Embed multiple texts
# # ---------------------------------------------------------

# def embed_texts(
#     texts: List[str],
#     model_name: str = DEFAULT_EMBEDDING_MODEL,
#     device: str = DEFAULT_DEVICE,
# ) -> List[List[float]]:
#     """
#     Convert multiple text chunks into embeddings.

#     Mostly used for testing.
#     ChromaDB usually calls embedding model automatically.

#     Args:
#         texts:
#             List of text chunks.

#     Returns:
#         List of embeddings.
#     """

#     cleaned_texts = clean_text_list(texts)

#     if not cleaned_texts:
#         return []

#     try:
#         embedding_model = get_embedding_model(
#             model_name=model_name,
#             device=device,
#         )

#         embeddings = embedding_model.embed_documents(cleaned_texts)

#         return embeddings

#     except Exception as e:
#         logger.error(f"Error while embedding texts: {str(e)}")
#         raise RuntimeError(f"Text embedding failed: {str(e)}")


# # ---------------------------------------------------------
# # Embed single query
# # ---------------------------------------------------------

# def embed_query(
#     query: str,
#     model_name: str = DEFAULT_EMBEDDING_MODEL,
#     device: str = DEFAULT_DEVICE,
# ) -> Optional[List[float]]:
#     """
#     Convert user question into embedding.

#     Mostly used for testing.
#     LangChain retriever normally handles query embedding automatically.

#     Args:
#         query:
#             User question.

#     Returns:
#         Embedding vector or None.
#     """

#     if not query or not query.strip():
#         return None

#     try:
#         embedding_model = get_embedding_model(
#             model_name=model_name,
#             device=device,
#         )

#         return embedding_model.embed_query(query.strip())

#     except Exception as e:
#         logger.error(f"Error while embedding query: {str(e)}")
#         raise RuntimeError(f"Query embedding failed: {str(e)}")


# # ---------------------------------------------------------
# # Text cleaning helpers
# # ---------------------------------------------------------

# def clean_text(text: str) -> str:
#     """
#     Clean one text before embedding.

#     This removes:
#     - extra spaces
#     - empty lines
#     - broken newlines
#     """

#     if not text:
#         return ""

#     text = str(text)
#     text = text.replace("\x00", " ")
#     text = text.replace("\t", " ")
#     text = text.replace("\r", " ")
#     text = text.replace("\n", " ")

#     while "  " in text:
#         text = text.replace("  ", " ")

#     return text.strip()


# def clean_text_list(texts: List[str]) -> List[str]:
#     """
#     Clean multiple text chunks.

#     Empty chunks are removed.
#     """

#     if not texts:
#         return []

#     cleaned = []

#     for text in texts:
#         cleaned_text = clean_text(text)

#         if cleaned_text:
#             cleaned.append(cleaned_text)

#     return cleaned


# # ---------------------------------------------------------
# # Validation helpers
# # ---------------------------------------------------------

# def is_valid_text(text: str, min_length: int = 3) -> bool:
#     """
#     Check whether text is valid for embedding.
#     """

#     if not text:
#         return False

#     if len(text.strip()) < min_length:
#         return False

#     return True


# def is_valid_text_list(texts: List[str]) -> bool:
#     """
#     Check whether list has at least one valid text.
#     """

#     if not texts:
#         return False

#     for text in texts:
#         if is_valid_text(text):
#             return True

#     return False


# # ---------------------------------------------------------
# # Model info helpers
# # ---------------------------------------------------------

# def get_embedding_model_name() -> str:
#     """
#     Return default embedding model name.
#     """

#     return DEFAULT_EMBEDDING_MODEL


# def get_embedding_dimension(
#     model_name: str = DEFAULT_EMBEDDING_MODEL,
#     device: str = DEFAULT_DEVICE,
# ) -> int:
#     """
#     Return embedding vector dimension.

#     For all-MiniLM-L6-v2, dimension is usually 384.
#     This function calculates it dynamically.
#     """

#     try:
#         sample_embedding = embed_query(
#             "test sentence",
#             model_name=model_name,
#             device=device,
#         )

#         if sample_embedding:
#             return len(sample_embedding)

#         return 0

#     except Exception:
#         return 0


# def get_embedding_status(
#     model_name: str = DEFAULT_EMBEDDING_MODEL,
#     device: str = DEFAULT_DEVICE,
# ) -> Dict:
#     """
#     Return embedding model status.

#     Useful for:
#     - Streamlit sidebar
#     - FastAPI health endpoint
#     """

#     try:
#         dimension = get_embedding_dimension(
#             model_name=model_name,
#             device=device,
#         )

#         return {
#             "success": True,
#             "model_name": model_name,
#             "device": device,
#             "dimension": dimension,
#             "message": "Embedding model is working.",
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "model_name": model_name,
#             "device": device,
#             "dimension": 0,
#             "message": str(e),
#         }


# # ---------------------------------------------------------
# # Cache helpers
# # ---------------------------------------------------------

# def clear_embedding_cache() -> bool:
#     """
#     Clear cached embedding models.

#     Useful when:
#     - changing model
#     - debugging
#     - freeing memory
#     """

#     global _embedding_model_cache

#     _embedding_model_cache.clear()

#     return True


# def get_cache_info() -> Dict:
#     """
#     Return information about cached models.
#     """

#     return {
#         "cached_models": list(_embedding_model_cache.keys()),
#         "total_cached": len(_embedding_model_cache),
#     }


# # ---------------------------------------------------------
# # Batch embedding helper
# # ---------------------------------------------------------

# def embed_texts_in_batches(
#     texts: List[str],
#     batch_size: int = 32,
#     model_name: str = DEFAULT_EMBEDDING_MODEL,
#     device: str = DEFAULT_DEVICE,
# ) -> List[List[float]]:
#     """
#     Embed large number of chunks in batches.

#     Useful if uploaded PDFs are large.

#     Args:
#         texts:
#             List of chunks.

#         batch_size:
#             Number of chunks per batch.

#     Returns:
#         All embeddings.
#     """

#     cleaned_texts = clean_text_list(texts)

#     if not cleaned_texts:
#         return []

#     all_embeddings = []

#     embedding_model = get_embedding_model(
#         model_name=model_name,
#         device=device,
#     )

#     for i in range(0, len(cleaned_texts), batch_size):
#         batch = cleaned_texts[i:i + batch_size]

#         batch_embeddings = embedding_model.embed_documents(batch)

#         all_embeddings.extend(batch_embeddings)

#     return all_embeddings


# # ---------------------------------------------------------
# # Similarity helper
# # ---------------------------------------------------------

# def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
#     """
#     Calculate cosine similarity between two vectors.

#     This is mainly for testing/debugging.
#     ChromaDB handles similarity search internally.
#     """

#     if not vec1 or not vec2:
#         return 0.0

#     if len(vec1) != len(vec2):
#         return 0.0

#     dot_product = sum(a * b for a, b in zip(vec1, vec2))

#     norm1 = sum(a * a for a in vec1) ** 0.5
#     norm2 = sum(b * b for b in vec2) ** 0.5

#     if norm1 == 0 or norm2 == 0:
#         return 0.0

#     return dot_product / (norm1 * norm2)


# def compare_text_similarity(
#     text1: str,
#     text2: str,
#     model_name: str = DEFAULT_EMBEDDING_MODEL,
#     device: str = DEFAULT_DEVICE,
# ) -> Dict:
#     """
#     Compare similarity between two texts.

#     Useful for testing embedding quality.
#     """

#     if not is_valid_text(text1) or not is_valid_text(text2):
#         return {
#             "success": False,
#             "similarity": 0.0,
#             "message": "Invalid text input.",
#         }

#     try:
#         emb1 = embed_query(text1, model_name=model_name, device=device)
#         emb2 = embed_query(text2, model_name=model_name, device=device)

#         similarity = cosine_similarity(emb1, emb2)

#         return {
#             "success": True,
#             "similarity": similarity,
#             "message": "Similarity calculated successfully.",
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "similarity": 0.0,
#             "message": str(e),
#         }


# # ---------------------------------------------------------
# # Test function
# # ---------------------------------------------------------

# def test_embedding_model(
#     model_name: str = DEFAULT_EMBEDDING_MODEL,
#     device: str = DEFAULT_DEVICE,
# ) -> bool:
#     """
#     Quick test to check whether embedding model is working.
#     """

#     try:
#         embedding = embed_query(
#             "What is machine learning?",
#             model_name=model_name,
#             device=device,
#         )

#         if embedding and len(embedding) > 0:
#             return True

#         return False

#     except Exception:
#         return False


# def run_embedding_self_test() -> Dict:
#     """
#     Full self-test for embedding module.

#     You can call this from:
#     - scripts/test_rag.py
#     - Streamlit debug button
#     - FastAPI health check
#     """

#     try:
#         test_texts = [
#             "Machine learning is a branch of artificial intelligence.",
#             "Database management system stores and manages data.",
#             "Operating system manages computer hardware and software resources.",
#         ]

#         embeddings = embed_texts(test_texts)

#         query_embedding = embed_query("What is DBMS?")

#         dimension = len(query_embedding) if query_embedding else 0

#         similarity_result = compare_text_similarity(
#             "Machine learning is part of AI.",
#             "Artificial intelligence includes machine learning.",
#         )

#         return {
#             "success": True,
#             "model": DEFAULT_EMBEDDING_MODEL,
#             "device": DEFAULT_DEVICE,
#             "total_test_texts": len(test_texts),
#             "total_embeddings": len(embeddings),
#             "embedding_dimension": dimension,
#             "similarity_test": similarity_result,
#             "cache_info": get_cache_info(),
#             "message": "Embedding self-test completed successfully.",
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "model": DEFAULT_EMBEDDING_MODEL,
#             "device": DEFAULT_DEVICE,
#             "message": str(e),
#         }


# # ---------------------------------------------------------
# # Direct run test
# # ---------------------------------------------------------

# if __name__ == "__main__":
#     result = run_embedding_self_test()

#     print(result)
from typing import Dict, List, Optional
import logging

from langchain_huggingface import HuggingFaceEmbeddings

from src.config import (
    DEFAULT_EMBEDDING_MODEL,
    EMBEDDING_DEVICE,
    NORMALIZE_EMBEDDINGS,
)


# ---------------------------------------------------------
# Logging setup
# ---------------------------------------------------------

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Default model settings from config.py
# ---------------------------------------------------------

DEFAULT_DEVICE = EMBEDDING_DEVICE

_embedding_model_cache: Dict[str, HuggingFaceEmbeddings] = {}


# ---------------------------------------------------------
# Model selection helper
# ---------------------------------------------------------

def get_available_embedding_models() -> Dict[str, Dict[str, str]]:
    """
    Return available recommended embedding models.
    """

    return {
        "fast": {
            "name": "sentence-transformers/all-MiniLM-L6-v2",
            "description": "Fast, small, CPU friendly, best for deployment demo.",
        },
        "accurate": {
            "name": "sentence-transformers/all-mpnet-base-v2",
            "description": "Better accuracy, heavier than MiniLM.",
        },
        "balanced": {
            "name": "BAAI/bge-small-en-v1.5",
            "description": "Good balance of accuracy and speed.",
        },
    }


def resolve_embedding_model(model_type: str = "fast") -> str:
    """
    Convert simple model type into actual HuggingFace model name.
    """

    models = get_available_embedding_models()

    if model_type in models:
        return models[model_type]["name"]

    return DEFAULT_EMBEDDING_MODEL


# ---------------------------------------------------------
# Main embedding model loader
# ---------------------------------------------------------

def get_embedding_model(
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    device: str = DEFAULT_DEVICE,
    normalize_embeddings: bool = NORMALIZE_EMBEDDINGS,
) -> HuggingFaceEmbeddings:
    """
    Load and return local embedding model.

    Used by vector_store.py and rag_chain.py.
    """

    safe_model_name = model_name or DEFAULT_EMBEDDING_MODEL
    safe_device = device or DEFAULT_DEVICE
    safe_normalize = bool(normalize_embeddings)

    cache_key = f"{safe_model_name}_{safe_device}_{safe_normalize}"

    if cache_key in _embedding_model_cache:
        return _embedding_model_cache[cache_key]

    try:
        logger.info(f"Loading embedding model: {safe_model_name} on {safe_device}")

        embedding_model = HuggingFaceEmbeddings(
            model_name=safe_model_name,
            model_kwargs={
                "device": safe_device,
            },
            encode_kwargs={
                "normalize_embeddings": safe_normalize,
            },
        )

        _embedding_model_cache[cache_key] = embedding_model

        logger.info("Embedding model loaded successfully.")

        return embedding_model

    except Exception as e:
        logger.error(f"Failed to load embedding model: {str(e)}")
        raise RuntimeError(
            f"Could not load embedding model '{safe_model_name}'. Error: {str(e)}"
        )


# ---------------------------------------------------------
# Text cleaning helpers
# ---------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Clean one text before embedding.
    """

    if not text:
        return ""

    text = str(text)
    text = text.replace("\x00", " ")
    text = text.replace("\t", " ")
    text = text.replace("\r", " ")
    text = text.replace("\n", " ")

    while "  " in text:
        text = text.replace("  ", " ")

    return text.strip()


def clean_text_list(texts: List[str]) -> List[str]:
    """
    Clean multiple text chunks.
    """

    if not texts:
        return []

    cleaned = []

    for text in texts:
        cleaned_text = clean_text(text)

        if cleaned_text:
            cleaned.append(cleaned_text)

    return cleaned


# ---------------------------------------------------------
# Embed multiple texts
# ---------------------------------------------------------

def embed_texts(
    texts: List[str],
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    device: str = DEFAULT_DEVICE,
) -> List[List[float]]:
    """
    Convert multiple text chunks into embeddings.
    """

    cleaned_texts = clean_text_list(texts)

    if not cleaned_texts:
        return []

    try:
        embedding_model = get_embedding_model(
            model_name=model_name,
            device=device,
        )

        embeddings = embedding_model.embed_documents(cleaned_texts)

        return embeddings

    except Exception as e:
        logger.error(f"Error while embedding texts: {str(e)}")
        raise RuntimeError(f"Text embedding failed: {str(e)}")


# ---------------------------------------------------------
# Embed single query
# ---------------------------------------------------------

def embed_query(
    query: str,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    device: str = DEFAULT_DEVICE,
) -> Optional[List[float]]:
    """
    Convert user question into embedding.
    """

    if not query or not query.strip():
        return None

    try:
        embedding_model = get_embedding_model(
            model_name=model_name,
            device=device,
        )

        return embedding_model.embed_query(query.strip())

    except Exception as e:
        logger.error(f"Error while embedding query: {str(e)}")
        raise RuntimeError(f"Query embedding failed: {str(e)}")


# ---------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------

def is_valid_text(text: str, min_length: int = 3) -> bool:
    """
    Check whether text is valid for embedding.
    """

    if not text:
        return False

    if len(str(text).strip()) < min_length:
        return False

    return True


def is_valid_text_list(texts: List[str]) -> bool:
    """
    Check whether list has at least one valid text.
    """

    if not texts:
        return False

    for text in texts:
        if is_valid_text(text):
            return True

    return False


# ---------------------------------------------------------
# Model info helpers
# ---------------------------------------------------------

def get_embedding_model_name() -> str:
    """
    Return default embedding model name.
    """

    return DEFAULT_EMBEDDING_MODEL


def get_embedding_dimension(
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    device: str = DEFAULT_DEVICE,
) -> int:
    """
    Return embedding vector dimension dynamically.
    """

    try:
        sample_embedding = embed_query(
            "test sentence",
            model_name=model_name,
            device=device,
        )

        if sample_embedding:
            return len(sample_embedding)

        return 0

    except Exception:
        return 0


def get_embedding_status(
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    device: str = DEFAULT_DEVICE,
) -> Dict:
    """
    Return embedding model status.
    """

    try:
        dimension = get_embedding_dimension(
            model_name=model_name,
            device=device,
        )

        return {
            "success": True,
            "model_name": model_name,
            "device": device,
            "dimension": dimension,
            "cached_models": list(_embedding_model_cache.keys()),
            "message": "Embedding model is working.",
        }

    except Exception as e:
        return {
            "success": False,
            "model_name": model_name,
            "device": device,
            "dimension": 0,
            "cached_models": list(_embedding_model_cache.keys()),
            "message": str(e),
        }


# ---------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------

def clear_embedding_cache() -> bool:
    """
    Clear cached embedding models.
    """

    global _embedding_model_cache

    _embedding_model_cache.clear()

    return True


def get_cache_info() -> Dict:
    """
    Return information about cached models.
    """

    return {
        "cached_models": list(_embedding_model_cache.keys()),
        "total_cached": len(_embedding_model_cache),
    }


# ---------------------------------------------------------
# Batch embedding helper
# ---------------------------------------------------------

def embed_texts_in_batches(
    texts: List[str],
    batch_size: int = 32,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    device: str = DEFAULT_DEVICE,
) -> List[List[float]]:
    """
    Embed large number of chunks in batches.
    """

    cleaned_texts = clean_text_list(texts)

    if not cleaned_texts:
        return []

    safe_batch_size = int(batch_size or 32)

    if safe_batch_size <= 0:
        safe_batch_size = 32

    all_embeddings = []

    embedding_model = get_embedding_model(
        model_name=model_name,
        device=device,
    )

    for i in range(0, len(cleaned_texts), safe_batch_size):
        batch = cleaned_texts[i:i + safe_batch_size]

        batch_embeddings = embedding_model.embed_documents(batch)

        all_embeddings.extend(batch_embeddings)

    return all_embeddings


# ---------------------------------------------------------
# Similarity helper
# ---------------------------------------------------------

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    """

    if not vec1 or not vec2:
        return 0.0

    if len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))

    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def compare_text_similarity(
    text1: str,
    text2: str,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    device: str = DEFAULT_DEVICE,
) -> Dict:
    """
    Compare similarity between two texts.
    """

    if not is_valid_text(text1) or not is_valid_text(text2):
        return {
            "success": False,
            "similarity": 0.0,
            "message": "Invalid text input.",
        }

    try:
        emb1 = embed_query(text1, model_name=model_name, device=device)
        emb2 = embed_query(text2, model_name=model_name, device=device)

        similarity = cosine_similarity(emb1, emb2)

        return {
            "success": True,
            "similarity": similarity,
            "message": "Similarity calculated successfully.",
        }

    except Exception as e:
        return {
            "success": False,
            "similarity": 0.0,
            "message": str(e),
        }


# ---------------------------------------------------------
# Test functions
# ---------------------------------------------------------

def test_embedding_model(
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    device: str = DEFAULT_DEVICE,
) -> bool:
    """
    Quick test to check whether embedding model is working.
    """

    try:
        embedding = embed_query(
            "What is machine learning?",
            model_name=model_name,
            device=device,
        )

        if embedding and len(embedding) > 0:
            return True

        return False

    except Exception:
        return False


def run_embedding_self_test() -> Dict:
    """
    Full self-test for embedding module.
    """

    try:
        test_texts = [
            "Machine learning is a branch of artificial intelligence.",
            "Database management system stores and manages data.",
            "Operating system manages computer hardware and software resources.",
        ]

        embeddings = embed_texts(test_texts)

        query_embedding = embed_query("What is DBMS?")

        dimension = len(query_embedding) if query_embedding else 0

        similarity_result = compare_text_similarity(
            "Machine learning is part of AI.",
            "Artificial intelligence includes machine learning.",
        )

        return {
            "success": True,
            "model": DEFAULT_EMBEDDING_MODEL,
            "device": DEFAULT_DEVICE,
            "total_test_texts": len(test_texts),
            "total_embeddings": len(embeddings),
            "embedding_dimension": dimension,
            "similarity_test": similarity_result,
            "cache_info": get_cache_info(),
            "message": "Embedding self-test completed successfully.",
        }

    except Exception as e:
        return {
            "success": False,
            "model": DEFAULT_EMBEDDING_MODEL,
            "device": DEFAULT_DEVICE,
            "message": str(e),
        }


# ---------------------------------------------------------
# Direct run test
# ---------------------------------------------------------

if __name__ == "__main__":
    result = run_embedding_self_test()
    print(result)