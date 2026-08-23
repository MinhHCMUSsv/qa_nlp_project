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

const DEFAULT_SAMPLE_QUESTIONS = [
  {
    id: "Q1",
    category: "WebSphere & Java",
    question: "How to resolve java.lang.OutOfMemoryError Java heap space in WebSphere Application Server?",
    description: "Troubleshoot JVM heap exhaustion, configure -Xms/-Xmx, and analyze verbose GC logs.",
  },
  {
    id: "Q2",
    category: "DB2 Database",
    question: "What causes DB2 SQL0911N reason code 68 lock timeout and how to fix it?",
    description: "Diagnose transaction lock contention, enable lock event monitors, and configure CUR_COMMIT.",
  },
  {
    id: "Q3",
    category: "IBM MQ",
    question: "How to troubleshoot IBM MQ reason code 2053 (MQRC_Q_FULL) on queue manager?",
    description: "Manage queue depth, alter MAXDEPTH, inspect dead letter queue, and balance consumer load.",
  },
  {
    id: "Q4",
    category: "Security & SSL",
    question: "How to fix PKIX path building failed SSLHandshakeException in Java client?",
    description: "Import missing SSL certificates into cacerts truststore using keytool or IBM IKEYMAN.",
  },
  {
    id: "Q5",
    category: "System Tuning",
    question: "How to tune Linux kernel file descriptors and sysctl parameters for high concurrency NLP?",
    description: "Configure limits.conf, somaxconn, and max_map_count for vector database workloads.",
  },
  {
    id: "Q6",
    category: "Transformer LLM",
    question: "How to optimize Llama 3.2 fine-tuning memory with Unsloth and QLoRA on low VRAM?",
    description: "Use 4-bit NF4 quantization, gradient checkpointing, and paged 8-bit AdamW optimizer.",
  },
];

export default function useChat() {
  // Messages history
  const [messages, setMessages] = useState([]);

  // Active streaming or API loading state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Active document shown in inspector panel
  const [activeSourceDoc, setActiveSourceDoc] = useState(null);

  // RAG Configuration settings
  const [ragSettings, setRagSettings] = useState({
    retrievalMode: "dense", // 'dense' | 'hybrid' | 'direct_llm'
    topK: 3,
    temperature: 0.7,
  });

  // System Health status
  const [healthStatus, setHealthStatus] = useState({
    isConnected: false,
    qdrantConnected: false,
    modelLoaded: false,
    engineMode: "engine_live",
    indexedCount: 69888,
    device: "cuda",
    version: "0.1.0",
    loading: true,
  });

  // Collection stats
  const [collectionStats, setCollectionStats] = useState(null);

  // Curated sample questions from TechQA dataset (with instant fallback)
  const [sampleQuestions, setSampleQuestions] = useState(DEFAULT_SAMPLE_QUESTIONS);

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
