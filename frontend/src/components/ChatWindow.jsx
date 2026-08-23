import React, { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  FaUser,
  FaCopy,
  FaCheck,
  FaFileAlt,
} from "react-icons/fa";
import { formatLatency, formatScore } from "../utils/formatters";

/**
 * ChatWindow — Claude editorial style conversation interface conforming to DESIGN.MD.
 */
export default function ChatWindow({
  messages,
  isLoading,
  onSelectSource,
  onSelectSampleQuestion,
  sampleQuestions,
}) {
  const messagesEndRef = useRef(null);
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleCopy = (text, msgId) => {
    navigator.clipboard.writeText(text);
    setCopiedId(msgId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="chat-window-container">
      {/* 1. Welcome Screen — Editorial Style with Serif Display */}
      {messages.length === 0 && (
        <div className="editorial-welcome-hero">
          <div className="welcome-glyph">✻</div>
          <h2 className="welcome-heading">Xin chào! Bạn cần tìm kiếm gì?</h2>
          <p className="welcome-subtext">
            Hệ thống QA kỹ thuật RAG kết hợp mô hình Transformer và cơ sở tri thức IBM TechQA.
          </p>

          <div className="welcome-feature-cards">
            {sampleQuestions.slice(0, 3).map((sq) => (
              <button
                key={sq.id}
                type="button"
                className="welcome-card-item"
                onClick={() => onSelectSampleQuestion(sq.question)}
              >
                <span className="welcome-card-tag">{sq.category}</span>
                <span className="welcome-card-title">{sq.question}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 2. Messages Stream */}
      <div className="messages-stream">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`message-entry ${
              msg.role === "user" ? "entry-user" : "entry-assistant"
            } ${msg.isError ? "entry-error" : ""}`}
          >
            <div className="entry-avatar">
              {msg.role === "user" ? <FaUser /> : <span className="assistant-glyph">✻</span>}
            </div>

            <div className="entry-card">
              <div className="entry-header">
                <span className="entry-author">
                  {msg.role === "user" ? "Bạn" : "TechQA"}
                </span>

                {msg.role === "assistant" && !msg.isError && (
                  <div className="entry-meta-right">
                    {msg.latencyMs > 0 && (
                      <span className="latency-badge">
                        {formatLatency(msg.latencyMs)}
                      </span>
                    )}
                    <button
                      className="btn-icon-circular"
                      onClick={() => handleCopy(msg.content, msg.id)}
                      title="Sao chép câu trả lời"
                    >
                      {copiedId === msg.id ? (
                        <FaCheck className="text-teal" />
                      ) : (
                        <FaCopy />
                      )}
                    </button>
                  </div>
                )}
              </div>

              {/* Markdown Content */}
              <div className="editorial-markdown">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>

              {/* Citations / Source Technotes */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="entry-citations-area">
                  <div className="citations-header">
                    <FaFileAlt className="citations-icon" />
                    <span>Tài liệu tham khảo ({msg.sources.length}):</span>
                  </div>
                  <div className="citations-pills-row">
                    {msg.sources.map((src, idx) => (
                      <button
                        key={src.doc_id || idx}
                        type="button"
                        className="source-connector-pill"
                        onClick={() => onSelectSource(src)}
                        title={`Xem chi tiết: ${src.title}`}
                      >
                        <span className="pill-score">
                          {formatScore(src.score)}
                        </span>
                        <span className="pill-name">
                          [{src.doc_id}] {src.title}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="message-entry entry-assistant entry-loading">
            <div className="entry-avatar">
              <span className="assistant-glyph">✻</span>
            </div>
            <div className="entry-card loading-card-cream">
              <div className="coral-pulse-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span className="loading-caption">Đang tổng hợp câu trả lời...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
