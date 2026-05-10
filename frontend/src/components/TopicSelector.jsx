import React from "react";
import "./TopicSelector.css";

const topics = ["HR", "Technical", "General"];

export function TopicSelector({
  onSelectTopic,
  onStart,
  selectedTopic,
  isLoading,
}) {
  return (
    <div className="topic-page">
      <div className="topic-bg-glow topic-bg-glow-one"></div>
      <div className="topic-bg-glow topic-bg-glow-two"></div>
      <div className="topic-bg-grid"></div>

      <div className="topic-container">
        <div className="topic-header">
          <h1>Virtual Mock Interview System</h1>

          <p>
            CS Mini Project I. Get real-time feedback and a comprehensive report
            to ace your next interview.
          </p>
        </div>

        <div className="topic-card">
          <div className="topic-section">
            <div className="topic-step-badge">1</div>

            <div>
              <h2>Select Your Interview Topic</h2>
              <p>Choose the type of interview practice you want to start.</p>
            </div>
          </div>

          <div className="topic-grid">
            {topics.map((topic) => {
              const isSelected = selectedTopic === topic;

              return (
                <button
                  key={topic}
                  type="button"
                  onClick={() => onSelectTopic(topic)}
                  className={`topic-option ${
                    isSelected ? "topic-option-active" : ""
                  }`}
                >
                  <span>{topic}</span>

                  {topic === "HR" && (
                    <small>Behavioral and culture-fit questions</small>
                  )}

                  {topic === "Technical" && (
                    <small>Coding, concepts, and problem-solving</small>
                  )}

                  {topic === "General" && (
                    <small>Mixed standard interview questions</small>
                  )}
                </button>
              );
            })}
          </div>

          <div className="topic-divider"></div>

          <div className="topic-section">
            <div className="topic-step-badge">2</div>

            <div>
              <h2>Start the Interview</h2>
              <p>
                Please allow access to your camera and microphone when prompted.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onStart}
            disabled={!selectedTopic || isLoading}
            className="topic-start-btn"
          >
            {isLoading ? (
              <>
                <span className="topic-spinner"></span>
                Starting...
              </>
            ) : (
              "Start Interview"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default TopicSelector;