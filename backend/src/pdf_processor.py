# from pathlib import Path
# from typing import Dict, List, Optional, Tuple
# import logging
# import uuid
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import os
# import gc

# import fitz
# from langchain_core.documents import Document

# from src.session_manager import (
#     get_uploaded_pdfs,
#     get_image_path,
#     mark_pdf_processed,
# )

# from src.config import (
#     ENABLE_OCR,
#     EXTRACT_IMAGES_FROM_PDF,
#     PDF_TEXT_MAX_CHARS_PER_PAGE,
#     STORAGE_DIR,
# )


# logger = logging.getLogger(__name__)

# DEFAULT_MAX_WORKERS = min(4, os.cpu_count() or 2)


# def clean_pdf_text(text: str) -> str:
#     if not text:
#         return ""

#     text = text.replace("\x00", " ")
#     text = text.replace("\t", " ")
#     text = text.replace("\r", "\n")

#     lines = text.splitlines()
#     cleaned_lines = []

#     for line in lines:
#         line = line.strip()

#         if line:
#             cleaned_lines.append(line)

#     return "\n".join(cleaned_lines).strip()


# def is_valid_pdf_path(pdf_path: Path) -> bool:
#     if not pdf_path:
#         return False

#     pdf_path = Path(pdf_path)

#     if not pdf_path.exists():
#         return False

#     if not pdf_path.is_file():
#         return False

#     if pdf_path.suffix.lower() != ".pdf":
#         return False

#     return True


# def safe_page_text(
#     text: str,
#     max_chars: int = PDF_TEXT_MAX_CHARS_PER_PAGE,
# ) -> str:
#     if not text:
#         return ""

#     if len(text) <= max_chars:
#         return text

#     return text[:max_chars]


# def should_use_ocr(enable_ocr: Optional[bool] = None) -> bool:
#     if enable_ocr is None:
#         return ENABLE_OCR

#     return bool(enable_ocr)


# def should_extract_images(extract_images: Optional[bool] = None) -> bool:
#     if extract_images is None:
#         return EXTRACT_IMAGES_FROM_PDF

#     return bool(extract_images)


# def get_pdf_page_count(pdf_path: Path) -> int:
#     if not is_valid_pdf_path(pdf_path):
#         return 0

#     try:
#         with fitz.open(str(pdf_path)) as pdf:
#             return pdf.page_count
#     except Exception as e:
#         logger.error(f"Could not read page count for {pdf_path}: {str(e)}")
#         return 0


# def get_pdf_info(pdf_path: Path) -> Dict:
#     pdf_path = Path(pdf_path)

#     info = {
#         "pdf_name": pdf_path.name,
#         "pdf_path": str(pdf_path),
#         "valid": is_valid_pdf_path(pdf_path),
#         "pages": 0,
#         "metadata": {},
#     }

#     if not info["valid"]:
#         return info

#     try:
#         with fitz.open(str(pdf_path)) as pdf:
#             info["pages"] = pdf.page_count
#             info["metadata"] = pdf.metadata or {}
#     except Exception as e:
#         info["error"] = str(e)

#     return info


# def extract_images_from_page(
#     pdf_doc,
#     page,
#     page_number: int,
#     pdf_name: str,
#     output_dir: Path,
# ) -> List[Dict]:
#     extracted_images = []
#     output_dir.mkdir(parents=True, exist_ok=True)

#     try:
#         image_list = page.get_images(full=True)

#         for image_index, image in enumerate(image_list, start=1):
#             xref = image[0]

#             try:
#                 base_image = pdf_doc.extract_image(xref)

#                 image_bytes = base_image.get("image")
#                 image_ext = base_image.get("ext", "png")

#                 if not image_bytes:
#                     continue

#                 image_filename = (
#                     f"{Path(pdf_name).stem}"
#                     f"_page_{page_number}"
#                     f"_img_{image_index}_{uuid.uuid4().hex[:8]}"
#                     f".{image_ext}"
#                 )

#                 image_path = output_dir / image_filename

#                 with open(image_path, "wb") as img_file:
#                     img_file.write(image_bytes)

#                 extracted_images.append(
#                     {
#                         "image_path": str(image_path),
#                         "page_number": page_number,
#                         "pdf_name": pdf_name,
#                         "image_index": image_index,
#                     }
#                 )

#             except Exception as e:
#                 logger.warning(
#                     f"Could not extract image {image_index} "
#                     f"from {pdf_name} page {page_number}: {str(e)}"
#                 )

#     except Exception as e:
#         logger.warning(
#             f"Could not read images from {pdf_name} page {page_number}: {str(e)}"
#         )

#     return extracted_images


# def run_ocr_on_images(image_items: List[Dict]) -> str:
#     if not image_items:
#         return ""

#     try:
#         from src.ocr_processor import extract_text_from_image
#     except Exception:
#         return ""

#     ocr_parts = []

#     for item in image_items:
#         image_path = item.get("image_path")

#         if not image_path:
#             continue

#         try:
#             ocr_text = extract_text_from_image(image_path)

#             if ocr_text and ocr_text.strip():
#                 ocr_parts.append(
#                     f"[OCR from image on page {item.get('page_number')}]\n"
#                     f"{ocr_text.strip()}"
#                 )

#         except Exception as e:
#             logger.warning(f"OCR failed for image {image_path}: {str(e)}")

#     return "\n\n".join(ocr_parts).strip()


# def extract_page_document(
#     pdf_doc,
#     page,
#     page_number: int,
#     pdf_path: Path,
#     image_output_dir: Path,
#     enable_ocr: Optional[bool] = None,
#     extract_images: Optional[bool] = None,
# ) -> Tuple[Optional[Document], Dict]:
#     pdf_name = pdf_path.name

#     use_ocr = should_use_ocr(enable_ocr)
#     use_images = should_extract_images(extract_images)

#     stats = {
#         "page_number": page_number,
#         "has_text": False,
#         "text_chars": 0,
#         "images": 0,
#         "has_ocr": False,
#         "ocr_chars": 0,
#     }

#     try:
#         raw_text = page.get_text("text")
#         text = clean_pdf_text(raw_text)
#         text = safe_page_text(text)

#         if text:
#             stats["has_text"] = True
#             stats["text_chars"] = len(text)

#         image_items = []

#         if use_images:
#             image_items = extract_images_from_page(
#                 pdf_doc=pdf_doc,
#                 page=page,
#                 page_number=page_number,
#                 pdf_name=pdf_name,
#                 output_dir=image_output_dir,
#             )

#             stats["images"] = len(image_items)

#         ocr_text = ""

#         if use_ocr and image_items:
#             ocr_text = run_ocr_on_images(image_items)

#             if ocr_text:
#                 stats["has_ocr"] = True
#                 stats["ocr_chars"] = len(ocr_text)

#         final_content_parts = []

#         if text:
#             final_content_parts.append(text)

#         if ocr_text:
#             final_content_parts.append(
#                 "\n[Extracted text from images/diagrams]\n" + ocr_text
#             )

#         final_content = "\n\n".join(final_content_parts).strip()

#         if not final_content:
#             return None, stats

#         metadata = {
#             "pdf_name": pdf_name,
#             "source": pdf_name,
#             "pdf_path": str(pdf_path),
#             "page_number": page_number,
#             "page": page_number,
#             "content_type": "pdf_page",
#             "has_text": stats["has_text"],
#             "has_images": stats["images"] > 0,
#             "has_ocr": stats["has_ocr"],
#             "image_count": stats["images"],
#         }

#         document = Document(
#             page_content=final_content,
#             metadata=metadata,
#         )

#         return document, stats

#     except Exception as e:
#         logger.error(
#             f"Failed to extract page {page_number} from {pdf_name}: {str(e)}"
#         )
#         return None, stats


# def process_single_pdf(
#     pdf_path: Path,
#     session_id: Optional[str] = None,
#     image_output_dir: Optional[Path] = None,
#     enable_ocr: Optional[bool] = None,
#     extract_images: Optional[bool] = None,
# ) -> Dict:
#     pdf_path = Path(pdf_path)

#     use_ocr = should_use_ocr(enable_ocr)
#     use_images = should_extract_images(extract_images)

#     if not is_valid_pdf_path(pdf_path):
#         return {
#             "success": False,
#             "pdf_name": pdf_path.name if pdf_path else "unknown",
#             "pdf_path": str(pdf_path),
#             "pages": 0,
#             "documents": [],
#             "stats": {},
#             "error": "Invalid PDF path.",
#         }

#     if image_output_dir is None:
#         if session_id:
#             image_output_dir = get_image_path(session_id)
#         else:
#             image_output_dir = STORAGE_DIR / "temp_images"

#     documents = []

#     stats = {
#         "total_pages": 0,
#         "pages_with_text": 0,
#         "pages_with_images": 0,
#         "pages_with_ocr": 0,
#         "total_images": 0,
#         "total_text_chars": 0,
#         "total_ocr_chars": 0,
#         "empty_pages": 0,
#         "ocr_enabled": use_ocr,
#         "image_extraction_enabled": use_images,
#     }

#     try:
#         with fitz.open(str(pdf_path)) as pdf_doc:
#             total_pages = pdf_doc.page_count
#             stats["total_pages"] = total_pages

#             for page_index in range(total_pages):
#                 page_number = page_index + 1
#                 page = pdf_doc.load_page(page_index)

#                 document, page_stats = extract_page_document(
#                     pdf_doc=pdf_doc,
#                     page=page,
#                     page_number=page_number,
#                     pdf_path=pdf_path,
#                     image_output_dir=image_output_dir,
#                     enable_ocr=use_ocr,
#                     extract_images=use_images,
#                 )

#                 if page_stats.get("has_text"):
#                     stats["pages_with_text"] += 1

#                 if page_stats.get("images", 0) > 0:
#                     stats["pages_with_images"] += 1

#                 if page_stats.get("has_ocr"):
#                     stats["pages_with_ocr"] += 1

#                 stats["total_images"] += page_stats.get("images", 0)
#                 stats["total_text_chars"] += page_stats.get("text_chars", 0)
#                 stats["total_ocr_chars"] += page_stats.get("ocr_chars", 0)

#                 if document:
#                     documents.append(document)
#                 else:
#                     stats["empty_pages"] += 1

#         if session_id:
#             mark_pdf_processed(
#                 session_id=session_id,
#                 pdf_name=pdf_path.name,
#                 pages=stats["total_pages"],
#                 chunks=0,
#             )

#         gc.collect()

#         return {
#             "success": True,
#             "pdf_name": pdf_path.name,
#             "pdf_path": str(pdf_path),
#             "pages": stats["total_pages"],
#             "documents": documents,
#             "stats": stats,
#             "error": None,
#         }

#     except Exception as e:
#         logger.error(f"Failed to process PDF {pdf_path}: {str(e)}")

#         gc.collect()

#         return {
#             "success": False,
#             "pdf_name": pdf_path.name,
#             "pdf_path": str(pdf_path),
#             "pages": 0,
#             "documents": [],
#             "stats": stats,
#             "error": str(e),
#         }


# def process_multiple_pdfs(
#     pdf_paths: List[Path],
#     session_id: Optional[str] = None,
#     enable_ocr: Optional[bool] = None,
#     extract_images: Optional[bool] = None,
#     max_workers: Optional[int] = None,
# ) -> Dict:
#     all_documents = []
#     pdf_results = []

#     total_pages = 0
#     total_images = 0
#     failed_pdfs = []

#     use_ocr = should_use_ocr(enable_ocr)
#     use_images = should_extract_images(extract_images)

#     if max_workers is None:
#         max_workers = DEFAULT_MAX_WORKERS

#     if session_id:
#         image_output_dir = get_image_path(session_id)
#     else:
#         image_output_dir = STORAGE_DIR / "temp_images"

#     pdf_paths = [Path(p) for p in pdf_paths if p and is_valid_pdf_path(Path(p))]

#     if not pdf_paths:
#         return {
#             "success": False,
#             "documents": [],
#             "pdf_results": [],
#             "total_pdfs": 0,
#             "failed_pdfs": [],
#             "total_documents": 0,
#             "total_pages": 0,
#             "total_images": 0,
#             "parallel_workers": 0,
#             "ocr_enabled": use_ocr,
#             "image_extraction_enabled": use_images,
#             "error": "No valid PDF paths provided.",
#         }

#     workers = max(1, min(max_workers, len(pdf_paths), DEFAULT_MAX_WORKERS))

#     if len(pdf_paths) == 1:
#         result = process_single_pdf(
#             pdf_path=pdf_paths[0],
#             session_id=session_id,
#             image_output_dir=image_output_dir,
#             enable_ocr=use_ocr,
#             extract_images=use_images,
#         )

#         pdf_results.append(
#             {
#                 "success": result.get("success"),
#                 "pdf_name": result.get("pdf_name"),
#                 "pdf_path": result.get("pdf_path"),
#                 "pages": result.get("pages"),
#                 "document_count": len(result.get("documents", [])),
#                 "stats": result.get("stats"),
#                 "error": result.get("error"),
#             }
#         )

#         if result.get("success"):
#             all_documents.extend(result.get("documents", []))
#             total_pages += result.get("pages", 0)
#             total_images += result.get("stats", {}).get("total_images", 0)
#         else:
#             failed_pdfs.append(result.get("pdf_name"))

#         return {
#             "success": len(all_documents) > 0,
#             "documents": all_documents,
#             "pdf_results": pdf_results,
#             "total_pdfs": len(pdf_paths),
#             "failed_pdfs": failed_pdfs,
#             "total_documents": len(all_documents),
#             "total_pages": total_pages,
#             "total_images": total_images,
#             "parallel_workers": 1,
#             "ocr_enabled": use_ocr,
#             "image_extraction_enabled": use_images,
#             "error": None,
#         }

#     with ThreadPoolExecutor(max_workers=workers) as executor:
#         future_to_pdf = {
#             executor.submit(
#                 process_single_pdf,
#                 pdf_path,
#                 session_id,
#                 image_output_dir,
#                 use_ocr,
#                 use_images,
#             ): pdf_path
#             for pdf_path in pdf_paths
#         }

#         for future in as_completed(future_to_pdf):
#             pdf_path = future_to_pdf[future]

#             try:
#                 result = future.result()
#             except Exception as e:
#                 result = {
#                     "success": False,
#                     "pdf_name": pdf_path.name,
#                     "pdf_path": str(pdf_path),
#                     "pages": 0,
#                     "documents": [],
#                     "stats": {},
#                     "error": str(e),
#                 }

#             pdf_results.append(
#                 {
#                     "success": result.get("success"),
#                     "pdf_name": result.get("pdf_name"),
#                     "pdf_path": result.get("pdf_path"),
#                     "pages": result.get("pages"),
#                     "document_count": len(result.get("documents", [])),
#                     "stats": result.get("stats"),
#                     "error": result.get("error"),
#                 }
#             )

#             if result.get("success"):
#                 docs = result.get("documents", [])
#                 all_documents.extend(docs)
#                 total_pages += result.get("pages", 0)
#                 total_images += result.get("stats", {}).get("total_images", 0)
#             else:
#                 failed_pdfs.append(result.get("pdf_name"))

#     all_documents.sort(
#         key=lambda doc: (
#             doc.metadata.get("pdf_name", ""),
#             int(doc.metadata.get("page_number", 0)),
#         )
#     )

#     pdf_results.sort(key=lambda item: item.get("pdf_name", ""))

#     gc.collect()

#     return {
#         "success": len(all_documents) > 0,
#         "documents": all_documents,
#         "pdf_results": pdf_results,
#         "total_pdfs": len(pdf_paths),
#         "failed_pdfs": failed_pdfs,
#         "total_documents": len(all_documents),
#         "total_pages": total_pages,
#         "total_images": total_images,
#         "parallel_workers": workers,
#         "ocr_enabled": use_ocr,
#         "image_extraction_enabled": use_images,
#         "error": None,
#     }


# def process_uploaded_pdfs_for_session(
#     session_id: str,
#     enable_ocr: Optional[bool] = None,
#     extract_images: Optional[bool] = None,
#     max_workers: Optional[int] = None,
# ) -> Dict:
#     pdf_paths = get_uploaded_pdfs(session_id)

#     if not pdf_paths:
#         return {
#             "success": False,
#             "documents": [],
#             "pdf_results": [],
#             "total_pdfs": 0,
#             "failed_pdfs": [],
#             "total_documents": 0,
#             "total_pages": 0,
#             "total_images": 0,
#             "parallel_workers": 0,
#             "ocr_enabled": should_use_ocr(enable_ocr),
#             "image_extraction_enabled": should_extract_images(extract_images),
#             "error": "No uploaded PDFs found.",
#         }

#     return process_multiple_pdfs(
#         pdf_paths=pdf_paths,
#         session_id=session_id,
#         enable_ocr=enable_ocr,
#         extract_images=extract_images,
#         max_workers=max_workers,
#     )


# def preview_pdf_text(
#     pdf_path: Path,
#     max_pages: int = 2,
#     max_chars_per_page: int = 1000,
# ) -> Dict:
#     pdf_path = Path(pdf_path)

#     if not is_valid_pdf_path(pdf_path):
#         return {
#             "success": False,
#             "pdf_name": pdf_path.name,
#             "preview": [],
#             "error": "Invalid PDF path.",
#         }

#     preview = []

#     try:
#         with fitz.open(str(pdf_path)) as pdf:
#             pages_to_read = min(pdf.page_count, max_pages)

#             for page_index in range(pages_to_read):
#                 page = pdf.load_page(page_index)
#                 text = clean_pdf_text(page.get_text("text"))

#                 preview.append(
#                     {
#                         "page": page_index + 1,
#                         "text": text[:max_chars_per_page],
#                     }
#                 )

#         return {
#             "success": True,
#             "pdf_name": pdf_path.name,
#             "preview": preview,
#             "error": None,
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "pdf_name": pdf_path.name,
#             "preview": [],
#             "error": str(e),
#         }


# def get_session_pdf_summary(session_id: str) -> Dict:
#     pdf_paths = get_uploaded_pdfs(session_id)

#     pdfs = []

#     for pdf_path in pdf_paths:
#         pdfs.append(get_pdf_info(pdf_path))

#     return {
#         "session_id": session_id,
#         "total_pdfs": len(pdfs),
#         "pdfs": pdfs,
#     }


# def run_pdf_processor_self_test(session_id: str) -> Dict:
#     try:
#         result = process_uploaded_pdfs_for_session(
#             session_id=session_id,
#             enable_ocr=False,
#             extract_images=False,
#             max_workers=DEFAULT_MAX_WORKERS,
#         )

#         return {
#             "success": result.get("success"),
#             "total_pdfs": result.get("total_pdfs"),
#             "total_documents": result.get("total_documents"),
#             "total_pages": result.get("total_pages"),
#             "failed_pdfs": result.get("failed_pdfs"),
#             "parallel_workers": result.get("parallel_workers"),
#             "message": "PDF processor self-test completed.",
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "message": str(e),
#         }


# if __name__ == "__main__":
#     print(
#         "PDF processor module loaded successfully. "
#         "Use process_uploaded_pdfs_for_session(session_id) from main.py."
#     )









from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import gc
import re

import fitz
from langchain_core.documents import Document

from src.session_manager import (
    get_uploaded_pdfs,
    get_image_path,
    mark_pdf_processed,
)

from src.config import (
    ENABLE_OCR,
    EXTRACT_IMAGES_FROM_PDF,
    PDF_TEXT_MAX_CHARS_PER_PAGE,
    STORAGE_DIR,
)


logger = logging.getLogger(__name__)

DEFAULT_MAX_WORKERS = min(4, os.cpu_count() or 2)

# If a page has less text than this, OCR can help if enabled.
MIN_USEFUL_PAGE_TEXT_CHARS = 80


# ---------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------

def clean_pdf_text(text: str) -> str:
    """
    Clean PDF text while preserving useful study structure.

    Important:
    Do not over-clean because headings, bullets, formulas, and line breaks
    help chunking and retrieval.
    """

    if not text:
        return ""

    text = str(text)

    text = text.replace("\x00", " ")
    text = text.replace("\t", " ")
    text = text.replace("\r", "\n")
    text = text.replace("\u00a0", " ")
    text = text.replace("\u200b", "")

    # Fix broken hyphenated words:
    # "classifi-\ncation" -> "classification"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    lines = text.splitlines()
    cleaned_lines = []

    previous_blank = False

    for line in lines:
        line = line.strip()
        line = re.sub(r"[ ]{2,}", " ", line)

        if not line:
            if not previous_blank:
                cleaned_lines.append("")
            previous_blank = True
            continue

        cleaned_lines.append(line)
        previous_blank = False

    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


def is_valid_pdf_path(pdf_path: Path) -> bool:
    if not pdf_path:
        return False

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        return False

    if not pdf_path.is_file():
        return False

    if pdf_path.suffix.lower() != ".pdf":
        return False

    return True


def safe_page_text(
    text: str,
    max_chars: int = PDF_TEXT_MAX_CHARS_PER_PAGE,
) -> str:
    if not text:
        return ""

    if len(text) <= max_chars:
        return text

    return text[:max_chars]


def should_use_ocr(enable_ocr: Optional[bool] = None) -> bool:
    if enable_ocr is None:
        return ENABLE_OCR

    return bool(enable_ocr)


def should_extract_images(extract_images: Optional[bool] = None) -> bool:
    if extract_images is None:
        return EXTRACT_IMAGES_FROM_PDF

    return bool(extract_images)


def get_text_quality_score(text: str) -> Dict:
    """
    Basic text quality stats for debugging poor PDF extraction.
    """

    if not text:
        return {
            "chars": 0,
            "words": 0,
            "lines": 0,
            "alnum_chars": 0,
            "quality": "empty",
        }

    chars = len(text)
    words = len(text.split())
    lines = len([line for line in text.splitlines() if line.strip()])
    alnum_chars = sum(ch.isalnum() for ch in text)

    if chars < MIN_USEFUL_PAGE_TEXT_CHARS:
        quality = "low"
    elif words < 20:
        quality = "medium"
    else:
        quality = "good"

    return {
        "chars": chars,
        "words": words,
        "lines": lines,
        "alnum_chars": alnum_chars,
        "quality": quality,
    }


# ---------------------------------------------------------
# PDF info
# ---------------------------------------------------------

def get_pdf_page_count(pdf_path: Path) -> int:
    if not is_valid_pdf_path(pdf_path):
        return 0

    try:
        with fitz.open(str(pdf_path)) as pdf:
            return pdf.page_count
    except Exception as e:
        logger.error(f"Could not read page count for {pdf_path}: {str(e)}")
        return 0


def get_pdf_info(pdf_path: Path) -> Dict:
    pdf_path = Path(pdf_path)

    info = {
        "pdf_name": pdf_path.name,
        "pdf_path": str(pdf_path),
        "valid": is_valid_pdf_path(pdf_path),
        "pages": 0,
        "metadata": {},
    }

    if not info["valid"]:
        return info

    try:
        with fitz.open(str(pdf_path)) as pdf:
            info["pages"] = pdf.page_count
            info["metadata"] = pdf.metadata or {}
    except Exception as e:
        info["error"] = str(e)

    return info


# ---------------------------------------------------------
# Better text extraction
# ---------------------------------------------------------

def extract_text_by_blocks(page) -> str:
    """
    Extract text using PyMuPDF text blocks.

    This often preserves reading order better than simple page.get_text("text").
    """

    try:
        blocks = page.get_text("blocks") or []

        cleaned_blocks = []

        for block in blocks:
            # PyMuPDF block tuple:
            # (x0, y0, x1, y1, text, block_no, block_type)
            if len(block) < 5:
                continue

            x0, y0, x1, y1, block_text = block[:5]

            if not block_text or not str(block_text).strip():
                continue

            cleaned_blocks.append(
                {
                    "x0": float(x0),
                    "y0": float(y0),
                    "x1": float(x1),
                    "y1": float(y1),
                    "text": str(block_text).strip(),
                }
            )

        # Sort top-to-bottom, then left-to-right
        cleaned_blocks.sort(key=lambda item: (round(item["y0"], 1), round(item["x0"], 1)))

        texts = []

        previous_y = None

        for item in cleaned_blocks:
            text = item["text"].strip()

            if not text:
                continue

            # Add paragraph gap when vertical distance is large
            if previous_y is not None and abs(item["y0"] - previous_y) > 20:
                texts.append("")

            texts.append(text)
            previous_y = item["y1"]

        return clean_pdf_text("\n".join(texts))

    except Exception as e:
        logger.warning(f"Block text extraction failed: {str(e)}")
        return ""


def extract_text_by_words(page) -> str:
    """
    Word-based fallback.

    Useful when normal/block extraction is poor.
    """

    try:
        words = page.get_text("words") or []

        if not words:
            return ""

        # word tuple: x0, y0, x1, y1, word, block_no, line_no, word_no
        words = sorted(words, key=lambda w: (round(w[1], 1), round(w[0], 1)))

        lines = []
        current_line = []
        current_y = None

        for word in words:
            if len(word) < 5:
                continue

            x0, y0, x1, y1, word_text = word[:5]

            if not word_text:
                continue

            if current_y is None:
                current_y = y0

            if abs(y0 - current_y) > 5:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [str(word_text)]
                current_y = y0
            else:
                current_line.append(str(word_text))

        if current_line:
            lines.append(" ".join(current_line))

        return clean_pdf_text("\n".join(lines))

    except Exception as e:
        logger.warning(f"Word text extraction failed: {str(e)}")
        return ""


def extract_best_page_text(page) -> str:
    """
    Try multiple extraction modes and choose the best one.

    Priority:
    1. block extraction if good
    2. normal text extraction
    3. word extraction fallback
    """

    block_text = extract_text_by_blocks(page)
    normal_text = clean_pdf_text(page.get_text("text") or "")
    word_text = extract_text_by_words(page)

    candidates = [block_text, normal_text, word_text]

    valid_candidates = []

    for candidate in candidates:
        candidate = clean_pdf_text(candidate)

        if not candidate:
            continue

        quality = get_text_quality_score(candidate)

        valid_candidates.append(
            {
                "text": candidate,
                "chars": quality["chars"],
                "words": quality["words"],
                "lines": quality["lines"],
                "quality": quality["quality"],
            }
        )

    if not valid_candidates:
        return ""

    # Pick the candidate with more useful words/chars.
    valid_candidates.sort(
        key=lambda item: (
            item["words"],
            item["chars"],
            item["lines"],
        ),
        reverse=True,
    )

    return safe_page_text(valid_candidates[0]["text"])


# ---------------------------------------------------------
# Image / OCR helpers
# ---------------------------------------------------------

def extract_images_from_page(
    pdf_doc,
    page,
    page_number: int,
    pdf_name: str,
    output_dir: Path,
) -> List[Dict]:
    extracted_images = []
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        image_list = page.get_images(full=True)

        for image_index, image in enumerate(image_list, start=1):
            xref = image[0]

            try:
                base_image = pdf_doc.extract_image(xref)

                image_bytes = base_image.get("image")
                image_ext = base_image.get("ext", "png")

                if not image_bytes:
                    continue

                image_filename = (
                    f"{Path(pdf_name).stem}"
                    f"_page_{page_number}"
                    f"_img_{image_index}_{uuid.uuid4().hex[:8]}"
                    f".{image_ext}"
                )

                image_path = output_dir / image_filename

                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)

                extracted_images.append(
                    {
                        "image_path": str(image_path),
                        "page_number": page_number,
                        "pdf_name": pdf_name,
                        "image_index": image_index,
                    }
                )

            except Exception as e:
                logger.warning(
                    f"Could not extract image {image_index} "
                    f"from {pdf_name} page {page_number}: {str(e)}"
                )

    except Exception as e:
        logger.warning(
            f"Could not read images from {pdf_name} page {page_number}: {str(e)}"
        )

    return extracted_images


def render_page_to_image(
    page,
    pdf_name: str,
    page_number: int,
    output_dir: Path,
    zoom: float = 2.0,
) -> Optional[Dict]:
    """
    Render full PDF page to image for OCR fallback.

    Useful for scanned PDFs where page.get_text() gives almost nothing.
    """

    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix, alpha=False)

        image_filename = (
            f"{Path(pdf_name).stem}"
            f"_page_{page_number}"
            f"_fullpage_{uuid.uuid4().hex[:8]}"
            f".png"
        )

        image_path = output_dir / image_filename
        pix.save(str(image_path))

        return {
            "image_path": str(image_path),
            "page_number": page_number,
            "pdf_name": pdf_name,
            "image_index": "full_page",
        }

    except Exception as e:
        logger.warning(
            f"Could not render full page image for OCR "
            f"{pdf_name} page {page_number}: {str(e)}"
        )
        return None


def run_ocr_on_images(image_items: List[Dict]) -> str:
    if not image_items:
        return ""

    try:
        from src.ocr_processor import extract_text_from_image
    except Exception as e:
        logger.warning(f"OCR processor unavailable: {str(e)}")
        return ""

    ocr_parts = []

    for item in image_items:
        image_path = item.get("image_path")

        if not image_path:
            continue

        try:
            ocr_text = extract_text_from_image(image_path)

            if ocr_text and ocr_text.strip():
                ocr_parts.append(
                    f"[OCR from image on page {item.get('page_number')}]\n"
                    f"{ocr_text.strip()}"
                )

        except Exception as e:
            logger.warning(f"OCR failed for image {image_path}: {str(e)}")

    return "\n\n".join(ocr_parts).strip()


# ---------------------------------------------------------
# Page extraction
# ---------------------------------------------------------

def extract_page_document(
    pdf_doc,
    page,
    page_number: int,
    pdf_path: Path,
    image_output_dir: Path,
    enable_ocr: Optional[bool] = None,
    extract_images: Optional[bool] = None,
) -> Tuple[Optional[Document], Dict]:
    pdf_name = pdf_path.name

    use_ocr = should_use_ocr(enable_ocr)
    use_images = should_extract_images(extract_images)

    stats = {
        "page_number": page_number,
        "has_text": False,
        "text_chars": 0,
        "text_words": 0,
        "text_quality": "empty",
        "images": 0,
        "has_ocr": False,
        "ocr_chars": 0,
        "ocr_source": None,
    }

    try:
        text = extract_best_page_text(page)
        text = safe_page_text(clean_pdf_text(text))

        text_quality = get_text_quality_score(text)

        stats["text_chars"] = text_quality["chars"]
        stats["text_words"] = text_quality["words"]
        stats["text_quality"] = text_quality["quality"]

        if text:
            stats["has_text"] = True

        image_items = []

        # Extract embedded images only if enabled.
        if use_images:
            image_items = extract_images_from_page(
                pdf_doc=pdf_doc,
                page=page,
                page_number=page_number,
                pdf_name=pdf_name,
                output_dir=image_output_dir,
            )

            stats["images"] = len(image_items)

        ocr_text = ""

        # OCR embedded images if enabled and images exist.
        if use_ocr and image_items:
            ocr_text = run_ocr_on_images(image_items)

            if ocr_text:
                stats["has_ocr"] = True
                stats["ocr_chars"] = len(ocr_text)
                stats["ocr_source"] = "embedded_images"

        # OCR full page fallback if page text is poor.
        # This helps scanned PDFs/slides.
        if use_ocr and len(text) < MIN_USEFUL_PAGE_TEXT_CHARS:
            full_page_image = render_page_to_image(
                page=page,
                pdf_name=pdf_name,
                page_number=page_number,
                output_dir=image_output_dir,
                zoom=2.0,
            )

            if full_page_image:
                full_page_ocr_text = run_ocr_on_images([full_page_image])

                if full_page_ocr_text:
                    if ocr_text:
                        ocr_text = f"{ocr_text}\n\n{full_page_ocr_text}"
                    else:
                        ocr_text = full_page_ocr_text

                    stats["has_ocr"] = True
                    stats["ocr_chars"] = len(ocr_text)
                    stats["ocr_source"] = "full_page_render"

        final_content_parts = []

        if text:
            final_content_parts.append(text)

        if ocr_text:
            final_content_parts.append(
                "[Extracted text from images/diagrams]\n" + clean_pdf_text(ocr_text)
            )

        final_content = "\n\n".join(final_content_parts).strip()

        if not final_content:
            return None, stats

        metadata = {
            "pdf_name": pdf_name,
            "source": pdf_name,
            "file_name": pdf_name,
            "pdf_path": str(pdf_path),
            "page_number": page_number,
            "page": page_number,
            "content_type": "pdf_page",
            "has_text": stats["has_text"],
            "text_chars": stats["text_chars"],
            "text_words": stats["text_words"],
            "text_quality": stats["text_quality"],
            "has_images": stats["images"] > 0,
            "has_ocr": stats["has_ocr"],
            "ocr_source": stats["ocr_source"],
            "image_count": stats["images"],
        }

        document = Document(
            page_content=final_content,
            metadata=metadata,
        )

        return document, stats

    except Exception as e:
        logger.error(
            f"Failed to extract page {page_number} from {pdf_name}: {str(e)}"
        )
        return None, stats


# ---------------------------------------------------------
# PDF processing
# ---------------------------------------------------------

def process_single_pdf(
    pdf_path: Path,
    session_id: Optional[str] = None,
    image_output_dir: Optional[Path] = None,
    enable_ocr: Optional[bool] = None,
    extract_images: Optional[bool] = None,
) -> Dict:
    pdf_path = Path(pdf_path)

    use_ocr = should_use_ocr(enable_ocr)
    use_images = should_extract_images(extract_images)

    if not is_valid_pdf_path(pdf_path):
        return {
            "success": False,
            "pdf_name": pdf_path.name if pdf_path else "unknown",
            "pdf_path": str(pdf_path),
            "pages": 0,
            "documents": [],
            "stats": {},
            "error": "Invalid PDF path.",
        }

    if image_output_dir is None:
        if session_id:
            image_output_dir = get_image_path(session_id)
        else:
            image_output_dir = STORAGE_DIR / "temp_images"

    documents = []

    stats = {
        "total_pages": 0,
        "pages_with_text": 0,
        "pages_with_good_text": 0,
        "pages_with_low_text": 0,
        "pages_with_images": 0,
        "pages_with_ocr": 0,
        "total_images": 0,
        "total_text_chars": 0,
        "total_text_words": 0,
        "total_ocr_chars": 0,
        "empty_pages": 0,
        "ocr_enabled": use_ocr,
        "image_extraction_enabled": use_images,
    }

    try:
        with fitz.open(str(pdf_path)) as pdf_doc:
            total_pages = pdf_doc.page_count
            stats["total_pages"] = total_pages

            for page_index in range(total_pages):
                page_number = page_index + 1
                page = pdf_doc.load_page(page_index)

                document, page_stats = extract_page_document(
                    pdf_doc=pdf_doc,
                    page=page,
                    page_number=page_number,
                    pdf_path=pdf_path,
                    image_output_dir=image_output_dir,
                    enable_ocr=use_ocr,
                    extract_images=use_images,
                )

                if page_stats.get("has_text"):
                    stats["pages_with_text"] += 1

                if page_stats.get("text_quality") == "good":
                    stats["pages_with_good_text"] += 1

                if page_stats.get("text_quality") in ["low", "empty"]:
                    stats["pages_with_low_text"] += 1

                if page_stats.get("images", 0) > 0:
                    stats["pages_with_images"] += 1

                if page_stats.get("has_ocr"):
                    stats["pages_with_ocr"] += 1

                stats["total_images"] += page_stats.get("images", 0)
                stats["total_text_chars"] += page_stats.get("text_chars", 0)
                stats["total_text_words"] += page_stats.get("text_words", 0)
                stats["total_ocr_chars"] += page_stats.get("ocr_chars", 0)

                if document:
                    documents.append(document)
                else:
                    stats["empty_pages"] += 1

        if session_id:
            mark_pdf_processed(
                session_id=session_id,
                pdf_name=pdf_path.name,
                pages=stats["total_pages"],
                chunks=0,
            )

        gc.collect()

        return {
            "success": True,
            "pdf_name": pdf_path.name,
            "pdf_path": str(pdf_path),
            "pages": stats["total_pages"],
            "documents": documents,
            "stats": stats,
            "error": None,
        }

    except Exception as e:
        logger.error(f"Failed to process PDF {pdf_path}: {str(e)}")

        gc.collect()

        return {
            "success": False,
            "pdf_name": pdf_path.name,
            "pdf_path": str(pdf_path),
            "pages": 0,
            "documents": [],
            "stats": stats,
            "error": str(e),
        }


def process_multiple_pdfs(
    pdf_paths: List[Path],
    session_id: Optional[str] = None,
    enable_ocr: Optional[bool] = None,
    extract_images: Optional[bool] = None,
    max_workers: Optional[int] = None,
) -> Dict:
    all_documents = []
    pdf_results = []

    total_pages = 0
    total_images = 0
    failed_pdfs = []

    use_ocr = should_use_ocr(enable_ocr)
    use_images = should_extract_images(extract_images)

    if max_workers is None:
        max_workers = DEFAULT_MAX_WORKERS

    if session_id:
        image_output_dir = get_image_path(session_id)
    else:
        image_output_dir = STORAGE_DIR / "temp_images"

    pdf_paths = [Path(p) for p in pdf_paths if p and is_valid_pdf_path(Path(p))]

    if not pdf_paths:
        return {
            "success": False,
            "documents": [],
            "pdf_results": [],
            "total_pdfs": 0,
            "failed_pdfs": [],
            "total_documents": 0,
            "total_pages": 0,
            "total_images": 0,
            "parallel_workers": 0,
            "ocr_enabled": use_ocr,
            "image_extraction_enabled": use_images,
            "error": "No valid PDF paths provided.",
        }

    workers = max(1, min(max_workers, len(pdf_paths), DEFAULT_MAX_WORKERS))

    if len(pdf_paths) == 1:
        result = process_single_pdf(
            pdf_path=pdf_paths[0],
            session_id=session_id,
            image_output_dir=image_output_dir,
            enable_ocr=use_ocr,
            extract_images=use_images,
        )

        pdf_results.append(
            {
                "success": result.get("success"),
                "pdf_name": result.get("pdf_name"),
                "pdf_path": result.get("pdf_path"),
                "pages": result.get("pages"),
                "document_count": len(result.get("documents", [])),
                "stats": result.get("stats"),
                "error": result.get("error"),
            }
        )

        if result.get("success"):
            all_documents.extend(result.get("documents", []))
            total_pages += result.get("pages", 0)
            total_images += result.get("stats", {}).get("total_images", 0)
        else:
            failed_pdfs.append(result.get("pdf_name"))

        return {
            "success": len(all_documents) > 0,
            "documents": all_documents,
            "pdf_results": pdf_results,
            "total_pdfs": len(pdf_paths),
            "failed_pdfs": failed_pdfs,
            "total_documents": len(all_documents),
            "total_pages": total_pages,
            "total_images": total_images,
            "parallel_workers": 1,
            "ocr_enabled": use_ocr,
            "image_extraction_enabled": use_images,
            "error": None,
        }

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_pdf = {
            executor.submit(
                process_single_pdf,
                pdf_path,
                session_id,
                image_output_dir,
                use_ocr,
                use_images,
            ): pdf_path
            for pdf_path in pdf_paths
        }

        for future in as_completed(future_to_pdf):
            pdf_path = future_to_pdf[future]

            try:
                result = future.result()
            except Exception as e:
                result = {
                    "success": False,
                    "pdf_name": pdf_path.name,
                    "pdf_path": str(pdf_path),
                    "pages": 0,
                    "documents": [],
                    "stats": {},
                    "error": str(e),
                }

            pdf_results.append(
                {
                    "success": result.get("success"),
                    "pdf_name": result.get("pdf_name"),
                    "pdf_path": result.get("pdf_path"),
                    "pages": result.get("pages"),
                    "document_count": len(result.get("documents", [])),
                    "stats": result.get("stats"),
                    "error": result.get("error"),
                }
            )

            if result.get("success"):
                docs = result.get("documents", [])
                all_documents.extend(docs)
                total_pages += result.get("pages", 0)
                total_images += result.get("stats", {}).get("total_images", 0)
            else:
                failed_pdfs.append(result.get("pdf_name"))

    all_documents.sort(
        key=lambda doc: (
            doc.metadata.get("pdf_name", ""),
            int(doc.metadata.get("page_number", 0)),
        )
    )

    pdf_results.sort(key=lambda item: item.get("pdf_name", ""))

    gc.collect()

    return {
        "success": len(all_documents) > 0,
        "documents": all_documents,
        "pdf_results": pdf_results,
        "total_pdfs": len(pdf_paths),
        "failed_pdfs": failed_pdfs,
        "total_documents": len(all_documents),
        "total_pages": total_pages,
        "total_images": total_images,
        "parallel_workers": workers,
        "ocr_enabled": use_ocr,
        "image_extraction_enabled": use_images,
        "error": None,
    }


def process_uploaded_pdfs_for_session(
    session_id: str,
    enable_ocr: Optional[bool] = None,
    extract_images: Optional[bool] = None,
    max_workers: Optional[int] = None,
) -> Dict:
    pdf_paths = get_uploaded_pdfs(session_id)

    if not pdf_paths:
        return {
            "success": False,
            "documents": [],
            "pdf_results": [],
            "total_pdfs": 0,
            "failed_pdfs": [],
            "total_documents": 0,
            "total_pages": 0,
            "total_images": 0,
            "parallel_workers": 0,
            "ocr_enabled": should_use_ocr(enable_ocr),
            "image_extraction_enabled": should_extract_images(extract_images),
            "error": "No uploaded PDFs found.",
        }

    return process_multiple_pdfs(
        pdf_paths=pdf_paths,
        session_id=session_id,
        enable_ocr=enable_ocr,
        extract_images=extract_images,
        max_workers=max_workers,
    )


# ---------------------------------------------------------
# Preview / summary helpers
# ---------------------------------------------------------

def preview_pdf_text(
    pdf_path: Path,
    max_pages: int = 2,
    max_chars_per_page: int = 1500,
) -> Dict:
    pdf_path = Path(pdf_path)

    if not is_valid_pdf_path(pdf_path):
        return {
            "success": False,
            "pdf_name": pdf_path.name,
            "preview": [],
            "error": "Invalid PDF path.",
        }

    preview = []

    try:
        with fitz.open(str(pdf_path)) as pdf:
            pages_to_read = min(pdf.page_count, max_pages)

            for page_index in range(pages_to_read):
                page = pdf.load_page(page_index)
                text = extract_best_page_text(page)
                text = clean_pdf_text(text)

                preview.append(
                    {
                        "page": page_index + 1,
                        "text": text[:max_chars_per_page],
                        "quality": get_text_quality_score(text),
                    }
                )

        return {
            "success": True,
            "pdf_name": pdf_path.name,
            "preview": preview,
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "pdf_name": pdf_path.name,
            "preview": [],
            "error": str(e),
        }


def get_session_pdf_summary(session_id: str) -> Dict:
    pdf_paths = get_uploaded_pdfs(session_id)

    pdfs = []

    for pdf_path in pdf_paths:
        pdfs.append(get_pdf_info(pdf_path))

    return {
        "session_id": session_id,
        "total_pdfs": len(pdfs),
        "pdfs": pdfs,
    }


# ---------------------------------------------------------
# Self test
# ---------------------------------------------------------

def run_pdf_processor_self_test(session_id: str) -> Dict:
    try:
        result = process_uploaded_pdfs_for_session(
            session_id=session_id,
            enable_ocr=False,
            extract_images=False,
            max_workers=DEFAULT_MAX_WORKERS,
        )

        return {
            "success": result.get("success"),
            "total_pdfs": result.get("total_pdfs"),
            "total_documents": result.get("total_documents"),
            "total_pages": result.get("total_pages"),
            "failed_pdfs": result.get("failed_pdfs"),
            "parallel_workers": result.get("parallel_workers"),
            "message": "PDF processor self-test completed.",
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
        }


if __name__ == "__main__":
    print(
        "PDF processor module loaded successfully. "
        "Use process_uploaded_pdfs_for_session(session_id) from main.py."
    )