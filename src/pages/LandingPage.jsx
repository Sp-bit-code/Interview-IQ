// import React, { useRef } from "react";
// import { Link, useNavigate } from "react-router";
// import {
//   Mic,
//   Eye,
//   BarChart,
//   History,
//   PlayCircle,
//   Star,
//   ShieldCheck,
//   Zap,
//   ArrowRight,
//   CheckCircle2,
//   Users,
//   Sparkles,
//   LogOut,
//   LayoutDashboard,
// } from "lucide-react";

// import { useAuthStore } from "../store/useAuthStore.js";
// import "./LandingPage.css";

// export default function LandingPage() {
//   const featuresRef = useRef(null);
//   const navigate = useNavigate();

//   const { user, signOut } = useAuthStore();

//   const scrollToFeatures = (event) => {
//     event.preventDefault();

//     if (featuresRef.current) {
//       featuresRef.current.scrollIntoView({
//         behavior: "smooth",
//       });
//     }
//   };

//   const handleLogout = async () => {
//     await signOut();
//     navigate("/");
//   };

//   return (
//     <div className="landing-page">
//       {/* Decorative Background Gradients */}
//       <div className="landing-gradient landing-gradient-one"></div>
//       <div className="landing-gradient landing-gradient-two"></div>
//       <div className="landing-gradient landing-gradient-three"></div>

//       {/* Header */}
//       <header className="landing-header">
//         <Link to="/" className="landing-logo">
//           <div className="landing-logo-icon">
//             <Mic size={21} />
//           </div>

//           <span>InterviewIQ</span>
//         </Link>

//         <nav className="landing-nav">
//           <a
//             href="#features"
//             onClick={scrollToFeatures}
//             className="landing-nav-link landing-features-link"
//           >
//             Features
//           </a>

//           {!user ? (
//             <>
//               <Link to="/login" className="landing-nav-link">
//                 Login
//               </Link>

//               <Link to="/setup" className="landing-header-btn">
//                 Get Started
//               </Link>
//             </>
//           ) : (
//             <>
//               <Link to="/dashboard" className="landing-nav-link landing-dashboard-link">
//                 <LayoutDashboard size={17} />
//                 Dashboard
//               </Link>

//               <button
//                 type="button"
//                 onClick={handleLogout}
//                 className="landing-logout-btn"
//               >
//                 <LogOut size={17} />
//                 Logout
//               </button>

//               <Link to="/setup" className="landing-header-btn">
//                 Practice Now
//               </Link>
//             </>
//           )}
//         </nav>
//       </header>

//       <main className="landing-main">
//         {/* Hero Section */}
//         <section className="landing-hero">
//           <div className="landing-ai-badge">
//             <Sparkles size={17} />
//             <span>Powered by Gemini 2.5 Flash AI</span>
//           </div>

//           <h1>
//             Ace Every Interview.
//             <br />
//             <span>Practice with AI.</span>
//           </h1>

//           <p>
//             Your AI interview coach that listens, responds, and gives real-time
//             behavioral feedback on your eye contact, posture, and communication
//             skills. Just like practicing with a real mentor — but available
//             anytime.
//           </p>

//           <div className="landing-hero-actions">
//             <Link to="/setup" className="landing-primary-action">
//               <PlayCircle size={21} />
//               <span>Start Free Practice</span>
//               <ArrowRight className="landing-action-arrow" size={21} />
//             </Link>

//             {user ? (
//               <Link to="/dashboard" className="landing-secondary-action">
//                 View Dashboard
//               </Link>
//             ) : (
//               <Link to="/login" className="landing-secondary-action">
//                 View Dashboard
//               </Link>
//             )}
//           </div>
//         </section>

//         {/* How It Works */}
//         <section className="landing-steps-grid">
//           <StepCard
//             number="1"
//             title="Pick Your Topic"
//             description="Choose HR, Technical, or paste a custom Job Description."
//           />

//           <StepCard
//             number="2"
//             title="Talk to Your AI Coach"
//             description="Real-time voice conversation with instant feedback on each answer."
//           />

//           <StepCard
//             number="3"
//             title="Get Your Report"
//             description="Detailed performance report with actionable improvement tips."
//           />
//         </section>

//         {/* Value Proposition */}
//         <section className="landing-value-section">
//           <div className="landing-value-content">
//             <div className="landing-value-text">
//               <h2>
//                 Practice makes <span>perfect</span>
//               </h2>

//               <p>
//                 Most people find it hard to express themselves in front of an
//                 interviewer. InterviewIQ gives you a safe space to practice as
//                 many times as you want — the AI coach gives feedback on every
//                 answer, just like a real mentor would.
//               </p>

//               <div className="landing-check-list">
//                 <CheckPoint text="Practice unlimited times, no judgment" />
//                 <CheckPoint text="Get instant feedback on every response" />
//                 <CheckPoint text="Track your progress over multiple sessions" />
//                 <CheckPoint text="Upload your resume for personalized questions" />
//               </div>
//             </div>

//             <div className="landing-value-visual">
//               <div className="landing-session-card">
//                 <Users size={68} />

//                 <div className="landing-session-info">
//                   <strong>15</strong>
//                   <span>AI-guided questions per session</span>
//                   <small>30-40 min interview simulation</small>
//                 </div>

//                 <div className="landing-free-badge">Free to use</div>
//               </div>
//             </div>
//           </div>
//         </section>

//         {/* Features Grid */}
//         <section
//           ref={featuresRef}
//           id="features"
//           className="landing-features-section"
//         >
//           <div className="landing-section-heading">
//             <h2>Why InterviewIQ?</h2>
//             <p>Professional interview coaching tools — available for free.</p>
//           </div>

//           <div className="landing-features-grid">
//             <FeatureCard
//               icon={<Eye size={34} />}
//               color="secondary"
//               title="Live Behavioral Coaching"
//               description="MediaPipe vision engine analyzes your webcam feed to coach you on eye contact and posture in real-time."
//             />

//             <FeatureCard
//               icon={<Mic size={34} />}
//               color="primary"
//               title="Voice Conversation"
//               description="Natural voice-to-voice conversation with the AI. It speaks, you speak — just like a real interview."
//             />

//             <FeatureCard
//               icon={<BarChart size={34} />}
//               color="secondary"
//               title="Detailed Score Report"
//               description="Get 0-10 breakdowns for communication, confidence, body language, and more with actionable tips."
//             />

//             <FeatureCard
//               icon={<History size={34} />}
//               color="primary"
//               title="Progress Tracking"
//               description="Dashboard charts track how much you improve session after session. See your growth over time."
//             />

//             <FeatureCard
//               icon={<Star size={34} />}
//               color="secondary"
//               title="Achievement Badges"
//               description="Earn badges like 'Eye Contact Pro' and '90+ Club' to stay motivated and challenge yourself."
//             />

//             <FeatureCard
//               icon={<ShieldCheck size={34} />}
//               color="primary"
//               title="Resume & JD-Aware"
//               description="Upload your resume or paste a Job Description — the AI tailors questions specifically for your profile."
//             />
//           </div>
//         </section>
//       </main>

//       <footer className="landing-footer">
//         <p>
//           © 2026 InterviewIQ. Built for students and job seekers.
//           <span> Practice → Improve → Ace it.</span>
//         </p>
//       </footer>
//     </div>
//   );
// }

// function StepCard({ number, title, description }) {
//   return (
//     <div className="landing-step-card">
//       <span>{number}</span>
//       <h3>{title}</h3>
//       <p>{description}</p>
//     </div>
//   );
// }

// function CheckPoint({ text }) {
//   return (
//     <div className="landing-check-item">
//       <CheckCircle2 size={21} />
//       <span>{text}</span>
//     </div>
//   );
// }

// function FeatureCard({ icon, color, title, description }) {
//   return (
//     <div className="landing-feature-card">
//       <div className={`landing-feature-icon landing-feature-icon-${color}`}>
//         {icon}
//       </div>

//       <h3>{title}</h3>

//       <p>{description}</p>
//     </div>
//   );
// }

import React, { useRef } from "react";
import { Link, useNavigate } from "react-router";
import {
  Mic,
  Eye,
  BarChart,
  History,
  PlayCircle,
  Star,
  ShieldCheck,
  Zap,
  ArrowRight,
  CheckCircle2,
  Users,
  Sparkles,
  LogOut,
  LayoutDashboard,
  BookOpen,
  Brain,
  ClipboardCheck,
  FileText,
  GraduationCap,
} from "lucide-react";

import { useAuthStore } from "../store/useAuthStore.js";
import "./LandingPage.css";

export default function LandingPage() {
  const featuresRef = useRef(null);
  const ragToolsRef = useRef(null);
  const navigate = useNavigate();

  const { user, signOut } = useAuthStore();

  const scrollToFeatures = (event) => {
    event.preventDefault();

    if (featuresRef.current) {
      featuresRef.current.scrollIntoView({
        behavior: "smooth",
      });
    }
  };

  const scrollToRagTools = (event) => {
    event.preventDefault();

    if (ragToolsRef.current) {
      ragToolsRef.current.scrollIntoView({
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
      {/* Decorative Background Gradients */}
      <div className="landing-gradient landing-gradient-one"></div>
      <div className="landing-gradient landing-gradient-two"></div>
      <div className="landing-gradient landing-gradient-three"></div>

      {/* Header */}
      <header className="landing-header">
        <Link to="/" className="landing-logo">
          <div className="landing-logo-icon">
            <Mic size={21} />
          </div>

          <span>InterviewIQ</span>
        </Link>

        <nav className="landing-nav">
          <a
            href="#features"
            onClick={scrollToFeatures}
            className="landing-nav-link landing-features-link"
          >
            Features
          </a>

          <a
            href="#rag-tools"
            onClick={scrollToRagTools}
            className="landing-nav-link landing-features-link"
          >
            AI Tools
          </a>

          <Link to="/study-notes" className="landing-nav-link">
            Study Notes
          </Link>

          <Link to="/resume-gap-finder" className="landing-nav-link">
            Resume Gap
          </Link>

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
                <LayoutDashboard size={17} />
                Dashboard
              </Link>

              <button
                type="button"
                onClick={handleLogout}
                className="landing-logout-btn"
              >
                <LogOut size={17} />
                Logout
              </button>

              <Link to="/setup" className="landing-header-btn">
                Practice Now
              </Link>
            </>
          )}
        </nav>
      </header>

      <main className="landing-main">
        {/* Hero Section */}
        <section className="landing-hero">
          <div className="landing-ai-badge">
            <Sparkles size={17} />
            <span>AI Interview + RAG Study Assistant</span>
          </div>

          <h1>
            Ace Every Interview.
            <br />
            <span>Practice with AI.</span>
          </h1>

          <p>
            Your AI interview coach that helps you practice voice interviews,
            study from PDF notes, generate flashcards, and compare your resume
            with job descriptions using RAG-powered AI tools.
          </p>

          <div className="landing-hero-actions">
            <Link to="/setup" className="landing-primary-action">
              <PlayCircle size={21} />
              <span>Start Interview Practice</span>
              <ArrowRight className="landing-action-arrow" size={21} />
            </Link>

            <Link to="/study-notes" className="landing-secondary-action">
              Study from Notes
            </Link>
          </div>

          <div className="landing-quick-tools">
            <QuickTool
              to="/study-notes"
              icon={<BookOpen size={18} />}
              title="Study from Notes"
            />

            <QuickTool
              to="/resume-gap-finder"
              icon={<ClipboardCheck size={18} />}
              title="Resume Gap Finder"
            />

            <QuickTool
              to="/flashcards"
              icon={<Brain size={18} />}
              title="Generate Flashcards"
            />
          </div>
        </section>

        {/* How It Works */}
        <section className="landing-steps-grid">
          <StepCard
            number="1"
            title="Pick Your Topic"
            description="Choose HR, Technical, General, or paste a custom Job Description."
          />

          <StepCard
            number="2"
            title="Talk to Your AI Coach"
            description="Real-time voice conversation with instant interview-style practice."
          />

          <StepCard
            number="3"
            title="Get Your Report"
            description="Detailed performance report with transcript, score, and improvement tips."
          />
        </section>

        {/* RAG Tools Section */}
        <section
          ref={ragToolsRef}
          id="rag-tools"
          className="landing-rag-tools-section"
        >
          <div className="landing-section-heading">
            <h2>AI Study & Resume Tools</h2>
            <p>
              Use your FastAPI RAG backend to study notes, generate flashcards,
              and find resume gaps.
            </p>
          </div>

          <div className="landing-rag-tools-grid">
            <RagToolCard
              to="/study-notes"
              icon={<BookOpen size={34} />}
              title="Study from Notes"
              description="Upload PDF notes, ask questions, summarize topics, and generate viva/interview questions from your own material."
              tag="PDF RAG"
            />

            <RagToolCard
              to="/resume-gap-finder"
              icon={<ClipboardCheck size={34} />}
              title="Resume Gap Finder"
              description="Upload your resume, paste a job description, and get match percentage, missing skills, weak areas, and improvement tips."
              tag="Resume + JD"
            />

            <RagToolCard
              to="/flashcards"
              icon={<Brain size={34} />}
              title="Generate Flashcards"
              description="Create MCQ flashcards from uploaded notes and practice with answer checking, explanation, and source references."
              tag="MCQ Practice"
            />
          </div>
        </section>

        {/* Value Proposition */}
        <section className="landing-value-section">
          <div className="landing-value-content">
            <div className="landing-value-text">
              <h2>
                Practice makes <span>perfect</span>
              </h2>

              <p>
                Most people find it hard to express themselves in front of an
                interviewer. InterviewIQ gives you a safe space to practice,
                revise from your notes, and improve your resume direction before
                applying.
              </p>

              <div className="landing-check-list">
                <CheckPoint text="Practice unlimited times, no judgment" />
                <CheckPoint text="Get instant feedback on every response" />
                <CheckPoint text="Study from your uploaded PDF notes" />
                <CheckPoint text="Generate flashcards for quick revision" />
                <CheckPoint text="Find resume gaps using job descriptions" />
              </div>
            </div>

            <div className="landing-value-visual">
              <div className="landing-session-card">
                <Users size={68} />

                <div className="landing-session-info">
                  <strong>3</strong>
                  <span>AI-powered preparation modes</span>
                  <small>Interview + Notes RAG + Resume Gap Finder</small>
                </div>

                <div className="landing-free-badge">Free to use</div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section
          ref={featuresRef}
          id="features"
          className="landing-features-section"
        >
          <div className="landing-section-heading">
            <h2>Why InterviewIQ?</h2>
            <p>Professional interview coaching tools — available for free.</p>
          </div>

          <div className="landing-features-grid">
            <FeatureCard
              icon={<Eye size={34} />}
              color="secondary"
              title="Live Behavioral Coaching"
              description="Camera-based feedback can help you improve confidence, eye contact, and posture during interview practice."
            />

            <FeatureCard
              icon={<Mic size={34} />}
              color="primary"
              title="Voice Conversation"
              description="Natural voice-to-voice conversation with AI. It speaks, you speak — just like a real interview."
            />

            <FeatureCard
              icon={<BarChart size={34} />}
              color="secondary"
              title="Detailed Score Report"
              description="Get 0-10 breakdowns for communication, confidence, body language, transcript, and session duration."
            />

            <FeatureCard
              icon={<BookOpen size={34} />}
              color="primary"
              title="RAG Notes Assistant"
              description="Upload notes and ask questions from your own PDFs using FastAPI, ChromaDB, embeddings, and Groq."
            />

            <FeatureCard
              icon={<Brain size={34} />}
              color="secondary"
              title="Flashcard Generator"
              description="Generate MCQ flashcards from notes with options, correct answer, explanation, and source reference."
            />

            <FeatureCard
              icon={<ShieldCheck size={34} />}
              color="primary"
              title="Resume & JD-Aware"
              description="Compare resume with job description and get missing skills, match score, and resume improvement suggestions."
            />
          </div>
        </section>
      </main>

      <footer className="landing-footer">
        <p>
          © 2026 InterviewIQ. Built for students and job seekers.
          <span> Practice → Study → Improve → Ace it.</span>
        </p>
      </footer>
    </div>
  );
}

function QuickTool({ to, icon, title }) {
  return (
    <Link to={to} className="landing-quick-tool">
      {icon}
      <span>{title}</span>
    </Link>
  );
}

function StepCard({ number, title, description }) {
  return (
    <div className="landing-step-card">
      <span>{number}</span>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function CheckPoint({ text }) {
  return (
    <div className="landing-check-item">
      <CheckCircle2 size={21} />
      <span>{text}</span>
    </div>
  );
}

function RagToolCard({ to, icon, title, description, tag }) {
  return (
    <Link to={to} className="landing-rag-tool-card">
      <div className="landing-rag-tool-top">
        <div className="landing-rag-tool-icon">{icon}</div>
        <span>{tag}</span>
      </div>

      <h3>{title}</h3>
      <p>{description}</p>

      <div className="landing-rag-tool-link">
        Open Tool
        <ArrowRight size={17} />
      </div>
    </Link>
  );
}

function FeatureCard({ icon, color, title, description }) {
  return (
    <div className="landing-feature-card">
      <div className={`landing-feature-icon landing-feature-icon-${color}`}>
        {icon}
      </div>

      <h3>{title}</h3>

      <p>{description}</p>
    </div>
  );
}