from typing import Dict, List, Optional
import logging
import hashlib
import math
import re

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
# Lightweight embedding settings
# ---------------------------------------------------------

DEFAULT_DEVICE = EMBEDDING_DEVICE

# Small dimension = low memory.
# Keep same dimension always, because Chroma collections expect fixed-size vectors.
LIGHTWEIGHT_EMBEDDING_DIMENSION = 384

_embedding_model_cache: Dict[str, "LightweightHashEmbeddings"] = {}


# ---------------------------------------------------------
# Lightweight embedding model
# ---------------------------------------------------------

class LightweightHashEmbeddings:
    """
    Very lightweight deterministic embedding model.

    This avoids:
    - torch
    - sentence-transformers
    - transformers
    - HuggingFace model loading

    It creates stable hash-based vectors from text tokens.
    Accuracy is lower than semantic embeddings, but it is much safer for
    Render Free / 512 MB RAM deployment.
    """

    def __init__(
        self,
        dimension: int = LIGHTWEIGHT_EMBEDDING_DIMENSION,
        normalize_embeddings: bool = True,
    ):
        self.dimension = int(dimension or LIGHTWEIGHT_EMBEDDING_DIMENSION)
        self.normalize_embeddings = bool(normalize_embeddings)

    def _tokenize(self, text: str) -> List[str]:
        text = clean_text(text).lower()

        if not text:
            return []

        # Words + useful numeric terms
        tokens = re.findall(r"[a-zA-Z0-9]+", text)

        # Add light bigrams for slightly better matching
        if len(tokens) >= 2:
            bigrams = [
                f"{tokens[i]}_{tokens[i + 1]}"
                for i in range(len(tokens) - 1)
            ]
            tokens.extend(bigrams)

        return tokens

    def _hash_token(self, token: str) -> int:
        digest = hashlib.md5(token.encode("utf-8")).hexdigest()
        return int(digest, 16)

    def _embed(self, text: str) -> List[float]:
        vector = [0.0] * self.dimension
        tokens = self._tokenize(text)

        if not tokens:
            return vector

        for token in tokens:
            hashed = self._hash_token(token)
            index = hashed % self.dimension

            # Signed hashing reduces collisions bias
            sign = 1.0 if ((hashed >> 1) % 2 == 0) else -1.0

            # Simple term weighting
            vector[index] += sign

        if self.normalize_embeddings:
            norm = math.sqrt(sum(value * value for value in vector))

            if norm > 0:
                vector = [value / norm for value in vector]

        return vector

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)


# ---------------------------------------------------------
# Model selection helper
# ---------------------------------------------------------

def get_available_embedding_models() -> Dict[str, Dict[str, str]]:
    """
    Return available recommended embedding models.

    Kept same function name for existing code compatibility.
    """

    return {
        "fast": {
            "name": "lightweight-hash-384",
            "description": "Ultra-lightweight hash embeddings for free deployment.",
        },
        "accurate": {
            "name": "lightweight-hash-384",
            "description": "Semantic model disabled for low-memory deployment.",
        },
        "balanced": {
            "name": "lightweight-hash-384",
            "description": "Balanced lightweight hash embeddings.",
        },
    }


def resolve_embedding_model(model_type: str = "fast") -> str:
    """
    Convert simple model type into actual embedding model name.
    """

    models = get_available_embedding_models()

    if model_type in models:
        return models[model_type]["name"]

    return "lightweight-hash-384"


# ---------------------------------------------------------
# Main embedding model loader
# ---------------------------------------------------------

def get_embedding_model(
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    device: str = DEFAULT_DEVICE,
    normalize_embeddings: bool = NORMALIZE_EMBEDDINGS,
) -> LightweightHashEmbeddings:
    """
    Load and return lightweight embedding model.

    Used by vector_store.py and rag_chain.py.

    Note:
    model_name/device are accepted for backward compatibility, but no heavy
    model is loaded.
    """

    safe_model_name = model_name or "lightweight-hash-384"
    safe_device = device or DEFAULT_DEVICE
    safe_normalize = bool(normalize_embeddings)

    cache_key = f"lightweight-hash-384_{safe_device}_{safe_normalize}"

    if cache_key in _embedding_model_cache:
        return _embedding_model_cache[cache_key]

    try:
        logger.info(
            "Loading lightweight hash embedding model "
            f"(requested model: {safe_model_name}, device: {safe_device})"
        )

        embedding_model = LightweightHashEmbeddings(
            dimension=LIGHTWEIGHT_EMBEDDING_DIMENSION,
            normalize_embeddings=safe_normalize,
        )

        _embedding_model_cache[cache_key] = embedding_model

        logger.info("Lightweight embedding model loaded successfully.")

        return embedding_model

    except Exception as e:
        logger.error(f"Failed to load lightweight embedding model: {str(e)}")
        raise RuntimeError(f"Could not load lightweight embedding model. Error: {str(e)}")


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
    Convert multiple text chunks into lightweight embeddings.
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
    Convert user question into lightweight embedding.
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
    Return lightweight embedding model name.
    """

    return "lightweight-hash-384"


def get_embedding_dimension(
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    device: str = DEFAULT_DEVICE,
) -> int:
    """
    Return embedding vector dimension.
    """

    return LIGHTWEIGHT_EMBEDDING_DIMENSION


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
            "model_name": "lightweight-hash-384",
            "requested_model_name": model_name,
            "device": device,
            "dimension": dimension,
            "cached_models": list(_embedding_model_cache.keys()),
            "message": "Lightweight embedding model is working.",
        }

    except Exception as e:
        return {
            "success": False,
            "model_name": "lightweight-hash-384",
            "requested_model_name": model_name,
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
    batch_size: int = 16,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    device: str = DEFAULT_DEVICE,
) -> List[List[float]]:
    """
    Embed chunks in small batches.

    Batch size kept lower for Render Free memory safety.
    """

    cleaned_texts = clean_text_list(texts)

    if not cleaned_texts:
        return []

    safe_batch_size = int(batch_size or 16)

    if safe_batch_size <= 0:
        safe_batch_size = 16

    # Prevent very large in-memory batches on free deployment
    safe_batch_size = min(safe_batch_size, 16)

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
            "model": "lightweight-hash-384",
            "requested_model": DEFAULT_EMBEDDING_MODEL,
            "device": DEFAULT_DEVICE,
            "total_test_texts": len(test_texts),
            "total_embeddings": len(embeddings),
            "embedding_dimension": dimension,
            "similarity_test": similarity_result,
            "cache_info": get_cache_info(),
            "message": "Lightweight embedding self-test completed successfully.",
        }

    except Exception as e:
        return {
            "success": False,
            "model": "lightweight-hash-384",
            "requested_model": DEFAULT_EMBEDDING_MODEL,
            "device": DEFAULT_DEVICE,
            "message": str(e),
        }


# ---------------------------------------------------------
# Direct run test
# ---------------------------------------------------------

if __name__ == "__main__":
    result = run_embedding_self_test()
    print(result)
