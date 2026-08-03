/**
 * API Client — communicates with the FastAPI backend.
 *
 * Base URL: http://localhost:8000/api
 */

import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 60000, // 60s timeout for LLM inference
});

/**
 * Ask a question and get a RAG-powered answer.
 * @param {string} question - The user's question
 * @param {number} topK - Number of documents to retrieve (default: 5)
 * @returns {Promise<{answer: string, sources: Array, question: string}>}
 */
export async function askQuestion(question, topK = 5) {
  const response = await apiClient.post("/ask", { question, top_k: topK });
  return response.data;
}

/**
 * Check system health status.
 * @returns {Promise<{status: string, qdrant_connected: boolean, model_loaded: boolean}>}
 */
export async function checkHealth() {
  const response = await apiClient.get("/health");
  return response.data;
}

/**
 * Trigger document indexing.
 * @returns {Promise<Object>}
 */
export async function indexDocuments() {
  const response = await apiClient.post("/index");
  return response.data;
}

/**
 * Get Qdrant collection statistics.
 * @returns {Promise<Object>}
 */
export async function getCollections() {
  const response = await apiClient.get("/collections");
  return response.data;
}

export default apiClient;
