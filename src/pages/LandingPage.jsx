import React, { useRef } from "react";
import { Link, useNavigate } from "react-router";

import { useAuthStore } from "../store/useAuthStore.js";
import "./LandingPage.css";

export default function LandingPage() {
  const servicesRef = useRef(null);
  const workflowRef = useRef(null);
  const developerRef = useRef(null);

  const navigate = useNavigate();
  const { user, signOut } = useAuthStore();

  const scrollToSection = (event, sectionRef) => {
    event.preventDefault();

    if (sectionRef.current) {
      sectionRef.current.scrollIntoView({
        behavior: "smooth",
      });
    }
  };

  const handleLogout = async () => {
    await signOut();
    navigate("/");
  };

  return (
    <div className="landing-page">
      {/* Background Layers */}
      <div className="landing-gradient landing-gradient-one"></div>
      <div className="landing-gradient landing-gradient-two"></div>
      <div className="landing-gradient landing-gradient-three"></div>
      <div className="landing-gradient landing-gradient-four"></div>

      <div className="landing-grid-bg"></div>
      <div className="landing-noise-bg"></div>

      {/* Navbar */}
      <header className="landing-header">
        <Link to="/" className="landing-logo">
          <div className="landing-logo-icon">
            <Icon symbol="🎙" size={21} />
          </div>

          <span>InterviewIQ</span>
        </Link>

        <nav className="landing-nav">
          <a
            href="#services"
            onClick={(event) => scrollToSection(event, servicesRef)}
            className="landing-nav-link"
          >
            Services
          </a>

          <a
            href="#workflow"
            onClick={(event) => scrollToSection(event, workflowRef)}
            className="landing-nav-link"
          >
            Workflow
          </a>

          <a
            href="#developers"
            onClick={(event) => scrollToSection(event, developerRef)}
            className="landing-nav-link"
          >
            Developers
          </a>

          {!user ? (
            <>
              <Link to="/login" className="landing-nav-link">
                Login
              </Link>

              <Link to="/setup" className="landing-header-btn">
                Get Started
              </Link>
            </>
          ) : (
            <>
              <Link
                to="/dashboard"
                className="landing-nav-link landing-dashboard-link"
              >
                <Icon symbol="▣" size={17} />
                <span>Dashboard</span>
              </Link>

              <button
                type="button"
                onClick={handleLogout}
                className="landing-logout-btn"
              >
                <Icon symbol="↪" size={17} />
                <span>Logout</span>
              </button>

              <Link to="/setup" className="landing-header-btn">
                Practice Now
              </Link>
            </>
          )}
        </nav>
      </header>

      <main className="landing-main">
        {/* Hero */}
        <section className="landing-hero">
          <div className="landing-hero-left">
            <div className="landing-ai-badge">
              <Icon symbol="✦" size={17} />
              <span>AI Interview Practice + RAG Study Assistant</span>
            </div>

            <h1>
              Prepare Smarter.
              <br />
              <span>Ace Every Interview.</span>
            </h1>

            <p>
              InterviewIQ helps you practice mock interviews, study from PDF
              notes, find resume gaps, and generate flashcards using AI-powered
              preparation tools made for students and job seekers.
            </p>

            <div className="landing-hero-actions">
              <Link to="/setup" className="landing-primary-action">
                <Icon symbol="▶" size={21} />
                <span>Start Interview Practice</span>
                <Icon
                  symbol="→"
                  size={21}
                  className="landing-action-arrow"
                />
              </Link>

              <Link to="/study-notes" className="landing-secondary-action">
                Study from Notes
              </Link>
            </div>

            <div className="landing-hero-trust-row">
              <TrustItem text="AI mock interview" />
              <TrustItem text="PDF-based study help" />
              <TrustItem text="Resume gap analysis" />
            </div>
          </div>

          <div className="landing-hero-right">
            <div className="landing-hero-dashboard-card">
              <div className="landing-dashboard-card-header">
                <div>
                  <span className="landing-dashboard-mini-label">
                    Preparation System
                  </span>

                  <h3>InterviewIQ AI Tools</h3>
                </div>

                <div className="landing-dashboard-status">
                  <span></span>
                  Live
                </div>
              </div>

              <div className="landing-score-circle">
                <strong>4</strong>
                <span>Smart Tools</span>
              </div>

              <div className="landing-score-list">
                <InfoRow
                  title="Interview Practice"
                  text="Voice-based mock interview preparation"
                  value="AI"
                />

                <InfoRow
                  title="Study Notes"
                  text="Ask questions from uploaded PDF notes"
                  value="RAG"
                />

                <InfoRow
                  title="Resume Gap"
                  text="Compare resume with job description"
                  value="JD"
                />
              </div>

              <div className="landing-dashboard-card-footer">
                <Icon symbol="🧠" size={18} />
                <span>Choose one tool and start improving today.</span>
              </div>
            </div>
          </div>
        </section>

        {/* Stats */}
        <section className="landing-stats-section">
          <StatCard icon="🎙" title="Mock" text="Interview Practice" />
          <StatCard icon="📘" title="RAG" text="Study from Notes" />
          <StatCard icon="✓" title="JD" text="Resume Matching" />
          <StatCard icon="🧠" title="MCQ" text="Flashcard Revision" />
        </section>

        {/* Services */}
        <section
          ref={servicesRef}
          id="services"
          className="landing-services-section"
        >
          <div className="landing-section-heading">
            <span className="landing-section-label">Our Services</span>

            <h2>Choose how you want to prepare</h2>

            <p>
              Everything you need for placement preparation is available in one
              place. Start with interview practice, revise notes, check resume
              gaps, or generate flashcards.
            </p>
          </div>

          <div className="landing-services-grid">
            <ServiceCard
              to="/setup"
              icon="🎙"
              title="Start Interview Practice"
              description="Practice real interview questions with AI and get structured feedback after every session."
              buttonText="Start Practice"
              tag="Mock Interview"
              points={[
                "Voice-based interview practice",
                "HR, technical, and custom JD questions",
                "Detailed report after every session",
              ]}
            />

            <ServiceCard
              to="/study-notes"
              icon="📘"
              title="Study from Notes"
              description="Upload PDF notes and ask questions directly from your own study material."
              buttonText="Open Notes Assistant"
              tag="PDF RAG"
              points={[
                "Upload PDF notes",
                "Ask questions from your content",
                "Get summarized answers",
              ]}
            />

            <ServiceCard
              to="/resume-gap-finder"
              icon="✓"
              title="Resume Gap Finder"
              description="Compare your resume with a job description and find missing skills before applying."
              buttonText="Check Resume Gap"
              tag="Resume + JD"
              points={[
                "Resume and JD comparison",
                "Skill gap detection",
                "Improvement suggestions",
              ]}
            />

            <ServiceCard
              to="/flashcards"
              icon="🧠"
              title="Generate Flashcards"
              description="Create MCQ flashcards from notes and revise important concepts quickly."
              buttonText="Generate Flashcards"
              tag="Smart Revision"
              points={[
                "Generate MCQ questions",
                "Practice with options",
                "Revise important topics quickly",
              ]}
            />
          </div>
        </section>

        {/* Workflow */}
        <section
          ref={workflowRef}
          id="workflow"
          className="landing-workflow-section"
        >
          <div className="landing-section-heading">
            <span className="landing-section-label">Simple Workflow</span>

            <h2>How InterviewIQ works</h2>

            <p>
              Select a preparation tool, add your content, let AI process it,
              and improve using the result.
            </p>
          </div>

          <div className="landing-workflow-grid">
            <WorkflowCard
              number="01"
              icon="👥"
              title="Choose your goal"
              description="Pick interview practice, notes assistant, resume gap finder, or flashcards."
            />

            <WorkflowCard
              number="02"
              icon="□"
              title="Add your content"
              description="Upload notes, resume, or paste a job description depending on the tool."
            />

            <WorkflowCard
              number="03"
              icon="🧠"
              title="AI processes it"
              description="The system uses AI and RAG logic to create useful preparation output."
            />

            <WorkflowCard
              number="04"
              icon="▥"
              title="Improve faster"
              description="Use feedback, flashcards, and reports to improve your preparation."
            />
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer ref={developerRef} id="developers" className="landing-footer">
        <div className="landing-footer-content">
          <div className="landing-footer-brand">
            <Link to="/" className="landing-footer-logo">
              <div className="landing-logo-icon">
                <Icon symbol="🎙" size={20} />
              </div>

              <span>InterviewIQ</span>
            </Link>

            <p>
              AI-powered interview preparation platform built for students,
              freshers, and job seekers.
            </p>

            <div className="landing-footer-mini-points">
              <span>Practice</span>
              <Icon symbol="→" size={15} />
              <span>Study</span>
              <Icon symbol="→" size={15} />
              <span>Improve</span>
              <Icon symbol="→" size={15} />
              <span>Ace it</span>
            </div>
          </div>

          <div className="landing-footer-links">
            <h3>Quick Links</h3>

            <Link to="/setup">Start Interview Practice</Link>
            <Link to="/study-notes">Study from Notes</Link>
            <Link to="/resume-gap-finder">Resume Gap Finder</Link>
            <Link to="/flashcards">Generate Flashcards</Link>
            <Link to="/dashboard">Dashboard</Link>
          </div>

          <div className="landing-footer-dev">
            <h3>Developer Details</h3>

            <div className="landing-developer-card">
              <div className="landing-developer-avatar">
                <Icon symbol="👤" size={34} />
              </div>

              <div className="landing-developer-info">
                <h4>Sparsh Srivastava</h4>

                <p>
                  Full Stack Developer | AI & RAG Project Developer | React,
                  FastAPI, Supabase, Groq, LangChain, and modern web
                  technologies.
                </p>

                <div className="landing-footer-socials">
                  <a
                    href="https://github.com/Sp-bit-code"
                    target="_blank"
                    rel="noreferrer"
                    aria-label="GitHub"
                  >
                    <Icon symbol="⌘" size={19} />
                    GitHub
                  </a>

                  <a
                    href="https://www.linkedin.com/in/sparsh-srivastava-621882289/"
                    target="_blank"
                    rel="noreferrer"
                    aria-label="LinkedIn"
                  >
                    <Icon symbol="in" size={19} />
                    LinkedIn
                  </a>

                  <a
                    href="https://www.instagram.com/sp_02arsh_/"
                    target="_blank"
                    rel="noreferrer"
                    aria-label="Instagram"
                  >
                    <Icon symbol="◎" size={19} />
                    Instagram
                  </a>

                  <a href="mailto:sparshsrivastava@example.com">
                    <Icon symbol="✉" size={19} />
                    Email
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="landing-footer-bottom">
          <p>
            © 2026 InterviewIQ. Built for students and job seekers.
            <span> Practice → Study → Improve → Ace it.</span>
          </p>
        </div>
      </footer>
    </div>
  );
}

function Icon({ symbol, size = 18, className = "" }) {
  return (
    <span
      className={`landing-text-icon ${className}`}
      style={{
        width: size,
        height: size,
        minWidth: size,
        fontSize: Math.max(12, size * 0.72),
        lineHeight: `${size}px`,
      }}
      aria-hidden="true"
    >
      {symbol}
    </span>
  );
}

function TrustItem({ text }) {
  return (
    <div className="landing-trust-item">
      <Icon symbol="✓" size={18} />
      <span>{text}</span>
    </div>
  );
}

function InfoRow({ title, text, value }) {
  return (
    <div className="landing-score-item">
      <div>
        <span>{title}</span>
        <small>{text}</small>
      </div>

      <strong>{value}</strong>
    </div>
  );
}

function StatCard({ icon, title, text }) {
  return (
    <div className="landing-stat-card">
      <div className="landing-stat-icon">
        <Icon symbol={icon} size={24} />
      </div>

      <strong>{title}</strong>
      <span>{text}</span>
    </div>
  );
}

function ServiceCard({
  to,
  icon,
  title,
  description,
  buttonText,
  tag,
  points = [],
}) {
  return (
    <div className="landing-service-card">
      <div className="landing-service-card-top">
        <div className="landing-service-icon">
          <Icon symbol={icon} size={38} />
        </div>

        <span className="landing-service-tag">{tag}</span>
      </div>

      <h3>{title}</h3>

      <p>{description}</p>

      <div className="landing-service-points">
        {points.map((point) => (
          <div className="landing-service-point" key={point}>
            <Icon symbol="✓" size={17} />
            <span>{point}</span>
          </div>
        ))}
      </div>

      <Link to={to} className="landing-service-btn">
        <span>{buttonText}</span>
        <Icon symbol="→" size={18} />
      </Link>
    </div>
  );
}

function WorkflowCard({ number, icon, title, description }) {
  return (
    <div className="landing-workflow-card">
      <div className="landing-workflow-card-top">
        <span>{number}</span>

        <div className="landing-workflow-icon">
          <Icon symbol={icon} size={28} />
        </div>
      </div>

      <h3>{title}</h3>

      <p>{description}</p>
    </div>
  );
}