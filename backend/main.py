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
















































# import os

# os.environ["TRANSFORMERS_VERBOSITY"] = "error"
# os.environ["TOKENIZERS_PARALLELISM"] = "false"

# import sys
# import re
# import uuid
# from pathlib import Path
# from typing import List, Optional, Dict, Any

# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel


# # ---------------------------------------------------------
# # Path setup
# # ---------------------------------------------------------

# BACKEND_ROOT = Path(__file__).resolve().parent
# PROJECT_ROOT = BACKEND_ROOT.parent

# sys.path.append(str(BACKEND_ROOT))
# sys.path.append(str(PROJECT_ROOT))


# # ---------------------------------------------------------
# # RAG backend imports
# # ---------------------------------------------------------

# from src.config import (
#     APP_NAME,
#     APP_VERSION,
#     API_DESCRIPTION,
#     FRONTEND_URL,
#     CORS_ALLOWED_ORIGINS,
#     MAX_PDFS_PER_SESSION,
#     validate_upload_file,
#     get_config_summary,
#     get_backend_llm_model,
#     get_backend_top_k,
#     get_backend_search_type,
#     get_backend_answer_mode,
#     get_parallel_pdf_workers,
# )

# from src.session_manager import (
#     create_user_folders,
#     get_session_summary,
#     clear_user_data,
#     clear_all_session_files,
#     clear_only_uploaded_files,
#     save_uploaded_pdf_bytes,
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

# from src.resume import analyze_resume_file_bytes_and_jd_with_rag


# # ---------------------------------------------------------
# # FastAPI app
# # ---------------------------------------------------------

# app = FastAPI(
#     title=APP_NAME,
#     version=APP_VERSION,
#     description=API_DESCRIPTION,
# )


# # ---------------------------------------------------------
# # CORS
# # ---------------------------------------------------------

# allowed_origins = list(set([
#     FRONTEND_URL,
#     "http://localhost:5173",
#     "http://127.0.0.1:5173",
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     *CORS_ALLOWED_ORIGINS,
# ]))

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=allowed_origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # ---------------------------------------------------------
# # Pydantic request models
# # ---------------------------------------------------------

# class AskNotesRequest(BaseModel):
#     session_id: str
#     question: str


# class FlashcardRequest(BaseModel):
#     session_id: str


# class DebugSearchRequest(BaseModel):
#     session_id: str
#     query: str
#     top_k: int = 5


# # ---------------------------------------------------------
# # Utility helpers
# # ---------------------------------------------------------

# def create_session_id() -> str:
#     return str(uuid.uuid4())


# def parse_flashcards(raw_text: str) -> List[Dict[str, Any]]:
#     """
#     Converts LLM flashcard text into structured MCQ cards.
#     """

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


# def process_notes_for_session(session_id: str) -> Dict[str, Any]:
#     """
#     PDF processing + chunking + vector indexing pipeline.
#     """

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
#         "pdf_result": {
#             "success": pdf_result.get("success"),
#             "total_pdfs": pdf_result.get("total_pdfs"),
#             "total_documents": pdf_result.get("total_documents"),
#             "total_pages": pdf_result.get("total_pages"),
#             "total_images": pdf_result.get("total_images"),
#             "failed_pdfs": pdf_result.get("failed_pdfs"),
#             "parallel_workers": pdf_result.get("parallel_workers"),
#             "ocr_enabled": pdf_result.get("ocr_enabled"),
#             "image_extraction_enabled": pdf_result.get("image_extraction_enabled"),
#             "pdf_results": pdf_result.get("pdf_results", []),
#             "error": pdf_result.get("error"),
#         },
#         "index_result": index_result,
#         "message": "Notes processed successfully.",
#     }


# # ---------------------------------------------------------
# # Root + health
# # ---------------------------------------------------------

# @app.get("/")
# def root():
#     return {
#         "success": True,
#         "message": "InterviewIQ RAG Backend is running",
#         "docs": "/docs",
#         "health": "/health",
#     }


# @app.get("/health")
# def health_check():
#     return {
#         "success": True,
#         "status": "ok",
#         "service": "InterviewIQ RAG Backend",
#         "version": APP_VERSION,
#     }


# # ---------------------------------------------------------
# # Notes upload + process
# # ---------------------------------------------------------

# @app.post("/api/notes/upload")
# async def upload_notes(
#     files: List[UploadFile] = File(...),
#     session_id: Optional[str] = Form(None),
# ):
#     """
#     Upload PDF notes, save them in session storage, process PDFs, and create vector DB.
#     """

#     if not files:
#         raise HTTPException(status_code=400, detail="No PDF files uploaded.")

#     if len(files) > MAX_PDFS_PER_SESSION:
#         raise HTTPException(
#             status_code=400,
#             detail=f"You can upload maximum {MAX_PDFS_PER_SESSION} PDFs per session.",
#         )

#     active_session_id = session_id or create_session_id()
#     create_user_folders(active_session_id)

#     saved_paths = []
#     invalid_files = []

#     for uploaded_file in files:
#         filename = uploaded_file.filename or "uploaded.pdf"

#         file_bytes = await uploaded_file.read()
#         file_size = len(file_bytes)

#         validation = validate_upload_file(
#             filename=filename,
#             size_bytes=file_size,
#         )

#         if not validation["valid"]:
#             invalid_files.append(
#                 {
#                     "name": filename,
#                     "message": validation["message"],
#                 }
#             )
#             continue

#         destination = save_uploaded_pdf_bytes(
#             file_bytes=file_bytes,
#             session_id=active_session_id,
#             original_filename=filename,
#         )

#         saved_paths.append(str(destination))

#     if invalid_files:
#         return {
#             "success": False,
#             "session_id": active_session_id,
#             "saved_paths": saved_paths,
#             "invalid_files": invalid_files,
#             "message": "Some files are invalid.",
#         }

#     if not saved_paths:
#         raise HTTPException(
#             status_code=400,
#             detail="No valid PDF files were uploaded.",
#         )

#     process_result = process_notes_for_session(active_session_id)

#     return {
#         "success": process_result.get("success", False),
#         "session_id": active_session_id,
#         "saved_paths": saved_paths,
#         "process_result": process_result,
#         "vector_status": get_vector_store_status(active_session_id),
#         "session_summary": get_session_summary(active_session_id),
#         "message": process_result.get("message", "Upload completed."),
#     }


# @app.post("/api/notes/process")
# def process_existing_notes(session_id: str = Form(...)):
#     """
#     Re-process PDFs already saved under a session.
#     """

#     if not session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     create_user_folders(session_id)

#     process_result = process_notes_for_session(session_id)

#     return {
#         "success": process_result.get("success", False),
#         "session_id": session_id,
#         "process_result": process_result,
#         "vector_status": get_vector_store_status(session_id),
#         "session_summary": get_session_summary(session_id),
#         "message": process_result.get("message", "Processing completed."),
#     }


# @app.post("/api/notes/ask")
# def ask_notes_question(request: AskNotesRequest):
#     """
#     Ask question from uploaded notes.
#     """

#     if not request.session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     if not request.question or not request.question.strip():
#         raise HTTPException(status_code=400, detail="question is required.")

#     rag_ready = check_rag_ready(request.session_id)

#     if not rag_ready:
#         raise HTTPException(
#             status_code=400,
#             detail="RAG is not ready. Please upload and process notes first.",
#         )

#     result = ask_rag(
#         session_id=request.session_id,
#         question=request.question,
#         model_name=get_backend_llm_model(),
#         top_k=get_backend_top_k(),
#         search_type=get_backend_search_type(),
#         answer_mode=get_backend_answer_mode(),
#     )

#     return {
#         "success": result.get("success", True),
#         "session_id": request.session_id,
#         "question": request.question,
#         "answer": result.get("answer", "No answer generated."),
#         "sources": result.get("sources", []),
#         "provider": result.get("provider"),
#         "model": result.get("model"),
#         "retrieved_chunks": result.get("retrieved_chunks", 0),
#     }


# # ---------------------------------------------------------
# # Study tools
# # ---------------------------------------------------------

# @app.post("/api/notes/summarize")
# def summarize_uploaded_notes(session_id: str = Form(...)):
#     if not session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     rag_ready = check_rag_ready(session_id)

#     if not rag_ready:
#         raise HTTPException(
#             status_code=400,
#             detail="RAG is not ready. Please upload and process notes first.",
#         )

#     result = summarize_notes(
#         session_id=session_id,
#         model_name=get_backend_llm_model(),
#     )

#     return {
#         "success": result.get("success", True),
#         "session_id": session_id,
#         "answer": result.get("answer", ""),
#         "sources": result.get("sources", []),
#         "provider": result.get("provider"),
#         "model": result.get("model"),
#         "retrieved_chunks": result.get("retrieved_chunks", 0),
#     }


# @app.post("/api/notes/questions")
# def generate_notes_questions(session_id: str = Form(...)):
#     if not session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     rag_ready = check_rag_ready(session_id)

#     if not rag_ready:
#         raise HTTPException(
#             status_code=400,
#             detail="RAG is not ready. Please upload and process notes first.",
#         )

#     result = generate_questions(
#         session_id=session_id,
#         model_name=get_backend_llm_model(),
#     )

#     return {
#         "success": result.get("success", True),
#         "session_id": session_id,
#         "answer": result.get("answer", ""),
#         "sources": result.get("sources", []),
#         "provider": result.get("provider"),
#         "model": result.get("model"),
#         "retrieved_chunks": result.get("retrieved_chunks", 0),
#     }


# @app.post("/api/flashcards/generate")
# def generate_notes_flashcards(request: FlashcardRequest):
#     if not request.session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     rag_ready = check_rag_ready(request.session_id)

#     if not rag_ready:
#         raise HTTPException(
#             status_code=400,
#             detail="RAG is not ready. Please upload and process notes first.",
#         )

#     result = generate_flashcards(
#         session_id=request.session_id,
#         model_name=get_backend_llm_model(),
#     )

#     raw_answer = result.get("answer", "")
#     parsed_cards = parse_flashcards(raw_answer)

#     return {
#         "success": result.get("success", True),
#         "session_id": request.session_id,
#         "raw": raw_answer,
#         "flashcards": parsed_cards,
#         "sources": result.get("sources", []),
#         "total_flashcards": len(parsed_cards),
#         "provider": result.get("provider"),
#         "model": result.get("model"),
#         "retrieved_chunks": result.get("retrieved_chunks", 0),
#     }


# # ---------------------------------------------------------
# # Resume Gap Finder
# # ---------------------------------------------------------

# @app.post("/api/resume/gap-analysis")
# async def resume_gap_analysis(
#     resume: UploadFile = File(...),
#     job_description: str = Form(...),
#     session_id: Optional[str] = Form(None),
# ):
#     """
#     Resume Gap Finder:
#     Upload resume + paste JD, then compare using RAG + Groq.
#     """

#     if resume is None:
#         raise HTTPException(status_code=400, detail="Resume file is required.")

#     if not job_description or not job_description.strip():
#         raise HTTPException(status_code=400, detail="Job description is required.")

#     active_session_id = session_id or create_session_id()

#     resume_bytes = await resume.read()

#     if not resume_bytes:
#         raise HTTPException(status_code=400, detail="Resume file is empty.")

#     result = analyze_resume_file_bytes_and_jd_with_rag(
#         base_session_id=active_session_id,
#         resume_bytes=resume_bytes,
#         resume_filename=resume.filename or "resume.pdf",
#         jd_text=job_description,
#     )

#     return {
#         "success": result.get("success", False),
#         "session_id": active_session_id,
#         "answer": result.get("answer", ""),
#         "data": result.get("data"),
#         "structured": result.get("structured"),
#         "resume_text": result.get("resume_text", ""),
#         "jd_text": result.get("jd_text", ""),
#         "rag_context": result.get("rag_context", ""),
#         "resume_rag_session_id": result.get("resume_rag_session_id"),
#         "retrieved_chunks": result.get("retrieved_chunks", 0),
#         "total_chunks": result.get("total_chunks", 0),
#         "model": result.get("model"),
#         "provider": result.get("provider"),
#     }


# # ---------------------------------------------------------
# # Session status + clear
# # ---------------------------------------------------------

# @app.get("/api/session/{session_id}/summary")
# def session_summary(session_id: str):
#     return {
#         "success": True,
#         "session_id": session_id,
#         "session_summary": get_session_summary(session_id),
#         "pdf_summary": get_session_pdf_summary(session_id),
#         "vector_status": get_vector_store_status(session_id),
#         "rag_ready": check_rag_ready(session_id),
#     }


# @app.delete("/api/session/{session_id}/clear")
# def clear_session(session_id: str, full_clear: bool = False):
#     if full_clear:
#         clear_all_session_files(session_id)
#     else:
#         clear_user_data(session_id)

#     return {
#         "success": True,
#         "session_id": session_id,
#         "full_clear": full_clear,
#         "message": "Session data cleared.",
#     }


# @app.delete("/api/session/{session_id}/uploaded-files")
# def clear_uploaded_files(session_id: str):
#     clear_only_uploaded_files(session_id)
#     clear_user_data(session_id)

#     return {
#         "success": True,
#         "session_id": session_id,
#         "message": "Uploaded PDFs and processed data cleared.",
#     }


# # ---------------------------------------------------------
# # Debug endpoints
# # ---------------------------------------------------------

# @app.get("/api/debug/config")
# def debug_config():
#     return {
#         "success": True,
#         "config": get_config_summary(),
#         "embedding_status": get_embedding_status(),
#         "ocr_status": get_ocr_status(),
#         "allowed_origins": allowed_origins,
#     }


# @app.post("/api/debug/search")
# def debug_vector_search(request: DebugSearchRequest):
#     if not request.session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     if not request.query or not request.query.strip():
#         raise HTTPException(status_code=400, detail="query is required.")

#     results = similarity_search_with_score(
#         session_id=request.session_id,
#         query=request.query,
#         top_k=request.top_k,
#     )

#     return {
#         "success": True,
#         "session_id": request.session_id,
#         "query": request.query,
#         "results": results,
#     }































# import os

# os.environ["TRANSFORMERS_VERBOSITY"] = "error"
# os.environ["TOKENIZERS_PARALLELISM"] = "false"

# import sys
# import re
# import json
# import uuid
# from pathlib import Path
# from typing import List, Optional, Dict, Any

# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field

# from groq import Groq


# # ---------------------------------------------------------
# # Path setup
# # ---------------------------------------------------------

# BACKEND_ROOT = Path(__file__).resolve().parent
# PROJECT_ROOT = BACKEND_ROOT.parent

# sys.path.append(str(BACKEND_ROOT))
# sys.path.append(str(PROJECT_ROOT))


# # ---------------------------------------------------------
# # RAG backend imports
# # ---------------------------------------------------------

# from src.config import (
#     APP_NAME,
#     APP_VERSION,
#     API_DESCRIPTION,
#     FRONTEND_URL,
#     CORS_ALLOWED_ORIGINS,
#     MAX_PDFS_PER_SESSION,
#     validate_upload_file,
#     get_config_summary,
#     get_backend_llm_model,
#     get_backend_top_k,
#     get_backend_search_type,
#     get_backend_answer_mode,
#     get_parallel_pdf_workers,
#     get_groq_api_key,
#     get_groq_model,
#     get_groq_max_tokens,
#     is_groq_configured,
# )

# from src.session_manager import (
#     create_user_folders,
#     get_session_summary,
#     clear_user_data,
#     clear_all_session_files,
#     clear_only_uploaded_files,
#     save_uploaded_pdf_bytes,
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

# from src.resume import (
#     analyze_resume_file_bytes_and_jd_with_rag,
#     extract_text_from_pdf_bytes,
#     extract_text_from_txt_bytes,
#     extract_text_from_docx_bytes,
# )


# # ---------------------------------------------------------
# # FastAPI app
# # ---------------------------------------------------------

# app = FastAPI(
#     title=APP_NAME,
#     version=APP_VERSION,
#     description=API_DESCRIPTION,
# )


# # ---------------------------------------------------------
# # CORS
# # ---------------------------------------------------------

# allowed_origins = list(
#     set(
#         [
#             FRONTEND_URL,
#             "http://localhost:5173",
#             "http://127.0.0.1:5173",
#             "http://localhost:3000",
#             "http://127.0.0.1:3000",
#             *CORS_ALLOWED_ORIGINS,
#         ]
#     )
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=allowed_origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # ---------------------------------------------------------
# # Pydantic request models
# # ---------------------------------------------------------

# class AskNotesRequest(BaseModel):
#     session_id: str
#     question: str


# class FlashcardRequest(BaseModel):
#     session_id: str


# class DebugSearchRequest(BaseModel):
#     session_id: str
#     query: str
#     top_k: int = 5


# class InterviewScoreRequest(BaseModel):
#     track: str = "General"
#     difficulty: str = "Fresher"
#     interview_title: str = ""
#     interview_role: str = ""
#     interview_company: str = ""
#     question_count: int = 15
#     skills: List[str] = Field(default_factory=list)

#     job_description: str = ""
#     resume_text: str = ""
#     resume_file_name: str = ""

#     transcript: List[Dict[str, Any]] = Field(default_factory=list)
#     transcript_text: str = ""
#     duration_seconds: int = 0

#     # New camera/speaking metrics from frontend
#     camera_metrics: Dict[str, Any] = Field(default_factory=dict)

#     eye_contact_score_estimate: Optional[float] = None
#     body_language_score_estimate: Optional[float] = None
#     speaking_pace_score_estimate: Optional[float] = None

#     face_visible_percent: Optional[float] = None
#     centered_face_percent: Optional[float] = None
#     eye_contact_percent: Optional[float] = None

#     movement_warnings: int = 0
#     face_missing_warnings: int = 0
#     off_center_warnings: int = 0
#     looking_away_warnings: int = 0

#     words_per_minute: Optional[float] = None
#     spoken_words: Optional[int] = None
#     warning_history: List[Dict[str, Any]] = Field(default_factory=list)


# # ---------------------------------------------------------
# # Utility helpers
# # ---------------------------------------------------------

# def create_session_id() -> str:
#     return str(uuid.uuid4())


# def clean_text(text: str) -> str:
#     if not text:
#         return ""

#     text = str(text)
#     text = text.replace("\x00", " ")
#     text = text.replace("\t", " ")
#     text = text.replace("\r", "\n")

#     lines = []

#     for line in text.splitlines():
#         line = line.strip()

#         if line:
#             lines.append(line)

#     return "\n".join(lines).strip()


# def limit_text(text: str, max_chars: int = 7000) -> str:
#     text = clean_text(text)

#     if len(text) <= max_chars:
#         return text

#     return text[:max_chars]


# def extract_text_from_upload_bytes(file_bytes: bytes, filename: str) -> str:
#     """
#     Extract readable text from uploaded PDF/DOCX/TXT bytes.
#     Used for JD upload in Resume Gap Finder.
#     """

#     if not file_bytes:
#         return ""

#     suffix = Path(filename or "").suffix.lower()

#     if suffix == ".pdf":
#         return extract_text_from_pdf_bytes(file_bytes)

#     if suffix == ".docx":
#         return extract_text_from_docx_bytes(file_bytes)

#     if suffix == ".txt":
#         return extract_text_from_txt_bytes(file_bytes)

#     raise ValueError("Only PDF, DOCX, and TXT files are supported.")


# def safe_float(value, fallback: float = 5.0) -> float:
#     try:
#         number = float(value)
#         return round(max(0.0, min(10.0, number)), 1)
#     except Exception:
#         return fallback


# def safe_optional_float(value):
#     try:
#         if value is None:
#             return None

#         number = float(value)
#         return round(max(0.0, min(10.0, number)), 1)
#     except Exception:
#         return None


# def safe_int(value, fallback: int = 0) -> int:
#     try:
#         return int(value)
#     except Exception:
#         return fallback


# def extract_json_from_text(text: str) -> Dict[str, Any]:
#     """
#     Groq may sometimes return extra text around JSON.
#     This safely extracts the first JSON object.
#     """

#     if not text:
#         return {}

#     text = text.strip()

#     try:
#         return json.loads(text)
#     except Exception:
#         pass

#     match = re.search(r"\{.*\}", text, re.DOTALL)

#     if not match:
#         return {}

#     try:
#         return json.loads(match.group(0))
#     except Exception:
#         return {}


# def parse_flashcards(raw_text: str) -> List[Dict[str, Any]]:
#     """
#     Converts LLM flashcard text into structured MCQ cards.
#     """

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


# def process_notes_for_session(session_id: str) -> Dict[str, Any]:
#     """
#     PDF processing + chunking + vector indexing pipeline.
#     """

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
#         "pdf_result": {
#             "success": pdf_result.get("success"),
#             "total_pdfs": pdf_result.get("total_pdfs"),
#             "total_documents": pdf_result.get("total_documents"),
#             "total_pages": pdf_result.get("total_pages"),
#             "total_images": pdf_result.get("total_images"),
#             "failed_pdfs": pdf_result.get("failed_pdfs"),
#             "parallel_workers": pdf_result.get("parallel_workers"),
#             "ocr_enabled": pdf_result.get("ocr_enabled"),
#             "image_extraction_enabled": pdf_result.get("image_extraction_enabled"),
#             "pdf_results": pdf_result.get("pdf_results", []),
#             "error": pdf_result.get("error"),
#         },
#         "index_result": index_result,
#         "message": "Notes processed successfully.",
#     }


# # ---------------------------------------------------------
# # Interview scoring helpers
# # ---------------------------------------------------------

# def build_interview_transcript_text(transcript: List[Dict[str, Any]]) -> str:
#     if not transcript:
#         return ""

#     lines = []

#     for item in transcript:
#         role = str(item.get("role", "")).strip()
#         content = str(item.get("content", "")).strip()

#         if not content:
#             continue

#         if role == "user":
#             label = "Candidate"
#         elif role == "assistant":
#             label = "AI Interviewer"
#         else:
#             label = role or "System"

#         lines.append(f"{label}: {content}")

#     return "\n".join(lines).strip()


# def get_transcript_stats(request: InterviewScoreRequest) -> Dict[str, Any]:
#     transcript = request.transcript or []

#     user_answers = [
#         str(message.get("content", "")).strip()
#         for message in transcript
#         if message.get("role") == "user" and str(message.get("content", "")).strip()
#     ]

#     assistant_questions = [
#         str(message.get("content", "")).strip()
#         for message in transcript
#         if message.get("role") == "assistant" and str(message.get("content", "")).strip()
#     ]

#     answer_word_counts = [
#         len(answer.split())
#         for answer in user_answers
#     ]

#     total_answer_words = sum(answer_word_counts)

#     avg_answer_words = (
#         total_answer_words / len(answer_word_counts)
#         if answer_word_counts
#         else 0
#     )

#     meaningful_answers = [
#         answer for answer in user_answers
#         if len(answer.split()) >= 8
#     ]

#     very_short_answers = [
#         answer for answer in user_answers
#         if len(answer.split()) <= 4
#     ]

#     return {
#         "total_messages": len(transcript),
#         "user_answers": user_answers,
#         "assistant_questions": assistant_questions,
#         "user_answer_count": len(user_answers),
#         "assistant_question_count": len(assistant_questions),
#         "answer_word_counts": answer_word_counts,
#         "total_answer_words": total_answer_words,
#         "avg_answer_words": avg_answer_words,
#         "meaningful_answer_count": len(meaningful_answers),
#         "very_short_answer_count": len(very_short_answers),
#     }


# def get_camera_metrics(request: InterviewScoreRequest) -> Dict[str, Any]:
#     """
#     Combine camera_metrics object and flat fields sent from frontend.
#     """

#     metrics = dict(request.camera_metrics or {})

#     def get_value(key, fallback=None):
#         value = metrics.get(key)

#         if value is None:
#             return fallback

#         return value

#     return {
#         "camera_metrics_available": bool(
#             get_value("cameraMetricsAvailable", False)
#             or get_value("camera_metrics_available", False)
#             or request.eye_contact_score_estimate is not None
#             or request.body_language_score_estimate is not None
#             or request.speaking_pace_score_estimate is not None
#         ),

#         "camera_ready": bool(
#             get_value("cameraReady", False)
#             or get_value("camera_ready", False)
#         ),

#         "face_detector_available": bool(
#             get_value("faceDetectorAvailable", False)
#             or get_value("face_detector_available", False)
#         ),

#         "eye_contact_score_estimate": safe_optional_float(
#             request.eye_contact_score_estimate
#             if request.eye_contact_score_estimate is not None
#             else get_value("eyeContactScoreEstimate")
#         ),

#         "body_language_score_estimate": safe_optional_float(
#             request.body_language_score_estimate
#             if request.body_language_score_estimate is not None
#             else get_value("bodyLanguageScoreEstimate")
#         ),

#         "speaking_pace_score_estimate": safe_optional_float(
#             request.speaking_pace_score_estimate
#             if request.speaking_pace_score_estimate is not None
#             else get_value("speakingPaceScoreEstimate")
#         ),

#         "face_visible_percent": safe_optional_float(
#             request.face_visible_percent
#             if request.face_visible_percent is not None
#             else get_value("faceVisiblePercent")
#         ),

#         "centered_face_percent": safe_optional_float(
#             request.centered_face_percent
#             if request.centered_face_percent is not None
#             else get_value("centeredFacePercent")
#         ),

#         "eye_contact_percent": safe_optional_float(
#             request.eye_contact_percent
#             if request.eye_contact_percent is not None
#             else get_value("eyeContactPercent")
#         ),

#         "movement_warnings": safe_int(
#             request.movement_warnings
#             if request.movement_warnings is not None
#             else get_value("movementWarnings"),
#             0,
#         ),

#         "face_missing_warnings": safe_int(
#             request.face_missing_warnings
#             if request.face_missing_warnings is not None
#             else get_value("faceMissingWarnings"),
#             0,
#         ),

#         "off_center_warnings": safe_int(
#             request.off_center_warnings
#             if request.off_center_warnings is not None
#             else get_value("offCenterWarnings"),
#             0,
#         ),

#         "looking_away_warnings": safe_int(
#             request.looking_away_warnings
#             if request.looking_away_warnings is not None
#             else get_value("lookingAwayWarnings"),
#             0,
#         ),

#         "words_per_minute": safe_optional_float(
#             request.words_per_minute
#             if request.words_per_minute is not None
#             else get_value("wordsPerMinute")
#         ),

#         "spoken_words": safe_int(
#             request.spoken_words
#             if request.spoken_words is not None
#             else get_value("spokenWords"),
#             0,
#         ),

#         "warning_history": request.warning_history
#         if request.warning_history
#         else get_value("warningHistory", []),
#     }


# def get_fallback_interview_score(request: InterviewScoreRequest) -> Dict[str, Any]:
#     """
#     Fallback scoring:
#     - transcript quality decides main score
#     - frontend camera estimates fill eye contact/body language/speaking pace
#     """

#     stats = get_transcript_stats(request)
#     camera = get_camera_metrics(request)

#     user_answer_count = stats["user_answer_count"]
#     assistant_question_count = stats["assistant_question_count"]
#     avg_answer_words = stats["avg_answer_words"]
#     meaningful_answer_count = stats["meaningful_answer_count"]
#     very_short_answer_count = stats["very_short_answer_count"]
#     total_messages = stats["total_messages"]

#     score = 5.5

#     if user_answer_count == 0:
#         score = 3.0
#     elif user_answer_count == 1:
#         score = 5.0
#     elif user_answer_count >= 2:
#         score = 6.0

#     if user_answer_count >= 3:
#         score += 0.5

#     if user_answer_count >= 5:
#         score += 0.4

#     if avg_answer_words >= 8:
#         score += 0.4

#     if avg_answer_words >= 15:
#         score += 0.5

#     if avg_answer_words >= 25:
#         score += 0.5

#     if avg_answer_words >= 40:
#         score += 0.4

#     if meaningful_answer_count >= 2:
#         score += 0.4

#     if meaningful_answer_count >= 4:
#         score += 0.4

#     if very_short_answer_count >= max(2, user_answer_count // 2):
#         score -= 0.8

#     if total_messages < 3:
#         score = min(score, 4.5)

#     score = safe_float(score, 5.5)

#     communication = safe_float(score + 0.1, score)
#     confidence = safe_float(score, score)

#     body_language = camera["body_language_score_estimate"]
#     eye_contact = camera["eye_contact_score_estimate"]
#     speaking_pace = camera["speaking_pace_score_estimate"]

#     if body_language is None:
#         body_language = 6.5 if camera["camera_metrics_available"] else 6.0

#     if eye_contact is None:
#         eye_contact = 6.5 if camera["camera_metrics_available"] else 6.0

#     if speaking_pace is None:
#         speaking_pace = 6.8

#     return {
#         "success": True,
#         "score_overall": score,
#         "score_communication": communication,
#         "score_confidence": confidence,

#         "score_body_language": safe_float(body_language, 6.0),
#         "score_eye_contact": safe_float(eye_contact, 6.0),
#         "score_speaking_pace": safe_float(speaking_pace, 6.8),

#         "camera_metrics_available": camera["camera_metrics_available"],
#         "non_verbal_metrics_counted": True,

#         "overallSummary": (
#             "Interview completed. Groq detailed scoring was not available, "
#             "so fallback scoring used transcript quality plus camera/speaking estimates."
#         ),
#         "improvementTips": [
#             "Give answers with a little more explanation and examples.",
#             "Try to answer in a clear structure: point, explanation, example.",
#             "Maintain eye contact by keeping your face centered in the camera.",
#             "Sit steady and avoid unnecessary movement.",
#         ],
#         "strengths": [
#             "Candidate participated in the interview.",
#         ],
#         "weaknesses": [
#             "Detailed Groq scoring was unavailable, so fallback evaluation was used.",
#         ],
#         "scoreReason": (
#             f"Fallback score based on {user_answer_count} candidate answers, "
#             f"{assistant_question_count} AI questions, average answer length "
#             f"of {avg_answer_words:.1f} words, and frontend camera/speaking estimates."
#         ),
#         "totalMessages": total_messages,
#         "userAnswers": user_answer_count,
#         "aiQuestions": assistant_question_count,
#         "durationSeconds": request.duration_seconds,
#         "cameraMetrics": camera,
#         "provider": "fallback",
#         "model": "fallback",
#     }


# def score_interview_with_groq(request: InterviewScoreRequest) -> Dict[str, Any]:
#     """
#     Groq scoring using:
#     - transcript answer quality
#     - frontend camera metrics
#     - frontend speaking pace estimate
#     """

#     if not is_groq_configured():
#         raise ValueError("GROQ_API_KEY is missing. Add GROQ_API_KEY in your .env file.")

#     transcript_text = request.transcript_text or build_interview_transcript_text(
#         request.transcript
#     )

#     if not transcript_text:
#         raise ValueError("Transcript is empty. Cannot score interview.")

#     stats = get_transcript_stats(request)
#     camera = get_camera_metrics(request)

#     system_prompt = """
# You are an expert mock interview evaluator for students and freshers.

# You will score the interview from two sources:
# 1. Transcript answer quality.
# 2. Frontend measured camera/speaking metrics.

# Important rules:
# 1. Overall score must mainly depend on transcript answer quality.
# 2. Eye contact score must use the provided eye contact/camera metrics.
# 3. Body language score must use the provided posture/face-center/movement metrics.
# 4. Speaking pace score must use provided words-per-minute and speaking pace estimate.
# 5. Do not invent camera data. Use only provided camera metrics.
# 6. If camera metrics are weak, give lower eye contact/body language score.
# 7. If camera metrics are good, give fair/good eye contact/body language score.
# 8. Be fair for fresher-level interviews.
# 9. Do not give a fixed score.
# 10. Use score range 0 to 10.
# 11. Return ONLY valid JSON.
# 12. Do not wrap JSON in markdown.

# Scoring philosophy:
# - A normal fresher with relevant but simple answers should usually be around 6.5 to 7.5 overall.
# - Strong, clear, structured, role-relevant answers should be 8.0+ overall.
# - Very short, irrelevant, or missing answers should be below 6 overall.
# - Only mostly silent/no meaningful responses should be below 4 overall.
# - Eye contact/body language/speaking pace can differ from overall score.
# """

#     user_prompt = f"""
# Interview Setup:
# - Title: {request.interview_title}
# - Track: {request.track}
# - Difficulty: {request.difficulty}
# - Role: {request.interview_role}
# - Company: {request.interview_company}
# - Question Count: {request.question_count}
# - Skills: {", ".join(request.skills or [])}
# - Resume File: {request.resume_file_name}
# - Duration Seconds: {request.duration_seconds}

# Transcript Stats:
# - Total Messages: {stats["total_messages"]}
# - Candidate Answers: {stats["user_answer_count"]}
# - AI Questions: {stats["assistant_question_count"]}
# - Average Candidate Answer Words: {stats["avg_answer_words"]:.1f}
# - Meaningful Answers Count: {stats["meaningful_answer_count"]}
# - Very Short Answers Count: {stats["very_short_answer_count"]}

# Camera And Speaking Metrics:
# - Camera Metrics Available: {camera["camera_metrics_available"]}
# - Camera Ready: {camera["camera_ready"]}
# - Face Detector Available: {camera["face_detector_available"]}

# - Eye Contact Score Estimate From Frontend: {camera["eye_contact_score_estimate"]}
# - Body Language Score Estimate From Frontend: {camera["body_language_score_estimate"]}
# - Speaking Pace Score Estimate From Frontend: {camera["speaking_pace_score_estimate"]}

# - Face Visible Percent: {camera["face_visible_percent"]}
# - Centered Face Percent: {camera["centered_face_percent"]}
# - Eye Contact Percent: {camera["eye_contact_percent"]}

# - Movement Warnings: {camera["movement_warnings"]}
# - Face Missing Warnings: {camera["face_missing_warnings"]}
# - Off Center Warnings: {camera["off_center_warnings"]}
# - Looking Away Warnings: {camera["looking_away_warnings"]}

# - Words Per Minute: {camera["words_per_minute"]}
# - Spoken Words: {camera["spoken_words"]}

# Recent Camera Warning History:
# {json.dumps(camera["warning_history"][-12:], indent=2)}

# Job Description:
# {limit_text(request.job_description, 2200)}

# Resume Text:
# {limit_text(request.resume_text, 2200)}

# Transcript:
# {limit_text(transcript_text, 9000)}

# Return ONLY this JSON format:

# {{
#   "success": true,
#   "score_overall": 0,
#   "score_communication": 0,
#   "score_confidence": 0,
#   "score_body_language": 0,
#   "score_eye_contact": 0,
#   "score_speaking_pace": 0,
#   "camera_metrics_available": true,
#   "non_verbal_metrics_counted": true,
#   "overallSummary": "short honest summary",
#   "improvementTips": [
#     "tip 1",
#     "tip 2",
#     "tip 3"
#   ],
#   "strengths": [
#     "strength 1",
#     "strength 2"
#   ],
#   "weaknesses": [
#     "weakness 1",
#     "weakness 2"
#   ],
#   "scoreReason": "why this score was given"
# }}

# Scoring guide:
# - Overall: score based mainly on transcript answer quality.
# - Communication: clarity, structure, relevance, answer completeness.
# - Confidence: answer completeness, directness, hesitation signs from transcript.
# - Body Language: use bodyLanguageScoreEstimate, centeredFacePercent, movementWarnings, faceMissingWarnings.
# - Eye Contact: use eyeContactScoreEstimate, eyeContactPercent, faceVisiblePercent, lookingAwayWarnings.
# - Speaking Pace: use speakingPaceScoreEstimate and wordsPerMinute.

# Important:
# - Do not give 0 for body language/eye contact/speaking pace if metrics are available.
# - If camera metrics are unavailable, use a neutral score around 6.0 to 6.8 and mention limited camera data.
# - Keep all scores realistic and varied.
# """

#     client = Groq(api_key=get_groq_api_key())

#     try:
#         max_tokens = min(int(get_groq_max_tokens() or 1400), 1600)
#     except Exception:
#         max_tokens = 1400

#     response = client.chat.completions.create(
#         model=get_groq_model(),
#         messages=[
#             {
#                 "role": "system",
#                 "content": system_prompt,
#             },
#             {
#                 "role": "user",
#                 "content": user_prompt,
#             },
#         ],
#         temperature=0.25,
#         max_tokens=max_tokens,
#     )

#     raw_answer = response.choices[0].message.content.strip()

#     parsed = extract_json_from_text(raw_answer)

#     if not parsed:
#         raise ValueError("Groq did not return valid JSON scoring output.")

#     score_overall = safe_float(parsed.get("score_overall"), 6.5)

#     body_language_fallback = (
#         camera["body_language_score_estimate"]
#         if camera["body_language_score_estimate"] is not None
#         else 6.5
#     )

#     eye_contact_fallback = (
#         camera["eye_contact_score_estimate"]
#         if camera["eye_contact_score_estimate"] is not None
#         else 6.5
#     )

#     speaking_pace_fallback = (
#         camera["speaking_pace_score_estimate"]
#         if camera["speaking_pace_score_estimate"] is not None
#         else 6.8
#     )

#     result = {
#         "success": True,

#         "score_overall": score_overall,
#         "score_communication": safe_float(
#             parsed.get("score_communication"),
#             score_overall,
#         ),
#         "score_confidence": safe_float(
#             parsed.get("score_confidence"),
#             score_overall,
#         ),

#         "score_body_language": safe_float(
#             parsed.get("score_body_language"),
#             body_language_fallback,
#         ),
#         "score_eye_contact": safe_float(
#             parsed.get("score_eye_contact"),
#             eye_contact_fallback,
#         ),
#         "score_speaking_pace": safe_float(
#             parsed.get("score_speaking_pace"),
#             speaking_pace_fallback,
#         ),

#         "camera_metrics_available": bool(
#             parsed.get("camera_metrics_available", camera["camera_metrics_available"])
#         ),
#         "non_verbal_metrics_counted": True,

#         "overallSummary": parsed.get("overallSummary")
#         or parsed.get("overall_summary")
#         or "Interview scored successfully from transcript and camera metrics.",
#         "improvementTips": parsed.get("improvementTips")
#         or parsed.get("improvement_tips")
#         or [],
#         "strengths": parsed.get("strengths") or [],
#         "weaknesses": parsed.get("weaknesses") or [],
#         "scoreReason": parsed.get("scoreReason")
#         or parsed.get("score_reason")
#         or "Score generated from transcript answer quality plus camera/speaking metrics.",

#         "cameraMetrics": camera,
#         "provider": "groq",
#         "model": get_groq_model(),
#         "raw": raw_answer,
#     }

#     return result


# # ---------------------------------------------------------
# # Root + health
# # ---------------------------------------------------------

# @app.get("/")
# def root():
#     return {
#         "success": True,
#         "message": "InterviewIQ RAG Backend is running",
#         "docs": "/docs",
#         "health": "/health",
#     }


# @app.get("/health")
# def health_check():
#     return {
#         "success": True,
#         "status": "ok",
#         "service": "InterviewIQ RAG Backend",
#         "version": APP_VERSION,
#     }


# # ---------------------------------------------------------
# # Notes upload + process
# # ---------------------------------------------------------

# @app.post("/api/notes/upload")
# async def upload_notes(
#     files: List[UploadFile] = File(...),
#     session_id: Optional[str] = Form(None),
# ):
#     """
#     Upload PDF notes, save them in session storage, process PDFs, and create vector DB.
#     """

#     if not files:
#         raise HTTPException(status_code=400, detail="No PDF files uploaded.")

#     if len(files) > MAX_PDFS_PER_SESSION:
#         raise HTTPException(
#             status_code=400,
#             detail=f"You can upload maximum {MAX_PDFS_PER_SESSION} PDFs per session.",
#         )

#     active_session_id = session_id or create_session_id()
#     create_user_folders(active_session_id)

#     saved_paths = []
#     invalid_files = []

#     for uploaded_file in files:
#         filename = uploaded_file.filename or "uploaded.pdf"

#         file_bytes = await uploaded_file.read()
#         file_size = len(file_bytes)

#         validation = validate_upload_file(
#             filename=filename,
#             size_bytes=file_size,
#         )

#         if not validation["valid"]:
#             invalid_files.append(
#                 {
#                     "name": filename,
#                     "message": validation["message"],
#                 }
#             )
#             continue

#         destination = save_uploaded_pdf_bytes(
#             file_bytes=file_bytes,
#             session_id=active_session_id,
#             original_filename=filename,
#         )

#         saved_paths.append(str(destination))

#     if invalid_files:
#         return {
#             "success": False,
#             "session_id": active_session_id,
#             "saved_paths": saved_paths,
#             "invalid_files": invalid_files,
#             "message": "Some files are invalid.",
#         }

#     if not saved_paths:
#         raise HTTPException(
#             status_code=400,
#             detail="No valid PDF files were uploaded.",
#         )

#     process_result = process_notes_for_session(active_session_id)

#     return {
#         "success": process_result.get("success", False),
#         "session_id": active_session_id,
#         "saved_paths": saved_paths,
#         "process_result": process_result,
#         "vector_status": get_vector_store_status(active_session_id),
#         "session_summary": get_session_summary(active_session_id),
#         "message": process_result.get("message", "Upload completed."),
#     }


# @app.post("/api/notes/process")
# def process_existing_notes(session_id: str = Form(...)):
#     """
#     Re-process PDFs already saved under a session.
#     """

#     if not session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     create_user_folders(session_id)

#     process_result = process_notes_for_session(session_id)

#     return {
#         "success": process_result.get("success", False),
#         "session_id": session_id,
#         "process_result": process_result,
#         "vector_status": get_vector_store_status(session_id),
#         "session_summary": get_session_summary(session_id),
#         "message": process_result.get("message", "Processing completed."),
#     }


# @app.post("/api/notes/ask")
# def ask_notes_question(request: AskNotesRequest):
#     """
#     Ask question from uploaded notes.
#     """

#     if not request.session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     if not request.question or not request.question.strip():
#         raise HTTPException(status_code=400, detail="question is required.")

#     rag_ready = check_rag_ready(request.session_id)

#     if not rag_ready:
#         raise HTTPException(
#             status_code=400,
#             detail="RAG is not ready. Please upload and process notes first.",
#         )

#     result = ask_rag(
#         session_id=request.session_id,
#         question=request.question,
#         model_name=get_backend_llm_model(),
#         top_k=get_backend_top_k(),
#         search_type=get_backend_search_type(),
#         answer_mode=get_backend_answer_mode(),
#     )

#     return {
#         "success": result.get("success", True),
#         "session_id": request.session_id,
#         "question": request.question,
#         "answer": result.get("answer", "No answer generated."),
#         "sources": result.get("sources", []),
#         "provider": result.get("provider"),
#         "model": result.get("model"),
#         "retrieved_chunks": result.get("retrieved_chunks", 0),
#     }


# # ---------------------------------------------------------
# # Study tools
# # ---------------------------------------------------------

# @app.post("/api/notes/summarize")
# def summarize_uploaded_notes(session_id: str = Form(...)):
#     if not session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     rag_ready = check_rag_ready(session_id)

#     if not rag_ready:
#         raise HTTPException(
#             status_code=400,
#             detail="RAG is not ready. Please upload and process notes first.",
#         )

#     result = summarize_notes(
#         session_id=session_id,
#         model_name=get_backend_llm_model(),
#     )

#     return {
#         "success": result.get("success", True),
#         "session_id": session_id,
#         "answer": result.get("answer", ""),
#         "sources": result.get("sources", []),
#         "provider": result.get("provider"),
#         "model": result.get("model"),
#         "retrieved_chunks": result.get("retrieved_chunks", 0),
#     }


# @app.post("/api/notes/questions")
# def generate_notes_questions(session_id: str = Form(...)):
#     if not session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     rag_ready = check_rag_ready(session_id)

#     if not rag_ready:
#         raise HTTPException(
#             status_code=400,
#             detail="RAG is not ready. Please upload and process notes first.",
#         )

#     result = generate_questions(
#         session_id=session_id,
#         model_name=get_backend_llm_model(),
#     )

#     return {
#         "success": result.get("success", True),
#         "session_id": session_id,
#         "answer": result.get("answer", ""),
#         "sources": result.get("sources", []),
#         "provider": result.get("provider"),
#         "model": result.get("model"),
#         "retrieved_chunks": result.get("retrieved_chunks", 0),
#     }


# @app.post("/api/flashcards/generate")
# def generate_notes_flashcards(request: FlashcardRequest):
#     if not request.session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     rag_ready = check_rag_ready(request.session_id)

#     if not rag_ready:
#         raise HTTPException(
#             status_code=400,
#             detail="RAG is not ready. Please upload and process notes first.",
#         )

#     result = generate_flashcards(
#         session_id=request.session_id,
#         model_name=get_backend_llm_model(),
#     )

#     raw_answer = result.get("answer", "")
#     parsed_cards = parse_flashcards(raw_answer)

#     return {
#         "success": result.get("success", True),
#         "session_id": request.session_id,
#         "raw": raw_answer,
#         "flashcards": parsed_cards,
#         "sources": result.get("sources", []),
#         "total_flashcards": len(parsed_cards),
#         "provider": result.get("provider"),
#         "model": result.get("model"),
#         "retrieved_chunks": result.get("retrieved_chunks", 0),
#     }


# # ---------------------------------------------------------
# # Resume Gap Finder
# # ---------------------------------------------------------

# @app.post("/api/resume/gap-analysis")
# async def resume_gap_analysis(
#     resume: UploadFile = File(...),
#     jd_file: Optional[UploadFile] = File(None),
#     job_description: str = Form(""),
#     session_id: Optional[str] = Form(None),
# ):
#     """
#     Resume Gap Finder:
#     Upload resume + either pasted JD or uploaded JD file, then compare using RAG + Groq.
#     """

#     if resume is None:
#         raise HTTPException(status_code=400, detail="Resume file is required.")

#     active_session_id = session_id or create_session_id()

#     resume_bytes = await resume.read()

#     if not resume_bytes:
#         raise HTTPException(status_code=400, detail="Resume file is empty.")

#     final_jd_text = clean_text(job_description or "")
#     jd_filename = "pasted_job_description"

#     if jd_file is not None:
#         jd_bytes = await jd_file.read()

#         if not jd_bytes:
#             raise HTTPException(status_code=400, detail="JD file is empty.")

#         try:
#             extracted_jd_text = extract_text_from_upload_bytes(
#                 file_bytes=jd_bytes,
#                 filename=jd_file.filename or "job_description",
#             )
#         except Exception as e:
#             raise HTTPException(status_code=400, detail=str(e))

#         extracted_jd_text = clean_text(extracted_jd_text)

#         if extracted_jd_text:
#             final_jd_text = extracted_jd_text
#             jd_filename = jd_file.filename or "job_description"

#     if not final_jd_text:
#         raise HTTPException(
#             status_code=400,
#             detail="Please upload JD file or paste job description.",
#         )

#     result = analyze_resume_file_bytes_and_jd_with_rag(
#         base_session_id=active_session_id,
#         resume_bytes=resume_bytes,
#         resume_filename=resume.filename or "resume.pdf",
#         jd_text=final_jd_text,
#         jd_filename=jd_filename,
#     )

#     return {
#         "success": result.get("success", False),
#         "session_id": active_session_id,
#         "answer": result.get("answer", ""),
#         "data": result.get("data"),
#         "structured": result.get("structured"),
#         "resume_text": result.get("resume_text", ""),
#         "jd_text": result.get("jd_text", ""),
#         "rag_context": result.get("rag_context", ""),
#         "resume_rag_session_id": result.get("resume_rag_session_id"),
#         "retrieved_chunks": result.get("retrieved_chunks", 0),
#         "total_chunks": result.get("total_chunks", 0),
#         "model": result.get("model"),
#         "provider": result.get("provider"),
#     }


# # ---------------------------------------------------------
# # Interview Scoring
# # ---------------------------------------------------------

# @app.post("/api/interview/score")
# def score_interview(request: InterviewScoreRequest):
#     """
#     Score Vapi interview transcript using Groq.

#     Now includes:
#     - transcript scoring
#     - camera metrics
#     - eye contact estimate
#     - body language estimate
#     - speaking pace estimate
#     """

#     if not request.transcript and not request.transcript_text:
#         raise HTTPException(
#             status_code=400,
#             detail="Transcript is required for scoring.",
#         )

#     try:
#         result = score_interview_with_groq(request)
#         return result

#     except Exception as e:
#         fallback = get_fallback_interview_score(request)
#         fallback["groq_error"] = str(e)
#         return fallback


# # ---------------------------------------------------------
# # Session status + clear
# # ---------------------------------------------------------

# @app.get("/api/session/{session_id}/summary")
# def session_summary(session_id: str):
#     return {
#         "success": True,
#         "session_id": session_id,
#         "session_summary": get_session_summary(session_id),
#         "pdf_summary": get_session_pdf_summary(session_id),
#         "vector_status": get_vector_store_status(session_id),
#         "rag_ready": check_rag_ready(session_id),
#     }


# @app.delete("/api/session/{session_id}/clear")
# def clear_session(session_id: str, full_clear: bool = False):
#     if full_clear:
#         clear_all_session_files(session_id)
#     else:
#         clear_user_data(session_id)

#     return {
#         "success": True,
#         "session_id": session_id,
#         "full_clear": full_clear,
#         "message": "Session data cleared.",
#     }


# @app.delete("/api/session/{session_id}/uploaded-files")
# def clear_uploaded_files(session_id: str):
#     clear_only_uploaded_files(session_id)
#     clear_user_data(session_id)

#     return {
#         "success": True,
#         "session_id": session_id,
#         "message": "Uploaded PDFs and processed data cleared.",
#     }


# # ---------------------------------------------------------
# # Debug endpoints
# # ---------------------------------------------------------

# @app.get("/api/debug/config")
# def debug_config():
#     return {
#         "success": True,
#         "config": get_config_summary(),
#         "embedding_status": get_embedding_status(),
#         "ocr_status": get_ocr_status(),
#         "allowed_origins": allowed_origins,
#     }


# @app.post("/api/debug/search")
# def debug_vector_search(request: DebugSearchRequest):
#     if not request.session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     if not request.query or not request.query.strip():
#         raise HTTPException(status_code=400, detail="query is required.")

#     results = similarity_search_with_score(
#         session_id=request.session_id,
#         query=request.query,
#         top_k=request.top_k,
#     )

#     return {
#         "success": True,
#         "session_id": request.session_id,
#         "query": request.query,
#         "results": results,
#     }




















# import os

# os.environ["TRANSFORMERS_VERBOSITY"] = "error"
# os.environ["TOKENIZERS_PARALLELISM"] = "false"

# import sys
# import re
# import json
# import uuid
# import time
# from pathlib import Path
# from typing import List, Optional, Dict, Any

# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field


# # ---------------------------------------------------------
# # Path setup
# # ---------------------------------------------------------

# BACKEND_ROOT = Path(__file__).resolve().parent
# PROJECT_ROOT = BACKEND_ROOT.parent

# sys.path.append(str(BACKEND_ROOT))
# sys.path.append(str(PROJECT_ROOT))


# # ---------------------------------------------------------
# # Lightweight imports only
# # Heavy RAG / embedding / PDF modules are imported lazily inside endpoints.
# # This fixes slow deployment startup.
# # ---------------------------------------------------------

# from src.config import (
#     APP_NAME,
#     APP_VERSION,
#     API_DESCRIPTION,
#     FRONTEND_URL,
#     CORS_ALLOWED_ORIGINS,
#     MAX_PDFS_PER_SESSION,
#     validate_upload_file,
#     get_config_summary,
#     get_backend_llm_model,
#     get_groq_api_key,
#     get_groq_model,
#     get_groq_max_tokens,
#     is_groq_configured,
# )

# from src.session_manager import (
#     create_user_folders,
#     get_session_summary,
#     clear_user_data,
#     clear_all_session_files,
#     clear_only_uploaded_files,
#     save_uploaded_pdf_bytes,
# )


# APP_START_TIME = time.time()


# # ---------------------------------------------------------
# # FastAPI app
# # ---------------------------------------------------------

# app = FastAPI(
#     title=APP_NAME,
#     version=APP_VERSION,
#     description=API_DESCRIPTION,
# )


# # ---------------------------------------------------------
# # CORS FIX
# # ---------------------------------------------------------

# allowed_origins = list(
#     set(
#         [
#             FRONTEND_URL,

#             # Vite ports
#             "http://localhost:5173",
#             "http://127.0.0.1:5173",
#             "http://localhost:5174",
#             "http://127.0.0.1:5174",
#             "http://localhost:5175",
#             "http://127.0.0.1:5175",

#             # React / Next ports
#             "http://localhost:3000",
#             "http://127.0.0.1:3000",
#             "http://localhost:3001",
#             "http://127.0.0.1:3001",

#             # Backend itself
#             "http://localhost:8000",
#             "http://127.0.0.1:8000",

#             *CORS_ALLOWED_ORIGINS,
#         ]
#     )
# )

# allowed_origins = [
#     origin.strip()
#     for origin in allowed_origins
#     if origin and origin.strip()
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=allowed_origins,
#     allow_origin_regex=(
#         r"https?://(localhost|127\.0\.0\.1)(:\d+)?"
#         r"|https://.*\.vercel\.app"
#         r"|https://.*\.netlify\.app"
#         r"|https://.*\.onrender\.com"
#     ),
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # ---------------------------------------------------------
# # Pydantic request models
# # ---------------------------------------------------------

# class AskNotesRequest(BaseModel):
#     session_id: str
#     question: str


# class FlashcardRequest(BaseModel):
#     session_id: str


# class DebugSearchRequest(BaseModel):
#     session_id: str
#     query: str
#     top_k: int = 10


# class InterviewScoreRequest(BaseModel):
#     track: str = "General"
#     difficulty: str = "Fresher"
#     interview_title: str = ""
#     interview_role: str = ""
#     interview_company: str = ""
#     question_count: int = 15
#     skills: List[str] = Field(default_factory=list)

#     job_description: str = ""
#     resume_text: str = ""
#     resume_file_name: str = ""

#     transcript: List[Dict[str, Any]] = Field(default_factory=list)
#     transcript_text: str = ""
#     duration_seconds: int = 0

#     camera_metrics: Dict[str, Any] = Field(default_factory=dict)

#     eye_contact_score_estimate: Optional[float] = None
#     body_language_score_estimate: Optional[float] = None
#     speaking_pace_score_estimate: Optional[float] = None

#     face_visible_percent: Optional[float] = None
#     centered_face_percent: Optional[float] = None
#     eye_contact_percent: Optional[float] = None

#     movement_warnings: int = 0
#     face_missing_warnings: int = 0
#     off_center_warnings: int = 0
#     looking_away_warnings: int = 0

#     words_per_minute: Optional[float] = None
#     spoken_words: Optional[int] = None
#     warning_history: List[Dict[str, Any]] = Field(default_factory=list)


# # ---------------------------------------------------------
# # Utility helpers
# # ---------------------------------------------------------

# def create_session_id() -> str:
#     return str(uuid.uuid4())


# def clean_text(text: str) -> str:
#     if not text:
#         return ""

#     text = str(text)
#     text = text.replace("\x00", " ")
#     text = text.replace("\t", " ")
#     text = text.replace("\r", "\n")

#     lines = []

#     for line in text.splitlines():
#         line = line.strip()

#         if line:
#             lines.append(line)

#     return "\n".join(lines).strip()


# def limit_text(text: str, max_chars: int = 7000) -> str:
#     text = clean_text(text)

#     if len(text) <= max_chars:
#         return text

#     return text[:max_chars]


# def safe_float(value, fallback: float = 5.0) -> float:
#     try:
#         number = float(value)
#         return round(max(0.0, min(10.0, number)), 1)
#     except Exception:
#         return fallback


# def safe_optional_float(value):
#     try:
#         if value is None:
#             return None

#         number = float(value)
#         return round(max(0.0, min(10.0, number)), 1)
#     except Exception:
#         return None


# def safe_int(value, fallback: int = 0) -> int:
#     try:
#         return int(value)
#     except Exception:
#         return fallback


# def extract_json_from_text(text: str) -> Dict[str, Any]:
#     if not text:
#         return {}

#     text = text.strip()

#     try:
#         return json.loads(text)
#     except Exception:
#         pass

#     match = re.search(r"\{.*\}", text, re.DOTALL)

#     if not match:
#         return {}

#     try:
#         return json.loads(match.group(0))
#     except Exception:
#         return {}


# def extract_text_from_upload_bytes(file_bytes: bytes, filename: str) -> str:
#     """
#     Lazy import resume text extractors.
#     This avoids loading PDF/DOCX libraries at app startup.
#     """

#     if not file_bytes:
#         return ""

#     from src.resume import (
#         extract_text_from_pdf_bytes,
#         extract_text_from_txt_bytes,
#         extract_text_from_docx_bytes,
#     )

#     suffix = Path(filename or "").suffix.lower()

#     if suffix == ".pdf":
#         return extract_text_from_pdf_bytes(file_bytes)

#     if suffix == ".docx":
#         return extract_text_from_docx_bytes(file_bytes)

#     if suffix == ".txt":
#         return extract_text_from_txt_bytes(file_bytes)

#     raise ValueError("Only PDF, DOCX, and TXT files are supported.")


# def parse_flashcards(raw_text: str) -> List[Dict[str, Any]]:
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


# def process_notes_for_session(session_id: str) -> Dict[str, Any]:
#     """
#     PDF processing + chunking + vector indexing pipeline.

#     Lazy imports keep backend startup fast on Render/local.
#     """

#     from src.config import get_parallel_pdf_workers
#     from src.pdf_processor import process_uploaded_pdfs_for_session
#     from src.vector_store import index_documents_pipeline

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
#         "pdf_result": {
#             "success": pdf_result.get("success"),
#             "total_pdfs": pdf_result.get("total_pdfs"),
#             "total_documents": pdf_result.get("total_documents"),
#             "total_pages": pdf_result.get("total_pages"),
#             "total_images": pdf_result.get("total_images"),
#             "failed_pdfs": pdf_result.get("failed_pdfs"),
#             "parallel_workers": pdf_result.get("parallel_workers"),
#             "ocr_enabled": pdf_result.get("ocr_enabled"),
#             "image_extraction_enabled": pdf_result.get("image_extraction_enabled"),
#             "pdf_results": pdf_result.get("pdf_results", []),
#             "error": pdf_result.get("error"),
#         },
#         "index_result": index_result,
#         "message": "Notes processed successfully.",
#     }


# # ---------------------------------------------------------
# # Interview scoring helpers
# # ---------------------------------------------------------

# def build_interview_transcript_text(transcript: List[Dict[str, Any]]) -> str:
#     if not transcript:
#         return ""

#     lines = []

#     for item in transcript:
#         role = str(item.get("role", "")).strip()
#         content = str(item.get("content", "")).strip()

#         if not content:
#             continue

#         if role == "user":
#             label = "Candidate"
#         elif role == "assistant":
#             label = "AI Interviewer"
#         else:
#             label = role or "System"

#         lines.append(f"{label}: {content}")

#     return "\n".join(lines).strip()


# def get_transcript_stats(request: InterviewScoreRequest) -> Dict[str, Any]:
#     transcript = request.transcript or []

#     user_answers = [
#         str(message.get("content", "")).strip()
#         for message in transcript
#         if message.get("role") == "user" and str(message.get("content", "")).strip()
#     ]

#     assistant_questions = [
#         str(message.get("content", "")).strip()
#         for message in transcript
#         if message.get("role") == "assistant" and str(message.get("content", "")).strip()
#     ]

#     answer_word_counts = [
#         len(answer.split())
#         for answer in user_answers
#     ]

#     total_answer_words = sum(answer_word_counts)

#     avg_answer_words = (
#         total_answer_words / len(answer_word_counts)
#         if answer_word_counts
#         else 0
#     )

#     meaningful_answers = [
#         answer for answer in user_answers
#         if len(answer.split()) >= 8
#     ]

#     very_short_answers = [
#         answer for answer in user_answers
#         if len(answer.split()) <= 4
#     ]

#     return {
#         "total_messages": len(transcript),
#         "user_answers": user_answers,
#         "assistant_questions": assistant_questions,
#         "user_answer_count": len(user_answers),
#         "assistant_question_count": len(assistant_questions),
#         "answer_word_counts": answer_word_counts,
#         "total_answer_words": total_answer_words,
#         "avg_answer_words": avg_answer_words,
#         "meaningful_answer_count": len(meaningful_answers),
#         "very_short_answer_count": len(very_short_answers),
#     }


# def get_camera_metrics(request: InterviewScoreRequest) -> Dict[str, Any]:
#     metrics = dict(request.camera_metrics or {})

#     def get_value(key, fallback=None):
#         value = metrics.get(key)

#         if value is None:
#             return fallback

#         return value

#     return {
#         "camera_metrics_available": bool(
#             get_value("cameraMetricsAvailable", False)
#             or get_value("camera_metrics_available", False)
#             or request.eye_contact_score_estimate is not None
#             or request.body_language_score_estimate is not None
#             or request.speaking_pace_score_estimate is not None
#         ),
#         "camera_ready": bool(
#             get_value("cameraReady", False)
#             or get_value("camera_ready", False)
#         ),
#         "face_detector_available": bool(
#             get_value("faceDetectorAvailable", False)
#             or get_value("face_detector_available", False)
#         ),
#         "eye_contact_score_estimate": safe_optional_float(
#             request.eye_contact_score_estimate
#             if request.eye_contact_score_estimate is not None
#             else get_value("eyeContactScoreEstimate")
#         ),
#         "body_language_score_estimate": safe_optional_float(
#             request.body_language_score_estimate
#             if request.body_language_score_estimate is not None
#             else get_value("bodyLanguageScoreEstimate")
#         ),
#         "speaking_pace_score_estimate": safe_optional_float(
#             request.speaking_pace_score_estimate
#             if request.speaking_pace_score_estimate is not None
#             else get_value("speakingPaceScoreEstimate")
#         ),
#         "face_visible_percent": safe_optional_float(
#             request.face_visible_percent
#             if request.face_visible_percent is not None
#             else get_value("faceVisiblePercent")
#         ),
#         "centered_face_percent": safe_optional_float(
#             request.centered_face_percent
#             if request.centered_face_percent is not None
#             else get_value("centeredFacePercent")
#         ),
#         "eye_contact_percent": safe_optional_float(
#             request.eye_contact_percent
#             if request.eye_contact_percent is not None
#             else get_value("eyeContactPercent")
#         ),
#         "movement_warnings": safe_int(
#             request.movement_warnings
#             if request.movement_warnings is not None
#             else get_value("movementWarnings"),
#             0,
#         ),
#         "face_missing_warnings": safe_int(
#             request.face_missing_warnings
#             if request.face_missing_warnings is not None
#             else get_value("faceMissingWarnings"),
#             0,
#         ),
#         "off_center_warnings": safe_int(
#             request.off_center_warnings
#             if request.off_center_warnings is not None
#             else get_value("offCenterWarnings"),
#             0,
#         ),
#         "looking_away_warnings": safe_int(
#             request.looking_away_warnings
#             if request.looking_away_warnings is not None
#             else get_value("lookingAwayWarnings"),
#             0,
#         ),
#         "words_per_minute": safe_optional_float(
#             request.words_per_minute
#             if request.words_per_minute is not None
#             else get_value("wordsPerMinute")
#         ),
#         "spoken_words": safe_int(
#             request.spoken_words
#             if request.spoken_words is not None
#             else get_value("spokenWords"),
#             0,
#         ),
#         "warning_history": request.warning_history
#         if request.warning_history
#         else get_value("warningHistory", []),
#     }


# def get_fallback_interview_score(request: InterviewScoreRequest) -> Dict[str, Any]:
#     stats = get_transcript_stats(request)
#     camera = get_camera_metrics(request)

#     user_answer_count = stats["user_answer_count"]
#     assistant_question_count = stats["assistant_question_count"]
#     avg_answer_words = stats["avg_answer_words"]
#     meaningful_answer_count = stats["meaningful_answer_count"]
#     very_short_answer_count = stats["very_short_answer_count"]
#     total_messages = stats["total_messages"]

#     score = 5.5

#     if user_answer_count == 0:
#         score = 3.0
#     elif user_answer_count == 1:
#         score = 5.0
#     elif user_answer_count >= 2:
#         score = 6.0

#     if user_answer_count >= 3:
#         score += 0.5

#     if user_answer_count >= 5:
#         score += 0.4

#     if avg_answer_words >= 8:
#         score += 0.4

#     if avg_answer_words >= 15:
#         score += 0.5

#     if avg_answer_words >= 25:
#         score += 0.5

#     if avg_answer_words >= 40:
#         score += 0.4

#     if meaningful_answer_count >= 2:
#         score += 0.4

#     if meaningful_answer_count >= 4:
#         score += 0.4

#     if very_short_answer_count >= max(2, user_answer_count // 2):
#         score -= 0.8

#     if total_messages < 3:
#         score = min(score, 4.5)

#     score = safe_float(score, 5.5)

#     communication = safe_float(score + 0.1, score)
#     confidence = safe_float(score, score)

#     body_language = camera["body_language_score_estimate"]
#     eye_contact = camera["eye_contact_score_estimate"]
#     speaking_pace = camera["speaking_pace_score_estimate"]

#     if body_language is None:
#         body_language = 6.5 if camera["camera_metrics_available"] else 6.0

#     if eye_contact is None:
#         eye_contact = 6.5 if camera["camera_metrics_available"] else 6.0

#     if speaking_pace is None:
#         speaking_pace = 6.8

#     return {
#         "success": True,
#         "score_overall": score,
#         "score_communication": communication,
#         "score_confidence": confidence,
#         "score_body_language": safe_float(body_language, 6.0),
#         "score_eye_contact": safe_float(eye_contact, 6.0),
#         "score_speaking_pace": safe_float(speaking_pace, 6.8),
#         "camera_metrics_available": camera["camera_metrics_available"],
#         "non_verbal_metrics_counted": True,
#         "overallSummary": (
#             "Interview completed. Groq detailed scoring was not available, "
#             "so fallback scoring used transcript quality plus camera/speaking estimates."
#         ),
#         "improvementTips": [
#             "Give answers with a little more explanation and examples.",
#             "Try to answer in a clear structure: point, explanation, example.",
#             "Maintain eye contact by keeping your face centered in the camera.",
#             "Sit steady and avoid unnecessary movement.",
#         ],
#         "strengths": [
#             "Candidate participated in the interview.",
#         ],
#         "weaknesses": [
#             "Detailed Groq scoring was unavailable, so fallback evaluation was used.",
#         ],
#         "scoreReason": (
#             f"Fallback score based on {user_answer_count} candidate answers, "
#             f"{assistant_question_count} AI questions, average answer length "
#             f"of {avg_answer_words:.1f} words, and frontend camera/speaking estimates."
#         ),
#         "totalMessages": total_messages,
#         "userAnswers": user_answer_count,
#         "aiQuestions": assistant_question_count,
#         "durationSeconds": request.duration_seconds,
#         "cameraMetrics": camera,
#         "provider": "fallback",
#         "model": "fallback",
#     }


# def score_interview_with_groq(request: InterviewScoreRequest) -> Dict[str, Any]:
#     if not is_groq_configured():
#         raise ValueError("GROQ_API_KEY is missing. Add GROQ_API_KEY in your .env file.")

#     from groq import Groq

#     transcript_text = request.transcript_text or build_interview_transcript_text(
#         request.transcript
#     )

#     if not transcript_text:
#         raise ValueError("Transcript is empty. Cannot score interview.")

#     stats = get_transcript_stats(request)
#     camera = get_camera_metrics(request)

#     system_prompt = """
# You are an expert mock interview evaluator for students and freshers.

# You will score the interview from two sources:
# 1. Transcript answer quality.
# 2. Frontend measured camera/speaking metrics.

# Important rules:
# 1. Overall score must mainly depend on transcript answer quality.
# 2. Eye contact score must use the provided eye contact/camera metrics.
# 3. Body language score must use the provided posture/face-center/movement metrics.
# 4. Speaking pace score must use provided words-per-minute and speaking pace estimate.
# 5. Do not invent camera data. Use only provided camera metrics.
# 6. If camera metrics are weak, give lower eye contact/body language score.
# 7. If camera metrics are good, give fair/good eye contact/body language score.
# 8. Be fair for fresher-level interviews.
# 9. Do not give a fixed score.
# 10. Use score range 0 to 10.
# 11. Return ONLY valid JSON.
# 12. Do not wrap JSON in markdown.

# Scoring philosophy:
# - A normal fresher with relevant but simple answers should usually be around 6.5 to 7.5 overall.
# - Strong, clear, structured, role-relevant answers should be 8.0+ overall.
# - Very short, irrelevant, or missing answers should be below 6 overall.
# - Only mostly silent/no meaningful responses should be below 4 overall.
# - Eye contact/body language/speaking pace can differ from overall score.
# """

#     user_prompt = f"""
# Interview Setup:
# - Title: {request.interview_title}
# - Track: {request.track}
# - Difficulty: {request.difficulty}
# - Role: {request.interview_role}
# - Company: {request.interview_company}
# - Question Count: {request.question_count}
# - Skills: {", ".join(request.skills or [])}
# - Resume File: {request.resume_file_name}
# - Duration Seconds: {request.duration_seconds}

# Transcript Stats:
# - Total Messages: {stats["total_messages"]}
# - Candidate Answers: {stats["user_answer_count"]}
# - AI Questions: {stats["assistant_question_count"]}
# - Average Candidate Answer Words: {stats["avg_answer_words"]:.1f}
# - Meaningful Answers Count: {stats["meaningful_answer_count"]}
# - Very Short Answers Count: {stats["very_short_answer_count"]}

# Camera And Speaking Metrics:
# - Camera Metrics Available: {camera["camera_metrics_available"]}
# - Camera Ready: {camera["camera_ready"]}
# - Face Detector Available: {camera["face_detector_available"]}

# - Eye Contact Score Estimate From Frontend: {camera["eye_contact_score_estimate"]}
# - Body Language Score Estimate From Frontend: {camera["body_language_score_estimate"]}
# - Speaking Pace Score Estimate From Frontend: {camera["speaking_pace_score_estimate"]}

# - Face Visible Percent: {camera["face_visible_percent"]}
# - Centered Face Percent: {camera["centered_face_percent"]}
# - Eye Contact Percent: {camera["eye_contact_percent"]}

# - Movement Warnings: {camera["movement_warnings"]}
# - Face Missing Warnings: {camera["face_missing_warnings"]}
# - Off Center Warnings: {camera["off_center_warnings"]}
# - Looking Away Warnings: {camera["looking_away_warnings"]}

# - Words Per Minute: {camera["words_per_minute"]}
# - Spoken Words: {camera["spoken_words"]}

# Recent Camera Warning History:
# {json.dumps(camera["warning_history"][-12:], indent=2)}

# Job Description:
# {limit_text(request.job_description, 2200)}

# Resume Text:
# {limit_text(request.resume_text, 2200)}

# Transcript:
# {limit_text(transcript_text, 9000)}

# Return ONLY this JSON format:

# {{
#   "success": true,
#   "score_overall": 0,
#   "score_communication": 0,
#   "score_confidence": 0,
#   "score_body_language": 0,
#   "score_eye_contact": 0,
#   "score_speaking_pace": 0,
#   "camera_metrics_available": true,
#   "non_verbal_metrics_counted": true,
#   "overallSummary": "short honest summary",
#   "improvementTips": [
#     "tip 1",
#     "tip 2",
#     "tip 3"
#   ],
#   "strengths": [
#     "strength 1",
#     "strength 2"
#   ],
#   "weaknesses": [
#     "weakness 1",
#     "weakness 2"
#   ],
#   "scoreReason": "why this score was given"
# }}

# Important:
# - Do not give 0 for body language/eye contact/speaking pace if metrics are available.
# - If camera metrics are unavailable, use a neutral score around 6.0 to 6.8 and mention limited camera data.
# - Keep all scores realistic and varied.
# """

#     client = Groq(api_key=get_groq_api_key())

#     try:
#         max_tokens = min(int(get_groq_max_tokens() or 1400), 1800)
#     except Exception:
#         max_tokens = 1400

#     response = client.chat.completions.create(
#         model=get_groq_model(),
#         messages=[
#             {
#                 "role": "system",
#                 "content": system_prompt,
#             },
#             {
#                 "role": "user",
#                 "content": user_prompt,
#             },
#         ],
#         temperature=0.25,
#         max_tokens=max_tokens,
#     )

#     raw_answer = response.choices[0].message.content.strip()
#     parsed = extract_json_from_text(raw_answer)

#     if not parsed:
#         raise ValueError("Groq did not return valid JSON scoring output.")

#     score_overall = safe_float(parsed.get("score_overall"), 6.5)

#     body_language_fallback = (
#         camera["body_language_score_estimate"]
#         if camera["body_language_score_estimate"] is not None
#         else 6.5
#     )

#     eye_contact_fallback = (
#         camera["eye_contact_score_estimate"]
#         if camera["eye_contact_score_estimate"] is not None
#         else 6.5
#     )

#     speaking_pace_fallback = (
#         camera["speaking_pace_score_estimate"]
#         if camera["speaking_pace_score_estimate"] is not None
#         else 6.8
#     )

#     return {
#         "success": True,
#         "score_overall": score_overall,
#         "score_communication": safe_float(
#             parsed.get("score_communication"),
#             score_overall,
#         ),
#         "score_confidence": safe_float(
#             parsed.get("score_confidence"),
#             score_overall,
#         ),
#         "score_body_language": safe_float(
#             parsed.get("score_body_language"),
#             body_language_fallback,
#         ),
#         "score_eye_contact": safe_float(
#             parsed.get("score_eye_contact"),
#             eye_contact_fallback,
#         ),
#         "score_speaking_pace": safe_float(
#             parsed.get("score_speaking_pace"),
#             speaking_pace_fallback,
#         ),
#         "camera_metrics_available": bool(
#             parsed.get("camera_metrics_available", camera["camera_metrics_available"])
#         ),
#         "non_verbal_metrics_counted": True,
#         "overallSummary": parsed.get("overallSummary")
#         or parsed.get("overall_summary")
#         or "Interview scored successfully from transcript and camera metrics.",
#         "improvementTips": parsed.get("improvementTips")
#         or parsed.get("improvement_tips")
#         or [],
#         "strengths": parsed.get("strengths") or [],
#         "weaknesses": parsed.get("weaknesses") or [],
#         "scoreReason": parsed.get("scoreReason")
#         or parsed.get("score_reason")
#         or "Score generated from transcript answer quality plus camera/speaking metrics.",
#         "cameraMetrics": camera,
#         "provider": "groq",
#         "model": get_groq_model(),
#         "raw": raw_answer,
#     }


# # ---------------------------------------------------------
# # Root + health
# # ---------------------------------------------------------

# @app.get("/")
# def root():
#     return {
#         "success": True,
#         "message": "InterviewIQ RAG Backend is running",
#         "docs": "/docs",
#         "health": "/health",
#         "startup_mode": "fast_lazy_loading",
#         "uptime_seconds": round(time.time() - APP_START_TIME, 2),
#     }


# @app.get("/health")
# def health_check():
#     return {
#         "success": True,
#         "status": "ok",
#         "service": "InterviewIQ RAG Backend",
#         "version": APP_VERSION,
#         "startup_mode": "fast_lazy_loading",
#         "uptime_seconds": round(time.time() - APP_START_TIME, 2),
#     }


# # ---------------------------------------------------------
# # Notes upload + process
# # ---------------------------------------------------------

# @app.post("/api/notes/upload")
# async def upload_notes(
#     files: List[UploadFile] = File(...),
#     session_id: Optional[str] = Form(None),
# ):
#     if not files:
#         raise HTTPException(status_code=400, detail="No PDF files uploaded.")

#     if len(files) > MAX_PDFS_PER_SESSION:
#         raise HTTPException(
#             status_code=400,
#             detail=f"You can upload maximum {MAX_PDFS_PER_SESSION} PDFs per session.",
#         )

#     active_session_id = session_id or create_session_id()
#     create_user_folders(active_session_id)

#     saved_paths = []
#     invalid_files = []

#     for uploaded_file in files:
#         filename = uploaded_file.filename or "uploaded.pdf"

#         file_bytes = await uploaded_file.read()
#         file_size = len(file_bytes)

#         validation = validate_upload_file(
#             filename=filename,
#             size_bytes=file_size,
#         )

#         if not validation["valid"]:
#             invalid_files.append(
#                 {
#                     "name": filename,
#                     "message": validation["message"],
#                 }
#             )
#             continue

#         destination = save_uploaded_pdf_bytes(
#             file_bytes=file_bytes,
#             session_id=active_session_id,
#             original_filename=filename,
#         )

#         saved_paths.append(str(destination))

#     if invalid_files:
#         return {
#             "success": False,
#             "session_id": active_session_id,
#             "saved_paths": saved_paths,
#             "invalid_files": invalid_files,
#             "message": "Some files are invalid.",
#         }

#     if not saved_paths:
#         raise HTTPException(
#             status_code=400,
#             detail="No valid PDF files were uploaded.",
#         )

#     process_result = process_notes_for_session(active_session_id)

#     from src.vector_store import get_vector_store_status

#     return {
#         "success": process_result.get("success", False),
#         "session_id": active_session_id,
#         "saved_paths": saved_paths,
#         "process_result": process_result,
#         "vector_status": get_vector_store_status(active_session_id),
#         "session_summary": get_session_summary(active_session_id),
#         "message": process_result.get("message", "Upload completed."),
#     }


# @app.post("/api/notes/process")
# def process_existing_notes(session_id: str = Form(...)):
#     if not session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     create_user_folders(session_id)
#     process_result = process_notes_for_session(session_id)

#     from src.vector_store import get_vector_store_status

#     return {
#         "success": process_result.get("success", False),
#         "session_id": session_id,
#         "process_result": process_result,
#         "vector_status": get_vector_store_status(session_id),
#         "session_summary": get_session_summary(session_id),
#         "message": process_result.get("message", "Processing completed."),
#     }


# @app.post("/api/notes/ask")
# def ask_notes_question(request: AskNotesRequest):
#     if not request.session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     if not request.question or not request.question.strip():
#         raise HTTPException(status_code=400, detail="question is required.")

#     from src.rag_chain import ask_rag, check_rag_ready

#     rag_ready = check_rag_ready(request.session_id)

#     if not rag_ready:
#         raise HTTPException(
#             status_code=400,
#             detail="RAG is not ready. Please upload and process notes first.",
#         )

#     result = ask_rag(
#         session_id=request.session_id,
#         question=request.question,
#         model_name=get_backend_llm_model(),
#         top_k=10,
#         search_type="mmr",
#         answer_mode="rag",
#     )

#     return {
#         "success": result.get("success", True),
#         "session_id": request.session_id,
#         "question": request.question,
#         "answer": result.get("answer", "No answer generated."),
#         "sources": result.get("sources", []),
#         "provider": result.get("provider"),
#         "model": result.get("model"),
#         "retrieved_chunks": result.get("retrieved_chunks", 0),
#     }


# # ---------------------------------------------------------
# # Study tools
# # ---------------------------------------------------------

# @app.post("/api/notes/summarize")
# def summarize_uploaded_notes(session_id: str = Form(...)):
#     if not session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     from src.rag_chain import summarize_notes, check_rag_ready

#     rag_ready = check_rag_ready(session_id)

#     if not rag_ready:
#         raise HTTPException(
#             status_code=400,
#             detail="RAG is not ready. Please upload and process notes first.",
#         )

#     result = summarize_notes(
#         session_id=session_id,
#         model_name=get_backend_llm_model(),
#         top_k=10,
#     )

#     return {
#         "success": result.get("success", True),
#         "session_id": session_id,
#         "answer": result.get("answer", ""),
#         "sources": result.get("sources", []),
#         "provider": result.get("provider"),
#         "model": result.get("model"),
#         "retrieved_chunks": result.get("retrieved_chunks", 0),
#     }


# @app.post("/api/notes/questions")
# def generate_notes_questions(session_id: str = Form(...)):
#     if not session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     from src.rag_chain import generate_questions, check_rag_ready

#     rag_ready = check_rag_ready(session_id)

#     if not rag_ready:
#         raise HTTPException(
#             status_code=400,
#             detail="RAG is not ready. Please upload and process notes first.",
#         )

#     result = generate_questions(
#         session_id=session_id,
#         model_name=get_backend_llm_model(),
#         top_k=10,
#     )

#     return {
#         "success": result.get("success", True),
#         "session_id": session_id,
#         "answer": result.get("answer", ""),
#         "sources": result.get("sources", []),
#         "provider": result.get("provider"),
#         "model": result.get("model"),
#         "retrieved_chunks": result.get("retrieved_chunks", 0),
#     }


# @app.post("/api/flashcards/generate")
# def generate_notes_flashcards(request: FlashcardRequest):
#     if not request.session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     from src.rag_chain import generate_flashcards, check_rag_ready

#     rag_ready = check_rag_ready(request.session_id)

#     if not rag_ready:
#         raise HTTPException(
#             status_code=400,
#             detail="RAG is not ready. Please upload and process notes first.",
#         )

#     result = generate_flashcards(
#         session_id=request.session_id,
#         model_name=get_backend_llm_model(),
#         top_k=10,
#     )

#     raw_answer = result.get("answer", "")
#     parsed_cards = parse_flashcards(raw_answer)

#     return {
#         "success": result.get("success", True),
#         "session_id": request.session_id,
#         "raw": raw_answer,
#         "flashcards": parsed_cards,
#         "sources": result.get("sources", []),
#         "total_flashcards": len(parsed_cards),
#         "provider": result.get("provider"),
#         "model": result.get("model"),
#         "retrieved_chunks": result.get("retrieved_chunks", 0),
#     }


# # ---------------------------------------------------------
# # Resume Gap Finder
# # ---------------------------------------------------------

# @app.post("/api/resume/gap-analysis")
# async def resume_gap_analysis(
#     resume: UploadFile = File(...),
#     jd_file: Optional[UploadFile] = File(None),
#     job_description: str = Form(""),
#     session_id: Optional[str] = Form(None),
# ):
#     if resume is None:
#         raise HTTPException(status_code=400, detail="Resume file is required.")

#     from src.resume import analyze_resume_file_bytes_and_jd_with_rag

#     active_session_id = session_id or create_session_id()

#     resume_bytes = await resume.read()

#     if not resume_bytes:
#         raise HTTPException(status_code=400, detail="Resume file is empty.")

#     final_jd_text = clean_text(job_description or "")
#     jd_filename = "pasted_job_description"

#     if jd_file is not None:
#         jd_bytes = await jd_file.read()

#         if not jd_bytes:
#             raise HTTPException(status_code=400, detail="JD file is empty.")

#         try:
#             extracted_jd_text = extract_text_from_upload_bytes(
#                 file_bytes=jd_bytes,
#                 filename=jd_file.filename or "job_description",
#             )
#         except Exception as e:
#             raise HTTPException(status_code=400, detail=str(e))

#         extracted_jd_text = clean_text(extracted_jd_text)

#         if extracted_jd_text:
#             final_jd_text = extracted_jd_text
#             jd_filename = jd_file.filename or "job_description"

#     if not final_jd_text:
#         raise HTTPException(
#             status_code=400,
#             detail="Please upload JD file or paste job description.",
#         )

#     result = analyze_resume_file_bytes_and_jd_with_rag(
#         base_session_id=active_session_id,
#         resume_bytes=resume_bytes,
#         resume_filename=resume.filename or "resume.pdf",
#         jd_text=final_jd_text,
#         jd_filename=jd_filename,
#     )

#     return {
#         "success": result.get("success", False),
#         "session_id": active_session_id,
#         "answer": result.get("answer", ""),
#         "data": result.get("data"),
#         "structured": result.get("structured"),
#         "resume_text": result.get("resume_text", ""),
#         "jd_text": result.get("jd_text", ""),
#         "rag_context": result.get("rag_context", ""),
#         "resume_rag_session_id": result.get("resume_rag_session_id"),
#         "retrieved_chunks": result.get("retrieved_chunks", 0),
#         "total_chunks": result.get("total_chunks", 0),
#         "model": result.get("model"),
#         "provider": result.get("provider"),
#     }


# # ---------------------------------------------------------
# # Interview Scoring
# # ---------------------------------------------------------

# @app.post("/api/interview/score")
# def score_interview(request: InterviewScoreRequest):
#     if not request.transcript and not request.transcript_text:
#         raise HTTPException(
#             status_code=400,
#             detail="Transcript is required for scoring.",
#         )

#     try:
#         result = score_interview_with_groq(request)
#         return result

#     except Exception as e:
#         fallback = get_fallback_interview_score(request)
#         fallback["groq_error"] = str(e)
#         return fallback


# # ---------------------------------------------------------
# # Session status + clear
# # ---------------------------------------------------------

# @app.get("/api/session/{session_id}/summary")
# def session_summary(session_id: str):
#     from src.pdf_processor import get_session_pdf_summary
#     from src.vector_store import get_vector_store_status
#     from src.rag_chain import check_rag_ready

#     return {
#         "success": True,
#         "session_id": session_id,
#         "session_summary": get_session_summary(session_id),
#         "pdf_summary": get_session_pdf_summary(session_id),
#         "vector_status": get_vector_store_status(session_id),
#         "rag_ready": check_rag_ready(session_id),
#     }


# @app.delete("/api/session/{session_id}/clear")
# def clear_session(session_id: str, full_clear: bool = False):
#     if full_clear:
#         clear_all_session_files(session_id)
#     else:
#         clear_user_data(session_id)

#     return {
#         "success": True,
#         "session_id": session_id,
#         "full_clear": full_clear,
#         "message": "Session data cleared.",
#     }


# @app.delete("/api/session/{session_id}/uploaded-files")
# def clear_uploaded_files(session_id: str):
#     clear_only_uploaded_files(session_id)
#     clear_user_data(session_id)

#     return {
#         "success": True,
#         "session_id": session_id,
#         "message": "Uploaded PDFs and processed data cleared.",
#     }


# # ---------------------------------------------------------
# # Debug endpoints
# # ---------------------------------------------------------

# @app.get("/api/debug/config")
# def debug_config():
#     from src.embeddings import get_embedding_status
#     from src.ocr_processor import get_ocr_status

#     return {
#         "success": True,
#         "config": get_config_summary(),
#         "embedding_status": get_embedding_status(),
#         "ocr_status": get_ocr_status(),
#         "allowed_origins": allowed_origins,
#         "startup_mode": "fast_lazy_loading",
#         "uptime_seconds": round(time.time() - APP_START_TIME, 2),
#     }


# @app.post("/api/debug/search")
# def debug_vector_search(request: DebugSearchRequest):
#     if not request.session_id:
#         raise HTTPException(status_code=400, detail="session_id is required.")

#     if not request.query or not request.query.strip():
#         raise HTTPException(status_code=400, detail="query is required.")

#     from src.vector_store import similarity_search_with_score

#     results = similarity_search_with_score(
#         session_id=request.session_id,
#         query=request.query,
#         top_k=max(int(request.top_k or 10), 10),
#     )

#     return {
#         "success": True,
#         "session_id": request.session_id,
#         "query": request.query,
#         "results": results,
#     }


































import os

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import re
import json
import uuid
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Path setup
# ---------------------------------------------------------

BACKEND_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_ROOT.parent

sys.path.append(str(BACKEND_ROOT))
sys.path.append(str(PROJECT_ROOT))


# ---------------------------------------------------------
# Lightweight imports only
# Heavy RAG / embedding / PDF modules are imported lazily inside endpoints.
# This fixes slow deployment startup.
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
    get_groq_api_key,
    get_groq_model,
    get_groq_max_tokens,
    is_groq_configured,
)

from src.session_manager import (
    create_user_folders,
    get_session_summary,
    clear_user_data,
    clear_all_session_files,
    clear_only_uploaded_files,
    save_uploaded_pdf_bytes,
)


APP_START_TIME = time.time()


# ---------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=API_DESCRIPTION,
)


# ---------------------------------------------------------
# CORS FIX
# ---------------------------------------------------------

allowed_origins = list(
    set(
        [
            FRONTEND_URL,

            # Vite ports
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "http://localhost:5175",
            "http://127.0.0.1:5175",

            # React / Next ports
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",

            # Backend itself
            "http://localhost:8000",
            "http://127.0.0.1:8000",

            *CORS_ALLOWED_ORIGINS,
        ]
    )
)

allowed_origins = [
    origin.strip()
    for origin in allowed_origins
    if origin and origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=(
        r"https?://(localhost|127\.0\.0\.1)(:\d+)?"
        r"|https://.*\.vercel\.app"
        r"|https://.*\.netlify\.app"
        r"|https://.*\.onrender\.com"
    ),
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
    top_k: int = 10


class InterviewScoreRequest(BaseModel):
    track: str = "General"
    difficulty: str = "Fresher"
    interview_title: str = ""
    interview_role: str = ""
    interview_company: str = ""
    question_count: int = 15
    skills: List[str] = Field(default_factory=list)

    job_description: str = ""
    resume_text: str = ""
    resume_file_name: str = ""

    transcript: List[Dict[str, Any]] = Field(default_factory=list)
    transcript_text: str = ""
    duration_seconds: int = 0

    camera_metrics: Dict[str, Any] = Field(default_factory=dict)

    eye_contact_score_estimate: Optional[float] = None
    body_language_score_estimate: Optional[float] = None
    speaking_pace_score_estimate: Optional[float] = None

    face_visible_percent: Optional[float] = None
    centered_face_percent: Optional[float] = None
    eye_contact_percent: Optional[float] = None

    movement_warnings: int = 0
    face_missing_warnings: int = 0
    off_center_warnings: int = 0
    looking_away_warnings: int = 0

    words_per_minute: Optional[float] = None
    spoken_words: Optional[int] = None
    warning_history: List[Dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------

def create_session_id() -> str:
    return str(uuid.uuid4())


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = str(text)
    text = text.replace("\x00", " ")
    text = text.replace("\t", " ")
    text = text.replace("\r", "\n")

    lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines).strip()


def limit_text(text: str, max_chars: int = 7000) -> str:
    text = clean_text(text)

    if len(text) <= max_chars:
        return text

    return text[:max_chars]


def safe_float(value, fallback: float = 5.0) -> float:
    try:
        number = float(value)
        return round(max(0.0, min(10.0, number)), 1)
    except Exception:
        return fallback


def safe_optional_float(value):
    try:
        if value is None:
            return None

        number = float(value)
        return round(max(0.0, min(10.0, number)), 1)
    except Exception:
        return None


def safe_int(value, fallback: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return fallback


def extract_json_from_text(text: str) -> Dict[str, Any]:
    if not text:
        return {}

    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        return {}

    try:
        return json.loads(match.group(0))
    except Exception:
        return {}


def extract_text_from_upload_bytes(file_bytes: bytes, filename: str) -> str:
    """
    Lazy import resume text extractors.
    This avoids loading PDF/DOCX libraries at app startup.
    """

    if not file_bytes:
        return ""

    from src.resume import (
        extract_text_from_pdf_bytes,
        extract_text_from_txt_bytes,
        extract_text_from_docx_bytes,
    )

    suffix = Path(filename or "").suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf_bytes(file_bytes)

    if suffix == ".docx":
        return extract_text_from_docx_bytes(file_bytes)

    if suffix == ".txt":
        return extract_text_from_txt_bytes(file_bytes)

    raise ValueError("Only PDF, DOCX, and TXT files are supported.")


def parse_flashcards(raw_text: str) -> List[Dict[str, Any]]:
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

    Lazy imports keep backend startup fast on Render/local.
    """

    from src.config import get_parallel_pdf_workers
    from src.pdf_processor import process_uploaded_pdfs_for_session
    from src.vector_store import index_documents_pipeline

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
# Interview scoring helpers
# ---------------------------------------------------------

def build_interview_transcript_text(transcript: List[Dict[str, Any]]) -> str:
    if not transcript:
        return ""

    lines = []

    for item in transcript:
        role = str(item.get("role", "")).strip()
        content = str(item.get("content", "")).strip()

        if not content:
            continue

        if role == "user":
            label = "Candidate"
        elif role == "assistant":
            label = "AI Interviewer"
        else:
            label = role or "System"

        lines.append(f"{label}: {content}")

    return "\n".join(lines).strip()


def get_transcript_stats(request: InterviewScoreRequest) -> Dict[str, Any]:
    transcript = request.transcript or []

    user_answers = [
        str(message.get("content", "")).strip()
        for message in transcript
        if message.get("role") == "user" and str(message.get("content", "")).strip()
    ]

    assistant_questions = [
        str(message.get("content", "")).strip()
        for message in transcript
        if message.get("role") == "assistant" and str(message.get("content", "")).strip()
    ]

    answer_word_counts = [
        len(answer.split())
        for answer in user_answers
    ]

    total_answer_words = sum(answer_word_counts)

    avg_answer_words = (
        total_answer_words / len(answer_word_counts)
        if answer_word_counts
        else 0
    )

    meaningful_answers = [
        answer for answer in user_answers
        if len(answer.split()) >= 8
    ]

    very_short_answers = [
        answer for answer in user_answers
        if len(answer.split()) <= 4
    ]

    return {
        "total_messages": len(transcript),
        "user_answers": user_answers,
        "assistant_questions": assistant_questions,
        "user_answer_count": len(user_answers),
        "assistant_question_count": len(assistant_questions),
        "answer_word_counts": answer_word_counts,
        "total_answer_words": total_answer_words,
        "avg_answer_words": avg_answer_words,
        "meaningful_answer_count": len(meaningful_answers),
        "very_short_answer_count": len(very_short_answers),
    }


def get_camera_metrics(request: InterviewScoreRequest) -> Dict[str, Any]:
    metrics = dict(request.camera_metrics or {})

    def get_value(key, fallback=None):
        value = metrics.get(key)

        if value is None:
            return fallback

        return value

    return {
        "camera_metrics_available": bool(
            get_value("cameraMetricsAvailable", False)
            or get_value("camera_metrics_available", False)
            or request.eye_contact_score_estimate is not None
            or request.body_language_score_estimate is not None
            or request.speaking_pace_score_estimate is not None
        ),
        "camera_ready": bool(
            get_value("cameraReady", False)
            or get_value("camera_ready", False)
        ),
        "face_detector_available": bool(
            get_value("faceDetectorAvailable", False)
            or get_value("face_detector_available", False)
        ),
        "eye_contact_score_estimate": safe_optional_float(
            request.eye_contact_score_estimate
            if request.eye_contact_score_estimate is not None
            else get_value("eyeContactScoreEstimate")
        ),
        "body_language_score_estimate": safe_optional_float(
            request.body_language_score_estimate
            if request.body_language_score_estimate is not None
            else get_value("bodyLanguageScoreEstimate")
        ),
        "speaking_pace_score_estimate": safe_optional_float(
            request.speaking_pace_score_estimate
            if request.speaking_pace_score_estimate is not None
            else get_value("speakingPaceScoreEstimate")
        ),
        "face_visible_percent": safe_optional_float(
            request.face_visible_percent
            if request.face_visible_percent is not None
            else get_value("faceVisiblePercent")
        ),
        "centered_face_percent": safe_optional_float(
            request.centered_face_percent
            if request.centered_face_percent is not None
            else get_value("centeredFacePercent")
        ),
        "eye_contact_percent": safe_optional_float(
            request.eye_contact_percent
            if request.eye_contact_percent is not None
            else get_value("eyeContactPercent")
        ),
        "movement_warnings": safe_int(
            request.movement_warnings
            if request.movement_warnings is not None
            else get_value("movementWarnings"),
            0,
        ),
        "face_missing_warnings": safe_int(
            request.face_missing_warnings
            if request.face_missing_warnings is not None
            else get_value("faceMissingWarnings"),
            0,
        ),
        "off_center_warnings": safe_int(
            request.off_center_warnings
            if request.off_center_warnings is not None
            else get_value("offCenterWarnings"),
            0,
        ),
        "looking_away_warnings": safe_int(
            request.looking_away_warnings
            if request.looking_away_warnings is not None
            else get_value("lookingAwayWarnings"),
            0,
        ),
        "words_per_minute": safe_optional_float(
            request.words_per_minute
            if request.words_per_minute is not None
            else get_value("wordsPerMinute")
        ),
        "spoken_words": safe_int(
            request.spoken_words
            if request.spoken_words is not None
            else get_value("spokenWords"),
            0,
        ),
        "warning_history": request.warning_history
        if request.warning_history
        else get_value("warningHistory", []),
    }


def get_fallback_interview_score(request: InterviewScoreRequest) -> Dict[str, Any]:
    stats = get_transcript_stats(request)
    camera = get_camera_metrics(request)

    user_answer_count = stats["user_answer_count"]
    assistant_question_count = stats["assistant_question_count"]
    avg_answer_words = stats["avg_answer_words"]
    meaningful_answer_count = stats["meaningful_answer_count"]
    very_short_answer_count = stats["very_short_answer_count"]
    total_messages = stats["total_messages"]

    score = 5.5

    if user_answer_count == 0:
        score = 3.0
    elif user_answer_count == 1:
        score = 5.0
    elif user_answer_count >= 2:
        score = 6.0

    if user_answer_count >= 3:
        score += 0.5

    if user_answer_count >= 5:
        score += 0.4

    if avg_answer_words >= 8:
        score += 0.4

    if avg_answer_words >= 15:
        score += 0.5

    if avg_answer_words >= 25:
        score += 0.5

    if avg_answer_words >= 40:
        score += 0.4

    if meaningful_answer_count >= 2:
        score += 0.4

    if meaningful_answer_count >= 4:
        score += 0.4

    if very_short_answer_count >= max(2, user_answer_count // 2):
        score -= 0.8

    if total_messages < 3:
        score = min(score, 4.5)

    score = safe_float(score, 5.5)

    communication = safe_float(score + 0.1, score)
    confidence = safe_float(score, score)

    body_language = camera["body_language_score_estimate"]
    eye_contact = camera["eye_contact_score_estimate"]
    speaking_pace = camera["speaking_pace_score_estimate"]

    if body_language is None:
        body_language = 6.5 if camera["camera_metrics_available"] else 6.0

    if eye_contact is None:
        eye_contact = 6.5 if camera["camera_metrics_available"] else 6.0

    if speaking_pace is None:
        speaking_pace = 6.8

    return {
        "success": True,
        "score_overall": score,
        "score_communication": communication,
        "score_confidence": confidence,
        "score_body_language": safe_float(body_language, 6.0),
        "score_eye_contact": safe_float(eye_contact, 6.0),
        "score_speaking_pace": safe_float(speaking_pace, 6.8),
        "camera_metrics_available": camera["camera_metrics_available"],
        "non_verbal_metrics_counted": True,
        "overallSummary": (
            "Interview completed. Groq detailed scoring was not available, "
            "so fallback scoring used transcript quality plus camera/speaking estimates."
        ),
        "improvementTips": [
            "Give answers with a little more explanation and examples.",
            "Try to answer in a clear structure: point, explanation, example.",
            "Maintain eye contact by keeping your face centered in the camera.",
            "Sit steady and avoid unnecessary movement.",
        ],
        "strengths": [
            "Candidate participated in the interview.",
        ],
        "weaknesses": [
            "Detailed Groq scoring was unavailable, so fallback evaluation was used.",
        ],
        "scoreReason": (
            f"Fallback score based on {user_answer_count} candidate answers, "
            f"{assistant_question_count} AI questions, average answer length "
            f"of {avg_answer_words:.1f} words, and frontend camera/speaking estimates."
        ),
        "totalMessages": total_messages,
        "userAnswers": user_answer_count,
        "aiQuestions": assistant_question_count,
        "durationSeconds": request.duration_seconds,
        "cameraMetrics": camera,
        "provider": "fallback",
        "model": "fallback",
    }


def score_interview_with_groq(request: InterviewScoreRequest) -> Dict[str, Any]:
    if not is_groq_configured():
        raise ValueError("GROQ_API_KEY is missing. Add GROQ_API_KEY in your .env file.")

    from groq import Groq

    transcript_text = request.transcript_text or build_interview_transcript_text(
        request.transcript
    )

    if not transcript_text:
        raise ValueError("Transcript is empty. Cannot score interview.")

    stats = get_transcript_stats(request)
    camera = get_camera_metrics(request)

    system_prompt = """
You are an expert mock interview evaluator for students and freshers.

You will score the interview from two sources:
1. Transcript answer quality.
2. Frontend measured camera/speaking metrics.

Important rules:
1. Overall score must mainly depend on transcript answer quality.
2. Eye contact score must use the provided eye contact/camera metrics.
3. Body language score must use the provided posture/face-center/movement metrics.
4. Speaking pace score must use provided words-per-minute and speaking pace estimate.
5. Do not invent camera data. Use only provided camera metrics.
6. If camera metrics are weak, give lower eye contact/body language score.
7. If camera metrics are good, give fair/good eye contact/body language score.
8. Be fair for fresher-level interviews.
9. Do not give a fixed score.
10. Use score range 0 to 10.
11. Return ONLY valid JSON.
12. Do not wrap JSON in markdown.

Scoring philosophy:
- A normal fresher with relevant but simple answers should usually be around 6.5 to 7.5 overall.
- Strong, clear, structured, role-relevant answers should be 8.0+ overall.
- Very short, irrelevant, or missing answers should be below 6 overall.
- Only mostly silent/no meaningful responses should be below 4 overall.
- Eye contact/body language/speaking pace can differ from overall score.
"""

    user_prompt = f"""
Interview Setup:
- Title: {request.interview_title}
- Track: {request.track}
- Difficulty: {request.difficulty}
- Role: {request.interview_role}
- Company: {request.interview_company}
- Question Count: {request.question_count}
- Skills: {", ".join(request.skills or [])}
- Resume File: {request.resume_file_name}
- Duration Seconds: {request.duration_seconds}

Transcript Stats:
- Total Messages: {stats["total_messages"]}
- Candidate Answers: {stats["user_answer_count"]}
- AI Questions: {stats["assistant_question_count"]}
- Average Candidate Answer Words: {stats["avg_answer_words"]:.1f}
- Meaningful Answers Count: {stats["meaningful_answer_count"]}
- Very Short Answers Count: {stats["very_short_answer_count"]}

Camera And Speaking Metrics:
- Camera Metrics Available: {camera["camera_metrics_available"]}
- Camera Ready: {camera["camera_ready"]}
- Face Detector Available: {camera["face_detector_available"]}

- Eye Contact Score Estimate From Frontend: {camera["eye_contact_score_estimate"]}
- Body Language Score Estimate From Frontend: {camera["body_language_score_estimate"]}
- Speaking Pace Score Estimate From Frontend: {camera["speaking_pace_score_estimate"]}

- Face Visible Percent: {camera["face_visible_percent"]}
- Centered Face Percent: {camera["centered_face_percent"]}
- Eye Contact Percent: {camera["eye_contact_percent"]}

- Movement Warnings: {camera["movement_warnings"]}
- Face Missing Warnings: {camera["face_missing_warnings"]}
- Off Center Warnings: {camera["off_center_warnings"]}
- Looking Away Warnings: {camera["looking_away_warnings"]}

- Words Per Minute: {camera["words_per_minute"]}
- Spoken Words: {camera["spoken_words"]}

Recent Camera Warning History:
{json.dumps(camera["warning_history"][-12:], indent=2)}

Job Description:
{limit_text(request.job_description, 2200)}

Resume Text:
{limit_text(request.resume_text, 2200)}

Transcript:
{limit_text(transcript_text, 9000)}

Return ONLY this JSON format:

{{
  "success": true,
  "score_overall": 0,
  "score_communication": 0,
  "score_confidence": 0,
  "score_body_language": 0,
  "score_eye_contact": 0,
  "score_speaking_pace": 0,
  "camera_metrics_available": true,
  "non_verbal_metrics_counted": true,
  "overallSummary": "short honest summary",
  "improvementTips": [
    "tip 1",
    "tip 2",
    "tip 3"
  ],
  "strengths": [
    "strength 1",
    "strength 2"
  ],
  "weaknesses": [
    "weakness 1",
    "weakness 2"
  ],
  "scoreReason": "why this score was given"
}}

Important:
- Do not give 0 for body language/eye contact/speaking pace if metrics are available.
- If camera metrics are unavailable, use a neutral score around 6.0 to 6.8 and mention limited camera data.
- Keep all scores realistic and varied.
"""

    client = Groq(api_key=get_groq_api_key())

    try:
        max_tokens = min(int(get_groq_max_tokens() or 1400), 1800)
    except Exception:
        max_tokens = 1400

    response = client.chat.completions.create(
        model=get_groq_model(),
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.25,
        max_tokens=max_tokens,
    )

    raw_answer = response.choices[0].message.content.strip()
    parsed = extract_json_from_text(raw_answer)

    if not parsed:
        raise ValueError("Groq did not return valid JSON scoring output.")

    score_overall = safe_float(parsed.get("score_overall"), 6.5)

    body_language_fallback = (
        camera["body_language_score_estimate"]
        if camera["body_language_score_estimate"] is not None
        else 6.5
    )

    eye_contact_fallback = (
        camera["eye_contact_score_estimate"]
        if camera["eye_contact_score_estimate"] is not None
        else 6.5
    )

    speaking_pace_fallback = (
        camera["speaking_pace_score_estimate"]
        if camera["speaking_pace_score_estimate"] is not None
        else 6.8
    )

    return {
        "success": True,
        "score_overall": score_overall,
        "score_communication": safe_float(
            parsed.get("score_communication"),
            score_overall,
        ),
        "score_confidence": safe_float(
            parsed.get("score_confidence"),
            score_overall,
        ),
        "score_body_language": safe_float(
            parsed.get("score_body_language"),
            body_language_fallback,
        ),
        "score_eye_contact": safe_float(
            parsed.get("score_eye_contact"),
            eye_contact_fallback,
        ),
        "score_speaking_pace": safe_float(
            parsed.get("score_speaking_pace"),
            speaking_pace_fallback,
        ),
        "camera_metrics_available": bool(
            parsed.get("camera_metrics_available", camera["camera_metrics_available"])
        ),
        "non_verbal_metrics_counted": True,
        "overallSummary": parsed.get("overallSummary")
        or parsed.get("overall_summary")
        or "Interview scored successfully from transcript and camera metrics.",
        "improvementTips": parsed.get("improvementTips")
        or parsed.get("improvement_tips")
        or [],
        "strengths": parsed.get("strengths") or [],
        "weaknesses": parsed.get("weaknesses") or [],
        "scoreReason": parsed.get("scoreReason")
        or parsed.get("score_reason")
        or "Score generated from transcript answer quality plus camera/speaking metrics.",
        "cameraMetrics": camera,
        "provider": "groq",
        "model": get_groq_model(),
        "raw": raw_answer,
    }


# ---------------------------------------------------------
# Root + health
# ---------------------------------------------------------

@app.get("/")
def root():
    frontend_index = PROJECT_ROOT / "dist" / "index.html"

    if frontend_index.exists():
        return FileResponse(frontend_index)

    return {
        "success": True,
        "message": "InterviewIQ RAG Backend is running",
        "docs": "/docs",
        "health": "/health",
        "startup_mode": "fast_lazy_loading",
        "uptime_seconds": round(time.time() - APP_START_TIME, 2),
    }


@app.get("/health")
def health_check():
    return {
        "success": True,
        "status": "ok",
        "service": "InterviewIQ RAG Backend",
        "version": APP_VERSION,
        "startup_mode": "fast_lazy_loading",
        "uptime_seconds": round(time.time() - APP_START_TIME, 2),
    }


# ---------------------------------------------------------
# Notes upload + process
# ---------------------------------------------------------

@app.post("/api/notes/upload")
async def upload_notes(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
):
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

    from src.vector_store import get_vector_store_status

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
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    create_user_folders(session_id)
    process_result = process_notes_for_session(session_id)

    from src.vector_store import get_vector_store_status

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
    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="question is required.")

    from src.rag_chain import ask_rag, check_rag_ready

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
        top_k=10,
        search_type="mmr",
        answer_mode="rag",
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

    from src.rag_chain import summarize_notes, check_rag_ready

    rag_ready = check_rag_ready(session_id)

    if not rag_ready:
        raise HTTPException(
            status_code=400,
            detail="RAG is not ready. Please upload and process notes first.",
        )

    result = summarize_notes(
        session_id=session_id,
        model_name=get_backend_llm_model(),
        top_k=10,
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

    from src.rag_chain import generate_questions, check_rag_ready

    rag_ready = check_rag_ready(session_id)

    if not rag_ready:
        raise HTTPException(
            status_code=400,
            detail="RAG is not ready. Please upload and process notes first.",
        )

    result = generate_questions(
        session_id=session_id,
        model_name=get_backend_llm_model(),
        top_k=10,
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

    from src.rag_chain import generate_flashcards, check_rag_ready

    rag_ready = check_rag_ready(request.session_id)

    if not rag_ready:
        raise HTTPException(
            status_code=400,
            detail="RAG is not ready. Please upload and process notes first.",
        )

    result = generate_flashcards(
        session_id=request.session_id,
        model_name=get_backend_llm_model(),
        top_k=10,
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
    jd_file: Optional[UploadFile] = File(None),
    job_description: str = Form(""),
    session_id: Optional[str] = Form(None),
):
    if resume is None:
        raise HTTPException(status_code=400, detail="Resume file is required.")

    from src.resume import analyze_resume_file_bytes_and_jd_with_rag

    active_session_id = session_id or create_session_id()

    resume_bytes = await resume.read()

    if not resume_bytes:
        raise HTTPException(status_code=400, detail="Resume file is empty.")

    final_jd_text = clean_text(job_description or "")
    jd_filename = "pasted_job_description"

    if jd_file is not None:
        jd_bytes = await jd_file.read()

        if not jd_bytes:
            raise HTTPException(status_code=400, detail="JD file is empty.")

        try:
            extracted_jd_text = extract_text_from_upload_bytes(
                file_bytes=jd_bytes,
                filename=jd_file.filename or "job_description",
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        extracted_jd_text = clean_text(extracted_jd_text)

        if extracted_jd_text:
            final_jd_text = extracted_jd_text
            jd_filename = jd_file.filename or "job_description"

    if not final_jd_text:
        raise HTTPException(
            status_code=400,
            detail="Please upload JD file or paste job description.",
        )

    result = analyze_resume_file_bytes_and_jd_with_rag(
        base_session_id=active_session_id,
        resume_bytes=resume_bytes,
        resume_filename=resume.filename or "resume.pdf",
        jd_text=final_jd_text,
        jd_filename=jd_filename,
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
# Interview Scoring
# ---------------------------------------------------------

@app.post("/api/interview/score")
def score_interview(request: InterviewScoreRequest):
    if not request.transcript and not request.transcript_text:
        raise HTTPException(
            status_code=400,
            detail="Transcript is required for scoring.",
        )

    try:
        result = score_interview_with_groq(request)
        return result

    except Exception as e:
        fallback = get_fallback_interview_score(request)
        fallback["groq_error"] = str(e)
        return fallback


# ---------------------------------------------------------
# Session status + clear
# ---------------------------------------------------------

@app.get("/api/session/{session_id}/summary")
def session_summary(session_id: str):
    from src.pdf_processor import get_session_pdf_summary
    from src.vector_store import get_vector_store_status
    from src.rag_chain import check_rag_ready

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
    from src.embeddings import get_embedding_status
    from src.ocr_processor import get_ocr_status

    return {
        "success": True,
        "config": get_config_summary(),
        "embedding_status": get_embedding_status(),
        "ocr_status": get_ocr_status(),
        "allowed_origins": allowed_origins,
        "startup_mode": "fast_lazy_loading",
        "uptime_seconds": round(time.time() - APP_START_TIME, 2),
    }


@app.post("/api/debug/search")
def debug_vector_search(request: DebugSearchRequest):
    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="query is required.")

    from src.vector_store import similarity_search_with_score

    results = similarity_search_with_score(
        session_id=request.session_id,
        query=request.query,
        top_k=max(int(request.top_k or 10), 10),
    )

    return {
        "success": True,
        "session_id": request.session_id,
        "query": request.query,
        "results": results,
    }


# ---------------------------------------------------------
# Serve React frontend build on Render single web service
# ---------------------------------------------------------

FRONTEND_DIST_DIR = PROJECT_ROOT / "dist"

if FRONTEND_DIST_DIR.exists():
    assets_dir = FRONTEND_DIST_DIR / "assets"

    if assets_dir.exists():
        app.mount(
            "/assets",
            StaticFiles(directory=assets_dir),
            name="frontend-assets",
        )


@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API route not found.")

    if full_path in {
        "health",
        "docs",
        "redoc",
        "openapi.json",
    }:
        raise HTTPException(status_code=404, detail="Route not found.")

    index_file = FRONTEND_DIST_DIR / "index.html"

    if index_file.exists():
        return FileResponse(index_file)

    return {
        "success": True,
        "message": "InterviewIQ backend is running, but frontend build was not found.",
        "hint": "Run npm run build before starting backend.",
        "docs": "/docs",
        "health": "/health",
    }


# ---------------------------------------------------------
# Local / Render server entrypoint
# ---------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )
