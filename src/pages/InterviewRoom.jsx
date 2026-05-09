// import React, { useEffect, useMemo, useRef, useState } from "react";
// import { useNavigate } from "react-router";
// import {
//   Bot,
//   User,
//   Phone,
//   PhoneOff,
//   Mic,
//   MicOff,
//   Loader2,
//   MessageSquare,
//   ArrowLeft,
//   FileText,
//   Briefcase,
//   Volume2,
//   AlertCircle,
//   LayoutDashboard,
//   RotateCcw,
//   Building2,
//   Hash,
// } from "lucide-react";

// import { useInterviewStore } from "../store/useInterviewStore";
// import { useAuthStore } from "../store/useAuthStore";
// import { supabase } from "../lib/supabase";
// import { useVapiInterview } from "../hooks/useVapiInterview";

// import "./InterviewRoom.css";

// export default function InterviewRoom() {
//   const navigate = useNavigate();

//   const { user } = useAuthStore();

//   const {
//     track,
//     difficulty,
//     jobDescription,
//     resumeFileName,
//     resumeText,
//     interviewTitle,
//     interviewRole,
//     interviewCompany,
//     questionCount,
//     createdInterviewId,
//   } = useInterviewStore();

//   const [sessionSaved, setSessionSaved] = useState(false);
//   const [savingSession, setSavingSession] = useState(false);
//   const [saveError, setSaveError] = useState("");

//   const sessionSavedRef = useRef(false);
//   const callStartTimeRef = useRef(null);

//   const candidateName = useMemo(() => {
//     if (user?.email) {
//       return user.email.split("@")[0];
//     }

//     return "Guest";
//   }, [user]);

//   const safeTrack = useMemo(() => {
//     return track || "General";
//   }, [track]);

//   const safeDifficulty = useMemo(() => {
//     return difficulty || "Fresher";
//   }, [difficulty]);

//   const safeInterviewTitle = useMemo(() => {
//     return interviewTitle || `${safeTrack} Interview`;
//   }, [interviewTitle, safeTrack]);

//   const safeInterviewRole = useMemo(() => {
//     return interviewRole || safeTrack;
//   }, [interviewRole, safeTrack]);

//   const safeQuestionCount = useMemo(() => {
//     return Number(questionCount) || 15;
//   }, [questionCount]);

//   const hasJobDescription = useMemo(() => {
//     return Boolean(jobDescription && jobDescription.trim().length > 0);
//   }, [jobDescription]);

//   const hasResumeText = useMemo(() => {
//     return Boolean(resumeText && resumeText.trim().length > 0);
//   }, [resumeText]);

//   const calculateEstimatedScore = (finalMessages) => {
//     const safeMessages = Array.isArray(finalMessages) ? finalMessages : [];

//     const totalMessages = safeMessages.length;

//     const userMessages = safeMessages.filter((msg) => msg.role === "user");

//     if (totalMessages >= 12 && userMessages.length >= 5) {
//       return 8.0;
//     }

//     if (totalMessages >= 8 && userMessages.length >= 3) {
//       return 7.5;
//     }

//     if (totalMessages >= 4 && userMessages.length >= 2) {
//       return 6.5;
//     }

//     if (totalMessages >= 2) {
//       return 5.5;
//     }

//     return 5.0;
//   };

//   const buildTranscriptText = (finalMessages) => {
//     if (!Array.isArray(finalMessages) || finalMessages.length === 0) {
//       return "";
//     }

//     return finalMessages
//       .map((msg) => {
//         const roleLabel =
//           msg.role === "user"
//             ? "Candidate"
//             : msg.role === "assistant"
//             ? "AI Interviewer"
//             : msg.role || "System";

//         return `${roleLabel}: ${msg.content}`;
//       })
//       .join("\n");
//   };

//   const handleCallFinished = async (finalMessages = []) => {
//     if (sessionSavedRef.current) {
//       return;
//     }

//     sessionSavedRef.current = true;
//     setSessionSaved(true);
//     setSavingSession(true);
//     setSaveError("");

//     try {
//       if (!user) {
//         console.log("Guest session ended. Not saving to Supabase.");
//         return;
//       }

//       const safeMessages = Array.isArray(finalMessages) ? finalMessages : [];

//       const userMessages = safeMessages.filter((msg) => msg.role === "user");

//       const assistantMessages = safeMessages.filter(
//         (msg) => msg.role === "assistant"
//       );

//       const transcriptText = buildTranscriptText(safeMessages);

//       const estimatedScore = calculateEstimatedScore(safeMessages);

//       const startedAt = callStartTimeRef.current;

//       const durationSeconds = startedAt
//         ? Math.max(0, Math.round((Date.now() - startedAt) / 1000))
//         : 0;

//       const reportJson = {
//         overallSummary:
//           "Vapi voice interview completed successfully. Full AI scoring/report generation can be added next from transcript analysis.",
//         transcript: safeMessages,
//         transcriptText,
//         totalMessages: safeMessages.length,
//         userAnswers: userMessages.length,
//         aiQuestions: assistantMessages.length,
//         durationSeconds,
//         setup: {
//           interviewId: createdInterviewId || null,
//           interviewTitle: safeInterviewTitle,
//           role: safeInterviewRole,
//           company: interviewCompany || null,
//           track: safeTrack,
//           difficulty: safeDifficulty,
//           questionCount: safeQuestionCount,
//           resumeFileName: resumeFileName || null,
//           hasJobDescription,
//           hasResumeText,
//         },
//       };

//       const { error } = await supabase.from("session_scores").insert({
//         user_id: user.id,
//         track: safeTrack,
//         difficulty: safeDifficulty,
//         score_overall: estimatedScore,
//         score_communication: estimatedScore,
//         score_confidence: estimatedScore,
//         score_body_language: 7,
//         score_eye_contact: 7,
//         score_speaking_pace: 7,
//         duration_seconds: durationSeconds,
//         report_json: reportJson,
//       });

//       if (error) {
//         throw error;
//       }

//       console.log("Vapi session saved to Supabase.");
//     } catch (err) {
//       console.error("Failed to save Vapi session:", err);
//       setSaveError(err?.message || "Failed to save interview session.");
//     } finally {
//       setSavingSession(false);
//     }
//   };

//   const {
//     CALL_STATUS,
//     callStatus,
//     messages,
//     lastMessage,
//     isSpeaking,
//     isMuted,
//     error,
//     startCall,
//     endCall,
//     toggleMute,
//   } = useVapiInterview({
//     userName: candidateName,
//     track: safeTrack,
//     difficulty: safeDifficulty,
//     jobDescription,
//     resumeText,
//     interviewTitle: safeInterviewTitle,
//     interviewRole: safeInterviewRole,
//     interviewCompany,
//     questionCount: safeQuestionCount,
//     onCallFinished: handleCallFinished,
//   });

//   useEffect(() => {
//     if (!track) {
//       console.warn("No interview setup found. Using default General interview.");
//     }
//   }, [track]);

//   useEffect(() => {
//     if (callStatus === CALL_STATUS.ACTIVE && !callStartTimeRef.current) {
//       callStartTimeRef.current = Date.now();
//     }
//   }, [callStatus, CALL_STATUS.ACTIVE]);

//   const isConnecting = callStatus === CALL_STATUS.CONNECTING;
//   const isActive = callStatus === CALL_STATUS.ACTIVE;
//   const isFinished = callStatus === CALL_STATUS.FINISHED;
//   const isError = callStatus === CALL_STATUS.ERROR;
//   const isInactive = callStatus === CALL_STATUS.INACTIVE;

//   const handleStartCall = async () => {
//     setSaveError("");
//     setSessionSaved(false);

//     sessionSavedRef.current = false;
//     callStartTimeRef.current = Date.now();

//     await startCall();
//   };

//   const handleEndCall = () => {
//     endCall();
//   };

//   const handleBackToSetup = () => {
//     if (isActive || isConnecting) {
//       const confirmLeave = window.confirm(
//         "Your interview call is still active. Do you want to end it and go back to setup?"
//       );

//       if (!confirmLeave) {
//         return;
//       }

//       endCall();
//     }

//     navigate("/setup");
//   };

//   const handleDashboardClick = () => {
//     if (!user) {
//       navigate("/login");
//       return;
//     }

//     navigate("/dashboard");
//   };

//   const handleNewInterview = () => {
//     if (isActive || isConnecting) {
//       const confirmRestart = window.confirm(
//         "Your current interview call is active. Do you want to end it and create a new interview?"
//       );

//       if (!confirmRestart) {
//         return;
//       }

//       endCall();
//     }

//     navigate("/setup");
//   };

//   return (
//     <div className="interview-room-page">
//       <div className="interview-room-bg interview-room-bg-one"></div>
//       <div className="interview-room-bg interview-room-bg-two"></div>

//       <header className="interview-room-header">
//         <button
//           type="button"
//           onClick={handleBackToSetup}
//           className="interview-room-back-btn"
//         >
//           <ArrowLeft size={18} />
//           <span>Setup</span>
//         </button>

//         <div className="interview-room-title-box">
//           <h1>AI Voice Interview</h1>
//           <p>Powered by Vapi</p>
//         </div>

//         <button
//           type="button"
//           onClick={handleDashboardClick}
//           className="interview-room-dashboard-btn"
//         >
//           <LayoutDashboard size={17} />
//           <span>{user ? "Dashboard" : "Login"}</span>
//         </button>
//       </header>

//       <main className="interview-room-main">
//         <section className="interview-room-left">
//           <div className="interview-room-info-card">
//             <div className="interview-room-info-top">
//               <div>
//                 <h2>{safeInterviewTitle}</h2>
//                 <p>
//                   {safeDifficulty} level practice session for {safeInterviewRole}
//                 </p>
//               </div>

//               <div
//                 className={`interview-room-status interview-room-status-${String(
//                   callStatus
//                 ).toLowerCase()}`}
//               >
//                 {isConnecting && <Loader2 size={15} className="spin" />}
//                 {isActive && <Volume2 size={15} />}
//                 {isFinished && <PhoneOff size={15} />}
//                 {isError && <AlertCircle size={15} />}
//                 {isInactive && <Phone size={15} />}

//                 <span>{callStatus}</span>
//               </div>
//             </div>

//             <div className="interview-room-meta-grid">
//               <MetaItem
//                 icon={<Briefcase size={18} />}
//                 label="Track"
//                 value={safeTrack}
//               />

//               <MetaItem
//                 icon={<User size={18} />}
//                 label="Role"
//                 value={safeInterviewRole}
//               />

//               <MetaItem
//                 icon={<Building2 size={18} />}
//                 label="Company"
//                 value={interviewCompany || "Not added"}
//               />

//               <MetaItem
//                 icon={<Hash size={18} />}
//                 label="Questions"
//                 value={`${safeQuestionCount}`}
//               />

//               <MetaItem
//                 icon={<FileText size={18} />}
//                 label="Resume"
//                 value={resumeFileName || "Not uploaded"}
//               />

//               <MetaItem
//                 icon={<MessageSquare size={18} />}
//                 label="JD"
//                 value={hasJobDescription ? "Added" : "Not added"}
//               />
//             </div>
//           </div>

//           <div className="interview-room-call-view">
//             <div className="interview-person-card ai-card">
//               <div className="interview-avatar ai-avatar">
//                 <Bot size={48} />
//                 {isSpeaking && <span className="speaking-ring"></span>}
//               </div>

//               <h3>AI Interviewer</h3>

//               <p>
//                 {isSpeaking
//                   ? "Speaking..."
//                   : isActive
//                   ? "Listening and ready"
//                   : "Ready to ask questions"}
//               </p>
//             </div>

//             <div className="interview-person-card user-card">
//               <div className="interview-avatar user-avatar">
//                 <User size={48} />
//               </div>

//               <h3>{candidateName}</h3>

//               <p>
//                 {isActive
//                   ? isMuted
//                     ? "Microphone muted"
//                     : "Microphone ready"
//                   : "Waiting to start"}
//               </p>
//             </div>
//           </div>

//           <div className="interview-room-controls">
//             {!isActive ? (
//               <button
//                 type="button"
//                 onClick={handleStartCall}
//                 disabled={isConnecting}
//                 className="interview-call-btn"
//               >
//                 {isConnecting ? (
//                   <>
//                     <Loader2 size={20} className="spin" />
//                     Connecting...
//                   </>
//                 ) : (
//                   <>
//                     <Phone size={20} />
//                     Start Vapi Interview
//                   </>
//                 )}
//               </button>
//             ) : (
//               <button
//                 type="button"
//                 onClick={handleEndCall}
//                 className="interview-end-btn"
//               >
//                 <PhoneOff size={20} />
//                 End Interview
//               </button>
//             )}

//             <button
//               type="button"
//               onClick={toggleMute}
//               disabled={!isActive}
//               className={`interview-mute-btn ${isMuted ? "muted" : ""}`}
//             >
//               {isMuted ? <MicOff size={20} /> : <Mic size={20} />}
//               {isMuted ? "Unmute" : "Mute"}
//             </button>

//             <button
//               type="button"
//               onClick={handleNewInterview}
//               className="interview-new-btn"
//             >
//               <RotateCcw size={18} />
//               New Setup
//             </button>
//           </div>

//           {error && <div className="interview-error-box">{error}</div>}

//           {saveError && <div className="interview-error-box">{saveError}</div>}

//           {savingSession && (
//             <div className="interview-saving-box">
//               <Loader2 size={18} className="spin" />
//               <span>Saving your interview session...</span>
//             </div>
//           )}

//           {isFinished && (
//             <div className="interview-finished-box">
//               <h3>Interview ended</h3>

//               <p>
//                 Your transcript is shown on the right. Logged-in users will see
//                 this session in dashboard history.
//               </p>

//               <div className="interview-finished-actions">
//                 <button type="button" onClick={handleDashboardClick}>
//                   {user ? "Go to Dashboard" : "Login to Save History"}
//                 </button>

//                 <button type="button" onClick={handleNewInterview}>
//                   New Interview
//                 </button>
//               </div>
//             </div>
//           )}

//           {sessionSaved && user && !savingSession && !saveError && (
//             <div className="interview-saving-box interview-save-success-box">
//               <span>✓ Interview session saved successfully.</span>
//             </div>
//           )}
//         </section>

//         <section className="interview-room-right">
//           <div className="interview-transcript-card">
//             <div className="interview-transcript-header">
//               <div>
//                 <h2>Live Transcript</h2>
//                 <p>{messages.length} messages captured</p>
//               </div>
//             </div>

//             {messages.length === 0 ? (
//               <div className="interview-empty-transcript">
//                 <MessageSquare size={34} />

//                 <h3>No transcript yet</h3>

//                 <p>
//                   Start the Vapi interview. Final transcripts will appear here
//                   after each spoken message.
//                 </p>
//               </div>
//             ) : (
//               <div className="interview-transcript-list">
//                 {messages.map((message, index) => (
//                   <TranscriptBubble
//                     key={`${message.role}-${index}`}
//                     role={message.role}
//                     content={message.content}
//                   />
//                 ))}
//               </div>
//             )}
//           </div>

//           {lastMessage && (
//             <div className="interview-last-message-card">
//               <span>Latest message</span>
//               <p>{lastMessage}</p>
//             </div>
//           )}
//         </section>
//       </main>
//     </div>
//   );
// }

// function MetaItem({ icon, label, value }) {
//   return (
//     <div className="interview-meta-item">
//       <div className="interview-meta-icon">{icon}</div>

//       <div>
//         <span>{label}</span>
//         <strong>{value}</strong>
//       </div>
//     </div>
//   );
// }

// function TranscriptBubble({ role, content }) {
//   const isUser = role === "user";
//   const isAssistant = role === "assistant";

//   return (
//     <div
//       className={`interview-transcript-bubble ${
//         isUser
//           ? "user-message"
//           : isAssistant
//           ? "assistant-message"
//           : "system-message"
//       }`}
//     >
//       <span>
//         {isUser
//           ? "You"
//           : isAssistant
//           ? "AI Interviewer"
//           : role || "System"}
//       </span>

//       <p>{content}</p>
//     </div>
//   );
// }
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
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
  Video,
  VideoOff,
  Eye,
  Activity,
} from "lucide-react";

import { useInterviewStore } from "../store/useInterviewStore";
import { useAuthStore } from "../store/useAuthStore";
import { supabase } from "../lib/supabase";
import { useVapiInterview } from "../hooks/useVapiInterview";
import { scoreInterviewSession } from "../lib/ragApi";

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
    interviewSkills,
  } = useInterviewStore();

  const [sessionSaved, setSessionSaved] = useState(false);
  const [savingSession, setSavingSession] = useState(false);
  const [saveError, setSaveError] = useState("");

  const [cameraReady, setCameraReady] = useState(false);
  const [cameraError, setCameraError] = useState("");
  const [cameraWarning, setCameraWarning] = useState(
    "Camera preview ready. Start interview to begin tracking."
  );

  const [liveCameraScores, setLiveCameraScores] = useState({
    eyeContact: 7,
    bodyLanguage: 7,
    speakingPace: 7,
  });

  const sessionSavedRef = useRef(false);
  const callStartTimeRef = useRef(null);

  const videoRef = useRef(null);
  const cameraStreamRef = useRef(null);
  const cameraCanvasRef = useRef(null);
  const cameraMonitorTimerRef = useRef(null);
  const faceDetectorRef = useRef(null);
  const lastWarningRef = useRef("");

  const cameraMetricsRef = useRef({
    cameraReady: false,
    trackingStartedAt: null,
    trackingEndedAt: null,

    totalChecks: 0,
    faceDetectedChecks: 0,
    centeredFaceChecks: 0,
    eyeContactChecks: 0,

    movementWarnings: 0,
    faceMissingWarnings: 0,
    offCenterWarnings: 0,
    lookingAwayWarnings: 0,

    lastFaceCenter: null,
    totalMovement: 0,

    warningHistory: [],
    faceDetectorAvailable: false,
  });

  const candidateName = useMemo(() => {
    if (user?.email) {
      return user.email.split("@")[0];
    }

    return "Guest";
  }, [user]);

  const safeTrack = useMemo(() => track || "General", [track]);

  const safeDifficulty = useMemo(() => difficulty || "Fresher", [difficulty]);

  const safeInterviewTitle = useMemo(() => {
    return interviewTitle || `${safeTrack} Interview`;
  }, [interviewTitle, safeTrack]);

  const safeInterviewRole = useMemo(() => {
    return interviewRole || safeTrack;
  }, [interviewRole, safeTrack]);

  const safeQuestionCount = useMemo(() => {
    return Number(questionCount) || 15;
  }, [questionCount]);

  const safeSkills = useMemo(() => {
    if (Array.isArray(interviewSkills)) {
      return interviewSkills;
    }

    try {
      const storedSkills = JSON.parse(
        localStorage.getItem("interview_setup_skills") || "[]"
      );

      return Array.isArray(storedSkills) ? storedSkills : [];
    } catch {
      return [];
    }
  }, [interviewSkills]);

  const hasJobDescription = useMemo(() => {
    return Boolean(jobDescription && jobDescription.trim().length > 0);
  }, [jobDescription]);

  const hasResumeText = useMemo(() => {
    return Boolean(resumeText && resumeText.trim().length > 0);
  }, [resumeText]);

  const clampScore = useCallback((value, fallback = 7) => {
    const num = Number(value);

    if (Number.isNaN(num)) {
      return fallback;
    }

    return Math.max(0, Math.min(10, Number(num.toFixed(1))));
  }, []);

  const addCameraWarning = useCallback((warning) => {
    if (!warning) {
      return;
    }

    if (lastWarningRef.current === warning) {
      return;
    }

    lastWarningRef.current = warning;
    setCameraWarning(warning);

    const history = cameraMetricsRef.current.warningHistory || [];

    cameraMetricsRef.current.warningHistory = [
      ...history,
      {
        text: warning,
        time: new Date().toISOString(),
      },
    ].slice(-40);
  }, []);

  const calculateCameraScores = useCallback(() => {
    const metrics = cameraMetricsRef.current;

    const totalChecks = Math.max(1, Number(metrics.totalChecks || 0));
    const faceDetectedChecks = Number(metrics.faceDetectedChecks || 0);
    const centeredFaceChecks = Number(metrics.centeredFaceChecks || 0);
    const eyeContactChecks = Number(metrics.eyeContactChecks || 0);

    const faceVisiblePercent = (faceDetectedChecks / totalChecks) * 100;
    const centeredFacePercent = (centeredFaceChecks / totalChecks) * 100;
    const eyeContactPercent = (eyeContactChecks / totalChecks) * 100;

    let eyeContactScore = 4 + eyeContactPercent / 16.5;
    let bodyLanguageScore = 4 + centeredFacePercent / 18;

    const movementPenalty = Math.min(
      2.2,
      Number(metrics.movementWarnings || 0) * 0.25
    );

    const faceMissingPenalty = Math.min(
      2.4,
      Number(metrics.faceMissingWarnings || 0) * 0.3
    );

    const offCenterPenalty = Math.min(
      1.8,
      Number(metrics.offCenterWarnings || 0) * 0.18
    );

    eyeContactScore -= faceMissingPenalty;
    eyeContactScore -= Math.min(
      1.6,
      Number(metrics.lookingAwayWarnings || 0) * 0.2
    );

    bodyLanguageScore -= movementPenalty;
    bodyLanguageScore -= offCenterPenalty;
    bodyLanguageScore -= Math.min(1.4, faceMissingPenalty);

    if (faceVisiblePercent >= 85 && centeredFacePercent >= 70) {
      bodyLanguageScore += 0.8;
    }

    if (eyeContactPercent >= 70) {
      eyeContactScore += 0.8;
    }

    return {
      eyeContactScore: clampScore(eyeContactScore, 7),
      bodyLanguageScore: clampScore(bodyLanguageScore, 7),
      faceVisiblePercent: Number(faceVisiblePercent.toFixed(1)),
      centeredFacePercent: Number(centeredFacePercent.toFixed(1)),
      eyeContactPercent: Number(eyeContactPercent.toFixed(1)),
    };
  }, [clampScore]);

  const calculateSpeakingPaceScore = useCallback(
    (finalMessages, durationSeconds) => {
      const safeMessages = Array.isArray(finalMessages) ? finalMessages : [];

      const userText = safeMessages
        .filter((msg) => msg.role === "user")
        .map((msg) => String(msg.content || ""))
        .join(" ");

      const words = userText.trim() ? userText.trim().split(/\s+/).length : 0;
      const minutes = durationSeconds > 0 ? durationSeconds / 60 : 1;
      const wordsPerMinute = words / minutes;

      let score = 7;

      if (words === 0) {
        score = 3;
      } else if (wordsPerMinute < 45) {
        score = 5.5;
      } else if (wordsPerMinute < 70) {
        score = 6.5;
      } else if (wordsPerMinute <= 155) {
        score = 8.2;
      } else if (wordsPerMinute <= 190) {
        score = 7.2;
      } else {
        score = 5.8;
      }

      return {
        speakingPaceScore: clampScore(score, 7),
        wordsPerMinute: Number(wordsPerMinute.toFixed(1)),
        spokenWords: words,
      };
    },
    [clampScore]
  );

  const getFinalCameraMetrics = useCallback(
    (finalMessages = [], durationSeconds = 0) => {
      const cameraScores = calculateCameraScores();
      const speaking = calculateSpeakingPaceScore(
        finalMessages,
        durationSeconds
      );

      const metrics = cameraMetricsRef.current;

      return {
        cameraReady: Boolean(cameraReady || metrics.cameraReady),
        cameraMetricsAvailable: Boolean(metrics.totalChecks > 0),
        faceDetectorAvailable: Boolean(metrics.faceDetectorAvailable),

        totalChecks: Number(metrics.totalChecks || 0),
        faceDetectedChecks: Number(metrics.faceDetectedChecks || 0),
        centeredFaceChecks: Number(metrics.centeredFaceChecks || 0),
        eyeContactChecks: Number(metrics.eyeContactChecks || 0),

        faceVisiblePercent: cameraScores.faceVisiblePercent,
        centeredFacePercent: cameraScores.centeredFacePercent,
        eyeContactPercent: cameraScores.eyeContactPercent,

        movementWarnings: Number(metrics.movementWarnings || 0),
        faceMissingWarnings: Number(metrics.faceMissingWarnings || 0),
        offCenterWarnings: Number(metrics.offCenterWarnings || 0),
        lookingAwayWarnings: Number(metrics.lookingAwayWarnings || 0),

        eyeContactScoreEstimate: cameraScores.eyeContactScore,
        bodyLanguageScoreEstimate: cameraScores.bodyLanguageScore,
        speakingPaceScoreEstimate: speaking.speakingPaceScore,

        wordsPerMinute: speaking.wordsPerMinute,
        spokenWords: speaking.spokenWords,

        warningHistory: metrics.warningHistory || [],
        latestWarning: cameraWarning,

        note:
          "Frontend-estimated camera and speaking metrics. Groq should use these as supportive signals with transcript quality.",
      };
    },
    [
      cameraReady,
      cameraWarning,
      calculateCameraScores,
      calculateSpeakingPaceScore,
    ]
  );

  const stopCameraMonitoring = useCallback(() => {
    if (cameraMonitorTimerRef.current) {
      clearInterval(cameraMonitorTimerRef.current);
      cameraMonitorTimerRef.current = null;
    }

    cameraMetricsRef.current.trackingEndedAt = new Date().toISOString();
  }, []);

  const analyzeCameraFrame = useCallback(async () => {
    const video = videoRef.current;

    if (!video || video.readyState < 2) {
      return;
    }

    const metrics = cameraMetricsRef.current;

    metrics.totalChecks += 1;

    const width = video.videoWidth || 640;
    const height = video.videoHeight || 360;

    if (!cameraCanvasRef.current) {
      cameraCanvasRef.current = document.createElement("canvas");
    }

    const canvas = cameraCanvasRef.current;
    canvas.width = width;
    canvas.height = height;

    const context = canvas.getContext("2d");

    if (!context) {
      return;
    }

    context.drawImage(video, 0, 0, width, height);

    try {
      if (!faceDetectorRef.current && "FaceDetector" in window) {
        faceDetectorRef.current = new window.FaceDetector({
          fastMode: true,
          maxDetectedFaces: 1,
        });

        metrics.faceDetectorAvailable = true;
      }

      if (!faceDetectorRef.current) {
        metrics.faceDetectedChecks += 1;
        metrics.centeredFaceChecks += 1;
        metrics.eyeContactChecks += 1;

        addCameraWarning(
          "Camera is active. Browser face tracking is limited, so keep your face centered."
        );

        const scores = calculateCameraScores();

        setLiveCameraScores((prev) => ({
          ...prev,
          eyeContact: scores.eyeContactScore,
          bodyLanguage: scores.bodyLanguageScore,
        }));

        return;
      }

      const faces = await faceDetectorRef.current.detect(canvas);

      if (!faces || faces.length === 0) {
        metrics.faceMissingWarnings += 1;

        addCameraWarning("Face not visible. Please sit in front of the camera.");

        const scores = calculateCameraScores();

        setLiveCameraScores((prev) => ({
          ...prev,
          eyeContact: scores.eyeContactScore,
          bodyLanguage: scores.bodyLanguageScore,
        }));

        return;
      }

      const face = faces[0];
      const box = face.boundingBox;

      const centerX = (box.x + box.width / 2) / width;
      const centerY = (box.y + box.height / 2) / height;
      const faceAreaRatio = (box.width * box.height) / (width * height);

      const isCentered =
        centerX >= 0.34 &&
        centerX <= 0.66 &&
        centerY >= 0.22 &&
        centerY <= 0.76;

      const isGoodFaceSize = faceAreaRatio >= 0.06 && faceAreaRatio <= 0.55;
      const looksLikeEyeContact = isCentered && isGoodFaceSize;

      metrics.faceDetectedChecks += 1;

      if (isCentered) {
        metrics.centeredFaceChecks += 1;
      } else {
        metrics.offCenterWarnings += 1;
      }

      if (looksLikeEyeContact) {
        metrics.eyeContactChecks += 1;
      } else {
        metrics.lookingAwayWarnings += 1;
      }

      if (metrics.lastFaceCenter) {
        const dx = centerX - metrics.lastFaceCenter.x;
        const dy = centerY - metrics.lastFaceCenter.y;
        const movement = Math.sqrt(dx * dx + dy * dy);

        metrics.totalMovement += movement;

        if (movement > 0.16) {
          metrics.movementWarnings += 1;
        }
      }

      metrics.lastFaceCenter = {
        x: centerX,
        y: centerY,
      };

      if (!isCentered) {
        addCameraWarning("Maintain eye contact. Keep your face centered.");
      } else if (!isGoodFaceSize) {
        addCameraWarning("Adjust your distance from camera.");
      } else if (
        metrics.movementWarnings > 0 &&
        metrics.movementWarnings % 4 === 0
      ) {
        addCameraWarning("Body movement is high. Sit steady and relaxed.");
      } else {
        addCameraWarning("Good camera posture. Keep answering confidently.");
      }

      const scores = calculateCameraScores();

      setLiveCameraScores((prev) => ({
        ...prev,
        eyeContact: scores.eyeContactScore,
        bodyLanguage: scores.bodyLanguageScore,
      }));
    } catch (err) {
      console.warn("Camera frame analysis failed:", err);

      metrics.faceDetectorAvailable = false;
      metrics.faceDetectedChecks += 1;
      metrics.centeredFaceChecks += 1;
      metrics.eyeContactChecks += 1;

      addCameraWarning(
        "Camera is active. Keep your face centered and maintain eye contact."
      );

      const scores = calculateCameraScores();

      setLiveCameraScores((prev) => ({
        ...prev,
        eyeContact: scores.eyeContactScore,
        bodyLanguage: scores.bodyLanguageScore,
      }));
    }
  }, [addCameraWarning, calculateCameraScores]);

  const startCameraMonitoring = useCallback(() => {
    stopCameraMonitoring();

    cameraMetricsRef.current = {
      cameraReady: Boolean(cameraReady),
      trackingStartedAt: new Date().toISOString(),
      trackingEndedAt: null,

      totalChecks: 0,
      faceDetectedChecks: 0,
      centeredFaceChecks: 0,
      eyeContactChecks: 0,

      movementWarnings: 0,
      faceMissingWarnings: 0,
      offCenterWarnings: 0,
      lookingAwayWarnings: 0,

      lastFaceCenter: null,
      totalMovement: 0,

      warningHistory: [],
      faceDetectorAvailable: false,
    };

    lastWarningRef.current = "";
    setCameraWarning("Camera tracking started. Keep your face centered.");

    cameraMonitorTimerRef.current = setInterval(() => {
      analyzeCameraFrame();
    }, 900);
  }, [analyzeCameraFrame, cameraReady, stopCameraMonitoring]);

  const stopCameraPreview = useCallback(() => {
    stopCameraMonitoring();

    if (cameraStreamRef.current) {
      cameraStreamRef.current.getTracks().forEach((trackItem) => {
        trackItem.stop();
      });

      cameraStreamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setCameraReady(false);
  }, [stopCameraMonitoring]);

  const startCameraPreview = useCallback(async () => {
    try {
      setCameraError("");

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setCameraError("Your browser does not support camera access.");
        setCameraReady(false);
        return;
      }

      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });

      cameraStreamRef.current = mediaStream;
      cameraMetricsRef.current.cameraReady = true;

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;

        try {
          await videoRef.current.play();
        } catch {
          // Browser may autoplay muted video automatically after render.
        }
      }

      setCameraReady(true);
      setCameraWarning("Camera is ready. Start interview to track eye contact.");
    } catch (err) {
      console.error("Interview camera preview error:", err);

      setCameraReady(false);
      setCameraError(
        "Camera permission was denied or camera is not available. Interview can continue, but camera-based scores may be low."
      );
      setCameraWarning(
        "Camera not available. Eye contact/body language cannot be tracked."
      );
    }
  }, []);

  useEffect(() => {
    startCameraPreview();

    return () => {
      stopCameraPreview();
    };
  }, [startCameraPreview, stopCameraPreview]);

  useEffect(() => {
    if (cameraReady && videoRef.current && cameraStreamRef.current) {
      videoRef.current.srcObject = cameraStreamRef.current;

      videoRef.current.play().catch(() => {
        // Safe ignore.
      });
    }
  }, [cameraReady]);

  const buildTranscriptText = useCallback((finalMessages) => {
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

        return `${roleLabel}: ${msg.content || ""}`;
      })
      .join("\n");
  }, []);

  const getFallbackScoreReport = useCallback(
    ({
      safeMessages,
      userMessages,
      assistantMessages,
      transcriptText,
      durationSeconds,
      cameraMetrics,
    }) => {
      const answerLengths = userMessages
        .map((msg) => String(msg.content || "").trim().split(/\s+/).length)
        .filter((count) => count > 0);

      const avgAnswerWords =
        answerLengths.length > 0
          ? answerLengths.reduce((sum, count) => sum + count, 0) /
            answerLengths.length
          : 0;

      let fallbackScore = 5.5;

      if (userMessages.length === 0) {
        fallbackScore = 3.0;
      } else if (userMessages.length === 1) {
        fallbackScore = 5.0;
      } else if (userMessages.length >= 2) {
        fallbackScore = 6.0;
      }

      if (userMessages.length >= 3) {
        fallbackScore += 0.5;
      }

      if (userMessages.length >= 5) {
        fallbackScore += 0.4;
      }

      if (avgAnswerWords >= 8) {
        fallbackScore += 0.4;
      }

      if (avgAnswerWords >= 15) {
        fallbackScore += 0.5;
      }

      if (avgAnswerWords >= 25) {
        fallbackScore += 0.5;
      }

      fallbackScore = clampScore(fallbackScore, 5);

      return {
        success: true,
        score_overall: fallbackScore,
        score_communication: fallbackScore,
        score_confidence: fallbackScore,

        score_body_language: cameraMetrics?.bodyLanguageScoreEstimate ?? 7,
        score_eye_contact: cameraMetrics?.eyeContactScoreEstimate ?? 7,
        score_speaking_pace: cameraMetrics?.speakingPaceScoreEstimate ?? 7,

        camera_metrics_available: Boolean(cameraMetrics?.cameraMetricsAvailable),
        non_verbal_metrics_counted: true,

        overallSummary:
          "Interview completed. Groq scoring was not available, so fallback scoring used transcript quality plus frontend camera/speaking estimates.",
        improvementTips: [
          "Give answers with a little more explanation and examples.",
          "Maintain eye contact by keeping your face centered.",
          "Sit steady and avoid unnecessary movement.",
          "Use clear structure: point, explanation, example.",
        ],
        strengths: [],
        weaknesses: [
          "Detailed Groq scoring was unavailable, so fallback scoring was used.",
        ],
        scoreReason: `Fallback score based on ${
          userMessages.length
        } candidate answers, ${
          assistantMessages.length
        } AI questions, average answer length of ${avgAnswerWords.toFixed(
          1
        )} words, and camera/speaking estimates.`,
        transcript: safeMessages,
        transcriptText,
        totalMessages: safeMessages.length,
        userAnswers: userMessages.length,
        aiQuestions: assistantMessages.length,
        durationSeconds,
        cameraMetrics,
        provider: "fallback",
        model: "fallback",
      };
    },
    [clampScore]
  );

  const normalizeScore = useCallback((value, fallback = 5) => {
    const num = Number(value);

    if (Number.isNaN(num)) {
      return fallback;
    }

    return Math.max(0, Math.min(10, Number(num.toFixed(1))));
  }, []);

  const handleCallFinished = useCallback(
    async (finalMessages = []) => {
      if (sessionSavedRef.current) {
        return;
      }

      stopCameraMonitoring();

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

        const startedAt = callStartTimeRef.current;

        const durationSeconds = startedAt
          ? Math.max(0, Math.round((Date.now() - startedAt) / 1000))
          : 0;

        const cameraMetrics = getFinalCameraMetrics(
          safeMessages,
          durationSeconds
        );

        setLiveCameraScores({
          eyeContact: cameraMetrics.eyeContactScoreEstimate,
          bodyLanguage: cameraMetrics.bodyLanguageScoreEstimate,
          speakingPace: cameraMetrics.speakingPaceScoreEstimate,
        });

        let scoringResult = null;

        try {
          scoringResult = await scoreInterviewSession({
            track: safeTrack,
            difficulty: safeDifficulty,
            interviewTitle: safeInterviewTitle,
            interviewRole: safeInterviewRole,
            interviewCompany: interviewCompany || "",
            questionCount: safeQuestionCount,
            skills: safeSkills,
            jobDescription: jobDescription || "",
            resumeText: resumeText || "",
            resumeFileName: resumeFileName || "",
            transcript: safeMessages,
            transcriptText,
            durationSeconds,
            cameraMetrics,
          });
        } catch (scoreErr) {
          console.warn("Groq scoring failed. Using fallback score:", scoreErr);

          scoringResult = getFallbackScoreReport({
            safeMessages,
            userMessages,
            assistantMessages,
            transcriptText,
            durationSeconds,
            cameraMetrics,
          });
        }

        const scoreOverall = normalizeScore(scoringResult?.score_overall, 5);

        const scoreCommunication = normalizeScore(
          scoringResult?.score_communication,
          scoreOverall
        );

        const scoreConfidence = normalizeScore(
          scoringResult?.score_confidence,
          scoreOverall
        );

        const scoreBodyLanguage = normalizeScore(
          scoringResult?.score_body_language,
          cameraMetrics.bodyLanguageScoreEstimate
        );

        const scoreEyeContact = normalizeScore(
          scoringResult?.score_eye_contact,
          cameraMetrics.eyeContactScoreEstimate
        );

        const scoreSpeakingPace = normalizeScore(
          scoringResult?.score_speaking_pace,
          cameraMetrics.speakingPaceScoreEstimate
        );

        const reportJson = {
          overallSummary:
            scoringResult?.overallSummary ||
            scoringResult?.overall_summary ||
            "Interview completed and scored from transcript + camera metrics.",

          improvementTips: Array.isArray(scoringResult?.improvementTips)
            ? scoringResult.improvementTips
            : Array.isArray(scoringResult?.improvement_tips)
            ? scoringResult.improvement_tips
            : [],

          strengths: Array.isArray(scoringResult?.strengths)
            ? scoringResult.strengths
            : [],

          weaknesses: Array.isArray(scoringResult?.weaknesses)
            ? scoringResult.weaknesses
            : [],

          scoreReason:
            scoringResult?.scoreReason ||
            scoringResult?.score_reason ||
            "Score generated from transcript, camera metrics, and speaking pace estimate.",

          transcript: safeMessages,
          transcriptText,
          totalMessages: safeMessages.length,
          userAnswers: userMessages.length,
          aiQuestions: assistantMessages.length,
          durationSeconds,

          groqScoring: scoringResult,
          cameraMetrics,

          setup: {
            interviewId: createdInterviewId || null,
            interviewTitle: safeInterviewTitle,
            role: safeInterviewRole,
            company: interviewCompany || null,
            track: safeTrack,
            difficulty: safeDifficulty,
            questionCount: safeQuestionCount,
            skills: safeSkills,
            resumeFileName: resumeFileName || null,
            hasJobDescription,
            hasResumeText,
          },
        };

        const { error } = await supabase.from("session_scores").insert({
          user_id: user.id,
          track: safeTrack,
          difficulty: safeDifficulty,
          score_overall: scoreOverall,
          score_communication: scoreCommunication,
          score_confidence: scoreConfidence,

          score_body_language: scoreBodyLanguage,
          score_eye_contact: scoreEyeContact,
          score_speaking_pace: scoreSpeakingPace,

          duration_seconds: durationSeconds,
          report_json: reportJson,
        });

        if (error) {
          throw error;
        }

        console.log(
          "Vapi session saved to Supabase with transcript + camera score."
        );
      } catch (err) {
        console.error("Failed to save Vapi session:", err);
        setSaveError(err?.message || "Failed to save interview session.");
      } finally {
        setSavingSession(false);
      }
    },
    [
      user,
      safeTrack,
      safeDifficulty,
      safeInterviewTitle,
      safeInterviewRole,
      interviewCompany,
      safeQuestionCount,
      safeSkills,
      jobDescription,
      resumeText,
      resumeFileName,
      createdInterviewId,
      hasJobDescription,
      hasResumeText,
      buildTranscriptText,
      getFinalCameraMetrics,
      getFallbackScoreReport,
      normalizeScore,
      stopCameraMonitoring,
    ]
  );

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
    skills: safeSkills,
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

  useEffect(() => {
    if (isActive && cameraReady && !cameraMonitorTimerRef.current) {
      startCameraMonitoring();
    }

    if (!isActive) {
      stopCameraMonitoring();
    }
  }, [isActive, cameraReady, startCameraMonitoring, stopCameraMonitoring]);

  const handleStartCall = async () => {
    setSaveError("");
    setSessionSaved(false);

    sessionSavedRef.current = false;
    callStartTimeRef.current = Date.now();

    if (!cameraStreamRef.current) {
      await startCameraPreview();
    }

    await startCall();
  };

  const handleEndCall = () => {
    stopCameraMonitoring();
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

    stopCameraPreview();
    navigate("/setup");
  };

  const handleDashboardClick = () => {
    if (!user) {
      navigate("/login");
      return;
    }

    stopCameraPreview();
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

    stopCameraPreview();
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
          <p>Powered by Vapi + Groq transcript/camera scoring</p>
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

          <div className="interview-room-camera-card">
            <div className="interview-camera-header">
              <div>
                <h3>Camera Preview</h3>
                <p>
                  Live warning and estimated eye contact/body language tracking.
                  These metrics are sent to Groq with your transcript.
                </p>
              </div>

              <span
                className={
                  cameraReady
                    ? "interview-camera-status-ready"
                    : "interview-camera-status-off"
                }
              >
                {cameraReady ? (
                  <>
                    <Video size={14} />
                    Camera On
                  </>
                ) : (
                  <>
                    <VideoOff size={14} />
                    Camera Off
                  </>
                )}
              </span>
            </div>

            <div className="interview-camera-preview-box">
              {cameraReady ? (
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="interview-camera-video"
                />
              ) : (
                <div className="interview-camera-placeholder">
                  <VideoOff size={38} />
                  <p>{cameraError || "Camera preview is not available."}</p>

                  <button type="button" onClick={startCameraPreview}>
                    Try Camera Again
                  </button>
                </div>
              )}
            </div>

            <div className="interview-camera-warning-box">
              <AlertCircle size={16} />
              <span>{cameraWarning}</span>
            </div>

            <div className="interview-live-score-grid">
              <LiveScoreItem
                icon={<Eye size={16} />}
                label="Eye Contact"
                value={liveCameraScores.eyeContact}
              />

              <LiveScoreItem
                icon={<Activity size={16} />}
                label="Body Language"
                value={liveCameraScores.bodyLanguage}
              />

              <LiveScoreItem
                icon={<Mic size={16} />}
                label="Speaking Pace"
                value={liveCameraScores.speakingPace}
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
              <span>Scoring with Groq and saving your interview...</span>
            </div>
          )}

          {isFinished && (
            <div className="interview-finished-box">
              <h3>Interview ended</h3>

              <p>
                Your transcript and camera metrics are shown in the final
                dashboard report.
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
              <span>✓ Interview session scored and saved successfully.</span>
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

function LiveScoreItem({ icon, label, value }) {
  return (
    <div className="interview-live-score-item">
      <div className="interview-live-score-icon">{icon}</div>

      <div>
        <span>{label}</span>
        <strong>{Number(value || 0).toFixed(1)}</strong>
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
        {isUser ? "You" : isAssistant ? "AI Interviewer" : role || "System"}
      </span>

      <p>{content}</p>
    </div>
  );
}