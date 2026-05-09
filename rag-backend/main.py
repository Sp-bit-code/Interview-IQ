# import os

# os.environ["TRANSFORMERS_VERBOSITY"] = "error"
# os.environ["TOKENIZERS_PARALLELISM"] = "false"

# import sys
# import re
# from pathlib import Path

# import streamlit as st


# PROJECT_ROOT = Path(__file__).resolve().parent
# sys.path.append(str(PROJECT_ROOT))


# from src.config import (
#     STREAMLIT_PAGE_TITLE,
#     STREAMLIT_PAGE_ICON,
#     STREAMLIT_LAYOUT,
#     MAX_PDFS_PER_SESSION,
#     validate_upload_file,
#     get_config_summary,
#     get_backend_llm_model,
#     get_backend_top_k,
#     get_backend_search_type,
#     get_backend_answer_mode,
#     get_parallel_pdf_workers,
#     should_clear_files_on_app_start,
#     should_show_clear_files_button,
# )

# from src.session_manager import (
#     get_or_create_session_id,
#     create_user_folders,
#     save_uploaded_pdf,
#     get_session_summary,
#     clear_user_data,
#     clear_all_session_files,
#     clear_only_uploaded_files,
# )

# from src.pdf_processor import (
#     process_uploaded_pdfs_for_session,
#     get_session_pdf_summary,
# )

# from src.vector_store import (
#     index_documents_pipeline,
#     get_vector_store_status,
#     similarity_search_with_score,
# )

# from src.rag_chain import (
#     ask_rag,
#     summarize_notes,
#     generate_questions,
#     generate_flashcards,
#     check_rag_ready,
# )

# from src.embeddings import get_embedding_status
# from src.ocr_processor import get_ocr_status
# from src.resume import render_resume_match_ui


# st.set_page_config(
#     page_title=STREAMLIT_PAGE_TITLE,
#     page_icon=STREAMLIT_PAGE_ICON,
#     layout=STREAMLIT_LAYOUT,
# )


# def init_state():
#     defaults = {
#         "processed": False,
#         "last_process_result": None,
#         "chat_history": [],
#         "last_saved_files": [],
#         "flashcards_raw": "",
#         "flashcards": [],
#         "flashcard_index": 0,
#         "selected_flashcard_option": None,
#         "flashcard_answer_checked": False,
#         "app_start_cleared": False,
#     }

#     for key, value in defaults.items():
#         if key not in st.session_state:
#             st.session_state[key] = value


# def reset_ui_state():
#     st.session_state["processed"] = False
#     st.session_state["last_process_result"] = None
#     st.session_state["chat_history"] = []
#     st.session_state["last_saved_files"] = []
#     st.session_state["flashcards_raw"] = ""
#     st.session_state["flashcards"] = []
#     st.session_state["flashcard_index"] = 0
#     st.session_state["selected_flashcard_option"] = None
#     st.session_state["flashcard_answer_checked"] = False


# def show_header():
#     st.title("📚 RAG Interview Assistant")
#     st.caption(
#         "Upload your PDF notes and ask questions from them using "
#         "RAG + LangChain + ChromaDB + Groq LLM."
#     )


# def clear_session_action(session_id: str, full_clear: bool = False):
#     if full_clear:
#         clear_all_session_files(session_id)
#     else:
#         clear_user_data(session_id)

#     reset_ui_state()
#     st.success("✅ Old PDFs, processed data, vectors, and chat history cleared.")
#     st.rerun()


# def show_sidebar(session_id: str):
#     st.sidebar.title("📌 Session")

#     with st.sidebar.expander("Session ID", expanded=False):
#         st.code(session_id)

#     vector_status = get_vector_store_status(session_id)

#     st.sidebar.subheader("System Status")
#     st.sidebar.write("Vector DB ready:", vector_status.get("ready", False))
#     st.sidebar.write("Total vectors:", vector_status.get("total_vectors", 0))
#     st.sidebar.write("PDF processing:", "Fast text mode")

#     st.sidebar.divider()

#     if st.sidebar.button("🧹 Clear this session data", use_container_width=True):
#         clear_session_action(session_id, full_clear=False)

#     if st.sidebar.button("🗑️ Hard Reset Files", use_container_width=True):
#         clear_session_action(session_id, full_clear=True)


# def save_uploaded_files(session_id: str, uploaded_files):
#     if not uploaded_files:
#         return {
#             "success": False,
#             "saved_paths": [],
#             "message": "No files uploaded.",
#         }

#     if len(uploaded_files) > MAX_PDFS_PER_SESSION:
#         return {
#             "success": False,
#             "saved_paths": [],
#             "message": f"You can upload maximum {MAX_PDFS_PER_SESSION} PDFs per session.",
#         }

#     saved_paths = []
#     invalid_files = []

#     for uploaded_file in uploaded_files:
#         file_size = getattr(uploaded_file, "size", None)

#         validation = validate_upload_file(
#             filename=uploaded_file.name,
#             size_bytes=file_size,
#         )

#         if not validation["valid"]:
#             invalid_files.append(
#                 {
#                     "name": uploaded_file.name,
#                     "message": validation["message"],
#                 }
#             )
#             continue

#         file_path = save_uploaded_pdf(
#             file_obj=uploaded_file,
#             session_id=session_id,
#             original_filename=uploaded_file.name,
#         )

#         saved_paths.append(file_path)

#     if invalid_files:
#         return {
#             "success": False,
#             "saved_paths": saved_paths,
#             "invalid_files": invalid_files,
#             "message": "Some files are invalid.",
#         }

#     return {
#         "success": True,
#         "saved_paths": saved_paths,
#         "invalid_files": [],
#         "message": f"Saved {len(saved_paths)} PDF file(s).",
#     }


# def process_notes(session_id: str):
#     pdf_result = process_uploaded_pdfs_for_session(
#         session_id=session_id,
#         enable_ocr=None,
#         extract_images=None,
#         max_workers=get_parallel_pdf_workers(),
#     )

#     if not pdf_result.get("success"):
#         return {
#             "success": False,
#             "stage": "pdf_processing",
#             "pdf_result": pdf_result,
#             "index_result": None,
#             "message": pdf_result.get("error", "PDF processing failed."),
#         }

#     index_result = index_documents_pipeline(
#         session_id=session_id,
#         documents=pdf_result["documents"],
#         reset_before_add=True,
#     )

#     if not index_result.get("success"):
#         return {
#             "success": False,
#             "stage": "indexing",
#             "pdf_result": pdf_result,
#             "index_result": index_result,
#             "message": index_result.get("message", "Indexing failed."),
#         }

#     return {
#         "success": True,
#         "stage": "completed",
#         "pdf_result": pdf_result,
#         "index_result": index_result,
#         "message": "Notes processed successfully.",
#     }


# def show_clear_files_box(session_id: str):
#     if not should_show_clear_files_button():
#         return

#     with st.container(border=True):
#         col1, col2 = st.columns([3, 1])

#         with col1:
#             st.markdown("### 🧹 Clear Old Files")
#             st.caption(
#                 "Use this when old uploaded PDFs or old RAG answers are still showing after rerun."
#             )

#         with col2:
#             if st.button("Clear Files", use_container_width=True):
#                 clear_session_action(session_id, full_clear=False)


# def show_upload_and_process(session_id: str):
#     st.subheader("1️⃣ Upload and Process Your PDF Notes")

#     show_clear_files_box(session_id)

#     uploaded_files = st.file_uploader(
#         "Upload one or multiple PDF files",
#         type=["pdf"],
#         accept_multiple_files=True,
#     )

#     session_summary = get_session_summary(session_id)
#     total_pdfs = session_summary.get("total_pdfs", 0)

#     if total_pdfs > 0:
#         st.info(f"Uploaded PDFs in current session: **{total_pdfs}**")

#         with st.expander("Uploaded PDF details"):
#             for pdf in session_summary.get("pdfs", []):
#                 st.write(
#                     f"- **{pdf.get('name')}** | "
#                     f"pages: `{pdf.get('pages', 0)}` | "
#                     f"chunks: `{pdf.get('chunks', 0)}` | "
#                     f"processed: `{pdf.get('processed', False)}`"
#                 )

#     process_disabled = not uploaded_files and total_pdfs == 0

#     col1, col2 = st.columns([2, 1])

#     with col1:
#         process_clicked = st.button(
#             "🚀 Process My Notes",
#             disabled=process_disabled,
#             use_container_width=True,
#         )

#     with col2:
#         clear_uploaded_clicked = st.button(
#             "🗑️ Clear Uploaded PDFs",
#             disabled=total_pdfs == 0,
#             use_container_width=True,
#         )

#     if clear_uploaded_clicked:
#         clear_only_uploaded_files(session_id)
#         clear_user_data(session_id)
#         reset_ui_state()
#         st.success("Uploaded PDFs and old processing data cleared.")
#         st.rerun()

#     if process_clicked:
#         if uploaded_files:
#             with st.spinner("Saving uploaded PDFs..."):
#                 save_result = save_uploaded_files(session_id, uploaded_files)

#             if not save_result["success"]:
#                 st.error(save_result["message"])

#                 for item in save_result.get("invalid_files", []):
#                     st.write(f"- {item['name']}: {item['message']}")

#                 return

#             st.session_state["last_saved_files"] = [
#                 str(path) for path in save_result["saved_paths"]
#             ]

#         with st.spinner("Processing notes and creating RAG index..."):
#             result = process_notes(session_id)

#         st.session_state["last_process_result"] = result

#         if result["success"]:
#             st.session_state["processed"] = True
#             st.session_state["chat_history"] = []
#             st.session_state["flashcards_raw"] = ""
#             st.session_state["flashcards"] = []
#             st.session_state["flashcard_index"] = 0
#             st.session_state["selected_flashcard_option"] = None
#             st.session_state["flashcard_answer_checked"] = False

#             st.success("✅ Notes processed successfully.")
#             st.rerun()
#         else:
#             st.session_state["processed"] = False
#             st.error(result["message"])

#     show_processing_status(session_id)


# def show_processing_status(session_id: str):
#     result = st.session_state.get("last_process_result")
#     vector_status = get_vector_store_status(session_id)

#     if result and result.get("success"):
#         pdf_result = result["pdf_result"]
#         index_result = result["index_result"]

#         col1, col2, col3, col4 = st.columns(4)

#         with col1:
#             st.metric("PDFs", pdf_result.get("total_pdfs", 0))

#         with col2:
#             st.metric("Pages", pdf_result.get("total_pages", 0))

#         with col3:
#             st.metric("Chunks", index_result.get("total_chunks", 0))

#         with col4:
#             st.metric("Vectors", vector_status.get("total_vectors", 0))

#     elif vector_status.get("ready"):
#         col1, col2 = st.columns(2)

#         with col1:
#             st.metric("Vector DB Ready", "Yes")

#         with col2:
#             st.metric("Total Vectors", vector_status.get("total_vectors", 0))

#     else:
#         st.info("Upload PDFs and click **Process My Notes** to start.")


# def show_chat_history():
#     for message in st.session_state["chat_history"]:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

#             if message.get("sources"):
#                 with st.expander("Sources"):
#                     for source in message["sources"]:
#                         st.write(
#                             f"- **{source.get('pdf_name')}**, "
#                             f"Page: `{source.get('page')}`, "
#                             f"Chunk: `{source.get('chunk_id')}`"
#                         )
#                         st.caption(source.get("content_preview", ""))


# def show_chat_section(session_id: str):
#     st.subheader("2️⃣ Ask Questions From Your Notes")

#     rag_ready = check_rag_ready(session_id)
#     vector_status = get_vector_store_status(session_id)

#     if not rag_ready:
#         st.warning("RAG is not ready. Please upload and process PDFs first.")

#         with st.expander("Why not ready?"):
#             st.json(vector_status)

#         return

#     st.success(
#         f"RAG is ready. Total indexed chunks/vectors: "
#         f"{vector_status.get('total_vectors', 0)}"
#     )

#     show_chat_history()

#     question = st.chat_input("Ask anything from your uploaded PDF notes...")

#     if not question:
#         return

#     st.session_state["chat_history"].append(
#         {
#             "role": "user",
#             "content": question,
#         }
#     )

#     with st.chat_message("user"):
#         st.markdown(question)

#     with st.chat_message("assistant"):
#         with st.spinner("Thinking from your notes..."):
#             result = ask_rag(
#                 session_id=session_id,
#                 question=question,
#                 model_name=get_backend_llm_model(),
#                 top_k=get_backend_top_k(),
#                 search_type=get_backend_search_type(),
#                 answer_mode=get_backend_answer_mode(),
#             )

#         answer = result.get("answer", "No answer generated.")
#         sources = result.get("sources", [])

#         st.caption(
#             f"Provider: {result.get('provider')} | "
#             f"Model: {result.get('model')} | "
#             f"Retrieved chunks: {result.get('retrieved_chunks')}"
#         )

#         st.markdown(answer)

#         if sources:
#             with st.expander("Sources"):
#                 for source in sources:
#                     st.write(
#                         f"- **{source.get('pdf_name')}**, "
#                         f"Page: `{source.get('page')}`, "
#                         f"Chunk: `{source.get('chunk_id')}`"
#                     )
#                     st.caption(source.get("content_preview", ""))

#         st.session_state["chat_history"].append(
#             {
#                 "role": "assistant",
#                 "content": answer,
#                 "sources": sources,
#             }
#         )


# def parse_flashcards(raw_text: str):
#     if not raw_text:
#         return []

#     cards = []
#     blocks = re.split(r"(?i)Flashcard\s*\d+\s*:", raw_text)

#     for block in blocks:
#         block = block.strip()

#         if not block:
#             continue

#         question_match = re.search(
#             r"(?is)Question\s*:\s*(.*?)(?=\n\s*A\)|\n\s*A\s*:)",
#             block,
#         )

#         if not question_match:
#             continue

#         question = question_match.group(1).strip()

#         options = {}

#         for label in ["A", "B", "C", "D"]:
#             pattern = rf"(?is)\n?\s*{label}\)\s*(.*?)(?=\n\s*[ABCD]\)|\n\s*Correct Option\s*:|\n\s*Answer\s*:|\n\s*Explanation\s*:|\n\s*Source\s*:|$)"
#             match = re.search(pattern, block)

#             if not match:
#                 pattern = rf"(?is)\n?\s*{label}\s*:\s*(.*?)(?=\n\s*[ABCD]\s*:|\n\s*Correct Option\s*:|\n\s*Answer\s*:|\n\s*Explanation\s*:|\n\s*Source\s*:|$)"
#                 match = re.search(pattern, block)

#             options[label] = match.group(1).strip() if match else ""

#         correct_match = re.search(
#             r"(?is)Correct Option\s*:\s*([ABCD])",
#             block,
#         )

#         answer_match = re.search(
#             r"(?is)Answer\s*:\s*(.*?)(?=\n\s*Explanation\s*:|\n\s*Source\s*:|$)",
#             block,
#         )

#         explanation_match = re.search(
#             r"(?is)Explanation\s*:\s*(.*?)(?=\n\s*Source\s*:|$)",
#             block,
#         )

#         source_match = re.search(
#             r"(?is)Source\s*:\s*(.*)$",
#             block,
#         )

#         correct = correct_match.group(1).strip().upper() if correct_match else ""
#         answer = answer_match.group(1).strip() if answer_match else ""
#         explanation = explanation_match.group(1).strip() if explanation_match else ""
#         source = source_match.group(1).strip() if source_match else ""

#         if question and all(options.values()) and correct in options:
#             cards.append(
#                 {
#                     "question": question,
#                     "options": options,
#                     "correct": correct,
#                     "answer": answer,
#                     "explanation": explanation,
#                     "source": source,
#                 }
#             )

#     return cards


# def reset_flashcard_answer():
#     st.session_state["selected_flashcard_option"] = None
#     st.session_state["flashcard_answer_checked"] = False


# def show_interactive_flashcards():
#     cards = st.session_state.get("flashcards", [])

#     if not cards:
#         return

#     index = st.session_state.get("flashcard_index", 0)
#     index = max(0, min(index, len(cards) - 1))
#     st.session_state["flashcard_index"] = index

#     card = cards[index]

#     st.markdown(f"### 🧠 Flashcard {index + 1} of {len(cards)}")

#     with st.container(border=True):
#         st.markdown(f"#### {card['question']}")

#         selected = st.radio(
#             "Choose the correct option:",
#             options=["A", "B", "C", "D"],
#             format_func=lambda option: f"{option}) {card['options'].get(option, '')}",
#             key=f"flashcard_radio_{index}",
#         )

#         st.session_state["selected_flashcard_option"] = selected

#         col1, col2, col3 = st.columns(3)

#         with col1:
#             if st.button("Check Answer", use_container_width=True):
#                 st.session_state["flashcard_answer_checked"] = True

#         with col2:
#             if st.button("Previous", disabled=index == 0, use_container_width=True):
#                 st.session_state["flashcard_index"] = index - 1
#                 reset_flashcard_answer()
#                 st.rerun()

#         with col3:
#             if st.button("Next", disabled=index == len(cards) - 1, use_container_width=True):
#                 st.session_state["flashcard_index"] = index + 1
#                 reset_flashcard_answer()
#                 st.rerun()

#         if st.session_state.get("flashcard_answer_checked"):
#             selected_option = st.session_state.get("selected_flashcard_option")
#             correct_option = card["correct"]

#             if selected_option == correct_option:
#                 st.success("✅ Correct answer!")
#             else:
#                 st.error(f"❌ Wrong answer. Correct option is {correct_option}.")

#             if card.get("answer"):
#                 st.markdown(f"**Answer:** {card['answer']}")

#             if card.get("explanation"):
#                 st.info(card["explanation"])

#             if card.get("source"):
#                 st.caption(f"Source: {card['source']}")

#     progress = (index + 1) / len(cards)
#     st.progress(progress)


# def show_tools_section(session_id: str):
#     st.subheader("3️⃣ Study Tools")

#     rag_ready = check_rag_ready(session_id)

#     if not rag_ready:
#         st.info("Process PDFs first to use study tools.")
#         return

#     selected_model = get_backend_llm_model()

#     col1, col2, col3 = st.columns(3)

#     with col1:
#         summarize_clicked = st.button(
#             "📝 Summarize Notes",
#             use_container_width=True,
#         )

#     with col2:
#         questions_clicked = st.button(
#             "❓ Generate Questions",
#             use_container_width=True,
#         )

#     with col3:
#         flashcards_clicked = st.button(
#             "🧠 Generate MCQ Flashcards",
#             use_container_width=True,
#         )

#     if summarize_clicked:
#         with st.spinner("Generating summary..."):
#             result = summarize_notes(
#                 session_id=session_id,
#                 model_name=selected_model,
#             )

#         st.markdown(result.get("answer", ""))

#         with st.expander("Sources"):
#             for source in result.get("sources", []):
#                 st.write(f"- {source.get('pdf_name')} | Page {source.get('page')}")

#     if questions_clicked:
#         with st.spinner("Generating questions..."):
#             result = generate_questions(
#                 session_id=session_id,
#                 model_name=selected_model,
#             )

#         st.markdown(result.get("answer", ""))

#         with st.expander("Sources"):
#             for source in result.get("sources", []):
#                 st.write(f"- {source.get('pdf_name')} | Page {source.get('page')}")

#     if flashcards_clicked:
#         with st.spinner("Generating interactive flashcards..."):
#             result = generate_flashcards(
#                 session_id=session_id,
#                 model_name=selected_model,
#             )

#         answer = result.get("answer", "")
#         cards = parse_flashcards(answer)

#         st.session_state["flashcards_raw"] = answer
#         st.session_state["flashcards"] = cards
#         st.session_state["flashcard_index"] = 0
#         st.session_state["selected_flashcard_option"] = None
#         st.session_state["flashcard_answer_checked"] = False

#         if not cards:
#             st.warning("Flashcards were generated, but could not be converted into MCQ format.")
#             st.markdown(answer)
#         else:
#             st.success(f"✅ {len(cards)} interactive flashcards generated.")

#         with st.expander("Sources"):
#             for source in result.get("sources", []):
#                 st.write(f"- {source.get('pdf_name')} | Page {source.get('page')}")

#     show_interactive_flashcards()

#     if st.session_state.get("flashcards_raw"):
#         with st.expander("Raw flashcard output"):
#             st.markdown(st.session_state["flashcards_raw"])


# def show_resume_analyzer_section(session_id: str):
#     st.subheader("4️⃣ Resume Analyzer")

#     render_resume_match_ui(st, session_id)


# def show_debug_section(session_id: str):
#     with st.expander("🛠 Debug / Developer Info"):
#         tab1, tab2, tab3, tab4 = st.tabs(
#             ["Session", "Vector DB", "PDFs", "Config"]
#         )

#         with tab1:
#             st.json(get_session_summary(session_id))

#         with tab2:
#             st.json(get_vector_store_status(session_id))

#             debug_query = st.text_input("Test vector search query")

#             if st.button("Search ChromaDB"):
#                 if debug_query:
#                     results = similarity_search_with_score(
#                         session_id=session_id,
#                         query=debug_query,
#                         top_k=5,
#                     )
#                     st.json(results)

#         with tab3:
#             st.json(get_session_pdf_summary(session_id))

#         with tab4:
#             st.json(get_config_summary())
#             st.json(get_embedding_status())
#             st.json(get_ocr_status())


# def main():
#     init_state()

#     session_id = get_or_create_session_id(st)
#     create_user_folders(session_id)

#     if should_clear_files_on_app_start() and not st.session_state["app_start_cleared"]:
#         clear_user_data(session_id)
#         reset_ui_state()
#         st.session_state["app_start_cleared"] = True

#     show_sidebar(session_id)
#     show_header()

#     st.divider()

#     show_upload_and_process(session_id)

#     st.divider()

#     show_chat_section(session_id)

#     st.divider()

#     show_tools_section(session_id)

#     st.divider()

#     show_resume_analyzer_section(session_id)

#     st.divider()

#     show_debug_section(session_id)


# if __name__ == "__main__":
#     main()

import os

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import re
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ---------------------------------------------------------
# Path setup
# ---------------------------------------------------------

BACKEND_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_ROOT.parent

sys.path.append(str(BACKEND_ROOT))
sys.path.append(str(PROJECT_ROOT))


# ---------------------------------------------------------
# RAG backend imports
# ---------------------------------------------------------

from src.config import (
    APP_NAME,
    APP_VERSION,
    API_DESCRIPTION,
    FRONTEND_URL,
    CORS_ALLOWED_ORIGINS,
    MAX_PDFS_PER_SESSION,
    validate_upload_file,
    get_config_summary,
    get_backend_llm_model,
    get_backend_top_k,
    get_backend_search_type,
    get_backend_answer_mode,
    get_parallel_pdf_workers,
)

from src.session_manager import (
    create_user_folders,
    get_session_summary,
    clear_user_data,
    clear_all_session_files,
    clear_only_uploaded_files,
    save_uploaded_pdf_bytes,
)

from src.pdf_processor import (
    process_uploaded_pdfs_for_session,
    get_session_pdf_summary,
)

from src.vector_store import (
    index_documents_pipeline,
    get_vector_store_status,
    similarity_search_with_score,
)

from src.rag_chain import (
    ask_rag,
    summarize_notes,
    generate_questions,
    generate_flashcards,
    check_rag_ready,
)

from src.embeddings import get_embedding_status
from src.ocr_processor import get_ocr_status

from src.resume import analyze_resume_file_bytes_and_jd_with_rag


# ---------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=API_DESCRIPTION,
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

allowed_origins = list(
    set(
        [
            FRONTEND_URL,
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            *CORS_ALLOWED_ORIGINS,
        ]
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Pydantic request models
# ---------------------------------------------------------

class AskNotesRequest(BaseModel):
    session_id: str
    question: str


class FlashcardRequest(BaseModel):
    session_id: str


class DebugSearchRequest(BaseModel):
    session_id: str
    query: str
    top_k: int = 5


# ---------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------

def create_session_id() -> str:
    return str(uuid.uuid4())


def parse_flashcards(raw_text: str) -> List[Dict[str, Any]]:
    """
    Converts LLM flashcard text into structured MCQ cards.
    """

    if not raw_text:
        return []

    cards = []
    blocks = re.split(r"(?i)Flashcard\s*\d+\s*:", raw_text)

    for block in blocks:
        block = block.strip()

        if not block:
            continue

        question_match = re.search(
            r"(?is)Question\s*:\s*(.*?)(?=\n\s*A\)|\n\s*A\s*:)",
            block,
        )

        if not question_match:
            continue

        question = question_match.group(1).strip()

        options = {}

        for label in ["A", "B", "C", "D"]:
            pattern = rf"(?is)\n?\s*{label}\)\s*(.*?)(?=\n\s*[ABCD]\)|\n\s*Correct Option\s*:|\n\s*Answer\s*:|\n\s*Explanation\s*:|\n\s*Source\s*:|$)"
            match = re.search(pattern, block)

            if not match:
                pattern = rf"(?is)\n?\s*{label}\s*:\s*(.*?)(?=\n\s*[ABCD]\s*:|\n\s*Correct Option\s*:|\n\s*Answer\s*:|\n\s*Explanation\s*:|\n\s*Source\s*:|$)"
                match = re.search(pattern, block)

            options[label] = match.group(1).strip() if match else ""

        correct_match = re.search(
            r"(?is)Correct Option\s*:\s*([ABCD])",
            block,
        )

        answer_match = re.search(
            r"(?is)Answer\s*:\s*(.*?)(?=\n\s*Explanation\s*:|\n\s*Source\s*:|$)",
            block,
        )

        explanation_match = re.search(
            r"(?is)Explanation\s*:\s*(.*?)(?=\n\s*Source\s*:|$)",
            block,
        )

        source_match = re.search(
            r"(?is)Source\s*:\s*(.*)$",
            block,
        )

        correct = correct_match.group(1).strip().upper() if correct_match else ""
        answer = answer_match.group(1).strip() if answer_match else ""
        explanation = explanation_match.group(1).strip() if explanation_match else ""
        source = source_match.group(1).strip() if source_match else ""

        if question and all(options.values()) and correct in options:
            cards.append(
                {
                    "question": question,
                    "options": options,
                    "correct": correct,
                    "answer": answer,
                    "explanation": explanation,
                    "source": source,
                }
            )

    return cards


def process_notes_for_session(session_id: str) -> Dict[str, Any]:
    """
    PDF processing + chunking + vector indexing pipeline.
    """

    pdf_result = process_uploaded_pdfs_for_session(
        session_id=session_id,
        enable_ocr=None,
        extract_images=None,
        max_workers=get_parallel_pdf_workers(),
    )

    if not pdf_result.get("success"):
        return {
            "success": False,
            "stage": "pdf_processing",
            "pdf_result": pdf_result,
            "index_result": None,
            "message": pdf_result.get("error", "PDF processing failed."),
        }

    index_result = index_documents_pipeline(
        session_id=session_id,
        documents=pdf_result["documents"],
        reset_before_add=True,
    )

    if not index_result.get("success"):
        return {
            "success": False,
            "stage": "indexing",
            "pdf_result": pdf_result,
            "index_result": index_result,
            "message": index_result.get("message", "Indexing failed."),
        }

    return {
        "success": True,
        "stage": "completed",
        "pdf_result": {
            "success": pdf_result.get("success"),
            "total_pdfs": pdf_result.get("total_pdfs"),
            "total_documents": pdf_result.get("total_documents"),
            "total_pages": pdf_result.get("total_pages"),
            "total_images": pdf_result.get("total_images"),
            "failed_pdfs": pdf_result.get("failed_pdfs"),
            "parallel_workers": pdf_result.get("parallel_workers"),
            "ocr_enabled": pdf_result.get("ocr_enabled"),
            "image_extraction_enabled": pdf_result.get("image_extraction_enabled"),
            "pdf_results": pdf_result.get("pdf_results", []),
            "error": pdf_result.get("error"),
        },
        "index_result": index_result,
        "message": "Notes processed successfully.",
    }


# ---------------------------------------------------------
# Root + health
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "success": True,
        "message": "InterviewIQ RAG Backend is running",
        "docs": "/docs",
        "health": "/health",
        "version": APP_VERSION,
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "InterviewIQ RAG Backend",
        "message": "Backend is running",
        "version": APP_VERSION,
    }


# ---------------------------------------------------------
# Notes upload + process
# ---------------------------------------------------------

@app.post("/api/notes/upload")
async def upload_notes(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
):
    """
    Upload PDF notes, save them in session storage, process PDFs, and create vector DB.
    """

    if not files:
        raise HTTPException(status_code=400, detail="No PDF files uploaded.")

    if len(files) > MAX_PDFS_PER_SESSION:
        raise HTTPException(
            status_code=400,
            detail=f"You can upload maximum {MAX_PDFS_PER_SESSION} PDFs per session.",
        )

    active_session_id = session_id or create_session_id()
    create_user_folders(active_session_id)

    saved_paths = []
    invalid_files = []

    for uploaded_file in files:
        filename = uploaded_file.filename or "uploaded.pdf"

        file_bytes = await uploaded_file.read()
        file_size = len(file_bytes)

        validation = validate_upload_file(
            filename=filename,
            size_bytes=file_size,
        )

        if not validation["valid"]:
            invalid_files.append(
                {
                    "name": filename,
                    "message": validation["message"],
                }
            )
            continue

        destination = save_uploaded_pdf_bytes(
            file_bytes=file_bytes,
            session_id=active_session_id,
            original_filename=filename,
        )

        saved_paths.append(str(destination))

    if invalid_files:
        return {
            "success": False,
            "session_id": active_session_id,
            "saved_paths": saved_paths,
            "invalid_files": invalid_files,
            "message": "Some files are invalid.",
        }

    if not saved_paths:
        raise HTTPException(
            status_code=400,
            detail="No valid PDF files were uploaded.",
        )

    process_result = process_notes_for_session(active_session_id)

    return {
        "success": process_result.get("success", False),
        "session_id": active_session_id,
        "saved_paths": saved_paths,
        "process_result": process_result,
        "vector_status": get_vector_store_status(active_session_id),
        "session_summary": get_session_summary(active_session_id),
        "message": process_result.get("message", "Upload completed."),
    }


@app.post("/api/notes/process")
def process_existing_notes(session_id: str = Form(...)):
    """
    Re-process PDFs already saved under a session.
    """

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    create_user_folders(session_id)

    process_result = process_notes_for_session(session_id)

    return {
        "success": process_result.get("success", False),
        "session_id": session_id,
        "process_result": process_result,
        "vector_status": get_vector_store_status(session_id),
        "session_summary": get_session_summary(session_id),
        "message": process_result.get("message", "Processing completed."),
    }


@app.post("/api/notes/ask")
def ask_notes_question(request: AskNotesRequest):
    """
    Ask question from uploaded notes.
    """

    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="question is required.")

    rag_ready = check_rag_ready(request.session_id)

    if not rag_ready:
        raise HTTPException(
            status_code=400,
            detail="RAG is not ready. Please upload and process notes first.",
        )

    result = ask_rag(
        session_id=request.session_id,
        question=request.question,
        model_name=get_backend_llm_model(),
        top_k=get_backend_top_k(),
        search_type=get_backend_search_type(),
        answer_mode=get_backend_answer_mode(),
    )

    return {
        "success": result.get("success", True),
        "session_id": request.session_id,
        "question": request.question,
        "answer": result.get("answer", "No answer generated."),
        "sources": result.get("sources", []),
        "provider": result.get("provider"),
        "model": result.get("model"),
        "retrieved_chunks": result.get("retrieved_chunks", 0),
    }


# ---------------------------------------------------------
# Study tools
# ---------------------------------------------------------

@app.post("/api/notes/summarize")
def summarize_uploaded_notes(session_id: str = Form(...)):
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    rag_ready = check_rag_ready(session_id)

    if not rag_ready:
        raise HTTPException(
            status_code=400,
            detail="RAG is not ready. Please upload and process notes first.",
        )

    result = summarize_notes(
        session_id=session_id,
        model_name=get_backend_llm_model(),
    )

    return {
        "success": result.get("success", True),
        "session_id": session_id,
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
        "provider": result.get("provider"),
        "model": result.get("model"),
        "retrieved_chunks": result.get("retrieved_chunks", 0),
    }


@app.post("/api/notes/questions")
def generate_notes_questions(session_id: str = Form(...)):
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    rag_ready = check_rag_ready(session_id)

    if not rag_ready:
        raise HTTPException(
            status_code=400,
            detail="RAG is not ready. Please upload and process notes first.",
        )

    result = generate_questions(
        session_id=session_id,
        model_name=get_backend_llm_model(),
    )

    return {
        "success": result.get("success", True),
        "session_id": session_id,
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
        "provider": result.get("provider"),
        "model": result.get("model"),
        "retrieved_chunks": result.get("retrieved_chunks", 0),
    }


@app.post("/api/flashcards/generate")
def generate_notes_flashcards(request: FlashcardRequest):
    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    rag_ready = check_rag_ready(request.session_id)

    if not rag_ready:
        raise HTTPException(
            status_code=400,
            detail="RAG is not ready. Please upload and process notes first.",
        )

    result = generate_flashcards(
        session_id=request.session_id,
        model_name=get_backend_llm_model(),
    )

    raw_answer = result.get("answer", "")
    parsed_cards = parse_flashcards(raw_answer)

    return {
        "success": result.get("success", True),
        "session_id": request.session_id,
        "raw": raw_answer,
        "flashcards": parsed_cards,
        "sources": result.get("sources", []),
        "total_flashcards": len(parsed_cards),
        "provider": result.get("provider"),
        "model": result.get("model"),
        "retrieved_chunks": result.get("retrieved_chunks", 0),
    }


# ---------------------------------------------------------
# Resume Gap Finder
# ---------------------------------------------------------

@app.post("/api/resume/gap-analysis")
async def resume_gap_analysis(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    session_id: Optional[str] = Form(None),
):
    """
    Resume Gap Finder:
    Upload resume + paste JD, then compare using RAG + Groq.
    """

    if resume is None:
        raise HTTPException(status_code=400, detail="Resume file is required.")

    if not job_description or not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required.")

    active_session_id = session_id or create_session_id()

    resume_bytes = await resume.read()

    if not resume_bytes:
        raise HTTPException(status_code=400, detail="Resume file is empty.")

    result = analyze_resume_file_bytes_and_jd_with_rag(
        base_session_id=active_session_id,
        resume_bytes=resume_bytes,
        resume_filename=resume.filename or "resume.pdf",
        jd_text=job_description,
    )

    return {
        "success": result.get("success", False),
        "session_id": active_session_id,
        "answer": result.get("answer", ""),
        "data": result.get("data"),
        "structured": result.get("structured"),
        "resume_text": result.get("resume_text", ""),
        "jd_text": result.get("jd_text", ""),
        "rag_context": result.get("rag_context", ""),
        "resume_rag_session_id": result.get("resume_rag_session_id"),
        "retrieved_chunks": result.get("retrieved_chunks", 0),
        "total_chunks": result.get("total_chunks", 0),
        "model": result.get("model"),
        "provider": result.get("provider"),
    }


# ---------------------------------------------------------
# Session status + clear
# ---------------------------------------------------------

@app.get("/api/session/{session_id}/summary")
def session_summary(session_id: str):
    return {
        "success": True,
        "session_id": session_id,
        "session_summary": get_session_summary(session_id),
        "pdf_summary": get_session_pdf_summary(session_id),
        "vector_status": get_vector_store_status(session_id),
        "rag_ready": check_rag_ready(session_id),
    }


@app.delete("/api/session/{session_id}/clear")
def clear_session(session_id: str, full_clear: bool = False):
    if full_clear:
        clear_all_session_files(session_id)
    else:
        clear_user_data(session_id)

    return {
        "success": True,
        "session_id": session_id,
        "full_clear": full_clear,
        "message": "Session data cleared.",
    }


@app.delete("/api/session/{session_id}/uploaded-files")
def clear_uploaded_files(session_id: str):
    clear_only_uploaded_files(session_id)
    clear_user_data(session_id)

    return {
        "success": True,
        "session_id": session_id,
        "message": "Uploaded PDFs and processed data cleared.",
    }


# ---------------------------------------------------------
# Debug endpoints
# ---------------------------------------------------------

@app.get("/api/debug/config")
def debug_config():
    return {
        "success": True,
        "config": get_config_summary(),
        "embedding_status": get_embedding_status(),
        "ocr_status": get_ocr_status(),
        "allowed_origins": allowed_origins,
    }


@app.post("/api/debug/search")
def debug_vector_search(request: DebugSearchRequest):
    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="query is required.")

    results = similarity_search_with_score(
        session_id=request.session_id,
        query=request.query,
        top_k=request.top_k,
    )

    return {
        "success": True,
        "session_id": request.session_id,
        "query": request.query,
        "results": results,
    }