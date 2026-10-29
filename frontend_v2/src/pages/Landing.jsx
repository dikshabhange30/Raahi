import { useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import Logo from "../components/Logo";
import Photo from "../components/Photo";
import Sticker from "../components/Stickers";

const languages = ["Marathi", "Tamil", "Telugu", "Kannada", "Malayalam", "Bengali", "Gujarati", "Punjabi", "Odia", "Assamese", "Konkani", "Hindi", "Urdu"];
const tones = ["pista", "blush", "olive", "sand"];
const cardStickers = ["leaf", "flower", "sun", "sparkle"];

const features = [
  { sticker: "pin", title: "Find your community", text: "Browse groups by city and language. Join the ones that feel like home, leave any time." },
  { sticker: "speech", title: "Talk with your group", text: "Every community has its own group chat. Only members can read it or write in it." },
  { sticker: "heart", title: "Ask a member for help", text: "Need a doctor, a flat or a tailor? Ask someone from your community. When they accept, you move to a private chat." },
];

const steps = [
  { title: "Create your account", text: "Sign up and confirm your email with a 6-digit code." },
  { title: "Join a community", text: "Pick a group in your city that shares your language or background." },
  { title: "Say hello", text: "Chat with the group and meet the members." },
  { title: "Ask for help", text: "Send a request to a member. If they accept, you can talk privately." },
];

const notes = [
  { tone: "pista", rotate: -2, text: "You move for a job. You shouldn't have to leave your language, your festivals and your food behind." },
  { tone: "blush", rotate: 1.5, text: "Finding someone to ask is easier when they already speak your language." },
  { tone: "sand", rotate: -1, text: "A new city feels smaller once there's a group chat waiting for you." },
];

const safety = [
  "Email verification when you sign up, and a login code every time you sign in.",
  "No public people search. You only see members of communities you have joined.",
  "Block anyone, or report them, in a couple of taps.",
  "Admins review reports and can deactivate accounts.",
];

export default function Landing() {
  const { user, loading } = useAuth();
  const [communities, setCommunities] = useState(null);

  useEffect(() => {
    api.get("/communities/")
      .then((r) => setCommunities(r.data.filter((c) => c.is_active).slice(0, 6)))
      .catch(() => setCommunities(undefined));
  }, []);

  if (!loading && user) return <Navigate to="/communities" replace />;

  return (
    <div className="lp">
      <header className="lp-nav">
        <Logo />
        <nav aria-label="Page sections" className="lp-links">
          <a href="#what">What is Raahi</a>
          <a href="#how">How it works</a>
          <a href="#communities">Communities</a>
          <a href="#safety">Safety</a>
        </nav>
        <div className="lp-nav-actions">
          <Link className="btn secondary" to="/login">Log in</Link>
          <Link className="btn" to="/register">Join Raahi</Link>
        </div>
      </header>

      <section className="lp-hero">
        <div className="lp-hero-text">
          <h1>New city. Same boli.</h1>
          <p className="lp-lead">
            Raahi connects people who share a language or background and live in the same city.
            Join a community, chat with your group, and ask a fellow member for help when you need it.
          </p>
          <div className="lp-cta">
            <Link className="btn big" to="/register">Join Raahi</Link>
            <Link className="btn secondary big" to="/login">Log in</Link>
          </div>
          <p className="muted small">Sign-up takes a minute. We confirm your email with a 6-digit code.</p>
        </div>
        <div className="lp-collage" aria-hidden="true">
          <Photo src="hero1.jpg" scene="city" caption="A new city" rotate={-5} className="p1" />
          <Photo src="hero2.jpg" scene="market" caption="Familiar flavours" rotate={4} className="p2" />
          <Photo src="hero3.jpg" scene="hills" caption="Weekend with your people" rotate={-2} className="p3" />
          <Sticker name="sparkle" size={70} rotate={-10} className="float" style={{ left: -6, top: 4 }} />
          <Sticker name="chai" size={96} rotate={8} className="float" style={{ right: -4, top: 150 }} />
          <Sticker name="bag" size={84} rotate={-8} className="float" style={{ left: 30, bottom: -14 }} />
          <Sticker name="flower" size={64} rotate={14} className="float" style={{ right: 70, top: -18 }} />
        </div>
      </section>

      <section className="lp-band">
        <p className="band-title">Groups for every language</p>
        <div className="chip-cloud">
          {languages.map((l, i) => <span key={l} className={`chip tone-${tones[i % 4]}`}>{l}</span>)}
          <span className="chip outline">and any language your city speaks</span>
        </div>
      </section>

      <section id="what" className="lp-section">
        <h2 className="lp-h2">What Raahi is for</h2>
        <p className="lp-sub">A raahi is a traveller. Moving to a new city makes everyone one. Raahi helps you find the people who already know the way.</p>
        <div className="lp-features">
          {features.map((f, i) => (
            <article key={f.title} className={`card feature tone-${tones[i]}`}>
              <Sticker name={f.sticker} size={72} rotate={i % 2 ? 6 : -6} />
              <h3>{f.title}</h3>
              <p>{f.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="lp-strip" aria-hidden="true">
        <Photo src="strip1.jpg" scene="home" caption="A flat near your people" rotate={-3} />
        <Photo src="strip2.jpg" scene="market" caption="Festival season" rotate={2} />
        <Photo src="strip3.jpg" scene="city" caption="Your first month" rotate={-2} />
        <Photo src="strip4.jpg" scene="hills" caption="Weekend plans" rotate={3} />
      </section>

      <section id="how" className="lp-section lp-pista">
        <h2 className="lp-h2">How it works</h2>
        <ol className="lp-steps">
          {steps.map((s, i) => (
            <li key={s.title}>
              <span className="step-num">{i + 1}</span>
              <div><h3>{s.title}</h3><p>{s.text}</p></div>
            </li>
          ))}
        </ol>
      </section>

      <section id="communities" className="lp-section">
        <h2 className="lp-h2">Communities you can join</h2>
        {communities === null && <div className="lp-features">{[1, 2, 3].map((i) => <div key={i} className="card skeleton" />)}</div>}
        {communities === undefined && <p className="lp-sub">Communities will show up here once the server is reachable.</p>}
        {Array.isArray(communities) && communities.length === 0 && (
          <div className="card empty-state">
            <Sticker name="house" size={80} />
            <h3>No communities yet</h3>
            <p className="muted">Create an account and start the first one for your city.</p>
          </div>
        )}
        {Array.isArray(communities) && communities.length > 0 && (
          <div className="lp-features">
            {communities.map((c) => (
              <article key={c.id} className={`card community tone-${tones[c.id % 4]}`}>
                <Sticker name={cardStickers[c.id % 4]} size={46} rotate={10} className="corner" />
                <h3>{c.name}</h3>
                <div className="chips"><span className="chip">{c.city}</span><span className="chip">{c.language}</span></div>
                <p className="muted">{c.description || "A community for people who share a language in this city."}</p>
                <div className="card-actions"><Link className="btn" to="/register">Join Raahi to enter</Link></div>
              </article>
            ))}
          </div>
        )}
      </section>

      <section id="safety" className="lp-section lp-olive">
        <div className="lp-safety">
          <Sticker name="shield" size={110} rotate={-6} />
          <div>
            <h2 className="lp-h2 left">Built to feel safe</h2>
            <ul className="tick-list">
              {safety.map((s) => <li key={s}>{s}</li>)}
            </ul>
          </div>
        </div>
      </section>

      <section className="lp-section">
        <h2 className="lp-h2">Why we built Raahi</h2>
        <div className="lp-notes">
          {notes.map((n) => (
            <blockquote key={n.text} className={`note tone-${n.tone}`} style={{ transform: `rotate(${n.rotate}deg)` }}>
              {n.text}
            </blockquote>
          ))}
        </div>
      </section>

      <section className="lp-final">
        <Sticker name="sparkle" size={60} rotate={-10} className="float" style={{ left: "12%", top: 24 }} />
        <Sticker name="flower" size={70} rotate={12} className="float" style={{ right: "12%", bottom: 24 }} />
        <h2>Your people are already in your city.</h2>
        <p>Create your account and find them.</p>
        <div className="lp-cta center">
          <Link className="btn big pista" to="/register">Join Raahi</Link>
          <Link className="btn big ghost" to="/login">Log in</Link>
        </div>
      </section>

      <footer className="lp-footer">
        <Logo light />
        <p>For everyone a little far from home.</p>
      </footer>
    </div>
  );
}
