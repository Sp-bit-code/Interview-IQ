# from typing import Dict, List

# from groq import Groq
# from langchain_ollama import ChatOllama
# from langchain_chroma import Chroma
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.documents import Document
# from langchain_core.output_parsers import StrOutputParser

# from src.embeddings import get_embedding_model
# from src.session_manager import get_chroma_path
# from src.vector_store import get_collection_name, get_vector_store_status

# from src.config import (
#     get_llm_provider,
#     get_groq_api_key,
#     get_groq_model,
#     get_groq_temperature,
#     get_groq_max_tokens,
#     is_groq_configured,
# )

# from src.prompts import (
#     SYSTEM_PROMPT,
#     RAG_USER_PROMPT,
#     INTERVIEW_ANSWER_PROMPT,
#     SUMMARY_PROMPT,
#     QUESTION_GENERATION_PROMPT,
#     FLASHCARD_PROMPT,
#     EQUATION_EXPLANATION_PROMPT,
#     IMAGE_DIAGRAM_PROMPT,
#     NOT_FOUND_RESPONSE,
# )


# DEFAULT_LLM_MODEL = "llama-3.1-8b-instant"


# STUDY_SYSTEM_PROMPT = """
# You are an AI Study and Interview Preparation Assistant.

# Follow these rules strictly:
# 1. Answer ONLY using the provided uploaded PDF context.
# 2. Do NOT use outside knowledge.
# 3. Do NOT guess.
# 4. If answer is missing, say exactly:
#    "I could not find this in your uploaded notes."
# 5. Use simple English.
# 6. Make the answer useful for study, exams, viva, and interviews.
# 7. Focus on technical concepts, definitions, algorithms, methods, examples, advantages, limitations, and applications.
# 8. Ignore administrative/course policy content unless the user directly asks about it.
# 9. Ignore deadlines, submissions, grading, late periods, office hours, lecture rules, and logistics unless directly asked.
# 10. Do not include unnecessary information.
# 11. Do not repeat the same point again and again.
# 12. Use headings and bullet points.
# 13. Always include citations from the given context only.
# 14. Do not create fake PDF names or page numbers.
# """


# ADMIN_KEYWORDS = [
#     "gradescope",
#     "late period",
#     "late periods",
#     "submission",
#     "submissions",
#     "homework",
#     "assignment deadline",
#     "deadline",
#     "grading",
#     "grade",
#     "office hour",
#     "office hours",
#     "lecture rule",
#     "attendance",
#     "policy",
#     "course policy",
#     "logistics",
#     "piazza",
#     "ed discussion",
#     "canvas",
#     "exam date",
#     "due date",
# ]


# TECHNICAL_QUERY_SUFFIX = (
#     " technical concepts definitions algorithms methods models examples "
#     "applications advantages limitations exam viva interview study notes "
#     "ignore course policy deadlines grading submissions logistics"
# )


# def get_local_llm(
#     model_name: str = "qwen2.5:3b",
#     temperature: float = 0.2,
# ):
#     return ChatOllama(
#         model=model_name,
#         temperature=temperature,
#     )


# def call_groq_llm(
#     system_prompt: str,
#     user_prompt: str,
#     model_name: str = DEFAULT_LLM_MODEL,
#     temperature: float = 0.2,
# ) -> str:
#     if not is_groq_configured():
#         raise ValueError("GROQ_API_KEY is missing. Add GROQ_API_KEY in your .env file.")

#     client = Groq(api_key=get_groq_api_key())

#     response = client.chat.completions.create(
#         model=model_name or get_groq_model(),
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
#         temperature=temperature,
#         max_tokens=get_groq_max_tokens(),
#     )

#     return response.choices[0].message.content.strip()


# def get_vector_db(session_id: str):
#     chroma_path = get_chroma_path(session_id)
#     embedding_model = get_embedding_model()

#     vector_db = Chroma(
#         collection_name=get_collection_name(session_id),
#         persist_directory=chroma_path,
#         embedding_function=embedding_model,
#     )

#     return vector_db


# def get_retriever(
#     session_id: str,
#     top_k: int = 5,
#     search_type: str = "similarity",
# ):
#     vector_db = get_vector_db(session_id)

#     if search_type == "mmr":
#         return vector_db.as_retriever(
#             search_type="mmr",
#             search_kwargs={
#                 "k": top_k,
#                 "fetch_k": max(top_k * 4, 20),
#             },
#         )

#     return vector_db.as_retriever(
#         search_type="similarity",
#         search_kwargs={"k": top_k},
#     )


# def is_admin_content(text: str) -> bool:
#     if not text:
#         return False

#     lowered = text.lower()
#     hits = 0

#     for keyword in ADMIN_KEYWORDS:
#         if keyword in lowered:
#             hits += 1

#     return hits >= 2


# def filter_study_docs(docs: List[Document]) -> List[Document]:
#     if not docs:
#         return []

#     study_docs = []

#     for doc in docs:
#         content = doc.page_content or ""

#         if is_admin_content(content):
#             continue

#         study_docs.append(doc)

#     if study_docs:
#         return study_docs

#     return docs


# def retrieve_docs(
#     session_id: str,
#     question: str,
#     top_k: int = 5,
#     search_type: str = "similarity",
#     filter_admin: bool = True,
# ) -> List[Document]:
#     search_question = f"{question} {TECHNICAL_QUERY_SUFFIX}"

#     retriever = get_retriever(
#         session_id=session_id,
#         top_k=top_k,
#         search_type=search_type,
#     )

#     docs = retriever.invoke(search_question)

#     if filter_admin:
#         docs = filter_study_docs(docs)

#     return docs


# def format_docs(docs: List[Document]) -> str:
#     formatted_chunks = []

#     for i, doc in enumerate(docs, start=1):
#         metadata = doc.metadata or {}

#         pdf_name = (
#             metadata.get("pdf_name")
#             or metadata.get("source")
#             or metadata.get("file_name")
#             or "Unknown PDF"
#         )

#         page_number = (
#             metadata.get("page_number")
#             or metadata.get("page")
#             or metadata.get("page_label")
#             or "Unknown page"
#         )

#         chunk_id = metadata.get("chunk_id", i)
#         chunk_text = doc.page_content.strip()

#         formatted_chunks.append(
#             f"""
# [Source {i}]
# PDF: {pdf_name}
# Page: {page_number}
# Chunk ID: {chunk_id}

# Content:
# {chunk_text}
# """
#         )

#     return "\n\n".join(formatted_chunks)


# def extract_sources(docs: List[Document]) -> List[Dict]:
#     sources = []
#     seen = set()

#     for doc in docs:
#         metadata = doc.metadata or {}

#         pdf_name = (
#             metadata.get("pdf_name")
#             or metadata.get("source")
#             or metadata.get("file_name")
#             or "Unknown PDF"
#         )

#         page_number = (
#             metadata.get("page_number")
#             or metadata.get("page")
#             or metadata.get("page_label")
#             or "Unknown page"
#         )

#         chunk_id = metadata.get("chunk_id", None)

#         key = f"{pdf_name}-{page_number}-{chunk_id}"

#         if key in seen:
#             continue

#         seen.add(key)

#         sources.append(
#             {
#                 "pdf_name": pdf_name,
#                 "page": page_number,
#                 "chunk_id": chunk_id,
#                 "content_preview": doc.page_content[:300],
#             }
#         )

#     return sources


# def build_user_prompt(
#     prompt_text: str,
#     question: str,
#     context: str,
# ) -> str:
#     return prompt_text.format(
#         question=question,
#         context=context,
#     )


# def build_prompt(prompt_text: str):
#     return ChatPromptTemplate.from_messages(
#         [
#             ("system", STUDY_SYSTEM_PROMPT),
#             ("human", prompt_text),
#         ]
#     )


# def run_llm_with_context(
#     question: str,
#     context: str,
#     prompt_text: str,
#     model_name: str = DEFAULT_LLM_MODEL,
#     temperature: float = 0.2,
# ) -> str:
#     provider = get_llm_provider()

#     if provider == "groq":
#         final_user_prompt = build_user_prompt(
#             prompt_text=prompt_text,
#             question=question,
#             context=context,
#         )

#         return call_groq_llm(
#             system_prompt=STUDY_SYSTEM_PROMPT,
#             user_prompt=final_user_prompt,
#             model_name=model_name or get_groq_model(),
#             temperature=temperature,
#         )

#     llm = get_local_llm(
#         model_name=model_name,
#         temperature=temperature,
#     )

#     prompt = build_prompt(prompt_text)
#     chain = prompt | llm | StrOutputParser()

#     return chain.invoke(
#         {
#             "question": question,
#             "context": context,
#         }
#     ).strip()


# def get_prompt_by_mode(answer_mode: str) -> str:
#     if answer_mode == "interview":
#         return INTERVIEW_ANSWER_PROMPT

#     if answer_mode == "equation":
#         return EQUATION_EXPLANATION_PROMPT

#     if answer_mode == "diagram":
#         return IMAGE_DIAGRAM_PROMPT

#     if answer_mode == "summary":
#         return SUMMARY_PROMPT

#     if answer_mode == "questions":
#         return QUESTION_GENERATION_PROMPT

#     if answer_mode == "flashcards":
#         return FLASHCARD_PROMPT

#     return RAG_USER_PROMPT


# def ask_rag(
#     session_id: str,
#     question: str,
#     model_name: str = DEFAULT_LLM_MODEL,
#     top_k: int = 5,
#     search_type: str = "similarity",
#     answer_mode: str = "rag",
# ) -> Dict:
#     if not question or not question.strip():
#         return {
#             "success": False,
#             "answer": "Please enter a valid question.",
#             "sources": [],
#             "model": model_name,
#             "provider": get_llm_provider(),
#             "retrieved_chunks": 0,
#         }

#     try:
#         docs = retrieve_docs(
#             session_id=session_id,
#             question=question,
#             top_k=top_k,
#             search_type=search_type,
#             filter_admin=True,
#         )

#         if not docs:
#             return {
#                 "success": True,
#                 "answer": NOT_FOUND_RESPONSE,
#                 "sources": [],
#                 "model": model_name,
#                 "provider": get_llm_provider(),
#                 "retrieved_chunks": 0,
#             }

#         context = format_docs(docs)
#         prompt_text = get_prompt_by_mode(answer_mode)

#         answer = run_llm_with_context(
#             question=question,
#             context=context,
#             prompt_text=prompt_text,
#             model_name=model_name,
#             temperature=get_groq_temperature(),
#         )

#         if not answer or answer.strip() == "":
#             answer = NOT_FOUND_RESPONSE

#         return {
#             "success": True,
#             "answer": answer,
#             "sources": extract_sources(docs),
#             "model": model_name,
#             "provider": get_llm_provider(),
#             "retrieved_chunks": len(docs),
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "answer": f"Error while generating answer: {str(e)}",
#             "sources": [],
#             "model": model_name,
#             "provider": get_llm_provider(),
#             "retrieved_chunks": 0,
#         }


# def summarize_notes(
#     session_id: str,
#     topic: str = "Summarize only technical study concepts, definitions, algorithms, methods, examples, and interview important points from the uploaded notes. Ignore course policy, deadlines, submissions, grading, and logistics.",
#     model_name: str = DEFAULT_LLM_MODEL,
#     top_k: int = 5,
# ) -> Dict:
#     try:
#         docs = retrieve_docs(
#             session_id=session_id,
#             question=topic,
#             top_k=top_k,
#             search_type="mmr",
#             filter_admin=True,
#         )

#         if not docs:
#             return {
#                 "success": True,
#                 "answer": NOT_FOUND_RESPONSE,
#                 "sources": [],
#                 "model": model_name,
#                 "provider": get_llm_provider(),
#                 "retrieved_chunks": 0,
#             }

#         context = format_docs(docs)

#         answer = run_llm_with_context(
#             question=topic,
#             context=context,
#             prompt_text=SUMMARY_PROMPT,
#             model_name=model_name,
#             temperature=get_groq_temperature(),
#         )

#         if not answer or answer.strip() == "":
#             answer = NOT_FOUND_RESPONSE

#         return {
#             "success": True,
#             "answer": answer,
#             "sources": extract_sources(docs),
#             "model": model_name,
#             "provider": get_llm_provider(),
#             "retrieved_chunks": len(docs),
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "answer": f"Error while summarizing notes: {str(e)}",
#             "sources": [],
#             "model": model_name,
#             "provider": get_llm_provider(),
#             "retrieved_chunks": 0,
#         }


# def generate_questions(
#     session_id: str,
#     topic: str = "Generate interview questions only from technical study concepts in uploaded notes. Ignore course policy, deadlines, submissions, grading, and logistics.",
#     model_name: str = DEFAULT_LLM_MODEL,
#     top_k: int = 5,
# ) -> Dict:
#     try:
#         docs = retrieve_docs(
#             session_id=session_id,
#             question=topic,
#             top_k=top_k,
#             search_type="mmr",
#             filter_admin=True,
#         )

#         if not docs:
#             return {
#                 "success": True,
#                 "answer": NOT_FOUND_RESPONSE,
#                 "sources": [],
#                 "model": model_name,
#                 "provider": get_llm_provider(),
#                 "retrieved_chunks": 0,
#             }

#         context = format_docs(docs)

#         answer = run_llm_with_context(
#             question=topic,
#             context=context,
#             prompt_text=QUESTION_GENERATION_PROMPT,
#             model_name=model_name,
#             temperature=0.35,
#         )

#         if not answer or answer.strip() == "":
#             answer = NOT_FOUND_RESPONSE

#         return {
#             "success": True,
#             "answer": answer,
#             "sources": extract_sources(docs),
#             "model": model_name,
#             "provider": get_llm_provider(),
#             "retrieved_chunks": len(docs),
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "answer": f"Error while generating questions: {str(e)}",
#             "sources": [],
#             "model": model_name,
#             "provider": get_llm_provider(),
#             "retrieved_chunks": 0,
#         }


# def generate_flashcards(
#     session_id: str,
#     topic: str = "Generate interactive MCQ flashcards only from technical study concepts in uploaded notes. Ignore course policy, deadlines, submissions, grading, and logistics.",
#     model_name: str = DEFAULT_LLM_MODEL,
#     top_k: int = 5,
# ) -> Dict:
#     try:
#         docs = retrieve_docs(
#             session_id=session_id,
#             question=topic,
#             top_k=top_k,
#             search_type="mmr",
#             filter_admin=True,
#         )

#         if not docs:
#             return {
#                 "success": True,
#                 "answer": NOT_FOUND_RESPONSE,
#                 "sources": [],
#                 "model": model_name,
#                 "provider": get_llm_provider(),
#                 "retrieved_chunks": 0,
#             }

#         context = format_docs(docs)

#         answer = run_llm_with_context(
#             question=topic,
#             context=context,
#             prompt_text=FLASHCARD_PROMPT,
#             model_name=model_name,
#             temperature=0.25,
#         )

#         if not answer or answer.strip() == "":
#             answer = NOT_FOUND_RESPONSE

#         return {
#             "success": True,
#             "answer": answer,
#             "sources": extract_sources(docs),
#             "model": model_name,
#             "provider": get_llm_provider(),
#             "retrieved_chunks": len(docs),
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "answer": f"Error while generating flashcards: {str(e)}",
#             "sources": [],
#             "model": model_name,
#             "provider": get_llm_provider(),
#             "retrieved_chunks": 0,
#         }


# def ask_direct_llm(
#     question: str,
#     model_name: str = DEFAULT_LLM_MODEL,
# ) -> Dict:
#     if not question or not question.strip():
#         return {
#             "success": False,
#             "answer": "Please enter a valid question.",
#             "model": model_name,
#             "provider": get_llm_provider(),
#         }

#     try:
#         if get_llm_provider() == "groq":
#             answer = call_groq_llm(
#                 system_prompt="You are a helpful AI study and interview preparation assistant. Explain in simple English with useful study points.",
#                 user_prompt=question,
#                 model_name=model_name or get_groq_model(),
#                 temperature=get_groq_temperature(),
#             )

#             return {
#                 "success": True,
#                 "answer": answer,
#                 "model": model_name,
#                 "provider": "groq",
#             }

#         llm = get_local_llm(
#             model_name=model_name,
#             temperature=0.3,
#         )

#         prompt = ChatPromptTemplate.from_messages(
#             [
#                 (
#                     "system",
#                     "You are a helpful AI study and interview preparation assistant. Explain in simple English with useful study points.",
#                 ),
#                 ("human", "{question}"),
#             ]
#         )

#         chain = prompt | llm | StrOutputParser()
#         answer = chain.invoke({"question": question}).strip()

#         return {
#             "success": True,
#             "answer": answer,
#             "model": model_name,
#             "provider": "ollama",
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "answer": f"Error while calling LLM: {str(e)}",
#             "model": model_name,
#             "provider": get_llm_provider(),
#         }


# def check_rag_ready(session_id: str) -> bool:
#     try:
#         status = get_vector_store_status(session_id)
#         return bool(status.get("ready", False))
#     except Exception:
#         return False


# def get_rag_status(session_id: str) -> Dict:
#     try:
#         status = get_vector_store_status(session_id)
#         status["llm_provider"] = get_llm_provider()
#         status["groq_configured"] = is_groq_configured()
#         status["groq_model"] = get_groq_model()
#         return status
#     except Exception as e:
#         return {
#             "ready": False,
#             "total_vectors": 0,
#             "llm_provider": get_llm_provider(),
#             "groq_configured": is_groq_configured(),
#             "error": str(e),
#         }

from typing import Dict, List

from groq import Groq
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser

from src.embeddings import get_embedding_model
from src.session_manager import get_chroma_path
from src.vector_store import get_collection_name, get_vector_store_status

from src.config import (
    get_llm_provider,
    get_groq_api_key,
    get_groq_model,
    get_groq_temperature,
    get_groq_max_tokens,
    is_groq_configured,
    get_backend_top_k,
    get_backend_search_type,
)

from src.prompts import (
    SYSTEM_PROMPT,
    RAG_USER_PROMPT,
    INTERVIEW_ANSWER_PROMPT,
    SUMMARY_PROMPT,
    QUESTION_GENERATION_PROMPT,
    FLASHCARD_PROMPT,
    EQUATION_EXPLANATION_PROMPT,
    IMAGE_DIAGRAM_PROMPT,
    NOT_FOUND_RESPONSE,
)


DEFAULT_LLM_MODEL = "llama-3.1-8b-instant"


STUDY_SYSTEM_PROMPT = """
You are an AI Study and Interview Preparation Assistant.

Follow these rules strictly:
1. Answer ONLY using the provided uploaded PDF context.
2. Do NOT use outside knowledge.
3. Do NOT guess.
4. If answer is missing, say exactly:
   "I could not find this in your uploaded notes."
5. Use simple English.
6. Make the answer useful for study, exams, viva, and interviews.
7. Focus on technical concepts, definitions, algorithms, methods, examples, advantages, limitations, and applications.
8. Ignore administrative/course policy content unless the user directly asks about it.
9. Ignore deadlines, submissions, grading, late periods, office hours, lecture rules, and logistics unless directly asked.
10. Do not include unnecessary information.
11. Do not repeat the same point again and again.
12. Use headings and bullet points.
13. Always include citations from the given context only.
14. Do not create fake PDF names or page numbers.
""".strip()


ADMIN_KEYWORDS = [
    "gradescope",
    "late period",
    "late periods",
    "submission",
    "submissions",
    "homework",
    "assignment deadline",
    "deadline",
    "grading",
    "grade",
    "office hour",
    "office hours",
    "lecture rule",
    "attendance",
    "policy",
    "course policy",
    "logistics",
    "piazza",
    "ed discussion",
    "canvas",
    "exam date",
    "due date",
]


TECHNICAL_QUERY_SUFFIX = (
    " technical concepts definitions algorithms methods models examples "
    "applications advantages limitations exam viva interview study notes "
    "ignore course policy deadlines grading submissions logistics"
)


# ---------------------------------------------------------
# LLM helpers
# ---------------------------------------------------------

def get_local_llm(
    model_name: str = "qwen2.5:3b",
    temperature: float = 0.2,
):
    return ChatOllama(
        model=model_name,
        temperature=temperature,
    )


def call_groq_llm(
    system_prompt: str,
    user_prompt: str,
    model_name: str = DEFAULT_LLM_MODEL,
    temperature: float = 0.2,
) -> str:
    if not is_groq_configured():
        raise ValueError(
            "GROQ_API_KEY is missing. Add GROQ_API_KEY in your root .env.local file."
        )

    safe_model = model_name or get_groq_model()
    safe_temperature = float(temperature if temperature is not None else get_groq_temperature())

    client = Groq(api_key=get_groq_api_key())

    response = client.chat.completions.create(
        model=safe_model,
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
        temperature=safe_temperature,
        max_tokens=get_groq_max_tokens(),
    )

    return response.choices[0].message.content.strip()


# ---------------------------------------------------------
# Vector DB helpers
# ---------------------------------------------------------

def get_vector_db(session_id: str):
    chroma_path = get_chroma_path(session_id)
    embedding_model = get_embedding_model()

    vector_db = Chroma(
        collection_name=get_collection_name(session_id),
        persist_directory=chroma_path,
        embedding_function=embedding_model,
    )

    return vector_db


def get_retriever(
    session_id: str,
    top_k: int = 5,
    search_type: str = "similarity",
):
    safe_top_k = int(top_k or get_backend_top_k())

    if safe_top_k <= 0:
        safe_top_k = get_backend_top_k()

    safe_search_type = search_type or get_backend_search_type()

    vector_db = get_vector_db(session_id)

    if safe_search_type == "mmr":
        return vector_db.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": safe_top_k,
                "fetch_k": max(safe_top_k * 4, 20),
            },
        )

    return vector_db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": safe_top_k},
    )


# ---------------------------------------------------------
# Filtering helpers
# ---------------------------------------------------------

def is_admin_content(text: str) -> bool:
    if not text:
        return False

    lowered = text.lower()
    hits = 0

    for keyword in ADMIN_KEYWORDS:
        if keyword in lowered:
            hits += 1

    return hits >= 2


def filter_study_docs(docs: List[Document]) -> List[Document]:
    if not docs:
        return []

    study_docs = []

    for doc in docs:
        content = doc.page_content or ""

        if is_admin_content(content):
            continue

        study_docs.append(doc)

    if study_docs:
        return study_docs

    return docs


def retrieve_docs(
    session_id: str,
    question: str,
    top_k: int = 5,
    search_type: str = "similarity",
    filter_admin: bool = True,
) -> List[Document]:
    if not question or not question.strip():
        return []

    search_question = f"{question} {TECHNICAL_QUERY_SUFFIX}"

    retriever = get_retriever(
        session_id=session_id,
        top_k=top_k,
        search_type=search_type,
    )

    docs = retriever.invoke(search_question)

    if filter_admin:
        docs = filter_study_docs(docs)

    return docs


# ---------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------

def format_docs(docs: List[Document]) -> str:
    formatted_chunks = []

    for i, doc in enumerate(docs, start=1):
        metadata = doc.metadata or {}

        pdf_name = (
            metadata.get("pdf_name")
            or metadata.get("source")
            or metadata.get("file_name")
            or "Unknown PDF"
        )

        page_number = (
            metadata.get("page_number")
            or metadata.get("page")
            or metadata.get("page_label")
            or "Unknown page"
        )

        chunk_id = metadata.get("chunk_id", i)
        chunk_text = (doc.page_content or "").strip()

        formatted_chunks.append(
            f"""
[Source {i}]
PDF: {pdf_name}
Page: {page_number}
Chunk ID: {chunk_id}

Content:
{chunk_text}
""".strip()
        )

    return "\n\n".join(formatted_chunks)


def extract_sources(docs: List[Document]) -> List[Dict]:
    sources = []
    seen = set()

    for doc in docs:
        metadata = doc.metadata or {}

        pdf_name = (
            metadata.get("pdf_name")
            or metadata.get("source")
            or metadata.get("file_name")
            or "Unknown PDF"
        )

        page_number = (
            metadata.get("page_number")
            or metadata.get("page")
            or metadata.get("page_label")
            or "Unknown page"
        )

        chunk_id = metadata.get("chunk_id", None)

        key = f"{pdf_name}-{page_number}-{chunk_id}"

        if key in seen:
            continue

        seen.add(key)

        sources.append(
            {
                "pdf_name": pdf_name,
                "page": page_number,
                "chunk_id": chunk_id,
                "content_preview": (doc.page_content or "")[:300],
            }
        )

    return sources


def build_user_prompt(
    prompt_text: str,
    question: str,
    context: str,
) -> str:
    return prompt_text.format(
        question=question,
        context=context,
    )


def build_prompt(prompt_text: str):
    return ChatPromptTemplate.from_messages(
        [
            ("system", STUDY_SYSTEM_PROMPT),
            ("human", prompt_text),
        ]
    )


# ---------------------------------------------------------
# LLM execution
# ---------------------------------------------------------

def run_llm_with_context(
    question: str,
    context: str,
    prompt_text: str,
    model_name: str = DEFAULT_LLM_MODEL,
    temperature: float = 0.2,
) -> str:
    provider = get_llm_provider()

    if provider == "groq":
        final_user_prompt = build_user_prompt(
            prompt_text=prompt_text,
            question=question,
            context=context,
        )

        return call_groq_llm(
            system_prompt=STUDY_SYSTEM_PROMPT,
            user_prompt=final_user_prompt,
            model_name=model_name or get_groq_model(),
            temperature=temperature,
        )

    llm = get_local_llm(
        model_name=model_name,
        temperature=temperature,
    )

    prompt = build_prompt(prompt_text)
    chain = prompt | llm | StrOutputParser()

    return chain.invoke(
        {
            "question": question,
            "context": context,
        }
    ).strip()


def get_prompt_by_mode(answer_mode: str) -> str:
    if answer_mode == "interview":
        return INTERVIEW_ANSWER_PROMPT

    if answer_mode == "equation":
        return EQUATION_EXPLANATION_PROMPT

    if answer_mode == "diagram":
        return IMAGE_DIAGRAM_PROMPT

    if answer_mode == "summary":
        return SUMMARY_PROMPT

    if answer_mode == "questions":
        return QUESTION_GENERATION_PROMPT

    if answer_mode == "flashcards":
        return FLASHCARD_PROMPT

    return RAG_USER_PROMPT


# ---------------------------------------------------------
# Main RAG question answering
# ---------------------------------------------------------

def ask_rag(
    session_id: str,
    question: str,
    model_name: str = DEFAULT_LLM_MODEL,
    top_k: int = 5,
    search_type: str = "similarity",
    answer_mode: str = "rag",
) -> Dict:
    if not question or not question.strip():
        return {
            "success": False,
            "answer": "Please enter a valid question.",
            "sources": [],
            "model": model_name,
            "provider": get_llm_provider(),
            "retrieved_chunks": 0,
        }

    try:
        docs = retrieve_docs(
            session_id=session_id,
            question=question,
            top_k=top_k,
            search_type=search_type,
            filter_admin=True,
        )

        if not docs:
            return {
                "success": True,
                "answer": NOT_FOUND_RESPONSE,
                "sources": [],
                "model": model_name,
                "provider": get_llm_provider(),
                "retrieved_chunks": 0,
            }

        context = format_docs(docs)
        prompt_text = get_prompt_by_mode(answer_mode)

        answer = run_llm_with_context(
            question=question,
            context=context,
            prompt_text=prompt_text,
            model_name=model_name,
            temperature=get_groq_temperature(),
        )

        if not answer or answer.strip() == "":
            answer = NOT_FOUND_RESPONSE

        return {
            "success": True,
            "answer": answer,
            "sources": extract_sources(docs),
            "model": model_name,
            "provider": get_llm_provider(),
            "retrieved_chunks": len(docs),
        }

    except Exception as e:
        return {
            "success": False,
            "answer": f"Error while generating answer: {str(e)}",
            "sources": [],
            "model": model_name,
            "provider": get_llm_provider(),
            "retrieved_chunks": 0,
        }


# ---------------------------------------------------------
# Study tools
# ---------------------------------------------------------

def summarize_notes(
    session_id: str,
    topic: str = "Summarize only technical study concepts, definitions, algorithms, methods, examples, and interview important points from the uploaded notes. Ignore course policy, deadlines, submissions, grading, and logistics.",
    model_name: str = DEFAULT_LLM_MODEL,
    top_k: int = 5,
) -> Dict:
    try:
        docs = retrieve_docs(
            session_id=session_id,
            question=topic,
            top_k=top_k,
            search_type="mmr",
            filter_admin=True,
        )

        if not docs:
            return {
                "success": True,
                "answer": NOT_FOUND_RESPONSE,
                "sources": [],
                "model": model_name,
                "provider": get_llm_provider(),
                "retrieved_chunks": 0,
            }

        context = format_docs(docs)

        answer = run_llm_with_context(
            question=topic,
            context=context,
            prompt_text=SUMMARY_PROMPT,
            model_name=model_name,
            temperature=get_groq_temperature(),
        )

        if not answer or answer.strip() == "":
            answer = NOT_FOUND_RESPONSE

        return {
            "success": True,
            "answer": answer,
            "sources": extract_sources(docs),
            "model": model_name,
            "provider": get_llm_provider(),
            "retrieved_chunks": len(docs),
        }

    except Exception as e:
        return {
            "success": False,
            "answer": f"Error while summarizing notes: {str(e)}",
            "sources": [],
            "model": model_name,
            "provider": get_llm_provider(),
            "retrieved_chunks": 0,
        }


def generate_questions(
    session_id: str,
    topic: str = "Generate interview questions only from technical study concepts in uploaded notes. Ignore course policy, deadlines, submissions, grading, and logistics.",
    model_name: str = DEFAULT_LLM_MODEL,
    top_k: int = 5,
) -> Dict:
    try:
        docs = retrieve_docs(
            session_id=session_id,
            question=topic,
            top_k=top_k,
            search_type="mmr",
            filter_admin=True,
        )

        if not docs:
            return {
                "success": True,
                "answer": NOT_FOUND_RESPONSE,
                "sources": [],
                "model": model_name,
                "provider": get_llm_provider(),
                "retrieved_chunks": 0,
            }

        context = format_docs(docs)

        answer = run_llm_with_context(
            question=topic,
            context=context,
            prompt_text=QUESTION_GENERATION_PROMPT,
            model_name=model_name,
            temperature=0.35,
        )

        if not answer or answer.strip() == "":
            answer = NOT_FOUND_RESPONSE

        return {
            "success": True,
            "answer": answer,
            "sources": extract_sources(docs),
            "model": model_name,
            "provider": get_llm_provider(),
            "retrieved_chunks": len(docs),
        }

    except Exception as e:
        return {
            "success": False,
            "answer": f"Error while generating questions: {str(e)}",
            "sources": [],
            "model": model_name,
            "provider": get_llm_provider(),
            "retrieved_chunks": 0,
        }


def generate_flashcards(
    session_id: str,
    topic: str = "Generate interactive MCQ flashcards only from technical study concepts in uploaded notes. Ignore course policy, deadlines, submissions, grading, and logistics.",
    model_name: str = DEFAULT_LLM_MODEL,
    top_k: int = 5,
) -> Dict:
    try:
        docs = retrieve_docs(
            session_id=session_id,
            question=topic,
            top_k=top_k,
            search_type="mmr",
            filter_admin=True,
        )

        if not docs:
            return {
                "success": True,
                "answer": NOT_FOUND_RESPONSE,
                "sources": [],
                "model": model_name,
                "provider": get_llm_provider(),
                "retrieved_chunks": 0,
            }

        context = format_docs(docs)

        answer = run_llm_with_context(
            question=topic,
            context=context,
            prompt_text=FLASHCARD_PROMPT,
            model_name=model_name,
            temperature=0.25,
        )

        if not answer or answer.strip() == "":
            answer = NOT_FOUND_RESPONSE

        return {
            "success": True,
            "answer": answer,
            "sources": extract_sources(docs),
            "model": model_name,
            "provider": get_llm_provider(),
            "retrieved_chunks": len(docs),
        }

    except Exception as e:
        return {
            "success": False,
            "answer": f"Error while generating flashcards: {str(e)}",
            "sources": [],
            "model": model_name,
            "provider": get_llm_provider(),
            "retrieved_chunks": 0,
        }


# ---------------------------------------------------------
# Direct LLM helper
# ---------------------------------------------------------

def ask_direct_llm(
    question: str,
    model_name: str = DEFAULT_LLM_MODEL,
) -> Dict:
    if not question or not question.strip():
        return {
            "success": False,
            "answer": "Please enter a valid question.",
            "model": model_name,
            "provider": get_llm_provider(),
        }

    try:
        if get_llm_provider() == "groq":
            answer = call_groq_llm(
                system_prompt=(
                    "You are a helpful AI study and interview preparation assistant. "
                    "Explain in simple English with useful study points."
                ),
                user_prompt=question,
                model_name=model_name or get_groq_model(),
                temperature=get_groq_temperature(),
            )

            return {
                "success": True,
                "answer": answer,
                "model": model_name,
                "provider": "groq",
            }

        llm = get_local_llm(
            model_name=model_name,
            temperature=0.3,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI study and interview preparation assistant. Explain in simple English with useful study points.",
                ),
                ("human", "{question}"),
            ]
        )

        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"question": question}).strip()

        return {
            "success": True,
            "answer": answer,
            "model": model_name,
            "provider": "ollama",
        }

    except Exception as e:
        return {
            "success": False,
            "answer": f"Error while calling LLM: {str(e)}",
            "model": model_name,
            "provider": get_llm_provider(),
        }


# ---------------------------------------------------------
# Status helpers
# ---------------------------------------------------------

def check_rag_ready(session_id: str) -> bool:
    try:
        status = get_vector_store_status(session_id)
        return bool(status.get("ready", False))
    except Exception:
        return False


def get_rag_status(session_id: str) -> Dict:
    try:
        status = get_vector_store_status(session_id)
        status["llm_provider"] = get_llm_provider()
        status["groq_configured"] = is_groq_configured()
        status["groq_model"] = get_groq_model()
        return status
    except Exception as e:
        return {
            "ready": False,
            "total_vectors": 0,
            "llm_provider": get_llm_provider(),
            "groq_configured": is_groq_configured(),
            "error": str(e),
        }


# ---------------------------------------------------------
# Self test
# ---------------------------------------------------------

def run_rag_chain_self_test(session_id: str) -> Dict:
    try:
        status = get_rag_status(session_id)

        if not status.get("ready"):
            return {
                "success": False,
                "message": "RAG is not ready for this session.",
                "status": status,
            }

        result = ask_rag(
            session_id=session_id,
            question="Give a short summary of these notes.",
            model_name=get_groq_model(),
            top_k=3,
            search_type="similarity",
            answer_mode="rag",
        )

        return {
            "success": result.get("success", False),
            "status": status,
            "result": result,
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
        }