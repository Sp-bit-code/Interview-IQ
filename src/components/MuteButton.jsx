import React from "react";
import { Mic, MicOff } from "lucide-react";
import "./MuteButton.css";

export default function MuteButton({
  isMuted = false,
  disabled = false,
  onToggleMute,
}) {
  return (
    <button
      type="button"
      onClick={onToggleMute}
      disabled={disabled}
      className={`mute-btn ${isMuted ? "mute-btn-muted" : ""}`}
    >
      {isMuted ? <MicOff size={20} /> : <Mic size={20} />}
      <span>{isMuted ? "Unmute" : "Mute"}</span>
    </button>
  );
}