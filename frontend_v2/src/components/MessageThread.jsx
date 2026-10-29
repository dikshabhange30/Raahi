import { useEffect, useRef, useState } from "react";
import { fmtTime, initials } from "../utils";

export default function MessageThread({ messages, meId, onSend, emptyText }) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const listRef = useRef(null);

  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages.length]);

  const submit = async (e) => {
    e.preventDefault();
    const content = text.trim();
    if (!content) return;
    setBusy(true);
    try {
      await onSend(content);
      setText("");
    } catch {
      /* error toast shown by parent */
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="thread">
      <div className="thread-list" ref={listRef}>
        {messages.length === 0 && <p className="empty">{emptyText || "No messages yet. Say hello!"}</p>}
        {messages.map((m) => {
          const mine = m.sender_id === meId;
          const name = m.sender_full_name || m.sender_username || `User #${m.sender_id}`;
          return (
            <div key={m.id} className={`msg ${mine ? "mine" : ""}`}>
              {!mine && <div className="avatar sm">{initials(name)}</div>}
              <div className="bubble">
                {!mine && <div className="msg-name">{name}</div>}
                <div className="msg-text">{m.content}</div>
                <div className="msg-time">{fmtTime(m.created_at)}</div>
              </div>
            </div>
          );
        })}
      </div>
      <form className="composer" onSubmit={submit}>
        <label htmlFor="composer-input" className="sr-only">Message</label>
        <input id="composer-input" value={text} onChange={(e) => setText(e.target.value)}
          placeholder="Write a message" maxLength={5000} autoComplete="off" />
        <button className="btn" disabled={busy || !text.trim()}>Send</button>
      </form>
    </div>
  );
}
