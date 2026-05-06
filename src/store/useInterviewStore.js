import { create } from "zustand";

const DEFAULT_INTERVIEW_STATE = {
  track: null,
  difficulty: "Fresher",

  jobDescription: "",
  resumeFileName: null,
  resumeText: "",

  interviewTitle: "",
  interviewRole: "",
  interviewCompany: "",
  interviewType: "Voice",
  questionCount: 15,

  createdInterviewId: null,
};

const createSafeId = () => {
  if (
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
  ) {
    return crypto.randomUUID();
  }

  return `interview_${Date.now()}_${Math.random()
    .toString(36)
    .slice(2, 10)}`;
};

const normalizeQuestionCount = (value) => {
  const numberValue = Number(value);

  if (!Number.isFinite(numberValue)) {
    return 15;
  }

  if (numberValue < 1) {
    return 1;
  }

  if (numberValue > 30) {
    return 30;
  }

  return Math.round(numberValue);
};

export const useInterviewStore = create((set, get) => ({
  ...DEFAULT_INTERVIEW_STATE,

  setTrack: (track) => {
    set({ track });
  },

  setDifficulty: (difficulty) => {
    set({ difficulty });
  },

  setJobDescription: (jobDescription) => {
    set({ jobDescription });
  },

  setResumeFileName: (resumeFileName) => {
    set({ resumeFileName });
  },

  setResumeText: (resumeText) => {
    set({ resumeText });
  },

  setInterviewTitle: (interviewTitle) => {
    set({ interviewTitle });
  },

  setInterviewRole: (interviewRole) => {
    set({ interviewRole });
  },

  setInterviewCompany: (interviewCompany) => {
    set({ interviewCompany });
  },

  setInterviewType: (interviewType) => {
    set({ interviewType });
  },

  setQuestionCount: (questionCount) => {
    set({
      questionCount: normalizeQuestionCount(questionCount),
    });
  },

  setCreatedInterviewId: (createdInterviewId) => {
    set({ createdInterviewId });
  },

  setFullInterviewSetup: (setupData = {}) => {
    set({
      track: setupData.track ?? get().track,
      difficulty: setupData.difficulty ?? get().difficulty,

      jobDescription: setupData.jobDescription ?? get().jobDescription,
      resumeFileName: setupData.resumeFileName ?? get().resumeFileName,
      resumeText: setupData.resumeText ?? get().resumeText,

      interviewTitle: setupData.interviewTitle ?? get().interviewTitle,
      interviewRole: setupData.interviewRole ?? get().interviewRole,
      interviewCompany: setupData.interviewCompany ?? get().interviewCompany,
      interviewType: setupData.interviewType ?? get().interviewType,
      questionCount:
        setupData.questionCount !== undefined
          ? normalizeQuestionCount(setupData.questionCount)
          : get().questionCount,
    });
  },

  createInterviewFromSetup: () => {
    const state = get();

    const safeTrack = state.track || "General";
    const safeDifficulty = state.difficulty || "Fresher";
    const safeRole = state.interviewRole || safeTrack;
    const safeQuestionCount = normalizeQuestionCount(state.questionCount);

    const generatedTitle = [safeRole, safeDifficulty, "Interview"]
      .filter(Boolean)
      .join(" ");

    const interviewData = {
      id: createSafeId(),
      title: state.interviewTitle || generatedTitle,
      role: safeRole,
      company: state.interviewCompany || "",
      track: safeTrack,
      difficulty: safeDifficulty,
      type: state.interviewType || "Voice",
      questionCount: safeQuestionCount,
      jobDescription: state.jobDescription || "",
      resumeFileName: state.resumeFileName || null,
      resumeText: state.resumeText || "",
      createdAt: new Date().toISOString(),
    };

    set({
      createdInterviewId: interviewData.id,
      interviewTitle: interviewData.title,
      interviewRole: interviewData.role,
      interviewCompany: interviewData.company,
      track: interviewData.track,
      difficulty: interviewData.difficulty,
      interviewType: interviewData.type,
      questionCount: interviewData.questionCount,
      jobDescription: interviewData.jobDescription,
      resumeFileName: interviewData.resumeFileName,
      resumeText: interviewData.resumeText,
    });

    return interviewData;
  },

  clearResume: () => {
    set({
      resumeFileName: null,
      resumeText: "",
    });
  },

  reset: () => {
    set({
      ...DEFAULT_INTERVIEW_STATE,
    });
  },
}));