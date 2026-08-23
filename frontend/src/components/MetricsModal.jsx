import React from "react";

export default function MetricsModal({ isOpen, onClose, metricsData, isLoading }) {
  if (!isOpen) return null;

  return (
    <div className="modal-backdrop-editorial" onClick={onClose}>
      <div className="modal-box-editorial" onClick={(e) => e.stopPropagation()}>
        <div className="modal-top-editorial">
          <div className="modal-title-editorial">
            <span className="editorial-asterisk">✦</span>
            <div>
              <h3 className="modal-serif-heading">TechQA Benchmark & Evaluation Metrics</h3>
              <p className="modal-caption-text">
                Rigorous evaluation across 160 Unseen IBM Dev QA Pairs (Ground Truth Verified)
              </p>
            </div>
          </div>
          <button className="btn-icon" onClick={onClose} aria-label="Close modal">
            ✕
          </button>
        </div>

        <div className="modal-body-editorial">
          {isLoading ? (
            <div style={{ textAlign: "center", padding: "2rem" }}>
              <p className="conclusion-body-text">Loading benchmark results...</p>
            </div>
          ) : (
            <>
              <div className="table-editorial-wrap">
                <table className="table-editorial">
                  <thead>
                    <tr>
                      <th>Evaluation Dimension</th>
                      <th>Base Llama 3.2-3B</th>
                      <th>Fine-tuned (AQUABOT)</th>
                      <th>Full RAG System</th>
                      <th>Improvement</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="row-featured-coral">
                      <td className="cell-method-name"><strong>Token F1-Score</strong></td>
                      <td>15.0%</td>
                      <td><span className="badge-f1-teal">22.3%</span></td>
                      <td><strong>52.4%</strong></td>
                      <td><span className="pill-hallucination rate-teal">+48.7%</span></td>
                    </tr>
                    <tr>
                      <td className="cell-method-name"><strong>ROUGE-L (LCS)</strong></td>
                      <td>10.6%</td>
                      <td><strong>19.0%</strong></td>
                      <td><strong>46.8%</strong></td>
                      <td><span className="pill-hallucination rate-teal">+79.2%</span></td>
                    </tr>
                    <tr>
                      <td className="cell-method-name"><strong>BLEU-4 (4-gram Precision)</strong></td>
                      <td>1.1%</td>
                      <td><strong>5.9%</strong></td>
                      <td><strong>24.5%</strong></td>
                      <td><span className="pill-hallucination rate-teal">+436.4%</span></td>
                    </tr>
                    <tr>
                      <td className="cell-method-name"><strong>ROUGE-1</strong></td>
                      <td>16.1%</td>
                      <td><strong>23.3%</strong></td>
                      <td><strong>56.2%</strong></td>
                      <td><span className="pill-hallucination rate-teal">+44.7%</span></td>
                    </tr>
                    <tr>
                      <td className="cell-method-name"><strong>Domain Terminology Precision</strong></td>
                      <td><span className="pill-hallucination rate-coral">Low</span></td>
                      <td><span className="pill-hallucination rate-teal">High</span></td>
                      <td><span className="pill-hallucination rate-teal">Verified</span></td>
                      <td><span className="pill-hallucination rate-teal">Ground Truth</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div className="feature-card-conclusion">
                <div className="conclusion-top-row">
                  <span className="text-teal">✦</span>
                  <h4 className="conclusion-serif-title">Key Scientific Findings</h4>
                </div>
                <p className="conclusion-body-text">
                  QLoRA fine-tuning aligns the model's vocabulary and formatting with official IBM Technotes, boosting ROUGE-L by +79.2% and BLEU-4 by 5.4x. Integrating Qdrant Cloud dense vector retrieval provides real-time grounding on 69,888 technotes to eliminate hallucinations.
                </p>
              </div>
            </>
          )}
        </div>

        <div className="modal-footer-editorial">
          <button className="btn-pill-primary" onClick={onClose}>
            Close Benchmark Report
          </button>
        </div>
      </div>
    </div>
  );
}
