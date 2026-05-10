"""
scripts/clear_data.py

This script clears generated RAG backend data.

It can delete:
- all storage data
- all user/session data
- one specific session
- ChromaDB only
- extracted images only
- uploaded PDFs only
- metadata only
- logs only

Important:
- This does NOT delete source code.
- This only deletes auto-created data inside rag-backend/storage/.
- Works for the new FastAPI backend.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path


# ---------------------------------------------------------
# Path setup
# Current file:
# interviewiq-main/rag-backend/scripts/clear_data.py
#
# BACKEND_ROOT:
# interviewiq-main/rag-backend
# ---------------------------------------------------------

BACKEND_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_ROOT.parent

sys.path.append(str(BACKEND_ROOT))
sys.path.append(str(PROJECT_ROOT))


from src.config import STORAGE_DIR, USERS_DIR, LOGS_DIR  # noqa: E402
from src.session_manager import (  # noqa: E402
    get_user_paths,
    create_user_folders,
    get_default_metadata,
    save_metadata,
)


# ---------------------------------------------------------
# Safe delete helpers
# ---------------------------------------------------------

def delete_path(path: Path) -> bool:
    """
    Delete file/folder safely.
    """

    try:
        path = Path(path)

        if not path.exists():
            return True

        if path.is_file():
            path.unlink(missing_ok=True)
            return True

        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
            return True

        return False

    except Exception as e:
        print(f"❌ Failed to delete {path}: {e}")
        return False


def clear_folder_contents(folder: Path) -> bool:
    """
    Delete only contents inside a folder.
    Folder itself remains.
    """

    try:
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)

        for item in folder.iterdir():
            delete_path(item)

        return True

    except Exception as e:
        print(f"❌ Failed to clear folder {folder}: {e}")
        return False


def ensure_base_folders() -> None:
    """
    Recreate required base folders.
    """

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    USERS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def reset_session_metadata(session_id: str, status: str = "cleared") -> None:
    """
    Reset metadata.json for one session.
    """

    create_user_folders(session_id)

    metadata = get_default_metadata(
        session_id=session_id,
        status=status,
    )

    save_metadata(session_id, metadata)


# ---------------------------------------------------------
# Clear actions
# ---------------------------------------------------------

def clear_all_storage() -> bool:
    """
    Delete complete storage folder.
    """

    print("⚠️ Clearing complete storage folder...")

    success = delete_path(STORAGE_DIR)

    ensure_base_folders()

    if success:
        print("✅ Complete storage cleared successfully.")

    return success


def clear_all_users() -> bool:
    """
    Delete all user/session folders.
    """

    print("⚠️ Clearing all user/session data...")

    success = delete_path(USERS_DIR)

    USERS_DIR.mkdir(parents=True, exist_ok=True)

    if success:
        print("✅ All user/session data cleared successfully.")

    return success


def clear_logs() -> bool:
    """
    Delete logs folder.
    """

    print("⚠️ Clearing logs...")

    success = delete_path(LOGS_DIR)

    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if success:
        print("✅ Logs cleared successfully.")

    return success


def clear_session(session_id: str) -> bool:
    """
    Delete one complete session/user folder.
    """

    if not session_id:
        print("❌ session_id is required.")
        return False

    paths = get_user_paths(session_id)
    user_dir = paths["user_dir"]

    print(f"⚠️ Clearing complete session: {session_id}")

    success = delete_path(user_dir)

    create_user_folders(session_id)
    reset_session_metadata(session_id, status="cleared")

    if success:
        print(f"✅ Session cleared: {session_id}")

    return success


def clear_session_chroma(session_id: str) -> bool:
    """
    Delete only ChromaDB folder for one session.
    """

    if not session_id:
        print("❌ session_id is required.")
        return False

    paths = get_user_paths(session_id)
    chroma_dir = paths["chroma_dir"]

    print(f"⚠️ Clearing ChromaDB for session: {session_id}")

    success = delete_path(chroma_dir)

    chroma_dir.mkdir(parents=True, exist_ok=True)

    metadata = get_default_metadata(session_id, status="chroma_cleared")
    save_metadata(session_id, metadata)

    if success:
        print("✅ ChromaDB cleared successfully.")

    return success


def clear_session_pdfs(session_id: str) -> bool:
    """
    Delete only uploaded PDFs for one session.
    """

    if not session_id:
        print("❌ session_id is required.")
        return False

    paths = get_user_paths(session_id)
    pdf_dir = paths["pdf_dir"]

    print(f"⚠️ Clearing PDFs for session: {session_id}")

    success = clear_folder_contents(pdf_dir)

    metadata = get_default_metadata(session_id, status="pdfs_cleared")
    save_metadata(session_id, metadata)

    if success:
        print("✅ Uploaded PDFs cleared successfully.")

    return success


def clear_session_images(session_id: str) -> bool:
    """
    Delete only extracted images for one session.
    """

    if not session_id:
        print("❌ session_id is required.")
        return False

    paths = get_user_paths(session_id)
    image_dir = paths["image_dir"]

    print(f"⚠️ Clearing images for session: {session_id}")

    success = clear_folder_contents(image_dir)

    if success:
        print("✅ Extracted images cleared successfully.")

    return success


def clear_session_metadata(session_id: str) -> bool:
    """
    Reset only metadata.json for one session.
    """

    if not session_id:
        print("❌ session_id is required.")
        return False

    print(f"⚠️ Resetting metadata for session: {session_id}")

    create_user_folders(session_id)
    reset_session_metadata(session_id, status="metadata_reset")

    print("✅ Metadata reset successfully.")
    return True


def clear_session_vectors_and_keep_files(session_id: str) -> bool:
    """
    Clear only vector database, keep PDFs and images.
    """

    return clear_session_chroma(session_id)


# ---------------------------------------------------------
# Summary helpers
# ---------------------------------------------------------

def get_folder_size_mb(folder: Path) -> float:
    """
    Calculate folder size in MB.
    """

    folder = Path(folder)

    if not folder.exists():
        return 0.0

    total_size = 0

    for item in folder.rglob("*"):
        try:
            if item.is_file():
                total_size += item.stat().st_size
        except Exception:
            pass

    return round(total_size / (1024 * 1024), 2)


def read_metadata_file(metadata_file: Path) -> dict:
    """
    Read metadata.json safely.
    """

    try:
        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as file:
                return json.load(file)
    except Exception:
        pass

    return {}


def show_storage_summary() -> None:
    """
    Show current storage summary.
    """

    ensure_base_folders()

    print("\n========== Storage Summary ==========")
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Backend root : {BACKEND_ROOT}")
    print(f"Storage dir  : {STORAGE_DIR}")
    print(f"Users dir    : {USERS_DIR}")
    print(f"Logs dir     : {LOGS_DIR}")
    print(f"Storage size : {get_folder_size_mb(STORAGE_DIR)} MB")
    print(f"Logs size    : {get_folder_size_mb(LOGS_DIR)} MB")

    if not USERS_DIR.exists():
        print("Total sessions: 0")
        print("=====================================\n")
        return

    sessions = [p for p in USERS_DIR.iterdir() if p.is_dir()]

    print(f"Total sessions: {len(sessions)}")

    for session_dir in sessions:
        pdf_dir = session_dir / "pdfs"
        image_dir = session_dir / "images"
        chroma_dir = session_dir / "chroma_db"
        metadata_file = session_dir / "metadata.json"

        pdf_count = len(list(pdf_dir.glob("*.pdf"))) if pdf_dir.exists() else 0
        image_count = len(list(image_dir.glob("*"))) if image_dir.exists() else 0

        chroma_exists = chroma_dir.exists()
        metadata_exists = metadata_file.exists()

        metadata = read_metadata_file(metadata_file)

        session_size = get_folder_size_mb(session_dir)

        print(f"\nSession: {session_dir.name}")
        print(f"  Size      : {session_size} MB")
        print(f"  PDFs      : {pdf_count}")
        print(f"  Images    : {image_count}")
        print(f"  ChromaDB  : {'yes' if chroma_exists else 'no'}")
        print(f"  Metadata  : {'yes' if metadata_exists else 'no'}")
        print(f"  Status    : {metadata.get('status', 'unknown')}")
        print(f"  Chunks    : {metadata.get('total_chunks', 0)}")

    print("=====================================\n")


# ---------------------------------------------------------
# CLI parser
# ---------------------------------------------------------

def parse_args():
    """
    Parse terminal arguments.
    """

    parser = argparse.ArgumentParser(
        description="Clear generated data for InterviewIQ RAG Backend."
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Clear complete storage folder.",
    )

    parser.add_argument(
        "--users",
        action="store_true",
        help="Clear all user/session data.",
    )

    parser.add_argument(
        "--logs",
        action="store_true",
        help="Clear logs folder.",
    )

    parser.add_argument(
        "--session",
        type=str,
        default="",
        help="Clear one full session/user by session_id.",
    )

    parser.add_argument(
        "--chroma",
        type=str,
        default="",
        help="Clear only ChromaDB for given session_id.",
    )

    parser.add_argument(
        "--vectors",
        type=str,
        default="",
        help="Same as --chroma. Clear vector database only.",
    )

    parser.add_argument(
        "--pdfs",
        type=str,
        default="",
        help="Clear only PDFs for given session_id.",
    )

    parser.add_argument(
        "--images",
        type=str,
        default="",
        help="Clear only extracted images for given session_id.",
    )

    parser.add_argument(
        "--metadata",
        type=str,
        default="",
        help="Reset only metadata for given session_id.",
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show storage summary.",
    )

    return parser.parse_args()


def print_help_commands() -> None:
    print("\nNo action selected.")
    print("Use one of these commands:\n")
    print("python scripts/clear_data.py --summary")
    print("python scripts/clear_data.py --all")
    print("python scripts/clear_data.py --users")
    print("python scripts/clear_data.py --logs")
    print("python scripts/clear_data.py --session SESSION_ID")
    print("python scripts/clear_data.py --chroma SESSION_ID")
    print("python scripts/clear_data.py --vectors SESSION_ID")
    print("python scripts/clear_data.py --pdfs SESSION_ID")
    print("python scripts/clear_data.py --images SESSION_ID")
    print("python scripts/clear_data.py --metadata SESSION_ID")


def main():
    """
    Main CLI entry.
    """

    args = parse_args()

    ensure_base_folders()

    if args.summary:
        show_storage_summary()
        return

    if args.all:
        clear_all_storage()
        return

    if args.users:
        clear_all_users()
        return

    if args.logs:
        clear_logs()
        return

    if args.session:
        clear_session(args.session)
        return

    if args.chroma:
        clear_session_chroma(args.chroma)
        return

    if args.vectors:
        clear_session_vectors_and_keep_files(args.vectors)
        return

    if args.pdfs:
        clear_session_pdfs(args.pdfs)
        return

    if args.images:
        clear_session_images(args.images)
        return

    if args.metadata:
        clear_session_metadata(args.metadata)
        return

    print_help_commands()


if __name__ == "__main__":
    main()