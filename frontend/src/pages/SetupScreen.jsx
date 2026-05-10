// import React, { useEffect, useRef, useState } from "react";
// import { Link, useNavigate } from "react-router";
// import {
//   Briefcase,
//   Code,
//   User,
//   ChevronRight,
//   UploadCloud,
//   CheckCircle2,
//   Video,
//   Mic as MicIcon,
//   VideoOff,
//   Settings,
//   FileText,
//   X,
//   Loader2,
//   Building2,
//   ClipboardList,
//   Hash,
//   PencilLine,
// } from "lucide-react";

// import { useInterviewStore } from "../store/useInterviewStore";
// import "./SetupScreen.css";

// const TRACKS = [
//   {
//     id: "HR",
//     title: "HR & Behavioral",
//     icon: User,
//     desc: "Culture-fit, teamwork, and leadership questions.",
//   },
//   {
//     id: "Technical",
//     title: "Technical",
//     icon: Code,
//     desc: "Coding, architecture, and problem-solving.",
//   },
//   {
//     id: "General",
//     title: "General",
//     icon: Briefcase,
//     desc: "A mix of all standard interview topics.",
//   },
// ];

// const DIFFICULTIES = [
//   {
//     id: "Fresher",
//     label: "Fresher",
//     desc: "Entry-level, 0-1 yrs",
//   },
//   {
//     id: "Mid-Level",
//     label: "Mid-Level",
//     desc: "2-5 years experience",
//   },
//   {
//     id: "Senior",
//     label: "Senior",
//     desc: "5+ years, leadership",
//   },
// ];

// const QUESTION_COUNTS = [5, 10, 15, 20];

// export default function SetupScreen() {
//   const navigate = useNavigate();

//   const {
//     track,
//     difficulty,
//     jobDescription,
//     resumeFileName,
//     interviewTitle,
//     interviewRole,
//     interviewCompany,
//     questionCount,

//     setTrack,
//     setDifficulty,
//     setJobDescription,
//     setResumeFileName,
//     setResumeText,
//     setInterviewTitle,
//     setInterviewRole,
//     setInterviewCompany,
//     setQuestionCount,
//     createInterviewFromSetup,
//   } = useInterviewStore();

//   const videoRef = useRef(null);
//   const streamRef = useRef(null);

//   const [mediaError, setMediaError] = useState("");
//   const [resumeLoading, setResumeLoading] = useState(false);
//   const [resumeParsed, setResumeParsed] = useState(false);

//   useEffect(() => {
//     const startMediaPreview = async () => {
//       try {
//         if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
//           setMediaError(
//             "Your browser does not support camera and microphone access."
//           );
//           return;
//         }

//         const mediaStream = await navigator.mediaDevices.getUserMedia({
//           video: true,
//           audio: true,
//         });

//         streamRef.current = mediaStream;

//         if (videoRef.current) {
//           videoRef.current.srcObject = mediaStream;
//         }
//       } catch (error) {
//         console.error("Media permission denied:", error);

//         setMediaError(
//           "Camera and Microphone permissions are required for the interview."
//         );
//       }
//     };

//     startMediaPreview();

//     return () => {
//       stopPreviewStream();
//     };
//   }, []);

//   const stopPreviewStream = () => {
//     if (streamRef.current) {
//       streamRef.current.getTracks().forEach((trackItem) => {
//         trackItem.stop();
//       });

//       streamRef.current = null;
//     }

//     if (videoRef.current) {
//       videoRef.current.srcObject = null;
//     }
//   };

//   const handleResumeUpload = async (event) => {
//     const file = event.target.files?.[0];

//     if (!file) {
//       return;
//     }

//     if (file.type !== "application/pdf") {
//       setResumeFileName(null);
//       setResumeText("");
//       setResumeParsed(false);
//       alert("Please upload only a PDF file.");
//       return;
//     }

//     if (file.size > 5 * 1024 * 1024) {
//       setResumeFileName(null);
//       setResumeText("");
//       setResumeParsed(false);
//       alert("PDF size should be less than 5MB.");
//       return;
//     }

//     setResumeFileName(file.name);
//     setResumeText("");
//     setResumeLoading(true);
//     setResumeParsed(false);

//     try {
//       const pdfjsLib = await import("pdfjs-dist");

//       pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.mjs`;

//       const arrayBuffer = await file.arrayBuffer();

//       const pdf = await pdfjsLib.getDocument({
//         data: arrayBuffer,
//       }).promise;

//       let fullText = "";

//       for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
//         const page = await pdf.getPage(pageNumber);
//         const textContent = await page.getTextContent();

//         const pageText = textContent.items
//           .map((item) => item.str || "")
//           .join(" ");

//         fullText += pageText + "\n";
//       }

//       const cleanedText = fullText.trim();

//       setResumeText(cleanedText);
//       setResumeParsed(Boolean(cleanedText));

//       console.log(
//         `Resume parsed: ${cleanedText.length} characters extracted from ${pdf.numPages} pages.`
//       );
//     } catch (error) {
//       console.error("Failed to parse PDF:", error);

//       setResumeText("");
//       setResumeParsed(false);

//       alert(
//         "Resume uploaded, but text could not be extracted. You can still continue using JD and selected track."
//       );
//     } finally {
//       setResumeLoading(false);
//     }
//   };

//   const clearResume = () => {
//     setResumeFileName(null);
//     setResumeText("");
//     setResumeParsed(false);
//   };

//   const beginInterview = () => {
//     if (!track || !difficulty) {
//       alert("Please select interview track and experience level.");
//       return;
//     }

//     if (resumeLoading) {
//       alert("Please wait. Resume text is still being extracted.");
//       return;
//     }

//     const createdInterview = createInterviewFromSetup();

//     console.log("Created interview setup:", createdInterview);

//     stopPreviewStream();

//     navigate("/interview", {
//       state: {
//         fromSetup: true,
//         interviewId: createdInterview.id,
//       },
//     });
//   };

//   const isReady = track !== null && difficulty !== null && !resumeLoading;

//   return (
//     <div className="setup-page">
//       <div className="setup-bg-glow setup-bg-glow-one"></div>
//       <div className="setup-bg-glow setup-bg-glow-two"></div>
//       <div className="setup-bg-grid"></div>

//       <div className="setup-container">
//         <header className="setup-header">
//           <div className="setup-header-left">
//             <div className="setup-header-icon">
//               <Settings size={29} />
//             </div>

//             <div>
//               <h1>Interview Setup</h1>
//               <p>Create your own AI voice interview using Vapi.</p>
//             </div>
//           </div>

//           <Link to="/" className="setup-home-link" onClick={stopPreviewStream}>
//             ← Home
//           </Link>
//         </header>

//         <section className="setup-card">
//           <StepTitle number="1" title="Create Your Interview" />

//           <p className="setup-small-text">
//             Add role/company details so the AI interviewer can personalize the
//             conversation.
//           </p>

//           <div className="setup-custom-grid">
//             <InputField
//               icon={<PencilLine size={19} />}
//               label="Interview Title"
//               value={interviewTitle}
//               onChange={setInterviewTitle}
//               placeholder="Example: Frontend Developer Mock Interview"
//             />

//             <InputField
//               icon={<Briefcase size={19} />}
//               label="Target Role"
//               value={interviewRole}
//               onChange={setInterviewRole}
//               placeholder="Example: React Developer"
//             />

//             <InputField
//               icon={<Building2 size={19} />}
//               label="Company"
//               value={interviewCompany}
//               onChange={setInterviewCompany}
//               placeholder="Example: Google, TCS, Infosys"
//             />

//             <div className="setup-field-group">
//               <label>
//                 <Hash size={19} />
//                 Questions
//               </label>

//               <div className="setup-question-count-row">
//                 {QUESTION_COUNTS.map((count) => {
//                   const isSelected = Number(questionCount) === count;

//                   return (
//                     <button
//                       key={count}
//                       type="button"
//                       onClick={() => setQuestionCount(count)}
//                       className={`setup-question-count-btn ${
//                         isSelected ? "setup-question-count-btn-active" : ""
//                       }`}
//                     >
//                       {count}
//                     </button>
//                   );
//                 })}
//               </div>
//             </div>
//           </div>
//         </section>

//         <section className="setup-card">
//           <StepTitle number="2" title="Select Interview Track" />

//           <div className="setup-track-grid">
//             {TRACKS.map((item) => {
//               const Icon = item.icon;
//               const isSelected = track === item.id;

//               return (
//                 <button
//                   key={item.id}
//                   type="button"
//                   onClick={() => setTrack(item.id)}
//                   className={`setup-track-card ${
//                     isSelected ? "setup-track-card-active" : ""
//                   }`}
//                 >
//                   {isSelected && (
//                     <CheckCircle2 className="setup-selected-icon" size={21} />
//                   )}

//                   <Icon
//                     className={`setup-track-icon ${
//                       isSelected ? "setup-track-icon-active" : ""
//                     }`}
//                     size={27}
//                   />

//                   <h3>{item.title}</h3>
//                   <p>{item.desc}</p>
//                 </button>
//               );
//             })}
//           </div>
//         </section>

//         <section className="setup-card">
//           <StepTitle number="3" title="Select Experience Level" />

//           <div className="setup-difficulty-grid">
//             {DIFFICULTIES.map((level) => {
//               const isSelected = difficulty === level.id;

//               return (
//                 <button
//                   key={level.id}
//                   type="button"
//                   onClick={() => setDifficulty(level.id)}
//                   className={`setup-difficulty-card ${
//                     isSelected ? "setup-difficulty-card-active" : ""
//                   }`}
//                 >
//                   <strong>{level.label}</strong>
//                   <span>{level.desc}</span>
//                 </button>
//               );
//             })}
//           </div>
//         </section>

//         <div className="setup-two-column-grid">
//           <div className="setup-left-stack">
//             <section className="setup-card">
//               <StepTitle number="4" title="Job Description" optional />

//               <p className="setup-small-text">
//                 Paste the JD and Vapi AI will ask role-specific questions.
//               </p>

//               <textarea
//                 value={jobDescription}
//                 onChange={(event) => setJobDescription(event.target.value)}
//                 placeholder="Paste the job description or role requirements here..."
//                 className="setup-textarea"
//               />
//             </section>

//             <section className="setup-card">
//               <StepTitle number="5" title="Upload Resume" optional />

//               <p className="setup-small-text">
//                 Upload your PDF resume for personalized questions based on your
//                 experience.
//               </p>

//               {resumeFileName ? (
//                 <div className="setup-uploaded-file">
//                   <div className="setup-file-icon">
//                     <FileText size={26} />
//                   </div>

//                   <div className="setup-file-info">
//                     <p>{resumeFileName}</p>

//                     <span>
//                       {resumeLoading ? (
//                         <span className="setup-file-loading">
//                           <Loader2 size={13} />
//                           Extracting text...
//                         </span>
//                       ) : resumeParsed ? (
//                         <span className="setup-file-success">
//                           ✓ Resume parsed successfully
//                         </span>
//                       ) : (
//                         "Uploaded"
//                       )}
//                     </span>
//                   </div>

//                   <button
//                     type="button"
//                     onClick={clearResume}
//                     className="setup-clear-file-btn"
//                   >
//                     <X size={21} />
//                   </button>
//                 </div>
//               ) : (
//                 <label className="setup-upload-box">
//                   <UploadCloud size={36} />

//                   <span>Click to upload PDF</span>
//                   <small>PDF max 5MB</small>

//                   <input
//                     type="file"
//                     accept="application/pdf"
//                     onChange={handleResumeUpload}
//                   />
//                 </label>
//               )}
//             </section>
//           </div>

//           <section className="setup-card setup-device-card">
//             <StepTitle number="6" title="Device Check" />

//             <p className="setup-small-text">
//               Ensure your face is clearly visible and your microphone is
//               available.
//             </p>

//             <div className="setup-video-box">
//               {mediaError ? (
//                 <div className="setup-media-error">
//                   <VideoOff size={42} />

//                   <p>{mediaError}</p>

//                   <span>
//                     Please allow camera and mic access in your browser settings.
//                   </span>
//                 </div>
//               ) : (
//                 <video
//                   ref={videoRef}
//                   autoPlay
//                   playsInline
//                   muted
//                   className="setup-video-preview"
//                 />
//               )}

//               {!mediaError && (
//                 <div className="setup-device-status">
//                   <div className="setup-ready-status">
//                     <span></span>
//                     System Ready
//                   </div>

//                   <div className="setup-device-icons">
//                     <MicIcon size={21} />
//                     <Video size={21} />
//                   </div>
//                 </div>
//               )}
//             </div>

//             <div className="setup-device-note">
//               <ClipboardList size={18} />
//               <span>
//                 Vapi will ask for microphone permission again when the call
//                 starts.
//               </span>
//             </div>
//           </section>
//         </div>

//         <footer className="setup-bottom-bar">
//           <Link to="/" className="setup-back-link" onClick={stopPreviewStream}>
//             ← Go Back
//           </Link>

//           <button
//             type="button"
//             onClick={beginInterview}
//             disabled={!isReady}
//             className={`setup-begin-btn ${
//               isReady ? "setup-begin-btn-ready" : ""
//             }`}
//           >
//             <span>{resumeLoading ? "Reading Resume..." : "Begin Interview"}</span>
//             {resumeLoading ? (
//               <Loader2 size={21} className="setup-spin-icon" />
//             ) : (
//               <ChevronRight size={21} />
//             )}
//           </button>
//         </footer>
//       </div>
//     </div>
//   );
// }

// function StepTitle({ number, title, optional = false }) {
//   return (
//     <h2 className="setup-step-title">
//       <span>{number}</span>
//       {title}
//       {optional && <small>(Optional)</small>}
//     </h2>
//   );
// }

// function InputField({ icon, label, value, onChange, placeholder }) {
//   return (
//     <div className="setup-field-group">
//       <label>
//         {icon}
//         {label}
//       </label>

//       <input
//         type="text"
//         value={value || ""}
//         onChange={(event) => onChange(event.target.value)}
//         placeholder={placeholder}
//         className="setup-input"
//       />
//     </div>
//   );
// }
import React, { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router";
import {
  Briefcase,
  Code,
  User,
  ChevronRight,
  UploadCloud,
  CheckCircle2,
  Video,
  Mic as MicIcon,
  VideoOff,
  Settings,
  FileText,
  X,
  Loader2,
  Building2,
  ClipboardList,
  Hash,
  PencilLine,
  Plus,
  Search,
  Tags,
} from "lucide-react";

import { useInterviewStore } from "../store/useInterviewStore";
import "./SetupScreen.css";

const TRACKS = [
  {
    id: "HR",
    title: "HR & Behavioral",
    icon: User,
    desc: "Culture-fit, teamwork, and leadership questions.",
  },
  {
    id: "Technical",
    title: "Technical",
    icon: Code,
    desc: "Coding, architecture, and problem-solving.",
  },
  {
    id: "General",
    title: "General",
    icon: Briefcase,
    desc: "A mix of all standard interview topics.",
  },
];

const DIFFICULTIES = [
  {
    id: "Fresher",
    label: "Fresher",
    desc: "Entry-level, 0-1 yrs",
  },
  {
    id: "Mid-Level",
    label: "Mid-Level",
    desc: "2-5 years experience",
  },
  {
    id: "Senior",
    label: "Senior",
    desc: "5+ years, leadership",
  },
];

const QUESTION_COUNTS = [5, 10, 15, 20];

const SKILL_OPTIONS = [
  "JavaScript",
  "TypeScript",
  "React",
  "Next.js",
  "Node.js",
  "Express.js",
  "MongoDB",
  "SQL",
  "PostgreSQL",
  "Python",
  "Java",
  "C++",
  "Data Structures",
  "Algorithms",
  "System Design",
  "HTML",
  "CSS",
  "Tailwind CSS",
  "Git",
  "GitHub",
  "REST API",
  "FastAPI",
  "Docker",
  "AWS",
  "Machine Learning",
  "Deep Learning",
  "NLP",
  "LLM",
  "RAG",
  "LangChain",
];

export default function SetupScreen() {
  const navigate = useNavigate();

  const {
    track,
    difficulty,
    jobDescription,
    resumeFileName,
    interviewTitle,
    interviewRole,
    interviewCompany,
    questionCount,

    setTrack,
    setDifficulty,
    setJobDescription,
    setResumeFileName,
    setResumeText,
    setInterviewTitle,
    setInterviewRole,
    setInterviewCompany,
    setQuestionCount,
    createInterviewFromSetup,

    interviewSkills,
    setInterviewSkills,
  } = useInterviewStore();

  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const skillDropdownRef = useRef(null);

  const [mediaError, setMediaError] = useState("");
  const [resumeLoading, setResumeLoading] = useState(false);
  const [resumeParsed, setResumeParsed] = useState(false);

  const [selectedSkills, setSelectedSkills] = useState(
    Array.isArray(interviewSkills) ? interviewSkills : []
  );
  const [skillSearch, setSkillSearch] = useState("");
  const [customSkill, setCustomSkill] = useState("");
  const [skillsDropdownOpen, setSkillsDropdownOpen] = useState(false);

  const filteredSkills = useMemo(() => {
    const search = skillSearch.trim().toLowerCase();

    return SKILL_OPTIONS.filter((skill) => {
      const alreadySelected = selectedSkills.some(
        (selected) => selected.toLowerCase() === skill.toLowerCase()
      );

      if (alreadySelected) {
        return false;
      }

      if (!search) {
        return true;
      }

      return skill.toLowerCase().includes(search);
    });
  }, [skillSearch, selectedSkills]);

  useEffect(() => {
    const startMediaPreview = async () => {
      try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          setMediaError(
            "Your browser does not support camera and microphone access."
          );
          return;
        }

        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });

        streamRef.current = mediaStream;

        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      } catch (error) {
        console.error("Media permission denied:", error);

        setMediaError(
          "Camera and Microphone permissions are required for the interview."
        );
      }
    };

    startMediaPreview();

    return () => {
      stopPreviewStream();
    };
  }, []);

  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (
        skillDropdownRef.current &&
        !skillDropdownRef.current.contains(event.target)
      ) {
        setSkillsDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleOutsideClick);

    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, []);

  const stopPreviewStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((trackItem) => {
        trackItem.stop();
      });

      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  const addSkill = (skill) => {
    const cleanSkill = String(skill || "").trim();

    if (!cleanSkill) {
      return;
    }

    const alreadySelected = selectedSkills.some(
      (selected) => selected.toLowerCase() === cleanSkill.toLowerCase()
    );

    if (alreadySelected) {
      setSkillSearch("");
      setCustomSkill("");
      return;
    }

    const updatedSkills = [...selectedSkills, cleanSkill];

    setSelectedSkills(updatedSkills);
    setSkillSearch("");
    setCustomSkill("");

    if (typeof setInterviewSkills === "function") {
      setInterviewSkills(updatedSkills);
    }
  };

  const removeSkill = (skillToRemove) => {
    const updatedSkills = selectedSkills.filter(
      (skill) => skill.toLowerCase() !== skillToRemove.toLowerCase()
    );

    setSelectedSkills(updatedSkills);

    if (typeof setInterviewSkills === "function") {
      setInterviewSkills(updatedSkills);
    }
  };

  const handleAddCustomSkill = () => {
    addSkill(customSkill);
  };

  const handleCustomSkillKeyDown = (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      handleAddCustomSkill();
    }
  };

  const handleResumeUpload = async (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (file.type !== "application/pdf") {
      setResumeFileName(null);
      setResumeText("");
      setResumeParsed(false);
      alert("Please upload only a PDF file.");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setResumeFileName(null);
      setResumeText("");
      setResumeParsed(false);
      alert("PDF size should be less than 5MB.");
      return;
    }

    setResumeFileName(file.name);
    setResumeText("");
    setResumeLoading(true);
    setResumeParsed(false);

    try {
      const pdfjsLib = await import("pdfjs-dist");

      pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.mjs`;

      const arrayBuffer = await file.arrayBuffer();

      const pdf = await pdfjsLib.getDocument({
        data: arrayBuffer,
      }).promise;

      let fullText = "";

      for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
        const page = await pdf.getPage(pageNumber);
        const textContent = await page.getTextContent();

        const pageText = textContent.items
          .map((item) => item.str || "")
          .join(" ");

        fullText += pageText + "\n";
      }

      const cleanedText = fullText.trim();

      setResumeText(cleanedText);
      setResumeParsed(Boolean(cleanedText));

      console.log(
        `Resume parsed: ${cleanedText.length} characters extracted from ${pdf.numPages} pages.`
      );
    } catch (error) {
      console.error("Failed to parse PDF:", error);

      setResumeText("");
      setResumeParsed(false);

      alert(
        "Resume uploaded, but text could not be extracted. You can still continue using JD and selected track."
      );
    } finally {
      setResumeLoading(false);
    }
  };

  const clearResume = () => {
    setResumeFileName(null);
    setResumeText("");
    setResumeParsed(false);
  };

  const beginInterview = () => {
    if (!track || !difficulty) {
      alert("Please select interview track and experience level.");
      return;
    }

    if (resumeLoading) {
      alert("Please wait. Resume text is still being extracted.");
      return;
    }

    if (typeof setInterviewSkills === "function") {
      setInterviewSkills(selectedSkills);
    }

    localStorage.setItem(
      "interview_setup_skills",
      JSON.stringify(selectedSkills)
    );

    const createdInterview = createInterviewFromSetup();

    const finalInterview = {
      ...createdInterview,
      skills: selectedSkills,
      selectedSkills,
    };

    console.log("Created interview setup:", finalInterview);

    stopPreviewStream();

    navigate("/interview", {
      state: {
        fromSetup: true,
        interviewId: createdInterview.id,
        selectedSkills,
      },
    });
  };

  const isReady = track !== null && difficulty !== null && !resumeLoading;

  return (
    <div className="setup-page">
      <div className="setup-bg-glow setup-bg-glow-one"></div>
      <div className="setup-bg-glow setup-bg-glow-two"></div>
      <div className="setup-bg-grid"></div>

      <div className="setup-container">
        <header className="setup-header">
          <div className="setup-header-left">
            <div className="setup-header-icon">
              <Settings size={29} />
            </div>

            <div>
              <h1>Interview Setup</h1>
              <p>Create your own AI voice interview using Vapi.</p>
            </div>
          </div>

          <Link to="/" className="setup-home-link" onClick={stopPreviewStream}>
            ← Home
          </Link>
        </header>

        <section className="setup-card setup-create-card">
          <StepTitle number="1" title="Create Your Interview" />

          <p className="setup-small-text">
            Add role/company details so the AI interviewer can personalize the
            conversation.
          </p>

          <div className="setup-custom-grid">
            <InputField
              icon={<PencilLine size={19} />}
              label="Interview Title"
              value={interviewTitle}
              onChange={setInterviewTitle}
              placeholder="Example: Frontend Developer Mock Interview"
            />

            <InputField
              icon={<Briefcase size={19} />}
              label="Target Role"
              value={interviewRole}
              onChange={setInterviewRole}
              placeholder="Example: React Developer"
            />

            <InputField
              icon={<Building2 size={19} />}
              label="Company"
              value={interviewCompany}
              onChange={setInterviewCompany}
              placeholder="Example: Google, TCS, Infosys"
            />

            <div className="setup-field-group">
              <label>
                <Hash size={19} />
                Questions
              </label>

              <div className="setup-question-count-row">
                {QUESTION_COUNTS.map((count) => {
                  const isSelected = Number(questionCount) === count;

                  return (
                    <button
                      key={count}
                      type="button"
                      onClick={() => setQuestionCount(count)}
                      className={`setup-question-count-btn ${
                        isSelected ? "setup-question-count-btn-active" : ""
                      }`}
                    >
                      {count}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <div
            className={`setup-skills-wrapper ${
              skillsDropdownOpen ? "setup-skills-wrapper-open" : ""
            }`}
          >
            <div className="setup-field-group setup-skills-field">
              <label>
                <Tags size={19} />
                Interview Skills
              </label>

              <div className="setup-skills-dropdown" ref={skillDropdownRef}>
                <button
                  type="button"
                  onClick={() => setSkillsDropdownOpen((prev) => !prev)}
                  className="setup-skills-dropdown-btn"
                >
                  <Search size={18} />

                  <span>
                    {selectedSkills.length > 0
                      ? `${selectedSkills.length} skill(s) selected`
                      : "Select skills from dropdown"}
                  </span>

                  <ChevronRight
                    size={18}
                    className={
                      skillsDropdownOpen ? "setup-dropdown-arrow-open" : ""
                    }
                  />
                </button>

                {skillsDropdownOpen && (
                  <div className="setup-skills-menu">
                    <input
                      type="text"
                      value={skillSearch}
                      onChange={(event) => setSkillSearch(event.target.value)}
                      placeholder="Search skills..."
                      className="setup-skills-search"
                    />

                    <div className="setup-skills-options">
                      {filteredSkills.length === 0 ? (
                        <p className="setup-no-skills">
                          No matching skills found.
                        </p>
                      ) : (
                        filteredSkills.map((skill) => (
                          <button
                            key={skill}
                            type="button"
                            onClick={() => addSkill(skill)}
                            className="setup-skill-option"
                          >
                            <Plus size={15} />
                            {skill}
                          </button>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="setup-field-group setup-custom-skill-field">
              <label>
                <PencilLine size={19} />
                Type Custom Skill
              </label>

              <div className="setup-custom-skill-row">
                <input
                  type="text"
                  value={customSkill}
                  onChange={(event) => setCustomSkill(event.target.value)}
                  onKeyDown={handleCustomSkillKeyDown}
                  placeholder="Example: Firebase, Redux, GraphQL"
                  className="setup-input"
                />

                <button
                  type="button"
                  onClick={handleAddCustomSkill}
                  className="setup-add-skill-btn"
                >
                  <Plus size={18} />
                  Add
                </button>
              </div>
            </div>
          </div>

          {selectedSkills.length > 0 && (
            <div className="setup-selected-skills">
              {selectedSkills.map((skill) => (
                <button
                  key={skill}
                  type="button"
                  onClick={() => removeSkill(skill)}
                  className="setup-skill-chip"
                  title="Click to remove"
                >
                  {skill}
                  <X size={14} />
                </button>
              ))}
            </div>
          )}
        </section>

        <section className="setup-card setup-track-section">
          <StepTitle number="2" title="Select Interview Track" />

          <div className="setup-track-grid">
            {TRACKS.map((item) => {
              const Icon = item.icon;
              const isSelected = track === item.id;

              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setTrack(item.id)}
                  className={`setup-track-card ${
                    isSelected ? "setup-track-card-active" : ""
                  }`}
                >
                  {isSelected && (
                    <CheckCircle2 className="setup-selected-icon" size={21} />
                  )}

                  <Icon
                    className={`setup-track-icon ${
                      isSelected ? "setup-track-icon-active" : ""
                    }`}
                    size={27}
                  />

                  <h3>{item.title}</h3>
                  <p>{item.desc}</p>
                </button>
              );
            })}
          </div>
        </section>

        <section className="setup-card setup-difficulty-section">
          <StepTitle number="3" title="Select Experience Level" />

          <div className="setup-difficulty-grid">
            {DIFFICULTIES.map((level) => {
              const isSelected = difficulty === level.id;

              return (
                <button
                  key={level.id}
                  type="button"
                  onClick={() => setDifficulty(level.id)}
                  className={`setup-difficulty-card ${
                    isSelected ? "setup-difficulty-card-active" : ""
                  }`}
                >
                  <strong>{level.label}</strong>
                  <span>{level.desc}</span>
                </button>
              );
            })}
          </div>
        </section>

        <div className="setup-two-column-grid">
          <div className="setup-left-stack">
            <section className="setup-card">
              <StepTitle number="4" title="Job Description" optional />

              <p className="setup-small-text">
                Paste the JD and Vapi AI will ask role-specific questions.
              </p>

              <textarea
                value={jobDescription}
                onChange={(event) => setJobDescription(event.target.value)}
                placeholder="Paste the job description or role requirements here..."
                className="setup-textarea"
              />
            </section>

            <section className="setup-card">
              <StepTitle number="5" title="Upload Resume" optional />

              <p className="setup-small-text">
                Upload your PDF resume for personalized questions based on your
                experience.
              </p>

              {resumeFileName ? (
                <div className="setup-uploaded-file">
                  <div className="setup-file-icon">
                    <FileText size={26} />
                  </div>

                  <div className="setup-file-info">
                    <p>{resumeFileName}</p>

                    <span>
                      {resumeLoading ? (
                        <span className="setup-file-loading">
                          <Loader2 size={13} />
                          Extracting text...
                        </span>
                      ) : resumeParsed ? (
                        <span className="setup-file-success">
                          ✓ Resume parsed successfully
                        </span>
                      ) : (
                        "Uploaded"
                      )}
                    </span>
                  </div>

                  <button
                    type="button"
                    onClick={clearResume}
                    className="setup-clear-file-btn"
                  >
                    <X size={21} />
                  </button>
                </div>
              ) : (
                <label className="setup-upload-box">
                  <UploadCloud size={36} />

                  <span>Click to upload PDF</span>
                  <small>PDF max 5MB</small>

                  <input
                    type="file"
                    accept="application/pdf"
                    onChange={handleResumeUpload}
                  />
                </label>
              )}
            </section>
          </div>

          <section className="setup-card setup-device-card">
            <StepTitle number="6" title="Device Check" />

            <p className="setup-small-text">
              Ensure your face is clearly visible and your microphone is
              available.
            </p>

            <div className="setup-video-box">
              {mediaError ? (
                <div className="setup-media-error">
                  <VideoOff size={42} />

                  <p>{mediaError}</p>

                  <span>
                    Please allow camera and mic access in your browser settings.
                  </span>
                </div>
              ) : (
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="setup-video-preview"
                />
              )}

              {!mediaError && (
                <div className="setup-device-status">
                  <div className="setup-ready-status">
                    <span></span>
                    System Ready
                  </div>

                  <div className="setup-device-icons">
                    <MicIcon size={21} />
                    <Video size={21} />
                  </div>
                </div>
              )}
            </div>

            <div className="setup-device-note">
              <ClipboardList size={18} />
              <span>
                Vapi will ask for microphone permission again when the call
                starts.
              </span>
            </div>
          </section>
        </div>

        <footer className="setup-bottom-bar">
          <Link to="/" className="setup-back-link" onClick={stopPreviewStream}>
            ← Go Back
          </Link>

          <button
            type="button"
            onClick={beginInterview}
            disabled={!isReady}
            className={`setup-begin-btn ${
              isReady ? "setup-begin-btn-ready" : ""
            }`}
          >
            <span>{resumeLoading ? "Reading Resume..." : "Begin Interview"}</span>

            {resumeLoading ? (
              <Loader2 size={21} className="setup-spin-icon" />
            ) : (
              <ChevronRight size={21} />
            )}
          </button>
        </footer>
      </div>
    </div>
  );
}

function StepTitle({ number, title, optional = false }) {
  return (
    <h2 className="setup-step-title">
      <span>{number}</span>
      {title}
      {optional && <small>(Optional)</small>}
    </h2>
  );
}

function InputField({ icon, label, value, onChange, placeholder }) {
  return (
    <div className="setup-field-group">
      <label>
        {icon}
        {label}
      </label>

      <input
        type="text"
        value={value || ""}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="setup-input"
      />
    </div>
  );
}