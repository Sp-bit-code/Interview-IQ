import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { vapi } from "../lib/vapi";

const CALL_STATUS = {
  INACTIVE: "INACTIVE",
  CONNECTING: "CONNECTING",
  ACTIVE: "ACTIVE",
  FINISHED: "FINISHED",
  ERROR: "ERROR",
};

export function useVapiInterview({
  userName = "Candidate",
  track = "General",
  difficulty = "Fresher",
  jobDescription = "",
  resumeText = "",

  interviewTitle = "",
  interviewRole = "",
  interviewCompany = "",
  interviewType = "Voice",
  questionCount = 15,

  onCallFinished,
} = {}) {
  const [callStatus, setCallStatus] = useState(CALL_STATUS.INACTIVE);
  const [messages, setMessages] = useState([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [error, setError] = useState(null);

  const messagesRef = useRef([]);
  const callEndedRef = useRef(false);
  const callStartedRef = useRef(false);

  const assistantId = import.meta.env.VITE_VAPI_ASSISTANT_ID;

  const publicKey =
    import.meta.env.VITE_VAPI_PUBLIC_KEY ||
    import.meta.env.VITE_VAPI_WEB_TOKEN ||
    "";

  const safeInterviewTitle = interviewTitle || `${track || "General"} Interview`;
  const safeInterviewRole = interviewRole || track || "General";
  const safeInterviewCompany = interviewCompany || "Not specified";
  const safeInterviewType = interviewType || "Voice";
  const safeQuestionCount = Number(questionCount) || 15;

  const lastMessage = useMemo(() => {
    if (messages.length === 0) {
      return "";
    }

    return messages[messages.length - 1]?.content || "";
  }, [messages]);

  const getErrorText = useCallback((err) => {
    if (!err) {
      return "Unknown error occurred.";
    }

    if (typeof err === "string") {
      return err;
    }

    if (err?.message && typeof err.message === "string") {
      return err.message;
    }

    if (err?.errorMsg && typeof err.errorMsg === "string") {
      return err.errorMsg;
    }

    if (err?.error && typeof err.error === "string") {
      return err.error;
    }

    if (err?.error?.message && typeof err.error.message === "string") {
      return err.error.message;
    }

    try {
      return JSON.stringify(err);
    } catch {
      return "Vapi call failed. Please check your Vapi setup.";
    }
  }, []);

  const normalizeRole = useCallback((role) => {
    if (role === "user") {
      return "user";
    }

    if (role === "assistant") {
      return "assistant";
    }

    if (role === "bot") {
      return "assistant";
    }

    if (role === "system") {
      return "system";
    }

    return "assistant";
  }, []);

  const addMessage = useCallback(
    (newMessage) => {
      if (!newMessage?.content) {
        return;
      }

      const cleanMessage = {
        role: normalizeRole(newMessage.role),
        content: String(newMessage.content).trim(),
        time: newMessage.time || new Date().toISOString(),
      };

      if (!cleanMessage.content) {
        return;
      }

      const previousMessage =
        messagesRef.current[messagesRef.current.length - 1];

      const isDuplicate =
        previousMessage &&
        previousMessage.role === cleanMessage.role &&
        previousMessage.content === cleanMessage.content;

      if (isDuplicate) {
        return;
      }

      messagesRef.current = [...messagesRef.current, cleanMessage];
      setMessages(messagesRef.current);
    },
    [normalizeRole]
  );

  const finishCallSafely = useCallback(() => {
    if (callEndedRef.current) {
      return;
    }

    callEndedRef.current = true;
    callStartedRef.current = false;

    setIsSpeaking(false);
    setIsMuted(false);
    setCallStatus(CALL_STATUS.FINISHED);

    if (typeof onCallFinished === "function") {
      onCallFinished(messagesRef.current);
    }
  }, [onCallFinished]);

  useEffect(() => {
    if (!vapi) {
      setError(
        "Vapi client is not initialized. Check VITE_VAPI_PUBLIC_KEY in .env.local and restart npm run dev."
      );
      return;
    }

    const handleCallStart = () => {
      console.log("Vapi call started");

      callStartedRef.current = true;
      callEndedRef.current = false;

      setCallStatus(CALL_STATUS.ACTIVE);
      setError(null);
    };

    const handleCallEnd = () => {
      console.log("Vapi call ended");
      finishCallSafely();
    };

    const handleMessage = (message) => {
      console.log("Vapi message:", message);

      if (
        message?.type === "transcript" &&
        message?.transcriptType === "final" &&
        message?.transcript
      ) {
        addMessage({
          role: message.role || "assistant",
          content: message.transcript,
          time: new Date().toISOString(),
        });

        return;
      }

      if (
        message?.type === "conversation-update" &&
        Array.isArray(message?.conversation)
      ) {
        const finalConversationMessages = message.conversation
          .filter((item) => item?.content || item?.message)
          .map((item) => ({
            role: normalizeRole(item.role || "assistant"),
            content: String(item.content || item.message || "").trim(),
            time: new Date().toISOString(),
          }))
          .filter((item) => item.content);

        messagesRef.current = finalConversationMessages;
        setMessages(finalConversationMessages);

        return;
      }

      if (message?.type === "function-call" || message?.type === "tool-calls") {
        console.log("Vapi function/tool call:", message);
      }
    };

    const handleSpeechStart = () => {
      console.log("Vapi speech started");
      setIsSpeaking(true);
    };

    const handleSpeechEnd = () => {
      console.log("Vapi speech ended");
      setIsSpeaking(false);
    };

    const handleError = (err) => {
      console.error("Vapi error:", err);

      const errorMessage = getErrorText(err);

      setError(errorMessage);
      setIsSpeaking(false);
      setIsMuted(false);
      setCallStatus(CALL_STATUS.ERROR);
    };

    vapi.on("call-start", handleCallStart);
    vapi.on("call-end", handleCallEnd);
    vapi.on("message", handleMessage);
    vapi.on("speech-start", handleSpeechStart);
    vapi.on("speech-end", handleSpeechEnd);
    vapi.on("error", handleError);

    return () => {
      if (!vapi) {
        return;
      }

      vapi.off("call-start", handleCallStart);
      vapi.off("call-end", handleCallEnd);
      vapi.off("message", handleMessage);
      vapi.off("speech-start", handleSpeechStart);
      vapi.off("speech-end", handleSpeechEnd);
      vapi.off("error", handleError);
    };
  }, [addMessage, finishCallSafely, normalizeRole, getErrorText]);

  const startCall = useCallback(async () => {
    try {
      if (!publicKey || publicKey.includes("your_")) {
        throw new Error(
          "VITE_VAPI_PUBLIC_KEY is missing or still placeholder in .env.local"
        );
      }

      if (!assistantId || assistantId.includes("your_")) {
        throw new Error(
          "VITE_VAPI_ASSISTANT_ID is missing or still placeholder in .env.local"
        );
      }

      if (!vapi) {
        throw new Error(
          "Vapi client is not initialized. Check VITE_VAPI_PUBLIC_KEY and restart npm run dev."
        );
      }

      setError(null);
      setMessages([]);
      setIsSpeaking(false);
      setIsMuted(false);

      messagesRef.current = [];
      callEndedRef.current = false;
      callStartedRef.current = false;

      setCallStatus(CALL_STATUS.CONNECTING);

      const shortJobDescription = jobDescription
        ? jobDescription.slice(0, 2500)
        : "";

      const shortResumeText = resumeText ? resumeText.slice(0, 3500) : "";

      await vapi.start(assistantId, {
        variableValues: {
          candidateName: userName || "Candidate",
          interviewTitle: safeInterviewTitle,
          interviewRole: safeInterviewRole,
          interviewCompany: safeInterviewCompany,
          interviewType: safeInterviewType,
          track: track || "General",
          difficulty: difficulty || "Fresher",
          questionCount: String(safeQuestionCount),
          jobDescription: shortJobDescription,
          resumeText: shortResumeText,
        },
      });
    } catch (err) {
      console.error("Failed to start Vapi call:", err);

      setError(getErrorText(err));
      setIsSpeaking(false);
      setIsMuted(false);
      setCallStatus(CALL_STATUS.ERROR);
    }
  }, [
    publicKey,
    assistantId,
    userName,
    safeInterviewTitle,
    safeInterviewRole,
    safeInterviewCompany,
    safeInterviewType,
    track,
    difficulty,
    safeQuestionCount,
    jobDescription,
    resumeText,
    getErrorText,
  ]);

  const endCall = useCallback(() => {
    try {
      if (vapi) {
        vapi.stop();
      }
    } catch (err) {
      console.error("Failed to stop Vapi call:", err);
      setError(getErrorText(err));
    }

    finishCallSafely();
  }, [finishCallSafely, getErrorText]);

  const toggleMute = useCallback(() => {
    try {
      if (!vapi) {
        throw new Error("Vapi client not initialized.");
      }

      const nextMuted = !isMuted;

      if (typeof vapi.setMuted === "function") {
        vapi.setMuted(nextMuted);
      } else {
        console.warn("vapi.setMuted is not available in this SDK version.");
      }

      setIsMuted(nextMuted);
    } catch (err) {
      console.error("Mute toggle failed:", err);
      setError(getErrorText(err));
    }
  }, [isMuted, getErrorText]);

  return {
    CALL_STATUS,
    callStatus,
    messages,
    lastMessage,
    isSpeaking,
    isMuted,
    error,
    startCall,
    endCall,
    toggleMute,
  };
}