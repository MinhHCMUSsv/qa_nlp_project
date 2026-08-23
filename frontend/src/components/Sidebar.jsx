import React from "react";
import { FaSlidersH, FaLightbulb } from "react-icons/fa";

/**
 * Sidebar — warm cream control panel conforming to DESIGN.MD.
 */
export default function Sidebar({
  ragSettings,
  onUpdateSettings,
  sampleQuestions,
  onSelectSampleQuestion,
  isLoading,
}) {
  return (
    <aside className="sidebar-container">
      {/* 1. RAG Configuration */}
      <div className="sidebar-group">
        <div className="group-heading">
          <FaSlidersH className="group-icon" />
          <span>Cấu hình RAG</span>
        </div>

        {/* Retrieval Mode Tabs */}
        <div className="control-item">
          <label className="control-label">Chế độ tìm kiếm</label>
          <div className="category-tabs">
            <button
              type="button"
              className={`category-tab ${
                ragSettings.retrievalMode === "dense" ? "category-tab-active" : ""
              }`}
              onClick={() => onUpdateSettings({ retrievalMode: "dense" })}
            >
              Dense
            </button>
            <button
              type="button"
              className={`category-tab ${
                ragSettings.retrievalMode === "hybrid" ? "category-tab-active" : ""
              }`}
              onClick={() => onUpdateSettings({ retrievalMode: "hybrid" })}
            >
              Hybrid
            </button>
            <button
              type="button"
              className={`category-tab ${
                ragSettings.retrievalMode === "direct_llm" ? "category-tab-active" : ""
              }`}
              onClick={() => onUpdateSettings({ retrievalMode: "direct_llm" })}
            >
              Direct LLM
            </button>
          </div>
        </div>

        {/* Top-K Slider */}
        {ragSettings.retrievalMode !== "direct_llm" && (
          <div className="control-item">
            <div className="control-header-row">
              <label className="control-label">Số tài liệu (Top-K)</label>
              <span className="control-value-badge">{ragSettings.topK} docs</span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              step="1"
              value={ragSettings.topK}
              onChange={(e) =>
                onUpdateSettings({ topK: parseInt(e.target.value, 10) })
              }
              className="range-slider-coral"
            />
          </div>
        )}

        {/* Temperature Slider */}
        <div className="control-item">
          <div className="control-header-row">
            <label className="control-label">Temperature</label>
            <span className="control-value-badge">{ragSettings.temperature}</span>
          </div>
          <input
            type="range"
            min="0.0"
            max="1.2"
            step="0.1"
            value={ragSettings.temperature}
            onChange={(e) =>
              onUpdateSettings({
                temperature: parseFloat(e.target.value),
              })
            }
            className="range-slider-coral"
          />
        </div>
      </div>

      {/* 2. Sample Questions */}
      <div className="sidebar-group">
        <div className="group-heading">
          <FaLightbulb className="group-icon text-coral" />
          <span>Câu hỏi mẫu TechQA</span>
        </div>

        <div className="sample-cards-list">
          {sampleQuestions.map((sq) => (
            <div
              key={sq.id}
              className={`sample-feature-card ${isLoading ? "disabled" : ""}`}
              onClick={() => !isLoading && onSelectSampleQuestion(sq.question)}
            >
              <span className="sample-cat-pill">{sq.category}</span>
              <p className="sample-query-title">{sq.question}</p>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}
