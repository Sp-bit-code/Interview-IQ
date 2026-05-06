import React, { useState, useRef, useCallback, useEffect } from "react";
import { GoogleGenAI } from "@google/genai";
import { useNavigate } from "react-router";

import { useInterviewStore } from "./src/store/useInterviewStore";
import { useAuthStore } from "./src/store/useAuthStore";
import { InterviewScreen } from "./components/InterviewScreen";
import { ReportScreen } from "./components/ReportScreen";
import { useVisionTracker } from "./src/hooks/useVisionTracker";

import "./App.css";

/* Build WAV blob from raw PCM audio */
function pcmBase64ToWavBlob(
  base64Pcm,
  sampleRate = 24000,
  channels = 1,
  bitsPerSample = 16
) {
  const pcmBytes = Uint8Array.from(atob(base64Pcm), (char) =>
    char.charCodeAt(0)
  );

  const dataLen = pcmBytes.length;
  const headerLen = 44;

  const buffer = new ArrayBuffer(headerLen + dataLen);
  const view = new DataView(buffer);

  const writeString = (offset, value) => {
    for (let i = 0; i < value.length; i++) {
      view.setUint8(offset + i, value.charCodeAt(i));
    }
  };

  writeString(0, "RIFF");
  view.setUint32(4, 36 + dataLen, true);
  writeString(8, "WAVE");
  writeString(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, channels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * channels * (bitsPerSample / 8), true);
  view.setUint16(32, channels * (bitsPerSample / 8), true);
  view.setUint16(34, bitsPerSample, true);
  writeString(36, "data");
  view.setUint32(40, dataLen, true);

  new Uint8Array(buffer, headerLen).set(pcmBytes);

  return new Blob([buffer], {
    type: "audio/wav",
  });
}

export default function App() {
  const { track, difficulty, jobDescription, resumeText } = useInterviewStore();
  const { user } = useAuthStore();

  const navigate = useNavigate();

  const [interviewState, setInterviewState] = useState("idle");
  const [transcript, setTranscript] = useState([]);
  const [liveFeedback, setLiveFeedback] = useState([]);
  const [finalReport, setFinalReport] = useState("");
  const [error, setError] = useState(null);

  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [loadingMessage, setLoadingMessage] = useState(
    "Connecting to Gemini AI..."
  );

  const videoRef = useRef(null);
  const mediaStreamRef = useRef(null);

  const { isReady: isTrackerReady, analyzeVideoFrame, getFinalMetrics } =
    useVisionTracker(videoRef);

  const conversationHistory = useRef("");
  const questionCount = useRef(0);
  const MAX_QUESTIONS = 15;
  const isInterviewActive = useRef(false);
  const startTimeRef = useRef(0);

  const mediaRecorderRef = useRef(null);
  const audioStreamRef = useRef(null);
  const audioChunksRef = useRef([]);
  const analyserRef = useRef(null);
  const audioContextRef = useRef(null);
  const levelIntervalRef = useRef(null);
  const silenceTimerRef = useRef(null);
  const silenceStartRef = useRef(0);

  const ttsAudioRef = useRef(null);
  const ttsObjectUrlRef = useRef(null);

  useEffect(() => {
    ttsAudioRef.current = new Audio();

    return () => {
      if (ttsObjectUrlRef.current) {
        URL.revokeObjectURL(ttsObjectUrlRef.current);
      }
    };
  }, []);

  useEffect(() => {
    let interval;

    if (interviewState === "in_progress" && isTrackerReady) {
      interval = setInterval(() => {
        analyzeVideoFrame((tip) => {
          setLiveFeedback((prev) => [tip, ...prev].slice(0, 5));
        });
      }, 100);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [interviewState, isTrackerReady, analyzeVideoFrame]);

  const cleanup = useCallback(() => {
    isInterviewActive.current = false;

    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      try {
        mediaRecorderRef.current.stop();
      } catch (error) {}
    }

    mediaRecorderRef.current = null;

    audioStreamRef.current?.getTracks().forEach((trackItem) => trackItem.stop());
    audioStreamRef.current = null;

    if (audioContextRef.current) {
      try {
        audioContextRef.current.close();
      } catch (error) {}

      audioContextRef.current = null;
    }

    analyserRef.current = null;

    if (levelIntervalRef.current) {
      clearInterval(levelIntervalRef.current);
      levelIntervalRef.current = null;
    }

    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }

    mediaStreamRef.current?.getTracks().forEach((trackItem) => trackItem.stop());
    mediaStreamRef.current = null;

    if (ttsAudioRef.current) {
      ttsAudioRef.current.pause();
      ttsAudioRef.current.src = "";
    }

    if (ttsObjectUrlRef.current) {
      URL.revokeObjectURL(ttsObjectUrlRef.current);
      ttsObjectUrlRef.current = null;
    }

    setIsSpeaking(false);
    setIsRecording(false);
    setIsProcessing(false);
    setAudioLevel(0);
  }, []);

  const handleError = useCallback(
    (message, err) => {
      console.error(message, err);
      setError(message);
      setInterviewState("error");
      cleanup();
    },
    [cleanup]
  );

  const startInterview = useCallback(async () => {
    if (!track) {
      handleError("Please go back and select a track/difficulty first.");
      return;
    }

    setInterviewState("starting");
    setError(null);
    setTranscript([]);
    setLiveFeedback([]);
    setFinalReport("");

    conversationHistory.current = "";
    questionCount.current = 0;
    isInterviewActive.current = true;
    startTimeRef.current = Date.now();

    try {
      const fullStream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: true,
      });

      fullStream.getAudioTracks().forEach((trackItem) => trackItem.stop());

      const videoOnlyStream = new MediaStream(fullStream.getVideoTracks());
      mediaStreamRef.current = videoOnlyStream;

      console.log("Camera and mic permissions granted.");

      setInterviewState("in_progress");

      setTimeout(() => {
        if (isInterviewActive.current) {
          generateNextAIResponse("");
        }
      }, 1500);
    } catch (err) {
      handleError(
        "Camera and Microphone permissions are required for the interview. Please allow access and try again.",
        err
      );
    }
  }, [track, handleError]);

  useEffect(() => {
    if (interviewState === "idle" && track) {
      startInterview();
    }
  }, []);

  useEffect(() => {
    if (
      interviewState === "in_progress" &&
      mediaStreamRef.current &&
      videoRef.current
    ) {
      if (videoRef.current.srcObject !== mediaStreamRef.current) {
        videoRef.current.srcObject = mediaStreamRef.current;
      }
    }
  }, [interviewState]);

  const FALLBACK_OPENER = `Hi! I'm your AI interview coach for this ${
    track || "technical"
  } session at ${
    difficulty || "Fresher"
  } level. Great to meet you! To kick things off, could you tell me a little about yourself and your background?`;

  const generateNextAIResponse = async (userSpokenText) => {
    if (!isInterviewActive.current) return;

    if (!userSpokenText) {
      setLoadingMessage("Gemini AI is preparing your first question...");
    }

    try {
      const apiKey = import.meta.env.VITE_GEMINI_API_KEY;

      if (!apiKey) {
        throw new Error("VITE_GEMINI_API_KEY is not set in .env.local");
      }

      const ai = new GoogleGenAI({ apiKey });

      if (userSpokenText) {
        conversationHistory.current += `\nCandidate: ${userSpokenText}`;
        questionCount.current += 1;
      }

      const resumeContext = resumeText
        ? `\nCandidate Resume:\n${resumeText.substring(0, 2000)}`
        : "";

      const jdContext = jobDescription
        ? `\nJob Description:\n${jobDescription.substring(0, 1500)}`
        : "";

      const systemInstruction = `You are a professional ${track} interview coach conducting a mock interview like the ones at Google, Meta, and Amazon.

Level: ${difficulty}.${jdContext}${resumeContext}

PACING:
- Q1-3: Introductions and icebreakers.
- Q4-8: Core technical/domain questions.
- Q9-12: Deep dive scenarios.
- Q13-15: Behavioral STAR questions and wrap-up.

RULES:
1. This is question ${questionCount.current + 1} of ${MAX_QUESTIONS}.
2. After the candidate answers, give ONE sentence of coaching feedback, then ask the next question.
3. Max 3 sentences.
4. Keep it natural and spoken. No markdown, bullets, or emojis.
5. First message: introduce yourself warmly and ask the candidate to tell you about themselves.
6. At question ${MAX_QUESTIONS} after their answer, respond exactly: "Interview complete. Generating your report."`;

      const prompt = `${systemInstruction}

History:
${conversationHistory.current || "(First message)"}

Your response:`;

      const responseText = await Promise.race([
        ai.models
          .generateContent({
            model: "gemini-2.5-flash",
            contents: prompt,
          })
          .then((response) => (response.text || "").trim()),

        new Promise((_, reject) => {
          setTimeout(
            () => reject(new Error("Gemini response timed out after 20s")),
            20000
          );
        }),
      ]);

      if (!responseText || !isInterviewActive.current) {
        throw new Error("Empty response from Gemini");
      }

      conversationHistory.current += `\nInterviewer: ${responseText}`;
      setTranscript((prev) => [...prev, { speaker: "ai", text: responseText }]);

      speakThenRecord(responseText);
    } catch (error) {
      console.error("Gemini text generation error:", error?.message || error);

      if (!isInterviewActive.current) return;

      if (questionCount.current === 0 && conversationHistory.current === "") {
        conversationHistory.current += `\nInterviewer: ${FALLBACK_OPENER}`;
        setTranscript((prev) => [
          ...prev,
          { speaker: "ai", text: FALLBACK_OPENER },
        ]);
        speakThenRecord(FALLBACK_OPENER);
      } else {
        const retryMsg =
          "I had a brief connection issue. Could you repeat your last answer?";

        conversationHistory.current += `\nInterviewer: ${retryMsg}`;
        setTranscript((prev) => [...prev, { speaker: "ai", text: retryMsg }]);
        speakThenRecord(retryMsg);
      }
    }
  };

  const speakWithBrowser = (text, onDone) => {
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    const voices = window.speechSynthesis.getVoices();

    const preferred =
      voices.find(
        (voice) =>
          voice.name.includes("Google US English") ||
          voice.name.includes("Microsoft David") ||
          voice.name.includes("Microsoft Mark") ||
          voice.name.includes("Samantha") ||
          voice.name.includes("Daniel")
      ) ||
      voices.find((voice) => voice.lang.startsWith("en") && !voice.localService) ||
      voices.find((voice) => voice.lang.startsWith("en"));

    if (preferred) {
      utterance.voice = preferred;
    }

    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.volume = 1;

    const keepAlive = setInterval(() => {
      if (!window.speechSynthesis.speaking) {
        clearInterval(keepAlive);
        return;
      }

      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
      }
    }, 3000);

    utterance.onend = () => {
      clearInterval(keepAlive);
      onDone();
    };

    utterance.onerror = () => {
      clearInterval(keepAlive);
      onDone();
    };

    window.speechSynthesis.speak(utterance);
  };

  const speakThenRecord = async (textToSay) => {
    if (!isInterviewActive.current) return;

    if (
      textToSay.includes("Interview complete") ||
      textToSay.includes("Generating your report")
    ) {
      setTranscript((prev) => {
        const last = prev[prev.length - 1];

        if (last?.text !== textToSay) {
          return [...prev, { speaker: "ai", text: textToSay }];
        }

        return prev;
      });

      setInterviewState("generating_report");
      return;
    }

    setIsSpeaking(true);
    setIsRecording(false);
    setIsProcessing(false);

    const afterSpeech = () => {
      if (!isInterviewActive.current) return;

      setIsSpeaking(false);

      setTimeout(() => {
        if (isInterviewActive.current) {
          startRecording();
        }
      }, 500);
    };

    try {
      const apiKey = import.meta.env.VITE_GEMINI_API_KEY;

      if (!apiKey) {
        throw new Error("No API key");
      }

      const ai = new GoogleGenAI({ apiKey });

      const ttsResponse = await Promise.race([
        ai.models.generateContent({
          model: "gemini-2.5-flash-preview-tts",
          contents: [{ parts: [{ text: textToSay }] }],
          config: {
            responseModalities: ["AUDIO"],
            speechConfig: {
              voiceConfig: {
                prebuiltVoiceConfig: {
                  voiceName: "Charon",
                },
              },
            },
          },
        }),

        new Promise((_, reject) => {
          setTimeout(() => reject(new Error("TTS timeout")), 15000);
        }),
      ]);

      const part = ttsResponse.candidates?.[0]?.content?.parts?.[0];
      const pcmBase64 = part?.inlineData?.data;

      if (!pcmBase64) {
        throw new Error("No PCM data in TTS response");
      }

      if (!isInterviewActive.current) return;

      const wavBlob = pcmBase64ToWavBlob(pcmBase64);

      if (ttsObjectUrlRef.current) {
        URL.revokeObjectURL(ttsObjectUrlRef.current);
      }

      const url = URL.createObjectURL(wavBlob);
      ttsObjectUrlRef.current = url;

      const audio = ttsAudioRef.current;

      audio.src = url;
      audio.onended = afterSpeech;
      audio.onerror = () => {
        console.warn("Audio element error. Using browser TTS.");
        speakWithBrowser(textToSay, afterSpeech);
      };

      await audio.play();
    } catch (error) {
      console.warn(
        "Gemini TTS unavailable. Falling back to browser TTS:",
        error?.message
      );

      setIsSpeaking(true);
      speakWithBrowser(textToSay, afterSpeech);
    }
  };

  const startRecording = async () => {
    if (!isInterviewActive.current) return;

    try {
      const audioStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      audioStreamRef.current = audioStream;

      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(audioStream);

      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyser.smoothingTimeConstant = 0.8;

      source.connect(analyser);
      analyserRef.current = analyser;

      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "audio/mp4";

      const recorder = new MediaRecorder(audioStream, { mimeType });
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        if (levelIntervalRef.current) clearInterval(levelIntervalRef.current);
        if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

        setAudioLevel(0);
      };

      recorder.start(500);

      setIsRecording(true);
      setIsProcessing(false);

      silenceStartRef.current = 0;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      let userHasSpoken = false;

      levelIntervalRef.current = setInterval(() => {
        if (!analyserRef.current) return;

        analyserRef.current.getByteFrequencyData(dataArray);

        const average =
          dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;

        const normalizedLevel = Math.min(average / 80, 1);
        setAudioLevel(normalizedLevel);

        const isSilent = average < 8;

        if (!isSilent) {
          userHasSpoken = true;
          silenceStartRef.current = 0;
        } else if (userHasSpoken) {
          if (silenceStartRef.current === 0) {
            silenceStartRef.current = Date.now();
          } else if (Date.now() - silenceStartRef.current > 5000) {
            stopAndSubmitRecording();
          }
        }
      }, 100);
    } catch (err) {
      console.error("Failed to start recording:", err);
      handleError(
        "Could not access microphone. Please check your browser permissions.",
        err
      );
    }
  };

  const stopAndSubmitRecording = useCallback(async () => {
    if (
      !mediaRecorderRef.current ||
      mediaRecorderRef.current.state === "inactive"
    ) {
      return;
    }

    setIsRecording(false);
    setIsProcessing(true);
    setAudioLevel(0);

    if (levelIntervalRef.current) {
      clearInterval(levelIntervalRef.current);
      levelIntervalRef.current = null;
    }

    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }

    const recorder = mediaRecorderRef.current;

    await new Promise((resolve) => {
      const originalOnStop = recorder.onstop;

      recorder.onstop = (event) => {
        if (originalOnStop) {
          originalOnStop.call(recorder, event);
        }

        resolve();
      };

      recorder.stop();
    });

    audioStreamRef.current?.getTracks().forEach((trackItem) => trackItem.stop());
    audioStreamRef.current = null;

    if (audioContextRef.current) {
      try {
        audioContextRef.current.close();
      } catch (error) {}

      audioContextRef.current = null;
    }

    analyserRef.current = null;

    const mimeType = recorder.mimeType || "audio/webm";
    const audioBlob = new Blob(audioChunksRef.current, {
      type: mimeType,
    });

    audioChunksRef.current = [];

    if (audioBlob.size < 1000) {
      setIsProcessing(false);

      if (isInterviewActive.current) {
        speakThenRecord(
          "I didn't hear an answer. Please try again when you're ready."
        );
      }

      return;
    }

    try {
      const base64Audio = await blobToBase64(audioBlob);
      await processAudioWithGemini(base64Audio, mimeType);
    } catch (error) {
      console.error("Error processing audio:", error);
      setIsProcessing(false);

      if (isInterviewActive.current) {
        speakThenRecord("I had trouble processing your answer. Could you try again?");
      }
    }
  }, []);

  const blobToBase64 = (blob) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onloadend = () => {
        const dataUrl = reader.result;
        const base64 = dataUrl.split(",")[1];
        resolve(base64);
      };

      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  };

  const processAudioWithGemini = async (base64Audio, mimeType) => {
    if (!isInterviewActive.current) return;

    try {
      const apiKey = import.meta.env.VITE_GEMINI_API_KEY;

      if (!apiKey) {
        throw new Error("API key not set.");
      }

      const ai = new GoogleGenAI({ apiKey });

      const transcribeResponse = await ai.models.generateContent({
        model: "gemini-2.5-flash",
        contents: [
          {
            role: "user",
            parts: [
              {
                inlineData: {
                  mimeType: mimeType.split(";")[0],
                  data: base64Audio,
                },
              },
              {
                text: 'Transcribe this audio recording accurately. Return ONLY the transcribed text, nothing else. If there is no speech or just noise, return exactly: "[no speech detected]"',
              },
            ],
          },
        ],
      });

      const transcription = (transcribeResponse.text || "").trim();

      if (
        !transcription ||
        transcription.includes("[no speech detected]") ||
        transcription.length < 3
      ) {
        setIsProcessing(false);

        if (isInterviewActive.current) {
          speakThenRecord(
            "I couldn't hear your answer clearly. Could you speak a bit louder and try again?"
          );
        }

        return;
      }

      setTranscript((prev) => [...prev, { speaker: "user", text: transcription }]);
      setIsProcessing(false);

      await generateNextAIResponse(transcription);
    } catch (error) {
      console.error("Gemini audio processing error:", error);

      setIsProcessing(false);

      if (isInterviewActive.current) {
        speakThenRecord(
          "Sorry, I had trouble processing that. Could you repeat your answer?"
        );
      }
    }
  };

  const handleManualSubmit = useCallback((text) => {
    if (!isInterviewActive.current || !text.trim()) return;

    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      try {
        mediaRecorderRef.current.stop();
      } catch (error) {}
    }

    audioStreamRef.current?.getTracks().forEach((trackItem) => trackItem.stop());

    setIsRecording(false);
    setIsProcessing(false);
    setAudioLevel(0);

    setTranscript((prev) => [...prev, { speaker: "user", text: text.trim() }]);
    generateNextAIResponse(text.trim());
  }, []);

  const endInterviewEarly = useCallback(() => {
    if (!isInterviewActive.current) return;

    cleanup();
    setInterviewState("generating_report");
  }, [cleanup]);

  const generateFinalReport = useCallback(
    async (finalTranscript) => {
      try {
        const apiKey = import.meta.env.VITE_GEMINI_API_KEY;

        if (!apiKey) {
          throw new Error("API key not set");
        }

        const ai = new GoogleGenAI({ apiKey });

        const transcriptText = finalTranscript
          .map(
            (item) =>
              `${item.speaker === "user" ? "Candidate" : "Interviewer"}: ${
                item.text
              }`
          )
          .join("\n");

        const metrics = getFinalMetrics();
        const duration = Math.round((Date.now() - startTimeRef.current) / 1000);

        const prompt = `You are an expert interview coach. Generate a performance report as JSON.

VISION DATA:
Eye Contact: ${metrics.eyeContactScore}/10
Posture: ${metrics.postureScore}/10

Duration: ${Math.floor(duration / 60)}m ${duration % 60}s
Track: ${track}
Level: ${difficulty}

JSON format:
{
  "overallSummary": "Summary paragraph...",
  "scores": {
    "communication": N,
    "confidence": N,
    "bodyLanguage": ${metrics.postureScore},
    "eyeContact": ${metrics.eyeContactScore},
    "speakingPace": N,
    "overall": N
  },
  "detailedAnalysis": {
    "communication": "...",
    "confidence": "...",
    "bodyLanguage": "...",
    "eyeContact": "...",
    "speakingPace": "..."
  },
  "strengths": ["...", "...", "..."],
  "improvementTips": ["...", "...", "...", "...", "..."]
}

Transcript:
${transcriptText}`;

        const response = await ai.models.generateContent({
          model: "gemini-2.5-flash",
          contents: prompt,
          config: {
            responseMimeType: "application/json",
          },
        });

        const reportJsonText = response.text || "";

        setFinalReport(reportJsonText);
        setInterviewState("report_ready");

        if (user) {
          try {
            const parsed = JSON.parse(reportJsonText);
            const { supabase } = await import("./src/lib/supabase");

            await supabase.from("session_scores").insert({
              user_id: user.id,
              track: track || "Unknown",
              difficulty: difficulty || "Fresher",
              score_overall: parsed.scores.overall,
              score_communication: parsed.scores.communication,
              score_confidence: parsed.scores.confidence,
              score_body_language: parsed.scores.bodyLanguage,
              score_eye_contact: parsed.scores.eyeContact,
              score_speaking_pace: parsed.scores.speakingPace,
              report_json: parsed,
              duration_seconds: duration,
            });
          } catch (error) {
            console.warn("DB save failed:", error);
          }
        }
      } catch (err) {
        handleError("Failed to generate report.", err);
      }
    },
    [handleError, track, difficulty, user, getFinalMetrics]
  );

  useEffect(() => {
    if (interviewState === "generating_report") {
      cleanup();
      generateFinalReport(transcript);
    }
  }, [interviewState]);

  const handleRestart = () => {
    cleanup();
    navigate("/setup");
  };

  const handleGoToDashboard = () => {
    cleanup();
    navigate("/dashboard");
  };

  const renderContent = () => {
    switch (interviewState) {
      case "idle":
      case "starting":
        return (
          <LoadingScreen
            title="Initializing AI Interview Coach..."
            subtitle={`Setting up ${difficulty || "Fresher"} ${
              track || "Interview"
            } session. Please allow camera + mic.`}
            smallText={loadingMessage}
            variant="primary"
          />
        );

      case "in_progress":
        return (
          <InterviewScreen
            videoRef={videoRef}
            transcript={transcript}
            liveFeedback={liveFeedback}
            startTime={startTimeRef.current}
            isSpeaking={isSpeaking}
            isRecording={isRecording}
            isProcessing={isProcessing}
            audioLevel={audioLevel}
            onEndInterview={endInterviewEarly}
            onStopRecording={stopAndSubmitRecording}
            onManualSubmit={handleManualSubmit}
          />
        );

      case "generating_report":
        return (
          <LoadingScreen
            title="Interview Complete! 🎉"
            subtitle="Analyzing your performance..."
            smallText="Generating your AI report..."
            variant="secondary"
          />
        );

      case "report_ready":
        return (
          <ReportScreen
            report={finalReport}
            onRestart={handleRestart}
            onDashboard={handleGoToDashboard}
            startTime={startTimeRef.current}
          />
        );

      case "error":
        return (
          <div className="app-error-page">
            <div className="app-error-icon">
              <svg
                className="app-error-svg"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth="2"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
                />
              </svg>
            </div>

            <h2>Something Went Wrong</h2>

            <p>{error}</p>

            <div className="app-error-actions">
              <button type="button" onClick={handleRestart}>
                Try Again
              </button>

              <button type="button" onClick={() => navigate("/")}>
                Go Home
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return <div className="app-root">{renderContent()}</div>;
}

function LoadingScreen({ title, subtitle, smallText, variant }) {
  return (
    <div className="app-loading-page">
      <div className="app-loading-spinner-wrap">
        <div
          className={`app-loading-glow ${
            variant === "secondary"
              ? "app-loading-glow-secondary"
              : "app-loading-glow-primary"
          }`}
        ></div>

        <svg
          className={`app-loading-spinner ${
            variant === "secondary"
              ? "app-loading-spinner-secondary"
              : "app-loading-spinner-primary"
          }`}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="app-loading-circle"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          ></circle>

          <path
            className="app-loading-path"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
      </div>

      <h2>{title}</h2>
      <p>{subtitle}</p>

      {smallText && <span>{smallText}</span>}
    </div>
  );
}