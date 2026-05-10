// import React, { useEffect } from "react";
// import { BrowserRouter, Routes, Route, Navigate } from "react-router";

// import LandingPage from "./pages/LandingPage.jsx";
// import SetupScreen from "./pages/SetupScreen.jsx";
// import Dashboard from "./pages/Dashboard.jsx";
// import LoginScreen from "./pages/LoginScreen.jsx";
// import InterviewRoom from "./pages/InterviewRoom.jsx";

// import { useAuthStore } from "./store/useAuthStore.js";

// function ProtectedRoute({ children }) {
//   const { user, isLoading } = useAuthStore();

//   if (isLoading) {
//     return (
//       <div className="router-loading-page">
//         <div className="router-loading-box">
//           <div className="router-spinner"></div>
//           <span>Authenticating...</span>
//         </div>
//       </div>
//     );
//   }

//   if (!user) {
//     return <Navigate to="/login" replace />;
//   }

//   return children;
// }

// export default function MainRouter() {
//   const initialize = useAuthStore((state) => state.initialize);

//   useEffect(() => {
//     initialize();
//   }, [initialize]);

//   return (
//     <BrowserRouter>
//       <Routes>
//         {/* Public home page */}
//         <Route path="/" element={<LandingPage />} />

//         {/* Login / signup */}
//         <Route path="/login" element={<LoginScreen />} />

//         {/* Guest + logged-in users both allowed */}
//         <Route path="/setup" element={<SetupScreen />} />
//         <Route path="/interview" element={<InterviewRoom />} />

//         {/* Only logged-in users allowed */}
//         <Route
//           path="/dashboard"
//           element={
//             <ProtectedRoute>
//               <Dashboard />
//             </ProtectedRoute>
//           }
//         />

//         {/* Wrong route fallback */}
//         <Route path="*" element={<Navigate to="/" replace />} />
//       </Routes>
//     </BrowserRouter>
//   );
// }
import React, { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router";

import LandingPage from "./pages/LandingPage.jsx";
import SetupScreen from "./pages/SetupScreen.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import LoginScreen from "./pages/LoginScreen.jsx";
import InterviewRoom from "./pages/InterviewRoom.jsx";

import StudyNotes from "./pages/StudyNotes.jsx";
import ResumeGapFinder from "./pages/ResumeGapFinder.jsx";
import Flashcards from "./pages/Flashcards.jsx";

import { useAuthStore } from "./store/useAuthStore.js";

function RouterLoadingScreen() {
  return (
    <div className="router-loading-page">
      <div className="router-loading-box">
        <div className="router-spinner"></div>
        <span>Authenticating...</span>
      </div>
    </div>
  );
}

function ProtectedRoute({ children }) {
  const { user, isLoading } = useAuthStore();

  if (isLoading) {
    return <RouterLoadingScreen />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default function MainRouter() {
  const initialize = useAuthStore((state) => state.initialize);

  useEffect(() => {
    initialize();
  }, [initialize]);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public home page */}
        <Route path="/" element={<LandingPage />} />

        {/* Login / signup */}
        <Route path="/login" element={<LoginScreen />} />

        {/* Vapi interview flow */}
        <Route path="/setup" element={<SetupScreen />} />
        <Route path="/interview" element={<InterviewRoom />} />

        {/* RAG backend features */}
        <Route path="/study-notes" element={<StudyNotes />} />
        <Route path="/resume-gap-finder" element={<ResumeGapFinder />} />
        <Route path="/flashcards" element={<Flashcards />} />

        {/* Logged-in user dashboard */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}