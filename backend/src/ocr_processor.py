# from pathlib import Path
# from typing import Dict, List, Optional, Union
# import logging
# import re

# from PIL import Image, ImageEnhance, ImageFilter


# logger = logging.getLogger(__name__)


# # ---------------------------------------------------------
# # Settings
# # ---------------------------------------------------------

# DEFAULT_LANGUAGES = ["en"]

# _easyocr_reader_cache = {}


# # ---------------------------------------------------------
# # Basic helpers
# # ---------------------------------------------------------

# def is_valid_image_path(image_path: Union[str, Path]) -> bool:
#     """
#     Check image path is valid.
#     """

#     if not image_path:
#         return False

#     image_path = Path(image_path)

#     if not image_path.exists():
#         return False

#     if not image_path.is_file():
#         return False

#     allowed_extensions = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]

#     if image_path.suffix.lower() not in allowed_extensions:
#         return False

#     return True


# def clean_ocr_text(text: str) -> str:
#     """
#     Clean OCR extracted text.
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

#         line = re.sub(r"\s+", " ", line)

#         cleaned_lines.append(line)

#     cleaned_text = "\n".join(cleaned_lines).strip()

#     return cleaned_text


# def is_useful_ocr_text(text: str, min_chars: int = 3) -> bool:
#     """
#     Check if OCR text is useful.
#     """

#     if not text:
#         return False

#     text = clean_ocr_text(text)

#     if len(text) < min_chars:
#         return False

#     alpha_numeric_count = sum(ch.isalnum() for ch in text)

#     if alpha_numeric_count < min_chars:
#         return False

#     return True


# # ---------------------------------------------------------
# # Image preprocessing
# # ---------------------------------------------------------

# def preprocess_image_for_ocr(
#     image_path: Union[str, Path],
#     output_path: Optional[Union[str, Path]] = None,
# ) -> Optional[Path]:
#     """
#     Preprocess image before OCR.

#     Steps:
#     - convert to grayscale
#     - increase contrast
#     - sharpen image

#     This improves OCR for PDF diagrams/screenshots.
#     """

#     image_path = Path(image_path)

#     if not is_valid_image_path(image_path):
#         return None

#     try:
#         image = Image.open(image_path)

#         image = image.convert("L")

#         enhancer = ImageEnhance.Contrast(image)
#         image = enhancer.enhance(1.8)

#         image = image.filter(ImageFilter.SHARPEN)

#         if output_path is None:
#             output_path = image_path.with_name(
#                 image_path.stem + "_ocr_preprocessed.png"
#             )

#         output_path = Path(output_path)

#         image.save(output_path)

#         return output_path

#     except Exception as e:
#         logger.warning(f"Image preprocessing failed for {image_path}: {str(e)}")
#         return None


# # ---------------------------------------------------------
# # EasyOCR support
# # ---------------------------------------------------------

# def is_easyocr_available() -> bool:
#     """
#     Check if EasyOCR is installed.
#     """

#     try:
#         import easyocr  # noqa: F401
#         return True
#     except Exception:
#         return False


# def get_easyocr_reader(
#     languages: Optional[List[str]] = None,
#     gpu: bool = False,
# ):
#     """
#     Get cached EasyOCR reader.

#     First run may take time because EasyOCR downloads local model files.
#     """

#     if languages is None:
#         languages = DEFAULT_LANGUAGES

#     cache_key = f"{'-'.join(languages)}_gpu_{gpu}"

#     if cache_key in _easyocr_reader_cache:
#         return _easyocr_reader_cache[cache_key]

#     try:
#         import easyocr

#         reader = easyocr.Reader(
#             languages,
#             gpu=gpu,
#         )

#         _easyocr_reader_cache[cache_key] = reader

#         return reader

#     except Exception as e:
#         logger.warning(f"EasyOCR reader load failed: {str(e)}")
#         return None


# def extract_text_with_easyocr(
#     image_path: Union[str, Path],
#     languages: Optional[List[str]] = None,
#     gpu: bool = False,
#     preprocess: bool = True,
# ) -> str:
#     """
#     Extract text from image using EasyOCR.
#     """

#     image_path = Path(image_path)

#     if not is_valid_image_path(image_path):
#         return ""

#     try:
#         ocr_image_path = image_path

#         if preprocess:
#             processed_path = preprocess_image_for_ocr(image_path)

#             if processed_path:
#                 ocr_image_path = processed_path

#         reader = get_easyocr_reader(
#             languages=languages,
#             gpu=gpu,
#         )

#         if reader is None:
#             return ""

#         results = reader.readtext(str(ocr_image_path))

#         text_parts = []

#         for result in results:
#             # EasyOCR result format:
#             # [bbox, text, confidence]
#             if len(result) >= 2:
#                 detected_text = result[1]
#                 confidence = result[2] if len(result) >= 3 else 1.0

#                 if detected_text and confidence >= 0.25:
#                     text_parts.append(str(detected_text))

#         return clean_ocr_text("\n".join(text_parts))

#     except Exception as e:
#         logger.warning(f"EasyOCR failed for {image_path}: {str(e)}")
#         return ""


# # ---------------------------------------------------------
# # pytesseract support
# # ---------------------------------------------------------

# def is_pytesseract_available() -> bool:
#     """
#     Check if pytesseract is installed and usable.
#     """

#     try:
#         import pytesseract  # noqa: F401
#         return True
#     except Exception:
#         return False


# def extract_text_with_tesseract(
#     image_path: Union[str, Path],
#     preprocess: bool = True,
#     lang: str = "eng",
# ) -> str:
#     """
#     Extract text from image using pytesseract.

#     Windows note:
#     You may need to install Tesseract OCR separately and set path:

#     pytesseract.pytesseract.tesseract_cmd =
#     r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
#     """

#     image_path = Path(image_path)

#     if not is_valid_image_path(image_path):
#         return ""

#     try:
#         import pytesseract

#         ocr_image_path = image_path

#         if preprocess:
#             processed_path = preprocess_image_for_ocr(image_path)

#             if processed_path:
#                 ocr_image_path = processed_path

#         image = Image.open(ocr_image_path)

#         text = pytesseract.image_to_string(
#             image,
#             lang=lang,
#             config="--psm 6",
#         )

#         return clean_ocr_text(text)

#     except Exception as e:
#         logger.warning(f"Tesseract OCR failed for {image_path}: {str(e)}")
#         return ""


# # ---------------------------------------------------------
# # Main OCR function
# # ---------------------------------------------------------

# def extract_text_from_image(
#     image_path: Union[str, Path],
#     engine: str = "auto",
#     languages: Optional[List[str]] = None,
#     gpu: bool = False,
#     preprocess: bool = True,
# ) -> str:
#     """
#     Main function used by pdf_processor.py.

#     Args:
#         image_path:
#             Path of image extracted from PDF.

#         engine:
#             auto, easyocr, tesseract, none

#         languages:
#             For EasyOCR. Default ["en"].

#         gpu:
#             Use GPU for EasyOCR if available.

#         preprocess:
#             Improve image before OCR.

#     Returns:
#         OCR text as string.
#     """

#     image_path = Path(image_path)

#     if not is_valid_image_path(image_path):
#         return ""

#     if engine == "none":
#         return ""

#     if engine == "easyocr":
#         return extract_text_with_easyocr(
#             image_path=image_path,
#             languages=languages,
#             gpu=gpu,
#             preprocess=preprocess,
#         )

#     if engine == "tesseract":
#         return extract_text_with_tesseract(
#             image_path=image_path,
#             preprocess=preprocess,
#         )

#     # Auto mode
#     if is_easyocr_available():
#         text = extract_text_with_easyocr(
#             image_path=image_path,
#             languages=languages,
#             gpu=gpu,
#             preprocess=preprocess,
#         )

#         if is_useful_ocr_text(text):
#             return text

#     if is_pytesseract_available():
#         text = extract_text_with_tesseract(
#             image_path=image_path,
#             preprocess=preprocess,
#         )

#         if is_useful_ocr_text(text):
#             return text

#     return ""


# # ---------------------------------------------------------
# # Batch OCR
# # ---------------------------------------------------------

# def extract_text_from_images(
#     image_paths: List[Union[str, Path]],
#     engine: str = "auto",
#     languages: Optional[List[str]] = None,
#     gpu: bool = False,
#     preprocess: bool = True,
# ) -> List[Dict]:
#     """
#     OCR multiple images.

#     Returns:
#         [
#             {
#                 "image_path": "...",
#                 "success": True,
#                 "text": "..."
#             }
#         ]
#     """

#     results = []

#     for image_path in image_paths:
#         image_path = Path(image_path)

#         if not is_valid_image_path(image_path):
#             results.append(
#                 {
#                     "image_path": str(image_path),
#                     "success": False,
#                     "text": "",
#                     "error": "Invalid image path.",
#                 }
#             )
#             continue

#         try:
#             text = extract_text_from_image(
#                 image_path=image_path,
#                 engine=engine,
#                 languages=languages,
#                 gpu=gpu,
#                 preprocess=preprocess,
#             )

#             results.append(
#                 {
#                     "image_path": str(image_path),
#                     "success": bool(text),
#                     "text": text,
#                     "error": None if text else "No OCR text found.",
#                 }
#             )

#         except Exception as e:
#             results.append(
#                 {
#                     "image_path": str(image_path),
#                     "success": False,
#                     "text": "",
#                     "error": str(e),
#                 }
#             )

#     return results


# def ocr_image_items(
#     image_items: List[Dict],
#     engine: str = "auto",
#     languages: Optional[List[str]] = None,
#     gpu: bool = False,
#     preprocess: bool = True,
# ) -> List[Dict]:
#     """
#     OCR image metadata items from pdf_processor.

#     Input:
#         [
#             {
#                 "image_path": "...",
#                 "page_number": 1,
#                 "pdf_name": "notes.pdf"
#             }
#         ]

#     Output keeps same metadata plus OCR text.
#     """

#     results = []

#     for item in image_items:
#         image_path = item.get("image_path")

#         text = extract_text_from_image(
#             image_path=image_path,
#             engine=engine,
#             languages=languages,
#             gpu=gpu,
#             preprocess=preprocess,
#         )

#         new_item = dict(item)
#         new_item["ocr_text"] = text
#         new_item["ocr_success"] = bool(text)

#         results.append(new_item)

#     return results


# # ---------------------------------------------------------
# # OCR status helpers
# # ---------------------------------------------------------

# def get_ocr_status() -> Dict:
#     """
#     Return OCR availability status.

#     Useful for:
#     - Streamlit sidebar
#     - FastAPI health endpoint
#     """

#     easyocr_available = is_easyocr_available()
#     tesseract_available = is_pytesseract_available()

#     if easyocr_available:
#         preferred_engine = "easyocr"
#     elif tesseract_available:
#         preferred_engine = "tesseract"
#     else:
#         preferred_engine = "none"

#     return {
#         "easyocr_available": easyocr_available,
#         "tesseract_available": tesseract_available,
#         "preferred_engine": preferred_engine,
#         "message": (
#             "OCR available."
#             if preferred_engine != "none"
#             else "OCR not available. Install easyocr or pytesseract."
#         ),
#     }


# def clear_ocr_cache() -> bool:
#     """
#     Clear EasyOCR cached readers.
#     """

#     global _easyocr_reader_cache

#     _easyocr_reader_cache.clear()

#     return True


# # ---------------------------------------------------------
# # Self test
# # ---------------------------------------------------------

# def run_ocr_self_test(image_path: Optional[Union[str, Path]] = None) -> Dict:
#     """
#     Test OCR module.

#     If image_path is not given, only checks OCR engine availability.
#     """

#     status = get_ocr_status()

#     result = {
#         "success": True,
#         "status": status,
#         "test_image": None,
#         "extracted_text": "",
#     }

#     if image_path:
#         image_path = Path(image_path)

#         result["test_image"] = str(image_path)

#         if not is_valid_image_path(image_path):
#             result["success"] = False
#             result["error"] = "Invalid image path."
#             return result

#         text = extract_text_from_image(image_path)

#         result["extracted_text"] = text
#         result["success"] = bool(text)

#     return result


# if __name__ == "__main__":
#     print(run_ocr_self_test())


from pathlib import Path
from typing import Dict, List, Optional, Union
import logging
import re

from PIL import Image, ImageEnhance, ImageFilter

from src.config import (
    OCR_ENGINE,
    OCR_LANGUAGES,
    OCR_USE_GPU,
    OCR_PREPROCESS_IMAGE,
)


logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Settings
# ---------------------------------------------------------

DEFAULT_LANGUAGES = OCR_LANGUAGES or ["en"]

_easyocr_reader_cache = {}


# ---------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------

def is_valid_image_path(image_path: Union[str, Path]) -> bool:
    """
    Check image path is valid.
    """

    if not image_path:
        return False

    image_path = Path(image_path)

    if not image_path.exists():
        return False

    if not image_path.is_file():
        return False

    allowed_extensions = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]

    if image_path.suffix.lower() not in allowed_extensions:
        return False

    return True


def clean_ocr_text(text: str) -> str:
    """
    Clean OCR extracted text.
    """

    if not text:
        return ""

    text = str(text)

    text = text.replace("\x00", " ")
    text = text.replace("\t", " ")
    text = text.replace("\r", "\n")

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        line = re.sub(r"\s+", " ", line)

        cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines).strip()

    return cleaned_text


def is_useful_ocr_text(text: str, min_chars: int = 3) -> bool:
    """
    Check if OCR text is useful.
    """

    if not text:
        return False

    text = clean_ocr_text(text)

    if len(text) < min_chars:
        return False

    alpha_numeric_count = sum(ch.isalnum() for ch in text)

    if alpha_numeric_count < min_chars:
        return False

    return True


# ---------------------------------------------------------
# Image preprocessing
# ---------------------------------------------------------

def preprocess_image_for_ocr(
    image_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
) -> Optional[Path]:
    """
    Preprocess image before OCR.

    Steps:
    - convert to grayscale
    - increase contrast
    - sharpen image
    """

    image_path = Path(image_path)

    if not is_valid_image_path(image_path):
        return None

    try:
        image = Image.open(image_path)

        image = image.convert("L")

        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.8)

        image = image.filter(ImageFilter.SHARPEN)

        if output_path is None:
            output_path = image_path.with_name(
                image_path.stem + "_ocr_preprocessed.png"
            )

        output_path = Path(output_path)

        image.save(output_path)

        return output_path

    except Exception as e:
        logger.warning(f"Image preprocessing failed for {image_path}: {str(e)}")
        return None


# ---------------------------------------------------------
# EasyOCR support
# ---------------------------------------------------------

def is_easyocr_available() -> bool:
    """
    Check if EasyOCR is installed.
    """

    try:
        import easyocr  # noqa: F401

        return True
    except Exception:
        return False


def get_easyocr_reader(
    languages: Optional[List[str]] = None,
    gpu: bool = False,
):
    """
    Get cached EasyOCR reader.

    First run may take time because EasyOCR downloads local model files.
    """

    if languages is None:
        languages = DEFAULT_LANGUAGES

    if not languages:
        languages = ["en"]

    cache_key = f"{'-'.join(languages)}_gpu_{gpu}"

    if cache_key in _easyocr_reader_cache:
        return _easyocr_reader_cache[cache_key]

    try:
        import easyocr

        reader = easyocr.Reader(
            languages,
            gpu=gpu,
        )

        _easyocr_reader_cache[cache_key] = reader

        return reader

    except Exception as e:
        logger.warning(f"EasyOCR reader load failed: {str(e)}")
        return None


def extract_text_with_easyocr(
    image_path: Union[str, Path],
    languages: Optional[List[str]] = None,
    gpu: bool = False,
    preprocess: bool = True,
) -> str:
    """
    Extract text from image using EasyOCR.
    """

    image_path = Path(image_path)

    if not is_valid_image_path(image_path):
        return ""

    try:
        ocr_image_path = image_path

        if preprocess:
            processed_path = preprocess_image_for_ocr(image_path)

            if processed_path:
                ocr_image_path = processed_path

        reader = get_easyocr_reader(
            languages=languages,
            gpu=gpu,
        )

        if reader is None:
            return ""

        results = reader.readtext(str(ocr_image_path))

        text_parts = []

        for result in results:
            if len(result) >= 2:
                detected_text = result[1]
                confidence = result[2] if len(result) >= 3 else 1.0

                if detected_text and confidence >= 0.25:
                    text_parts.append(str(detected_text))

        return clean_ocr_text("\n".join(text_parts))

    except Exception as e:
        logger.warning(f"EasyOCR failed for {image_path}: {str(e)}")
        return ""


# ---------------------------------------------------------
# pytesseract support
# ---------------------------------------------------------

def is_pytesseract_available() -> bool:
    """
    Check if pytesseract is installed and usable.
    """

    try:
        import pytesseract  # noqa: F401

        return True
    except Exception:
        return False


def extract_text_with_tesseract(
    image_path: Union[str, Path],
    preprocess: bool = True,
    lang: str = "eng",
) -> str:
    """
    Extract text from image using pytesseract.

    Windows note:
    You may need to install Tesseract OCR separately and set path:

    pytesseract.pytesseract.tesseract_cmd =
    r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    """

    image_path = Path(image_path)

    if not is_valid_image_path(image_path):
        return ""

    try:
        import pytesseract

        ocr_image_path = image_path

        if preprocess:
            processed_path = preprocess_image_for_ocr(image_path)

            if processed_path:
                ocr_image_path = processed_path

        image = Image.open(ocr_image_path)

        text = pytesseract.image_to_string(
            image,
            lang=lang,
            config="--psm 6",
        )

        return clean_ocr_text(text)

    except Exception as e:
        logger.warning(f"Tesseract OCR failed for {image_path}: {str(e)}")
        return ""


# ---------------------------------------------------------
# Main OCR function
# ---------------------------------------------------------

def extract_text_from_image(
    image_path: Union[str, Path],
    engine: str = OCR_ENGINE,
    languages: Optional[List[str]] = None,
    gpu: bool = OCR_USE_GPU,
    preprocess: bool = OCR_PREPROCESS_IMAGE,
) -> str:
    """
    Main function used by pdf_processor.py.

    Args:
        image_path:
            Path of image extracted from PDF.

        engine:
            auto, easyocr, tesseract, none

        languages:
            For EasyOCR. Default ["en"].

        gpu:
            Use GPU for EasyOCR if available.

        preprocess:
            Improve image before OCR.

    Returns:
        OCR text as string.
    """

    image_path = Path(image_path)

    if not is_valid_image_path(image_path):
        return ""

    safe_engine = (engine or "auto").lower().strip()

    if safe_engine == "none":
        return ""

    if languages is None:
        languages = DEFAULT_LANGUAGES

    if safe_engine == "easyocr":
        return extract_text_with_easyocr(
            image_path=image_path,
            languages=languages,
            gpu=gpu,
            preprocess=preprocess,
        )

    if safe_engine == "tesseract":
        return extract_text_with_tesseract(
            image_path=image_path,
            preprocess=preprocess,
        )

    # Auto mode
    if is_easyocr_available():
        text = extract_text_with_easyocr(
            image_path=image_path,
            languages=languages,
            gpu=gpu,
            preprocess=preprocess,
        )

        if is_useful_ocr_text(text):
            return text

    if is_pytesseract_available():
        text = extract_text_with_tesseract(
            image_path=image_path,
            preprocess=preprocess,
        )

        if is_useful_ocr_text(text):
            return text

    return ""


# ---------------------------------------------------------
# Batch OCR
# ---------------------------------------------------------

def extract_text_from_images(
    image_paths: List[Union[str, Path]],
    engine: str = OCR_ENGINE,
    languages: Optional[List[str]] = None,
    gpu: bool = OCR_USE_GPU,
    preprocess: bool = OCR_PREPROCESS_IMAGE,
) -> List[Dict]:
    """
    OCR multiple images.
    """

    results = []

    if not image_paths:
        return results

    for image_path in image_paths:
        image_path = Path(image_path)

        if not is_valid_image_path(image_path):
            results.append(
                {
                    "image_path": str(image_path),
                    "success": False,
                    "text": "",
                    "error": "Invalid image path.",
                }
            )
            continue

        try:
            text = extract_text_from_image(
                image_path=image_path,
                engine=engine,
                languages=languages,
                gpu=gpu,
                preprocess=preprocess,
            )

            results.append(
                {
                    "image_path": str(image_path),
                    "success": bool(text),
                    "text": text,
                    "error": None if text else "No OCR text found.",
                }
            )

        except Exception as e:
            results.append(
                {
                    "image_path": str(image_path),
                    "success": False,
                    "text": "",
                    "error": str(e),
                }
            )

    return results


def ocr_image_items(
    image_items: List[Dict],
    engine: str = OCR_ENGINE,
    languages: Optional[List[str]] = None,
    gpu: bool = OCR_USE_GPU,
    preprocess: bool = OCR_PREPROCESS_IMAGE,
) -> List[Dict]:
    """
    OCR image metadata items from pdf_processor.
    """

    results = []

    if not image_items:
        return results

    for item in image_items:
        image_path = item.get("image_path")

        text = extract_text_from_image(
            image_path=image_path,
            engine=engine,
            languages=languages,
            gpu=gpu,
            preprocess=preprocess,
        )

        new_item = dict(item)
        new_item["ocr_text"] = text
        new_item["ocr_success"] = bool(text)

        results.append(new_item)

    return results


# ---------------------------------------------------------
# OCR status helpers
# ---------------------------------------------------------

def get_ocr_status() -> Dict:
    """
    Return OCR availability status.
    """

    easyocr_available = is_easyocr_available()
    tesseract_available = is_pytesseract_available()

    configured_engine = (OCR_ENGINE or "none").lower().strip()

    if configured_engine == "none":
        preferred_engine = "none"
    elif configured_engine in ["easyocr", "tesseract", "auto"]:
        preferred_engine = configured_engine
    elif easyocr_available:
        preferred_engine = "easyocr"
    elif tesseract_available:
        preferred_engine = "tesseract"
    else:
        preferred_engine = "none"

    return {
        "easyocr_available": easyocr_available,
        "tesseract_available": tesseract_available,
        "configured_engine": configured_engine,
        "preferred_engine": preferred_engine,
        "languages": DEFAULT_LANGUAGES,
        "gpu": OCR_USE_GPU,
        "preprocess": OCR_PREPROCESS_IMAGE,
        "message": (
            "OCR available."
            if preferred_engine != "none"
            else "OCR not enabled or OCR library not available."
        ),
    }


def clear_ocr_cache() -> bool:
    """
    Clear EasyOCR cached readers.
    """

    global _easyocr_reader_cache

    _easyocr_reader_cache.clear()

    return True


# ---------------------------------------------------------
# Self test
# ---------------------------------------------------------

def run_ocr_self_test(image_path: Optional[Union[str, Path]] = None) -> Dict:
    """
    Test OCR module.

    If image_path is not given, only checks OCR engine availability.
    """

    status = get_ocr_status()

    result = {
        "success": True,
        "status": status,
        "test_image": None,
        "extracted_text": "",
    }

    if image_path:
        image_path = Path(image_path)

        result["test_image"] = str(image_path)

        if not is_valid_image_path(image_path):
            result["success"] = False
            result["error"] = "Invalid image path."
            return result

        text = extract_text_from_image(image_path)

        result["extracted_text"] = text
        result["success"] = bool(text)

    return result


if __name__ == "__main__":
    print(run_ocr_self_test())