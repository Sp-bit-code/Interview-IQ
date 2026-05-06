from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import gc

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


def clean_pdf_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = text.replace("\t", " ")
    text = text.replace("\r", "\n")

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


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


def run_ocr_on_images(image_items: List[Dict]) -> str:
    if not image_items:
        return ""

    try:
        from src.ocr_processor import extract_text_from_image
    except Exception:
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
        "images": 0,
        "has_ocr": False,
        "ocr_chars": 0,
    }

    try:
        raw_text = page.get_text("text")
        text = clean_pdf_text(raw_text)
        text = safe_page_text(text)

        if text:
            stats["has_text"] = True
            stats["text_chars"] = len(text)

        image_items = []

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

        if use_ocr and image_items:
            ocr_text = run_ocr_on_images(image_items)

            if ocr_text:
                stats["has_ocr"] = True
                stats["ocr_chars"] = len(ocr_text)

        final_content_parts = []

        if text:
            final_content_parts.append(text)

        if ocr_text:
            final_content_parts.append(
                "\n[Extracted text from images/diagrams]\n" + ocr_text
            )

        final_content = "\n\n".join(final_content_parts).strip()

        if not final_content:
            return None, stats

        metadata = {
            "pdf_name": pdf_name,
            "source": pdf_name,
            "pdf_path": str(pdf_path),
            "page_number": page_number,
            "page": page_number,
            "content_type": "pdf_page",
            "has_text": stats["has_text"],
            "has_images": stats["images"] > 0,
            "has_ocr": stats["has_ocr"],
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
        "pages_with_images": 0,
        "pages_with_ocr": 0,
        "total_images": 0,
        "total_text_chars": 0,
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

                if page_stats.get("images", 0) > 0:
                    stats["pages_with_images"] += 1

                if page_stats.get("has_ocr"):
                    stats["pages_with_ocr"] += 1

                stats["total_images"] += page_stats.get("images", 0)
                stats["total_text_chars"] += page_stats.get("text_chars", 0)
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


def preview_pdf_text(
    pdf_path: Path,
    max_pages: int = 2,
    max_chars_per_page: int = 1000,
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
                text = clean_pdf_text(page.get_text("text"))

                preview.append(
                    {
                        "page": page_index + 1,
                        "text": text[:max_chars_per_page],
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