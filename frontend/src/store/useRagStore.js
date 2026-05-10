import { create } from "zustand";

const DEFAULT_RAG_STATE = {
  // Backend status
  backendStatus: "unknown",
  backendError: "",

  // Current RAG notes session
  sessionId: localStorage.getItem("rag_session_id") || "",
  ragReady: false,

  // Uploaded notes info
  uploadedFiles: [],
  savedPaths: [],
  sessionSummary: null,
  pdfSummary: null,
  vectorStatus: null,

  // UI loading states
  uploading: false,
  processing: false,
  asking: false,
  summarizing: false,
  generatingQuestions: false,
  generatingFlashcards: false,
  clearing: false,

  // Chat
  question: "",
  chatMessages: [],

  // Study tools output
  summaryAnswer: "",
  generatedQuestionsAnswer: "",

  // Flashcards
  flashcards: [],
  flashcardsRaw: "",
  flashcardIndex: 0,
  selectedFlashcardOption: "",
  flashcardAnswerChecked: false,

  // Resume Gap Finder
  resumeSessionId: localStorage.getItem("resume_gap_session_id") || "",
  resumeFile: null,
  jobDescription: "",
  resumeLoading: false,
  resumeResult: null,
  resumeError: "",

  // General error/success
  error: "",
  successMessage: "",
};

export const useRagStore = create((set, get) => ({
  ...DEFAULT_RAG_STATE,

  // ---------------------------------------------------------
  // Backend status
  // ---------------------------------------------------------

  setBackendStatus: (backendStatus) => {
    set({ backendStatus });
  },

  setBackendError: (backendError) => {
    set({ backendError });
  },

  // ---------------------------------------------------------
  // Session
  // ---------------------------------------------------------

  setSessionId: (sessionId) => {
    const safeSessionId = sessionId || "";

    if (safeSessionId) {
      localStorage.setItem("rag_session_id", safeSessionId);
    } else {
      localStorage.removeItem("rag_session_id");
    }

    set({ sessionId: safeSessionId });
  },

  setRagReady: (ragReady) => {
    set({ ragReady: Boolean(ragReady) });
  },

  setSessionSummary: (sessionSummary) => {
    set({ sessionSummary });
  },

  setPdfSummary: (pdfSummary) => {
    set({ pdfSummary });
  },

  setVectorStatus: (vectorStatus) => {
    set({
      vectorStatus,
      ragReady: Boolean(vectorStatus?.ready),
    });
  },

  setSessionData: ({
    sessionId,
    sessionSummary,
    pdfSummary,
    vectorStatus,
    ragReady,
  } = {}) => {
    const updates = {};

    if (sessionId !== undefined) {
      updates.sessionId = sessionId || "";

      if (sessionId) {
        localStorage.setItem("rag_session_id", sessionId);
      } else {
        localStorage.removeItem("rag_session_id");
      }
    }

    if (sessionSummary !== undefined) {
      updates.sessionSummary = sessionSummary;
    }

    if (pdfSummary !== undefined) {
      updates.pdfSummary = pdfSummary;
    }

    if (vectorStatus !== undefined) {
      updates.vectorStatus = vectorStatus;
    }

    if (ragReady !== undefined) {
      updates.ragReady = Boolean(ragReady);
    } else if (vectorStatus !== undefined) {
      updates.ragReady = Boolean(vectorStatus?.ready);
    }

    set(updates);
  },

  // ---------------------------------------------------------
  // Uploaded files
  // ---------------------------------------------------------

  setUploadedFiles: (uploadedFiles) => {
    set({
      uploadedFiles: Array.from(uploadedFiles || []),
    });
  },

  setSavedPaths: (savedPaths) => {
    set({
      savedPaths: Array.isArray(savedPaths) ? savedPaths : [],
    });
  },

  clearUploadedFilesState: () => {
    set({
      uploadedFiles: [],
      savedPaths: [],
      sessionSummary: null,
      pdfSummary: null,
      vectorStatus: null,
      ragReady: false,
    });
  },

  // ---------------------------------------------------------
  // Loading states
  // ---------------------------------------------------------

  setUploading: (uploading) => {
    set({ uploading: Boolean(uploading) });
  },

  setProcessing: (processing) => {
    set({ processing: Boolean(processing) });
  },

  setAsking: (asking) => {
    set({ asking: Boolean(asking) });
  },

  setSummarizing: (summarizing) => {
    set({ summarizing: Boolean(summarizing) });
  },

  setGeneratingQuestions: (generatingQuestions) => {
    set({ generatingQuestions: Boolean(generatingQuestions) });
  },

  setGeneratingFlashcards: (generatingFlashcards) => {
    set({ generatingFlashcards: Boolean(generatingFlashcards) });
  },

  setClearing: (clearing) => {
    set({ clearing: Boolean(clearing) });
  },

  // ---------------------------------------------------------
  // Chat
  // ---------------------------------------------------------

  setQuestion: (question) => {
    set({ question });
  },

  setChatMessages: (chatMessages) => {
    set({
      chatMessages: Array.isArray(chatMessages) ? chatMessages : [],
    });
  },

  addChatMessage: (message) => {
    if (!message) return;

    const cleanMessage = {
      role: message.role || "assistant",
      content: String(message.content || ""),
      sources: Array.isArray(message.sources) ? message.sources : [],
      time: message.time || new Date().toISOString(),
    };

    if (!cleanMessage.content.trim()) return;

    set((state) => ({
      chatMessages: [...state.chatMessages, cleanMessage],
    }));
  },

  addUserMessage: (content) => {
    const text = String(content || "").trim();

    if (!text) return;

    get().addChatMessage({
      role: "user",
      content: text,
      sources: [],
    });
  },

  addAssistantMessage: (content, sources = []) => {
    const text = String(content || "").trim();

    if (!text) return;

    get().addChatMessage({
      role: "assistant",
      content: text,
      sources,
    });
  },

  clearChat: () => {
    set({
      question: "",
      chatMessages: [],
    });
  },

  // ---------------------------------------------------------
  // Summary + Questions
  // ---------------------------------------------------------

  setSummaryAnswer: (summaryAnswer) => {
    set({
      summaryAnswer: summaryAnswer || "",
    });
  },

  setGeneratedQuestionsAnswer: (generatedQuestionsAnswer) => {
    set({
      generatedQuestionsAnswer: generatedQuestionsAnswer || "",
    });
  },

  clearStudyToolOutputs: () => {
    set({
      summaryAnswer: "",
      generatedQuestionsAnswer: "",
      flashcards: [],
      flashcardsRaw: "",
      flashcardIndex: 0,
      selectedFlashcardOption: "",
      flashcardAnswerChecked: false,
    });
  },

  // ---------------------------------------------------------
  // Flashcards
  // ---------------------------------------------------------

  setFlashcards: (flashcards, raw = "") => {
    set({
      flashcards: Array.isArray(flashcards) ? flashcards : [],
      flashcardsRaw: raw || "",
      flashcardIndex: 0,
      selectedFlashcardOption: "",
      flashcardAnswerChecked: false,
    });
  },

  setFlashcardsRaw: (flashcardsRaw) => {
    set({
      flashcardsRaw: flashcardsRaw || "",
    });
  },

  setFlashcardIndex: (flashcardIndex) => {
    const cards = get().flashcards || [];
    const maxIndex = Math.max(cards.length - 1, 0);

    const safeIndex = Math.max(0, Math.min(Number(flashcardIndex) || 0, maxIndex));

    set({
      flashcardIndex: safeIndex,
      selectedFlashcardOption: "",
      flashcardAnswerChecked: false,
    });
  },

  nextFlashcard: () => {
    const { flashcardIndex, flashcards } = get();

    if (!flashcards || flashcards.length === 0) return;

    const nextIndex = Math.min(flashcardIndex + 1, flashcards.length - 1);

    set({
      flashcardIndex: nextIndex,
      selectedFlashcardOption: "",
      flashcardAnswerChecked: false,
    });
  },

  previousFlashcard: () => {
    const { flashcardIndex } = get();

    const previousIndex = Math.max(flashcardIndex - 1, 0);

    set({
      flashcardIndex: previousIndex,
      selectedFlashcardOption: "",
      flashcardAnswerChecked: false,
    });
  },

  setSelectedFlashcardOption: (selectedFlashcardOption) => {
    set({
      selectedFlashcardOption: selectedFlashcardOption || "",
    });
  },

  checkFlashcardAnswer: () => {
    set({
      flashcardAnswerChecked: true,
    });
  },

  resetFlashcardAnswer: () => {
    set({
      selectedFlashcardOption: "",
      flashcardAnswerChecked: false,
    });
  },

  clearFlashcards: () => {
    set({
      flashcards: [],
      flashcardsRaw: "",
      flashcardIndex: 0,
      selectedFlashcardOption: "",
      flashcardAnswerChecked: false,
    });
  },

  // ---------------------------------------------------------
  // Resume Gap Finder
  // ---------------------------------------------------------

  setResumeSessionId: (resumeSessionId) => {
    const safeSessionId = resumeSessionId || "";

    if (safeSessionId) {
      localStorage.setItem("resume_gap_session_id", safeSessionId);
    } else {
      localStorage.removeItem("resume_gap_session_id");
    }

    set({ resumeSessionId: safeSessionId });
  },

  setResumeFile: (resumeFile) => {
    set({ resumeFile });
  },

  setJobDescription: (jobDescription) => {
    set({ jobDescription });
  },

  setResumeLoading: (resumeLoading) => {
    set({ resumeLoading: Boolean(resumeLoading) });
  },

  setResumeResult: (resumeResult) => {
    set({
      resumeResult,
      resumeError: "",
    });
  },

  setResumeError: (resumeError) => {
    set({
      resumeError: resumeError || "",
    });
  },

  clearResumeGapState: () => {
    localStorage.removeItem("resume_gap_session_id");

    set({
      resumeSessionId: "",
      resumeFile: null,
      jobDescription: "",
      resumeLoading: false,
      resumeResult: null,
      resumeError: "",
    });
  },

  // ---------------------------------------------------------
  // Error / success
  // ---------------------------------------------------------

  setError: (error) => {
    set({
      error: error || "",
    });
  },

  clearError: () => {
    set({
      error: "",
    });
  },

  setSuccessMessage: (successMessage) => {
    set({
      successMessage: successMessage || "",
    });
  },

  clearSuccessMessage: () => {
    set({
      successMessage: "",
    });
  },

  clearAlerts: () => {
    set({
      error: "",
      successMessage: "",
      backendError: "",
      resumeError: "",
    });
  },

  // ---------------------------------------------------------
  // Full resets
  // ---------------------------------------------------------

  resetNotesState: () => {
    localStorage.removeItem("rag_session_id");

    set({
      sessionId: "",
      ragReady: false,
      uploadedFiles: [],
      savedPaths: [],
      sessionSummary: null,
      pdfSummary: null,
      vectorStatus: null,

      uploading: false,
      processing: false,
      asking: false,
      summarizing: false,
      generatingQuestions: false,
      generatingFlashcards: false,
      clearing: false,

      question: "",
      chatMessages: [],

      summaryAnswer: "",
      generatedQuestionsAnswer: "",

      flashcards: [],
      flashcardsRaw: "",
      flashcardIndex: 0,
      selectedFlashcardOption: "",
      flashcardAnswerChecked: false,

      error: "",
      successMessage: "",
    });
  },

  resetAllRagState: () => {
    localStorage.removeItem("rag_session_id");
    localStorage.removeItem("resume_gap_session_id");

    set({
      ...DEFAULT_RAG_STATE,
      sessionId: "",
      resumeSessionId: "",
    });
  },
}));