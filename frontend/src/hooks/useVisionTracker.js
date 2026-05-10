import { useEffect, useRef, useState, useCallback } from "react";
import { FaceLandmarker, FilesetResolver } from "@mediapipe/tasks-vision";

export function useVisionTracker(videoRef) {
  const landmarkerRef = useRef(null);

  const [isReady, setIsReady] = useState(false);

  const sessionStats = useRef({
    totalFrames: 0,
    goodEyeContactFrames: 0,
    goodPostureFrames: 0,
  });

  const lastAlertTime = useRef(0);

  useEffect(() => {
    let active = true;

    const initVisionTracker = async () => {
      try {
        const vision = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.12/wasm"
        );

        const faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
          baseOptions: {
            modelAssetPath:
              "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
            delegate: "GPU",
          },
          outputFaceBlendshapes: true,
          runningMode: "VIDEO",
          numFaces: 1,
        });

        if (active) {
          landmarkerRef.current = faceLandmarker;
          setIsReady(true);
          console.log("MediaPipe Vision Engine Loaded.");
        }
      } catch (error) {
        console.error("Vision AI failed to load:", error);

        if (active) {
          setIsReady(false);
        }
      }
    };

    initVisionTracker();

    return () => {
      active = false;
    };
  }, []);

  const analyzeVideoFrame = useCallback(
    (onFeedback) => {
      if (!landmarkerRef.current) return;
      if (!videoRef.current) return;
      if (videoRef.current.readyState < 2) return;

      try {
        const results = landmarkerRef.current.detectForVideo(
          videoRef.current,
          performance.now()
        );

        if (!results.faceBlendshapes || results.faceBlendshapes.length === 0) {
          return;
        }

        sessionStats.current.totalFrames += 1;

        const shapes = results.faceBlendshapes[0].categories;

        const threshold = 0.5;

        const lookOutLeft =
          shapes.find((shape) => shape.categoryName === "eyeLookOutLeft")
            ?.score || 0;

        const lookInLeft =
          shapes.find((shape) => shape.categoryName === "eyeLookInLeft")
            ?.score || 0;

        const lookUp =
          shapes.find((shape) => shape.categoryName === "eyeLookUpLeft")
            ?.score || 0;

        const lookDown =
          shapes.find((shape) => shape.categoryName === "eyeLookDownLeft")
            ?.score || 0;

        const isLookingAway =
          lookOutLeft > threshold ||
          lookInLeft > threshold ||
          lookUp > threshold ||
          lookDown > threshold;

        let isSlouching = false;

        if (results.faceLandmarks && results.faceLandmarks[0]) {
          const landmarks = results.faceLandmarks[0];

          const topHead = landmarks[10];
          const chin = landmarks[152];

          if (topHead && chin) {
            const zDiff = chin.z - topHead.z;

            if (zDiff > 0.05) {
              isSlouching = true;
            }
          }
        }

        if (!isLookingAway) {
          sessionStats.current.goodEyeContactFrames += 1;
        }

        if (!isSlouching) {
          sessionStats.current.goodPostureFrames += 1;
        }

        const now = performance.now();

        if (now - lastAlertTime.current > 10000) {
          if (isLookingAway) {
            onFeedback("Try to maintain better eye contact with the camera.");
            lastAlertTime.current = now;
          } else if (isSlouching) {
            onFeedback("Remember to sit up straight and face the camera.");
            lastAlertTime.current = now;
          }
        }
      } catch (error) {
        // Some frames can fail while camera is starting or switching tabs.
        // We silently ignore frame-level tracking errors.
      }
    },
    [videoRef]
  );

  const getFinalMetrics = () => {
    const totalFrames = sessionStats.current.totalFrames;

    if (totalFrames === 0) {
      return {
        eyeContactScore: 7,
        postureScore: 7,
      };
    }

    const eyeContactPercent =
      sessionStats.current.goodEyeContactFrames / totalFrames;

    const posturePercent =
      sessionStats.current.goodPostureFrames / totalFrames;

    return {
      eyeContactScore: Math.round(eyeContactPercent * 10 * 10) / 10,
      postureScore: Math.round(posturePercent * 10 * 10) / 10,
    };
  };

  const resetMetrics = () => {
    sessionStats.current = {
      totalFrames: 0,
      goodEyeContactFrames: 0,
      goodPostureFrames: 0,
    };

    lastAlertTime.current = 0;
  };

  return {
    isReady,
    analyzeVideoFrame,
    getFinalMetrics,
    resetMetrics,
  };
}