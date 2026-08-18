from typing import Dict, List

from groq import Groq
from langchain_core.documents import Document

from src.vector_store import (
    get_vector_store_status,
    get_retriever as get_vector_store_retriever,
    similarity_search,
    mmr_search,
)

from src.config import (
    get_groq_api_key,
    get_groq_model,
    get_groq_temperature,
    get_groq_max_tokens,
    is_groq_configured,
    get_backend_top_k,
    get_backend_search_type,
)

from src.prompts import (
    RAG_USER_PROMPT,
    INTERVIEW_ANSWER_PROMPT,
    SUMMARY_PROMPT,
    QUESTION_GENERATION_PROMPT,
    FLASHCARD_PROMPT,
    EQUATION_EXPLANATION_PROMPT,
    IMAGE_DIAGRAM_PROMPT,
    NOT_FOUND_RESPONSE,
)


DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"

# Same detailed RAG behavior, but safer for low-memory deployment.
DEFAULT_RAG_TOP_K = 10
DEFAULT_RAG_FETCH_K = 40
MAX_CONTEXT_CHARS = 30000


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
7. Focus on technical concepts, definitions, algorithms, methods, examples, advantages, limitations, applications, architecture, working, steps, formulas, and comparisons.
8. Ignore administrative/course policy content unless the user directly asks about it.
9. Ignore deadlines, submissions, grading, late periods, office hours, lecture rules, and logistics unless directly asked.
10. Do not include unnecessary information.
11. Do not repeat the same point again and again.
12. Use proper headings, subheadings, bullet points, and examples.
13. Always include citations from the given context only.
14. Do not create fake PDF names or page numbers.
15. If the user asks a specific topic, explain it in depth from the retrieved PDF context, not just a short overview.
16. Prefer detailed explanation over short answer.
17. If retrieved context has only partial information, explain the available part clearly and mention what is missing.
""".strip()


DETAILED_RAG_PROMPT = """
You are given PDF context and a user question.

Your task:
Answer the question in a detailed study-note style using ONLY the PDF context.

Important rules:
1. Do NOT give only overview.
2. Explain the topic in depth.
3. Use simple English.
4. Use headings and bullet points.
5. Include these sections when available in context:
   - Definition
   - Main idea
   - Working / Process / Steps
   - Architecture / Components
   - Types
   - Examples
   - Advantages
   - Limitations
   - Applications
   - Interview important points
6. If the topic is an algorithm, model, method, architecture, or protocol, explain it step-by-step.
7. If formulas are present, explain each term clearly.
8. If examples are present in the context, include them.
9. If the PDF context does not contain enough details, first explain whatever is available, then write:
   "The uploaded notes do not contain more detailed information about this part."
10. Add citations using the given source labels like [Source 1], [Source 2].
11. Do not invent information outside the PDF context.

PDF Context:
{context}

User Question:
{question}

Detailed Answer:
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
    "applications advantages limitations architecture working steps formula "
    "exam viva interview study notes detailed explanation "
    "ignore course policy deadlines grading submissions logistics"
)


# ---------------------------------------------------------
# Groq LLM helper
# ---------------------------------------------------------

def call_groq_llm(
    system_prompt: str,
    user_prompt: str,
    model_name: str = DEFAULT_GROQ_MODEL,
    temperature: float = 0.2,
) -> str:
    if not is_groq_configured():
        raise ValueError(
            "GROQ_API_KEY is missing. Add GROQ_API_KEY in your root .env.local file."
        )

    safe_model = model_name or get_groq_model() or DEFAULT_GROQ_MODEL
    safe_temperature = float(
        temperature if temperature is not None else get_groq_temperature()
    )

    configured_max_tokens = get_groq_max_tokens()

    try:
        configured_max_tokens = int(configured_max_tokens)
    except Exception:
        configured_max_tokens = 1800

    # Detailed answers need more output tokens.
    safe_max_tokens = max(configured_max_tokens, 2000)

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
        max_tokens=safe_max_tokens,
    )

    return response.choices[0].message.content.strip()


# ---------------------------------------------------------
# Vector DB helpers
# ---------------------------------------------------------

def get_vector_db(session_id: str):
    """
    Backward-compatible helper.

    Old version returned Chroma.
    New version uses lightweight vector_store.py retriever.
    """

    return get_vector_store_retriever(
        session_id=session_id,
        top_k=DEFAULT_RAG_TOP_K,
        search_type="mmr",
    )


def get_retriever(
    session_id: str,
    top_k: int = DEFAULT_RAG_TOP_K,
    search_type: str = "mmr",
):
    safe_top_k = int(top_k or get_backend_top_k() or DEFAULT_RAG_TOP_K)

    if safe_top_k <= 0:
        safe_top_k = DEFAULT_RAG_TOP_K

    # Keep old behavior: never retrieve too few chunks.
    safe_top_k = max(safe_top_k, DEFAULT_RAG_TOP_K)

    safe_search_type = search_type or get_backend_search_type() or "mmr"

    return get_vector_store_retriever(
        session_id=session_id,
        top_k=safe_top_k,
        search_type=safe_search_type,
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


def dedupe_docs(docs: List[Document]) -> List[Document]:
    unique_docs = []
    seen = set()

    for doc in docs:
        metadata = doc.metadata or {}
        content = (doc.page_content or "").strip()

        key = (
            metadata.get("pdf_name"),
            metadata.get("source"),
            metadata.get("file_name"),
            metadata.get("page_number") or metadata.get("page"),
            metadata.get("chunk_id"),
            content[:300],
        )

        if key in seen:
            continue

        seen.add(key)
        unique_docs.append(doc)

    return unique_docs


def retrieve_docs(
    session_id: str,
    question: str,
    top_k: int = DEFAULT_RAG_TOP_K,
    search_type: str = "mmr",
    filter_admin: bool = True,
) -> List[Document]:
    """
    Improved retrieval for detailed explanations:
    1. Uses multiple query variants.
    2. Retrieves more chunks.
    3. Uses MMR by default.
    4. Deduplicates chunks.
    5. Filters admin/course policy content.

    Lightweight change:
    Uses src.vector_store lightweight JSON retrieval instead of direct Chroma.
    """
    if not question or not question.strip():
        return []

    safe_top_k = max(int(top_k or DEFAULT_RAG_TOP_K), DEFAULT_RAG_TOP_K)

    clean_question = question.strip()

    query_variants = [
        clean_question,
        f"{clean_question} detailed explanation working steps examples advantages limitations applications",
        f"{clean_question} definition architecture components types process formula interview exam",
        f"{clean_question} {TECHNICAL_QUERY_SUFFIX}",
    ]

    all_docs: List[Document] = []

    for query in query_variants:
        try:
            safe_search_type = search_type or get_backend_search_type() or "mmr"

            if safe_search_type == "mmr":
                docs = mmr_search(
                    session_id=session_id,
                    query=query,
                    top_k=safe_top_k,
                    fetch_k=max(safe_top_k * 4, DEFAULT_RAG_FETCH_K),
                )
            else:
                docs = similarity_search(
                    session_id=session_id,
                    query=query,
                    top_k=safe_top_k,
                )

            all_docs.extend(docs)

        except Exception:
            continue

    all_docs = dedupe_docs(all_docs)

    if filter_admin:
        all_docs = filter_study_docs(all_docs)

    return all_docs[: safe_top_k]


# ---------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------

def normalize_page_number(page_value):
    if page_value is None:
        return "Unknown page"

    try:
        page_int = int(page_value)

        # Some loaders store page as 0-based index.
        if page_int >= 0:
            return page_int + 1

        return page_int
    except Exception:
        return page_value


def format_docs(docs: List[Document]) -> str:
    formatted_chunks = []
    current_length = 0

    for i, doc in enumerate(docs, start=1):
        metadata = doc.metadata or {}

        pdf_name = (
            metadata.get("pdf_name")
            or metadata.get("source")
            or metadata.get("file_name")
            or "Unknown PDF"
        )

        raw_page_number = (
            metadata.get("page_number")
            or metadata.get("page")
            or metadata.get("page_label")
            or None
        )

        page_number = normalize_page_number(raw_page_number)

        chunk_id = metadata.get("chunk_id", i)
        chunk_text = (doc.page_content or "").strip()

        if not chunk_text:
            continue

        formatted_chunk = f"""
[Source {i}]
PDF: {pdf_name}
Page: {page_number}
Chunk ID: {chunk_id}

Content:
{chunk_text}
""".strip()

        if current_length + len(formatted_chunk) > MAX_CONTEXT_CHARS:
            break

        formatted_chunks.append(formatted_chunk)
        current_length += len(formatted_chunk)

    return "\n\n".join(formatted_chunks)


def extract_sources(docs: List[Document]) -> List[Dict]:
    sources = []
    seen = set()

    for index, doc in enumerate(docs, start=1):
        metadata = doc.metadata or {}

        pdf_name = (
            metadata.get("pdf_name")
            or metadata.get("source")
            or metadata.get("file_name")
            or "Unknown PDF"
        )

        raw_page_number = (
            metadata.get("page_number")
            or metadata.get("page")
            or metadata.get("page_label")
            or None
        )

        page_number = normalize_page_number(raw_page_number)
        chunk_id = metadata.get("chunk_id", None)

        key = f"{pdf_name}-{page_number}-{chunk_id}"

        if key in seen:
            continue

        seen.add(key)

        sources.append(
            {
                "source_number": index,
                "pdf_name": pdf_name,
                "page": page_number,
                "chunk_id": chunk_id,
                "content_preview": (doc.page_content or "")[:500],
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


# ---------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------

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

    # Default RAG mode uses stronger detailed prompt.
    return DETAILED_RAG_PROMPT


# ---------------------------------------------------------
# LLM execution
# ---------------------------------------------------------

def run_llm_with_context(
    question: str,
    context: str,
    prompt_text: str,
    model_name: str = DEFAULT_GROQ_MODEL,
    temperature: float = 0.2,
) -> str:
    final_user_prompt = build_user_prompt(
        prompt_text=prompt_text,
        question=question,
        context=context,
    )

    return call_groq_llm(
        system_prompt=STUDY_SYSTEM_PROMPT,
        user_prompt=final_user_prompt,
        model_name=model_name or get_groq_model() or DEFAULT_GROQ_MODEL,
        temperature=temperature,
    )


# ---------------------------------------------------------
# Main RAG question answering
# ---------------------------------------------------------

def ask_rag(
    session_id: str,
    question: str,
    model_name: str = DEFAULT_GROQ_MODEL,
    top_k: int = DEFAULT_RAG_TOP_K,
    search_type: str = "mmr",
    answer_mode: str = "rag",
) -> Dict:
    if not question or not question.strip():
        return {
            "success": False,
            "answer": "Please enter a valid question.",
            "sources": [],
            "model": model_name,
            "provider": "groq",
            "retrieved_chunks": 0,
        }

    try:
        safe_top_k = max(int(top_k or DEFAULT_RAG_TOP_K), DEFAULT_RAG_TOP_K)

        docs = retrieve_docs(
            session_id=session_id,
            question=question,
            top_k=safe_top_k,
            search_type=search_type or "mmr",
            filter_admin=True,
        )

        if not docs:
            return {
                "success": True,
                "answer": NOT_FOUND_RESPONSE,
                "sources": [],
                "model": model_name,
                "provider": "groq",
                "retrieved_chunks": 0,
            }

        context = format_docs(docs)

        if not context.strip():
            return {
                "success": True,
                "answer": NOT_FOUND_RESPONSE,
                "sources": [],
                "model": model_name,
                "provider": "groq",
                "retrieved_chunks": 0,
            }

        prompt_text = get_prompt_by_mode(answer_mode)

        answer = run_llm_with_context(
            question=question,
            context=context,
            prompt_text=prompt_text,
            model_name=model_name or get_groq_model() or DEFAULT_GROQ_MODEL,
            temperature=get_groq_temperature(),
        )

        if not answer or answer.strip() == "":
            answer = NOT_FOUND_RESPONSE

        return {
            "success": True,
            "answer": answer,
            "sources": extract_sources(docs),
            "model": model_name or get_groq_model() or DEFAULT_GROQ_MODEL,
            "provider": "groq",
            "retrieved_chunks": len(docs),
        }

    except Exception as e:
        return {
            "success": False,
            "answer": f"Error while generating answer: {str(e)}",
            "sources": [],
            "model": model_name,
            "provider": "groq",
            "retrieved_chunks": 0,
        }


# ---------------------------------------------------------
# Study tools
# ---------------------------------------------------------

def summarize_notes(
    session_id: str,
    topic: str = "Summarize only technical study concepts, definitions, algorithms, methods, examples, and interview important points from the uploaded notes. Ignore course policy, deadlines, submissions, grading, and logistics.",
    model_name: str = DEFAULT_GROQ_MODEL,
    top_k: int = DEFAULT_RAG_TOP_K,
) -> Dict:
    try:
        docs = retrieve_docs(
            session_id=session_id,
            question=topic,
            top_k=max(int(top_k or DEFAULT_RAG_TOP_K), DEFAULT_RAG_TOP_K),
            search_type="mmr",
            filter_admin=True,
        )

        if not docs:
            return {
                "success": True,
                "answer": NOT_FOUND_RESPONSE,
                "sources": [],
                "model": model_name,
                "provider": "groq",
                "retrieved_chunks": 0,
            }

        context = format_docs(docs)

        answer = run_llm_with_context(
            question=topic,
            context=context,
            prompt_text=SUMMARY_PROMPT,
            model_name=model_name or get_groq_model() or DEFAULT_GROQ_MODEL,
            temperature=get_groq_temperature(),
        )

        if not answer or answer.strip() == "":
            answer = NOT_FOUND_RESPONSE

        return {
            "success": True,
            "answer": answer,
            "sources": extract_sources(docs),
            "model": model_name or get_groq_model() or DEFAULT_GROQ_MODEL,
            "provider": "groq",
            "retrieved_chunks": len(docs),
        }

    except Exception as e:
        return {
            "success": False,
            "answer": f"Error while summarizing notes: {str(e)}",
            "sources": [],
            "model": model_name,
            "provider": "groq",
            "retrieved_chunks": 0,
        }


def generate_questions(
    session_id: str,
    topic: str = "Generate interview questions only from technical study concepts in uploaded notes. Ignore course policy, deadlines, submissions, grading, and logistics.",
    model_name: str = DEFAULT_GROQ_MODEL,
    top_k: int = DEFAULT_RAG_TOP_K,
) -> Dict:
    try:
        docs = retrieve_docs(
            session_id=session_id,
            question=topic,
            top_k=max(int(top_k or DEFAULT_RAG_TOP_K), DEFAULT_RAG_TOP_K),
            search_type="mmr",
            filter_admin=True,
        )

        if not docs:
            return {
                "success": True,
                "answer": NOT_FOUND_RESPONSE,
                "sources": [],
                "model": model_name,
                "provider": "groq",
                "retrieved_chunks": 0,
            }

        context = format_docs(docs)

        answer = run_llm_with_context(
            question=topic,
            context=context,
            prompt_text=QUESTION_GENERATION_PROMPT,
            model_name=model_name or get_groq_model() or DEFAULT_GROQ_MODEL,
            temperature=0.35,
        )

        if not answer or answer.strip() == "":
            answer = NOT_FOUND_RESPONSE

        return {
            "success": True,
            "answer": answer,
            "sources": extract_sources(docs),
            "model": model_name or get_groq_model() or DEFAULT_GROQ_MODEL,
            "provider": "groq",
            "retrieved_chunks": len(docs),
        }

    except Exception as e:
        return {
            "success": False,
            "answer": f"Error while generating questions: {str(e)}",
            "sources": [],
            "model": model_name,
            "provider": "groq",
            "retrieved_chunks": 0,
        }


def generate_flashcards(
    session_id: str,
    topic: str = "Generate interactive MCQ flashcards only from technical study concepts in uploaded notes. Ignore course policy, deadlines, submissions, grading, and logistics.",
    model_name: str = DEFAULT_GROQ_MODEL,
    top_k: int = DEFAULT_RAG_TOP_K,
) -> Dict:
    try:
        docs = retrieve_docs(
            session_id=session_id,
            question=topic,
            top_k=max(int(top_k or DEFAULT_RAG_TOP_K), DEFAULT_RAG_TOP_K),
            search_type="mmr",
            filter_admin=True,
        )

        if not docs:
            return {
                "success": True,
                "answer": NOT_FOUND_RESPONSE,
                "sources": [],
                "model": model_name,
                "provider": "groq",
                "retrieved_chunks": 0,
            }

        context = format_docs(docs)

        answer = run_llm_with_context(
            question=topic,
            context=context,
            prompt_text=FLASHCARD_PROMPT,
            model_name=model_name or get_groq_model() or DEFAULT_GROQ_MODEL,
            temperature=0.25,
        )

        if not answer or answer.strip() == "":
            answer = NOT_FOUND_RESPONSE

        return {
            "success": True,
            "answer": answer,
            "sources": extract_sources(docs),
            "model": model_name or get_groq_model() or DEFAULT_GROQ_MODEL,
            "provider": "groq",
            "retrieved_chunks": len(docs),
        }

    except Exception as e:
        return {
            "success": False,
            "answer": f"Error while generating flashcards: {str(e)}",
            "sources": [],
            "model": model_name,
            "provider": "groq",
            "retrieved_chunks": 0,
        }


# ---------------------------------------------------------
# Direct Groq helper
# ---------------------------------------------------------

def ask_direct_llm(
    question: str,
    model_name: str = DEFAULT_GROQ_MODEL,
) -> Dict:
    if not question or not question.strip():
        return {
            "success": False,
            "answer": "Please enter a valid question.",
            "model": model_name,
            "provider": "groq",
        }

    try:
        answer = call_groq_llm(
            system_prompt=(
                "You are a helpful AI study and interview preparation assistant. "
                "Explain in simple English with useful study points, examples, and clear structure."
            ),
            user_prompt=question,
            model_name=model_name or get_groq_model() or DEFAULT_GROQ_MODEL,
            temperature=get_groq_temperature(),
        )

        return {
            "success": True,
            "answer": answer,
            "model": model_name or get_groq_model() or DEFAULT_GROQ_MODEL,
            "provider": "groq",
        }

    except Exception as e:
        return {
            "success": False,
            "answer": f"Error while calling Groq LLM: {str(e)}",
            "model": model_name,
            "provider": "groq",
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
        status["llm_provider"] = "groq"
        status["groq_configured"] = is_groq_configured()
        status["groq_model"] = get_groq_model() or DEFAULT_GROQ_MODEL
        status["backend_top_k"] = max(
            int(get_backend_top_k() or DEFAULT_RAG_TOP_K),
            DEFAULT_RAG_TOP_K,
        )
        status["backend_search_type"] = get_backend_search_type() or "mmr"
        return status
    except Exception as e:
        return {
            "ready": False,
            "total_vectors": 0,
            "llm_provider": "groq",
            "groq_configured": is_groq_configured(),
            "groq_model": get_groq_model() or DEFAULT_GROQ_MODEL,
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
            question="Give a detailed summary of the main technical concepts from these notes.",
            model_name=get_groq_model() or DEFAULT_GROQ_MODEL,
            top_k=DEFAULT_RAG_TOP_K,
            search_type="mmr",
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
