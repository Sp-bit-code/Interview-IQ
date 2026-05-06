import React, { useEffect, useMemo } from "react";
import { Link, useNavigate } from "react-router";
import {
  ArrowLeft,
  Brain,
  BookOpen,
  Loader2,
  AlertCircle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  Sparkles,
  ExternalLink,
  FileText,
  UploadCloud,
} from "lucide-react";

import {
  checkRagBackendHealth,
  generateFlashcards,
  getSessionSummary,
} from "../lib/ragApi";

import { useRagStore } from "../store/useRagStore";

import "./Flashcards.css";

export default function Flashcards() {
  const navigate = useNavigate();

  const {
    backendStatus,
    backendError,

    sessionId,
    ragReady,
    sessionSummary,
    vectorStatus,

    generatingFlashcards,

    flashcards,
    flashcardsRaw,
    flashcardIndex,
    selectedFlashcardOption,
    flashcardAnswerChecked,

    error,
    successMessage,

    setBackendStatus,
    setBackendError,

    setSessionData,

    setGeneratingFlashcards,
    setFlashcards,
    setFlashcardIndex,
    nextFlashcard,
    previousFlashcard,
    setSelectedFlashcardOption,
    checkFlashcardAnswer,
    resetFlashcardAnswer,
    clearFlashcards,

    setError,
    clearError,
    setSuccessMessage,
    clearSuccessMessage,
    clearAlerts,
  } = useRagStore();

  const totalPdfs = sessionSummary?.total_pdfs || 0;
  const totalChunks = sessionSummary?.total_chunks || 0;
  const totalVectors = vectorStatus?.total_vectors || 0;

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

  const progressPercent = useMemo(() => {
    if (!flashcards || flashcards.length === 0) {
      return 0;
    }

    return Math.round(((flashcardIndex + 1) / flashcards.length) * 100);
  }, [flashcards, flashcardIndex]);

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

  const handleGenerateFlashcards = async () => {
    if (!sessionId || !ragReady) {
      setError("Please upload and process notes first in Study from Notes.");
      return;
    }

    try {
      clearAlerts();
      setGeneratingFlashcards(true);

      const result = await generateFlashcards(sessionId);

      setFlashcards(result?.flashcards || [], result?.raw || "");

      if (!result?.flashcards || result.flashcards.length === 0) {
        setError(
          "Flashcards were generated but could not be parsed into MCQ format."
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

  const handleClearFlashcards = () => {
    clearFlashcards();
    clearError();
    clearSuccessMessage();
  };

  return (
    <div className="flashcards-page">
      <div className="flashcards-bg flashcards-bg-one"></div>
      <div className="flashcards-bg flashcards-bg-two"></div>

      <header className="flashcards-header">
        <button
          type="button"
          onClick={() => navigate("/dashboard")}
          className="flashcards-back-btn"
        >
          <ArrowLeft size={18} />
          <span>Dashboard</span>
        </button>

        <div className="flashcards-title-box">
          <h1>Generate Flashcards</h1>
          <p>Practice MCQ flashcards generated from your uploaded PDF notes.</p>
        </div>

        <Link to="/study-notes" className="flashcards-header-link">
          Study from Notes
          <ExternalLink size={16} />
        </Link>
      </header>

      <main className="flashcards-main">
        <section className="flashcards-sidebar">
          <div className="flashcards-card">
            <div className="flashcards-card-title">
              <div className="flashcards-card-icon">
                <Brain size={22} />
              </div>

              <div>
                <h2>Flashcard Setup</h2>
                <p>
                  Flashcards use the same RAG session from Study from Notes.
                </p>
              </div>
            </div>

            <div className="flashcards-status-grid">
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
                label="Session"
                value={sessionId ? shortSession(sessionId) : "None"}
              />
            </div>

            {backendError && (
              <div className="flashcards-alert flashcards-alert-error">
                <AlertCircle size={17} />
                <span>{backendError}</span>
              </div>
            )}

            {!sessionId || !ragReady ? (
              <div className="flashcards-note-box">
                <UploadCloud size={26} />
                <h3>Upload notes first</h3>
                <p>
                  Go to Study from Notes, upload PDF notes, then come back here
                  to generate flashcards.
                </p>

                <Link to="/study-notes">
                  Open Study from Notes
                  <ExternalLink size={15} />
                </Link>
              </div>
            ) : (
              <button
                type="button"
                onClick={handleGenerateFlashcards}
                disabled={generatingFlashcards}
                className="flashcards-primary-btn"
              >
                {generatingFlashcards ? (
                  <>
                    <Loader2 size={19} className="flashcards-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles size={19} />
                    Generate Flashcards
                  </>
                )}
              </button>
            )}

            <button
              type="button"
              onClick={handleClearFlashcards}
              disabled={!flashcards.length && !flashcardsRaw}
              className="flashcards-secondary-btn"
            >
              <RotateCcw size={17} />
              Clear Flashcards
            </button>
          </div>

          <div className="flashcards-card">
            <div className="flashcards-card-title">
              <div className="flashcards-card-icon">
                <FileText size={22} />
              </div>

              <div>
                <h2>How it works</h2>
                <p>Simple RAG flashcard generation flow.</p>
              </div>
            </div>

            <div className="flashcards-steps">
              <StepItem number="1" text="Upload PDF notes in Study from Notes." />
              <StepItem number="2" text="Backend extracts and chunks text." />
              <StepItem number="3" text="ChromaDB stores note vectors." />
              <StepItem number="4" text="Groq generates MCQ flashcards." />
            </div>
          </div>
        </section>

        <section className="flashcards-content">
          {(error || successMessage) && (
            <div
              className={`flashcards-alert ${
                error ? "flashcards-alert-error" : "flashcards-alert-success"
              }`}
            >
              {error ? <AlertCircle size={18} /> : <CheckCircle2 size={18} />}
              <span>{error || successMessage}</span>

              <button
                type="button"
                onClick={clearAlerts}
                className="flashcards-alert-close"
              >
                ×
              </button>
            </div>
          )}

          <div className="flashcards-card flashcards-practice-card">
            <div className="flashcards-output-header">
              <div>
                <h2>Practice Flashcards</h2>
                <p>
                  Select an option, check your answer, and move to the next card.
                </p>
              </div>

              {flashcards.length > 0 && (
                <span className="flashcards-pill-ready">
                  {flashcardIndex + 1} / {flashcards.length}
                </span>
              )}
            </div>

            {generatingFlashcards ? (
              <div className="flashcards-loading-box">
                <Loader2 size={42} className="flashcards-spin" />
                <h3>Generating flashcards...</h3>
                <p>This may take a few seconds depending on your notes.</p>
              </div>
            ) : !currentFlashcard ? (
              <div className="flashcards-empty-state">
                <Brain size={54} />
                <h3>No flashcards generated yet</h3>
                <p>
                  Generate flashcards after uploading and processing notes in
                  Study from Notes.
                </p>

                <div className="flashcards-empty-actions">
                  <Link to="/study-notes" className="flashcards-secondary-link">
                    <BookOpen size={17} />
                    Study from Notes
                  </Link>

                  <button
                    type="button"
                    onClick={handleGenerateFlashcards}
                    disabled={!sessionId || !ragReady}
                    className="flashcards-primary-small-btn"
                  >
                    <Sparkles size={17} />
                    Generate Now
                  </button>
                </div>

                {flashcardsRaw && (
                  <details className="flashcards-raw-output">
                    <summary>Raw output</summary>
                    <pre>{flashcardsRaw}</pre>
                  </details>
                )}
              </div>
            ) : (
              <div className="flashcards-practice-box">
                <div className="flashcards-progress">
                  <div
                    className="flashcards-progress-fill"
                    style={{ width: `${progressPercent}%` }}
                  ></div>
                </div>

                <div className="flashcards-question-box">
                  <span>Question {flashcardIndex + 1}</span>
                  <h3>{currentFlashcard.question}</h3>
                </div>

                <div className="flashcards-options">
                  {["A", "B", "C", "D"].map((option) => (
                    <button
                      key={option}
                      type="button"
                      onClick={() => {
                        if (!flashcardAnswerChecked) {
                          setSelectedFlashcardOption(option);
                        }
                      }}
                      className={`flashcards-option ${
                        selectedFlashcardOption === option
                          ? "flashcards-option-selected"
                          : ""
                      } ${
                        flashcardAnswerChecked &&
                        option === currentFlashcard.correct
                          ? "flashcards-option-correct"
                          : ""
                      } ${
                        flashcardAnswerChecked &&
                        selectedFlashcardOption === option &&
                        option !== currentFlashcard.correct
                          ? "flashcards-option-wrong"
                          : ""
                      }`}
                    >
                      <strong>{option}</strong>
                      <span>{currentFlashcard.options?.[option]}</span>
                    </button>
                  ))}
                </div>

                <div className="flashcards-actions">
                  <button
                    type="button"
                    onClick={previousFlashcard}
                    disabled={flashcardIndex === 0}
                    className="flashcards-secondary-btn"
                  >
                    <ChevronLeft size={17} />
                    Previous
                  </button>

                  <button
                    type="button"
                    onClick={checkFlashcardAnswer}
                    disabled={!selectedFlashcardOption}
                    className="flashcards-primary-btn flashcards-check-btn"
                  >
                    Check Answer
                  </button>

                  <button
                    type="button"
                    onClick={nextFlashcard}
                    disabled={flashcardIndex >= flashcards.length - 1}
                    className="flashcards-secondary-btn"
                  >
                    Next
                    <ChevronRight size={17} />
                  </button>
                </div>

                {flashcardAnswerChecked && (
                  <div
                    className={`flashcards-result-box ${
                      isCurrentAnswerCorrect
                        ? "flashcards-result-correct"
                        : "flashcards-result-wrong"
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

                <div className="flashcards-bottom-actions">
                  <button
                    type="button"
                    onClick={resetFlashcardAnswer}
                    className="flashcards-secondary-btn"
                  >
                    <RotateCcw size={17} />
                    Reset Current Answer
                  </button>

                  <button
                    type="button"
                    onClick={() => setFlashcardIndex(0)}
                    className="flashcards-secondary-btn"
                  >
                    Go to First Card
                  </button>
                </div>
              </div>
            )}
          </div>

          {flashcardsRaw && (
            <div className="flashcards-card flashcards-raw-card">
              <details>
                <summary>Raw Flashcard Output</summary>
                <pre>{flashcardsRaw}</pre>
              </details>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

function StatusItem({ label, value, good = false }) {
  return (
    <div className="flashcards-status-item">
      <span>{label}</span>
      <strong className={good ? "flashcards-status-good" : ""}>{value}</strong>
    </div>
  );
}

function StepItem({ number, text }) {
  return (
    <div className="flashcards-step-item">
      <span>{number}</span>
      <p>{text}</p>
    </div>
  );
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