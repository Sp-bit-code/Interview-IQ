// import React, { useEffect, useMemo, useRef, useState } from "react";
// import { Link, useNavigate } from "react-router";
// import {
//   ArrowLeft,
//   UploadCloud,
//   FileText,
//   Send,
//   Loader2,
//   BookOpen,
//   Sparkles,
//   MessageSquare,
//   Brain,
//   HelpCircle,
//   Trash2,
//   CheckCircle2,
//   AlertCircle,
//   RefreshCcw,
//   Layers,
//   Database,
//   FileQuestion,
//   ChevronLeft,
//   ChevronRight,
//   RotateCcw,
//   ExternalLink,
// } from "lucide-react";

// import {
//   checkRagBackendHealth,
//   uploadNotes,
//   askNotesQuestion,
//   summarizeNotes,
//   generateNotesQuestions,
//   generateFlashcards,
//   getSessionSummary,
//   clearSessionData,
// } from "../lib/ragApi";

// import { useRagStore } from "../store/useRagStore";

// import "./StudyNotes.css";

// export default function StudyNotes() {
//   const navigate = useNavigate();
//   const fileInputRef = useRef(null);
//   const chatEndRef = useRef(null);

//   const {
//     backendStatus,
//     backendError,
//     sessionId,
//     ragReady,
//     uploadedFiles,
//     savedPaths,
//     sessionSummary,
//     pdfSummary,
//     vectorStatus,

//     uploading,
//     asking,
//     summarizing,
//     generatingQuestions,
//     generatingFlashcards,
//     clearing,

//     question,
//     chatMessages,

//     summaryAnswer,
//     generatedQuestionsAnswer,

//     flashcards,
//     flashcardsRaw,
//     flashcardIndex,
//     selectedFlashcardOption,
//     flashcardAnswerChecked,

//     error,
//     successMessage,

//     setBackendStatus,
//     setBackendError,
//     setSessionId,
//     setRagReady,
//     setUploadedFiles,
//     setSavedPaths,
//     setSessionData,

//     setUploading,
//     setAsking,
//     setSummarizing,
//     setGeneratingQuestions,
//     setGeneratingFlashcards,
//     setClearing,

//     setQuestion,
//     addUserMessage,
//     addAssistantMessage,
//     clearChat,

//     setSummaryAnswer,
//     setGeneratedQuestionsAnswer,

//     setFlashcards,
//     setFlashcardIndex,
//     nextFlashcard,
//     previousFlashcard,
//     setSelectedFlashcardOption,
//     checkFlashcardAnswer,
//     clearFlashcards,

//     setError,
//     clearError,
//     setSuccessMessage,
//     clearSuccessMessage,
//     clearAlerts,
//     resetNotesState,
//   } = useRagStore();

//   const [activeTool, setActiveTool] = useState("chat");

//   const selectedFilesCount = uploadedFiles?.length || 0;
//   const totalVectors = vectorStatus?.total_vectors || 0;
//   const totalPdfs = sessionSummary?.total_pdfs || 0;
//   const totalChunks = sessionSummary?.total_chunks || 0;

//   const currentFlashcard = useMemo(() => {
//     if (!Array.isArray(flashcards) || flashcards.length === 0) {
//       return null;
//     }

//     return flashcards[flashcardIndex] || flashcards[0];
//   }, [flashcards, flashcardIndex]);

//   const isCurrentAnswerCorrect = useMemo(() => {
//     if (!currentFlashcard || !selectedFlashcardOption) {
//       return false;
//     }

//     return selectedFlashcardOption === currentFlashcard.correct;
//   }, [currentFlashcard, selectedFlashcardOption]);

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

//   useEffect(() => {
//     const loadExistingSession = async () => {
//       if (!sessionId) {
//         return;
//       }

//       try {
//         const result = await getSessionSummary(sessionId);

//         setSessionData({
//           sessionId,
//           sessionSummary: result?.session_summary,
//           pdfSummary: result?.pdf_summary,
//           vectorStatus: result?.vector_status,
//           ragReady: result?.rag_ready,
//         });
//       } catch (err) {
//         console.warn("Could not load previous RAG session:", err);
//       }
//     };

//     loadExistingSession();
//   }, [sessionId, setSessionData]);

//   useEffect(() => {
//     chatEndRef.current?.scrollIntoView({
//       behavior: "smooth",
//       block: "end",
//     });
//   }, [chatMessages]);

//   const handleFileChange = (event) => {
//     const files = Array.from(event.target.files || []);

//     if (!files.length) {
//       return;
//     }

//     const invalidFiles = files.filter((file) => file.type !== "application/pdf");

//     if (invalidFiles.length > 0) {
//       setError("Please upload only PDF files.");
//       return;
//     }

//     setUploadedFiles(files);
//     clearError();
//     clearSuccessMessage();
//   };

//   const handleUploadAndProcess = async () => {
//     if (!uploadedFiles || uploadedFiles.length === 0) {
//       setError("Please select at least one PDF file.");
//       return;
//     }

//     try {
//       clearAlerts();
//       setUploading(true);

//       const result = await uploadNotes({
//         files: uploadedFiles,
//         sessionId,
//       });

//       if (!result?.success) {
//         throw new Error(result?.message || "Notes upload failed.");
//       }

//       const newSessionId = result.session_id || sessionId;

//       setSessionId(newSessionId);
//       setSavedPaths(result.saved_paths || []);

//       setSessionData({
//         sessionId: newSessionId,
//         sessionSummary: result.session_summary,
//         vectorStatus: result.vector_status,
//         ragReady: Boolean(result?.vector_status?.ready),
//       });

//       setSuccessMessage(
//         result?.message ||
//           "PDF notes uploaded, processed, and indexed successfully."
//       );

//       setActiveTool("chat");

//       if (fileInputRef.current) {
//         fileInputRef.current.value = "";
//       }
//     } catch (err) {
//       console.error("Upload/process error:", err);

//       setError(
//         err?.message ||
//           "Failed to upload/process notes. Check backend and try again."
//       );
//     } finally {
//       setUploading(false);
//     }
//   };

//   const handleRefreshSession = async () => {
//     if (!sessionId) {
//       setError("No session found. Upload notes first.");
//       return;
//     }

//     try {
//       clearAlerts();

//       const result = await getSessionSummary(sessionId);

//       setSessionData({
//         sessionId,
//         sessionSummary: result?.session_summary,
//         pdfSummary: result?.pdf_summary,
//         vectorStatus: result?.vector_status,
//         ragReady: result?.rag_ready,
//       });

//       setSuccessMessage("Session status refreshed.");
//     } catch (err) {
//       console.error("Refresh session error:", err);

//       setError(err?.message || "Failed to refresh session.");
//     }
//   };

//   const handleAskQuestion = async (event) => {
//     event.preventDefault();

//     const cleanQuestion = question.trim();

//     if (!cleanQuestion) {
//       setError("Please enter a question.");
//       return;
//     }

//     if (!sessionId || !ragReady) {
//       setError("Please upload and process notes first.");
//       return;
//     }

//     try {
//       clearAlerts();
//       setAsking(true);

//       addUserMessage(cleanQuestion);
//       setQuestion("");

//       const result = await askNotesQuestion({
//         sessionId,
//         question: cleanQuestion,
//       });

//       addAssistantMessage(result?.answer || "No answer generated.", result?.sources || []);
//     } catch (err) {
//       console.error("Ask notes error:", err);

//       addAssistantMessage(
//         err?.message ||
//           "Failed to answer from notes. Please check backend and try again.",
//         []
//       );

//       setError(err?.message || "Failed to ask question.");
//     } finally {
//       setAsking(false);
//     }
//   };

//   const handleSummarizeNotes = async () => {
//     if (!sessionId || !ragReady) {
//       setError("Please upload and process notes first.");
//       return;
//     }

//     try {
//       clearAlerts();
//       setActiveTool("summary");
//       setSummarizing(true);

//       const result = await summarizeNotes(sessionId);

//       setSummaryAnswer(result?.answer || "No summary generated.");
//     } catch (err) {
//       console.error("Summarize notes error:", err);

//       setError(err?.message || "Failed to summarize notes.");
//     } finally {
//       setSummarizing(false);
//     }
//   };

//   const handleGenerateQuestions = async () => {
//     if (!sessionId || !ragReady) {
//       setError("Please upload and process notes first.");
//       return;
//     }

//     try {
//       clearAlerts();
//       setActiveTool("questions");
//       setGeneratingQuestions(true);

//       const result = await generateNotesQuestions(sessionId);

//       setGeneratedQuestionsAnswer(result?.answer || "No questions generated.");
//     } catch (err) {
//       console.error("Generate questions error:", err);

//       setError(err?.message || "Failed to generate questions.");
//     } finally {
//       setGeneratingQuestions(false);
//     }
//   };

//   const handleGenerateFlashcards = async () => {
//     if (!sessionId || !ragReady) {
//       setError("Please upload and process notes first.");
//       return;
//     }

//     try {
//       clearAlerts();
//       setActiveTool("flashcards");
//       setGeneratingFlashcards(true);

//       const result = await generateFlashcards(sessionId);

//       setFlashcards(result?.flashcards || [], result?.raw || "");

//       if (!result?.flashcards || result.flashcards.length === 0) {
//         setError(
//           "Flashcards were generated but could not be parsed into MCQ format. Check raw output below."
//         );
//       } else {
//         setSuccessMessage(`${result.flashcards.length} flashcards generated.`);
//       }
//     } catch (err) {
//       console.error("Generate flashcards error:", err);

//       setError(err?.message || "Failed to generate flashcards.");
//     } finally {
//       setGeneratingFlashcards(false);
//     }
//   };

//   const handleClearSession = async () => {
//     if (!sessionId) {
//       resetNotesState();

//       if (fileInputRef.current) {
//         fileInputRef.current.value = "";
//       }

//       return;
//     }

//     const confirmClear = window.confirm(
//       "This will clear uploaded PDFs, vectors, chat, summary, questions, and flashcards. Continue?"
//     );

//     if (!confirmClear) {
//       return;
//     }

//     try {
//       clearAlerts();
//       setClearing(true);

//       await clearSessionData(sessionId, true);

//       resetNotesState();

//       if (fileInputRef.current) {
//         fileInputRef.current.value = "";
//       }

//       setSuccessMessage("RAG notes session cleared.");
//     } catch (err) {
//       console.error("Clear session error:", err);

//       setError(err?.message || "Failed to clear session.");
//     } finally {
//       setClearing(false);
//     }
//   };

//   const handleResetOnlyUi = () => {
//     clearChat();
//     setSummaryAnswer("");
//     setGeneratedQuestionsAnswer("");
//     clearFlashcards();
//     clearAlerts();
//   };

//   return (
//     <div className="study-notes-page">
//       <div className="study-notes-bg study-notes-bg-one"></div>
//       <div className="study-notes-bg study-notes-bg-two"></div>

//       <header className="study-notes-header">
//         <button
//           type="button"
//           onClick={() => navigate("/dashboard")}
//           className="study-notes-back-btn"
//         >
//           <ArrowLeft size={18} />
//           <span>Dashboard</span>
//         </button>

//         <div className="study-notes-title-box">
//           <h1>Study from Notes</h1>
//           <p>Upload PDFs and study using RAG, LangChain, ChromaDB, and Groq.</p>
//         </div>

//         <Link to="/resume-gap-finder" className="study-notes-header-link">
//           Resume Gap Finder
//           <ExternalLink size={16} />
//         </Link>
//       </header>

//       <main className="study-notes-main">
//         <section className="study-notes-left">
//           <div className="study-card study-upload-card">
//             <div className="study-card-title">
//               <div className="study-card-icon">
//                 <UploadCloud size={22} />
//               </div>

//               <div>
//                 <h2>Upload PDF Notes</h2>
//                 <p>Upload one or multiple PDFs. Backend will process and index them.</p>
//               </div>
//             </div>

//             <label className="study-upload-box">
//               <input
//                 ref={fileInputRef}
//                 type="file"
//                 accept="application/pdf"
//                 multiple
//                 onChange={handleFileChange}
//               />

//               <UploadCloud size={42} />
//               <strong>Click to select PDF notes</strong>
//               <span>Only PDF files are supported</span>
//             </label>

//             {selectedFilesCount > 0 && (
//               <div className="study-selected-files">
//                 {uploadedFiles.map((file, index) => (
//                   <div key={`${file.name}-${index}`} className="study-selected-file">
//                     <FileText size={17} />
//                     <span>{file.name}</span>
//                     <small>{formatFileSize(file.size)}</small>
//                   </div>
//                 ))}
//               </div>
//             )}

//             <button
//               type="button"
//               onClick={handleUploadAndProcess}
//               disabled={uploading || selectedFilesCount === 0}
//               className="study-primary-btn"
//             >
//               {uploading ? (
//                 <>
//                   <Loader2 size={19} className="study-spin" />
//                   Processing Notes...
//                 </>
//               ) : (
//                 <>
//                   <Sparkles size={19} />
//                   Upload & Process Notes
//                 </>
//               )}
//             </button>
//           </div>

//           <div className="study-card study-status-card">
//             <div className="study-card-title">
//               <div className="study-card-icon">
//                 <Database size={22} />
//               </div>

//               <div>
//                 <h2>RAG Status</h2>
//                 <p>Current backend and vector database status.</p>
//               </div>
//             </div>

//             <div className="study-status-grid">
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
//                 label="RAG Ready"
//                 value={ragReady ? "Yes" : "No"}
//                 good={ragReady}
//               />

//               <StatusItem label="PDFs" value={String(totalPdfs)} />
//               <StatusItem label="Chunks" value={String(totalChunks)} />
//               <StatusItem label="Vectors" value={String(totalVectors)} />
//               <StatusItem
//                 label="Session"
//                 value={sessionId ? shortSession(sessionId) : "None"}
//               />
//             </div>

//             {backendError && (
//               <div className="study-alert study-alert-error">
//                 <AlertCircle size={17} />
//                 <span>{backendError}</span>
//               </div>
//             )}

//             <div className="study-status-actions">
//               <button
//                 type="button"
//                 onClick={handleRefreshSession}
//                 disabled={!sessionId}
//                 className="study-secondary-btn"
//               >
//                 <RefreshCcw size={17} />
//                 Refresh
//               </button>

//               <button
//                 type="button"
//                 onClick={handleClearSession}
//                 disabled={clearing}
//                 className="study-danger-btn"
//               >
//                 {clearing ? (
//                   <Loader2 size={17} className="study-spin" />
//                 ) : (
//                   <Trash2 size={17} />
//                 )}
//                 Clear
//               </button>
//             </div>

//             {savedPaths.length > 0 && (
//               <div className="study-small-info">
//                 <strong>Saved files:</strong>
//                 {savedPaths.map((path, index) => (
//                   <span key={`${path}-${index}`}>{path}</span>
//                 ))}
//               </div>
//             )}
//           </div>

//           <div className="study-card study-tools-card">
//             <div className="study-card-title">
//               <div className="study-card-icon">
//                 <Layers size={22} />
//               </div>

//               <div>
//                 <h2>Study Tools</h2>
//                 <p>Use your uploaded notes for revision and interview prep.</p>
//               </div>
//             </div>

//             <div className="study-tool-grid">
//               <ToolButton
//                 title="Chat"
//                 desc="Ask questions from notes"
//                 icon={<MessageSquare size={21} />}
//                 active={activeTool === "chat"}
//                 onClick={() => setActiveTool("chat")}
//               />

//               <ToolButton
//                 title="Summary"
//                 desc="Summarize uploaded notes"
//                 icon={<BookOpen size={21} />}
//                 active={activeTool === "summary"}
//                 loading={summarizing}
//                 onClick={handleSummarizeNotes}
//               />

//               <ToolButton
//                 title="Questions"
//                 desc="Generate viva questions"
//                 icon={<FileQuestion size={21} />}
//                 active={activeTool === "questions"}
//                 loading={generatingQuestions}
//                 onClick={handleGenerateQuestions}
//               />

//               <ToolButton
//                 title="Flashcards"
//                 desc="Generate MCQ cards"
//                 icon={<Brain size={21} />}
//                 active={activeTool === "flashcards"}
//                 loading={generatingFlashcards}
//                 onClick={handleGenerateFlashcards}
//               />
//             </div>

//             <button
//               type="button"
//               onClick={handleResetOnlyUi}
//               className="study-secondary-btn study-full-btn"
//             >
//               <RotateCcw size={17} />
//               Clear Chat / Tool Output
//             </button>
//           </div>
//         </section>

//         <section className="study-notes-right">
//           {(error || successMessage) && (
//             <div
//               className={`study-alert ${
//                 error ? "study-alert-error" : "study-alert-success"
//               }`}
//             >
//               {error ? <AlertCircle size={18} /> : <CheckCircle2 size={18} />}
//               <span>{error || successMessage}</span>
//               <button
//                 type="button"
//                 onClick={clearAlerts}
//                 className="study-alert-close"
//               >
//                 ×
//               </button>
//             </div>
//           )}

//           {activeTool === "chat" && (
//             <div className="study-card study-chat-card">
//               <div className="study-output-header">
//                 <div>
//                   <h2>Ask Questions From Notes</h2>
//                   <p>
//                     Ask anything from uploaded PDFs. Answers include source chunks.
//                   </p>
//                 </div>

//                 <span className={ragReady ? "study-pill-ready" : "study-pill-off"}>
//                   {ragReady ? "RAG Ready" : "Upload notes first"}
//                 </span>
//               </div>

//               <div className="study-chat-list">
//                 {chatMessages.length === 0 ? (
//                   <div className="study-empty-state">
//                     <MessageSquare size={42} />
//                     <h3>No chat yet</h3>
//                     <p>
//                       Upload notes, then ask questions like “Explain this topic in
//                       simple points.”
//                     </p>
//                   </div>
//                 ) : (
//                   chatMessages.map((message, index) => (
//                     <ChatBubble
//                       key={`${message.role}-${index}`}
//                       role={message.role}
//                       content={message.content}
//                       sources={message.sources}
//                     />
//                   ))
//                 )}

//                 {asking && (
//                   <div className="study-thinking">
//                     <Loader2 size={18} className="study-spin" />
//                     Thinking from your notes...
//                   </div>
//                 )}

//                 <div ref={chatEndRef}></div>
//               </div>

//               <form onSubmit={handleAskQuestion} className="study-chat-form">
//                 <input
//                   type="text"
//                   value={question}
//                   onChange={(event) => setQuestion(event.target.value)}
//                   placeholder={
//                     ragReady
//                       ? "Ask from your notes..."
//                       : "Upload and process PDFs first..."
//                   }
//                   disabled={!ragReady || asking}
//                 />

//                 <button type="submit" disabled={!ragReady || asking}>
//                   {asking ? (
//                     <Loader2 size={19} className="study-spin" />
//                   ) : (
//                     <Send size={19} />
//                   )}
//                 </button>
//               </form>
//             </div>
//           )}

//           {activeTool === "summary" && (
//             <OutputPanel
//               title="Notes Summary"
//               subtitle="Generated study-friendly summary from your uploaded notes."
//               loading={summarizing}
//               emptyTitle="No summary generated yet"
//               emptyText="Click the Summary tool button to generate summary."
//               content={summaryAnswer}
//               icon={<BookOpen size={42} />}
//             />
//           )}

//           {activeTool === "questions" && (
//             <OutputPanel
//               title="Generated Questions"
//               subtitle="Viva and interview questions generated from your notes."
//               loading={generatingQuestions}
//               emptyTitle="No questions generated yet"
//               emptyText="Click the Questions tool button to generate questions."
//               content={generatedQuestionsAnswer}
//               icon={<HelpCircle size={42} />}
//             />
//           )}

//           {activeTool === "flashcards" && (
//             <div className="study-card study-flashcard-card">
//               <div className="study-output-header">
//                 <div>
//                   <h2>MCQ Flashcards</h2>
//                   <p>Practice revision cards generated from uploaded notes.</p>
//                 </div>

//                 {flashcards.length > 0 && (
//                   <span className="study-pill-ready">
//                     {flashcardIndex + 1} / {flashcards.length}
//                   </span>
//                 )}
//               </div>

//               {generatingFlashcards ? (
//                 <div className="study-loading-output">
//                   <Loader2 size={34} className="study-spin" />
//                   <p>Generating flashcards...</p>
//                 </div>
//               ) : !currentFlashcard ? (
//                 <div className="study-empty-state">
//                   <Brain size={42} />
//                   <h3>No flashcards yet</h3>
//                   <p>Click the Flashcards tool button to generate MCQ cards.</p>

//                   {flashcardsRaw && (
//                     <details className="study-raw-output">
//                       <summary>Raw output</summary>
//                       <pre>{flashcardsRaw}</pre>
//                     </details>
//                   )}
//                 </div>
//               ) : (
//                 <div className="study-flashcard-box">
//                   <div className="study-flashcard-question">
//                     <span>Question</span>
//                     <h3>{currentFlashcard.question}</h3>
//                   </div>

//                   <div className="study-flashcard-options">
//                     {["A", "B", "C", "D"].map((option) => (
//                       <button
//                         key={option}
//                         type="button"
//                         onClick={() => setSelectedFlashcardOption(option)}
//                         className={`study-flashcard-option ${
//                           selectedFlashcardOption === option
//                             ? "study-flashcard-option-selected"
//                             : ""
//                         } ${
//                           flashcardAnswerChecked &&
//                           option === currentFlashcard.correct
//                             ? "study-flashcard-option-correct"
//                             : ""
//                         } ${
//                           flashcardAnswerChecked &&
//                           selectedFlashcardOption === option &&
//                           option !== currentFlashcard.correct
//                             ? "study-flashcard-option-wrong"
//                             : ""
//                         }`}
//                       >
//                         <strong>{option}</strong>
//                         <span>{currentFlashcard.options?.[option]}</span>
//                       </button>
//                     ))}
//                   </div>

//                   <div className="study-flashcard-actions">
//                     <button
//                       type="button"
//                       onClick={previousFlashcard}
//                       disabled={flashcardIndex === 0}
//                       className="study-secondary-btn"
//                     >
//                       <ChevronLeft size={17} />
//                       Previous
//                     </button>

//                     <button
//                       type="button"
//                       onClick={checkFlashcardAnswer}
//                       disabled={!selectedFlashcardOption}
//                       className="study-primary-btn study-check-btn"
//                     >
//                       Check Answer
//                     </button>

//                     <button
//                       type="button"
//                       onClick={nextFlashcard}
//                       disabled={flashcardIndex >= flashcards.length - 1}
//                       className="study-secondary-btn"
//                     >
//                       Next
//                       <ChevronRight size={17} />
//                     </button>
//                   </div>

//                   {flashcardAnswerChecked && (
//                     <div
//                       className={`study-flashcard-result ${
//                         isCurrentAnswerCorrect
//                           ? "study-flashcard-result-correct"
//                           : "study-flashcard-result-wrong"
//                       }`}
//                     >
//                       <h4>
//                         {isCurrentAnswerCorrect
//                           ? "Correct answer!"
//                           : `Wrong answer. Correct option is ${currentFlashcard.correct}.`}
//                       </h4>

//                       {currentFlashcard.answer && (
//                         <p>
//                           <strong>Answer:</strong> {currentFlashcard.answer}
//                         </p>
//                       )}

//                       {currentFlashcard.explanation && (
//                         <p>
//                           <strong>Explanation:</strong>{" "}
//                           {currentFlashcard.explanation}
//                         </p>
//                       )}

//                       {currentFlashcard.source && (
//                         <small>Source: {currentFlashcard.source}</small>
//                       )}
//                     </div>
//                   )}
//                 </div>
//               )}
//             </div>
//           )}
//         </section>
//       </main>
//     </div>
//   );
// }

// function ToolButton({ title, desc, icon, active, loading, onClick }) {
//   return (
//     <button
//       type="button"
//       onClick={onClick}
//       className={`study-tool-btn ${active ? "study-tool-btn-active" : ""}`}
//     >
//       <div className="study-tool-icon">
//         {loading ? <Loader2 size={21} className="study-spin" /> : icon}
//       </div>

//       <div>
//         <strong>{title}</strong>
//         <span>{desc}</span>
//       </div>
//     </button>
//   );
// }

// function StatusItem({ label, value, good = false }) {
//   return (
//     <div className="study-status-item">
//       <span>{label}</span>
//       <strong className={good ? "study-status-good" : ""}>{value}</strong>
//     </div>
//   );
// }

// function ChatBubble({ role, content, sources = [] }) {
//   const isUser = role === "user";

//   return (
//     <div
//       className={`study-chat-bubble ${
//         isUser ? "study-chat-user" : "study-chat-assistant"
//       }`}
//     >
//       <span>{isUser ? "You" : "AI Study Assistant"}</span>
//       <div className="study-markdown-output">{content}</div>

//       {!isUser && sources.length > 0 && (
//         <details className="study-source-details">
//           <summary>Sources ({sources.length})</summary>

//           <div className="study-source-list">
//             {sources.map((source, index) => (
//               <div key={index} className="study-source-item">
//                 <strong>
//                   {source.pdf_name || "PDF"}{" "}
//                   {source.page ? `• Page ${source.page}` : ""}
//                 </strong>

//                 {source.content_preview && <p>{source.content_preview}</p>}
//               </div>
//             ))}
//           </div>
//         </details>
//       )}
//     </div>
//   );
// }

// function OutputPanel({
//   title,
//   subtitle,
//   loading,
//   emptyTitle,
//   emptyText,
//   content,
//   icon,
// }) {
//   return (
//     <div className="study-card study-output-card">
//       <div className="study-output-header">
//         <div>
//           <h2>{title}</h2>
//           <p>{subtitle}</p>
//         </div>
//       </div>

//       {loading ? (
//         <div className="study-loading-output">
//           <Loader2 size={34} className="study-spin" />
//           <p>Generating...</p>
//         </div>
//       ) : content ? (
//         <div className="study-markdown-output study-large-output">
//           {content}
//         </div>
//       ) : (
//         <div className="study-empty-state">
//           {icon}
//           <h3>{emptyTitle}</h3>
//           <p>{emptyText}</p>
//         </div>
//       )}
//     </div>
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

























// import React, { useEffect, useMemo, useRef, useState } from "react";
// import { Link, useNavigate } from "react-router";
// import {
//   ArrowLeft,
//   UploadCloud,
//   FileText,
//   Send,
//   Loader2,
//   BookOpen,
//   Sparkles,
//   MessageSquare,
//   Brain,
//   HelpCircle,
//   Trash2,
//   CheckCircle2,
//   AlertCircle,
//   RefreshCcw,
//   Layers,
//   Database,
//   FileQuestion,
//   ChevronLeft,
//   ChevronRight,
//   RotateCcw,
//   ExternalLink,
// } from "lucide-react";

// import {
//   checkRagBackendHealth,
//   uploadNotes,
//   askNotesQuestion,
//   summarizeNotes,
//   generateNotesQuestions,
//   generateFlashcards,
//   getSessionSummary,
//   clearSessionData,
// } from "../lib/ragApi";

// import { useRagStore } from "../store/useRagStore";

// import "./StudyNotes.css";

// export default function StudyNotes() {
//   const navigate = useNavigate();
//   const fileInputRef = useRef(null);
//   const chatEndRef = useRef(null);

//   const {
//     backendStatus,
//     backendError,
//     sessionId,
//     ragReady,
//     uploadedFiles,
//     savedPaths,
//     sessionSummary,
//     pdfSummary,
//     vectorStatus,

//     uploading,
//     asking,
//     summarizing,
//     generatingQuestions,
//     generatingFlashcards,
//     clearing,

//     question,
//     chatMessages,

//     summaryAnswer,
//     generatedQuestionsAnswer,

//     flashcards,
//     flashcardsRaw,
//     flashcardIndex,
//     selectedFlashcardOption,
//     flashcardAnswerChecked,

//     error,
//     successMessage,

//     setBackendStatus,
//     setBackendError,
//     setSessionId,
//     setRagReady,
//     setUploadedFiles,
//     setSavedPaths,
//     setSessionData,

//     setUploading,
//     setAsking,
//     setSummarizing,
//     setGeneratingQuestions,
//     setGeneratingFlashcards,
//     setClearing,

//     setQuestion,
//     addUserMessage,
//     addAssistantMessage,
//     clearChat,

//     setSummaryAnswer,
//     setGeneratedQuestionsAnswer,

//     setFlashcards,
//     setFlashcardIndex,
//     nextFlashcard,
//     previousFlashcard,
//     setSelectedFlashcardOption,
//     checkFlashcardAnswer,
//     clearFlashcards,

//     setError,
//     clearError,
//     setSuccessMessage,
//     clearSuccessMessage,
//     clearAlerts,
//     resetNotesState,
//   } = useRagStore();

//   const [activeTool, setActiveTool] = useState("chat");

//   const selectedFilesCount = uploadedFiles?.length || 0;
//   const totalVectors = vectorStatus?.total_vectors || 0;
//   const totalPdfs = sessionSummary?.total_pdfs || 0;
//   const totalChunks = sessionSummary?.total_chunks || 0;

//   const currentFlashcard = useMemo(() => {
//     if (!Array.isArray(flashcards) || flashcards.length === 0) {
//       return null;
//     }

//     return flashcards[flashcardIndex] || flashcards[0];
//   }, [flashcards, flashcardIndex]);

//   const isCurrentAnswerCorrect = useMemo(() => {
//     if (!currentFlashcard || !selectedFlashcardOption) {
//       return false;
//     }

//     return selectedFlashcardOption === currentFlashcard.correct;
//   }, [currentFlashcard, selectedFlashcardOption]);

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

//   useEffect(() => {
//     const loadExistingSession = async () => {
//       if (!sessionId) {
//         return;
//       }

//       try {
//         const result = await getSessionSummary(sessionId);

//         setSessionData({
//           sessionId,
//           sessionSummary: result?.session_summary,
//           pdfSummary: result?.pdf_summary,
//           vectorStatus: result?.vector_status,
//           ragReady: result?.rag_ready,
//         });
//       } catch (err) {
//         console.warn("Could not load previous RAG session:", err);
//       }
//     };

//     loadExistingSession();
//   }, [sessionId, setSessionData]);

//   useEffect(() => {
//     chatEndRef.current?.scrollIntoView({
//       behavior: "smooth",
//       block: "end",
//     });
//   }, [chatMessages]);

//   const handleFileChange = (event) => {
//     const files = Array.from(event.target.files || []);

//     if (!files.length) {
//       return;
//     }

//     const invalidFiles = files.filter((file) => {
//       return file.type !== "application/pdf" && !file.name.endsWith(".pdf");
//     });

//     if (invalidFiles.length > 0) {
//       setError("Please upload only PDF files.");
//       return;
//     }

//     setUploadedFiles(files);
//     clearError();
//     clearSuccessMessage();
//   };

//   const handleUploadAndProcess = async () => {
//     if (!uploadedFiles || uploadedFiles.length === 0) {
//       setError("Please select at least one PDF file.");
//       return;
//     }

//     try {
//       clearAlerts();
//       setUploading(true);

//       const result = await uploadNotes({
//         files: uploadedFiles,
//         sessionId,
//       });

//       if (!result?.success) {
//         throw new Error(result?.message || "Notes upload failed.");
//       }

//       const newSessionId = result.session_id || sessionId;

//       setSessionId(newSessionId);
//       setSavedPaths(result.saved_paths || []);

//       setSessionData({
//         sessionId: newSessionId,
//         sessionSummary: result.session_summary,
//         pdfSummary: result.pdf_summary,
//         vectorStatus: result.vector_status,
//         ragReady: Boolean(result?.vector_status?.ready),
//       });

//       setSuccessMessage(
//         result?.message ||
//           "PDF notes uploaded, processed, and indexed successfully."
//       );

//       setActiveTool("chat");

//       if (fileInputRef.current) {
//         fileInputRef.current.value = "";
//       }
//     } catch (err) {
//       console.error("Upload/process error:", err);

//       setError(
//         err?.message ||
//           "Failed to upload/process notes. Check backend and try again."
//       );
//     } finally {
//       setUploading(false);
//     }
//   };

//   const handleRefreshSession = async () => {
//     if (!sessionId) {
//       setError("No session found. Upload notes first.");
//       return;
//     }

//     try {
//       clearAlerts();

//       const result = await getSessionSummary(sessionId);

//       setSessionData({
//         sessionId,
//         sessionSummary: result?.session_summary,
//         pdfSummary: result?.pdf_summary,
//         vectorStatus: result?.vector_status,
//         ragReady: result?.rag_ready,
//       });

//       setSuccessMessage("Session status refreshed.");
//     } catch (err) {
//       console.error("Refresh session error:", err);

//       setError(err?.message || "Failed to refresh session.");
//     }
//   };

//   const handleAskQuestion = async (event) => {
//     event.preventDefault();

//     const cleanQuestion = question.trim();

//     if (!cleanQuestion) {
//       setError("Please enter a question.");
//       return;
//     }

//     if (!sessionId || !ragReady) {
//       setError("Please upload and process notes first.");
//       return;
//     }

//     try {
//       clearAlerts();
//       setAsking(true);

//       addUserMessage(cleanQuestion);
//       setQuestion("");

//       const result = await askNotesQuestion({
//         sessionId,
//         question: cleanQuestion,
//       });

//       addAssistantMessage(
//         result?.answer || "No answer generated.",
//         result?.sources || []
//       );
//     } catch (err) {
//       console.error("Ask notes error:", err);

//       addAssistantMessage(
//         err?.message ||
//           "Failed to answer from notes. Please check backend and try again.",
//         []
//       );

//       setError(err?.message || "Failed to ask question.");
//     } finally {
//       setAsking(false);
//     }
//   };

//   const handleSummarizeNotes = async () => {
//     if (!sessionId || !ragReady) {
//       setError("Please upload and process notes first.");
//       return;
//     }

//     try {
//       clearAlerts();
//       setActiveTool("summary");
//       setSummarizing(true);

//       const result = await summarizeNotes(sessionId);

//       setSummaryAnswer(result?.answer || "No summary generated.");
//     } catch (err) {
//       console.error("Summarize notes error:", err);

//       setError(err?.message || "Failed to summarize notes.");
//     } finally {
//       setSummarizing(false);
//     }
//   };

//   const handleGenerateQuestions = async () => {
//     if (!sessionId || !ragReady) {
//       setError("Please upload and process notes first.");
//       return;
//     }

//     try {
//       clearAlerts();
//       setActiveTool("questions");
//       setGeneratingQuestions(true);

//       const result = await generateNotesQuestions(sessionId);

//       setGeneratedQuestionsAnswer(result?.answer || "No questions generated.");
//     } catch (err) {
//       console.error("Generate questions error:", err);

//       setError(err?.message || "Failed to generate questions.");
//     } finally {
//       setGeneratingQuestions(false);
//     }
//   };

//   const handleGenerateFlashcards = async () => {
//     if (!sessionId || !ragReady) {
//       setError("Please upload and process notes first.");
//       return;
//     }

//     try {
//       clearAlerts();
//       setActiveTool("flashcards");
//       setGeneratingFlashcards(true);

//       const result = await generateFlashcards(sessionId);

//       setFlashcards(result?.flashcards || [], result?.raw || "");

//       if (!result?.flashcards || result.flashcards.length === 0) {
//         setError(
//           "Flashcards were generated but could not be parsed into MCQ format. Check raw output below."
//         );
//       } else {
//         setSuccessMessage(`${result.flashcards.length} flashcards generated.`);
//       }
//     } catch (err) {
//       console.error("Generate flashcards error:", err);

//       setError(err?.message || "Failed to generate flashcards.");
//     } finally {
//       setGeneratingFlashcards(false);
//     }
//   };

//   const handleClearSession = async () => {
//     if (!sessionId) {
//       resetNotesState();

//       if (fileInputRef.current) {
//         fileInputRef.current.value = "";
//       }

//       return;
//     }

//     const confirmClear = window.confirm(
//       "This will clear uploaded PDFs, vectors, chat, summary, questions, and flashcards. Continue?"
//     );

//     if (!confirmClear) {
//       return;
//     }

//     try {
//       clearAlerts();
//       setClearing(true);

//       await clearSessionData(sessionId, true);

//       resetNotesState();

//       if (fileInputRef.current) {
//         fileInputRef.current.value = "";
//       }

//       setSuccessMessage("RAG notes session cleared.");
//     } catch (err) {
//       console.error("Clear session error:", err);

//       setError(err?.message || "Failed to clear session.");
//     } finally {
//       setClearing(false);
//     }
//   };

//   const handleResetOnlyUi = () => {
//     clearChat();
//     setSummaryAnswer("");
//     setGeneratedQuestionsAnswer("");
//     clearFlashcards();
//     clearAlerts();
//   };

//   return (
//     <div className="study-notes-page">
//       <div className="study-notes-bg study-notes-bg-one"></div>
//       <div className="study-notes-bg study-notes-bg-two"></div>

//       <header className="study-notes-header">
//         <button
//           type="button"
//           onClick={() => navigate("/dashboard")}
//           className="study-notes-back-btn"
//         >
//           <ArrowLeft size={18} />
//           <span>Dashboard</span>
//         </button>

//         <div className="study-notes-title-box">
//           <h1>Study from Notes</h1>
//           <p>Upload PDFs and study using RAG, LangChain, ChromaDB, and Groq.</p>
//         </div>

//         <Link to="/" className="study-notes-header-link">
//           Home
//           <ExternalLink size={16} />
//         </Link>
//       </header>

//       <main className="study-notes-main">
//         <section className="study-notes-left">
//           <div className="study-card study-upload-card">
//             <div className="study-card-title">
//               <div className="study-card-icon">
//                 <UploadCloud size={22} />
//               </div>

//               <div>
//                 <h2>Upload PDF Notes</h2>
//                 <p>Upload one or multiple PDFs. Backend will process and index them.</p>
//               </div>
//             </div>

//             <label className="study-upload-box">
//               <input
//                 ref={fileInputRef}
//                 type="file"
//                 accept="application/pdf"
//                 multiple
//                 onChange={handleFileChange}
//               />

//               <UploadCloud size={42} />
//               <strong>Click to select PDF notes</strong>
//               <span>Only PDF files are supported</span>
//             </label>

//             {selectedFilesCount > 0 && (
//               <div className="study-selected-files">
//                 {uploadedFiles.map((file, index) => (
//                   <div
//                     key={`${file.name}-${index}`}
//                     className="study-selected-file"
//                   >
//                     <FileText size={17} />
//                     <span>{file.name}</span>
//                     <small>{formatFileSize(file.size)}</small>
//                   </div>
//                 ))}
//               </div>
//             )}

//             <button
//               type="button"
//               onClick={handleUploadAndProcess}
//               disabled={uploading || selectedFilesCount === 0}
//               className="study-primary-btn"
//             >
//               {uploading ? (
//                 <>
//                   <Loader2 size={19} className="study-spin" />
//                   Processing Notes...
//                 </>
//               ) : (
//                 <>
//                   <Sparkles size={19} />
//                   Upload & Process Notes
//                 </>
//               )}
//             </button>
//           </div>

//           <div className="study-card study-status-card">
//             <div className="study-card-title">
//               <div className="study-card-icon">
//                 <Database size={22} />
//               </div>

//               <div>
//                 <h2>RAG Status</h2>
//                 <p>Current backend and vector database status.</p>
//               </div>
//             </div>

//             <div className="study-status-grid">
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
//                 label="RAG Ready"
//                 value={ragReady ? "Yes" : "No"}
//                 good={ragReady}
//               />

//               <StatusItem label="PDFs" value={String(totalPdfs)} />
//               <StatusItem label="Chunks" value={String(totalChunks)} />
//               <StatusItem label="Vectors" value={String(totalVectors)} />
//               <StatusItem
//                 label="Session"
//                 value={sessionId ? shortSession(sessionId) : "None"}
//               />
//             </div>

//             {backendError && (
//               <div className="study-alert study-alert-error">
//                 <AlertCircle size={17} />
//                 <span>{backendError}</span>
//               </div>
//             )}

//             <div className="study-status-actions">
//               <button
//                 type="button"
//                 onClick={handleRefreshSession}
//                 disabled={!sessionId}
//                 className="study-secondary-btn"
//               >
//                 <RefreshCcw size={17} />
//                 Refresh
//               </button>

//               <button
//                 type="button"
//                 onClick={handleClearSession}
//                 disabled={clearing}
//                 className="study-danger-btn"
//               >
//                 {clearing ? (
//                   <Loader2 size={17} className="study-spin" />
//                 ) : (
//                   <Trash2 size={17} />
//                 )}
//                 Clear
//               </button>
//             </div>

//             {savedPaths.length > 0 && (
//               <div className="study-small-info">
//                 <strong>Saved files:</strong>
//                 {savedPaths.map((path, index) => (
//                   <span key={`${path}-${index}`}>{path}</span>
//                 ))}
//               </div>
//             )}
//           </div>

//           <div className="study-card study-tools-card">
//             <div className="study-card-title">
//               <div className="study-card-icon">
//                 <Layers size={22} />
//               </div>

//               <div>
//                 <h2>Study Tools</h2>
//                 <p>Use your uploaded notes for revision and interview prep.</p>
//               </div>
//             </div>

//             <div className="study-tool-grid">
//               <ToolButton
//                 title="Chat"
//                 desc="Ask questions from notes"
//                 icon={<MessageSquare size={21} />}
//                 active={activeTool === "chat"}
//                 onClick={() => setActiveTool("chat")}
//               />

//               <ToolButton
//                 title="Summary"
//                 desc="Summarize uploaded notes"
//                 icon={<BookOpen size={21} />}
//                 active={activeTool === "summary"}
//                 loading={summarizing}
//                 onClick={handleSummarizeNotes}
//               />

//               <ToolButton
//                 title="Questions"
//                 desc="Generate viva questions"
//                 icon={<FileQuestion size={21} />}
//                 active={activeTool === "questions"}
//                 loading={generatingQuestions}
//                 onClick={handleGenerateQuestions}
//               />
//             </div>

//             <button
//               type="button"
//               onClick={handleResetOnlyUi}
//               className="study-secondary-btn study-full-btn"
//             >
//               <RotateCcw size={17} />
//               Clear Chat / Tool Output
//             </button>
//           </div>
//         </section>

//         <section className="study-notes-right">
//           {(error || successMessage) && (
//             <div
//               className={`study-alert ${
//                 error ? "study-alert-error" : "study-alert-success"
//               }`}
//             >
//               {error ? <AlertCircle size={18} /> : <CheckCircle2 size={18} />}
//               <span>{error || successMessage}</span>

//               <button
//                 type="button"
//                 onClick={clearAlerts}
//                 className="study-alert-close"
//               >
//                 ×
//               </button>
//             </div>
//           )}

//           {activeTool === "chat" && (
//             <div className="study-card study-chat-card">
//               <div className="study-output-header">
//                 <div>
//                   <h2>Ask Questions From Notes</h2>
//                   <p>
//                     Ask anything from uploaded PDFs. Answers include source chunks.
//                   </p>
//                 </div>

//                 <span className={ragReady ? "study-pill-ready" : "study-pill-off"}>
//                   {ragReady ? "RAG Ready" : "Upload notes first"}
//                 </span>
//               </div>

//               <div className="study-chat-list">
//                 {chatMessages.length === 0 ? (
//                   <div className="study-empty-state">
//                     <MessageSquare size={42} />
//                     <h3>No chat yet</h3>
//                     <p>
//                       Upload notes, then ask questions like “Explain this topic in
//                       simple points.”
//                     </p>
//                   </div>
//                 ) : (
//                   chatMessages.map((message, index) => (
//                     <ChatBubble
//                       key={`${message.role}-${index}`}
//                       role={message.role}
//                       content={message.content}
//                       sources={message.sources}
//                     />
//                   ))
//                 )}

//                 {asking && (
//                   <div className="study-thinking">
//                     <Loader2 size={18} className="study-spin" />
//                     Thinking from your notes...
//                   </div>
//                 )}

//                 <div ref={chatEndRef}></div>
//               </div>

//               <form onSubmit={handleAskQuestion} className="study-chat-form">
//                 <input
//                   type="text"
//                   value={question}
//                   onChange={(event) => setQuestion(event.target.value)}
//                   placeholder={
//                     ragReady
//                       ? "Ask from your notes..."
//                       : "Upload and process PDFs first..."
//                   }
//                   disabled={!ragReady || asking}
//                 />

//                 <button type="submit" disabled={!ragReady || asking}>
//                   {asking ? (
//                     <Loader2 size={19} className="study-spin" />
//                   ) : (
//                     <Send size={19} />
//                   )}
//                 </button>
//               </form>
//             </div>
//           )}

//           {activeTool === "summary" && (
//             <OutputPanel
//               title="Notes Summary"
//               subtitle="Generated study-friendly summary from your uploaded notes."
//               loading={summarizing}
//               emptyTitle="No summary generated yet"
//               emptyText="Click the Summary tool button to generate summary."
//               content={summaryAnswer}
//               icon={<BookOpen size={42} />}
//             />
//           )}

//           {activeTool === "questions" && (
//             <OutputPanel
//               title="Generated Questions"
//               subtitle="Viva and interview questions generated from your notes."
//               loading={generatingQuestions}
//               emptyTitle="No questions generated yet"
//               emptyText="Click the Questions tool button to generate questions."
//               content={generatedQuestionsAnswer}
//               icon={<HelpCircle size={42} />}
//             />
//           )}

//           {activeTool === "flashcards" && (
//             <div className="study-card study-flashcard-card">
//               <div className="study-output-header">
//                 <div>
//                   <h2>MCQ Flashcards</h2>
//                   <p>Practice revision cards generated from uploaded notes.</p>
//                 </div>

//                 {flashcards.length > 0 && (
//                   <span className="study-pill-ready">
//                     {flashcardIndex + 1} / {flashcards.length}
//                   </span>
//                 )}
//               </div>

//               {generatingFlashcards ? (
//                 <div className="study-loading-output">
//                   <Loader2 size={34} className="study-spin" />
//                   <p>Generating flashcards...</p>
//                 </div>
//               ) : !currentFlashcard ? (
//                 <div className="study-empty-state">
//                   <Brain size={42} />
//                   <h3>No flashcards yet</h3>
//                   <p>Click the Flashcards tool button to generate MCQ cards.</p>

//                   {flashcardsRaw && (
//                     <details className="study-raw-output">
//                       <summary>Raw output</summary>
//                       <pre>{flashcardsRaw}</pre>
//                     </details>
//                   )}
//                 </div>
//               ) : (
//                 <div className="study-flashcard-box">
//                   <div className="study-flashcard-question">
//                     <span>Question</span>
//                     <h3>{currentFlashcard.question}</h3>
//                   </div>

//                   <div className="study-flashcard-options">
//                     {["A", "B", "C", "D"].map((option) => (
//                       <button
//                         key={option}
//                         type="button"
//                         onClick={() => setSelectedFlashcardOption(option)}
//                         className={`study-flashcard-option ${
//                           selectedFlashcardOption === option
//                             ? "study-flashcard-option-selected"
//                             : ""
//                         } ${
//                           flashcardAnswerChecked &&
//                           option === currentFlashcard.correct
//                             ? "study-flashcard-option-correct"
//                             : ""
//                         } ${
//                           flashcardAnswerChecked &&
//                           selectedFlashcardOption === option &&
//                           option !== currentFlashcard.correct
//                             ? "study-flashcard-option-wrong"
//                             : ""
//                         }`}
//                       >
//                         <strong>{option}</strong>
//                         <span>{currentFlashcard.options?.[option]}</span>
//                       </button>
//                     ))}
//                   </div>

//                   <div className="study-flashcard-actions">
//                     <button
//                       type="button"
//                       onClick={previousFlashcard}
//                       disabled={flashcardIndex === 0}
//                       className="study-secondary-btn"
//                     >
//                       <ChevronLeft size={17} />
//                       Previous
//                     </button>

//                     <button
//                       type="button"
//                       onClick={checkFlashcardAnswer}
//                       disabled={!selectedFlashcardOption}
//                       className="study-primary-btn study-check-btn"
//                     >
//                       Check Answer
//                     </button>

//                     <button
//                       type="button"
//                       onClick={nextFlashcard}
//                       disabled={flashcardIndex >= flashcards.length - 1}
//                       className="study-secondary-btn"
//                     >
//                       Next
//                       <ChevronRight size={17} />
//                     </button>
//                   </div>

//                   {flashcardAnswerChecked && (
//                     <div
//                       className={`study-flashcard-result ${
//                         isCurrentAnswerCorrect
//                           ? "study-flashcard-result-correct"
//                           : "study-flashcard-result-wrong"
//                       }`}
//                     >
//                       <h4>
//                         {isCurrentAnswerCorrect
//                           ? "Correct answer!"
//                           : `Wrong answer. Correct option is ${currentFlashcard.correct}.`}
//                       </h4>

//                       {currentFlashcard.answer && (
//                         <p>
//                           <strong>Answer:</strong> {currentFlashcard.answer}
//                         </p>
//                       )}

//                       {currentFlashcard.explanation && (
//                         <p>
//                           <strong>Explanation:</strong>{" "}
//                           {currentFlashcard.explanation}
//                         </p>
//                       )}

//                       {currentFlashcard.source && (
//                         <small>Source: {currentFlashcard.source}</small>
//                       )}
//                     </div>
//                   )}
//                 </div>
//               )}
//             </div>
//           )}
//         </section>
//       </main>
//     </div>
//   );
// }

// function ToolButton({ title, desc, icon, active, loading, onClick }) {
//   return (
//     <button
//       type="button"
//       onClick={onClick}
//       className={`study-tool-btn ${active ? "study-tool-btn-active" : ""}`}
//     >
//       <div className="study-tool-icon">
//         {loading ? <Loader2 size={21} className="study-spin" /> : icon}
//       </div>

//       <div>
//         <strong>{title}</strong>
//         <span>{desc}</span>
//       </div>
//     </button>
//   );
// }

// function StatusItem({ label, value, good = false }) {
//   return (
//     <div className="study-status-item">
//       <span>{label}</span>
//       <strong className={good ? "study-status-good" : ""}>{value}</strong>
//     </div>
//   );
// }

// function ChatBubble({ role, content, sources = [] }) {
//   const isUser = role === "user";

//   return (
//     <div
//       className={`study-chat-row ${
//         isUser ? "study-chat-row-user" : "study-chat-row-assistant"
//       }`}
//     >
//       <div
//         className={`study-chat-avatar ${
//           isUser ? "study-chat-avatar-user" : "study-chat-avatar-ai"
//         }`}
//       >
//         {isUser ? "Y" : "AI"}
//       </div>

//       <div
//         className={`study-chat-bubble ${
//           isUser ? "study-chat-user" : "study-chat-assistant"
//         }`}
//       >
//         <div className="study-chat-name">
//           {isUser ? "You" : "AI Study Assistant"}
//         </div>

//         <div className="study-markdown-output">
//           {renderStudyMarkdown(content)}
//         </div>

//         {!isUser && sources.length > 0 && (
//           <details className="study-source-details">
//             <summary>Sources ({sources.length})</summary>

//             <div className="study-source-list">
//               {sources.map((source, index) => (
//                 <div key={index} className="study-source-item">
//                   <strong>
//                     {source.pdf_name || "PDF"}{" "}
//                     {source.page ? `• Page ${source.page}` : ""}
//                   </strong>

//                   {source.content_preview && <p>{source.content_preview}</p>}
//                 </div>
//               ))}
//             </div>
//           </details>
//         )}
//       </div>
//     </div>
//   );
// }

// function OutputPanel({
//   title,
//   subtitle,
//   loading,
//   emptyTitle,
//   emptyText,
//   content,
//   icon,
// }) {
//   return (
//     <div className="study-card study-output-card">
//       <div className="study-output-header">
//         <div>
//           <h2>{title}</h2>
//           <p>{subtitle}</p>
//         </div>
//       </div>

//       {loading ? (
//         <div className="study-loading-output">
//           <Loader2 size={34} className="study-spin" />
//           <p>Generating...</p>
//         </div>
//       ) : content ? (
//         <div className="study-markdown-output study-large-output">
//           {renderStudyMarkdown(content)}
//         </div>
//       ) : (
//         <div className="study-empty-state">
//           {icon}
//           <h3>{emptyTitle}</h3>
//           <p>{emptyText}</p>
//         </div>
//       )}
//     </div>
//   );
// }

// function renderInlineBold(text) {
//   if (!text) {
//     return null;
//   }

//   const parts = String(text).split(/(\*\*.*?\*\*)/g);

//   return parts.map((part, index) => {
//     if (part.startsWith("**") && part.endsWith("**")) {
//       return (
//         <strong key={index} className="study-inline-bold">
//           {part.replace(/\*\*/g, "")}
//         </strong>
//       );
//     }

//     return <React.Fragment key={index}>{part}</React.Fragment>;
//   });
// }

// function cleanMarkdownLine(line) {
//   return String(line || "")
//     .replace(/^[-*+]\s+/, "")
//     .replace(/^\d+\.\s+/, "")
//     .trim();
// }

// function isHeadingLine(line) {
//   const cleanLine = String(line || "").trim();

//   if (/^\*\*.+\*\*:?\s*$/.test(cleanLine)) {
//     return true;
//   }

//   if (/^[A-Z][A-Za-z0-9 /&().,-]+:\s*$/.test(cleanLine)) {
//     return true;
//   }

//   return false;
// }

// function getHeadingText(line) {
//   return String(line || "")
//     .replace(/\*\*/g, "")
//     .replace(/:$/, "")
//     .trim();
// }

// function isBulletLine(line) {
//   const cleanLine = String(line || "").trim();

//   return /^[-*+]\s+/.test(cleanLine) || /^\d+\.\s+/.test(cleanLine);
// }

// function renderStudyMarkdown(content) {
//   if (!content) {
//     return null;
//   }

//   const lines = String(content)
//     .replace(/\r/g, "")
//     .split("\n")
//     .map((line) => line.trim())
//     .filter(Boolean);

//   const elements = [];
//   let listItems = [];

//   const flushList = () => {
//     if (listItems.length > 0) {
//       elements.push(
//         <ul key={`list-${elements.length}`} className="study-output-list">
//           {listItems.map((item, index) => (
//             <li key={index}>{renderInlineBold(item)}</li>
//           ))}
//         </ul>
//       );

//       listItems = [];
//     }
//   };

//   lines.forEach((line, index) => {
//     if (isHeadingLine(line)) {
//       flushList();

//       elements.push(
//         <h3 key={`heading-${index}`} className="study-output-heading">
//           {getHeadingText(line)}
//         </h3>
//       );

//       return;
//     }

//     if (isBulletLine(line)) {
//       listItems.push(cleanMarkdownLine(line));
//       return;
//     }

//     flushList();

//     elements.push(
//       <p key={`para-${index}`} className="study-output-paragraph">
//         {renderInlineBold(line)}
//       </p>
//     );
//   });

//   flushList();

//   return elements;
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
  Send,
  Loader2,
  BookOpen,
  Sparkles,
  MessageSquare,
  Brain,
  HelpCircle,
  Trash2,
  CheckCircle2,
  AlertCircle,
  RefreshCcw,
  Layers,
  Database,
  FileQuestion,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  ExternalLink,
} from "lucide-react";

import {
  checkRagBackendHealth,
  uploadNotes,
  askNotesQuestion,
  summarizeNotes,
  generateNotesQuestions,
  generateFlashcards,
  getSessionSummary,
  clearSessionData,
} from "../lib/ragApi";

import { useRagStore } from "../store/useRagStore";

import {
  getCompletedTopicCount,
  saveProgress,
} from "../lib/progressApi";

import "./StudyNotes.css";

export default function StudyNotes() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  const {
    backendStatus,
    backendError,
    sessionId,
    ragReady,
    uploadedFiles,
    savedPaths,
    sessionSummary,
    pdfSummary,
    vectorStatus,

    uploading,
    asking,
    summarizing,
    generatingQuestions,
    generatingFlashcards,
    clearing,

    question,
    chatMessages,

    summaryAnswer,
    generatedQuestionsAnswer,

    flashcards,
    flashcardsRaw,
    flashcardIndex,
    selectedFlashcardOption,
    flashcardAnswerChecked,

    error,
    successMessage,

    setBackendStatus,
    setBackendError,
    setSessionId,
    setRagReady,
    setUploadedFiles,
    setSavedPaths,
    setSessionData,

    setUploading,
    setAsking,
    setSummarizing,
    setGeneratingQuestions,
    setGeneratingFlashcards,
    setClearing,

    setQuestion,
    addUserMessage,
    addAssistantMessage,
    clearChat,

    setSummaryAnswer,
    setGeneratedQuestionsAnswer,

    setFlashcards,
    setFlashcardIndex,
    nextFlashcard,
    previousFlashcard,
    setSelectedFlashcardOption,
    checkFlashcardAnswer,
    clearFlashcards,

    setError,
    clearError,
    setSuccessMessage,
    clearSuccessMessage,
    clearAlerts,
    resetNotesState,
  } = useRagStore();

  const [activeTool, setActiveTool] = useState("chat");

  // Spring Boot study-progress microservice state.
  // This is intentionally separate from the existing RAG state so that
  // progress-service failures never break the existing notes experience.
  const [springProgressStatus, setSpringProgressStatus] = useState("idle");
  const [completedStudyActions, setCompletedStudyActions] = useState(0);

  const totalTrackedStudyActions = 4;

  const selectedFilesCount = uploadedFiles?.length || 0;
  const totalVectors = vectorStatus?.total_vectors || 0;
  const totalPdfs = sessionSummary?.total_pdfs || 0;
  const totalChunks = sessionSummary?.total_chunks || 0;

  const currentFlashcard = useMemo(() => {
    if (!Array.isArray(flashcards) || flashcards.length === 0) {
      return null;
    }

    return flashcards[flashcardIndex] || flashcards[0];
  }, [flashcards, flashcardIndex]);

  const isCurrentAnswerCorrect = useMemo(() => {
    if (!currentFlashcard || !selectedFlashcardOption) {
      return false;
    }

    return selectedFlashcardOption === currentFlashcard.correct;
  }, [currentFlashcard, selectedFlashcardOption]);

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

  useEffect(() => {
    const loadExistingSession = async () => {
      if (!sessionId) {
        return;
      }

      try {
        const result = await getSessionSummary(sessionId);

        setSessionData({
          sessionId,
          sessionSummary: result?.session_summary,
          pdfSummary: result?.pdf_summary,
          vectorStatus: result?.vector_status,
          ragReady: result?.rag_ready,
        });
      } catch (err) {
        console.warn("Could not load previous RAG session:", err);
      }
    };

    loadExistingSession();
  }, [sessionId, setSessionData]);

  useEffect(() => {
    const loadSpringProgress = async () => {
      if (!sessionId) {
        setSpringProgressStatus("idle");
        setCompletedStudyActions(0);
        return;
      }

      try {
        setSpringProgressStatus("checking");

        const completedCount = await getCompletedTopicCount(sessionId);

        setCompletedStudyActions(Number(completedCount) || 0);
        setSpringProgressStatus("online");
      } catch (err) {
        console.warn("Spring progress service is unavailable:", err);
        setSpringProgressStatus("offline");
      }
    };

    loadSpringProgress();
  }, [sessionId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [chatMessages]);

  const trackStudyAction = async (topicName, progressSessionId = sessionId) => {
    if (!progressSessionId || !topicName) {
      return;
    }

    try {
      await saveProgress({
        userId: progressSessionId,
        topicName,
        completed: true,
      });

      const completedCount = await getCompletedTopicCount(progressSessionId);

      setCompletedStudyActions(Number(completedCount) || 0);
      setSpringProgressStatus("online");
    } catch (err) {
      // Progress tracking is an additional Spring feature.
      // It must not interrupt any existing RAG workflow if the service is down.
      console.warn(`Could not track "${topicName}" in Spring service:`, err);
      setSpringProgressStatus("offline");
    }
  };

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files || []);

    if (!files.length) {
      return;
    }

    const invalidFiles = files.filter((file) => {
      return file.type !== "application/pdf" && !file.name.endsWith(".pdf");
    });

    if (invalidFiles.length > 0) {
      setError("Please upload only PDF files.");
      return;
    }

    setUploadedFiles(files);
    clearError();
    clearSuccessMessage();
  };

  const handleUploadAndProcess = async () => {
    if (!uploadedFiles || uploadedFiles.length === 0) {
      setError("Please select at least one PDF file.");
      return;
    }

    try {
      clearAlerts();
      setUploading(true);

      const result = await uploadNotes({
        files: uploadedFiles,
        sessionId,
      });

      if (!result?.success) {
        throw new Error(result?.message || "Notes upload failed.");
      }

      const newSessionId = result.session_id || sessionId;

      setSessionId(newSessionId);
      setSavedPaths(result.saved_paths || []);

      setSessionData({
        sessionId: newSessionId,
        sessionSummary: result.session_summary,
        pdfSummary: result.pdf_summary,
        vectorStatus: result.vector_status,
        ragReady: Boolean(result?.vector_status?.ready),
      });

      trackStudyAction("PDF Notes Processed", newSessionId);

      setSuccessMessage(
        result?.message ||
          "PDF notes uploaded, processed, and indexed successfully."
      );

      setActiveTool("chat");

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      console.error("Upload/process error:", err);

      setError(
        err?.message ||
          "Failed to upload/process notes. Check backend and try again."
      );
    } finally {
      setUploading(false);
    }
  };

  const handleRefreshSession = async () => {
    if (!sessionId) {
      setError("No session found. Upload notes first.");
      return;
    }

    try {
      clearAlerts();

      const result = await getSessionSummary(sessionId);

      setSessionData({
        sessionId,
        sessionSummary: result?.session_summary,
        pdfSummary: result?.pdf_summary,
        vectorStatus: result?.vector_status,
        ragReady: result?.rag_ready,
      });

      setSuccessMessage("Session status refreshed.");
    } catch (err) {
      console.error("Refresh session error:", err);

      setError(err?.message || "Failed to refresh session.");
    }
  };

  const handleAskQuestion = async (event) => {
    event.preventDefault();

    const cleanQuestion = question.trim();

    if (!cleanQuestion) {
      setError("Please enter a question.");
      return;
    }

    if (!sessionId || !ragReady) {
      setError("Please upload and process notes first.");
      return;
    }

    try {
      clearAlerts();
      setAsking(true);

      addUserMessage(cleanQuestion);
      setQuestion("");

      const result = await askNotesQuestion({
        sessionId,
        question: cleanQuestion,
      });

      addAssistantMessage(
        result?.answer || "No answer generated.",
        result?.sources || []
      );
    } catch (err) {
      console.error("Ask notes error:", err);

      addAssistantMessage(
        err?.message ||
          "Failed to answer from notes. Please check backend and try again.",
        []
      );

      setError(err?.message || "Failed to ask question.");
    } finally {
      setAsking(false);
    }
  };

  const handleSummarizeNotes = async () => {
    if (!sessionId || !ragReady) {
      setError("Please upload and process notes first.");
      return;
    }

    try {
      clearAlerts();
      setActiveTool("summary");
      setSummarizing(true);

      const result = await summarizeNotes(sessionId);

      setSummaryAnswer(result?.answer || "No summary generated.");

      trackStudyAction("Summary Generated");
    } catch (err) {
      console.error("Summarize notes error:", err);

      setError(err?.message || "Failed to summarize notes.");
    } finally {
      setSummarizing(false);
    }
  };

  const handleGenerateQuestions = async () => {
    if (!sessionId || !ragReady) {
      setError("Please upload and process notes first.");
      return;
    }

    try {
      clearAlerts();
      setActiveTool("questions");
      setGeneratingQuestions(true);

      const result = await generateNotesQuestions(sessionId);

      setGeneratedQuestionsAnswer(result?.answer || "No questions generated.");

      trackStudyAction("Practice Questions Generated");
    } catch (err) {
      console.error("Generate questions error:", err);

      setError(err?.message || "Failed to generate questions.");
    } finally {
      setGeneratingQuestions(false);
    }
  };

  const handleGenerateFlashcards = async () => {
    if (!sessionId || !ragReady) {
      setError("Please upload and process notes first.");
      return;
    }

    try {
      clearAlerts();
      setActiveTool("flashcards");
      setGeneratingFlashcards(true);

      const result = await generateFlashcards(sessionId);

      setFlashcards(result?.flashcards || [], result?.raw || "");

      trackStudyAction("Flashcards Generated");

      if (!result?.flashcards || result.flashcards.length === 0) {
        setError(
          "Flashcards were generated but could not be parsed into MCQ format. Check raw output below."
        );
      } else {
        setSuccessMessage(`${result.flashcards.length} flashcards generated.`);
      }
    } catch (err) {
      console.error("Generate flashcards error:", err);

      setError(err?.message || "Failed to generate flashcards.");
    } finally {
      setGeneratingFlashcards(false);
    }
  };

  const handleClearSession = async () => {
    if (!sessionId) {
      resetNotesState();

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      return;
    }

    const confirmClear = window.confirm(
      "This will clear uploaded PDFs, vectors, chat, summary, questions, and flashcards. Continue?"
    );

    if (!confirmClear) {
      return;
    }

    try {
      clearAlerts();
      setClearing(true);

      await clearSessionData(sessionId, true);

      resetNotesState();

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      setSuccessMessage("RAG notes session cleared.");
    } catch (err) {
      console.error("Clear session error:", err);

      setError(err?.message || "Failed to clear session.");
    } finally {
      setClearing(false);
    }
  };

  const handleResetOnlyUi = () => {
    clearChat();
    setSummaryAnswer("");
    setGeneratedQuestionsAnswer("");
    clearFlashcards();
    clearAlerts();
  };

  return (
    <div className="study-notes-page">
      <div className="study-notes-bg study-notes-bg-one"></div>
      <div className="study-notes-bg study-notes-bg-two"></div>

      <header className="study-notes-header">
        <button
          type="button"
          onClick={() => navigate("/dashboard")}
          className="study-notes-back-btn"
        >
          <ArrowLeft size={18} />
          <span>Dashboard</span>
        </button>

        <div className="study-notes-title-box">
          <h1>Study from Notes</h1>
          <p>Upload PDFs and study using RAG, LangChain, ChromaDB, and Groq.</p>
        </div>

        <Link to="/" className="study-notes-header-link">
          Home
          <ExternalLink size={16} />
        </Link>
      </header>

      <main className="study-notes-main">
        <section className="study-notes-left">
          <div className="study-card study-upload-card">
            <div className="study-card-title">
              <div className="study-card-icon">
                <UploadCloud size={22} />
              </div>

              <div>
                <h2>Upload PDF Notes</h2>
                <p>Upload one or multiple PDFs. Backend will process and index them.</p>
              </div>
            </div>

            <label className="study-upload-box">
              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf"
                multiple
                onChange={handleFileChange}
              />

              <UploadCloud size={42} />
              <strong>Click to select PDF notes</strong>
              <span>Only PDF files are supported</span>
            </label>

            {selectedFilesCount > 0 && (
              <div className="study-selected-files">
                {uploadedFiles.map((file, index) => (
                  <div
                    key={`${file.name}-${index}`}
                    className="study-selected-file"
                  >
                    <FileText size={17} />
                    <span>{file.name}</span>
                    <small>{formatFileSize(file.size)}</small>
                  </div>
                ))}
              </div>
            )}

            <button
              type="button"
              onClick={handleUploadAndProcess}
              disabled={uploading || selectedFilesCount === 0}
              className="study-primary-btn"
            >
              {uploading ? (
                <>
                  <Loader2 size={19} className="study-spin" />
                  Processing Notes...
                </>
              ) : (
                <>
                  <Sparkles size={19} />
                  Upload & Process Notes
                </>
              )}
            </button>
          </div>

          <div className="study-card study-status-card">
            <div className="study-card-title">
              <div className="study-card-icon">
                <Database size={22} />
              </div>

              <div>
                <h2>RAG Status</h2>
                <p>Current backend and vector database status.</p>
              </div>
            </div>

            <div className="study-status-grid">
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
                label="RAG Ready"
                value={ragReady ? "Yes" : "No"}
                good={ragReady}
              />

              <StatusItem label="PDFs" value={String(totalPdfs)} />
              <StatusItem label="Chunks" value={String(totalChunks)} />
              <StatusItem label="Vectors" value={String(totalVectors)} />

              <StatusItem
                label="Spring API"
                value={
                  springProgressStatus === "online"
                    ? "Online"
                    : springProgressStatus === "checking"
                    ? "Checking"
                    : springProgressStatus === "offline"
                    ? "Offline"
                    : "Waiting"
                }
                good={springProgressStatus === "online"}
              />

              <StatusItem
                label="Study Progress"
                value={`${completedStudyActions}/${totalTrackedStudyActions}`}
                good={completedStudyActions >= totalTrackedStudyActions}
              />

              <StatusItem
                label="Session"
                value={sessionId ? shortSession(sessionId) : "None"}
              />
            </div>

            {backendError && (
              <div className="study-alert study-alert-error">
                <AlertCircle size={17} />
                <span>{backendError}</span>
              </div>
            )}

            <div className="study-status-actions">
              <button
                type="button"
                onClick={handleRefreshSession}
                disabled={!sessionId}
                className="study-secondary-btn"
              >
                <RefreshCcw size={17} />
                Refresh
              </button>

              <button
                type="button"
                onClick={handleClearSession}
                disabled={clearing}
                className="study-danger-btn"
              >
                {clearing ? (
                  <Loader2 size={17} className="study-spin" />
                ) : (
                  <Trash2 size={17} />
                )}
                Clear
              </button>
            </div>

            {savedPaths.length > 0 && (
              <div className="study-small-info">
                <strong>Saved files:</strong>
                {savedPaths.map((path, index) => (
                  <span key={`${path}-${index}`}>{path}</span>
                ))}
              </div>
            )}
          </div>

          <div className="study-card study-tools-card">
            <div className="study-card-title">
              <div className="study-card-icon">
                <Layers size={22} />
              </div>

              <div>
                <h2>Study Tools</h2>
                <p>Use your uploaded notes for revision and interview prep.</p>
              </div>
            </div>

            <div className="study-tool-grid">
              <ToolButton
                title="Chat"
                desc="Ask questions from notes"
                icon={<MessageSquare size={21} />}
                active={activeTool === "chat"}
                onClick={() => setActiveTool("chat")}
              />

              <ToolButton
                title="Summary"
                desc="Summarize uploaded notes"
                icon={<BookOpen size={21} />}
                active={activeTool === "summary"}
                loading={summarizing}
                onClick={handleSummarizeNotes}
              />

              <ToolButton
                title="Questions"
                desc="Generate viva questions"
                icon={<FileQuestion size={21} />}
                active={activeTool === "questions"}
                loading={generatingQuestions}
                onClick={handleGenerateQuestions}
              />
            </div>

            <button
              type="button"
              onClick={handleResetOnlyUi}
              className="study-secondary-btn study-full-btn"
            >
              <RotateCcw size={17} />
              Clear Chat / Tool Output
            </button>
          </div>
        </section>

        <section className="study-notes-right">
          {(error || successMessage) && (
            <div
              className={`study-alert ${
                error ? "study-alert-error" : "study-alert-success"
              }`}
            >
              {error ? <AlertCircle size={18} /> : <CheckCircle2 size={18} />}
              <span>{error || successMessage}</span>

              <button
                type="button"
                onClick={clearAlerts}
                className="study-alert-close"
              >
                ×
              </button>
            </div>
          )}

          {activeTool === "chat" && (
            <div className="study-card study-chat-card">
              <div className="study-output-header">
                <div>
                  <h2>Ask Questions From Notes</h2>
                  <p>
                    Ask anything from uploaded PDFs. Answers include source chunks.
                  </p>
                </div>

                <span className={ragReady ? "study-pill-ready" : "study-pill-off"}>
                  {ragReady ? "RAG Ready" : "Upload notes first"}
                </span>
              </div>

              <div className="study-chat-list">
                {chatMessages.length === 0 ? (
                  <div className="study-empty-state">
                    <MessageSquare size={42} />
                    <h3>No chat yet</h3>
                    <p>
                      Upload notes, then ask questions like “Explain this topic in
                      simple points.”
                    </p>
                  </div>
                ) : (
                  chatMessages.map((message, index) => (
                    <ChatBubble
                      key={`${message.role}-${index}`}
                      role={message.role}
                      content={message.content}
                      sources={message.sources}
                    />
                  ))
                )}

                {asking && (
                  <div className="study-thinking">
                    <Loader2 size={18} className="study-spin" />
                    Thinking from your notes...
                  </div>
                )}

                <div ref={chatEndRef}></div>
              </div>

              <form onSubmit={handleAskQuestion} className="study-chat-form">
                <input
                  type="text"
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder={
                    ragReady
                      ? "Ask from your notes..."
                      : "Upload and process PDFs first..."
                  }
                  disabled={!ragReady || asking}
                />

                <button type="submit" disabled={!ragReady || asking}>
                  {asking ? (
                    <Loader2 size={19} className="study-spin" />
                  ) : (
                    <Send size={19} />
                  )}
                </button>
              </form>
            </div>
          )}

          {activeTool === "summary" && (
            <OutputPanel
              title="Notes Summary"
              subtitle="Generated study-friendly summary from your uploaded notes."
              loading={summarizing}
              emptyTitle="No summary generated yet"
              emptyText="Click the Summary tool button to generate summary."
              content={summaryAnswer}
              icon={<BookOpen size={42} />}
            />
          )}

          {activeTool === "questions" && (
            <OutputPanel
              title="Generated Questions"
              subtitle="Viva and interview questions generated from your notes."
              loading={generatingQuestions}
              emptyTitle="No questions generated yet"
              emptyText="Click the Questions tool button to generate questions."
              content={generatedQuestionsAnswer}
              icon={<HelpCircle size={42} />}
            />
          )}

          {activeTool === "flashcards" && (
            <div className="study-card study-flashcard-card">
              <div className="study-output-header">
                <div>
                  <h2>MCQ Flashcards</h2>
                  <p>Practice revision cards generated from uploaded notes.</p>
                </div>

                {flashcards.length > 0 && (
                  <span className="study-pill-ready">
                    {flashcardIndex + 1} / {flashcards.length}
                  </span>
                )}
              </div>

              {generatingFlashcards ? (
                <div className="study-loading-output">
                  <Loader2 size={34} className="study-spin" />
                  <p>Generating flashcards...</p>
                </div>
              ) : !currentFlashcard ? (
                <div className="study-empty-state">
                  <Brain size={42} />
                  <h3>No flashcards yet</h3>
                  <p>Click the Flashcards tool button to generate MCQ cards.</p>

                  {flashcardsRaw && (
                    <details className="study-raw-output">
                      <summary>Raw output</summary>
                      <pre>{flashcardsRaw}</pre>
                    </details>
                  )}
                </div>
              ) : (
                <div className="study-flashcard-box">
                  <div className="study-flashcard-question">
                    <span>Question</span>
                    <h3>{currentFlashcard.question}</h3>
                  </div>

                  <div className="study-flashcard-options">
                    {["A", "B", "C", "D"].map((option) => (
                      <button
                        key={option}
                        type="button"
                        onClick={() => setSelectedFlashcardOption(option)}
                        className={`study-flashcard-option ${
                          selectedFlashcardOption === option
                            ? "study-flashcard-option-selected"
                            : ""
                        } ${
                          flashcardAnswerChecked &&
                          option === currentFlashcard.correct
                            ? "study-flashcard-option-correct"
                            : ""
                        } ${
                          flashcardAnswerChecked &&
                          selectedFlashcardOption === option &&
                          option !== currentFlashcard.correct
                            ? "study-flashcard-option-wrong"
                            : ""
                        }`}
                      >
                        <strong>{option}</strong>
                        <span>{currentFlashcard.options?.[option]}</span>
                      </button>
                    ))}
                  </div>

                  <div className="study-flashcard-actions">
                    <button
                      type="button"
                      onClick={previousFlashcard}
                      disabled={flashcardIndex === 0}
                      className="study-secondary-btn"
                    >
                      <ChevronLeft size={17} />
                      Previous
                    </button>

                    <button
                      type="button"
                      onClick={checkFlashcardAnswer}
                      disabled={!selectedFlashcardOption}
                      className="study-primary-btn study-check-btn"
                    >
                      Check Answer
                    </button>

                    <button
                      type="button"
                      onClick={nextFlashcard}
                      disabled={flashcardIndex >= flashcards.length - 1}
                      className="study-secondary-btn"
                    >
                      Next
                      <ChevronRight size={17} />
                    </button>
                  </div>

                  {flashcardAnswerChecked && (
                    <div
                      className={`study-flashcard-result ${
                        isCurrentAnswerCorrect
                          ? "study-flashcard-result-correct"
                          : "study-flashcard-result-wrong"
                      }`}
                    >
                      <h4>
                        {isCurrentAnswerCorrect
                          ? "Correct answer!"
                          : `Wrong answer. Correct option is ${currentFlashcard.correct}.`}
                      </h4>

                      {currentFlashcard.answer && (
                        <p>
                          <strong>Answer:</strong> {currentFlashcard.answer}
                        </p>
                      )}

                      {currentFlashcard.explanation && (
                        <p>
                          <strong>Explanation:</strong>{" "}
                          {currentFlashcard.explanation}
                        </p>
                      )}

                      {currentFlashcard.source && (
                        <small>Source: {currentFlashcard.source}</small>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

function ToolButton({ title, desc, icon, active, loading, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`study-tool-btn ${active ? "study-tool-btn-active" : ""}`}
    >
      <div className="study-tool-icon">
        {loading ? <Loader2 size={21} className="study-spin" /> : icon}
      </div>

      <div>
        <strong>{title}</strong>
        <span>{desc}</span>
      </div>
    </button>
  );
}

function StatusItem({ label, value, good = false }) {
  return (
    <div className="study-status-item">
      <span>{label}</span>
      <strong className={good ? "study-status-good" : ""}>{value}</strong>
    </div>
  );
}

function ChatBubble({ role, content, sources = [] }) {
  const isUser = role === "user";

  return (
    <div
      className={`study-chat-row ${
        isUser ? "study-chat-row-user" : "study-chat-row-assistant"
      }`}
    >
      <div
        className={`study-chat-avatar ${
          isUser ? "study-chat-avatar-user" : "study-chat-avatar-ai"
        }`}
      >
        {isUser ? "Y" : "AI"}
      </div>

      <div
        className={`study-chat-bubble ${
          isUser ? "study-chat-user" : "study-chat-assistant"
        }`}
      >
        <div className="study-chat-name">
          {isUser ? "You" : "AI Study Assistant"}
        </div>

        <div className="study-markdown-output">
          {renderStudyMarkdown(content)}
        </div>

        {!isUser && sources.length > 0 && (
          <details className="study-source-details">
            <summary>Sources ({sources.length})</summary>

            <div className="study-source-list">
              {sources.map((source, index) => (
                <div key={index} className="study-source-item">
                  <strong>
                    {source.pdf_name || "PDF"}{" "}
                    {source.page ? `• Page ${source.page}` : ""}
                  </strong>

                  {source.content_preview && <p>{source.content_preview}</p>}
                </div>
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  );
}

function OutputPanel({
  title,
  subtitle,
  loading,
  emptyTitle,
  emptyText,
  content,
  icon,
}) {
  return (
    <div className="study-card study-output-card">
      <div className="study-output-header">
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
      </div>

      {loading ? (
        <div className="study-loading-output">
          <Loader2 size={34} className="study-spin" />
          <p>Generating...</p>
        </div>
      ) : content ? (
        <div className="study-markdown-output study-large-output">
          {renderStudyMarkdown(content)}
        </div>
      ) : (
        <div className="study-empty-state">
          {icon}
          <h3>{emptyTitle}</h3>
          <p>{emptyText}</p>
        </div>
      )}
    </div>
  );
}

function renderInlineBold(text) {
  if (!text) {
    return null;
  }

  const parts = String(text).split(/(\*\*.*?\*\*)/g);

  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={index} className="study-inline-bold">
          {part.replace(/\*\*/g, "")}
        </strong>
      );
    }

    return <React.Fragment key={index}>{part}</React.Fragment>;
  });
}

function cleanMarkdownLine(line) {
  return String(line || "")
    .replace(/^[-*+]\s+/, "")
    .replace(/^\d+\.\s+/, "")
    .trim();
}

function isHeadingLine(line) {
  const cleanLine = String(line || "").trim();

  if (/^\*\*.+\*\*:?\s*$/.test(cleanLine)) {
    return true;
  }

  if (/^[A-Z][A-Za-z0-9 /&().,-]+:\s*$/.test(cleanLine)) {
    return true;
  }

  return false;
}

function getHeadingText(line) {
  return String(line || "")
    .replace(/\*\*/g, "")
    .replace(/:$/, "")
    .trim();
}

function isBulletLine(line) {
  const cleanLine = String(line || "").trim();

  return /^[-*+]\s+/.test(cleanLine) || /^\d+\.\s+/.test(cleanLine);
}

function renderStudyMarkdown(content) {
  if (!content) {
    return null;
  }

  const lines = String(content)
    .replace(/\r/g, "")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  const elements = [];
  let listItems = [];

  const flushList = () => {
    if (listItems.length > 0) {
      elements.push(
        <ul key={`list-${elements.length}`} className="study-output-list">
          {listItems.map((item, index) => (
            <li key={index}>{renderInlineBold(item)}</li>
          ))}
        </ul>
      );

      listItems = [];
    }
  };

  lines.forEach((line, index) => {
    if (isHeadingLine(line)) {
      flushList();

      elements.push(
        <h3 key={`heading-${index}`} className="study-output-heading">
          {getHeadingText(line)}
        </h3>
      );

      return;
    }

    if (isBulletLine(line)) {
      listItems.push(cleanMarkdownLine(line));
      return;
    }

    flushList();

    elements.push(
      <p key={`para-${index}`} className="study-output-paragraph">
        {renderInlineBold(line)}
      </p>
    );
  });

  flushList();

  return elements;
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