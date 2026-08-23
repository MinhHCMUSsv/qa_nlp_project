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
              <h3 className="modal-serif-heading">TechQA Benchmark & Ablation Study</h3>
              <p className="modal-caption-text">
                Ablation Study: QA Performance Across 160 Unseen IBM Dev Pairs (Ground Truth Verified)
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
                      <th>Model Configuration</th>
                      <th>EM (%)</th>
                      <th>Token F1 (%)</th>
                      <th>ROUGE-L (%)</th>
                      <th>BLEU-4 (%)</th>
                      <th>Gain vs Base</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="cell-method-name"><strong>1. Base Model</strong> (Llama-3.2-3B)</td>
                      <td>0.0%</td>
                      <td>15.00%</td>
                      <td>10.60%</td>
                      <td>1.10%</td>
                      <td><span className="pill-hallucination rate-coral">Baseline</span></td>
                    </tr>
                    <tr>
                      <td className="cell-method-name"><strong>2. Fine-tuned Model</strong> (AQUABOT)</td>
                      <td>0.0%</td>
                      <td><span className="badge-f1-teal">22.30%</span></td>
                      <td>19.00%</td>
                      <td>5.90%</td>
                      <td><span className="pill-hallucination rate-teal">+48.7% F1</span></td>
                    </tr>
                    <tr>
                      <td className="cell-method-name"><strong>3. Base Model + RAG</strong> (Qdrant)</td>
                      <td>0.0%</td>
                      <td>36.01%</td>
                      <td>29.87%</td>
                      <td>9.32%</td>
                      <td><span className="pill-hallucination rate-teal">+140.1% F1</span></td>
                    </tr>
                    <tr className="row-featured-coral">
                      <td className="cell-method-name"><strong>4. Fine-tuned + RAG</strong> (Full System)</td>
                      <td>0.0%</td>
                      <td><span className="badge-f1-teal" style={{ fontSize: "0.95rem" }}>49.06%</span></td>
                      <td><strong>40.06%</strong></td>
                      <td><strong>17.18%</strong></td>
                      <td><span className="pill-hallucination rate-teal" style={{ fontWeight: 700 }}>+227.1% F1 (15.6x BLEU)</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div className="feature-card-conclusion">
                <div className="conclusion-top-row">
                  <span className="text-teal">✦</span>
                  <h4 className="conclusion-serif-title">Key Scientific Findings & Architecture Insights</h4>
                </div>

                <p className="conclusion-body-text">
                  QLoRA fine-tuning aligns the model's vocabulary and syntax with official IBM Technotes (+48.7% F1 gain). Integrating Qdrant Cloud dense vector retrieval (69,888 technotes) with the fine-tuned generator propels F1-score to <strong>49.06%</strong> and BLEU-4 to <strong>17.18%</strong> (15.6x baseline), proving the combined synergy of domain adaptation and retrieval grounding.
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
