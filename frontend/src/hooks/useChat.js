/**
 * useChat — custom hook for conversation, RAG parameters, and system state management.
 */

import { useState, useEffect, useCallback } from "react";
import {
  askQuestion,
  checkHealth,
  getSampleQuestions,
  getEvaluationMetrics,
  getCollections,
} from "../api/qaClient";

export default function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Active document selected for inspection in the side drawer
  const [activeSourceDoc, setActiveSourceDoc] = useState(null);

  // RAG Configuration settings
  const [ragSettings, setRagSettings] = useState({
    topK: 5,
    temperature: 0.7,
    retrievalMode: "dense", // "dense", "hybrid", "direct_llm"
  });

  // System status and diagnostic metadata
  const [healthStatus, setHealthStatus] = useState({
    isConnected: false,
    qdrantConnected: false,
    modelLoaded: false,
    engineMode: "unknown",
    indexedCount: 0,
    device: "cpu",
    version: "0.1.0",
    loading: true,
  });

  // Collection stats
  const [collectionStats, setCollectionStats] = useState(null);

  // Curated sample questions from TechQA dataset
  const [sampleQuestions, setSampleQuestions] = useState([]);

  // Metrics Modal state & data
  const [showMetricsModal, setShowMetricsModal] = useState(false);
  const [metricsData, setMetricsData] = useState(null);
  const [metricsLoading, setMetricsLoading] = useState(false);

  // Poll / Check system health on mount
  const fetchHealth = useCallback(async () => {
    try {
      const data = await checkHealth();
      setHealthStatus({
        isConnected: true,
        qdrantConnected: data.qdrant_connected,
        modelLoaded: data.model_loaded,
        engineMode: data.engine_mode,
        indexedCount: data.indexed_documents_count,
        device: data.device,
        version: data.version,
        loading: false,
      });
    } catch (err) {
      setHealthStatus((prev) => ({
        ...prev,
        isConnected: false,
        loading: false,
      }));
    }
  }, []);

  // Fetch sample questions on mount
  const fetchSampleQuestions = useCallback(async () => {
    try {
      const data = await getSampleQuestions();
      setSampleQuestions(data);
    } catch (err) {
      console.warn("Could not fetch sample questions:", err.message);
    }
  }, []);

  // Fetch collections info
  const fetchCollections = useCallback(async () => {
    try {
      const data = await getCollections();
      setCollectionStats(data);
    } catch (err) {
      console.warn("Could not fetch collections:", err.message);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    fetchSampleQuestions();
    fetchCollections();

    // Check health every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, [fetchHealth, fetchSampleQuestions, fetchCollections]);

  // Send a question to backend RAG pipeline
  const sendMessage = async (questionText) => {
    if (!questionText || !questionText.trim() || isLoading) return;

    const trimmedQuestion = questionText.trim();
    setError(null);

    // Append user message immediately
    const userMessage = {
      id: Date.now().toString(),
      role: "user",
      content: trimmedQuestion,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const result = await askQuestion({
        question: trimmedQuestion,
        topK: ragSettings.topK,
        temperature: ragSettings.temperature,
        retrievalMode: ragSettings.retrievalMode,
      });

      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: result.answer,
        sources: result.sources || [],
        latencyMs: result.latency_ms,
        retrievalMode: result.retrieval_mode,
        modelName: result.model_name,
        confidenceScore: result.confidence_score,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // If sources returned, set the top source as active preview if none opened
      if (result.sources && result.sources.length > 0 && !activeSourceDoc) {
        setActiveSourceDoc(result.sources[0]);
      }
    } catch (err) {
      const errorMsg =
        err.response?.data?.detail ||
        err.message ||
        "Lỗi không thể kết nối đến Backend Server.";
      setError(errorMsg);

      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `⚠️ **Đã xảy ra lỗi khi xử lý câu hỏi:** ${errorMsg}\n\nVui lòng kiểm tra xem Backend FastAPI đã được khởi động tại \`http://localhost:8000\` chưa.`,
        sources: [],
        latencyMs: 0,
        isError: true,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Open Metrics modal and fetch benchmark data
  const openMetrics = async () => {
    setShowMetricsModal(true);
    if (!metricsData) {
      setMetricsLoading(true);
      try {
        const data = await getEvaluationMetrics();
        setMetricsData(data);
      } catch (err) {
        console.error("Failed to load metrics:", err);
      } finally {
        setMetricsLoading(false);
      }
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
    setActiveSourceDoc(null);
  };

  const updateSettings = (newSettings) => {
    setRagSettings((prev) => ({ ...prev, ...newSettings }));
  };

  return {
    messages,
    isLoading,
    error,
    activeSourceDoc,
    setActiveSourceDoc,
    ragSettings,
    updateSettings,
    healthStatus,
    fetchHealth,
    collectionStats,
    sampleQuestions,
    showMetricsModal,
    setShowMetricsModal,
    metricsData,
    metricsLoading,
    openMetrics,
    sendMessage,
    clearChat,
  };
}
