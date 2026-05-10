// import React, { useEffect, useMemo, useState } from "react";
// import { Link, useNavigate } from "react-router";
// import {
//   BarChart3,
//   LayoutDashboard,
//   LineChart,
//   Target,
//   Zap,
//   History,
//   Award,
//   Calendar,
//   Loader2,
//   LogOut,
//   X,
//   Eye,
//   ChevronRight,
//   ExternalLink,
//   MessageSquare,
//   Briefcase,
//   User,
//   Clock,
//   FileText,
// } from "lucide-react";
// import {
//   AreaChart,
//   Area,
//   XAxis,
//   YAxis,
//   CartesianGrid,
//   Tooltip,
//   ResponsiveContainer,
// } from "recharts";

// import { useAuthStore } from "../store/useAuthStore";
// import { supabase } from "../lib/supabase";
// import "./Dashboard.css";

// export default function Dashboard() {
//   const { user, signOut } = useAuthStore();
//   const navigate = useNavigate();

//   const [sessions, setSessions] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [selectedReport, setSelectedReport] = useState(null);
//   const [activeTab, setActiveTab] = useState("dashboard");
//   const [fetchError, setFetchError] = useState("");

//   useEffect(() => {
//     const fetchSessions = async () => {
//       if (!user?.id) {
//         setSessions([]);
//         setLoading(false);
//         return;
//       }

//       setLoading(true);
//       setFetchError("");

//       try {
//         const { data, error } = await supabase
//           .from("session_scores")
//           .select("*")
//           .eq("user_id", user.id)
//           .order("created_at", { ascending: true });

//         if (error) {
//           console.error("Dashboard fetch error:", error);
//           setFetchError(error?.message || "Failed to load dashboard data.");
//           setSessions([]);
//           return;
//         }

//         setSessions(Array.isArray(data) ? data : []);
//       } catch (err) {
//         console.error("Unexpected dashboard error:", err);
//         setFetchError(err?.message || "Unexpected dashboard error.");
//         setSessions([]);
//       } finally {
//         setLoading(false);
//       }
//     };

//     fetchSessions();
//   }, [user]);

//   const handleSignOut = async () => {
//     await signOut();
//     navigate("/login");
//   };

//   const totalSessions = sessions.length;

//   const averageScore = useMemo(() => {
//     if (totalSessions === 0) {
//       return "0.0";
//     }

//     const total = sessions.reduce((acc, session) => {
//       return acc + Number(session.score_overall || 0);
//     }, 0);

//     return (total / totalSessions).toFixed(1);
//   }, [sessions, totalSessions]);

//   const bestScore = useMemo(() => {
//     if (totalSessions === 0) {
//       return "0.0";
//     }

//     return Math.max(
//       ...sessions.map((session) => Number(session.score_overall || 0))
//     ).toFixed(1);
//   }, [sessions, totalSessions]);

//   const chartData = useMemo(() => {
//     return sessions.map((session, index) => {
//       const createdDate = session.created_at
//         ? new Date(session.created_at)
//         : new Date();

//       return {
//         date: createdDate.toLocaleDateString(undefined, {
//           month: "short",
//           day: "numeric",
//         }),
//         score: Number(session.score_overall || 0),
//         track: session.track || "General",
//         difficulty: session.difficulty || "Fresher",
//         sessionNo: index + 1,
//       };
//     });
//   }, [sessions]);

//   const hasEyeContactPro = sessions.some((session) => {
//     const eyeContact = Number(session.score_eye_contact || 0);
//     const bodyLanguage = Number(session.score_body_language || 0);

//     return eyeContact >= 9 || bodyLanguage >= 9;
//   });

//   const has90Club = sessions.some((session) => {
//     return Number(session.score_overall || 0) >= 9;
//   });

//   const has5Streak = totalSessions >= 5;

//   if (loading) {
//     return (
//       <div className="dashboard-loading">
//         <Loader2 className="dashboard-loading-icon" />
//         <span>Loading your dashboard...</span>
//       </div>
//     );
//   }

//   return (
//     <div className="dashboard-page">
//       <aside className="dashboard-sidebar">
//         <div className="dashboard-logo">
//           <div className="dashboard-logo-icon">
//             <Zap size={17} />
//           </div>

//           <span>InterviewIQ</span>
//         </div>

//         <nav className="dashboard-nav">
//           <button
//             type="button"
//             onClick={() => setActiveTab("dashboard")}
//             className={`dashboard-nav-btn ${
//               activeTab === "dashboard" ? "dashboard-nav-btn-active" : ""
//             }`}
//           >
//             <LayoutDashboard size={20} />
//             <span>Dashboard</span>
//           </button>

//           <button
//             type="button"
//             onClick={() => setActiveTab("sessions")}
//             className={`dashboard-nav-btn ${
//               activeTab === "sessions" ? "dashboard-nav-btn-active" : ""
//             }`}
//           >
//             <History size={20} />
//             <span>Past Sessions</span>
//           </button>
//         </nav>

//         <div className="dashboard-user-box">
//           <div className="dashboard-user-info">
//             <div className="dashboard-avatar">
//               {user?.email?.[0]?.toUpperCase() || "U"}
//             </div>

//             <div className="dashboard-user-text">
//               <p>{user?.email?.split("@")[0] || "User"}</p>
//               <span>{user?.email || "No email found"}</span>
//             </div>
//           </div>

//           <button
//             type="button"
//             onClick={handleSignOut}
//             className="dashboard-signout-btn"
//           >
//             <LogOut size={17} />
//             <span>Sign Out</span>
//           </button>
//         </div>
//       </aside>

//       <main className="dashboard-main">
//         <div className="dashboard-container">
//           <div className="dashboard-header">
//             <div>
//               <h1>
//                 {activeTab === "dashboard"
//                   ? "Welcome Back! 👋"
//                   : "Past Sessions"}
//               </h1>

//               <p>
//                 {activeTab === "dashboard"
//                   ? totalSessions === 0
//                     ? "You have not completed any interviews yet. Start your first practice."
//                     : "Your interview performance overview."
//                   : `${totalSessions} interview sessions recorded.`}
//               </p>
//             </div>

//             <Link to="/setup" className="dashboard-new-btn">
//               <span>+ New Practice</span>
//               <ChevronRight size={17} />
//             </Link>
//           </div>

//           {fetchError && (
//             <div className="interview-error-box">
//               {typeof fetchError === "string"
//                 ? fetchError
//                 : JSON.stringify(fetchError)}
//             </div>
//           )}

//           {activeTab === "dashboard" && (
//             <>
//               <div className="dashboard-stats-grid">
//                 <StatCard
//                   title="Total Sessions"
//                   value={totalSessions}
//                   icon={<History size={20} />}
//                 />

//                 <StatCard
//                   title="Average Score"
//                   value={averageScore}
//                   suffix="/10"
//                   icon={<BarChart3 size={20} />}
//                 />

//                 <StatCard
//                   title="Best Score"
//                   value={bestScore}
//                   icon={<StarIcon />}
//                   special
//                 />

//                 <StatCard
//                   title="Consistency"
//                   value={totalSessions}
//                   suffix=" sessions"
//                   icon={<Zap size={20} />}
//                 />
//               </div>

//               <div className="dashboard-overview-grid">
//                 <section className="dashboard-card dashboard-chart-card">
//                   <div className="dashboard-section-title">
//                     <LineChart size={20} />
//                     <h2>Performance Growth</h2>
//                   </div>

//                   <div className="dashboard-chart-area">
//                     {totalSessions === 0 ? (
//                       <div className="dashboard-empty-chart">
//                         <Target size={38} />
//                         <p>Complete your first session to unlock charts.</p>
//                       </div>
//                     ) : (
//                       <ResponsiveContainer width="100%" height="100%">
//                         <AreaChart data={chartData}>
//                           <defs>
//                             <linearGradient
//                               id="colorScore"
//                               x1="0"
//                               y1="0"
//                               x2="0"
//                               y2="1"
//                             >
//                               <stop
//                                 offset="5%"
//                                 stopColor="var(--dash-primary)"
//                                 stopOpacity={0.3}
//                               />

//                               <stop
//                                 offset="95%"
//                                 stopColor="var(--dash-primary)"
//                                 stopOpacity={0}
//                               />
//                             </linearGradient>
//                           </defs>

//                           <CartesianGrid
//                             strokeDasharray="3 3"
//                             vertical={false}
//                             stroke="var(--dash-border)"
//                           />

//                           <XAxis
//                             dataKey="date"
//                             axisLine={false}
//                             tickLine={false}
//                             tick={{
//                               fill: "var(--dash-muted)",
//                               fontSize: 12,
//                             }}
//                             dy={10}
//                           />

//                           <YAxis
//                             domain={[0, 10]}
//                             axisLine={false}
//                             tickLine={false}
//                             tick={{
//                               fill: "var(--dash-muted)",
//                               fontSize: 12,
//                             }}
//                             dx={-10}
//                           />

//                           <Tooltip
//                             contentStyle={{
//                               backgroundColor: "var(--dash-card)",
//                               borderRadius: "14px",
//                               border: "1px solid var(--dash-border)",
//                               color: "var(--dash-text)",
//                             }}
//                             itemStyle={{
//                               color: "var(--dash-text)",
//                               fontWeight: "700",
//                             }}
//                           />

//                           <Area
//                             type="monotone"
//                             dataKey="score"
//                             stroke="var(--dash-primary)"
//                             strokeWidth={3}
//                             fillOpacity={1}
//                             fill="url(#colorScore)"
//                           />
//                         </AreaChart>
//                       </ResponsiveContainer>
//                     )}
//                   </div>
//                 </section>

//                 <section className="dashboard-card dashboard-badges-card">
//                   <div className="dashboard-section-title dashboard-section-title-secondary">
//                     <Award size={20} />
//                     <h2>Badges</h2>
//                   </div>

//                   <div className="dashboard-badge-grid">
//                     <BadgeItem
//                       icon={<Eye size={25} />}
//                       title="Eye Contact Pro"
//                       earned={hasEyeContactPro}
//                       color="secondary"
//                     />

//                     <BadgeItem
//                       icon={<StarIcon width="25" height="25" />}
//                       title="90+ Club"
//                       earned={has90Club}
//                       color="yellow"
//                     />

//                     <div className="dashboard-badge-wide">
//                       <BadgeItem
//                         icon={<Zap size={22} />}
//                         title={`5-Session Streak ${
//                           !has5Streak ? "(Locked)" : ""
//                         }`}
//                         earned={has5Streak}
//                         color="primary"
//                       />
//                     </div>
//                   </div>
//                 </section>
//               </div>
//             </>
//           )}

//           <section className="dashboard-card dashboard-table-card">
//             <h2 className="dashboard-table-title">
//               {activeTab === "sessions" ? "All Sessions" : "Recent Sessions"}
//             </h2>

//             <div className="dashboard-table-wrapper">
//               <table className="dashboard-table">
//                 <thead>
//                   <tr>
//                     <th>Date</th>
//                     <th>Track</th>
//                     <th>Level</th>
//                     <th className="dashboard-text-right">Score</th>
//                     <th className="dashboard-text-center">Report</th>
//                   </tr>
//                 </thead>

//                 <tbody>
//                   {sessions.length === 0 ? (
//                     <tr>
//                       <td colSpan="5" className="dashboard-no-data">
//                         No sessions recorded yet. Start your first practice.
//                       </td>
//                     </tr>
//                   ) : (
//                     sessions
//                       .slice()
//                       .reverse()
//                       .slice(0, activeTab === "sessions" ? undefined : 5)
//                       .map((session) => {
//                         const score = Number(session.score_overall || 0);

//                         return (
//                           <tr key={session.id}>
//                             <td>
//                               <div className="dashboard-date-cell">
//                                 <Calendar size={16} />
//                                 {session.created_at
//                                   ? new Date(
//                                       session.created_at
//                                     ).toLocaleDateString()
//                                   : "Unknown"}
//                               </div>
//                             </td>

//                             <td className="dashboard-track-cell">
//                               {session.track || "General"}
//                             </td>

//                             <td>
//                               <span className="dashboard-level-pill">
//                                 {session.difficulty || "Fresher"}
//                               </span>
//                             </td>

//                             <td className="dashboard-text-right">
//                               <span
//                                 className={`dashboard-score ${
//                                   score >= 8
//                                     ? "dashboard-score-good"
//                                     : score >= 6
//                                     ? "dashboard-score-mid"
//                                     : "dashboard-score-low"
//                                 }`}
//                               >
//                                 {score.toFixed(1)}
//                               </span>
//                             </td>

//                             <td className="dashboard-text-center">
//                               <button
//                                 type="button"
//                                 onClick={() => setSelectedReport(session)}
//                                 className="dashboard-view-btn"
//                               >
//                                 <span>View</span>
//                                 <ExternalLink size={13} />
//                               </button>
//                             </td>
//                           </tr>
//                         );
//                       })
//                   )}
//                 </tbody>
//               </table>
//             </div>
//           </section>
//         </div>
//       </main>

//       {selectedReport && (
//         <ReportModal
//           report={selectedReport}
//           onClose={() => setSelectedReport(null)}
//         />
//       )}
//     </div>
//   );
// }

// function ReportModal({ report, onClose }) {
//   const data = report.report_json || {};
//   const setup = data.setup || {};
//   const transcript = Array.isArray(data.transcript) ? data.transcript : [];

//   const overallScore = Number(report.score_overall || 0);
//   const communicationScore = Number(report.score_communication || 0);
//   const confidenceScore = Number(report.score_confidence || 0);
//   const bodyLanguageScore = Number(report.score_body_language || 0);
//   const eyeContactScore = Number(report.score_eye_contact || 0);
//   const speakingPaceScore = Number(report.score_speaking_pace || 0);

//   const durationSeconds = Number(
//     report.duration_seconds || data.durationSeconds || 0
//   );

//   const formattedDuration =
//     durationSeconds > 0
//       ? `${Math.floor(durationSeconds / 60)}m ${durationSeconds % 60}s`
//       : "Not tracked";

//   const summary =
//     typeof data.overallSummary === "string"
//       ? data.overallSummary
//       : "Vapi voice interview completed. Transcript and basic score are saved.";

//   return (
//     <div className="dashboard-modal-overlay" onClick={onClose}>
//       <div
//         className="dashboard-modal"
//         onClick={(event) => event.stopPropagation()}
//       >
//         <div className="dashboard-modal-header">
//           <div>
//             <h2>Session Report</h2>

//             <div className="dashboard-modal-tags">
//               <span className="dashboard-modal-tag-primary">
//                 {report.track || "General"}
//               </span>

//               <span>{report.difficulty || "Fresher"}</span>

//               <span>
//                 {report.created_at
//                   ? new Date(report.created_at).toLocaleDateString()
//                   : "Unknown date"}
//               </span>
//             </div>
//           </div>

//           <button type="button" onClick={onClose} className="dashboard-modal-close">
//             <X size={20} />
//           </button>
//         </div>

//         <div className="dashboard-overall-score-box">
//           <p>Overall Score</p>
//           <h3>{overallScore.toFixed(1)}</h3>
//           <span>out of 10</span>
//         </div>

//         <div className="dashboard-score-grid">
//           <ScoreItem label="Communication" value={communicationScore} />
//           <ScoreItem label="Confidence" value={confidenceScore} />
//           <ScoreItem label="Body Language" value={bodyLanguageScore} />
//           <ScoreItem label="Eye Contact" value={eyeContactScore} />
//           <ScoreItem label="Speaking Pace" value={speakingPaceScore} />
//           <ScoreItem label="Duration" value={formattedDuration} isText />
//         </div>

//         <div className="dashboard-report-section">
//           <h3>Summary</h3>
//           <p>{summary}</p>
//         </div>

//         <div className="dashboard-report-section">
//           <h3>Interview Setup</h3>

//           <div className="dashboard-report-meta-grid">
//             <ReportMetaItem
//               icon={<Briefcase size={16} />}
//               label="Track"
//               value={report.track || setup.track || "General"}
//             />

//             <ReportMetaItem
//               icon={<User size={16} />}
//               label="Difficulty"
//               value={report.difficulty || setup.difficulty || "Fresher"}
//             />

//             <ReportMetaItem
//               icon={<FileText size={16} />}
//               label="Resume"
//               value={setup.resumeFileName || "Not uploaded"}
//             />

//             <ReportMetaItem
//               icon={<MessageSquare size={16} />}
//               label="Messages"
//               value={String(data.totalMessages || transcript.length || 0)}
//             />

//             <ReportMetaItem
//               icon={<Clock size={16} />}
//               label="Duration"
//               value={formattedDuration}
//             />

//             <ReportMetaItem
//               icon={<MessageSquare size={16} />}
//               label="JD"
//               value={setup.hasJobDescription ? "Added" : "Not added"}
//             />
//           </div>
//         </div>

//         {Array.isArray(data.improvementTips) && data.improvementTips.length > 0 && (
//           <div className="dashboard-report-section">
//             <h3>Improvement Tips</h3>

//             <div className="dashboard-tips-list">
//               {data.improvementTips.map((tip, index) => (
//                 <div key={index} className="dashboard-tip-item">
//                   <span>{index + 1}</span>
//                   <p>{String(tip)}</p>
//                 </div>
//               ))}
//             </div>
//           </div>
//         )}

//         <div className="dashboard-report-section">
//           <h3>Transcript</h3>

//           {transcript.length === 0 ? (
//             <p>No transcript captured for this session.</p>
//           ) : (
//             <div className="dashboard-transcript-box">
//               {transcript.map((message, index) => {
//                 const isUser = message.role === "user";
//                 const roleLabel = isUser ? "You" : "AI Interviewer";

//                 return (
//                   <div
//                     key={`${message.role}-${index}`}
//                     className={`dashboard-transcript-item ${
//                       isUser
//                         ? "dashboard-transcript-user"
//                         : "dashboard-transcript-ai"
//                     }`}
//                   >
//                     <strong>{roleLabel}</strong>
//                     <p>{String(message.content || "")}</p>
//                   </div>
//                 );
//               })}
//             </div>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }

// function ReportMetaItem({ icon, label, value }) {
//   return (
//     <div className="dashboard-report-meta-item">
//       <div className="dashboard-report-meta-icon">{icon}</div>

//       <div>
//         <span>{label}</span>
//         <strong>{value}</strong>
//       </div>
//     </div>
//   );
// }

// function ScoreItem({ label, value, isText = false }) {
//   if (isText) {
//     return (
//       <div className="dashboard-score-item">
//         <span>{label}</span>
//         <strong>{value}</strong>
//       </div>
//     );
//   }

//   const finalValue = Number(value || 0);

//   let scoreClass = "dashboard-score-low";

//   if (finalValue >= 8) {
//     scoreClass = "dashboard-score-good";
//   } else if (finalValue >= 6) {
//     scoreClass = "dashboard-score-mid";
//   }

//   return (
//     <div className="dashboard-score-item">
//       <span>{label}</span>
//       <strong className={scoreClass}>{finalValue.toFixed(1)}</strong>
//     </div>
//   );
// }

// function StatCard({ title, value, icon, suffix = "", special = false }) {
//   return (
//     <div
//       className={`dashboard-stat-card ${
//         special ? "dashboard-stat-special" : ""
//       }`}
//     >
//       <div className="dashboard-stat-top">
//         <p>{title}</p>
//         <div className="dashboard-stat-icon">{icon}</div>
//       </div>

//       <div className="dashboard-stat-value">
//         <h3>{value}</h3>
//         {suffix && <span>{suffix}</span>}
//       </div>
//     </div>
//   );
// }

// function BadgeItem({ icon, title, earned, color }) {
//   return (
//     <div
//       className={`dashboard-badge-item ${
//         earned
//           ? `dashboard-badge-earned dashboard-badge-${color}`
//           : "dashboard-badge-locked"
//       }`}
//     >
//       <div className="dashboard-badge-icon">{icon}</div>
//       <h4>{title}</h4>
//     </div>
//   );
// }

// function StarIcon(props) {
//   return (
//     <svg
//       xmlns="http://www.w3.org/2000/svg"
//       width={props.width || 20}
//       height={props.height || 20}
//       viewBox="0 0 24 24"
//       fill="none"
//       stroke="currentColor"
//       strokeWidth="2"
//       strokeLinecap="round"
//       strokeLinejoin="round"
//       {...props}
//     >
//       <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
//     </svg>
//   );
// }
import React, { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router";
import {
  BarChart3,
  LayoutDashboard,
  LineChart,
  Target,
  Zap,
  History,
  Award,
  Calendar,
  Loader2,
  LogOut,
  X,
  Eye,
  ChevronRight,
  ExternalLink,
  MessageSquare,
  Briefcase,
  User,
  Clock,
  FileText,
  BookOpen,
  Brain,
  ClipboardCheck,
  Mic,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { useAuthStore } from "../store/useAuthStore";
import { supabase } from "../lib/supabase";
import "./Dashboard.css";

const RAG_FEATURES = [
  {
    title: "Study from Notes",
    desc: "Upload PDFs, ask questions, summarize notes, and generate study questions.",
    path: "/study-notes",
    icon: BookOpen,
    tag: "RAG Notes",
  },
  {
    title: "Resume Gap Finder",
    desc: "Upload your resume and compare it with a job description using AI.",
    path: "/resume-gap-finder",
    icon: ClipboardCheck,
    tag: "Resume + JD",
  },
  {
    title: "Generate Flashcards",
    desc: "Create MCQ flashcards from your uploaded notes for quick revision.",
    path: "/flashcards",
    icon: Brain,
    tag: "MCQ Practice",
  },
];

function getNumberOrNull(value) {
  if (value === null || value === undefined || value === "") {
    return null;
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return null;
  }

  return number;
}

function formatScore(value) {
  const number = getNumberOrNull(value);

  if (number === null) {
    return "Not measured";
  }

  return number.toFixed(1);
}

function getScoreClass(value) {
  const number = getNumberOrNull(value);

  if (number === null) {
    return "dashboard-score-neutral";
  }

  if (number >= 8) {
    return "dashboard-score-good";
  }

  if (number >= 6) {
    return "dashboard-score-mid";
  }

  return "dashboard-score-low";
}

function getAverageScoreFromSessions(sessions) {
  const validScores = sessions
    .map((session) => getNumberOrNull(session.score_overall))
    .filter((score) => score !== null);

  if (validScores.length === 0) {
    return "0.0";
  }

  const total = validScores.reduce((acc, score) => acc + score, 0);

  return (total / validScores.length).toFixed(1);
}

function getBestScoreFromSessions(sessions) {
  const validScores = sessions
    .map((session) => getNumberOrNull(session.score_overall))
    .filter((score) => score !== null);

  if (validScores.length === 0) {
    return "0.0";
  }

  return Math.max(...validScores).toFixed(1);
}

export default function Dashboard() {
  const { user, signOut } = useAuthStore();
  const navigate = useNavigate();

  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState(null);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [fetchError, setFetchError] = useState("");

  useEffect(() => {
    const fetchSessions = async () => {
      if (!user?.id) {
        setSessions([]);
        setLoading(false);
        return;
      }

      setLoading(true);
      setFetchError("");

      try {
        const { data, error } = await supabase
          .from("session_scores")
          .select("*")
          .eq("user_id", user.id)
          .order("created_at", { ascending: true });

        if (error) {
          console.error("Dashboard fetch error:", error);
          setFetchError(error?.message || "Failed to load dashboard data.");
          setSessions([]);
          return;
        }

        setSessions(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Unexpected dashboard error:", err);
        setFetchError(err?.message || "Unexpected dashboard error.");
        setSessions([]);
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, [user]);

  const handleSignOut = async () => {
    await signOut();
    navigate("/login");
  };

  const totalSessions = sessions.length;

  const averageScore = useMemo(() => {
    return getAverageScoreFromSessions(sessions);
  }, [sessions]);

  const bestScore = useMemo(() => {
    return getBestScoreFromSessions(sessions);
  }, [sessions]);

  const chartData = useMemo(() => {
    return sessions.map((session, index) => {
      const createdDate = session.created_at
        ? new Date(session.created_at)
        : new Date();

      const score = getNumberOrNull(session.score_overall);

      return {
        date: createdDate.toLocaleDateString(undefined, {
          month: "short",
          day: "numeric",
        }),
        score: score === null ? 0 : score,
        track: session.track || "General",
        difficulty: session.difficulty || "Fresher",
        sessionNo: index + 1,
      };
    });
  }, [sessions]);

  const hasEyeContactPro = sessions.some((session) => {
    const eyeContact = getNumberOrNull(session.score_eye_contact);
    const bodyLanguage = getNumberOrNull(session.score_body_language);

    return (
      (eyeContact !== null && eyeContact >= 9) ||
      (bodyLanguage !== null && bodyLanguage >= 9)
    );
  });

  const has90Club = sessions.some((session) => {
    const overall = getNumberOrNull(session.score_overall);
    return overall !== null && overall >= 9;
  });

  const has5Streak = totalSessions >= 5;

  if (loading) {
    return (
      <div className="dashboard-loading">
        <Loader2 className="dashboard-loading-icon" />
        <span>Loading your dashboard...</span>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <aside className="dashboard-sidebar">
        <div className="dashboard-logo">
          <div className="dashboard-logo-icon">
            <Zap size={17} />
          </div>

          <span>InterviewIQ</span>
        </div>

        <nav className="dashboard-nav">
          <button
            type="button"
            onClick={() => setActiveTab("dashboard")}
            className={`dashboard-nav-btn ${
              activeTab === "dashboard" ? "dashboard-nav-btn-active" : ""
            }`}
          >
            <LayoutDashboard size={20} />
            <span>Dashboard</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("sessions")}
            className={`dashboard-nav-btn ${
              activeTab === "sessions" ? "dashboard-nav-btn-active" : ""
            }`}
          >
            <History size={20} />
            <span>Past Sessions</span>
          </button>

          <button
            type="button"
            onClick={() => navigate("/study-notes")}
            className="dashboard-nav-btn"
          >
            <BookOpen size={20} />
            <span>Study Notes</span>
          </button>

          <button
            type="button"
            onClick={() => navigate("/resume-gap-finder")}
            className="dashboard-nav-btn"
          >
            <ClipboardCheck size={20} />
            <span>Resume Gap</span>
          </button>

          <button
            type="button"
            onClick={() => navigate("/flashcards")}
            className="dashboard-nav-btn"
          >
            <Brain size={20} />
            <span>Flashcards</span>
          </button>
        </nav>

        <div className="dashboard-user-box">
          <div className="dashboard-user-info">
            <div className="dashboard-avatar">
              {user?.email?.[0]?.toUpperCase() || "U"}
            </div>

            <div className="dashboard-user-text">
              <p>{user?.email?.split("@")[0] || "User"}</p>
              <span>{user?.email || "No email found"}</span>
            </div>
          </div>

          <button
            type="button"
            onClick={handleSignOut}
            className="dashboard-signout-btn"
          >
            <LogOut size={17} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      <main className="dashboard-main">
        <div className="dashboard-container">
          <div className="dashboard-header">
            <div>
              <h1>
                {activeTab === "dashboard"
                  ? "Welcome Back"
                  : "Past Sessions"}
              </h1>

              <p>
                {activeTab === "dashboard"
                  ? totalSessions === 0
                    ? "You have not completed any interviews yet. Start your first practice."
                    : "Your interview performance overview."
                  : `${totalSessions} interview sessions recorded.`}
              </p>
            </div>

            <div className="dashboard-header-actions">
              <Link to="/study-notes" className="dashboard-tool-btn">
                <BookOpen size={17} />
                <span>Study Notes</span>
              </Link>

              <Link to="/resume-gap-finder" className="dashboard-tool-btn">
                <ClipboardCheck size={17} />
                <span>Resume Gap</span>
              </Link>

              <Link to="/setup" className="dashboard-new-btn">
                <Mic size={17} />
                <span>New Practice</span>
                <ChevronRight size={17} />
              </Link>
            </div>
          </div>

          {fetchError && (
            <div className="interview-error-box">
              {typeof fetchError === "string"
                ? fetchError
                : JSON.stringify(fetchError)}
            </div>
          )}

          {activeTab === "dashboard" && (
            <>
              <section className="dashboard-card dashboard-rag-card">
                <div className="dashboard-section-title">
                  <Brain size={20} />
                  <h2>AI Study Tools</h2>
                </div>

                <p className="dashboard-rag-subtitle">
                  Use your FastAPI RAG backend for notes, flashcards, and resume
                  gap analysis.
                </p>

                <div className="dashboard-rag-grid">
                  {RAG_FEATURES.map((feature) => {
                    const Icon = feature.icon;

                    return (
                      <button
                        key={feature.title}
                        type="button"
                        onClick={() => navigate(feature.path)}
                        className="dashboard-rag-feature-card"
                      >
                        <div className="dashboard-rag-feature-top">
                          <div className="dashboard-rag-feature-icon">
                            <Icon size={24} />
                          </div>

                          <span>{feature.tag}</span>
                        </div>

                        <h3>{feature.title}</h3>
                        <p>{feature.desc}</p>

                        <div className="dashboard-rag-feature-link">
                          <span>Open Tool</span>
                          <ChevronRight size={16} />
                        </div>
                      </button>
                    );
                  })}
                </div>
              </section>

              <div className="dashboard-stats-grid">
                <StatCard
                  title="Total Sessions"
                  value={totalSessions}
                  icon={<History size={20} />}
                />

                <StatCard
                  title="Average Score"
                  value={averageScore}
                  suffix="/10"
                  icon={<BarChart3 size={20} />}
                />

                <StatCard
                  title="Best Score"
                  value={bestScore}
                  icon={<StarIcon />}
                  special
                />

                <StatCard
                  title="Consistency"
                  value={totalSessions}
                  suffix=" sessions"
                  icon={<Zap size={20} />}
                />
              </div>

              <div className="dashboard-overview-grid">
                <section className="dashboard-card dashboard-chart-card">
                  <div className="dashboard-section-title">
                    <LineChart size={20} />
                    <h2>Performance Growth</h2>
                  </div>

                  <div className="dashboard-chart-area">
                    {totalSessions === 0 ? (
                      <div className="dashboard-empty-chart">
                        <Target size={38} />
                        <p>Complete your first session to unlock charts.</p>
                      </div>
                    ) : (
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData}>
                          <defs>
                            <linearGradient
                              id="colorScore"
                              x1="0"
                              y1="0"
                              x2="0"
                              y2="1"
                            >
                              <stop
                                offset="5%"
                                stopColor="var(--dash-primary)"
                                stopOpacity={0.3}
                              />

                              <stop
                                offset="95%"
                                stopColor="var(--dash-primary)"
                                stopOpacity={0}
                              />
                            </linearGradient>
                          </defs>

                          <CartesianGrid
                            strokeDasharray="3 3"
                            vertical={false}
                            stroke="var(--dash-border)"
                          />

                          <XAxis
                            dataKey="date"
                            axisLine={false}
                            tickLine={false}
                            tick={{
                              fill: "var(--dash-muted)",
                              fontSize: 12,
                            }}
                            dy={10}
                          />

                          <YAxis
                            domain={[0, 10]}
                            axisLine={false}
                            tickLine={false}
                            tick={{
                              fill: "var(--dash-muted)",
                              fontSize: 12,
                            }}
                            dx={-10}
                          />

                          <Tooltip
                            contentStyle={{
                              backgroundColor: "var(--dash-card)",
                              borderRadius: "14px",
                              border: "1px solid var(--dash-border)",
                              color: "var(--dash-text)",
                            }}
                            itemStyle={{
                              color: "var(--dash-text)",
                              fontWeight: "700",
                            }}
                          />

                          <Area
                            type="monotone"
                            dataKey="score"
                            stroke="var(--dash-primary)"
                            strokeWidth={3}
                            fillOpacity={1}
                            fill="url(#colorScore)"
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    )}
                  </div>
                </section>

                <section className="dashboard-card dashboard-badges-card">
                  <div className="dashboard-section-title dashboard-section-title-secondary">
                    <Award size={20} />
                    <h2>Badges</h2>
                  </div>

                  <div className="dashboard-badge-grid">
                    <BadgeItem
                      icon={<Eye size={25} />}
                      title="Eye Contact Pro"
                      earned={hasEyeContactPro}
                      color="secondary"
                    />

                    <BadgeItem
                      icon={<StarIcon width="25" height="25" />}
                      title="90+ Club"
                      earned={has90Club}
                      color="yellow"
                    />

                    <div className="dashboard-badge-wide">
                      <BadgeItem
                        icon={<Zap size={22} />}
                        title={`5-Session Streak ${
                          !has5Streak ? "(Locked)" : ""
                        }`}
                        earned={has5Streak}
                        color="primary"
                      />
                    </div>
                  </div>
                </section>
              </div>
            </>
          )}

          <section className="dashboard-card dashboard-table-card">
            <h2 className="dashboard-table-title">
              {activeTab === "sessions" ? "All Sessions" : "Recent Sessions"}
            </h2>

            <div className="dashboard-table-wrapper">
              <table className="dashboard-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Track</th>
                    <th>Level</th>
                    <th className="dashboard-text-right">Score</th>
                    <th className="dashboard-text-center">Report</th>
                  </tr>
                </thead>

                <tbody>
                  {sessions.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="dashboard-no-data">
                        No sessions recorded yet. Start your first practice.
                      </td>
                    </tr>
                  ) : (
                    sessions
                      .slice()
                      .reverse()
                      .slice(0, activeTab === "sessions" ? undefined : 5)
                      .map((session) => {
                        const score = getNumberOrNull(session.score_overall);

                        return (
                          <tr key={session.id}>
                            <td>
                              <div className="dashboard-date-cell">
                                <Calendar size={16} />
                                {session.created_at
                                  ? new Date(
                                      session.created_at
                                    ).toLocaleDateString()
                                  : "Unknown"}
                              </div>
                            </td>

                            <td className="dashboard-track-cell">
                              {session.track || "General"}
                            </td>

                            <td>
                              <span className="dashboard-level-pill">
                                {session.difficulty || "Fresher"}
                              </span>
                            </td>

                            <td className="dashboard-text-right">
                              <span
                                className={`dashboard-score ${getScoreClass(
                                  score
                                )}`}
                              >
                                {formatScore(score)}
                              </span>
                            </td>

                            <td className="dashboard-text-center">
                              <button
                                type="button"
                                onClick={() => setSelectedReport(session)}
                                className="dashboard-view-btn"
                              >
                                <span>View</span>
                                <ExternalLink size={13} />
                              </button>
                            </td>
                          </tr>
                        );
                      })
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </main>

      {selectedReport && (
        <ReportModal
          report={selectedReport}
          onClose={() => setSelectedReport(null)}
        />
      )}
    </div>
  );
}

function ReportModal({ report, onClose }) {
  const data = report.report_json || {};
  const setup = data.setup || {};
  const transcript = Array.isArray(data.transcript) ? data.transcript : [];

  const overallScore = getNumberOrNull(report.score_overall);
  const communicationScore = getNumberOrNull(report.score_communication);
  const confidenceScore = getNumberOrNull(report.score_confidence);
  const bodyLanguageScore = getNumberOrNull(report.score_body_language);
  const eyeContactScore = getNumberOrNull(report.score_eye_contact);
  const speakingPaceScore = getNumberOrNull(report.score_speaking_pace);

  const durationSeconds = Number(
    report.duration_seconds || data.durationSeconds || 0
  );

  const formattedDuration =
    durationSeconds > 0
      ? `${Math.floor(durationSeconds / 60)}m ${durationSeconds % 60}s`
      : "Not tracked";

  const summary =
    typeof data.overallSummary === "string"
      ? data.overallSummary
      : "Vapi voice interview completed. Transcript and score are saved.";

  const scoreReason =
    typeof data.scoreReason === "string"
      ? data.scoreReason
      : data.groqScoring?.scoreReason || "";

  const cameraMetrics =
    data.cameraMetrics ||
    data.groqScoring?.cameraMetrics ||
    data.groqScoring?.camera_metrics ||
    {};

  return (
    <div className="dashboard-modal-overlay" onClick={onClose}>
      <div
        className="dashboard-modal"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="dashboard-modal-header">
          <div>
            <h2>Session Report</h2>

            <div className="dashboard-modal-tags">
              <span className="dashboard-modal-tag-primary">
                {report.track || "General"}
              </span>

              <span>{report.difficulty || "Fresher"}</span>

              <span>
                {report.created_at
                  ? new Date(report.created_at).toLocaleDateString()
                  : "Unknown date"}
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="dashboard-modal-close"
          >
            <X size={20} />
          </button>
        </div>

        <div className="dashboard-overall-score-box">
          <p>Overall Score</p>
          <h3>{formatScore(overallScore)}</h3>
          <span>out of 10</span>
        </div>

        <div className="dashboard-score-grid">
          <ScoreItem label="Communication" value={communicationScore} />
          <ScoreItem label="Confidence" value={confidenceScore} />
          <ScoreItem label="Body Language" value={bodyLanguageScore} />
          <ScoreItem label="Eye Contact" value={eyeContactScore} />
          <ScoreItem label="Speaking Pace" value={speakingPaceScore} />
          <ScoreItem label="Duration" value={formattedDuration} isText />
        </div>

        <div className="dashboard-report-section">
          <h3>Summary</h3>
          <p>{summary}</p>
        </div>

        {scoreReason && (
          <div className="dashboard-report-section">
            <h3>Score Reason</h3>
            <p>{scoreReason}</p>
          </div>
        )}

        <div className="dashboard-report-section">
          <h3>Interview Setup</h3>

          <div className="dashboard-report-meta-grid">
            <ReportMetaItem
              icon={<Briefcase size={16} />}
              label="Track"
              value={report.track || setup.track || "General"}
            />

            <ReportMetaItem
              icon={<User size={16} />}
              label="Difficulty"
              value={report.difficulty || setup.difficulty || "Fresher"}
            />

            <ReportMetaItem
              icon={<FileText size={16} />}
              label="Resume"
              value={setup.resumeFileName || "Not uploaded"}
            />

            <ReportMetaItem
              icon={<MessageSquare size={16} />}
              label="Messages"
              value={String(data.totalMessages || transcript.length || 0)}
            />

            <ReportMetaItem
              icon={<Clock size={16} />}
              label="Duration"
              value={formattedDuration}
            />

            <ReportMetaItem
              icon={<MessageSquare size={16} />}
              label="JD"
              value={setup.hasJobDescription ? "Added" : "Not added"}
            />
          </div>
        </div>

        {cameraMetrics && Object.keys(cameraMetrics).length > 0 && (
          <div className="dashboard-report-section">
            <h3>Camera / Speaking Metrics</h3>

            <div className="dashboard-report-meta-grid">
              <ReportMetaItem
                icon={<Eye size={16} />}
                label="Eye Contact"
                value={
                  cameraMetrics.eye_contact_percent !== undefined
                    ? `${cameraMetrics.eye_contact_percent}%`
                    : cameraMetrics.eyeContactPercent !== undefined
                    ? `${cameraMetrics.eyeContactPercent}%`
                    : "Tracked"
                }
              />

              <ReportMetaItem
                icon={<User size={16} />}
                label="Face Visible"
                value={
                  cameraMetrics.face_visible_percent !== undefined
                    ? `${cameraMetrics.face_visible_percent}%`
                    : cameraMetrics.faceVisiblePercent !== undefined
                    ? `${cameraMetrics.faceVisiblePercent}%`
                    : "Tracked"
                }
              />

              <ReportMetaItem
                icon={<Target size={16} />}
                label="Centered Face"
                value={
                  cameraMetrics.centered_face_percent !== undefined
                    ? `${cameraMetrics.centered_face_percent}%`
                    : cameraMetrics.centeredFacePercent !== undefined
                    ? `${cameraMetrics.centeredFacePercent}%`
                    : "Tracked"
                }
              />

              <ReportMetaItem
                icon={<Mic size={16} />}
                label="Words / Min"
                value={
                  cameraMetrics.words_per_minute !== undefined
                    ? String(cameraMetrics.words_per_minute)
                    : cameraMetrics.wordsPerMinute !== undefined
                    ? String(cameraMetrics.wordsPerMinute)
                    : "Tracked"
                }
              />
            </div>
          </div>
        )}

        {Array.isArray(data.improvementTips) &&
          data.improvementTips.length > 0 && (
            <div className="dashboard-report-section">
              <h3>Improvement Tips</h3>

              <div className="dashboard-tips-list">
                {data.improvementTips.map((tip, index) => (
                  <div key={index} className="dashboard-tip-item">
                    <span>{index + 1}</span>
                    <p>{String(tip)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

        {Array.isArray(data.strengths) && data.strengths.length > 0 && (
          <div className="dashboard-report-section">
            <h3>Strengths</h3>

            <div className="dashboard-tips-list">
              {data.strengths.map((item, index) => (
                <div key={index} className="dashboard-tip-item">
                  <span>{index + 1}</span>
                  <p>{String(item)}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {Array.isArray(data.weaknesses) && data.weaknesses.length > 0 && (
          <div className="dashboard-report-section">
            <h3>Weak Areas</h3>

            <div className="dashboard-tips-list">
              {data.weaknesses.map((item, index) => (
                <div key={index} className="dashboard-tip-item">
                  <span>{index + 1}</span>
                  <p>{String(item)}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="dashboard-report-section">
          <h3>Transcript</h3>

          {transcript.length === 0 ? (
            <p>No transcript captured for this session.</p>
          ) : (
            <div className="dashboard-transcript-box">
              {transcript.map((message, index) => {
                const isUser = message.role === "user";
                const roleLabel = isUser ? "You" : "AI Interviewer";

                return (
                  <div
                    key={`${message.role}-${index}`}
                    className={`dashboard-transcript-item ${
                      isUser
                        ? "dashboard-transcript-user"
                        : "dashboard-transcript-ai"
                    }`}
                  >
                    <strong>{roleLabel}</strong>
                    <p>{String(message.content || "")}</p>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ReportMetaItem({ icon, label, value }) {
  return (
    <div className="dashboard-report-meta-item">
      <div className="dashboard-report-meta-icon">{icon}</div>

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

function ScoreItem({ label, value, isText = false }) {
  if (isText) {
    return (
      <div className="dashboard-score-item">
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    );
  }

  return (
    <div className="dashboard-score-item">
      <span>{label}</span>
      <strong className={getScoreClass(value)}>{formatScore(value)}</strong>
    </div>
  );
}

function StatCard({ title, value, icon, suffix = "", special = false }) {
  return (
    <div
      className={`dashboard-stat-card ${
        special ? "dashboard-stat-special" : ""
      }`}
    >
      <div className="dashboard-stat-top">
        <p>{title}</p>
        <div className="dashboard-stat-icon">{icon}</div>
      </div>

      <div className="dashboard-stat-value">
        <h3>{value}</h3>
        {suffix && <span>{suffix}</span>}
      </div>
    </div>
  );
}

function BadgeItem({ icon, title, earned, color }) {
  return (
    <div
      className={`dashboard-badge-item ${
        earned
          ? `dashboard-badge-earned dashboard-badge-${color}`
          : "dashboard-badge-locked"
      }`}
    >
      <div className="dashboard-badge-icon">{icon}</div>
      <h4>{title}</h4>
    </div>
  );
}

function StarIcon(props) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={props.width || 20}
      height={props.height || 20}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
    </svg>
  );
}