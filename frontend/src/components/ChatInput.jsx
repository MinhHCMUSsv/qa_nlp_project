import React, { useState, useRef, useEffect } from "react";
import { FaArrowUp, FaSpinner } from "react-icons/fa";

/**
 * ChatInput — Claude style input box conforming to DESIGN.MD.
 */
export default function ChatInput({ onSendMessage, isLoading, isOnline }) {
  const [text, setText] = useState("");
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        140
      )}px`;
    }
  }, [text]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!text.trim() || isLoading || !isOnline) return;
    onSendMessage(text);
    setText("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <form className="editorial-chat-form" onSubmit={handleSubmit}>
      <div className="input-box-editorial">
        <textarea
          ref={textareaRef}
          className="textarea-editorial"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            isOnline
              ? "Hỏi về WebSphere JVM heap, DB2 Lock Timeout, IBM MQ 2053, SSL..."
              : "Đang chờ kết nối Backend..."
          }
          rows={1}
          disabled={isLoading || !isOnline}
        />

        <button
          type="submit"
          className={`button-primary button-send-coral ${
            !text.trim() || isLoading ? "disabled" : ""
          }`}
          disabled={!text.trim() || isLoading || !isOnline}
          title="Gửi câu hỏi (Enter)"
        >
          {isLoading ? (
            <FaSpinner className="spinner-spin" />
          ) : (
            <FaArrowUp />
          )}
        </button>
      </div>
    </form>
  );
}
