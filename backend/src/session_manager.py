# import json
# import shutil
# import uuid
# import gc
# from datetime import datetime
# from pathlib import Path
# from typing import Dict, List, Optional


# BASE_STORAGE_DIR = Path("storage")
# USERS_DIR = BASE_STORAGE_DIR / "users"


# def generate_session_id() -> str:
#     return str(uuid.uuid4())


# def get_or_create_session_id(st=None, user_id: Optional[str] = None) -> str:
#     if user_id:
#         return str(user_id)

#     fixed_session_id = "local_dev_session"

#     if st is not None:
#         st.session_state["session_id"] = fixed_session_id
#         return fixed_session_id

#     return fixed_session_id


# def get_user_dir(session_id: str) -> Path:
#     return USERS_DIR / str(session_id)


# def get_user_paths(session_id: str) -> Dict[str, Path]:
#     user_dir = get_user_dir(session_id)

#     return {
#         "user_dir": user_dir,
#         "pdf_dir": user_dir / "pdfs",
#         "image_dir": user_dir / "images",
#         "chroma_dir": user_dir / "chroma_db",
#         "metadata_file": user_dir / "metadata.json",
#     }


# def create_user_folders(session_id: str) -> Dict[str, Path]:
#     paths = get_user_paths(session_id)

#     paths["pdf_dir"].mkdir(parents=True, exist_ok=True)
#     paths["image_dir"].mkdir(parents=True, exist_ok=True)
#     paths["chroma_dir"].mkdir(parents=True, exist_ok=True)

#     if not paths["metadata_file"].exists():
#         metadata = get_default_metadata(session_id, status="created")
#         save_metadata(session_id, metadata)

#     return paths


# def current_time() -> str:
#     return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# def safe_filename(filename: str) -> str:
#     if not filename:
#         return f"uploaded_{uuid.uuid4()}.pdf"

#     filename = filename.replace("\\", "_").replace("/", "_")
#     filename = filename.replace(":", "_").replace("*", "_")
#     filename = filename.replace("?", "_").replace('"', "_")
#     filename = filename.replace("<", "_").replace(">", "_")
#     filename = filename.replace("|", "_")

#     return filename.strip()


# def get_default_metadata(session_id: str, status: str = "created") -> Dict:
#     return {
#         "session_id": session_id,
#         "created_at": current_time(),
#         "updated_at": current_time(),
#         "pdfs": [],
#         "total_chunks": 0,
#         "status": status,
#     }


# def load_metadata(session_id: str) -> Dict:
#     paths = get_user_paths(session_id)

#     if not paths["metadata_file"].exists():
#         create_user_folders(session_id)

#     try:
#         with open(paths["metadata_file"], "r", encoding="utf-8") as f:
#             return json.load(f)
#     except Exception:
#         metadata = get_default_metadata(session_id, status="created")
#         save_metadata(session_id, metadata)
#         return metadata


# def save_metadata(session_id: str, metadata: Dict) -> None:
#     paths = get_user_paths(session_id)
#     paths["user_dir"].mkdir(parents=True, exist_ok=True)

#     metadata["updated_at"] = current_time()

#     with open(paths["metadata_file"], "w", encoding="utf-8") as f:
#         json.dump(metadata, f, indent=4)


# def read_file_bytes(file_obj) -> bytes:
#     if hasattr(file_obj, "getbuffer"):
#         return bytes(file_obj.getbuffer())

#     if hasattr(file_obj, "read"):
#         data = file_obj.read()

#         try:
#             file_obj.seek(0)
#         except Exception:
#             pass

#         return data

#     raise ValueError("Unsupported file object. Cannot read uploaded PDF.")


# def save_uploaded_pdf(
#     file_obj,
#     session_id: str,
#     original_filename: Optional[str] = None,
# ) -> Path:
#     paths = create_user_folders(session_id)

#     filename = original_filename or getattr(file_obj, "name", None)

#     if not filename:
#         filename = f"uploaded_{uuid.uuid4()}.pdf"

#     filename = safe_filename(Path(filename).name)

#     if not filename.lower().endswith(".pdf"):
#         filename += ".pdf"

#     file_path = paths["pdf_dir"] / filename
#     file_bytes = read_file_bytes(file_obj)

#     with open(file_path, "wb") as f:
#         f.write(file_bytes)

#     add_pdf_to_metadata(
#         session_id=session_id,
#         pdf_name=filename,
#         file_path=str(file_path),
#     )

#     return file_path


# def add_pdf_to_metadata(
#     session_id: str,
#     pdf_name: str,
#     file_path: str,
#     pages: int = 0,
# ) -> None:
#     metadata = load_metadata(session_id)
#     pdfs: List[Dict] = metadata.get("pdfs", [])

#     found = False

#     for pdf in pdfs:
#         if pdf.get("name") == pdf_name:
#             pdf["path"] = file_path
#             pdf["pages"] = pages
#             pdf["updated_at"] = current_time()
#             pdf["processed"] = False
#             found = True
#             break

#     if not found:
#         pdfs.append(
#             {
#                 "name": pdf_name,
#                 "path": file_path,
#                 "pages": pages,
#                 "uploaded_at": current_time(),
#                 "updated_at": current_time(),
#                 "processed": False,
#                 "chunks": 0,
#             }
#         )

#     metadata["pdfs"] = pdfs
#     metadata["status"] = "pdf_uploaded"
#     save_metadata(session_id, metadata)


# def mark_pdf_processed(
#     session_id: str,
#     pdf_name: str,
#     pages: int,
#     chunks: int,
# ) -> None:
#     metadata = load_metadata(session_id)
#     found = False

#     for pdf in metadata.get("pdfs", []):
#         if pdf.get("name") == pdf_name:
#             pdf["pages"] = pages
#             pdf["chunks"] = chunks
#             pdf["processed"] = True
#             pdf["processed_at"] = current_time()
#             pdf["updated_at"] = current_time()
#             found = True
#             break

#     if not found:
#         metadata.setdefault("pdfs", []).append(
#             {
#                 "name": pdf_name,
#                 "path": "",
#                 "pages": pages,
#                 "chunks": chunks,
#                 "uploaded_at": current_time(),
#                 "updated_at": current_time(),
#                 "processed": True,
#                 "processed_at": current_time(),
#             }
#         )

#     metadata["status"] = "processed"
#     save_metadata(session_id, metadata)


# def update_total_chunks(session_id: str, total_chunks: int) -> None:
#     metadata = load_metadata(session_id)
#     metadata["total_chunks"] = total_chunks
#     metadata["status"] = "indexed" if total_chunks > 0 else "created"
#     save_metadata(session_id, metadata)


# def get_uploaded_pdfs(session_id: str) -> List[Path]:
#     paths = create_user_folders(session_id)
#     return sorted(list(paths["pdf_dir"].glob("*.pdf")))


# def get_chroma_path(session_id: str) -> str:
#     paths = create_user_folders(session_id)
#     return str(paths["chroma_dir"])


# def get_image_path(session_id: str) -> Path:
#     paths = create_user_folders(session_id)
#     return paths["image_dir"]


# def session_exists(session_id: str) -> bool:
#     return get_user_dir(session_id).exists()


# def get_session_summary(session_id: str) -> Dict:
#     metadata = load_metadata(session_id)

#     return {
#         "session_id": session_id,
#         "total_pdfs": len(metadata.get("pdfs", [])),
#         "total_chunks": metadata.get("total_chunks", 0),
#         "status": metadata.get("status", "unknown"),
#         "pdfs": metadata.get("pdfs", []),
#     }


# def safe_remove_dir_contents(folder: Path) -> bool:
#     try:
#         folder = Path(folder)
#         folder.mkdir(parents=True, exist_ok=True)

#         for item in folder.iterdir():
#             try:
#                 if item.is_file():
#                     item.unlink(missing_ok=True)
#                 elif item.is_dir():
#                     shutil.rmtree(item, ignore_errors=True)
#             except Exception:
#                 pass

#         return True
#     except Exception:
#         return False


# def safe_remove_file(file_path: Path) -> bool:
#     try:
#         file_path = Path(file_path)

#         if file_path.exists() and file_path.is_file():
#             file_path.unlink(missing_ok=True)

#         return True
#     except Exception:
#         return False


# def reset_chroma_collection(session_id: str) -> bool:
#     try:
#         from src.vector_store import delete_existing_collection_items
#         delete_existing_collection_items(session_id)
#         return True
#     except Exception:
#         return False


# def clear_user_data(session_id: str) -> bool:
#     paths = create_user_folders(session_id)

#     gc.collect()

#     reset_chroma_collection(session_id)

#     safe_remove_dir_contents(paths["pdf_dir"])
#     safe_remove_dir_contents(paths["image_dir"])

#     metadata = get_default_metadata(session_id, status="cleared")
#     save_metadata(session_id, metadata)

#     return True


# def clear_all_session_files(session_id: str) -> bool:
#     paths = create_user_folders(session_id)

#     gc.collect()

#     reset_chroma_collection(session_id)

#     safe_remove_dir_contents(paths["pdf_dir"])
#     safe_remove_dir_contents(paths["image_dir"])
#     safe_remove_dir_contents(paths["chroma_dir"])

#     metadata = get_default_metadata(session_id, status="cleared")
#     save_metadata(session_id, metadata)

#     return True


# def clear_only_uploaded_files(session_id: str) -> bool:
#     paths = create_user_folders(session_id)

#     safe_remove_dir_contents(paths["pdf_dir"])
#     safe_remove_dir_contents(paths["image_dir"])

#     metadata = load_metadata(session_id)
#     metadata["pdfs"] = []
#     metadata["total_chunks"] = 0
#     metadata["status"] = "files_cleared"

#     save_metadata(session_id, metadata)

#     return True


# def clear_on_app_start(session_id: str, enabled: bool = False) -> bool:
#     if enabled:
#         return clear_user_data(session_id)

#     create_user_folders(session_id)
#     return False


# def delete_single_pdf(session_id: str, pdf_name: str) -> bool:
#     paths = create_user_folders(session_id)
#     pdf_name = safe_filename(pdf_name)
#     pdf_path = paths["pdf_dir"] / pdf_name

#     safe_remove_file(pdf_path)

#     metadata = load_metadata(session_id)

#     metadata["pdfs"] = [
#         pdf for pdf in metadata.get("pdfs", [])
#         if pdf.get("name") != pdf_name
#     ]

#     metadata["total_chunks"] = sum(
#         int(pdf.get("chunks", 0) or 0)
#         for pdf in metadata.get("pdfs", [])
#     )

#     metadata["status"] = "pdf_deleted"

#     save_metadata(session_id, metadata)

#     return True


import json
import shutil
import uuid
import gc
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------
# Important:
# This file is now inside:
# interviewiq-main/rag-backend/src/session_manager.py
#
# Storage will be:
# interviewiq-main/rag-backend/storage/users/<session_id>/
# ---------------------------------------------------------

try:
    from src.config import STORAGE_DIR, USERS_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent.parent
    STORAGE_DIR = BASE_DIR / "storage"
    USERS_DIR = STORAGE_DIR / "users"


BASE_STORAGE_DIR = STORAGE_DIR


def generate_session_id() -> str:
    return str(uuid.uuid4())


def get_or_create_session_id(st=None, user_id: Optional[str] = None) -> str:
    """
    Old Streamlit support is kept.

    FastAPI/React flow:
    - If frontend sends user/session id, use that.
    - Otherwise use local_dev_session.
    """
    if user_id:
        return str(user_id)

    fixed_session_id = "local_dev_session"

    if st is not None:
        st.session_state["session_id"] = fixed_session_id
        return fixed_session_id

    return fixed_session_id


def get_user_dir(session_id: str) -> Path:
    return USERS_DIR / str(session_id)


def get_user_paths(session_id: str) -> Dict[str, Path]:
    user_dir = get_user_dir(session_id)

    return {
        "user_dir": user_dir,
        "pdf_dir": user_dir / "pdfs",
        "image_dir": user_dir / "images",
        "chroma_dir": user_dir / "chroma_db",
        "metadata_file": user_dir / "metadata.json",
    }


def create_user_folders(session_id: str) -> Dict[str, Path]:
    paths = get_user_paths(session_id)

    paths["user_dir"].mkdir(parents=True, exist_ok=True)
    paths["pdf_dir"].mkdir(parents=True, exist_ok=True)
    paths["image_dir"].mkdir(parents=True, exist_ok=True)
    paths["chroma_dir"].mkdir(parents=True, exist_ok=True)

    if not paths["metadata_file"].exists():
        metadata = get_default_metadata(session_id, status="created")
        save_metadata(session_id, metadata)

    return paths


def current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_filename(filename: str) -> str:
    if not filename:
        return f"uploaded_{uuid.uuid4()}.pdf"

    filename = filename.replace("\\", "_").replace("/", "_")
    filename = filename.replace(":", "_").replace("*", "_")
    filename = filename.replace("?", "_").replace('"', "_")
    filename = filename.replace("<", "_").replace(">", "_")
    filename = filename.replace("|", "_")

    filename = filename.strip()

    if not filename:
        return f"uploaded_{uuid.uuid4()}.pdf"

    return filename


def get_default_metadata(session_id: str, status: str = "created") -> Dict:
    return {
        "session_id": session_id,
        "created_at": current_time(),
        "updated_at": current_time(),
        "pdfs": [],
        "total_chunks": 0,
        "status": status,
    }


def load_metadata(session_id: str) -> Dict:
    paths = get_user_paths(session_id)

    if not paths["metadata_file"].exists():
        create_user_folders(session_id)

    try:
        with open(paths["metadata_file"], "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        metadata = get_default_metadata(session_id, status="created")
        save_metadata(session_id, metadata)
        return metadata


def save_metadata(session_id: str, metadata: Dict) -> None:
    paths = get_user_paths(session_id)
    paths["user_dir"].mkdir(parents=True, exist_ok=True)

    metadata["updated_at"] = current_time()

    with open(paths["metadata_file"], "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)


def read_file_bytes(file_obj) -> bytes:
    """
    Supports:
    1. Streamlit UploadedFile
    2. Normal file object
    3. FastAPI UploadFile.file
    """
    if hasattr(file_obj, "getbuffer"):
        return bytes(file_obj.getbuffer())

    if hasattr(file_obj, "read"):
        data = file_obj.read()

        try:
            file_obj.seek(0)
        except Exception:
            pass

        return data

    raise ValueError("Unsupported file object. Cannot read uploaded PDF.")


def save_uploaded_pdf(
    file_obj,
    session_id: str,
    original_filename: Optional[str] = None,
) -> Path:
    paths = create_user_folders(session_id)

    filename = original_filename or getattr(file_obj, "name", None)

    if not filename:
        filename = f"uploaded_{uuid.uuid4()}.pdf"

    filename = safe_filename(Path(filename).name)

    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    file_path = paths["pdf_dir"] / filename
    file_bytes = read_file_bytes(file_obj)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    add_pdf_to_metadata(
        session_id=session_id,
        pdf_name=filename,
        file_path=str(file_path),
    )

    return file_path


def save_uploaded_pdf_bytes(
    file_bytes: bytes,
    session_id: str,
    original_filename: Optional[str] = None,
) -> Path:
    """
    New FastAPI-friendly helper.

    Use this when FastAPI gives you bytes from UploadFile.read().
    """
    paths = create_user_folders(session_id)

    filename = original_filename or f"uploaded_{uuid.uuid4()}.pdf"
    filename = safe_filename(Path(filename).name)

    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    file_path = paths["pdf_dir"] / filename

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    add_pdf_to_metadata(
        session_id=session_id,
        pdf_name=filename,
        file_path=str(file_path),
    )

    return file_path


def add_pdf_to_metadata(
    session_id: str,
    pdf_name: str,
    file_path: str,
    pages: int = 0,
) -> None:
    metadata = load_metadata(session_id)
    pdfs: List[Dict] = metadata.get("pdfs", [])

    found = False

    for pdf in pdfs:
        if pdf.get("name") == pdf_name:
            pdf["path"] = file_path
            pdf["pages"] = pages
            pdf["updated_at"] = current_time()
            pdf["processed"] = False
            found = True
            break

    if not found:
        pdfs.append(
            {
                "name": pdf_name,
                "path": file_path,
                "pages": pages,
                "uploaded_at": current_time(),
                "updated_at": current_time(),
                "processed": False,
                "chunks": 0,
            }
        )

    metadata["pdfs"] = pdfs
    metadata["status"] = "pdf_uploaded"
    save_metadata(session_id, metadata)


def mark_pdf_processed(
    session_id: str,
    pdf_name: str,
    pages: int,
    chunks: int,
) -> None:
    metadata = load_metadata(session_id)
    found = False

    for pdf in metadata.get("pdfs", []):
        if pdf.get("name") == pdf_name:
            pdf["pages"] = pages
            pdf["chunks"] = chunks
            pdf["processed"] = True
            pdf["processed_at"] = current_time()
            pdf["updated_at"] = current_time()
            found = True
            break

    if not found:
        metadata.setdefault("pdfs", []).append(
            {
                "name": pdf_name,
                "path": "",
                "pages": pages,
                "chunks": chunks,
                "uploaded_at": current_time(),
                "updated_at": current_time(),
                "processed": True,
                "processed_at": current_time(),
            }
        )

    metadata["status"] = "processed"
    save_metadata(session_id, metadata)


def update_total_chunks(session_id: str, total_chunks: int) -> None:
    metadata = load_metadata(session_id)
    metadata["total_chunks"] = total_chunks
    metadata["status"] = "indexed" if total_chunks > 0 else "created"
    save_metadata(session_id, metadata)


def get_uploaded_pdfs(session_id: str) -> List[Path]:
    paths = create_user_folders(session_id)
    return sorted(list(paths["pdf_dir"].glob("*.pdf")))


def get_chroma_path(session_id: str) -> str:
    paths = create_user_folders(session_id)
    return str(paths["chroma_dir"])


def get_image_path(session_id: str) -> Path:
    paths = create_user_folders(session_id)
    return paths["image_dir"]


def session_exists(session_id: str) -> bool:
    return get_user_dir(session_id).exists()


def get_session_summary(session_id: str) -> Dict:
    metadata = load_metadata(session_id)

    return {
        "session_id": session_id,
        "total_pdfs": len(metadata.get("pdfs", [])),
        "total_chunks": metadata.get("total_chunks", 0),
        "status": metadata.get("status", "unknown"),
        "pdfs": metadata.get("pdfs", []),
    }


def safe_remove_dir_contents(folder: Path) -> bool:
    try:
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)

        for item in folder.iterdir():
            try:
                if item.is_file():
                    item.unlink(missing_ok=True)
                elif item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
            except Exception:
                pass

        return True
    except Exception:
        return False


def safe_remove_file(file_path: Path) -> bool:
    try:
        file_path = Path(file_path)

        if file_path.exists() and file_path.is_file():
            file_path.unlink(missing_ok=True)

        return True
    except Exception:
        return False


def reset_chroma_collection(session_id: str) -> bool:
    try:
        from src.vector_store import delete_existing_collection_items

        delete_existing_collection_items(session_id)
        return True
    except Exception:
        return False


def clear_user_data(session_id: str) -> bool:
    paths = create_user_folders(session_id)

    gc.collect()

    reset_chroma_collection(session_id)

    safe_remove_dir_contents(paths["pdf_dir"])
    safe_remove_dir_contents(paths["image_dir"])

    metadata = get_default_metadata(session_id, status="cleared")
    save_metadata(session_id, metadata)

    return True


def clear_all_session_files(session_id: str) -> bool:
    paths = create_user_folders(session_id)

    gc.collect()

    reset_chroma_collection(session_id)

    safe_remove_dir_contents(paths["pdf_dir"])
    safe_remove_dir_contents(paths["image_dir"])
    safe_remove_dir_contents(paths["chroma_dir"])

    metadata = get_default_metadata(session_id, status="cleared")
    save_metadata(session_id, metadata)

    return True


def clear_only_uploaded_files(session_id: str) -> bool:
    paths = create_user_folders(session_id)

    safe_remove_dir_contents(paths["pdf_dir"])
    safe_remove_dir_contents(paths["image_dir"])

    metadata = load_metadata(session_id)
    metadata["pdfs"] = []
    metadata["total_chunks"] = 0
    metadata["status"] = "files_cleared"

    save_metadata(session_id, metadata)

    return True


def clear_on_app_start(session_id: str, enabled: bool = False) -> bool:
    if enabled:
        return clear_user_data(session_id)

    create_user_folders(session_id)
    return False


def delete_single_pdf(session_id: str, pdf_name: str) -> bool:
    paths = create_user_folders(session_id)
    pdf_name = safe_filename(pdf_name)
    pdf_path = paths["pdf_dir"] / pdf_name

    safe_remove_file(pdf_path)

    metadata = load_metadata(session_id)

    metadata["pdfs"] = [
        pdf for pdf in metadata.get("pdfs", []) if pdf.get("name") != pdf_name
    ]

    metadata["total_chunks"] = sum(
        int(pdf.get("chunks", 0) or 0) for pdf in metadata.get("pdfs", [])
    )

    metadata["status"] = "pdf_deleted"

    save_metadata(session_id, metadata)

    return True