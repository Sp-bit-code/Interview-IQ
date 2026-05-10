import React from "react";
import { Phone, PhoneOff, Loader2, RotateCcw } from "lucide-react";
import MuteButton from "./MuteButton";
import "./VapiCallControls.css";

export default function VapiCallControls({
  isActive = false,
  isConnecting = false,
  isMuted = false,
  onStart,
  onEnd,
  onToggleMute,
  onNewSetup,
  startLabel = "Start Vapi Interview",
  endLabel = "End Interview",
}) {
  return (
    <div className="vapi-controls">
      {!isActive ? (
        <button
          type="button"
          onClick={onStart}
          disabled={isConnecting}
          className="vapi-control-btn vapi-start-btn"
        >
          {isConnecting ? (
            <>
              <Loader2 size={20} className="vapi-spin" />
              Connecting...
            </>
          ) : (
            <>
              <Phone size={20} />
              {startLabel}
            </>
          )}
        </button>
      ) : (
        <button
          type="button"
          onClick={onEnd}
          className="vapi-control-btn vapi-end-btn"
        >
          <PhoneOff size={20} />
          {endLabel}
        </button>
      )}

      <MuteButton
        isMuted={isMuted}
        disabled={!isActive}
        onToggleMute={onToggleMute}
      />

      {onNewSetup && (
        <button
          type="button"
          onClick={onNewSetup}
          className="vapi-control-btn vapi-new-btn"
        >
          <RotateCcw size={18} />
          New Setup
        </button>
      )}
    </div>
  );
}