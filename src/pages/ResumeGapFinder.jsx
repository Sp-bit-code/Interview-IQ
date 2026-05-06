// import React, { useEffect, useMemo, useRef } from "react";
// import { Link, useNavigate } from "react-router";
// import {
//   ArrowLeft,
//   UploadCloud,
//   FileText,
//   ClipboardCheck,
//   Loader2,
//   AlertCircle,
//   CheckCircle2,
//   Sparkles,
//   Trash2,
//   Briefcase,
//   Percent,
//   Target,
//   BadgeCheck,
//   BookOpen,
//   ExternalLink,
//   RotateCcw,
//   FileSearch,
//   Brain,
//   Lightbulb,
// } from "lucide-react";

// import {
//   analyzeResumeGap,
//   checkRagBackendHealth,
// } from "../lib/ragApi";

// import { useRagStore } from "../store/useRagStore";

// import "./ResumeGapFinder.css";

// export default function ResumeGapFinder() {
//   const navigate = useNavigate();
//   const resumeInputRef = useRef(null);

//   const {
//     backendStatus,
//     backendError,

//     resumeSessionId,
//     resumeFile,
//     jobDescription,
//     resumeLoading,
//     resumeResult,
//     resumeError,

//     successMessage,
//     error,

//     setBackendStatus,
//     setBackendError,

//     setResumeSessionId,
//     setResumeFile,
//     setJobDescription,
//     setResumeLoading,
//     setResumeResult,
//     setResumeError,
//     clearResumeGapState,

//     setError,
//     clearError,
//     setSuccessMessage,
//     clearSuccessMessage,
//     clearAlerts,
//   } = useRagStore();

//   const parsedData = resumeResult?.data || {};
//   const matchPercentage = Number(parsedData.match_percentage || 0);
//   const verdict = parsedData.verdict || "Not generated";
//   const shouldApply = parsedData.should_apply || "Not generated";

//   const resultAnswer = resumeResult?.answer || "";
//   const resumeText = resumeResult?.resume_text || "";
//   const jdText = resumeResult?.jd_text || "";
//   const ragContext = resumeResult?.rag_context || "";

//   const scoreLabel = useMemo(() => {
//     if (!resumeResult) {
//       return "No analysis yet";
//     }

//     if (matchPercentage >= 80) {
//       return "Strong Match";
//     }

//     if (matchPercentage >= 65) {
//       return "Good Match";
//     }

//     if (matchPercentage >= 45) {
//       return "Average Match";
//     }

//     return "Weak Match";
//   }, [matchPercentage, resumeResult]);

//   useEffect(() => {
//     const checkBackend = async () => {
//       try {
//         setBackendStatus("checking");
//         setBackendError("");

//         await checkRagBackendHealth();

//         setBackendStatus("online");
//       } catch (err) {
//         console.error("RAG backend health check failed:", err);

//         setBackendStatus("offline");
//         setBackendError(
//           err?.message ||
//             "RAG backend is not running. Start FastAPI on port 8000."
//         );
//       }
//     };

//     checkBackend();
//   }, [setBackendStatus, setBackendError]);

//   const handleResumeChange = (event) => {
//     const file = event.target.files?.[0];

//     if (!file) {
//       return;
//     }

//     const allowedExtensions = [".pdf", ".docx", ".txt"];
//     const fileName = file.name.toLowerCase();
//     const isAllowed = allowedExtensions.some((ext) => fileName.endsWith(ext));

//     if (!isAllowed) {
//       setResumeFile(null);
//       setResumeError("Only PDF, DOCX, and TXT resume files are supported.");
//       return;
//     }

//     setResumeFile(file);
//     setResumeError("");
//     clearError();
//     clearSuccessMessage();
//   };

//   const handleAnalyzeResume = async () => {
//     if (!resumeFile) {
//       setResumeError("Please upload your resume first.");
//       return;
//     }

//     if (!jobDescription || !jobDescription.trim()) {
//       setResumeError("Please paste the job description.");
//       return;
//     }

//     try {
//       clearAlerts();
//       setResumeError("");
//       setResumeLoading(true);

//       const result = await analyzeResumeGap({
//         resumeFile,
//         jobDescription,
//         sessionId: resumeSessionId,
//       });

//       if (!result?.success) {
//         throw new Error(result?.answer || result?.message || "Resume analysis failed.");
//       }

//       if (result?.session_id) {
//         setResumeSessionId(result.session_id);
//       }

//       setResumeResult(result);
//       setSuccessMessage("Resume gap analysis completed successfully.");
//     } catch (err) {
//       console.error("Resume gap analysis error:", err);

//       setResumeError(
//         err?.message ||
//           "Failed to analyze resume. Please check backend and try again."
//       );
//       setError(err?.message || "Resume analysis failed.");
//     } finally {
//       setResumeLoading(false);
//     }
//   };

//   const handleClearAll = () => {
//     const confirmClear = window.confirm(
//       "This will clear resume, job description, and analysis result. Continue?"
//     );

//     if (!confirmClear) {
//       return;
//     }

//     clearResumeGapState();
//     clearAlerts();

//     if (resumeInputRef.current) {
//       resumeInputRef.current.value = "";
//     }
//   };

//   const handleClearResultOnly = () => {
//     setResumeResult(null);
//     setResumeError("");
//     clearError();
//     clearSuccessMessage();
//   };

//   return (
//     <div className="resume-gap-page">
//       <div className="resume-gap-bg resume-gap-bg-one"></div>
//       <div className="resume-gap-bg resume-gap-bg-two"></div>

//       <header className="resume-gap-header">
//         <button
//           type="button"
//           onClick={() => navigate("/dashboard")}
//           className="resume-gap-back-btn"
//         >
//           <ArrowLeft size={18} />
//           <span>Dashboard</span>
//         </button>

//         <div className="resume-gap-title-box">
//           <h1>Resume Gap Finder</h1>
//           <p>Compare your resume with a job description using RAG + Groq AI.</p>
//         </div>

//         <Link to="/study-notes" className="resume-gap-header-link">
//           Study from Notes
//           <ExternalLink size={16} />
//         </Link>
//       </header>

//       <main className="resume-gap-main">
//         <section className="resume-gap-left">
//           <div className="resume-card resume-upload-card">
//             <div className="resume-card-title">
//               <div className="resume-card-icon">
//                 <UploadCloud size={22} />
//               </div>

//               <div>
//                 <h2>Upload Resume</h2>
//                 <p>Upload your resume in PDF, DOCX, or TXT format.</p>
//               </div>
//             </div>

//             <label className="resume-upload-box">
//               <input
//                 ref={resumeInputRef}
//                 type="file"
//                 accept=".pdf,.docx,.txt"
//                 onChange={handleResumeChange}
//               />

//               <UploadCloud size={42} />
//               <strong>Click to upload resume</strong>
//               <span>PDF, DOCX, or TXT supported</span>
//             </label>

//             {resumeFile && (
//               <div className="resume-selected-file">
//                 <FileText size={18} />
//                 <div>
//                   <strong>{resumeFile.name}</strong>
//                   <span>{formatFileSize(resumeFile.size)}</span>
//                 </div>
//               </div>
//             )}
//           </div>

//           <div className="resume-card resume-jd-card">
//             <div className="resume-card-title">
//               <div className="resume-card-icon">
//                 <Briefcase size={22} />
//               </div>

//               <div>
//                 <h2>Paste Job Description</h2>
//                 <p>Paste the JD so AI can find skills, requirements, and gaps.</p>
//               </div>
//             </div>

//             <textarea
//               value={jobDescription}
//               onChange={(event) => setJobDescription(event.target.value)}
//               placeholder="Paste job description here..."
//               className="resume-jd-textarea"
//             />

//             <div className="resume-jd-footer">
//               <span>{jobDescription.trim().length} characters</span>
//               <button
//                 type="button"
//                 onClick={() => setJobDescription("")}
//                 disabled={!jobDescription}
//               >
//                 Clear JD
//               </button>
//             </div>
//           </div>

//           <div className="resume-card resume-action-card">
//             <div className="resume-card-title">
//               <div className="resume-card-icon">
//                 <Brain size={22} />
//               </div>

//               <div>
//                 <h2>Analyze Match</h2>
//                 <p>Backend will extract, index, retrieve, and analyze using Groq.</p>
//               </div>
//             </div>

//             <div className="resume-status-grid">
//               <StatusItem
//                 label="Backend"
//                 value={
//                   backendStatus === "online"
//                     ? "Online"
//                     : backendStatus === "checking"
//                     ? "Checking"
//                     : "Offline"
//                 }
//                 good={backendStatus === "online"}
//               />

//               <StatusItem
//                 label="Resume"
//                 value={resumeFile ? "Uploaded" : "Missing"}
//                 good={Boolean(resumeFile)}
//               />

//               <StatusItem
//                 label="JD"
//                 value={jobDescription.trim() ? "Added" : "Missing"}
//                 good={Boolean(jobDescription.trim())}
//               />

//               <StatusItem
//                 label="Session"
//                 value={resumeSessionId ? shortSession(resumeSessionId) : "New"}
//               />
//             </div>

//             {backendError && (
//               <div className="resume-alert resume-alert-error">
//                 <AlertCircle size={17} />
//                 <span>{backendError}</span>
//               </div>
//             )}

//             <button
//               type="button"
//               onClick={handleAnalyzeResume}
//               disabled={resumeLoading}
//               className="resume-primary-btn"
//             >
//               {resumeLoading ? (
//                 <>
//                   <Loader2 size={19} className="resume-spin" />
//                   Analyzing Resume...
//                 </>
//               ) : (
//                 <>
//                   <Sparkles size={19} />
//                   Analyze Resume Gap
//                 </>
//               )}
//             </button>

//             <div className="resume-action-row">
//               <button
//                 type="button"
//                 onClick={handleClearResultOnly}
//                 className="resume-secondary-btn"
//               >
//                 <RotateCcw size={17} />
//                 Clear Result
//               </button>

//               <button
//                 type="button"
//                 onClick={handleClearAll}
//                 className="resume-danger-btn"
//               >
//                 <Trash2 size={17} />
//                 Clear All
//               </button>
//             </div>
//           </div>
//         </section>

//         <section className="resume-gap-right">
//           {(resumeError || error || successMessage) && (
//             <div
//               className={`resume-alert ${
//                 resumeError || error
//                   ? "resume-alert-error"
//                   : "resume-alert-success"
//               }`}
//             >
//               {resumeError || error ? (
//                 <AlertCircle size={18} />
//               ) : (
//                 <CheckCircle2 size={18} />
//               )}

//               <span>{resumeError || error || successMessage}</span>

//               <button
//                 type="button"
//                 onClick={clearAlerts}
//                 className="resume-alert-close"
//               >
//                 ×
//               </button>
//             </div>
//           )}

//           {!resumeResult && !resumeLoading && (
//             <div className="resume-card resume-empty-card">
//               <FileSearch size={54} />
//               <h2>No analysis yet</h2>
//               <p>
//                 Upload your resume, paste a job description, and click Analyze
//                 Resume Gap.
//               </p>

//               <div className="resume-empty-steps">
//                 <StepItem number="1" text="Upload resume file" />
//                 <StepItem number="2" text="Paste job description" />
//                 <StepItem number="3" text="Run AI gap analysis" />
//               </div>
//             </div>
//           )}

//           {resumeLoading && (
//             <div className="resume-card resume-loading-card">
//               <Loader2 size={46} className="resume-spin" />
//               <h2>Analyzing your resume...</h2>
//               <p>
//                 Extracting resume text, indexing with ChromaDB, retrieving
//                 context, and generating match report.
//               </p>
//             </div>
//           )}

//           {resumeResult && !resumeLoading && (
//             <>
//               <div className="resume-card resume-score-card">
//                 <div className="resume-score-circle">
//                   <span>{matchPercentage}%</span>
//                   <small>Match</small>
//                 </div>

//                 <div className="resume-score-content">
//                   <span className="resume-score-label">{scoreLabel}</span>
//                   <h2>{verdict}</h2>
//                   <p>
//                     Apply decision: <strong>{shouldApply}</strong>
//                   </p>
//                 </div>
//               </div>

//               <div className="resume-result-grid">
//                 <MiniResultCard
//                   icon={<Percent size={20} />}
//                   label="Match Percentage"
//                   value={`${matchPercentage}%`}
//                 />

//                 <MiniResultCard
//                   icon={<BadgeCheck size={20} />}
//                   label="Verdict"
//                   value={verdict}
//                 />

//                 <MiniResultCard
//                   icon={<Target size={20} />}
//                   label="Should Apply"
//                   value={shouldApply}
//                 />

//                 <MiniResultCard
//                   icon={<DatabaseIcon />}
//                   label="Retrieved Chunks"
//                   value={String(resumeResult.retrieved_chunks || 0)}
//                 />
//               </div>

//               <div className="resume-card resume-report-card">
//                 <div className="resume-output-header">
//                   <div>
//                     <h2>Detailed Resume Gap Report</h2>
//                     <p>
//                       Match skills, missing skills, weak areas, and resume
//                       improvement suggestions.
//                     </p>
//                   </div>
//                 </div>

//                 <div className="resume-markdown-output">{resultAnswer}</div>
//               </div>

//               <div className="resume-card resume-debug-card">
//                 <details>
//                   <summary>
//                     <BookOpen size={17} />
//                     Retrieved RAG Context
//                   </summary>

//                   <pre>{ragContext || "No RAG context available."}</pre>
//                 </details>

//                 <details>
//                   <summary>
//                     <FileText size={17} />
//                     Extracted Resume Text
//                   </summary>

//                   <pre>{resumeText || "No resume text available."}</pre>
//                 </details>

//                 <details>
//                   <summary>
//                     <Briefcase size={17} />
//                     Extracted JD Text
//                   </summary>

//                   <pre>{jdText || "No job description text available."}</pre>
//                 </details>
//               </div>
//             </>
//           )}
//         </section>
//       </main>
//     </div>
//   );
// }

// function StatusItem({ label, value, good = false }) {
//   return (
//     <div className="resume-status-item">
//       <span>{label}</span>
//       <strong className={good ? "resume-status-good" : ""}>{value}</strong>
//     </div>
//   );
// }

// function StepItem({ number, text }) {
//   return (
//     <div className="resume-step-item">
//       <span>{number}</span>
//       <p>{text}</p>
//     </div>
//   );
// }

// function MiniResultCard({ icon, label, value }) {
//   return (
//     <div className="resume-mini-result-card">
//       <div className="resume-mini-result-icon">{icon}</div>

//       <div>
//         <span>{label}</span>
//         <strong>{value}</strong>
//       </div>
//     </div>
//   );
// }

// function DatabaseIcon() {
//   return (
//     <svg
//       xmlns="http://www.w3.org/2000/svg"
//       width="20"
//       height="20"
//       viewBox="0 0 24 24"
//       fill="none"
//       stroke="currentColor"
//       strokeWidth="2"
//       strokeLinecap="round"
//       strokeLinejoin="round"
//     >
//       <ellipse cx="12" cy="5" rx="9" ry="3" />
//       <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5" />
//       <path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3" />
//     </svg>
//   );
// }

// function formatFileSize(sizeBytes) {
//   if (!sizeBytes) {
//     return "0 KB";
//   }

//   const sizeKb = sizeBytes / 1024;

//   if (sizeKb < 1024) {
//     return `${sizeKb.toFixed(1)} KB`;
//   }

//   return `${(sizeKb / 1024).toFixed(2)} MB`;
// }

// function shortSession(sessionId) {
//   if (!sessionId) {
//     return "None";
//   }

//   if (sessionId.length <= 12) {
//     return sessionId;
//   }

//   return `${sessionId.slice(0, 6)}...${sessionId.slice(-4)}`;
// }
import React, { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router";
import {
  ArrowLeft,
  UploadCloud,
  FileText,
  ClipboardCheck,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Sparkles,
  Trash2,
  Briefcase,
  Percent,
  Target,
  BadgeCheck,
  BookOpen,
  ExternalLink,
  RotateCcw,
  FileSearch,
  Brain,
} from "lucide-react";

import { analyzeResumeGap, checkRagBackendHealth } from "../lib/ragApi";

import { useRagStore } from "../store/useRagStore";

import "./ResumeGapFinder.css";

export default function ResumeGapFinder() {
  const navigate = useNavigate();

  const resumeInputRef = useRef(null);
  const jdInputRef = useRef(null);

  const [jdFile, setJdFile] = useState(null);
  const [jdFileError, setJdFileError] = useState("");

  const {
    backendStatus,
    backendError,

    resumeSessionId,
    resumeFile,
    jobDescription,
    resumeLoading,
    resumeResult,
    resumeError,

    successMessage,
    error,

    setBackendStatus,
    setBackendError,

    setResumeSessionId,
    setResumeFile,
    setJobDescription,
    setResumeLoading,
    setResumeResult,
    setResumeError,
    clearResumeGapState,

    setError,
    clearError,
    setSuccessMessage,
    clearSuccessMessage,
    clearAlerts,
  } = useRagStore();

  const parsedData = resumeResult?.data || {};
  const matchPercentage = Number(parsedData.match_percentage || 0);
  const verdict = parsedData.verdict || "Not generated";
  const shouldApply = parsedData.should_apply || "Not generated";

  const resultAnswer = resumeResult?.answer || "";
  const resumeText = resumeResult?.resume_text || "";
  const jdText = resumeResult?.jd_text || "";
  const ragContext = resumeResult?.rag_context || "";

  const hasPastedJd = Boolean(jobDescription?.trim());
  const hasJdFile = Boolean(jdFile);
  const hasAnyJd = hasPastedJd || hasJdFile;

  const scoreLabel = useMemo(() => {
    if (!resumeResult) {
      return "No analysis yet";
    }

    if (matchPercentage >= 80) {
      return "Strong Match";
    }

    if (matchPercentage >= 65) {
      return "Good Match";
    }

    if (matchPercentage >= 45) {
      return "Average Match";
    }

    return "Weak Match";
  }, [matchPercentage, resumeResult]);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        setBackendStatus("checking");
        setBackendError("");

        await checkRagBackendHealth();

        setBackendStatus("online");
      } catch (err) {
        console.error("RAG backend health check failed:", err);

        setBackendStatus("offline");
        setBackendError(
          err?.message ||
            "RAG backend is not running. Start FastAPI on port 8000."
        );
      }
    };

    checkBackend();
  }, [setBackendStatus, setBackendError]);

  const isAllowedDocumentFile = (file) => {
    if (!file?.name) {
      return false;
    }

    const allowedExtensions = [".pdf", ".docx", ".txt"];
    const fileName = file.name.toLowerCase();

    return allowedExtensions.some((ext) => fileName.endsWith(ext));
  };

  const handleResumeChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (!isAllowedDocumentFile(file)) {
      setResumeFile(null);
      setResumeError("Only PDF, DOCX, and TXT resume files are supported.");
      return;
    }

    setResumeFile(file);
    setResumeError("");
    clearError();
    clearSuccessMessage();
  };

  const handleJdFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (!isAllowedDocumentFile(file)) {
      setJdFile(null);
      setJdFileError("Only PDF, DOCX, and TXT JD files are supported.");
      return;
    }

    setJdFile(file);
    setJdFileError("");
    setResumeError("");
    clearError();
    clearSuccessMessage();
  };

  const handleClearJdFile = () => {
    setJdFile(null);
    setJdFileError("");

    if (jdInputRef.current) {
      jdInputRef.current.value = "";
    }
  };

  const handleAnalyzeResume = async () => {
    if (!resumeFile) {
      setResumeError("Please upload your resume first.");
      return;
    }

    if (!hasAnyJd) {
      setResumeError("Please upload JD file or paste the job description.");
      return;
    }

    try {
      clearAlerts();
      setResumeError("");
      setJdFileError("");
      setResumeLoading(true);

      const result = await analyzeResumeGap({
        resumeFile,
        jdFile,
        jobDescription,
        sessionId: resumeSessionId,
      });

      if (!result?.success) {
        throw new Error(
          result?.answer || result?.message || "Resume analysis failed."
        );
      }

      if (result?.session_id) {
        setResumeSessionId(result.session_id);
      }

      setResumeResult(result);
      setSuccessMessage("Resume gap analysis completed successfully.");
    } catch (err) {
      console.error("Resume gap analysis error:", err);

      setResumeError(
        err?.message ||
          "Failed to analyze resume. Please check backend and try again."
      );

      setError(err?.message || "Resume analysis failed.");
    } finally {
      setResumeLoading(false);
    }
  };

  const handleClearAll = () => {
    const confirmClear = window.confirm(
      "This will clear resume, job description, JD file, and analysis result. Continue?"
    );

    if (!confirmClear) {
      return;
    }

    clearResumeGapState();
    clearAlerts();
    setJdFile(null);
    setJdFileError("");

    if (resumeInputRef.current) {
      resumeInputRef.current.value = "";
    }

    if (jdInputRef.current) {
      jdInputRef.current.value = "";
    }
  };

  const handleClearResultOnly = () => {
    setResumeResult(null);
    setResumeError("");
    setJdFileError("");
    clearError();
    clearSuccessMessage();
  };

  return (
    <div className="resume-gap-page">
      <div className="resume-gap-bg resume-gap-bg-one"></div>
      <div className="resume-gap-bg resume-gap-bg-two"></div>

      <header className="resume-gap-header">
        <button
          type="button"
          onClick={() => navigate("/dashboard")}
          className="resume-gap-back-btn"
        >
          <ArrowLeft size={18} />
          <span>Dashboard</span>
        </button>

        <div className="resume-gap-title-box">
          <h1>Resume Gap Finder</h1>
          <p>Compare your resume with a job description using RAG + Groq AI.</p>
        </div>

        <Link to="/study-notes" className="resume-gap-header-link">
          Study from Notes
          <ExternalLink size={16} />
        </Link>
      </header>

      <main className="resume-gap-main">
        <section className="resume-gap-left">
          <div className="resume-card resume-upload-card">
            <div className="resume-card-title">
              <div className="resume-card-icon">
                <UploadCloud size={22} />
              </div>

              <div>
                <h2>Upload Resume</h2>
                <p>Upload your resume in PDF, DOCX, or TXT format.</p>
              </div>
            </div>

            <label className="resume-upload-box">
              <input
                ref={resumeInputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleResumeChange}
              />

              <UploadCloud size={42} />
              <strong>Click to upload resume</strong>
              <span>PDF, DOCX, or TXT supported</span>
            </label>

            {resumeFile && (
              <div className="resume-selected-file">
                <FileText size={18} />

                <div>
                  <strong>{resumeFile.name}</strong>
                  <span>{formatFileSize(resumeFile.size)}</span>
                </div>
              </div>
            )}
          </div>

          <div className="resume-card resume-jd-card">
            <div className="resume-card-title">
              <div className="resume-card-icon">
                <Briefcase size={22} />
              </div>

              <div>
                <h2>Job Description</h2>
                <p>Upload JD file or paste the job description manually.</p>
              </div>
            </div>

            <label className="resume-upload-box resume-jd-upload-box">
              <input
                ref={jdInputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleJdFileChange}
              />

              <UploadCloud size={38} />
              <strong>Click to upload JD file</strong>
              <span>PDF, DOCX, or TXT supported</span>
            </label>

            {jdFile && (
              <div className="resume-selected-file">
                <FileText size={18} />

                <div>
                  <strong>{jdFile.name}</strong>
                  <span>{formatFileSize(jdFile.size)}</span>
                </div>

                <button
                  type="button"
                  onClick={handleClearJdFile}
                  className="resume-file-clear-btn"
                >
                  ×
                </button>
              </div>
            )}

            <div className="resume-or-divider">
              <span>OR</span>
            </div>

            <textarea
              value={jobDescription}
              onChange={(event) => setJobDescription(event.target.value)}
              placeholder="Paste job description here..."
              className="resume-jd-textarea"
            />

            <div className="resume-jd-footer">
              <span>{jobDescription.trim().length} characters</span>

              <button
                type="button"
                onClick={() => setJobDescription("")}
                disabled={!jobDescription}
              >
                Clear Pasted JD
              </button>
            </div>

            {jdFileError && (
              <div className="resume-alert resume-alert-error resume-mini-alert">
                <AlertCircle size={17} />
                <span>{jdFileError}</span>
              </div>
            )}
          </div>

          <div className="resume-card resume-action-card">
            <div className="resume-card-title">
              <div className="resume-card-icon">
                <Brain size={22} />
              </div>

              <div>
                <h2>Analyze Match</h2>
                <p>Backend will extract, index, retrieve, and analyze using Groq.</p>
              </div>
            </div>

            <div className="resume-status-grid">
              <StatusItem
                label="Backend"
                value={
                  backendStatus === "online"
                    ? "Online"
                    : backendStatus === "checking"
                    ? "Checking"
                    : "Offline"
                }
                good={backendStatus === "online"}
              />

              <StatusItem
                label="Resume"
                value={resumeFile ? "Uploaded" : "Missing"}
                good={Boolean(resumeFile)}
              />

              <StatusItem
                label="JD"
                value={
                  hasJdFile
                    ? "File uploaded"
                    : hasPastedJd
                    ? "Pasted"
                    : "Missing"
                }
                good={hasAnyJd}
              />

              <StatusItem
                label="Session"
                value={resumeSessionId ? shortSession(resumeSessionId) : "New"}
              />
            </div>

            {backendError && (
              <div className="resume-alert resume-alert-error">
                <AlertCircle size={17} />
                <span>{backendError}</span>
              </div>
            )}

            <button
              type="button"
              onClick={handleAnalyzeResume}
              disabled={resumeLoading}
              className="resume-primary-btn"
            >
              {resumeLoading ? (
                <>
                  <Loader2 size={19} className="resume-spin" />
                  Analyzing Resume...
                </>
              ) : (
                <>
                  <Sparkles size={19} />
                  Analyze Resume Gap
                </>
              )}
            </button>

            <div className="resume-action-row">
              <button
                type="button"
                onClick={handleClearResultOnly}
                className="resume-secondary-btn"
              >
                <RotateCcw size={17} />
                Clear Result
              </button>

              <button
                type="button"
                onClick={handleClearAll}
                className="resume-danger-btn"
              >
                <Trash2 size={17} />
                Clear All
              </button>
            </div>
          </div>
        </section>

        <section className="resume-gap-right">
          {(resumeError || error || successMessage) && (
            <div
              className={`resume-alert ${
                resumeError || error
                  ? "resume-alert-error"
                  : "resume-alert-success"
              }`}
            >
              {resumeError || error ? (
                <AlertCircle size={18} />
              ) : (
                <CheckCircle2 size={18} />
              )}

              <span>{resumeError || error || successMessage}</span>

              <button
                type="button"
                onClick={clearAlerts}
                className="resume-alert-close"
              >
                ×
              </button>
            </div>
          )}

          {!resumeResult && !resumeLoading && (
            <div className="resume-card resume-empty-card">
              <FileSearch size={54} />

              <h2>No analysis yet</h2>

              <p>
                Upload your resume, upload or paste a job description, and click
                Analyze Resume Gap.
              </p>

              <div className="resume-empty-steps">
                <StepItem number="1" text="Upload resume file" />
                <StepItem number="2" text="Upload JD or paste JD" />
                <StepItem number="3" text="Run AI gap analysis" />
              </div>
            </div>
          )}

          {resumeLoading && (
            <div className="resume-card resume-loading-card">
              <Loader2 size={46} className="resume-spin" />

              <h2>Analyzing your resume...</h2>

              <p>
                Extracting resume and JD text, indexing with ChromaDB,
                retrieving context, and generating match report.
              </p>
            </div>
          )}

          {resumeResult && !resumeLoading && (
            <>
              <div className="resume-card resume-score-card">
                <div className="resume-score-circle">
                  <span>{matchPercentage}%</span>
                  <small>Match</small>
                </div>

                <div className="resume-score-content">
                  <span className="resume-score-label">{scoreLabel}</span>

                  <h2>{verdict}</h2>

                  <p>
                    Apply decision: <strong>{shouldApply}</strong>
                  </p>
                </div>
              </div>

              <div className="resume-result-grid">
                <MiniResultCard
                  icon={<Percent size={20} />}
                  label="Match Percentage"
                  value={`${matchPercentage}%`}
                />

                <MiniResultCard
                  icon={<BadgeCheck size={20} />}
                  label="Verdict"
                  value={verdict}
                />

                <MiniResultCard
                  icon={<Target size={20} />}
                  label="Should Apply"
                  value={shouldApply}
                />

                <MiniResultCard
                  icon={<DatabaseIcon />}
                  label="Retrieved Chunks"
                  value={String(resumeResult.retrieved_chunks || 0)}
                />
              </div>

              <div className="resume-card resume-report-card">
                <div className="resume-output-header">
                  <div>
                    <h2>Detailed Resume Gap Report</h2>

                    <p>
                      Match skills, missing skills, weak areas, and resume
                      improvement suggestions.
                    </p>
                  </div>
                </div>

                <div className="resume-markdown-output">{resultAnswer}</div>
              </div>

              <div className="resume-card resume-debug-card">
                <details>
                  <summary>
                    <BookOpen size={17} />
                    Retrieved RAG Context
                  </summary>

                  <pre>{ragContext || "No RAG context available."}</pre>
                </details>

                <details>
                  <summary>
                    <FileText size={17} />
                    Extracted Resume Text
                  </summary>

                  <pre>{resumeText || "No resume text available."}</pre>
                </details>

                <details>
                  <summary>
                    <Briefcase size={17} />
                    Extracted JD Text
                  </summary>

                  <pre>{jdText || "No job description text available."}</pre>
                </details>
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

function StatusItem({ label, value, good = false }) {
  return (
    <div className="resume-status-item">
      <span>{label}</span>
      <strong className={good ? "resume-status-good" : ""}>{value}</strong>
    </div>
  );
}

function StepItem({ number, text }) {
  return (
    <div className="resume-step-item">
      <span>{number}</span>
      <p>{text}</p>
    </div>
  );
}

function MiniResultCard({ icon, label, value }) {
  return (
    <div className="resume-mini-result-card">
      <div className="resume-mini-result-icon">{icon}</div>

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

function DatabaseIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5" />
      <path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3" />
    </svg>
  );
}

function formatFileSize(sizeBytes) {
  if (!sizeBytes) {
    return "0 KB";
  }

  const sizeKb = sizeBytes / 1024;

  if (sizeKb < 1024) {
    return `${sizeKb.toFixed(1)} KB`;
  }

  return `${(sizeKb / 1024).toFixed(2)} MB`;
}

function shortSession(sessionId) {
  if (!sessionId) {
    return "None";
  }

  if (sessionId.length <= 12) {
    return sessionId;
  }

  return `${sessionId.slice(0, 6)}...${sessionId.slice(-4)}`;
}