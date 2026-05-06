import React, { useEffect, useRef, useState } from "react";
import {
  Mic,
  MicOff,
  Eye,
  BadgeInfo,
  PhoneOff,
  Cpu,
  Volume2,
  Clock,
  Send,
  Keyboard,
  Square,
  Loader2,
} from "lucide-react";

import { useInterviewStore } from "../src/store/useInterviewStore";
import "./InterviewScreen.css";

export function InterviewScreen({
  videoRef,
  transcript = [],
  liveFeedback = [],
  startTime,
  isSpeaking,
  isRecording,
  isProcessing,
  audioLevel = 0,
  onEndInterview,
  onStopRecording,
  onManualSubmit,
}) {
  const { track, difficulty } = useInterviewStore();

  const transcriptEndRef = useRef(null);
  const inputRef = useRef(null);

  const [elapsed, setElapsed] = useState(0);
  const [showEndConfirm, setShowEndConfirm] = useState(false);
  const [manualText, setManualText] = useState("");
  const [showTextInput, setShowTextInput] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);

  useEffect(() => {
    if (!startTime) return;

    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  useEffect(() => {
    let interval;

    if (isRecording) {
      setRecordingTime(0);

      interval = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } else {
      setRecordingTime(0);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRecording]);

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [transcript]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;

    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  };

  const handleTextSubmit = (event) => {
    event?.preventDefault();

    const finalText = manualText.trim();

    if (!finalText) return;

    onManualSubmit(finalText);
    setManualText("");
  };

  const questionNumber = transcript.filter(
    (message) => message.speaker === "ai"
  ).length;

  const generateBars = (count) => {
    return Array.from({ length: count }).map((_, index) => {
      const barHeight = isRecording
        ? Math.max(4, audioLevel * 40 * (0.5 + Math.random() * 0.5))
        : 4;

      return (
        <div
          key={index}
          className="interview-recording-bar"
          style={{
            height: `${barHeight}px`,
          }}
        />
      );
    });
  };

  return (
    <div className="interview-screen">
      <header className="interview-header">
        <div className="interview-header-left">
          <div className="interview-ai-badge">
            <Cpu size={15} />
            <span>Gemini AI</span>
          </div>

          <div className="interview-meta-pills">
            <span>{track || "Track"}</span>
            <span>{difficulty || "Level"}</span>
          </div>

          {questionNumber > 0 && (
            <div className="interview-question-pill">Q{questionNumber}/15</div>
          )}
        </div>

        <div className="interview-header-right">
          <StatusBadge
            isSpeaking={isSpeaking}
            isRecording={isRecording}
            isProcessing={isProcessing}
            recordingTime={recordingTime}
            formatTime={formatTime}
          />

          <div className="interview-main-timer">
            <Clock size={15} />
            <span>{formatTime(elapsed)}</span>
          </div>
        </div>
      </header>

      <main className="interview-main">
        <section className="interview-camera-column">
          <div className="interview-camera-box">
            <video
              ref={videoRef}
              autoPlay
              muted
              playsInline
              className="interview-video"
            />

            <div className="interview-live-badge">
              <span></span>
              LIVE
            </div>

            {isSpeaking && (
              <div className="interview-ai-visualizer">
                {Array.from({ length: 24 }).map((_, index) => (
                  <div
                    key={index}
                    className="interview-audio-bar interview-audio-bar-secondary"
                    style={{
                      animationDelay: `${index * 0.08}s`,
                      animationDuration: `${0.5 + Math.random() * 0.5}s`,
                    }}
                  />
                ))}
              </div>
            )}

            {isRecording && (
              <div className="interview-recording-overlay">
                <div className="interview-recording-bars">
                  {generateBars(32)}
                </div>

                <div className="interview-recording-pill">
                  <span></span>
                  <strong>Recording — speak your answer</strong>
                </div>
              </div>
            )}

            {isProcessing && (
              <div className="interview-processing-overlay">
                <div className="interview-processing-pill">
                  <Loader2 size={17} />
                  <strong>Transcribing your answer with AI...</strong>
                </div>
              </div>
            )}
          </div>
        </section>

        <section className="interview-panel-column">
          <div className="interview-coaching-card">
            <h2>
              <Eye size={17} />
              Real-Time AI Coaching
            </h2>

            <div className="interview-feedback-list">
              {liveFeedback.length === 0 ? (
                <div className="interview-empty-feedback">
                  <BadgeInfo size={26} />
                  <p>
                    Posture and eye contact coaching tips will appear here.
                  </p>
                </div>
              ) : (
                liveFeedback.map((feedback, index) => (
                  <div key={index} className="interview-feedback-item">
                    <span>💡 Tip</span>
                    <p>{feedback}</p>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="interview-transcript-card">
            <h2>
              <Mic size={17} />
              Live Transcript
              <span>{transcript.length} msgs</span>
            </h2>

            <div className="interview-transcript-list">
              {transcript.length === 0 ? (
                <div className="interview-empty-transcript">
                  <div className="interview-small-spinner"></div>
                  <p>Waiting for the interview to begin...</p>
                </div>
              ) : (
                transcript.map((message, index) => (
                  <div
                    key={index}
                    className={`interview-message ${
                      message.speaker === "user"
                        ? "interview-message-user"
                        : "interview-message-ai"
                    }`}
                  >
                    <span className="interview-message-label">
                      {message.speaker === "user" ? "🎤 You" : "🤖 AI Coach"}
                    </span>

                    <div className="interview-message-bubble">
                      {message.text}
                    </div>
                  </div>
                ))
              )}

              <div ref={transcriptEndRef} />
            </div>
          </div>
        </section>
      </main>

      <footer className="interview-footer">
        <div className="interview-footer-left">
          <span>
            <strong>{questionNumber}</strong>/15 questions
          </span>
        </div>

        <div className="interview-footer-center">
          {isRecording && (
            <button
              type="button"
              onClick={onStopRecording}
              className="interview-submit-answer-btn"
            >
              <Square size={17} />
              <span>Submit Answer</span>
            </button>
          )}

          {isProcessing && (
            <div className="interview-footer-processing">
              <Loader2 size={17} />
              <span>Processing your answer...</span>
            </div>
          )}

          {isSpeaking && (
            <div className="interview-footer-speaking">
              <Volume2 size={17} />
              <span>AI is speaking...</span>
            </div>
          )}

          {!isRecording && !isProcessing && !isSpeaking && (
            <>
              {showTextInput ? (
                <form
                  onSubmit={handleTextSubmit}
                  className="interview-text-form"
                >
                  <input
                    ref={inputRef}
                    type="text"
                    value={manualText}
                    onChange={(event) => setManualText(event.target.value)}
                    placeholder="Type answer..."
                  />

                  <button type="submit" disabled={!manualText.trim()}>
                    <Send size={17} />
                  </button>
                </form>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    setShowTextInput(true);

                    setTimeout(() => {
                      inputRef.current?.focus();
                    }, 50);
                  }}
                  className="interview-type-toggle"
                >
                  <Keyboard size={15} />
                  <span>Type instead</span>
                </button>
              )}
            </>
          )}
        </div>

        <div className="interview-footer-right">
          {showEndConfirm ? (
            <div className="interview-end-confirm">
              <button
                type="button"
                onClick={() => {
                  setShowEndConfirm(false);
                  onEndInterview();
                }}
                className="interview-end-yes"
              >
                Yes, End
              </button>

              <button
                type="button"
                onClick={() => setShowEndConfirm(false)}
                className="interview-end-no"
              >
                No
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => setShowEndConfirm(true)}
              className="interview-end-btn"
            >
              <PhoneOff size={15} />
              <span>End Interview</span>
            </button>
          )}
        </div>
      </footer>
    </div>
  );
}

function StatusBadge({
  isSpeaking,
  isRecording,
  isProcessing,
  recordingTime,
  formatTime,
}) {
  if (isSpeaking) {
    return (
      <div className="interview-status-badge interview-status-speaking">
        <Volume2 size={15} />
        <span>AI Speaking</span>

        <div className="interview-status-bars">
          {Array.from({ length: 4 }).map((_, index) => (
            <div
              key={index}
              className="interview-audio-bar interview-audio-bar-small"
              style={{
                animationDelay: `${index * 0.15}s`,
              }}
            />
          ))}
        </div>
      </div>
    );
  }

  if (isRecording) {
    return (
      <div className="interview-status-badge interview-status-recording">
        <div className="interview-status-dot"></div>
        <span>Recording {formatTime(recordingTime)}</span>
      </div>
    );
  }

  if (isProcessing) {
    return (
      <div className="interview-status-badge interview-status-processing">
        <Loader2 size={15} />
        <span>Processing...</span>
      </div>
    );
  }

  return (
    <div className="interview-status-badge interview-status-waiting">
      <MicOff size={15} />
      <span>Waiting</span>
    </div>
  );
}

export default InterviewScreen;