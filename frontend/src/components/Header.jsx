import React from "react";
import { FaChartBar, FaTrashAlt } from "react-icons/fa";

/**
 * Header — Claude/Anthropic editorial style top nav conforming to DESIGN.MD.
 */
export default function Header({
  healthStatus,
  onOpenMetrics,
  onClearChat,
  messageCount,
}) {
  return (
    <header className="app-header">
      <div className="header-left">
        <div className="brand-logo">
          {/* Anthropic radial-style mark */}
          <span className="brand-glyph" aria-hidden="true">✻</span>
          <h1 className="brand-title">TechQA</h1>
          <span className="badge-pill">HCMUS</span>
        </div>
      </div>

      <div className="header-right">
        {/* Connection status with teal dot */}
        <div
          className={`health-badge ${
            healthStatus.isConnected ? "status-online" : "status-offline"
          }`}
          title={
            healthStatus.isConnected
              ? `Backend Sẵn sàng (v${healthStatus.version})`
              : "Backend Offline (http://localhost:8000)"
          }
        >
          <span className="status-dot"></span>
          <span className="status-text">
            {healthStatus.isConnected ? "Sẵn sàng" : "Mất kết nối"}
          </span>
        </div>

        {/* Coral Primary CTA Button */}
        <button
          className="button-primary"
          onClick={onOpenMetrics}
          title="Xem bảng so sánh đánh giá mô hình"
        >
          <FaChartBar className="btn-icon" />
          <span>Đánh giá mô hình</span>
        </button>

        {/* Clear Chat Button */}
        {messageCount > 0 && (
          <button
            className="button-secondary"
            onClick={onClearChat}
            title="Xóa đoạn chat"
          >
            <FaTrashAlt className="btn-icon" />
            <span>Xóa</span>
          </button>
        )}
      </div>
    </header>
  );
}
