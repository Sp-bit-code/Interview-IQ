// const DEFAULT_RAG_API_URL = "http://127.0.0.1:8000";

// export const RAG_API_BASE_URL =
//   import.meta.env.VITE_RAG_API_URL || DEFAULT_RAG_API_URL;

// /**
//  * Converts backend/FastAPI error response into readable message.
//  */
// async function getReadableError(response) {
//   try {
//     const data = await response.json();

//     if (typeof data?.detail === "string") {
//       return data.detail;
//     }

//     if (Array.isArray(data?.detail)) {
//       return data.detail
//         .map((item) => item?.msg || JSON.stringify(item))
//         .join(", ");
//     }

//     if (typeof data?.message === "string") {
//       return data.message;
//     }

//     if (typeof data?.answer === "string") {
//       return data.answer;
//     }

//     return JSON.stringify(data);
//   } catch {
//     return `Request failed with status ${response.status}`;
//   }
// }

// /**
//  * Normal fetch wrapper for JSON APIs.
//  */
// async function requestJson(endpoint, options = {}) {
//   const url = `${RAG_API_BASE_URL}${endpoint}`;

//   const response = await fetch(url, {
//     ...options,
//     headers: {
//       "Content-Type": "application/json",
//       ...(options.headers || {}),
//     },
//   });

//   if (!response.ok) {
//     const message = await getReadableError(response);
//     throw new Error(message);
//   }

//   return response.json();
// }

// /**
//  * Fetch wrapper for FormData APIs.
//  * Do not manually set Content-Type here.
//  * Browser will set multipart/form-data boundary automatically.
//  */
// async function requestForm(endpoint, formData, options = {}) {
//   const url = `${RAG_API_BASE_URL}${endpoint}`;

//   const response = await fetch(url, {
//     method: "POST",
//     ...options,
//     body: formData,
//     headers: {
//       ...(options.headers || {}),
//     },
//   });

//   if (!response.ok) {
//     const message = await getReadableError(response);
//     throw new Error(message);
//   }

//   return response.json();
// }

// /**
//  * Check if RAG backend is running.
//  * FastAPI route:
//  * GET /health
//  */
// export async function checkRagBackendHealth() {
//   return requestJson("/health", {
//     method: "GET",
//   });
// }

// /**
//  * Get backend config/debug information.
//  * FastAPI route:
//  * GET /api/debug/config
//  */
// export async function getRagDebugConfig() {
//   return requestJson("/api/debug/config", {
//     method: "GET",
//   });
// }

// /**
//  * Upload PDF notes and process them.
//  *
//  * FastAPI route:
//  * POST /api/notes/upload
//  *
//  * Expected backend fields:
//  * - files: PDF files
//  * - session_id: optional existing session id
//  */
// export async function uploadNotes({ files, sessionId = "" }) {
//   if (!files || files.length === 0) {
//     throw new Error("Please select at least one PDF file.");
//   }

//   const formData = new FormData();

//   Array.from(files).forEach((file) => {
//     formData.append("files", file);
//   });

//   if (sessionId) {
//     formData.append("session_id", sessionId);
//   }

//   return requestForm("/api/notes/upload", formData);
// }

// /**
//  * Re-process already uploaded PDFs for a session.
//  *
//  * FastAPI route:
//  * POST /api/notes/process
//  */
// export async function processExistingNotes(sessionId) {
//   if (!sessionId) {
//     throw new Error("Session ID is required.");
//   }

//   const formData = new FormData();
//   formData.append("session_id", sessionId);

//   return requestForm("/api/notes/process", formData);
// }

// /**
//  * Ask question from uploaded notes.
//  *
//  * FastAPI route:
//  * POST /api/notes/ask
//  *
//  * Body:
//  * {
//  *   session_id,
//  *   question
//  * }
//  */
// export async function askNotesQuestion({ sessionId, question }) {
//   if (!sessionId) {
//     throw new Error("Session ID is missing. Please upload notes first.");
//   }

//   if (!question || !question.trim()) {
//     throw new Error("Please enter a question.");
//   }

//   return requestJson("/api/notes/ask", {
//     method: "POST",
//     body: JSON.stringify({
//       session_id: sessionId,
//       question: question.trim(),
//     }),
//   });
// }

// /**
//  * Summarize uploaded notes.
//  *
//  * FastAPI route:
//  * POST /api/notes/summarize
//  */
// export async function summarizeNotes(sessionId) {
//   if (!sessionId) {
//     throw new Error("Session ID is missing. Please upload notes first.");
//   }

//   const formData = new FormData();
//   formData.append("session_id", sessionId);

//   return requestForm("/api/notes/summarize", formData);
// }

// /**
//  * Generate viva/interview questions from uploaded notes.
//  *
//  * FastAPI route:
//  * POST /api/notes/questions
//  */
// export async function generateNotesQuestions(sessionId) {
//   if (!sessionId) {
//     throw new Error("Session ID is missing. Please upload notes first.");
//   }

//   const formData = new FormData();
//   formData.append("session_id", sessionId);

//   return requestForm("/api/notes/questions", formData);
// }

// /**
//  * Generate MCQ flashcards from uploaded notes.
//  *
//  * FastAPI route:
//  * POST /api/flashcards/generate
//  *
//  * Body:
//  * {
//  *   session_id
//  * }
//  */
// export async function generateFlashcards(sessionId) {
//   if (!sessionId) {
//     throw new Error("Session ID is missing. Please upload notes first.");
//   }

//   return requestJson("/api/flashcards/generate", {
//     method: "POST",
//     body: JSON.stringify({
//       session_id: sessionId,
//     }),
//   });
// }

// /**
//  * Get current session summary.
//  *
//  * FastAPI route:
//  * GET /api/session/{session_id}/summary
//  */
// export async function getSessionSummary(sessionId) {
//   if (!sessionId) {
//     throw new Error("Session ID is required.");
//   }

//   return requestJson(`/api/session/${sessionId}/summary`, {
//     method: "GET",
//   });
// }

// /**
//  * Clear full session data.
//  *
//  * FastAPI route:
//  * DELETE /api/session/{session_id}/clear
//  */
// export async function clearSessionData(sessionId, fullClear = false) {
//   if (!sessionId) {
//     throw new Error("Session ID is required.");
//   }

//   const query = fullClear ? "?full_clear=true" : "";

//   return requestJson(`/api/session/${sessionId}/clear${query}`, {
//     method: "DELETE",
//   });
// }

// /**
//  * Clear only uploaded files + processed vectors.
//  *
//  * FastAPI route:
//  * DELETE /api/session/{session_id}/uploaded-files
//  */
// export async function clearUploadedFiles(sessionId) {
//   if (!sessionId) {
//     throw new Error("Session ID is required.");
//   }

//   return requestJson(`/api/session/${sessionId}/uploaded-files`, {
//     method: "DELETE",
//   });
// }

// /**
//  * Resume Gap Finder.
//  *
//  * FastAPI route:
//  * POST /api/resume/gap-analysis
//  *
//  * Expected fields:
//  * - resume: uploaded resume file
//  * - job_description: pasted JD text
//  * - session_id: optional
//  */
// export async function analyzeResumeGap({
//   resumeFile,
//   jobDescription,
//   sessionId = "",
// }) {
//   if (!resumeFile) {
//     throw new Error("Please upload your resume.");
//   }

//   if (!jobDescription || !jobDescription.trim()) {
//     throw new Error("Please paste the job description.");
//   }

//   const formData = new FormData();

//   formData.append("resume", resumeFile);
//   formData.append("job_description", jobDescription.trim());

//   if (sessionId) {
//     formData.append("session_id", sessionId);
//   }

//   return requestForm("/api/resume/gap-analysis", formData);
// }

// /**
//  * Debug vector search.
//  *
//  * FastAPI route:
//  * POST /api/debug/search
//  */
// export async function debugVectorSearch({
//   sessionId,
//   query,
//   topK = 5,
// }) {
//   if (!sessionId) {
//     throw new Error("Session ID is required.");
//   }

//   if (!query || !query.trim()) {
//     throw new Error("Search query is required.");
//   }

//   return requestJson("/api/debug/search", {
//     method: "POST",
//     body: JSON.stringify({
//       session_id: sessionId,
//       query: query.trim(),
//       top_k: topK,
//     }),
//   });
// }

// /**
//  * One object export also, so pages can import either way.
//  */
// export const ragApi = {
//   baseUrl: RAG_API_BASE_URL,

//   checkHealth: checkRagBackendHealth,
//   getDebugConfig: getRagDebugConfig,

//   uploadNotes,
//   processExistingNotes,
//   askNotesQuestion,
//   summarizeNotes,
//   generateNotesQuestions,
//   generateFlashcards,

//   getSessionSummary,
//   clearSessionData,
//   clearUploadedFiles,

//   analyzeResumeGap,
//   debugVectorSearch,
// };

// export default ragApi;
const DEFAULT_RAG_API_URL = "http://127.0.0.1:8000";

export const RAG_API_BASE_URL =
  import.meta.env.VITE_RAG_API_URL || DEFAULT_RAG_API_URL;

/**
 * Converts backend/FastAPI error response into readable message.
 */
async function getReadableError(response) {
  try {
    const data = await response.json();

    if (typeof data?.detail === "string") {
      return data.detail;
    }

    if (Array.isArray(data?.detail)) {
      return data.detail
        .map((item) => item?.msg || JSON.stringify(item))
        .join(", ");
    }

    if (typeof data?.message === "string") {
      return data.message;
    }

    if (typeof data?.answer === "string") {
      return data.answer;
    }

    return JSON.stringify(data);
  } catch {
    return `Request failed with status ${response.status}`;
  }
}

/**
 * Normal fetch wrapper for JSON APIs.
 */
async function requestJson(endpoint, options = {}) {
  const url = `${RAG_API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const message = await getReadableError(response);
    throw new Error(message);
  }

  return response.json();
}

/**
 * Fetch wrapper for FormData APIs.
 * Do not manually set Content-Type here.
 * Browser will set multipart/form-data boundary automatically.
 */
async function requestForm(endpoint, formData, options = {}) {
  const url = `${RAG_API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    method: "POST",
    ...options,
    body: formData,
    headers: {
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const message = await getReadableError(response);
    throw new Error(message);
  }

  return response.json();
}

/**
 * Document file validation helper.
 */
function isAllowedDocumentFile(file) {
  if (!file?.name) {
    return false;
  }

  const allowedExtensions = [".pdf", ".docx", ".txt"];
  const fileName = file.name.toLowerCase();

  return allowedExtensions.some((ext) => fileName.endsWith(ext));
}

/**
 * Check if RAG backend is running.
 * FastAPI route:
 * GET /health
 */
export async function checkRagBackendHealth() {
  return requestJson("/health", {
    method: "GET",
  });
}

/**
 * Get backend config/debug information.
 * FastAPI route:
 * GET /api/debug/config
 */
export async function getRagDebugConfig() {
  return requestJson("/api/debug/config", {
    method: "GET",
  });
}

/**
 * Upload PDF notes and process them.
 *
 * FastAPI route:
 * POST /api/notes/upload
 *
 * Expected backend fields:
 * - files: PDF files
 * - session_id: optional existing session id
 */
export async function uploadNotes({ files, sessionId = "" }) {
  if (!files || files.length === 0) {
    throw new Error("Please select at least one PDF file.");
  }

  const formData = new FormData();

  Array.from(files).forEach((file) => {
    formData.append("files", file);
  });

  if (sessionId) {
    formData.append("session_id", sessionId);
  }

  return requestForm("/api/notes/upload", formData);
}

/**
 * Re-process already uploaded PDFs for a session.
 *
 * FastAPI route:
 * POST /api/notes/process
 */
export async function processExistingNotes(sessionId) {
  if (!sessionId) {
    throw new Error("Session ID is required.");
  }

  const formData = new FormData();
  formData.append("session_id", sessionId);

  return requestForm("/api/notes/process", formData);
}

/**
 * Ask question from uploaded notes.
 *
 * FastAPI route:
 * POST /api/notes/ask
 */
export async function askNotesQuestion({ sessionId, question }) {
  if (!sessionId) {
    throw new Error("Session ID is missing. Please upload notes first.");
  }

  if (!question || !question.trim()) {
    throw new Error("Please enter a question.");
  }

  return requestJson("/api/notes/ask", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      question: question.trim(),
    }),
  });
}

/**
 * Summarize uploaded notes.
 *
 * FastAPI route:
 * POST /api/notes/summarize
 */
export async function summarizeNotes(sessionId) {
  if (!sessionId) {
    throw new Error("Session ID is missing. Please upload notes first.");
  }

  const formData = new FormData();
  formData.append("session_id", sessionId);

  return requestForm("/api/notes/summarize", formData);
}

/**
 * Generate viva/interview questions from uploaded notes.
 *
 * FastAPI route:
 * POST /api/notes/questions
 */
export async function generateNotesQuestions(sessionId) {
  if (!sessionId) {
    throw new Error("Session ID is missing. Please upload notes first.");
  }

  const formData = new FormData();
  formData.append("session_id", sessionId);

  return requestForm("/api/notes/questions", formData);
}

/**
 * Generate MCQ flashcards from uploaded notes.
 *
 * FastAPI route:
 * POST /api/flashcards/generate
 */
export async function generateFlashcards(sessionId) {
  if (!sessionId) {
    throw new Error("Session ID is missing. Please upload notes first.");
  }

  return requestJson("/api/flashcards/generate", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
    }),
  });
}

/**
 * Get current session summary.
 *
 * FastAPI route:
 * GET /api/session/{session_id}/summary
 */
export async function getSessionSummary(sessionId) {
  if (!sessionId) {
    throw new Error("Session ID is required.");
  }

  return requestJson(`/api/session/${sessionId}/summary`, {
    method: "GET",
  });
}

/**
 * Clear full session data.
 *
 * FastAPI route:
 * DELETE /api/session/{session_id}/clear
 */
export async function clearSessionData(sessionId, fullClear = false) {
  if (!sessionId) {
    throw new Error("Session ID is required.");
  }

  const query = fullClear ? "?full_clear=true" : "";

  return requestJson(`/api/session/${sessionId}/clear${query}`, {
    method: "DELETE",
  });
}

/**
 * Clear only uploaded files + processed vectors.
 *
 * FastAPI route:
 * DELETE /api/session/{session_id}/uploaded-files
 */
export async function clearUploadedFiles(sessionId) {
  if (!sessionId) {
    throw new Error("Session ID is required.");
  }

  return requestJson(`/api/session/${sessionId}/uploaded-files`, {
    method: "DELETE",
  });
}

/**
 * Resume Gap Finder.
 *
 * FastAPI route:
 * POST /api/resume/gap-analysis
 *
 * Supported frontend inputs:
 * - resumeFile: uploaded resume file
 * - jdFile: optional uploaded JD file PDF/DOCX/TXT
 * - jobDescription: optional pasted JD text
 * - sessionId: optional existing session id
 *
 * Important:
 * User must provide resumeFile.
 * User must provide either jdFile OR pasted jobDescription.
 */
export async function analyzeResumeGap({
  resumeFile,
  jdFile = null,
  jobDescription = "",
  sessionId = "",
}) {
  if (!resumeFile) {
    throw new Error("Please upload your resume.");
  }

  if (!isAllowedDocumentFile(resumeFile)) {
    throw new Error("Resume must be PDF, DOCX, or TXT.");
  }

  if (jdFile && !isAllowedDocumentFile(jdFile)) {
    throw new Error("Job description file must be PDF, DOCX, or TXT.");
  }

  const cleanJobDescription = String(jobDescription || "").trim();

  if (!jdFile && !cleanJobDescription) {
    throw new Error("Please upload JD file or paste the job description.");
  }

  const formData = new FormData();

  formData.append("resume", resumeFile);

  if (jdFile) {
    formData.append("jd_file", jdFile);
  }

  if (cleanJobDescription) {
    formData.append("job_description", cleanJobDescription);
  } else {
    formData.append("job_description", "");
  }

  if (sessionId) {
    formData.append("session_id", sessionId);
  }

  return requestForm("/api/resume/gap-analysis", formData);
}

/**
 * Debug vector search.
 *
 * FastAPI route:
 * POST /api/debug/search
 */
export async function debugVectorSearch({ sessionId, query, topK = 5 }) {
  if (!sessionId) {
    throw new Error("Session ID is required.");
  }

  if (!query || !query.trim()) {
    throw new Error("Search query is required.");
  }

  return requestJson("/api/debug/search", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      query: query.trim(),
      top_k: topK,
    }),
  });
}

/**
 * One object export also, so pages can import either way.
 */
export const ragApi = {
  baseUrl: RAG_API_BASE_URL,

  checkHealth: checkRagBackendHealth,
  getDebugConfig: getRagDebugConfig,

  uploadNotes,
  processExistingNotes,
  askNotesQuestion,
  summarizeNotes,
  generateNotesQuestions,
  generateFlashcards,

  getSessionSummary,
  clearSessionData,
  clearUploadedFiles,

  analyzeResumeGap,
  debugVectorSearch,
};

export default ragApi;