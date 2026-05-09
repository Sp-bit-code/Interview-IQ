// import React, { useState } from "react";
// import { Link, useNavigate } from "react-router";
// import { supabase } from "../lib/supabase";
// import { useAuthStore } from "../store/useAuthStore.js";
// import { Mic, Mail, Lock, ArrowRight } from "lucide-react";

// import "./LoginScreen.css";

// export default function LoginScreen() {
//   const navigate = useNavigate();
//   const setUser = useAuthStore((state) => state.setUser);

//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");

//   const [isSignUp, setIsSignUp] = useState(false);
//   const [loading, setLoading] = useState(false);
//   const [googleLoading, setGoogleLoading] = useState(false);

//   const [error, setError] = useState(null);

//   const handleEmailAuth = async (event) => {
//     event.preventDefault();

//     setLoading(true);
//     setError(null);

//     try {
//       if (isSignUp) {
//         const { error } = await supabase.auth.signUp({
//           email,
//           password,
//           options: {
//             emailRedirectTo: `${window.location.origin}/`,
//           },
//         });

//         if (error) {
//           throw error;
//         }

//         setError("Success! Check your email for a confirmation link.");
//       } else {
//         const { data, error } = await supabase.auth.signInWithPassword({
//           email,
//           password,
//         });

//         if (error) {
//           throw error;
//         }

//         setUser(data?.user || null);

//         navigate("/", {
//           replace: true,
//         });
//       }
//     } catch (err) {
//       setError(err?.message || "An error occurred.");
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleGoogleAuth = async () => {
//     setGoogleLoading(true);
//     setError(null);

//     try {
//       const { error } = await supabase.auth.signInWithOAuth({
//         provider: "google",
//         options: {
//           redirectTo: `${window.location.origin}/`,
//         },
//       });

//       if (error) {
//         throw error;
//       }
//     } catch (err) {
//       setError(err?.message || "Google login failed.");
//       setGoogleLoading(false);
//     }
//   };

//   const handleGuestPractice = () => {
//     navigate("/setup");
//   };

//   return (
//     <div className="login-page">
//       <div className="login-bg-glow login-bg-glow-one"></div>
//       <div className="login-bg-glow login-bg-glow-two"></div>
//       <div className="login-bg-grid"></div>

//       <Link to="/" className="login-brand">
//         <div className="login-brand-icon">
//           <Mic size={21} />
//         </div>
//         <span>InterviewIQ</span>
//       </Link>

//       <div className="login-card">
//         <div className="login-card-header">
//           <h1>{isSignUp ? "Create an Account" : "Welcome Back"}</h1>

//           <p>
//             {isSignUp
//               ? "Sign up to save your interview history and track progress."
//               : "Log in to access your dashboard and history."}
//           </p>
//         </div>

//         {error && (
//           <div
//             className={`login-message ${
//               String(error).includes("Success")
//                 ? "login-message-success"
//                 : "login-message-error"
//             }`}
//           >
//             {error}
//           </div>
//         )}

//         <form onSubmit={handleEmailAuth} className="login-form">
//           <div className="login-field-group">
//             <label>Email Address</label>

//             <div className="login-input-wrapper">
//               <Mail size={20} className="login-input-icon" />

//               <input
//                 type="email"
//                 required
//                 value={email}
//                 onChange={(event) => setEmail(event.target.value)}
//                 placeholder="you@domain.com"
//                 autoComplete="email"
//               />
//             </div>
//           </div>

//           <div className="login-field-group">
//             <label>Password</label>

//             <div className="login-input-wrapper">
//               <Lock size={20} className="login-input-icon" />

//               <input
//                 type="password"
//                 required
//                 minLength={6}
//                 value={password}
//                 onChange={(event) => setPassword(event.target.value)}
//                 placeholder="••••••••"
//                 autoComplete={isSignUp ? "new-password" : "current-password"}
//               />
//             </div>
//           </div>

//           <button
//             type="submit"
//             disabled={loading || googleLoading}
//             className="login-submit-btn"
//           >
//             <span>
//               {loading
//                 ? "Processing..."
//                 : isSignUp
//                 ? "Create Account"
//                 : "Sign In"}
//             </span>

//             {!loading && <ArrowRight size={17} />}
//           </button>
//         </form>

//         <div className="login-divider">
//           <span>OR CONTINUE WITH</span>
//         </div>

//         <button
//           type="button"
//           onClick={handleGoogleAuth}
//           disabled={googleLoading || loading}
//           className="login-google-btn"
//         >
//           <GoogleIcon />
//           <span>{googleLoading ? "Redirecting..." : "Google Account"}</span>
//         </button>

//         <p className="login-switch-text">
//           {isSignUp ? "Already have an account?" : "Don't have an account?"}

//           <button
//             type="button"
//             onClick={() => {
//               setIsSignUp(!isSignUp);
//               setError(null);
//             }}
//           >
//             {isSignUp ? "Log In" : "Sign Up"}
//           </button>
//         </p>

//         <div className="login-guest-box">
//           <button type="button" onClick={handleGuestPractice}>
//             Skip login → Practice as guest
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// }

// function GoogleIcon() {
//   return (
//     <svg
//       xmlns="http://www.w3.org/2000/svg"
//       viewBox="0 0 24 24"
//       className="login-google-icon"
//     >
//       <path
//         fill="#4285F4"
//         d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
//       />
//       <path
//         fill="#34A853"
//         d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
//       />
//       <path
//         fill="#FBBC05"
//         d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
//       />
//       <path
//         fill="#EA4335"
//         d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
//       />
//     </svg>
//   );
// }







import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { ArrowRight, Lock, Mail, Mic } from "lucide-react";

import Beams from "../components/Beams";
import { useAuthStore } from "../store/useAuthStore";

import "./LoginScreen.css";

export default function LoginScreen() {
  const navigate = useNavigate();

  const authStore = useAuthStore();

  const signIn =
    authStore?.signIn ||
    authStore?.login ||
    authStore?.signInWithEmail ||
    authStore?.loginWithEmail;

  const signInWithGoogle =
    authStore?.signInWithGoogle ||
    authStore?.loginWithGoogle ||
    authStore?.googleLogin;

  const [email, setEmail] = useState("ayushichauhan21101712@gmail.com");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (event) => {
    event.preventDefault();

    if (!signIn) {
      alert("signIn function not found in useAuthStore.");
      return;
    }

    try {
      setLoading(true);
      await signIn(email, password);
      navigate("/");
    } catch (error) {
      console.error("Login error:", error);
      alert("Failed to log into account. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    if (!signInWithGoogle) {
      alert("Google login function not found in useAuthStore.");
      return;
    }

    try {
      setLoading(true);
      await signInWithGoogle();
      navigate("/");
    } catch (error) {
      console.error("Google login error:", error);
      alert("Failed to log into account. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleGuestLogin = () => {
    navigate("/");
  };

  return (
    <main className="login-page">
      <div className="login-beams-bg">
        <Beams
          beamWidth={3}
          beamHeight={30}
          beamNumber={20}
          lightColor="#ffffff"
          speed={2}
          noiseIntensity={1.75}
          scale={0.2}
          rotation={30}
        />
      </div>

      <header className="login-brand">
        <div className="login-brand-icon">
          <Mic size={30} strokeWidth={2.5} />
        </div>

        <span>InterviewIQ</span>
      </header>

      <section className="login-card">
        <div className="login-card-header">
          <h1>Welcome Back</h1>
          <p>Log in to access your dashboard and history.</p>
        </div>

        <form className="login-form" onSubmit={handleLogin}>
          <label className="login-label" htmlFor="login-email">
            Email Address
          </label>

          <div className="login-input-wrapper">
            <Mail size={22} className="login-input-icon" />

            <input
              id="login-email"
              type="email"
              value={email}
              placeholder="Enter your email"
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
              required
            />
          </div>

          <label className="login-label" htmlFor="login-password">
            Password
          </label>

          <div className="login-input-wrapper">
            <Lock size={22} className="login-input-icon" />

            <input
              id="login-password"
              type="password"
              value={password}
              placeholder="Enter your password"
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
          </div>

          <button className="login-main-btn" type="submit" disabled={loading}>
            <span>{loading ? "Signing In..." : "Sign In"}</span>
            <ArrowRight size={21} />
          </button>
        </form>

        <div className="login-divider">
          <span>OR CONTINUE WITH</span>
        </div>

        <button
          className="login-google-btn"
          type="button"
          onClick={handleGoogleLogin}
          disabled={loading}
        >
          <span className="login-google-icon">G</span>
          <span>Google Account</span>
        </button>

        <p className="login-switch">
          Don&apos;t have an account? <Link to="/signup">Sign Up</Link>
        </p>

        <div className="login-bottom-line" />

        <button
          className="login-guest-btn"
          type="button"
          onClick={handleGuestLogin}
        >
          Skip login → Practice as guest
        </button>
      </section>
    </main>
  );
}