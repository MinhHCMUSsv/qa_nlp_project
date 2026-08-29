/**
 * API Client — communicates with the FastAPI backend.
 *
 * Base URL defaults to http://localhost:8000/api
 */

import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 300000, // 300s timeout for LLM / RAG inference (increased for model loading)
});

/**
 * Ask a question and get a RAG-powered answer.
 * @param {Object} params
 * @param {string} params.question - The user's question
 * @param {number} [params.topK=5] - Number of documents to retrieve
 * @param {number} [params.temperature=0.7] - LLM temperature
 * @param {string} [params.retrievalMode="dense"] - "dense" | "hybrid" | "direct_llm"
 * @param {string} [params.sessionId] - Session ID
 * @returns {Promise<{
 *   question: string,
 *   answer: string,
 *   sources: Array,
 *   latency_ms: number,
 *   retrieval_mode: string,
 *   model_name: string,
 *   confidence_score: number
 * }>}
 */
export async function askQuestion({
  question,
  topK = 5,
  temperature = 0.7,
  retrievalMode = "dense",
  sessionId = null,
}) {
  const response = await apiClient.post("/ask", {
    question,
    top_k: topK,
    temperature,
    retrieval_mode: retrievalMode,
    session_id: sessionId,
  });
  return response.data;
}

/**
 * Check backend system health status.
 * @returns {Promise<{
 *   status: string,
 *   qdrant_connected: boolean,
 *   model_loaded: boolean,
 *   embedder_loaded: boolean,
 *   engine_mode: string,
 *   indexed_documents_count: number,
 *   device: string,
 *   version: string
 * }>}
 */
export async function checkHealth() {
  const response = await apiClient.get("/health");
  return response.data;
}

/**
 * Trigger document indexing.
 * @param {string} [corpusSplit="techqa_all"]
 * @param {boolean} [forceReindex=false]
 * @returns {Promise<{
 *   status: string,
 *   indexed_count: number,
 *   collection_name: string,
 *   duration_seconds: number
 * }>}
 */
export async function indexDocuments(corpusSplit = "techqa_all", forceReindex = false) {
  const response = await apiClient.post("/index", {
    corpus_split: corpusSplit,
    force_reindex: forceReindex,
  });
  return response.data;
}

/**
 * Get Qdrant collection statistics.
 * @returns {Promise<{
 *   collection_name: string,
 *   points_count: number,
 *   vector_size: number,
 *   distance_metric: string,
 *   status: string
 * }>}
 */
export async function getCollections() {
  const response = await apiClient.get("/collections");
  return response.data;
}

/**
 * Get sample TechQA questions.
 * @returns {Promise<Array<{
 *   id: string,
 *   category: string,
 *   question: string,
 *   description: string
 * }>>}
 */
export async function getSampleQuestions() {
  const response = await apiClient.get("/sample-questions");
  return response.data;
}

/**
 * Get benchmark evaluation metrics for model comparison.
 * @returns {Promise<{
 *   dataset: string,
 *   test_samples_count: number,
 *   metrics: Array<Object>,
 *   conclusion: string
 * }>}
 */
export async function getEvaluationMetrics() {
  const response = await apiClient.get("/metrics");
  return response.data;
}

export default apiClient;
