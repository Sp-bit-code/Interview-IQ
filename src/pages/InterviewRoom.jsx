import React, { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router";
import {
  Bot,
  User,
  Phone,
  PhoneOff,
  Mic,
  MicOff,
  Loader2,
  MessageSquare,
  ArrowLeft,
  FileText,
  Briefcase,
  Volume2,
  AlertCircle,
  LayoutDashboard,
  RotateCcw,
  Building2,
  Hash,
} from "lucide-react";

import { useInterviewStore } from "../store/useInterviewStore";
import { useAuthStore } from "../store/useAuthStore";
import { supabase } from "../lib/supabase";
import { useVapiInterview } from "../hooks/useVapiInterview";

import "./InterviewRoom.css";

export default function InterviewRoom() {
  const navigate = useNavigate();

  const { user } = useAuthStore();

  const {
    track,
    difficulty,
    jobDescription,
    resumeFileName,
    resumeText,
    interviewTitle,
    interviewRole,
    interviewCompany,
    questionCount,
    createdInterviewId,
  } = useInterviewStore();

  const [sessionSaved, setSessionSaved] = useState(false);
  const [savingSession, setSavingSession] = useState(false);
  const [saveError, setSaveError] = useState("");

  const sessionSavedRef = useRef(false);
  const callStartTimeRef = useRef(null);

  const candidateName = useMemo(() => {
    if (user?.email) {
      return user.email.split("@")[0];
    }

    return "Guest";
  }, [user]);

  const safeTrack = useMemo(() => {
    return track || "General";
  }, [track]);

  const safeDifficulty = useMemo(() => {
    return difficulty || "Fresher";
  }, [difficulty]);

  const safeInterviewTitle = useMemo(() => {
    return interviewTitle || `${safeTrack} Interview`;
  }, [interviewTitle, safeTrack]);

  const safeInterviewRole = useMemo(() => {
    return interviewRole || safeTrack;
  }, [interviewRole, safeTrack]);

  const safeQuestionCount = useMemo(() => {
    return Number(questionCount) || 15;
  }, [questionCount]);

  const hasJobDescription = useMemo(() => {
    return Boolean(jobDescription && jobDescription.trim().length > 0);
  }, [jobDescription]);

  const hasResumeText = useMemo(() => {
    return Boolean(resumeText && resumeText.trim().length > 0);
  }, [resumeText]);

  const calculateEstimatedScore = (finalMessages) => {
    const safeMessages = Array.isArray(finalMessages) ? finalMessages : [];

    const totalMessages = safeMessages.length;

    const userMessages = safeMessages.filter((msg) => msg.role === "user");

    if (totalMessages >= 12 && userMessages.length >= 5) {
      return 8.0;
    }

    if (totalMessages >= 8 && userMessages.length >= 3) {
      return 7.5;
    }

    if (totalMessages >= 4 && userMessages.length >= 2) {
      return 6.5;
    }

    if (totalMessages >= 2) {
      return 5.5;
    }

    return 5.0;
  };

  const buildTranscriptText = (finalMessages) => {
    if (!Array.isArray(finalMessages) || finalMessages.length === 0) {
      return "";
    }

    return finalMessages
      .map((msg) => {
        const roleLabel =
          msg.role === "user"
            ? "Candidate"
            : msg.role === "assistant"
            ? "AI Interviewer"
            : msg.role || "System";

        return `${roleLabel}: ${msg.content}`;
      })
      .join("\n");
  };

  const handleCallFinished = async (finalMessages = []) => {
    if (sessionSavedRef.current) {
      return;
    }

    sessionSavedRef.current = true;
    setSessionSaved(true);
    setSavingSession(true);
    setSaveError("");

    try {
      if (!user) {
        console.log("Guest session ended. Not saving to Supabase.");
        return;
      }

      const safeMessages = Array.isArray(finalMessages) ? finalMessages : [];

      const userMessages = safeMessages.filter((msg) => msg.role === "user");

      const assistantMessages = safeMessages.filter(
        (msg) => msg.role === "assistant"
      );

      const transcriptText = buildTranscriptText(safeMessages);

      const estimatedScore = calculateEstimatedScore(safeMessages);

      const startedAt = callStartTimeRef.current;

      const durationSeconds = startedAt
        ? Math.max(0, Math.round((Date.now() - startedAt) / 1000))
        : 0;

      const reportJson = {
        overallSummary:
          "Vapi voice interview completed successfully. Full AI scoring/report generation can be added next from transcript analysis.",
        transcript: safeMessages,
        transcriptText,
        totalMessages: safeMessages.length,
        userAnswers: userMessages.length,
        aiQuestions: assistantMessages.length,
        durationSeconds,
        setup: {
          interviewId: createdInterviewId || null,
          interviewTitle: safeInterviewTitle,
          role: safeInterviewRole,
          company: interviewCompany || null,
          track: safeTrack,
          difficulty: safeDifficulty,
          questionCount: safeQuestionCount,
          resumeFileName: resumeFileName || null,
          hasJobDescription,
          hasResumeText,
        },
      };

      const { error } = await supabase.from("session_scores").insert({
        user_id: user.id,
        track: safeTrack,
        difficulty: safeDifficulty,
        score_overall: estimatedScore,
        score_communication: estimatedScore,
        score_confidence: estimatedScore,
        score_body_language: 7,
        score_eye_contact: 7,
        score_speaking_pace: 7,
        duration_seconds: durationSeconds,
        report_json: reportJson,
      });

      if (error) {
        throw error;
      }

      console.log("Vapi session saved to Supabase.");
    } catch (err) {
      console.error("Failed to save Vapi session:", err);
      setSaveError(err?.message || "Failed to save interview session.");
    } finally {
      setSavingSession(false);
    }
  };

  const {
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
  } = useVapiInterview({
    userName: candidateName,
    track: safeTrack,
    difficulty: safeDifficulty,
    jobDescription,
    resumeText,
    interviewTitle: safeInterviewTitle,
    interviewRole: safeInterviewRole,
    interviewCompany,
    questionCount: safeQuestionCount,
    onCallFinished: handleCallFinished,
  });

  useEffect(() => {
    if (!track) {
      console.warn("No interview setup found. Using default General interview.");
    }
  }, [track]);

  useEffect(() => {
    if (callStatus === CALL_STATUS.ACTIVE && !callStartTimeRef.current) {
      callStartTimeRef.current = Date.now();
    }
  }, [callStatus, CALL_STATUS.ACTIVE]);

  const isConnecting = callStatus === CALL_STATUS.CONNECTING;
  const isActive = callStatus === CALL_STATUS.ACTIVE;
  const isFinished = callStatus === CALL_STATUS.FINISHED;
  const isError = callStatus === CALL_STATUS.ERROR;
  const isInactive = callStatus === CALL_STATUS.INACTIVE;

  const handleStartCall = async () => {
    setSaveError("");
    setSessionSaved(false);

    sessionSavedRef.current = false;
    callStartTimeRef.current = Date.now();

    await startCall();
  };

  const handleEndCall = () => {
    endCall();
  };

  const handleBackToSetup = () => {
    if (isActive || isConnecting) {
      const confirmLeave = window.confirm(
        "Your interview call is still active. Do you want to end it and go back to setup?"
      );

      if (!confirmLeave) {
        return;
      }

      endCall();
    }

    navigate("/setup");
  };

  const handleDashboardClick = () => {
    if (!user) {
      navigate("/login");
      return;
    }

    navigate("/dashboard");
  };

  const handleNewInterview = () => {
    if (isActive || isConnecting) {
      const confirmRestart = window.confirm(
        "Your current interview call is active. Do you want to end it and create a new interview?"
      );

      if (!confirmRestart) {
        return;
      }

      endCall();
    }

    navigate("/setup");
  };

  return (
    <div className="interview-room-page">
      <div className="interview-room-bg interview-room-bg-one"></div>
      <div className="interview-room-bg interview-room-bg-two"></div>

      <header className="interview-room-header">
        <button
          type="button"
          onClick={handleBackToSetup}
          className="interview-room-back-btn"
        >
          <ArrowLeft size={18} />
          <span>Setup</span>
        </button>

        <div className="interview-room-title-box">
          <h1>AI Voice Interview</h1>
          <p>Powered by Vapi</p>
        </div>

        <button
          type="button"
          onClick={handleDashboardClick}
          className="interview-room-dashboard-btn"
        >
          <LayoutDashboard size={17} />
          <span>{user ? "Dashboard" : "Login"}</span>
        </button>
      </header>

      <main className="interview-room-main">
        <section className="interview-room-left">
          <div className="interview-room-info-card">
            <div className="interview-room-info-top">
              <div>
                <h2>{safeInterviewTitle}</h2>
                <p>
                  {safeDifficulty} level practice session for {safeInterviewRole}
                </p>
              </div>

              <div
                className={`interview-room-status interview-room-status-${String(
                  callStatus
                ).toLowerCase()}`}
              >
                {isConnecting && <Loader2 size={15} className="spin" />}
                {isActive && <Volume2 size={15} />}
                {isFinished && <PhoneOff size={15} />}
                {isError && <AlertCircle size={15} />}
                {isInactive && <Phone size={15} />}

                <span>{callStatus}</span>
              </div>
            </div>

            <div className="interview-room-meta-grid">
              <MetaItem
                icon={<Briefcase size={18} />}
                label="Track"
                value={safeTrack}
              />

              <MetaItem
                icon={<User size={18} />}
                label="Role"
                value={safeInterviewRole}
              />

              <MetaItem
                icon={<Building2 size={18} />}
                label="Company"
                value={interviewCompany || "Not added"}
              />

              <MetaItem
                icon={<Hash size={18} />}
                label="Questions"
                value={`${safeQuestionCount}`}
              />

              <MetaItem
                icon={<FileText size={18} />}
                label="Resume"
                value={resumeFileName || "Not uploaded"}
              />

              <MetaItem
                icon={<MessageSquare size={18} />}
                label="JD"
                value={hasJobDescription ? "Added" : "Not added"}
              />
            </div>
          </div>

          <div className="interview-room-call-view">
            <div className="interview-person-card ai-card">
              <div className="interview-avatar ai-avatar">
                <Bot size={48} />
                {isSpeaking && <span className="speaking-ring"></span>}
              </div>

              <h3>AI Interviewer</h3>

              <p>
                {isSpeaking
                  ? "Speaking..."
                  : isActive
                  ? "Listening and ready"
                  : "Ready to ask questions"}
              </p>
            </div>

            <div className="interview-person-card user-card">
              <div className="interview-avatar user-avatar">
                <User size={48} />
              </div>

              <h3>{candidateName}</h3>

              <p>
                {isActive
                  ? isMuted
                    ? "Microphone muted"
                    : "Microphone ready"
                  : "Waiting to start"}
              </p>
            </div>
          </div>

          <div className="interview-room-controls">
            {!isActive ? (
              <button
                type="button"
                onClick={handleStartCall}
                disabled={isConnecting}
                className="interview-call-btn"
              >
                {isConnecting ? (
                  <>
                    <Loader2 size={20} className="spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <Phone size={20} />
                    Start Vapi Interview
                  </>
                )}
              </button>
            ) : (
              <button
                type="button"
                onClick={handleEndCall}
                className="interview-end-btn"
              >
                <PhoneOff size={20} />
                End Interview
              </button>
            )}

            <button
              type="button"
              onClick={toggleMute}
              disabled={!isActive}
              className={`interview-mute-btn ${isMuted ? "muted" : ""}`}
            >
              {isMuted ? <MicOff size={20} /> : <Mic size={20} />}
              {isMuted ? "Unmute" : "Mute"}
            </button>

            <button
              type="button"
              onClick={handleNewInterview}
              className="interview-new-btn"
            >
              <RotateCcw size={18} />
              New Setup
            </button>
          </div>

          {error && <div className="interview-error-box">{error}</div>}

          {saveError && <div className="interview-error-box">{saveError}</div>}

          {savingSession && (
            <div className="interview-saving-box">
              <Loader2 size={18} className="spin" />
              <span>Saving your interview session...</span>
            </div>
          )}

          {isFinished && (
            <div className="interview-finished-box">
              <h3>Interview ended</h3>

              <p>
                Your transcript is shown on the right. Logged-in users will see
                this session in dashboard history.
              </p>

              <div className="interview-finished-actions">
                <button type="button" onClick={handleDashboardClick}>
                  {user ? "Go to Dashboard" : "Login to Save History"}
                </button>

                <button type="button" onClick={handleNewInterview}>
                  New Interview
                </button>
              </div>
            </div>
          )}

          {sessionSaved && user && !savingSession && !saveError && (
            <div className="interview-saving-box interview-save-success-box">
              <span>✓ Interview session saved successfully.</span>
            </div>
          )}
        </section>

        <section className="interview-room-right">
          <div className="interview-transcript-card">
            <div className="interview-transcript-header">
              <div>
                <h2>Live Transcript</h2>
                <p>{messages.length} messages captured</p>
              </div>
            </div>

            {messages.length === 0 ? (
              <div className="interview-empty-transcript">
                <MessageSquare size={34} />

                <h3>No transcript yet</h3>

                <p>
                  Start the Vapi interview. Final transcripts will appear here
                  after each spoken message.
                </p>
              </div>
            ) : (
              <div className="interview-transcript-list">
                {messages.map((message, index) => (
                  <TranscriptBubble
                    key={`${message.role}-${index}`}
                    role={message.role}
                    content={message.content}
                  />
                ))}
              </div>
            )}
          </div>

          {lastMessage && (
            <div className="interview-last-message-card">
              <span>Latest message</span>
              <p>{lastMessage}</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

function MetaItem({ icon, label, value }) {
  return (
    <div className="interview-meta-item">
      <div className="interview-meta-icon">{icon}</div>

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

function TranscriptBubble({ role, content }) {
  const isUser = role === "user";
  const isAssistant = role === "assistant";

  return (
    <div
      className={`interview-transcript-bubble ${
        isUser
          ? "user-message"
          : isAssistant
          ? "assistant-message"
          : "system-message"
      }`}
    >
      <span>
        {isUser
          ? "You"
          : isAssistant
          ? "AI Interviewer"
          : role || "System"}
      </span>

      <p>{content}</p>
    </div>
  );
}