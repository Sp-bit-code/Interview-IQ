import React, { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router";
import {
  ArrowLeft,
  Brain,
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
  uploadNotes,
  generateFlashcards,
  getSessionSummary,
} from "../lib/ragApi";

import { useRagStore } from "../store/useRagStore";

import "./Flashcards.css";

export default function Flashcards() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const {
    backendStatus,
    backendError,

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

  const [flashcardFiles, setFlashcardFiles] = useState([]);
  const [flashcardSessionId, setFlashcardSessionId] = useState("");
  const [flashcardRagReady, setFlashcardRagReady] = useState(false);
  const [flashcardSessionSummary, setFlashcardSessionSummary] = useState(null);
  const [flashcardVectorStatus, setFlashcardVectorStatus] = useState(null);
  const [uploadingFlashcardDocs, setUploadingFlashcardDocs] = useState(false);
  const [flashcardCount, setFlashcardCount] = useState(10);

  const totalPdfs = flashcardSessionSummary?.total_pdfs || 0;
  const totalChunks = flashcardSessionSummary?.total_chunks || 0;
  const totalVectors = flashcardVectorStatus?.total_vectors || 0;
  const selectedFilesCount = flashcardFiles?.length || 0;

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
    const loadExistingFlashcardSession = async () => {
      if (!flashcardSessionId) {
        return;
      }

      try {
        const result = await getSessionSummary(flashcardSessionId);

        setFlashcardSessionSummary(result?.session_summary || null);
        setFlashcardVectorStatus(result?.vector_status || null);
        setFlashcardRagReady(Boolean(result?.rag_ready));
      } catch (err) {
        console.warn("Could not load flashcard RAG session:", err);
      }
    };

    loadExistingFlashcardSession();
  }, [flashcardSessionId]);

  const handleFlashcardFileChange = (event) => {
    const files = Array.from(event.target.files || []);

    if (!files.length) {
      return;
    }

    const invalidFiles = files.filter((file) => {
      return file.type !== "application/pdf" && !file.name.endsWith(".pdf");
    });

    if (invalidFiles.length > 0) {
      setError("Please upload only PDF files for flashcards.");
      return;
    }

    setFlashcardFiles(files);
    clearError();
    clearSuccessMessage();
  };

  const handleUploadFlashcardDocs = async () => {
    if (!flashcardFiles || flashcardFiles.length === 0) {
      setError("Please select at least one PDF file for flashcards.");
      return;
    }

    try {
      clearAlerts();
      clearFlashcards();
      setUploadingFlashcardDocs(true);

      const result = await uploadNotes({
        files: flashcardFiles,
        sessionId: flashcardSessionId || undefined,
      });

      if (!result?.success) {
        throw new Error(result?.message || "Flashcard PDF upload failed.");
      }

      const newSessionId = result.session_id || flashcardSessionId;

      setFlashcardSessionId(newSessionId);
      setFlashcardSessionSummary(result.session_summary || null);
      setFlashcardVectorStatus(result.vector_status || null);
      setFlashcardRagReady(Boolean(result?.vector_status?.ready));

      setSuccessMessage(
        result?.message ||
          "Flashcard PDFs uploaded, processed, and indexed successfully."
      );

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      console.error("Flashcard PDF upload/process error:", err);

      setError(
        err?.message ||
          "Failed to upload/process flashcard PDFs. Check backend and try again."
      );
    } finally {
      setUploadingFlashcardDocs(false);
    }
  };

  const handleGenerateFlashcards = async () => {
    if (!flashcardSessionId || !flashcardRagReady) {
      setError("Please upload and process PDF docs for flashcards first.");
      return;
    }

    try {
      clearAlerts();
      clearFlashcards();
      setGeneratingFlashcards(true);

      const targetCount = Number(flashcardCount) || 10;
      const collectedFlashcards = [];
      const rawOutputs = [];

      let attempts = 0;
      const maxAttempts = Math.max(2, Math.ceil(targetCount / 5) + 2);

      while (collectedFlashcards.length < targetCount && attempts < maxAttempts) {
        attempts += 1;

        const remainingCount = targetCount - collectedFlashcards.length;

        const result = await generateFlashcards(flashcardSessionId, remainingCount);

        if (result?.raw) {
          rawOutputs.push(result.raw);
        }

        const batchCards = Array.isArray(result?.flashcards)
          ? result.flashcards
          : [];

        if (batchCards.length === 0) {
          break;
        }

        collectedFlashcards.push(...batchCards);
      }

      const finalCards = shuffleFlashcardOptions(
        collectedFlashcards.slice(0, targetCount)
      );

      setFlashcards(finalCards, rawOutputs.join("\n\n"));

      if (!finalCards || finalCards.length === 0) {
        setError(
          "Flashcards were generated but could not be parsed into MCQ format."
        );
      } else if (finalCards.length < targetCount) {
        setSuccessMessage(
          `${finalCards.length} flashcards generated. Backend returned fewer cards than selected.`
        );
      } else {
        setSuccessMessage(`${finalCards.length} flashcards generated.`);
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

  const handleResetFlashcardSession = () => {
    clearFlashcards();
    clearError();
    clearSuccessMessage();

    setFlashcardFiles([]);
    setFlashcardSessionId("");
    setFlashcardRagReady(false);
    setFlashcardSessionSummary(null);
    setFlashcardVectorStatus(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
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
          <p>
            Upload PDF docs and generate MCQ flashcards using a separate RAG
            session.
          </p>
        </div>

        <Link to="/" className="flashcards-header-link">
          Home
          <ExternalLink size={16} />
        </Link>
      </header>

      <main className="flashcards-main">
        <section className="flashcards-sidebar">
          <div className="flashcards-card">
            <div className="flashcards-card-title">
              <div className="flashcards-card-icon">
                <UploadCloud size={22} />
              </div>

              <div>
                <h2>Upload PDF Docs</h2>
                <p>
                  This upload is separate from Study from Notes and creates a
                  separate flashcard RAG session.
                </p>
              </div>
            </div>

            <label className="flashcards-upload-box">
              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf"
                multiple
                onChange={handleFlashcardFileChange}
              />

              <UploadCloud size={42} />
              <strong>Click to select PDF docs</strong>
              <span>Only PDF files are supported for flashcards</span>
            </label>

            {selectedFilesCount > 0 && (
              <div className="flashcards-selected-files">
                {flashcardFiles.map((file, index) => (
                  <div
                    key={`${file.name}-${index}`}
                    className="flashcards-selected-file"
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
              onClick={handleUploadFlashcardDocs}
              disabled={uploadingFlashcardDocs || selectedFilesCount === 0}
              className="flashcards-primary-btn"
            >
              {uploadingFlashcardDocs ? (
                <>
                  <Loader2 size={19} className="flashcards-spin" />
                  Processing PDFs...
                </>
              ) : (
                <>
                  <Sparkles size={19} />
                  Upload & Process Docs
                </>
              )}
            </button>
          </div>

          <div className="flashcards-card">
            <div className="flashcards-card-title">
              <div className="flashcards-card-icon">
                <Brain size={22} />
              </div>

              <div>
                <h2>Flashcard Setup</h2>
                <p>
                  Select how many cards you want to generate from the uploaded
                  PDF docs.
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
                value={flashcardRagReady ? "Yes" : "No"}
                good={flashcardRagReady}
              />

              <StatusItem label="PDFs" value={String(totalPdfs)} />
              <StatusItem label="Chunks" value={String(totalChunks)} />
              <StatusItem label="Vectors" value={String(totalVectors)} />
              <StatusItem
                label="Session"
                value={
                  flashcardSessionId ? shortSession(flashcardSessionId) : "None"
                }
              />
            </div>

            <div className="flashcards-count-box">
              <label htmlFor="flashcardCount">How many flashcards?</label>

              <select
                id="flashcardCount"
                value={flashcardCount}
                onChange={(event) =>
                  setFlashcardCount(Number(event.target.value))
                }
                className="flashcards-count-select"
              >
                <option value={5}>5 cards</option>
                <option value={10}>10 cards</option>
                <option value={15}>15 cards</option>
                <option value={20}>20 cards</option>
                <option value={25}>25 cards</option>
                <option value={30}>30 cards</option>
              </select>
            </div>

            {backendError && (
              <div className="flashcards-alert flashcards-alert-error">
                <AlertCircle size={17} />
                <span>{backendError}</span>
              </div>
            )}

            {!flashcardSessionId || !flashcardRagReady ? (
              <div className="flashcards-note-box">
                <UploadCloud size={26} />
                <h3>Upload PDF docs first</h3>
                <p>
                  Upload your PDFs here. This page creates a separate RAG
                  session only for flashcard generation.
                </p>
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
                    Generate {flashcardCount} Flashcards
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

            <button
              type="button"
              onClick={handleResetFlashcardSession}
              disabled={
                uploadingFlashcardDocs ||
                generatingFlashcards ||
                (!flashcardSessionId && !flashcardFiles.length)
              }
              className="flashcards-secondary-btn"
            >
              <RotateCcw size={17} />
              Reset Flashcard Session
            </button>
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
                <p>This may take a few seconds depending on your PDF docs.</p>
              </div>
            ) : !currentFlashcard ? (
              <div className="flashcards-empty-state">
                <Brain size={54} />
                <h3>No flashcards generated yet</h3>
                <p>
                  Upload PDF docs on this page, select how many cards you want,
                  and generate flashcards from this separate RAG session.
                </p>

                <div className="flashcards-empty-actions">
                  <button
                    type="button"
                    onClick={handleGenerateFlashcards}
                    disabled={!flashcardSessionId || !flashcardRagReady}
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

function shuffleFlashcardOptions(cards) {
  if (!Array.isArray(cards)) {
    return [];
  }

  return cards.map((card, cardIndex) => {
    const originalOptions = card?.options || {};
    const originalCorrect = String(card?.correct || "C").trim().toUpperCase();
    const correctText = originalOptions[originalCorrect];

    const optionValues = ["A", "B", "C", "D"]
      .map((key) => originalOptions[key])
      .filter((value) => value !== undefined && value !== null && value !== "");

    if (optionValues.length < 4 || !correctText) {
      return card;
    }

    const shuffledValues = deterministicShuffle(optionValues, cardIndex);
    const letters = ["A", "B", "C", "D"];

    const newOptions = {};
    let newCorrect = "A";

    letters.forEach((letter, index) => {
      newOptions[letter] = shuffledValues[index];

      if (shuffledValues[index] === correctText) {
        newCorrect = letter;
      }
    });

    return {
      ...card,
      options: newOptions,
      correct: newCorrect,
    };
  });
}

function deterministicShuffle(items, seed) {
  const shuffled = [...items];

  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const swapIndex = (seed + index * 7 + 3) % (index + 1);
    const temp = shuffled[index];

    shuffled[index] = shuffled[swapIndex];
    shuffled[swapIndex] = temp;
  }

  return shuffled;
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