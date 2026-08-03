/**
 * ChatInput — user text input for asking questions.
 *
 * TODO: Implement in Phase 5
 * - Text input with send button
 * - Enter to submit
 * - Loading state (disable while generating)
 */

export default function ChatInput() {
  return (
    <div className="chat-input">
      <input
        type="text"
        placeholder="Ask a technical question..."
        disabled
        style={{ width: "100%", padding: "0.75rem", borderRadius: "8px" }}
      />
    </div>
  );
}
