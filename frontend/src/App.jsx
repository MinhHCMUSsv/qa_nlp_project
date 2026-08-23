import React, { useState } from "react";
import "./App.css";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import DocumentInspector from "./components/DocumentInspector";
import MetricsModal from "./components/MetricsModal";
import useChat from "./hooks/useChat";

function App() {
  const {
    messages,
    isLoading,
    activeSourceDoc,
    setActiveSourceDoc,
    ragSettings,
    updateSettings,
    healthStatus,
    sampleQuestions,
    showMetricsModal,
    setShowMetricsModal,
    metricsData,
    metricsLoading,
    openMetrics,
    sendMessage,
    clearChat,
  } = useChat();

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isInspectorOpen, setIsInspectorOpen] = useState(true);

  const handleSelectSample = (questionText) => {
    sendMessage(questionText);
  };

  const handleSelectSource = (sourceDoc) => {
    setActiveSourceDoc(sourceDoc);
    setIsInspectorOpen(true);
  };

  return (
    <div className="app-root">
      {/* 1. Header Bar */}
      <Header
        healthStatus={healthStatus}
        onOpenMetrics={openMetrics}
        onClearChat={clearChat}
        messageCount={messages.length}
      />

      {/* 2. Main Dashboard Layout */}
      <main className="app-main-layout">
        {/* Left Sidebar: Controls & Sample Questions */}
        <div className={`layout-sidebar ${isSidebarOpen ? "open" : "collapsed"}`}>
          <Sidebar
            ragSettings={ragSettings}
            onUpdateSettings={updateSettings}
            healthStatus={healthStatus}
            sampleQuestions={sampleQuestions}
            onSelectSampleQuestion={handleSelectSample}
            isLoading={isLoading}
          />
        </div>

        {/* Center Panel: Chat Conversation & Input */}
        <section className="layout-chat-panel">
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            onSelectSource={handleSelectSource}
            onSelectSampleQuestion={handleSelectSample}
            sampleQuestions={sampleQuestions}
          />

          <div className="chat-input-sticky">
            <ChatInput
              onSendMessage={sendMessage}
              isLoading={isLoading}
              isOnline={healthStatus.isConnected}
            />
          </div>
        </section>

        {/* Right Panel: Document Inspector (Technote Viewer) */}
        {isInspectorOpen && activeSourceDoc && (
          <aside className="layout-inspector-panel">
            <DocumentInspector
              document={activeSourceDoc}
              onClose={() => setIsInspectorOpen(false)}
            />
          </aside>
        )}
      </main>

      {/* 3. Evaluation & Benchmark Modal */}
      <MetricsModal
        isOpen={showMetricsModal}
        onClose={() => setShowMetricsModal(false)}
        metricsData={metricsData}
        isLoading={metricsLoading}
      />
    </div>
  );
}

export default App;
