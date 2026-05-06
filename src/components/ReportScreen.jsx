import React, { useEffect, useRef, useState } from "react";
import {
  Download,
  RefreshCcw,
  Award,
  MessageSquare,
  ShieldCheck,
  UserCheck,
  Eye,
  LayoutDashboard,
  Gauge,
  TrendingUp,
  Lightbulb,
  Trophy,
  ArrowRight,
  Loader2,
} from "lucide-react";

import { useInterviewStore } from "../src/store/useInterviewStore";
import "./ReportScreen.css";

export function ReportScreen({
  report,
  onRestart,
  onDashboard,
  startTime,
}) {
  const { track, difficulty } = useInterviewStore();

  const reportContentRef = useRef(null);

  const [pdfLoading, setPdfLoading] = useState(false);

  let data = {};

  try {
    data = JSON.parse(report);
  } catch (error) {
    console.error("Failed to parse JSON report:", error);
  }

  const scores = data?.scores || {
    communication: 0,
    confidence: 0,
    bodyLanguage: 0,
    eyeContact: 0,
    speakingPace: 0,
    overall: 0,
  };

  const duration = startTime
    ? Math.round((Date.now() - startTime) / 1000)
    : 0;

  const durationStr =
    duration > 0
      ? `${Math.floor(duration / 60)}m ${duration % 60}s`
      : "N/A";

  const handleDownloadPDF = async () => {
    setPdfLoading(true);

    try {
      const html2pdf = (await import("html2pdf.js")).default;
      const element = reportContentRef.current;

      if (!element) return;

      const options = {
        margin: [10, 10, 10, 10],
        filename: `InterviewIQ_Report_${track || "Interview"}_${
          new Date().toISOString().split("T")[0]
        }.pdf`,
        image: {
          type: "jpeg",
          quality: 0.98,
        },
        html2canvas: {
          scale: 2,
          useCORS: true,
          backgroundColor: "#070b14",
        },
        jsPDF: {
          unit: "mm",
          format: "a4",
          orientation: "portrait",
        },
      };

      await html2pdf().set(options).from(element).save();
    } catch (error) {
      console.error("PDF generation failed:", error);

      const blob = new Blob([report], {
        type: "application/json",
      });

      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "interview_report.json";

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } finally {
      setPdfLoading(false);
    }
  };

  return (
    <div className="report-page">
      <div className="report-bg-glow report-bg-glow-one"></div>
      <div className="report-bg-glow report-bg-glow-two"></div>
      <div className="report-bg-grid"></div>

      <div className="report-container">
        <div ref={reportContentRef} className="report-export-area">
          {/* Header Section */}
          <section className="report-hero-card">
            <div className="report-hero-left">
              <div className="report-tags">
                <span className="report-tag report-tag-primary">
                  {track || "Interview"} Track
                </span>

                <span className="report-tag">{difficulty || "Level"}</span>

                <span className="report-tag">{durationStr}</span>

                <span className="report-tag report-tag-secondary">
                  AI Assessed
                </span>
              </div>

              <h1>Performance Report</h1>

              <p>
                {data.overallSummary ||
                  "Your interview report is ready. Review your scores, strengths, and improvement tips below."}
              </p>
            </div>

            <div className="report-overall-card">
              <span>Overall Score</span>

              <AnimatedScore value={Number(scores.overall || 0)} />

              <small>out of 10</small>
            </div>
          </section>

          {/* Score Cards */}
          <section className="report-score-grid">
            <ScoreCard
              title="Communication"
              score={Number(scores.communication || 0)}
              icon={<MessageSquare size={17} />}
            />

            <ScoreCard
              title="Confidence"
              score={Number(scores.confidence || 0)}
              icon={<Trophy size={17} />}
            />

            <ScoreCard
              title="Body Language"
              score={Number(scores.bodyLanguage || 0)}
              icon={<UserCheck size={17} />}
            />

            <ScoreCard
              title="Eye Contact"
              score={Number(scores.eyeContact || 0)}
              icon={<Eye size={17} />}
            />

            <ScoreCard
              title="Speaking Pace"
              score={Number(scores.speakingPace || 0)}
              icon={<Gauge size={17} />}
            />
          </section>

          <section className="report-main-grid">
            {/* Score Bars */}
            <div className="report-bars-section">
              <h3>
                <TrendingUp size={21} />
                Score Bars
              </h3>

              <div className="report-bars-list">
                <ScoreBar
                  title="Communication"
                  score={Number(scores.communication || 0)}
                />

                <ScoreBar
                  title="Confidence"
                  score={Number(scores.confidence || 0)}
                />

                <ScoreBar
                  title="Body Language"
                  score={Number(scores.bodyLanguage || 0)}
                />

                <ScoreBar
                  title="Eye Contact"
                  score={Number(scores.eyeContact || 0)}
                />

                <ScoreBar
                  title="Speaking Pace"
                  score={Number(scores.speakingPace || 0)}
                />
              </div>
            </div>

            {/* Detailed Analysis */}
            <div className="report-analysis-section">
              <h3>
                <Award size={21} />
                Detailed Analysis
              </h3>

              <div className="report-analysis-grid">
                <AnalysisCard
                  title="Communication"
                  text={data?.detailedAnalysis?.communication}
                />

                <AnalysisCard
                  title="Confidence"
                  text={data?.detailedAnalysis?.confidence}
                />

                <AnalysisCard
                  title="Body Language"
                  text={data?.detailedAnalysis?.bodyLanguage}
                />

                <AnalysisCard
                  title="Eye Contact"
                  text={data?.detailedAnalysis?.eyeContact}
                />

                <AnalysisCard
                  title="Speaking Pace"
                  text={data?.detailedAnalysis?.speakingPace}
                  className="report-analysis-wide"
                />
              </div>
            </div>
          </section>

          {/* Strengths */}
          {data?.strengths && data.strengths.length > 0 && (
            <section className="report-strengths-card">
              <h4>
                <ShieldCheck size={21} />
                Your Strengths
              </h4>

              <div className="report-strengths-grid">
                {data.strengths.map((strength, index) => (
                  <div key={index} className="report-strength-item">
                    <span>✓</span>
                    <p>{strength}</p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Improvement Tips */}
          {data?.improvementTips && data.improvementTips.length > 0 && (
            <section className="report-tips-card">
              <h4>
                <Lightbulb size={21} />
                Actionable Improvement Tips
              </h4>

              <div className="report-tips-list">
                {data.improvementTips.map((tip, index) => (
                  <div key={index} className="report-tip-item">
                    <span>{index + 1}</span>
                    <p>{tip}</p>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Action Buttons */}
        <div className="report-actions no-print">
          <button
            type="button"
            onClick={handleDownloadPDF}
            disabled={pdfLoading}
            className="report-action-btn report-download-btn"
          >
            {pdfLoading ? (
              <Loader2 size={21} className="report-spin-icon" />
            ) : (
              <Download size={21} />
            )}

            <span>{pdfLoading ? "Generating PDF..." : "Download PDF Report"}</span>
          </button>

          <button
            type="button"
            onClick={onRestart}
            className="report-action-btn report-restart-btn"
          >
            <RefreshCcw size={21} />
            <span>New Interview</span>
          </button>

          {onDashboard && (
            <button
              type="button"
              onClick={onDashboard}
              className="report-action-btn report-dashboard-btn"
            >
              <LayoutDashboard size={21} />
              <span>Go to Dashboard</span>
              <ArrowRight size={17} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function AnimatedScore({ value }) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    let frame;
    const duration = 1200;
    const start = performance.now();

    const animate = (now) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);

      const eased = 1 - Math.pow(1 - progress, 3);

      setDisplay(Number((eased * value).toFixed(1)));

      if (progress < 1) {
        frame = requestAnimationFrame(animate);
      }
    };

    frame = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(frame);
    };
  }, [value]);

  return <div className="report-animated-score">{display}</div>;
}

function ScoreCard({ title, score, icon }) {
  const scoreClass = getScoreClass(score);

  return (
    <div className="report-score-card">
      <div className="report-score-card-title">
        {icon}
        <span>{title}</span>
      </div>

      <strong className={scoreClass}>{score}</strong>
    </div>
  );
}

function ScoreBar({ title, score }) {
  const scoreClass = getScoreClass(score);
  const barClass = getScoreBarClass(score);

  const safeScore = Math.max(0, Math.min(10, score));
  const widthStr = `${safeScore * 10}%`;

  return (
    <div className="report-bar-card">
      <div className="report-bar-top">
        <span>{title}</span>
        <strong className={scoreClass}>{score}</strong>
      </div>

      <div className="report-bar-track">
        <div
          className={`report-bar-fill ${barClass}`}
          style={{
            width: widthStr,
          }}
        />
      </div>
    </div>
  );
}

function AnalysisCard({ title, text, className = "" }) {
  return (
    <div className={`report-analysis-card ${className}`}>
      <h4>{title}</h4>
      <p>{text || "No analysis available."}</p>
    </div>
  );
}

function getScoreClass(score) {
  if (score >= 8) return "report-score-good";
  if (score >= 6) return "report-score-mid";
  return "report-score-low";
}

function getScoreBarClass(score) {
  if (score >= 8) return "report-bar-good";
  if (score >= 6) return "report-bar-mid";
  return "report-bar-low";
}

export default ReportScreen;