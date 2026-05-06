import React, { useEffect, useRef, useState } from "react";
import { Keyboard, Send, X } from "lucide-react";
import "./TypeAnswerBox.css";

export default function TypeAnswerBox({
  disabled = false,
  placeholder = "Type your answer...",
  onSubmit,
}) {
  const inputRef = useRef(null);

  const [isOpen, setIsOpen] = useState(false);
  const [answer, setAnswer] = useState("");

  useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => {
        inputRef.current?.focus();
      }, 80);

      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  const handleSubmit = (event) => {
    event.preventDefault();

    const cleanedAnswer = answer.trim();

    if (!cleanedAnswer || disabled) {
      return;
    }

    if (onSubmit) {
      onSubmit(cleanedAnswer);
    }

    setAnswer("");
  };

  const handleClose = () => {
    setIsOpen(false);
    setAnswer("");
  };

  if (!isOpen) {
    return (
      <button
        type="button"
        disabled={disabled}
        onClick={() => setIsOpen(true)}
        className="type-answer-toggle-btn"
      >
        <Keyboard size={18} />
        Type instead
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="type-answer-box">
      <div className="type-answer-input-wrap">
        <Keyboard size={18} className="type-answer-icon" />

        <input
          ref={inputRef}
          type="text"
          value={answer}
          disabled={disabled}
          onChange={(event) => setAnswer(event.target.value)}
          placeholder={placeholder}
        />
      </div>

      <button
        type="submit"
        disabled={!answer.trim() || disabled}
        className="type-answer-send-btn"
      >
        <Send size={18} />
      </button>

      <button
        type="button"
        onClick={handleClose}
        className="type-answer-close-btn"
      >
        <X size={18} />
      </button>
    </form>
  );
}