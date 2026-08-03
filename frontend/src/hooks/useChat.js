/**
 * useChat — custom hook for chat state management.
 *
 * TODO: Implement in Phase 5
 * - messages state (array of {role, content, sources})
 * - sendMessage() function
 * - loading state
 * - error handling
 */

import { useState } from "react";

export default function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = async (question) => {
    // TODO: Implement API call
    console.log("sendMessage:", question);
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  return { messages, isLoading, error, sendMessage, clearChat };
}
