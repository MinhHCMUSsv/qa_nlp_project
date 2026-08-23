import React from "react";
import {
  FaTimes,
  FaExternalLinkAlt,
  FaFileAlt,
  FaCheckCircle,
} from "react-icons/fa";
import { formatScore } from "../utils/formatters";

/**
 * DocumentInspector — Claude-style code window card and technote inspector.
 */
export default function DocumentInspector({ document, onClose }) {
  if (!document) {
    return (
      <div className="inspector-editorial-panel inspector-blank">
        <div className="blank-editorial-content">
          <FaFileAlt className="blank-glyph" />
          <p>Nhấp vào một nguồn tài liệu để xem nội dung chi tiết.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="inspector-editorial-panel">
      {/* Top Bar */}
      <div className="inspector-editorial-top">
        <div className="doc-meta-editorial">
          <span className="badge-pill badge-category-pill">
            {document.category || "IBM Technote"}
          </span>
          <h3 className="doc-serif-title">{document.title}</h3>
          <span className="doc-code-pill font-mono">{document.doc_id}</span>
        </div>
        <button
          className="btn-icon-circular"
          onClick={onClose}
          title="Đóng"
        >
          <FaTimes />
        </button>
      </div>

      {/* Similarity & External Link */}
      <div className="inspector-status-bar">
        <div className="score-teal-pill">
          <FaCheckCircle className="score-check-icon" />
          <span>Độ tương đồng: <strong>{formatScore(document.score)}</strong></span>
        </div>

        {document.url && (
          <a
            href={document.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-link"
          >
            <FaExternalLinkAlt /> Bài gốc IBM
          </a>
        )}
      </div>

      {/* Dark Code Window Card (Product Chrome from DESIGN.MD) */}
      <div className="code-window-card">
        <div className="code-window-header">
          <span className="window-dot red"></span>
          <span className="window-dot yellow"></span>
          <span className="window-dot green"></span>
          <span className="window-title-tab">{document.doc_id}.txt</span>
        </div>
        <div className="code-window-content">
          <pre className="code-pre font-mono">{document.content}</pre>
        </div>
      </div>
    </div>
  );
}
