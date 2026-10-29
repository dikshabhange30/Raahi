import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api, { getErrorMessage } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import MessageThread from "../components/MessageThread";

export default function ConversationChat() {
  const { id } = useParams();
  const { user } = useAuth();
  const toast = useToast();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    const { data } = await api.get(`/conversations/${id}/messages`);
    setMessages([...data].sort((a, b) => a.id - b.id));
  }, [id]);

  useEffect(() => {
    load().catch((e) => setError(getErrorMessage(e))).finally(() => setLoading(false));
    const t = setInterval(() => load().catch(() => {}), 10000);
    return () => clearInterval(t);
  }, [load]);

  const send = async (content) => {
    try {
      const { data } = await api.post(`/conversations/${id}/messages`, { content });
      setMessages((m) => [...m, data]);
    } catch (err) {
      toast(getErrorMessage(err), "error");
      throw err;
    }
  };

  return (
    <div className="page">
      <header className="page-head">
        <div>
          <Link to="/messages" className="back">← Messages</Link>
          <h1>Conversation #{id}</h1>
        </div>
        <button className="btn secondary" onClick={() => load().catch((e) => toast(getErrorMessage(e), "error"))}>Refresh</button>
      </header>
      {error && <div className="error" role="alert">{error}</div>}
      {loading ? <div className="card skeleton tall" /> : (
        <MessageThread messages={messages} meId={user.id} onSend={send} emptyText="No messages yet. Say hello." />
      )}
    </div>
  );
}
